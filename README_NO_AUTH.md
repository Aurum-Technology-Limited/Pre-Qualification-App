# Pre-Qualification App

A professional mortgage pre-qualification calculator that helps lenders instantly assess borrower affordability and generate official PDF certificates.

---

## 🎯 What It Does

The Pre-Qualification App provides two core calculation paths:

1. **Affordability Calculator** - Determines maximum loan amount based on income
2. **Payment Calculator** - Calculates monthly payments for a specific loan amount

Both include regulatory stress testing and generate professional PDF certificates.

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** (Python 3.9+) - High-performance API framework
- **Pydantic** - Data validation
- **ReportLab** - PDF generation
- **Uvicorn** - ASGI server

### Frontend
- **React.js** 18.2+ - UI library
- **Tailwind CSS** - Styling framework
- **Axios** - HTTP client
- **Dark Mode** - Built-in theme support

### Architecture
- **RESTful API** - Backend exposes `/api/calculate` and `/api/generate-certificate` endpoints
- **Serverless Ready** - Can be deployed on Vercel, AWS Lambda, Google Cloud Functions
- **CORS Enabled** - Automatic support for all Vercel domains
- **No Database Required** - Stateless operation (certificates stored as PDFs)

---

## 📐 Core Calculations

### 1. Affordability (Income → Maximum Loan)

**Formula:**
```
Step 1: Affordable Payment = (Gross Income × DSR) - Existing Obligations
Step 2: Max Loan = P × [1 - (1 + r)^(-n)] / r

Where:
- P = Affordable monthly payment
- r = Monthly interest rate (Annual Rate ÷ 12)
- n = Total payments (Years × 12)
- DSR = Debt Service Ratio (typically 40%)
```

**Example:**
- Income: $10,000/month
- DSR: 40%
- Obligations: $1,500/month
- Rate: 6%
- Term: 20 years

**Result:** Max Loan = $348,950

### 2. Payment (Loan → Monthly Payment)

**Formula:**
```
Monthly Payment = L × [r × (1 + r)^n] / [(1 + r)^n - 1]

Where:
- L = Loan principal amount
- r = Monthly interest rate
- n = Total payments
```

**Example:**
- Loan: $350,000
- Rate: 6%
- Term: 20 years

**Result:** Monthly Payment = $2,507.50

### 3. Stress Testing

Adds 200-300 basis points (2-3%) to interest rate to test affordability under higher rates.

**Regulatory Compliance:**
- Post-2008 financial crisis requirement
- Ensures borrowers can handle rate increases
- Reduces default risk for lenders

---

## 🚀 Quick Start

### Prerequisites
- **Backend:** Python 3.9+
- **Frontend:** Node.js 16+ and npm/yarn

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Install dependencies:**
```bash
pip install -r requirements_no_auth.txt
```

3. **Run the server:**
```bash
uvicorn server_no_auth:app --host 0.0.0.0 --port 8001 --reload
```

Server runs at: `http://localhost:8001`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
# or
yarn install
```

3. **Update environment variables:**

Create `.env` file:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

4. **Start development server:**
```bash
npm start
# or
yarn start
```

App runs at: `http://localhost:3000`

---

## 📁 Project Structure

```
prequalification-app/
├── backend/
│   ├── server_no_auth.py          # Main API (no auth version)
│   ├── requirements_no_auth.txt   # Python dependencies
│   └── certificates/               # Generated PDF storage
│
├── frontend/
│   ├── src/
│   │   ├── AppNoAuth.js           # Main app component
│   │   ├── CalculatorNoAuth.js    # Calculator UI
│   │   ├── ThemeContext.js        # Dark mode support
│   │   ├── App.css                # Styles
│   │   └── index.js               # Entry point
│   ├── package_no_auth.json       # Node dependencies
│   ├── tailwind.config.js         # Tailwind configuration
│   └── public/
│
├── README.md                       # This file
└── PRD.md                          # Product requirements
```

---

## 🔌 API Endpoints

### 1. Health Check
```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Pre-Qualification App API"
}
```

### 2. Calculate Pre-Qualification
```
POST /api/calculate
```

**Request Body:**
```json
{
  "calculation_type": "AFFORDABILITY",
  "applicant": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-123-4567"
  },
  "affordability_input": {
    "gross_monthly_income": 10000,
    "dsr_ratio": 0.4,
    "monthly_obligations": 1500,
    "annual_interest_rate": 0.06,
    "term_years": 20,
    "stress_rate_bps": 200
  },
  "currency": "TTD",
  "validity_days": 90
}
```

**Response:**
```json
{
  "certificate_id": "A1B2C3D4",
  "max_loan_amount": 348950,
  "max_loan_formatted": "TTD $348,950.00",
  "affordable_payment": 2500,
  "interest_rate_percent": 6.0,
  "stress_test": {
    "stress_rate_percent": 8.0,
    "stress_max_loan": 308450,
    "reduction_percent": 11.6
  }
}
```

### 3. Generate Certificate PDF
```
POST /api/generate-certificate/{certificate_id}
```

**Request Body:** (Same as calculation response)

**Response:** PDF file download

---

## 🎨 Features

### ✅ Core Functionality
- Two calculation modes (Affordability & Payment)
- Stress testing with customizable basis points
- Multi-currency support (TTD, USD)
- Professional PDF certificate generation
- Unique certificate IDs with expiry dates

### ✅ User Experience
- Dark mode toggle
- Responsive design (mobile-friendly)
- Real-time input validation
- Clear error messaging
- Instant calculations (<1 second)

### ✅ Developer Features
- RESTful API design
- CORS support for all Vercel domains
- Stateless architecture
- No database required
- Easy to deploy

---

## 🌐 Deployment

### Vercel (Frontend)

1. **Set Root Directory:** `frontend`
2. **Build Command:** `npm run build`
3. **Output Directory:** `build`
4. **Environment Variables:**
   ```
   REACT_APP_BACKEND_URL=https://your-backend-url.com
   ```

### Python Hosting (Backend)

Deploy to:
- **Render** (recommended)
- **Railway**
- **Fly.io**
- **AWS Lambda** (with FastAPI adapter)
- **Google Cloud Run**

**Requirements:**
- Python 3.9+
- Install from `requirements_no_auth.txt`
- Run: `uvicorn server_no_auth:app --host 0.0.0.0 --port 8001`

---

## 📊 Customization

### Branding
Update colors in `frontend/tailwind.config.js`:
```javascript
colors: {
  'lime': '#32CD32',        // Your primary color
  'lime-dark': '#228B22',   // Your accent color
}
```

### Currency
Add new currencies in `backend/server_no_auth.py`:
```python
currency: Literal["TTD", "USD", "EUR", "GBP"] = "TTD"
```

### PDF Template
Modify `generate_certificate_pdf()` function in `backend/server_no_auth.py`

---

## 🧪 Testing

### Backend
```bash
curl -X POST http://localhost:8001/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "calculation_type": "AFFORDABILITY",
    "applicant": {"name": "Test User"},
    "affordability_input": {
      "gross_monthly_income": 10000,
      "dsr_ratio": 0.4,
      "monthly_obligations": 1500,
      "annual_interest_rate": 0.06,
      "term_years": 20
    },
    "currency": "TTD"
  }'
```

### Frontend
1. Start both backend and frontend
2. Navigate to `http://localhost:3000`
3. Fill out the form and submit
4. Verify results and PDF download

---

## 📝 Product Requirements (PRD)

See `PRD.md` for complete product requirements including:
- Business objectives
- User stories
- Functional requirements
- Technical specifications
- Regulatory compliance details
- Future enhancements

---

## 🔧 Troubleshooting

### CORS Errors
- Ensure backend CORS middleware allows your frontend domain
- Pattern matching automatically allows `*.vercel.app` domains

### PDF Generation Issues
- Verify ReportLab is installed: `pip install reportlab`
- Check `certificates/` directory has write permissions

### Calculation Errors
- Validate input ranges (DSR 0.1-0.8, rates 0.1%-50%)
- Ensure monthly obligations < gross income

---

## 📄 License

Proprietary - All rights reserved © 2025 Pre-Qualification App

---

## 🤝 Support

For technical support or feature requests, contact: support@prequalificationapp.com

---

## 🚀 Quick Commands

**Start Backend:**
```bash
cd backend && uvicorn server_no_auth:app --reload --port 8001
```

**Start Frontend:**
```bash
cd frontend && npm start
```

**Build Frontend:**
```bash
cd frontend && npm run build
```

**Install All Dependencies:**
```bash
cd backend && pip install -r requirements_no_auth.txt
cd ../frontend && npm install
```

---

**Built with ❤️ using FastAPI and React**
