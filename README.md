# Pre-Qualification App - Mortgage Calculator

## 📋 Overview

The Pre-Qualification App is a full-stack mortgage pre-qualification calculator that helps users determine their borrowing capacity or calculate monthly payments for potential home loans. The application generates professional PDF certificates with unique IDs and provides stress testing capabilities to assess loan viability under adverse conditions.

## 🎯 Purpose

This application serves as a comprehensive tool for:
- **Loan Officers**: Quickly generate pre-qualification certificates for clients
- **Home Buyers**: Understand their borrowing capacity before house hunting
- **Financial Advisors**: Assess client affordability and payment scenarios
- **Mortgage Brokers**: Provide instant pre-qualification estimates

## ✨ Key Features

### 1. Dual Calculation Modes
- **Affordability Assessment (Path A)**: Calculate maximum loan amount based on income, debt service ratio, and existing obligations
- **Payment Calculation (Path B)**: Calculate monthly payments for a specified loan amount

### 2. Advanced Features
- 🔐 **User Authentication**: Secure email/password login with Supabase
- 📊 **Stress Testing**: Apply additional basis points to assess loan viability under higher rates
- 💱 **Multi-Currency Support**: TTD, USD, CAD with proper formatting
- 📄 **PDF Certificates**: Professional certificates with unique IDs and lime green branding
- 🔒 **Data Isolation**: Each user can only access their own certificates
- 📅 **Validity Periods**: Configurable certificate expiry (60-180 days)
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices

### 3. User Experience
- Clean, intuitive interface with lime green (#32CD32) branding
- Real-time form validation
- Interactive DSR slider (10% - 80%)
- Loading states and error handling
- Certificate history and retrieval

---

## 🏗️ Tech Stack

### Frontend
- **Framework**: React 18.2.0
- **Styling**: Tailwind CSS 3.4.0 (customized with lime green theme)
- **HTTP Client**: Axios 1.6.2
- **Authentication**: @supabase/supabase-js 2.76.1
- **State Management**: React Context API (AuthContext)
- **Build Tool**: React Scripts 5.0.1

### Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.11
- **Server**: Uvicorn 0.24.0
- **PDF Generation**: ReportLab 4.0.7
- **Database Client**: Supabase Python SDK (supabase-py)
- **Authentication**: JWT token verification via Supabase
- **Environment**: Python-dotenv 1.0.0

### Database
- **Platform**: Supabase (PostgreSQL)
- **Features**:
  - Row-Level Security (RLS)
  - JSONB support for flexible data storage
  - Real-time capabilities (not currently used)
  - Built-in authentication

### Authentication & Security
- **Provider**: Supabase Auth
- **Method**: Email/Password
- **Token Type**: JWT (JSON Web Tokens)
- **Session Management**: Automatic token refresh
- **Security**: Row-Level Security policies for data isolation

### Infrastructure
- **Process Manager**: Supervisor (for backend and frontend)
- **Reverse Proxy**: Nginx (for routing /api requests)
- **Development**: Hot reload enabled for both frontend and backend

---

## 📐 Calculation Formulas

### Affordability Assessment (Path A)

Calculates the maximum loan amount a borrower can afford based on their financial situation.

#### Formula Breakdown:

1. **Calculate Affordable Monthly Payment**:
   ```
   Affordable Payment = (Gross Monthly Income × DSR) - Existing Monthly Obligations
   ```
   - **DSR**: Debt Service Ratio (typically 0.1 to 0.8 or 10% to 80%)
   - **Example**: Income $30,000 × 40% DSR = $12,000 - $4,000 obligations = $8,000

2. **Calculate Maximum Loan Amount** (Annuity Formula):
   ```
   Max Loan = Affordable Payment × [(1 - (1 + r)^-n) / r]
   ```
   Where:
   - `r` = monthly interest rate (annual rate ÷ 12)
   - `n` = total number of payments (years × 12)
   - `(1 + r)^-n` = discount factor

   **Special Case**: If interest rate = 0:
   ```
   Max Loan = Affordable Payment × n
   ```

3. **Example Calculation**:
   - Affordable Payment: $8,000
   - Annual Rate: 12% → Monthly Rate: 1% (0.01)
   - Term: 20 years → Payments: 240
   
   ```
   Max Loan = $8,000 × [(1 - (1.01)^-240) / 0.01]
            = $8,000 × 90.819416
            = $726,555.33
   ```

### Payment Calculation (Path B)

Calculates the monthly payment required for a given loan amount.

#### Formula:
```
Monthly Payment = Principal × [r × (1 + r)^n] / [(1 + r)^n - 1]
```

Where:
- `Principal` = loan amount
- `r` = monthly interest rate
- `n` = number of monthly payments
- `(1 + r)^n` = compound interest factor

**Special Case**: If interest rate = 0:
```
Monthly Payment = Principal / n
```

#### Example Calculation:
- Principal: $800,000
- Annual Rate: 12% → Monthly Rate: 1% (0.01)
- Term: 20 years → Payments: 240

```
Monthly Payment = $800,000 × [0.01 × (1.01)^240] / [(1.01)^240 - 1]
                = $800,000 × [0.01 × 10.892554] / [9.892554]
                = $800,000 × 0.011011
                = $8,808.69
```

### Stress Testing

Applies additional interest rate to test loan viability under adverse conditions.

#### Formula:
```
Stressed Rate = Base Annual Rate + (Stress Basis Points / 10,000)
```

**Example**:
- Base Rate: 12% (0.12)
- Stress: 200 basis points
- Stressed Rate: 0.12 + (200 / 10,000) = 0.12 + 0.02 = 0.14 (14%)

#### Impact on Affordability:
```
Reduction % = [(Base Max Loan - Stressed Max Loan) / Base Max Loan] × 100
```

**Example**:
- Base Max Loan: $726,555
- Stressed Max Loan (14%): $643,335
- Reduction: (83,220 / 726,555) × 100 = 11.45%

#### Impact on Payments:
```
Increase % = [(Stressed Payment - Base Payment) / Base Payment] × 100
```

**Example**:
- Base Payment (12%): $8,808.69
- Stressed Payment (14%): $9,948.17
- Increase: (1,139.48 / 8,808.69) × 100 = 12.94%

### Additional Metrics

#### Total Amount Paid:
```
Total Paid = Monthly Payment × Number of Payments
```

#### Total Interest Paid:
```
Total Interest = Total Paid - Principal
```

---

## 🗄️ Database Schema

### Certificates Table

```sql
CREATE TABLE public.certificates (
    id BIGSERIAL PRIMARY KEY,
    certificate_id TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    calculation_type TEXT NOT NULL,
    applicant JSONB NOT NULL,
    currency TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    validity_days INTEGER NOT NULL,
    
    -- Affordability fields
    gross_monthly_income NUMERIC,
    dsr_ratio NUMERIC,
    monthly_obligations NUMERIC,
    affordable_payment NUMERIC,
    affordable_payment_formatted TEXT,
    max_loan_amount NUMERIC,
    max_loan_formatted TEXT,
    
    -- Payment fields
    principal_amount NUMERIC,
    principal_formatted TEXT,
    monthly_payment NUMERIC,
    monthly_payment_formatted TEXT,
    total_payments NUMERIC,
    total_payments_formatted TEXT,
    total_interest NUMERIC,
    total_interest_formatted TEXT,
    
    -- Common fields
    annual_interest_rate NUMERIC NOT NULL,
    interest_rate_percent NUMERIC NOT NULL,
    term_years INTEGER NOT NULL,
    stress_test JSONB,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pdf_generated BOOLEAN DEFAULT FALSE,
    pdf_path TEXT
);
```

### Indexes
```sql
CREATE INDEX idx_certificates_certificate_id ON certificates(certificate_id);
CREATE INDEX idx_certificates_user_id ON certificates(user_id);
CREATE INDEX idx_certificates_created_at ON certificates(created_at DESC);
```

### Row-Level Security Policies

```sql
-- Users can only view their own certificates
CREATE POLICY "Users can view own certificates" ON certificates
    FOR SELECT USING (auth.uid() = user_id);

-- Users can only insert their own certificates
CREATE POLICY "Users can insert own certificates" ON certificates
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can only update their own certificates
CREATE POLICY "Users can update own certificates" ON certificates
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can only delete their own certificates
CREATE POLICY "Users can delete own certificates" ON certificates
    FOR DELETE USING (auth.uid() = user_id);
```

---

## 🔌 API Endpoints

### Health Check
```http
GET /api/health
```
**Description**: Check if the API is running

**Response**:
```json
{
  "status": "healthy",
  "service": "Pre-Qualification App API"
}
```

---

### Calculate Pre-Qualification
```http
POST /api/calculate
```
**Description**: Perform affordability or payment calculation

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body (Affordability)**:
```json
{
  "calculation_type": "AFFORDABILITY",
  "affordability_input": {
    "gross_monthly_income": 30000,
    "dsr_ratio": 0.4,
    "monthly_obligations": 4000,
    "annual_interest_rate": 0.12,
    "term_years": 20,
    "stress_rate_bps": 200
  },
  "applicant": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-234-567-8900"
  },
  "currency": "TTD",
  "validity_days": 90
}
```

**Request Body (Payment)**:
```json
{
  "calculation_type": "PAYMENT",
  "payment_input": {
    "principal_amount": 800000,
    "annual_interest_rate": 0.12,
    "term_years": 20,
    "stress_rate_bps": 200
  },
  "applicant": {
    "name": "Jane Smith",
    "email": "jane@example.com"
  },
  "currency": "TTD",
  "validity_days": 90
}
```

**Response**:
```json
{
  "certificate_id": "A1B2C3D4",
  "calculation_type": "AFFORDABILITY",
  "max_loan_amount": 726555.33,
  "max_loan_formatted": "TTD $726,555.33",
  "affordable_payment": 8000.00,
  "affordable_payment_formatted": "TTD $8,000.00",
  "stress_test": {
    "stress_rate_bps": 200,
    "stress_annual_rate": 0.14,
    "stress_rate_percent": 14.0,
    "stress_max_loan": 643334.63,
    "stress_max_loan_formatted": "TTD $643,334.63",
    "reduction_amount": 83220.70,
    "reduction_percent": 11.45
  },
  "issue_date": "2024-10-22",
  "expiry_date": "2025-01-20",
  "validity_days": 90
}
```

---

### Generate Certificate PDF
```http
POST /api/generate-certificate/{certificate_id}
```
**Description**: Generate and download PDF certificate

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Response**: PDF file download

---

### Get Certificate Details
```http
GET /api/certificates/{certificate_id}
```
**Description**: Retrieve details of a specific certificate

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Response**: Certificate data object

---

### List User Certificates
```http
GET /api/certificates?limit=10
```
**Description**: List user's recent certificates

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Query Parameters**:
- `limit` (optional): Number of certificates to return (default: 10)

**Response**:
```json
{
  "certificates": [...],
  "count": 10
}
```

---

## 🎨 Design System

### Color Palette
- **Primary**: Lime Green `#32CD32`
- **Secondary**: White `#FFFFFF`
- **Accent**: Dark Green `#228B22`
- **Error**: Red `#DC3545`
- **Warning**: Orange `#FD7E14`
- **Success**: Dark Green `#228B22`

### Typography
- **Font Family**: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto'
- **Headers**: Bold, Lime Green
- **Body**: Regular, Dark Green
- **Amounts**: Bold, Large, Lime Green

### Components
- **Buttons**: Lime green gradient with hover effects
- **Input Fields**: Lime green focus border
- **Cards**: White with lime green accents
- **Tabs**: Lime green active indicator
- **Sliders**: Lime green thumb

---

## 📱 User Guide

### Getting Started

1. **Sign Up**
   - Navigate to the application
   - Click "Sign Up"
   - Enter your name, email, and password (min 6 characters)
   - Click "Sign Up" button
   - You'll be automatically logged in

2. **Sign In**
   - Enter your email and password
   - Click "Sign In"
   - Access the calculator dashboard

### Using the Calculator

#### Affordability Assessment
1. Select the **Affordability Assessment** tab
2. Fill in:
   - Your full name
   - Email address (optional)
   - Phone number (optional)
   - Gross monthly income
   - Monthly debt obligations (if any)
   - Adjust DSR ratio slider (default 40%)
   - Annual interest rate
   - Loan term (years)
   - Stress test rate (optional, in basis points)
3. Click **Calculate**
4. View your maximum loan amount and stress test results
5. Click **Download Certificate (PDF)** to save

#### Payment Calculation
1. Select the **Payment Calculation** tab
2. Fill in:
   - Your full name
   - Email address (optional)
   - Principal loan amount
   - Annual interest rate
   - Loan term (years)
   - Stress test rate (optional)
3. Click **Calculate**
4. View monthly payment, total paid, and total interest
5. Download your certificate

### Understanding Results

#### Affordability Results
- **Affordable Monthly Payment**: Amount you can afford based on income and DSR
- **Maximum Loan Amount**: The largest loan you qualify for
- **Stress Test**: Shows reduced loan amount at higher interest rate

#### Payment Results
- **Monthly Payment**: Regular payment required
- **Total Amount Paid**: Sum of all payments over loan term
- **Total Interest**: Interest paid over the life of the loan
- **Stress Test**: Shows increased payment at higher interest rate

### Certificate Management
- All your certificates are automatically saved
- Each certificate has a unique ID
- Certificates are valid for 60-180 days (you choose)
- Only you can access your certificates

---

## 🚀 Deployment

### Environment Variables

**Backend** (`/app/backend/.env`):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
BACKEND_PORT=8001
FRONTEND_URL=http://localhost:3000
```

**Frontend** (`/app/frontend/.env`):
```env
REACT_APP_BACKEND_URL=https://your-domain.com
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
PORT=3000
DANGEROUSLY_DISABLE_HOST_CHECK=true
FAST_REFRESH=false
```

### Running Locally

1. **Install Dependencies**:
   ```bash
   # Backend
   cd /app/backend
   pip install -r requirements.txt
   
   # Frontend
   cd /app/frontend
   yarn install
   ```

2. **Start Services**:
   ```bash
   # Using Supervisor (recommended)
   sudo supervisorctl restart all
   
   # Or manually
   # Backend
   cd /app/backend && python server.py
   
   # Frontend
   cd /app/frontend && yarn start
   ```

3. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

### Production Deployment

1. **Build Frontend**:
   ```bash
   cd /app/frontend
   yarn build
   ```

2. **Configure Environment**:
   - Update `.env` files with production URLs
   - Set up SSL/TLS certificates
   - Configure firewall rules

3. **Database Setup**:
   - Create Supabase project
   - Run SQL migrations
   - Enable RLS policies

4. **Deploy**:
   - Use Docker for containerization
   - Set up reverse proxy (Nginx)
   - Configure process manager (Supervisor/PM2)
   - Set up monitoring and logging

---

## 🔒 Security Features

### Authentication
- JWT-based authentication via Supabase
- Secure password hashing (handled by Supabase)
- Session token automatic refresh
- Token expiration handling

### Authorization
- Row-Level Security (RLS) policies
- User-scoped database queries
- Token verification on all protected endpoints

### Data Protection
- HTTPS enforced in production
- CORS properly configured
- SQL injection prevention (parameterized queries)
- XSS protection (React escaping)

### Best Practices
- Environment variables for sensitive data
- No hardcoded credentials
- Secure token storage (httpOnly cookies in production)
- Rate limiting (implement in production)

---

## 🧪 Testing

### Backend Tests
```bash
python /app/tests/test_calculations.py
```

### Health Check
```bash
/app/scripts/health_check.sh
```

### Manual API Testing
```bash
# Test affordability
curl -X POST http://localhost:8001/api/calculate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## 📊 Performance

- **API Response Time**: ~200ms average
- **Calculation Accuracy**: Exact to specification (±$0.01)
- **PDF Generation**: ~1 second
- **Page Load**: ~1 second
- **Database Queries**: Indexed for optimal performance

---

## 🐛 Troubleshooting

See [TROUBLESHOOTING.md](/app/TROUBLESHOOTING.md) for common issues and solutions.

---

## 📄 License

Copyright © 2024 Pre-Qualification App. All rights reserved.

---

## 📞 Support

For issues or questions:
- Check logs: `/var/log/supervisor/`
- Run health check: `/app/scripts/health_check.sh`
- API documentation: http://localhost:8001/docs

---

## 🎯 Roadmap

### Potential Future Features
- [ ] Multiple applicant support (co-borrowers)
- [ ] Property tax and insurance calculator
- [ ] Amortization schedule generation
- [ ] Email delivery of certificates
- [ ] Dashboard with analytics
- [ ] Export to Excel/CSV
- [ ] Mobile app (React Native)
- [ ] Integration with credit bureaus
- [ ] Saved templates
- [ ] Admin panel for loan officers

---

**Built with ❤️ using React, FastAPI, and Supabase**