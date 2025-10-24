from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime, timedelta
import os
import math
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from pathlib import Path

# Load environment variables
load_dotenv()

app = FastAPI(title="Pre-Qualification App API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pre-qualification-app-yq1a-6mq1m82ra-marc-alleynes-projects.vercel.app",
        "https://mortgage-preapp.preview.emergentagent.com",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase Connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ensure PDF directory exists
PDF_DIR = Path("/app/backend/certificates")
PDF_DIR.mkdir(exist_ok=True)

# Pydantic Models
class ApplicantInfo(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class AffordabilityInput(BaseModel):
    gross_monthly_income: float = Field(gt=0, le=1000000)
    dsr_ratio: float = Field(ge=0.1, le=0.8)
    monthly_obligations: float = Field(ge=0)
    annual_interest_rate: float = Field(gt=0.001, le=0.50)
    term_years: int = Field(ge=1, le=50)
    stress_rate_bps: Optional[int] = Field(default=0, ge=0, le=1000)
    
    @field_validator('monthly_obligations')
    @classmethod
    def validate_obligations(cls, v, info):
        if 'gross_monthly_income' in info.data and v >= info.data['gross_monthly_income']:
            raise ValueError('Monthly obligations must be less than gross income')
        return v

class PaymentInput(BaseModel):
    principal_amount: float = Field(gt=0, le=50000000)
    annual_interest_rate: float = Field(gt=0.001, le=0.50)
    term_years: int = Field(ge=1, le=50)
    stress_rate_bps: Optional[int] = Field(default=0, ge=0, le=1000)

class CalculationRequest(BaseModel):
    calculation_type: Literal["AFFORDABILITY", "PAYMENT"]
    affordability_input: Optional[AffordabilityInput] = None
    payment_input: Optional[PaymentInput] = None
    applicant: ApplicantInfo
    currency: str = "TTD"
    validity_days: int = Field(default=90, ge=60, le=180)

# Calculation Functions
def calculate_monthly_payment(principal: float, annual_rate: float, term_years: int) -> float:
    """Calculate monthly payment using annuity formula"""
    if annual_rate == 0:
        return round(principal / (term_years * 12), 2)
    
    monthly_rate = annual_rate / 12
    num_payments = term_years * 12
    
    payment = principal * (monthly_rate * math.pow(1 + monthly_rate, num_payments)) / \
              (math.pow(1 + monthly_rate, num_payments) - 1)
    
    return round(payment, 2)

def calculate_max_loan(affordable_payment: float, annual_rate: float, term_years: int) -> float:
    """Calculate maximum loan amount from affordable payment"""
    if annual_rate == 0:
        return round(affordable_payment * term_years * 12, 2)
    
    monthly_rate = annual_rate / 12
    num_payments = term_years * 12
    
    max_loan = affordable_payment * (1 - math.pow(1 + monthly_rate, -num_payments)) / monthly_rate
    
    return round(max_loan, 2)

def format_currency(amount: float, currency: str = "TTD") -> str:
    """Format amount as currency"""
    return f"{currency} ${amount:,.2f}"

def generate_certificate_pdf(certificate_data: dict) -> str:
    """Generate PDF certificate and return file path"""
    cert_id = certificate_data['certificate_id']
    filename = f"{cert_id}.pdf"
    filepath = PDF_DIR / filename
    
    # Create PDF
    c = canvas.Canvas(str(filepath), pagesize=letter)
    width, height = letter
    
    # Colors
    lime_green = HexColor('#32CD32')
    dark_green = HexColor('#228B22')
    white = HexColor('#FFFFFF')
    
    # Header with lime green background
    c.setFillColor(lime_green)
    c.rect(0, height - 120, width, 120, fill=1, stroke=0)
    
    # Company name and logo
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width / 2, height - 60, "Pre-Qualification App")
    
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 90, "Pre-Qualification Certificate")
    
    # Certificate ID and dates
    c.setFillColor(dark_green)
    c.setFont("Helvetica", 10)
    y_pos = height - 150
    c.drawString(50, y_pos, f"Certificate ID: {cert_id}")
    c.drawRightString(width - 50, y_pos, f"Issue Date: {certificate_data['issue_date']}")
    c.drawRightString(width - 50, y_pos - 15, f"Expiry Date: {certificate_data['expiry_date']}")
    
    # Applicant Information
    y_pos -= 50
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(lime_green)
    c.drawString(50, y_pos, "Applicant Information")
    
    c.setFillColor(dark_green)
    c.setFont("Helvetica", 11)
    y_pos -= 25
    c.drawString(70, y_pos, f"Name: {certificate_data['applicant_name']}")
    if certificate_data.get('applicant_email'):
        y_pos -= 20
        c.drawString(70, y_pos, f"Email: {certificate_data['applicant_email']}")
    
    # Results Section
    y_pos -= 40
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(lime_green)
    c.drawString(50, y_pos, "Assessment Results")
    
    # Draw results box
    y_pos -= 30
    c.setFillColor(HexColor('#F0FFF0'))
    c.rect(50, y_pos - 150, width - 100, 150, fill=1, stroke=1)
    c.setStrokeColor(lime_green)
    c.setLineWidth(2)
    c.rect(50, y_pos - 150, width - 100, 150, fill=0, stroke=1)
    
    # Results text
    c.setFillColor(dark_green)
    c.setFont("Helvetica", 11)
    y_pos -= 25
    
    calc_type = certificate_data['calculation_type']
    if calc_type == "AFFORDABILITY":
        c.drawString(70, y_pos, f"Gross Monthly Income: {certificate_data['gross_income']}")
        y_pos -= 20
        c.drawString(70, y_pos, f"DSR Ratio: {certificate_data['dsr_ratio']}%")
        y_pos -= 20
        c.drawString(70, y_pos, f"Monthly Obligations: {certificate_data['monthly_obligations']}")
        y_pos -= 20
        c.drawString(70, y_pos, f"Affordable Monthly Payment: {certificate_data['affordable_payment']}")
        y_pos -= 25
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(lime_green)
        c.drawString(70, y_pos, f"Maximum Loan Amount: {certificate_data['max_loan']}")
    else:
        c.drawString(70, y_pos, f"Principal Loan Amount: {certificate_data['principal_amount']}")
        y_pos -= 25
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(lime_green)
        c.drawString(70, y_pos, f"Monthly Payment: {certificate_data['monthly_payment']}")
    
    c.setFont("Helvetica", 11)
    c.setFillColor(dark_green)
    y_pos -= 25
    c.drawString(70, y_pos, f"Annual Interest Rate: {certificate_data['interest_rate']}%")
    y_pos -= 20
    c.drawString(70, y_pos, f"Loan Term: {certificate_data['term_years']} years")
    
    # Stress test results if applicable
    if certificate_data.get('stress_results'):
        y_pos -= 30
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(HexColor('#FD7E14'))
        c.drawString(70, y_pos, f"Stress Test Results (+ {certificate_data['stress_bps']} bps):")
        y_pos -= 20
        c.setFont("Helvetica", 11)
        c.drawString(70, y_pos, certificate_data['stress_results'])
    
    # Disclaimer
    y_pos -= 60
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(lime_green)
    c.drawString(50, y_pos, "Important Disclaimer")
    
    y_pos -= 20
    c.setFont("Helvetica", 9)
    c.setFillColor(dark_green)
    disclaimer_text = [
        "This pre-qualification certificate is an estimate only and does not constitute a loan approval or commitment.",
        "Final loan approval is subject to credit verification, property appraisal, and other lending criteria.",
        f"This certificate is valid for {certificate_data['validity_days']} days from the issue date.",
        "Interest rates and terms are subject to change. Please consult with a loan officer for details."
    ]
    
    for line in disclaimer_text:
        c.drawString(50, y_pos, line)
        y_pos -= 15
    
    # Footer
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(lime_green)
    c.drawCentredString(width / 2, 40, "Pre-Qualification App - Your Mortgage Calculator")
    c.setFont("Helvetica", 8)
    c.setFillColor(dark_green)
    c.drawCentredString(width / 2, 25, "www.prequalificationapp.com")
    
    c.save()
    return str(filepath)

# Authentication helper
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Extract and verify user from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.replace("Bearer ", "")
        
        # Verify token with Supabase
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return {"user": user_response.user, "token": token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

# API Endpoints
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Pre-Qualification App API"}

@app.post("/api/calculate")
async def calculate(request: CalculationRequest, auth_data = Depends(get_current_user)):
    try:
        user = auth_data["user"]
        token = auth_data["token"]
        
        # Create authenticated Supabase client for this request
        user_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        user_supabase.postgrest.auth(token)
        cert_id = str(uuid.uuid4())[:8].upper()
        issue_date = datetime.now()
        expiry_date = issue_date + timedelta(days=request.validity_days)
        
        result = {
            "certificate_id": cert_id,
            "calculation_type": request.calculation_type,
            "applicant": request.applicant.dict(),
            "currency": request.currency,
            "issue_date": issue_date.strftime("%Y-%m-%d"),
            "expiry_date": expiry_date.strftime("%Y-%m-%d"),
            "validity_days": request.validity_days
        }
        
        if request.calculation_type == "AFFORDABILITY":
            if not request.affordability_input:
                raise HTTPException(status_code=400, detail="Affordability input required")
            
            inp = request.affordability_input
            
            # Calculate affordable payment
            affordable_payment = (inp.gross_monthly_income * inp.dsr_ratio) - inp.monthly_obligations
            
            if affordable_payment <= 0:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Negative affordability",
                        "message": "Monthly obligations exceed affordable debt service. Cannot generate certificate.",
                        "affordable_payment": round(affordable_payment, 2)
                    }
                )
            
            # Calculate max loan at base rate
            max_loan = calculate_max_loan(
                affordable_payment,
                inp.annual_interest_rate,
                inp.term_years
            )
            
            result.update({
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
            })
            
            # Stress test if applicable
            if inp.stress_rate_bps > 0:
                stress_rate = inp.annual_interest_rate + (inp.stress_rate_bps / 10000)
                stress_max_loan = calculate_max_loan(
                    affordable_payment,
                    stress_rate,
                    inp.term_years
                )
                
                result.update({
                    "stress_test": {
                        "stress_rate_bps": inp.stress_rate_bps,
                        "stress_annual_rate": stress_rate,
                        "stress_rate_percent": round(stress_rate * 100, 2),
                        "stress_max_loan": stress_max_loan,
                        "stress_max_loan_formatted": format_currency(stress_max_loan, request.currency),
                        "reduction_amount": round(max_loan - stress_max_loan, 2),
                        "reduction_percent": round(((max_loan - stress_max_loan) / max_loan) * 100, 2)
                    }
                })
        
        elif request.calculation_type == "PAYMENT":
            if not request.payment_input:
                raise HTTPException(status_code=400, detail="Payment input required")
            
            inp = request.payment_input
            
            # Calculate monthly payment
            monthly_payment = calculate_monthly_payment(
                inp.principal_amount,
                inp.annual_interest_rate,
                inp.term_years
            )
            
            total_payments = monthly_payment * inp.term_years * 12
            total_interest = total_payments - inp.principal_amount
            
            result.update({
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
            })
            
            # Stress test if applicable
            if inp.stress_rate_bps > 0:
                stress_rate = inp.annual_interest_rate + (inp.stress_rate_bps / 10000)
                stress_payment = calculate_monthly_payment(
                    inp.principal_amount,
                    stress_rate,
                    inp.term_years
                )
                
                result.update({
                    "stress_test": {
                        "stress_rate_bps": inp.stress_rate_bps,
                        "stress_annual_rate": stress_rate,
                        "stress_rate_percent": round(stress_rate * 100, 2),
                        "stress_monthly_payment": stress_payment,
                        "stress_payment_formatted": format_currency(stress_payment, request.currency),
                        "increase_amount": round(stress_payment - monthly_payment, 2),
                        "increase_percent": round(((stress_payment - monthly_payment) / monthly_payment) * 100, 2)
                    }
                })
        
        # Store in Supabase with user_id (using authenticated client)
        certificate_doc = {
            **result,
            "user_id": user.id,
            "created_at": datetime.now().isoformat(),
            "pdf_generated": False
        }
        
        user_supabase.table("certificates").insert(certificate_doc).execute()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-certificate/{certificate_id}")
async def generate_certificate(certificate_id: str, auth_data = Depends(get_current_user)):
    try:
        user = auth_data["user"]
        token = auth_data["token"]
        
        # Create authenticated Supabase client
        user_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        user_supabase.postgrest.auth(token)
        
        # Retrieve certificate data from Supabase (user-specific)
        response = user_supabase.table("certificates").select("*").eq("certificate_id", certificate_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        cert_data = response.data[0]
        
        # Prepare certificate data for PDF
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
        
        if cert_data["calculation_type"] == "AFFORDABILITY":
            pdf_data.update({
                "gross_income": cert_data["affordable_payment_formatted"].replace(cert_data["affordable_payment_formatted"].split()[0], cert_data["currency"]),
                "dsr_ratio": round(cert_data["dsr_ratio"] * 100, 1),
                "monthly_obligations": format_currency(cert_data["monthly_obligations"], cert_data["currency"]),
                "affordable_payment": cert_data["affordable_payment_formatted"],
                "max_loan": cert_data["max_loan_formatted"]
            })
            
            if "stress_test" in cert_data:
                pdf_data["stress_bps"] = cert_data["stress_test"]["stress_rate_bps"]
                pdf_data["stress_results"] = f"{cert_data['stress_test']['stress_max_loan_formatted']} (Reduction: {cert_data['stress_test']['reduction_percent']}%)"
        else:
            pdf_data.update({
                "principal_amount": cert_data["principal_formatted"],
                "monthly_payment": cert_data["monthly_payment_formatted"]
            })
            
            if "stress_test" in cert_data:
                pdf_data["stress_bps"] = cert_data["stress_test"]["stress_rate_bps"]
                pdf_data["stress_results"] = f"{cert_data['stress_test']['stress_payment_formatted']} (Increase: {cert_data['stress_test']['increase_percent']}%)"
        
        # Generate PDF
        pdf_path = generate_certificate_pdf(pdf_data)
        
        # Update Supabase
        user_supabase.table("certificates").update({"pdf_generated": True, "pdf_path": pdf_path}).eq("certificate_id", certificate_id).execute()
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"Pre-Qualification_Certificate_{certificate_id}.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/certificates/{certificate_id}")
async def get_certificate(certificate_id: str, auth_data = Depends(get_current_user)):
    user = auth_data["user"]
    token = auth_data["token"]
    
    user_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    user_supabase.postgrest.auth(token)
    
    response = user_supabase.table("certificates").select("*").eq("certificate_id", certificate_id).execute()
    
    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    return response.data[0]

@app.get("/api/certificates")
async def list_certificates(limit: int = 10, auth_data = Depends(get_current_user)):
    user = auth_data["user"]
    token = auth_data["token"]
    
    user_supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    user_supabase.postgrest.auth(token)
    
    response = user_supabase.table("certificates").select("*").order("created_at", desc=True).limit(limit).execute()
    
    return {"certificates": response.data, "count": len(response.data)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
