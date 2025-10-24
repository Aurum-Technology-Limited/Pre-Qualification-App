"""
Pre-Qualification App API
A FastAPI application for mortgage pre-qualification calculations and PDF certificate generation.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime, timedelta
from starlette.middleware.base import BaseHTTPMiddleware
import math
import uuid
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title="Pre-Qualification App API",
    description="Mortgage pre-qualification calculator with PDF certificate generation",
    version="1.0.0"
)

# PDF storage directory
PDF_DIR = Path("/app/backend/certificates")
PDF_DIR.mkdir(exist_ok=True)

# Brand colors
COLORS = {
    "lime_green": HexColor('#32CD32'),
    "dark_green": HexColor('#228B22'),
    "white": HexColor('#FFFFFF'),
    "light_bg": HexColor('#F0FFF0'),
    "warning": HexColor('#FD7E14')
}

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

class CustomCORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware that allows requests from specific domain patterns.
    Supports Vercel deployments, local development, and production domains.
    """
    
    # Allowed domain patterns
    ALLOWED_PATTERNS = [
        "vercel.app",       # All Vercel deployments
        "emergentagent.com", # Production domain
        "localhost:3000",    # Local development
        "localhost:3001"     # Alternative local port
    ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request and add appropriate CORS headers."""
        origin = request.headers.get("origin")
        is_allowed = self._is_origin_allowed(origin)
        
        # Handle preflight (OPTIONS) requests
        if request.method == "OPTIONS":
            return self._create_preflight_response(origin, is_allowed)
        
        # Process normal requests
        response = await call_next(request)
        
        # Add CORS headers if origin is allowed
        if is_allowed and origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response
    
    def _is_origin_allowed(self, origin: Optional[str]) -> bool:
        """Check if the origin matches any allowed pattern."""
        if not origin:
            return False
        return any(pattern in origin for pattern in self.ALLOWED_PATTERNS)
    
    def _create_preflight_response(self, origin: Optional[str], is_allowed: bool) -> JSONResponse:
        """Create response for preflight requests."""
        response = JSONResponse(content={}, status_code=200)
        
        if is_allowed and origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response


app.add_middleware(CustomCORSMiddleware)

# ============================================================================
# DATA MODELS
# ============================================================================

class ApplicantInfo(BaseModel):
    """Applicant personal information."""
    name: str = Field(..., min_length=1, max_length=200, description="Full name of applicant")
    email: Optional[str] = Field(None, description="Email address (optional)")
    phone: Optional[str] = Field(None, description="Phone number (optional)")


class AffordabilityInput(BaseModel):
    """Input parameters for affordability calculation."""
    gross_monthly_income: float = Field(
        ..., gt=0, le=1_000_000,
        description="Gross monthly income in selected currency"
    )
    dsr_ratio: float = Field(
        ..., ge=0.1, le=0.8,
        description="Debt Service Ratio (0.1 to 0.8, typically 0.4)"
    )
    monthly_obligations: float = Field(
        default=0, ge=0,
        description="Existing monthly debt obligations"
    )
    annual_interest_rate: float = Field(
        ..., gt=0.001, le=0.50,
        description="Annual interest rate (as decimal, e.g., 0.06 for 6%)"
    )
    term_years: int = Field(
        ..., ge=1, le=50,
        description="Loan term in years"
    )
    stress_rate_bps: Optional[int] = Field(
        default=0, ge=0, le=1000,
        description="Stress test rate increase in basis points (e.g., 200 for 2%)"
    )
    
    @field_validator('monthly_obligations')
    @classmethod
    def validate_obligations(cls, value, info):
        """Ensure monthly obligations don't exceed gross income."""
        gross_income = info.data.get('gross_monthly_income')
        if gross_income and value >= gross_income:
            raise ValueError('Monthly obligations must be less than gross income')
        return value


class PaymentInput(BaseModel):
    """Input parameters for payment calculation."""
    principal_amount: float = Field(
        ..., gt=0, le=10_000_000,
        description="Principal loan amount"
    )
    annual_interest_rate: float = Field(
        ..., gt=0.001, le=0.50,
        description="Annual interest rate (as decimal)"
    )
    term_years: int = Field(
        ..., ge=1, le=50,
        description="Loan term in years"
    )
    stress_rate_bps: Optional[int] = Field(
        default=0, ge=0, le=1000,
        description="Stress test rate increase in basis points"
    )


class CalculationRequest(BaseModel):
    """Main calculation request model."""
    calculation_type: Literal["AFFORDABILITY", "PAYMENT"] = Field(
        ..., description="Type of calculation to perform"
    )
    applicant: ApplicantInfo
    affordability_input: Optional[AffordabilityInput] = None
    payment_input: Optional[PaymentInput] = None
    currency: Literal["TTD", "USD"] = Field(
        default="TTD",
        description="Currency for display (TTD or USD)"
    )
    validity_days: int = Field(
        default=90, ge=1, le=365,
        description="Certificate validity period in days"
    )

# ============================================================================
# CALCULATION FUNCTIONS
# ============================================================================

def calculate_monthly_payment(
    principal: float,
    annual_rate: float,
    term_years: int
) -> float:
    """
    Calculate monthly loan payment using the standard amortization formula.
    
    Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
    Where:
        M = Monthly payment
        P = Principal amount
        r = Monthly interest rate
        n = Total number of payments
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate (as decimal, e.g., 0.06 for 6%)
        term_years: Loan term in years
    
    Returns:
        Monthly payment amount rounded to 2 decimal places
    """
    # Handle edge case of zero interest
    if annual_rate == 0:
        return round(principal / (term_years * 12), 2)
    
    monthly_rate = annual_rate / 12
    num_payments = term_years * 12
    
    # Apply amortization formula
    payment = principal * (
        monthly_rate * math.pow(1 + monthly_rate, num_payments)
    ) / (math.pow(1 + monthly_rate, num_payments) - 1)
    
    return round(payment, 2)


def calculate_max_loan(
    affordable_payment: float,
    annual_rate: float,
    term_years: int
) -> float:
    """
    Calculate maximum loan amount from affordable monthly payment.
    Uses present value of annuity formula.
    
    Formula: PV = PMT * [1 - (1+r)^(-n)] / r
    Where:
        PV = Present value (max loan)
        PMT = Payment amount
        r = Monthly interest rate
        n = Total number of payments
    
    Args:
        affordable_payment: Monthly payment the applicant can afford
        annual_rate: Annual interest rate (as decimal)
        term_years: Loan term in years
    
    Returns:
        Maximum loan amount rounded to 2 decimal places
    """
    # Handle edge case of zero interest
    if annual_rate == 0:
        return round(affordable_payment * term_years * 12, 2)
    
    monthly_rate = annual_rate / 12
    num_payments = term_years * 12
    
    # Apply present value formula
    max_loan = affordable_payment * (
        1 - math.pow(1 + monthly_rate, -num_payments)
    ) / monthly_rate
    
    return round(max_loan, 2)


def format_currency(amount: float, currency: str = "TTD") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Numeric amount
        currency: Currency code (TTD or USD)
    
    Returns:
        Formatted string (e.g., "TTD $1,234.56")
    """
    return f"{currency} ${amount:,.2f}"

# ============================================================================
# PDF GENERATION
# ============================================================================

def generate_certificate_pdf(cert_data: dict) -> str:
    """
    Generate PDF certificate with pre-qualification results.
    
    Args:
        cert_data: Dictionary containing certificate information
    
    Returns:
        File path to generated PDF
    """
    cert_id = cert_data['certificate_id']
    filepath = PDF_DIR / f"{cert_id}.pdf"
    
    # Create PDF canvas
    c = canvas.Canvas(str(filepath), pagesize=letter)
    width, height = letter
    
    # Draw header
    _draw_header(c, width, height)
    
    # Draw certificate details
    y_pos = height - 150
    y_pos = _draw_certificate_info(c, cert_data, y_pos, width)
    y_pos = _draw_applicant_info(c, cert_data, y_pos)
    y_pos = _draw_results_section(c, cert_data, y_pos, width)
    y_pos = _draw_stress_test(c, cert_data, y_pos)
    y_pos = _draw_disclaimer(c, cert_data, y_pos)
    
    # Draw footer
    _draw_footer(c, width)
    
    c.save()
    return str(filepath)


def _draw_header(c: canvas.Canvas, width: float, height: float) -> None:
    """Draw certificate header with lime green background."""
    c.setFillColor(COLORS["lime_green"])
    c.rect(0, height - 120, width, 120, fill=1, stroke=0)
    
    c.setFillColor(COLORS["white"])
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width / 2, height - 60, "Pre-Qualification App")
    
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 90, "Pre-Qualification Certificate")


def _draw_certificate_info(
    c: canvas.Canvas,
    cert_data: dict,
    y_pos: float,
    width: float
) -> float:
    """Draw certificate ID and date information."""
    c.setFillColor(COLORS["dark_green"])
    c.setFont("Helvetica", 10)
    c.drawString(50, y_pos, f"Certificate ID: {cert_data['certificate_id']}")
    c.drawRightString(width - 50, y_pos, f"Issue Date: {cert_data['issue_date']}")
    c.drawRightString(width - 50, y_pos - 15, f"Expiry Date: {cert_data['expiry_date']}")
    
    return y_pos - 50


def _draw_applicant_info(c: canvas.Canvas, cert_data: dict, y_pos: float) -> float:
    """Draw applicant information section."""
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(COLORS["lime_green"])
    c.drawString(50, y_pos, "Applicant Information")
    
    c.setFillColor(COLORS["dark_green"])
    c.setFont("Helvetica", 11)
    y_pos -= 25
    c.drawString(70, y_pos, f"Name: {cert_data['applicant_name']}")
    
    if cert_data.get('applicant_email'):
        y_pos -= 20
        c.drawString(70, y_pos, f"Email: {cert_data['applicant_email']}")
    
    return y_pos - 40


def _draw_results_section(
    c: canvas.Canvas,
    cert_data: dict,
    y_pos: float,
    width: float
) -> float:
    """Draw results box with calculation outcomes."""
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(COLORS["lime_green"])
    c.drawString(50, y_pos, "Assessment Results")
    
    # Draw results box
    y_pos -= 30
    c.setFillColor(COLORS["light_bg"])
    c.rect(50, y_pos - 150, width - 100, 150, fill=1, stroke=1)
    c.setStrokeColor(COLORS["lime_green"])
    c.setLineWidth(2)
    c.rect(50, y_pos - 150, width - 100, 150, fill=0, stroke=1)
    
    # Draw results text
    c.setFillColor(COLORS["dark_green"])
    c.setFont("Helvetica", 11)
    y_pos -= 25
    
    calc_type = cert_data['calculation_type']
    if calc_type == "AFFORDABILITY":
        y_pos = _draw_affordability_results(c, cert_data, y_pos)
    else:
        y_pos = _draw_payment_results(c, cert_data, y_pos)
    
    # Common details
    c.setFont("Helvetica", 11)
    c.setFillColor(COLORS["dark_green"])
    y_pos -= 25
    c.drawString(70, y_pos, f"Annual Interest Rate: {cert_data['interest_rate']}%")
    y_pos -= 20
    c.drawString(70, y_pos, f"Loan Term: {cert_data['term_years']} years")
    
    return y_pos - 30


def _draw_affordability_results(
    c: canvas.Canvas,
    cert_data: dict,
    y_pos: float
) -> float:
    """Draw affordability calculation results."""
    c.drawString(70, y_pos, f"Gross Monthly Income: {cert_data['gross_income']}")
    y_pos -= 20
    c.drawString(70, y_pos, f"DSR Ratio: {cert_data['dsr_ratio']}%")
    y_pos -= 20
    c.drawString(70, y_pos, f"Monthly Obligations: {cert_data['monthly_obligations']}")
    y_pos -= 20
    c.drawString(70, y_pos, f"Affordable Monthly Payment: {cert_data['affordable_payment']}")
    y_pos -= 25
    
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(COLORS["lime_green"])
    c.drawString(70, y_pos, f"Maximum Loan Amount: {cert_data['max_loan']}")
    
    return y_pos


def _draw_payment_results(
    c: canvas.Canvas,
    cert_data: dict,
    y_pos: float
) -> float:
    """Draw payment calculation results."""
    c.drawString(70, y_pos, f"Principal Loan Amount: {cert_data['principal_amount']}")
    y_pos -= 25
    
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(COLORS["lime_green"])
    c.drawString(70, y_pos, f"Monthly Payment: {cert_data['monthly_payment']}")
    
    return y_pos


def _draw_stress_test(c: canvas.Canvas, cert_data: dict, y_pos: float) -> float:
    """Draw stress test results if applicable."""
    if not cert_data.get('stress_results'):
        return y_pos
    
    y_pos -= 30
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(COLORS["warning"])
    c.drawString(
        70, y_pos,
        f"Stress Test Results (+ {cert_data['stress_bps']} bps):"
    )
    
    y_pos -= 20
    c.setFont("Helvetica", 11)
    c.drawString(70, y_pos, cert_data['stress_results'])
    
    return y_pos


def _draw_disclaimer(c: canvas.Canvas, cert_data: dict, y_pos: float) -> float:
    """Draw disclaimer section."""
    y_pos -= 60
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(COLORS["lime_green"])
    c.drawString(50, y_pos, "Important Disclaimer")
    
    y_pos -= 20
    c.setFont("Helvetica", 9)
    c.setFillColor(COLORS["dark_green"])
    
    disclaimer_lines = [
        "This pre-qualification certificate is an estimate only and does not constitute a loan approval or commitment.",
        "Final loan approval is subject to credit verification, property appraisal, and other lending criteria.",
        f"This certificate is valid for {cert_data['validity_days']} days from the issue date.",
        "Interest rates and terms are subject to change. Please consult with a loan officer for details."
    ]
    
    for line in disclaimer_lines:
        c.drawString(50, y_pos, line)
        y_pos -= 15
    
    return y_pos


def _draw_footer(c: canvas.Canvas, width: float) -> None:
    """Draw footer with branding."""
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(COLORS["lime_green"])
    c.drawCentredString(width / 2, 40, "Pre-Qualification App - Your Mortgage Calculator")
    
    c.setFont("Helvetica", 8)
    c.setFillColor(COLORS["dark_green"])
    c.drawCentredString(width / 2, 25, "www.prequalificationapp.com")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Check API health status."""
    return {
        "status": "healthy",
        "service": "Pre-Qualification App API",
        "version": "1.0.0"
    }


@app.post("/api/calculate", tags=["Calculations"])
async def calculate(request: CalculationRequest):
    """
    Calculate pre-qualification based on input parameters.
    
    Supports two calculation types:
    - AFFORDABILITY: Calculate maximum loan from income
    - PAYMENT: Calculate monthly payment from loan amount
    
    Both include optional stress testing.
    """
    try:
        # Generate unique certificate ID
        cert_id = str(uuid.uuid4())[:8].upper()
        issue_date = datetime.now()
        expiry_date = issue_date + timedelta(days=request.validity_days)
        
        # Base result structure
        result = {
            "certificate_id": cert_id,
            "calculation_type": request.calculation_type,
            "applicant": request.applicant.dict(),
            "currency": request.currency,
            "issue_date": issue_date.strftime("%Y-%m-%d"),
            "expiry_date": expiry_date.strftime("%Y-%m-%d"),
            "validity_days": request.validity_days
        }
        
        # Process based on calculation type
        if request.calculation_type == "AFFORDABILITY":
            result.update(_process_affordability(request))
        else:
            result.update(_process_payment(request))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _process_affordability(request: CalculationRequest) -> dict:
    """Process affordability calculation."""
    if not request.affordability_input:
        raise HTTPException(status_code=400, detail="Affordability input required")
    
    inp = request.affordability_input
    
    # Calculate affordable monthly payment
    affordable_payment = (
        inp.gross_monthly_income * inp.dsr_ratio
    ) - inp.monthly_obligations
    
    # Validate positive affordability
    if affordable_payment <= 0:
        raise HTTPException(
            status_code=400,
            detail="Monthly obligations exceed affordable debt service"
        )
    
    # Calculate maximum loan
    max_loan = calculate_max_loan(
        affordable_payment,
        inp.annual_interest_rate,
        inp.term_years
    )
    
    result = {
        "gross_monthly_income": inp.gross_monthly_income,
        "dsr_ratio": inp.dsr_ratio,
        "monthly_obligations": inp.monthly_obligations,
        "affordable_payment": round(affordable_payment, 2),
        "affordable_payment_formatted": format_currency(affordable_payment, request.currency),
        "max_loan_amount": max_loan,
        "max_loan_formatted": format_currency(max_loan, request.currency),
        "annual_interest_rate": inp.annual_interest_rate,
        "interest_rate_percent": round(inp.annual_interest_rate * 100, 2),
        "term_years": inp.term_years,
        "monthly_payment": round(affordable_payment, 2)
    }
    
    # Add stress test if applicable
    if inp.stress_rate_bps > 0:
        result["stress_test"] = _calculate_affordability_stress_test(
            inp, affordable_payment, max_loan, request.currency
        )
    
    return result


def _calculate_affordability_stress_test(
    inp: AffordabilityInput,
    affordable_payment: float,
    base_max_loan: float,
    currency: str
) -> dict:
    """Calculate stress test for affordability."""
    stress_rate = inp.annual_interest_rate + (inp.stress_rate_bps / 10000)
    stress_max_loan = calculate_max_loan(
        affordable_payment,
        stress_rate,
        inp.term_years
    )
    
    return {
        "stress_rate_bps": inp.stress_rate_bps,
        "stress_annual_rate": stress_rate,
        "stress_rate_percent": round(stress_rate * 100, 2),
        "stress_max_loan": stress_max_loan,
        "stress_max_loan_formatted": format_currency(stress_max_loan, currency),
        "reduction_amount": round(base_max_loan - stress_max_loan, 2),
        "reduction_percent": round(
            ((base_max_loan - stress_max_loan) / base_max_loan) * 100, 2
        )
    }


def _process_payment(request: CalculationRequest) -> dict:
    """Process payment calculation."""
    if not request.payment_input:
        raise HTTPException(status_code=400, detail="Payment input required")
    
    inp = request.payment_input
    
    # Calculate monthly payment
    monthly_payment = calculate_monthly_payment(
        inp.principal_amount,
        inp.annual_interest_rate,
        inp.term_years
    )
    
    # Calculate totals
    total_payments = monthly_payment * inp.term_years * 12
    total_interest = total_payments - inp.principal_amount
    
    result = {
        "principal_amount": inp.principal_amount,
        "principal_formatted": format_currency(inp.principal_amount, request.currency),
        "monthly_payment": monthly_payment,
        "monthly_payment_formatted": format_currency(monthly_payment, request.currency),
        "annual_interest_rate": inp.annual_interest_rate,
        "interest_rate_percent": round(inp.annual_interest_rate * 100, 2),
        "term_years": inp.term_years,
        "total_payments": round(total_payments, 2),
        "total_payments_formatted": format_currency(total_payments, request.currency),
        "total_interest": round(total_interest, 2),
        "total_interest_formatted": format_currency(total_interest, request.currency)
    }
    
    # Add stress test if applicable
    if inp.stress_rate_bps > 0:
        result["stress_test"] = _calculate_payment_stress_test(
            inp, monthly_payment, request.currency
        )
    
    return result


def _calculate_payment_stress_test(
    inp: PaymentInput,
    base_payment: float,
    currency: str
) -> dict:
    """Calculate stress test for payment."""
    stress_rate = inp.annual_interest_rate + (inp.stress_rate_bps / 10000)
    stress_payment = calculate_monthly_payment(
        inp.principal_amount,
        stress_rate,
        inp.term_years
    )
    
    return {
        "stress_rate_bps": inp.stress_rate_bps,
        "stress_annual_rate": stress_rate,
        "stress_rate_percent": round(stress_rate * 100, 2),
        "stress_monthly_payment": stress_payment,
        "stress_payment_formatted": format_currency(stress_payment, currency),
        "increase_amount": round(stress_payment - base_payment, 2),
        "increase_percent": round(
            ((stress_payment - base_payment) / base_payment) * 100, 2
        )
    }


@app.post("/api/generate-certificate/{certificate_id}", tags=["Certificates"])
async def generate_certificate(certificate_id: str, cert_data: dict):
    """
    Generate PDF certificate for completed calculation.
    
    Args:
        certificate_id: Unique certificate identifier
        cert_data: Complete calculation results
    
    Returns:
        PDF file download
    """
    try:
        # Prepare data for PDF generation
        pdf_data = _prepare_pdf_data(cert_data)
        
        # Generate PDF
        pdf_path = generate_certificate_pdf(pdf_data)
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"Pre-Qualification_Certificate_{certificate_id}.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _prepare_pdf_data(cert_data: dict) -> dict:
    """Prepare calculation data for PDF generation."""
    pdf_data = {
        "certificate_id": cert_data["certificate_id"],
        "issue_date": cert_data["issue_date"],
        "expiry_date": cert_data["expiry_date"],
        "validity_days": cert_data["validity_days"],
        "applicant_name": cert_data["applicant"]["name"],
        "applicant_email": cert_data["applicant"].get("email", ""),
        "calculation_type": cert_data["calculation_type"],
        "interest_rate": cert_data["interest_rate_percent"],
        "term_years": cert_data["term_years"]
    }
    
    # Add type-specific data
    if cert_data["calculation_type"] == "AFFORDABILITY":
        pdf_data.update({
            "gross_income": cert_data["affordable_payment_formatted"],
            "dsr_ratio": round(cert_data["dsr_ratio"] * 100, 1),
            "monthly_obligations": cert_data.get("affordable_payment_formatted", "N/A"),
            "affordable_payment": cert_data["affordable_payment_formatted"],
            "max_loan": cert_data["max_loan_formatted"]
        })
        
        # Add stress test if present
        if "stress_test" in cert_data:
            st = cert_data["stress_test"]
            pdf_data["stress_results"] = (
                f"At {st['stress_rate_percent']}%: "
                f"Max Loan {st['stress_max_loan_formatted']} "
                f"(Reduction: {st['reduction_percent']}%)"
            )
            pdf_data["stress_bps"] = st["stress_rate_bps"]
    else:
        pdf_data.update({
            "principal_amount": cert_data["principal_formatted"],
            "monthly_payment": cert_data["monthly_payment_formatted"]
        })
        
        # Add stress test if present
        if "stress_test" in cert_data:
            st = cert_data["stress_test"]
            pdf_data["stress_results"] = (
                f"At {st['stress_rate_percent']}%: "
                f"Monthly Payment {st['stress_payment_formatted']} "
                f"(Increase: {st['increase_percent']}%)"
            )
            pdf_data["stress_bps"] = st["stress_rate_bps"]
    
    return pdf_data
