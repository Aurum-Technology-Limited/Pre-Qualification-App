# Technical Documentation - Pre-Qualification App

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Frontend Architecture](#frontend-architecture)
3. [Backend Architecture](#backend-architecture)
4. [Database Design](#database-design)
5. [Authentication Flow](#authentication-flow)
6. [API Design](#api-design)
7. [Calculation Engine](#calculation-engine)
8. [PDF Generation](#pdf-generation)
9. [Security Implementation](#security-implementation)
10. [Performance Optimization](#performance-optimization)

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Browser                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           React Application (Port 3000)            │    │
│  │                                                     │    │
│  │  - Auth Context (Supabase Client)                 │    │
│  │  - Calculator Component                            │    │
│  │  - Auth Component                                  │    │
│  │  - Tailwind CSS Styling                           │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ HTTPS / WebSocket
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                    Nginx Reverse Proxy                       │
│                                                              │
│  - Routes /api/* → Backend (8001)                           │
│  - Routes /* → Frontend (3000)                              │
│  - SSL/TLS Termination                                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌──────────────────┐
│   Frontend    │   │     Backend      │
│  React Server │   │  FastAPI Server  │
│  (Port 3000)  │   │   (Port 8001)    │
│               │   │                  │
│  - Serve UI   │   │  - API Endpoints │
│  - Hot Reload │   │  - Auth Verify   │
└───────────────┘   │  - Calculations  │
                    │  - PDF Gen       │
                    └────────┬─────────┘
                             │
                             │ REST API
                             │
                    ┌────────▼──────────┐
                    │     Supabase      │
                    │   (PostgreSQL)    │
                    │                   │
                    │  - Auth Service   │
                    │  - PostgreSQL DB  │
                    │  - RLS Policies   │
                    │  - JWT Tokens     │
                    └───────────────────┘
```

### Technology Stack Details

#### Frontend Stack
```javascript
{
  "framework": "React 18.2.0",
  "language": "JavaScript (ES6+)",
  "styling": "Tailwind CSS 3.4.0",
  "http": "Axios 1.6.2",
  "auth": "@supabase/supabase-js 2.76.1",
  "state": "React Context API",
  "build": "React Scripts 5.0.1 (Webpack)"
}
```

#### Backend Stack
```python
{
  "framework": "FastAPI 0.104.1",
  "language": "Python 3.11",
  "server": "Uvicorn 0.24.0",
  "pdf": "ReportLab 4.0.7",
  "database_client": "supabase-py",
  "validation": "Pydantic 2.5.0",
  "async": "asyncio (native)"
}
```

---

## Frontend Architecture

### Component Hierarchy

```
App (AuthProvider)
├── AuthContext (Session Management)
│   ├── User State
│   ├── Session State
│   └── Auth Methods (signUp, signIn, signOut)
│
├── Auth Component (Login/Signup)
│   ├── Login Form
│   ├── Signup Form
│   └── Toggle Button
│
└── Calculator Component (Main App)
    ├── Navigation Bar
    │   ├── App Title
    │   ├── User Email
    │   └── Logout Button
    │
    ├── Calculation Form
    │   ├── Tab Selector (Affordability / Payment)
    │   ├── Applicant Info Fields
    │   ├── Financial Input Fields
    │   ├── DSR Slider (Affordability only)
    │   ├── Loan Parameters
    │   ├── Reset Button
    │   └── Calculate Button
    │
    ├── Results Display
    │   ├── Certificate ID
    │   ├── Calculation Results
    │   ├── Stress Test Results
    │   ├── Financial Details Grid
    │   └── New Calculation Button
    │
    └── Certificate Section
        ├── Download Button
        └── Certificate Info
```

### State Management

```javascript
// AuthContext State
{
  user: {
    id: "uuid",
    email: "user@example.com",
    user_metadata: { full_name: "User Name" }
  },
  session: {
    access_token: "jwt-token",
    refresh_token: "refresh-token",
    expires_at: timestamp
  },
  loading: false
}

// Calculator Component State
{
  calculationType: "AFFORDABILITY" | "PAYMENT",
  loading: false,
  results: {...},
  error: null,
  
  // Form fields
  applicantName: "",
  applicantEmail: "",
  grossIncome: "",
  dsrRatio: 0.4,
  monthlyObligations: "",
  principalAmount: "",
  interestRate: "",
  termYears: "20",
  stressRateBps: "",
  currency: "TTD",
  validityDays: "90"
}
```

### API Integration

```javascript
// API Call with Authentication
const { data: { session } } = await supabase.auth.getSession();

const response = await axios.post(
  `${BACKEND_URL}/api/calculate`,
  requestData,
  {
    headers: {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json'
    }
  }
);
```

---

## Backend Architecture

### Application Structure

```python
from fastapi import FastAPI, Depends, Header

app = FastAPI()

# Middleware
app.add_middleware(CORSMiddleware, ...)

# Authentication Dependency
async def get_current_user(authorization: str = Header(...)):
    # Extract and verify JWT token
    # Return user data and token
    pass

# Endpoints
@app.get("/api/health")
@app.post("/api/calculate", dependencies=[Depends(get_current_user)])
@app.post("/api/generate-certificate/{id}", dependencies=[...])
@app.get("/api/certificates/{id}", dependencies=[...])
@app.get("/api/certificates", dependencies=[...])
```

### Request Flow

```
1. Request arrives at FastAPI
   ↓
2. CORS middleware checks origin
   ↓
3. Auth dependency extracts JWT from header
   ↓
4. Supabase verifies token and returns user
   ↓
5. Create user-scoped Supabase client
   ↓
6. Execute business logic (calculations)
   ↓
7. Store/retrieve data with RLS context
   ↓
8. Return response to client
```

### Calculation Engine

```python
import math

def calculate_monthly_payment(principal, annual_rate, term_years):
    """
    Calculate monthly payment using annuity formula.
    
    Formula: P * [r * (1 + r)^n] / [(1 + r)^n - 1]
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (decimal)
        term_years: Loan term in years
    
    Returns:
        Monthly payment amount
    """
    if annual_rate == 0:
        return round(principal / (term_years * 12), 2)
    
    monthly_rate = annual_rate / 12
    num_payments = term_years * 12
    
    payment = principal * (monthly_rate * math.pow(1 + monthly_rate, num_payments)) / \
              (math.pow(1 + monthly_rate, num_payments) - 1)
    
    return round(payment, 2)

def calculate_max_loan(affordable_payment, annual_rate, term_years):
    """
    Calculate maximum loan from affordable payment.
    
    Formula: Payment * [(1 - (1 + r)^-n) / r]
    
    Args:
        affordable_payment: Maximum monthly payment
        annual_rate: Annual interest rate (decimal)
        term_years: Loan term in years
    
    Returns:
        Maximum loan amount
    """
    if annual_rate == 0:
        return round(affordable_payment * term_years * 12, 2)
    
    monthly_rate = annual_rate / 12
    num_payments = term_years * 12
    
    max_loan = affordable_payment * (1 - math.pow(1 + monthly_rate, -num_payments)) / monthly_rate
    
    return round(max_loan, 2)
```

---

## Database Design

### Entity Relationship Diagram

```
┌────────────────────┐
│    auth.users      │ (Managed by Supabase)
├────────────────────┤
│ id (UUID) PK       │
│ email              │
│ encrypted_password │
│ email_confirmed_at │
│ created_at         │
│ user_metadata      │
└────────┬───────────┘
         │
         │ 1:N
         │
         ▼
┌────────────────────┐
│   certificates     │
├────────────────────┤
│ id (BIGSERIAL) PK  │
│ certificate_id UK  │
│ user_id FK ────────┘
│ calculation_type   │
│ applicant (JSONB)  │
│ currency           │
│ issue_date         │
│ expiry_date        │
│ validity_days      │
│ ... (financial data)
│ stress_test (JSONB)│
│ created_at         │
│ pdf_generated      │
│ pdf_path           │
└────────────────────┘
```

### Data Types

```sql
-- Numeric fields
NUMERIC          -- For financial calculations (no rounding errors)
INTEGER          -- For whole numbers (term_years, validity_days)
BIGSERIAL        -- For auto-incrementing IDs

-- Text fields
TEXT             -- For strings (certificate_id, email, etc.)
UUID             -- For user_id (references auth.users)

-- JSON fields
JSONB            -- For flexible nested data (applicant, stress_test)
                 -- Indexed and queryable

-- Date/Time
TIMESTAMP WITH TIME ZONE  -- For created_at (includes timezone)
TEXT             -- For issue_date, expiry_date (formatted strings)

-- Boolean
BOOLEAN          -- For pdf_generated flag
```

### Indexing Strategy

```sql
-- Primary key (automatic)
PRIMARY KEY (id)

-- Unique constraint for certificate lookups
UNIQUE (certificate_id)

-- Foreign key index for user queries
INDEX idx_certificates_user_id ON certificates(user_id)

-- Timestamp index for sorting (DESC for recent-first)
INDEX idx_certificates_created_at ON certificates(created_at DESC)

-- Certificate ID index for fast lookups
INDEX idx_certificates_certificate_id ON certificates(certificate_id)
```

---

## Authentication Flow

### Sign Up Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │
     │ 1. Enter email, password, name
     ▼
┌────────────┐
│  Frontend  │
└─────┬──────┘
      │
      │ 2. supabase.auth.signUp({...})
      ▼
┌──────────────┐
│   Supabase   │
│   Auth API   │
└──────┬───────┘
       │
       │ 3. Create user in auth.users
       │ 4. Return session with JWT tokens
       ▼
┌────────────┐
│  Frontend  │
└─────┬──────┘
      │
      │ 5. Store session in AuthContext
      │ 6. Redirect to Calculator
      ▼
┌─────────┐
│  User   │
└─────────┘
```

### Sign In Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │
     │ 1. Enter email, password
     ▼
┌────────────┐
│  Frontend  │
└─────┬──────┘
      │
      │ 2. supabase.auth.signInWithPassword({...})
      ▼
┌──────────────┐
│   Supabase   │
│   Auth API   │
└──────┬───────┘
       │
       │ 3. Verify credentials
       │ 4. Return session with JWT tokens
       ▼
┌────────────┐
│  Frontend  │
└─────┬──────┘
      │
      │ 5. Store session
      │ 6. Redirect to Calculator
      ▼
┌─────────┐
│  User   │
└─────────┘
```

### API Request Authentication Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │
     │ 1. Click "Calculate"
     ▼
┌────────────┐
│  Frontend  │
└─────┬──────┘
      │
      │ 2. Get session.access_token
      │ 3. axios.post(..., { headers: { Authorization: "Bearer <token>" }})
      ▼
┌────────────┐
│   Backend  │
└─────┬──────┘
      │
      │ 4. Extract token from header
      │ 5. supabase.auth.get_user(token)
      ▼
┌──────────────┐
│   Supabase   │
└──────┬───────┘
       │
       │ 6. Verify JWT signature
       │ 7. Return user data
       ▼
┌────────────┐
│   Backend  │
└─────┬──────┘
      │
      │ 8. Create user-scoped DB client
      │ 9. Execute business logic
      │ 10. RLS policies enforce user_id check
      ▼
┌──────────────┐
│   Database   │
└──────┬───────┘
       │
       │ 11. Return data
       ▼
┌────────────┐
│   Backend  │
└─────┬──────┘
      │
      │ 12. Return response
      ▼
┌────────────┐
│  Frontend  │
└─────┬──────┘
      │
      │ 13. Display results
      ▼
┌─────────┐
│  User   │
└─────────┘
```

### Token Refresh

```javascript
// Automatic token refresh (handled by Supabase client)
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'TOKEN_REFRESHED') {
    console.log('Token refreshed automatically');
    // Update local session
    setSession(session);
  }
});
```

---

## API Design

### RESTful Principles

```
GET    /api/health                      → Health check
POST   /api/calculate                   → Create calculation
POST   /api/generate-certificate/:id    → Generate PDF
GET    /api/certificates/:id            → Get single certificate
GET    /api/certificates                → List certificates
```

### Request/Response Patterns

#### Success Response (200)
```json
{
  "certificate_id": "ABC123",
  "calculation_type": "AFFORDABILITY",
  "max_loan_amount": 726555.33,
  "max_loan_formatted": "TTD $726,555.33",
  ...
}
```

#### Error Response (4xx/5xx)
```json
{
  "detail": "Error message describing what went wrong"
}
```

#### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "affordability_input", "gross_monthly_income"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### Input Validation

```python
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
```

---

## PDF Generation

### Template Structure

```python
def generate_certificate_pdf(certificate_data):
    # Initialize PDF
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Layout sections:
    # 1. Header (0px to 120px from top)
    #    - Lime green background
    #    - App title and subtitle
    
    # 2. Certificate ID & Dates (120px to 150px)
    #    - Left: Certificate ID
    #    - Right: Issue and expiry dates
    
    # 3. Applicant Info (200px to 250px)
    #    - Name, email, phone
    
    # 4. Results Section (300px to 450px)
    #    - Light green background box
    #    - Calculation results
    #    - Highlighted max loan / payment
    
    # 5. Stress Test (if applicable)
    #    - Orange warning section
    
    # 6. Disclaimer (bottom 150px)
    #    - Important legal text
    
    # 7. Footer (bottom 50px)
    #    - Company info and website
    
    c.save()
    return filepath
```

### Color Usage

```python
lime_green = HexColor('#32CD32')  # Primary brand color
dark_green = HexColor('#228B22')  # Text and accents
white = HexColor('#FFFFFF')       # Header text
light_green = HexColor('#F0FFF0') # Results background
orange = HexColor('#FD7E14')      # Stress test warning
```

---

## Security Implementation

### Row-Level Security (RLS)

```sql
-- Enable RLS on table
ALTER TABLE certificates ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own data
CREATE POLICY "view_own" ON certificates
  FOR SELECT
  USING (auth.uid() = user_id);

-- How it works:
-- 1. Client sends JWT token
-- 2. Backend creates authenticated Supabase client
-- 3. RLS policies check: auth.uid() = user_id
-- 4. Only matching rows returned
```

### JWT Token Verification

```python
async def get_current_user(authorization: str = Header(...)):
    # Extract token
    token = authorization.replace("Bearer ", "")
    
    # Verify with Supabase
    user_response = supabase.auth.get_user(token)
    
    if not user_response or not user_response.user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Return verified user
    return {"user": user_response.user, "token": token}
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Optimization

### Database Optimization

```sql
-- Indexes for fast queries
CREATE INDEX idx_user_id ON certificates(user_id);
CREATE INDEX idx_created_at ON certificates(created_at DESC);
CREATE INDEX idx_certificate_id ON certificates(certificate_id);

-- JSONB indexes for nested queries (if needed)
CREATE INDEX idx_applicant ON certificates USING GIN (applicant);
```

### Frontend Optimization

```javascript
// Code splitting
import React, { lazy, Suspense } from 'react';
const Calculator = lazy(() => import('./Calculator'));

// Memoization
const formatCurrency = useMemo(() => {
  return (value) => new Intl.NumberFormat('en-US', {...}).format(value);
}, []);

// Debouncing (if needed for real-time validation)
import { debounce } from 'lodash';
const debouncedValidate = debounce(validate, 300);
```

### Backend Optimization

```python
# Async/await for non-blocking operations
async def calculate(request: CalculationRequest, ...):
    # Database queries are async
    result = await supabase.table(...).insert(...).execute()
    
# Response model for automatic validation
class CalculationResponse(BaseModel):
    certificate_id: str
    max_loan_amount: float
    # FastAPI automatically serializes
```

### Caching Strategies

```python
# Cache static PDF templates (if implemented)
from functools import lru_cache

@lru_cache(maxsize=128)
def get_pdf_template():
    return template

# HTTP caching headers
@app.get("/api/health")
def health_check():
    return Response(
        content=json.dumps({"status": "healthy"}),
        headers={"Cache-Control": "public, max-age=60"}
    )
```

---

## Monitoring & Logging

### Backend Logging

```python
import logging

logger = logging.getLogger(__name__)

@app.post("/api/calculate")
async def calculate(...):
    logger.info(f"Calculation request from user {user.id}")
    try:
        # ... logic
        logger.info(f"Calculation successful: {cert_id}")
    except Exception as e:
        logger.error(f"Calculation failed: {str(e)}")
        raise
```

### Error Tracking

```python
# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] RLS policies enabled
- [ ] HTTPS/SSL configured
- [ ] CORS origins restricted
- [ ] Rate limiting implemented
- [ ] Monitoring/logging set up
- [ ] Error tracking configured
- [ ] Backup strategy in place
- [ ] Health check endpoint tested
- [ ] Load testing completed
- [ ] Security audit performed

---

**Document Version**: 1.0  
**Last Updated**: October 2024  
**Maintained By**: Development Team