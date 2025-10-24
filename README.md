# Pre-Qualification App

A professional mortgage pre-qualification calculator that helps lenders instantly assess borrower affordability and generate branded PDF certificates.

---

## 🎯 Overview

The Pre-Qualification App provides two core calculations:

1. **Affordability Calculator** - Determines maximum loan amount based on income and debt obligations
2. **Payment Calculator** - Calculates monthly payments for a specific loan amount

Both include regulatory stress testing and generate professional PDF certificates with unique IDs.

---

## 🏗️ Tech Stack

### Backend
- **FastAPI** (Python 3.9+) - High-performance REST API
- **Pydantic** - Data validation and serialization
- **ReportLab** - PDF certificate generation
- **Uvicorn** - ASGI server

### Frontend
- **React.js** 18.2+ - Modern UI library
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **Dark Mode** - Built-in theme toggle

---

## 📐 Calculations

### 1. Affordability (Income → Maximum Loan)

Calculates the maximum loan amount a borrower can afford based on their income and debt obligations.

**Formula:**
```
Step 1: Affordable Payment = (Gross Income × DSR) - Existing Obligations
Step 2: Max Loan = Payment × [1 - (1 + r)^(-n)] / r

Where:
  DSR = Debt Service Ratio (typically 40%)
  r = Monthly interest rate
  n = Total number of payments
```

**Example:**
- Monthly Income: $10,000
- DSR: 40%
- Existing Obligations: $1,500
- Interest Rate: 6% annual
- Term: 20 years

**Result:** Maximum Loan = $348,950

---

### 2. Payment (Loan → Monthly Payment)

Calculates the monthly payment required for a specific loan amount.

**Formula:**
```
Monthly Payment = Principal × [r × (1 + r)^n] / [(1 + r)^n - 1]

Where:
  r = Monthly interest rate
  n = Total number of payments
```

**Example:**
- Loan Amount: $350,000
- Interest Rate: 6% annual
- Term: 20 years

**Result:** Monthly Payment = $2,507.50

---

### 3. Stress Testing

Regulatory requirement that tests affordability at higher interest rates (typically +200 basis points).

**Purpose:**
- Post-2008 financial crisis requirement
- Ensures borrowers can handle rate increases
- Reduces default risk for lenders

---

## 🚀 Getting Started

### Prerequisites
- **Backend:** Python 3.9+
- **Frontend:** Node.js 16+ (yarn or npm)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the server:
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

Server runs at: `http://localhost:8001`

API docs available at: `http://localhost:8001/docs`

---

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
yarn install
# or
npm install
```

3. Create environment file:

Create `.env` in the frontend directory:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

4. Start development server:
```bash
yarn start
# or
npm start
```

App runs at: `http://localhost:3000`

---

## 📁 Project Structure

```
pre-qualification-app/
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── certificates/          # Generated PDF storage
│
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main app component
│   │   ├── Calculator.js     # Calculator UI
│   │   ├── ThemeContext.js   # Dark mode context
│   │   ├── setupProxy.js     # Dev server proxy config
│   │   ├── App.css           # Styles
│   │   └── index.js          # Entry point
│   ├── public/
│   │   └── index.html
│   ├── package.json          # Node dependencies
│   ├── tailwind.config.js    # Tailwind configuration
│   └── postcss.config.js
│
└── README.md                  # This file
```

---

## 🔌 API Endpoints

### Health Check
```http
GET /api/health
```

### Calculate Pre-Qualification
```http
POST /api/calculate
Content-Type: application/json

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

### Generate Certificate PDF
```http
POST /api/generate-certificate/{certificate_id}
Content-Type: application/json

[Calculation result data]
```

**Full API documentation:** Visit `http://localhost:8001/docs` when server is running.

---

## ✨ Features

### Core Functionality
- ✅ Two calculation modes (Affordability & Payment)
- ✅ Regulatory stress testing (customizable basis points)
- ✅ Multi-currency support (TTD, USD)
- ✅ Professional PDF certificate generation
- ✅ Unique certificate IDs with expiry dates
- ✅ Input validation and error handling

### User Experience
- ✅ Dark mode toggle
- ✅ Responsive design (mobile-friendly)
- ✅ Real-time validation
- ✅ Clear error messaging
- ✅ Instant calculations (<1 second)
- ✅ One-click PDF download

### Developer Features
- ✅ RESTful API design
- ✅ CORS support for all Vercel domains
- ✅ Comprehensive documentation
- ✅ Type validation with Pydantic
- ✅ Modular, maintainable code

---

## 🌐 Deployment

### Frontend (Vercel)

1. **Connect repository** to Vercel
2. **Configure build settings:**
   - **Framework:** Create React App
   - **Root Directory:** `frontend`
   - **Build Command:** `yarn build`
   - **Output Directory:** `build`

3. **Set environment variables:**
   ```
   REACT_APP_BACKEND_URL=https://your-backend-api.com
   ```

### Backend (Python Hosting)

Deploy to any Python-compatible platform:
- **Render** (recommended)
- **Railway**
- **Fly.io**
- **AWS Lambda** (with adapter)
- **Google Cloud Run**
- **Heroku**

**Deployment command:**
```bash
uvicorn server:app --host 0.0.0.0 --port 8001
```

---

## 🎨 Customization

### Branding Colors

Update `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      'lime': '#32CD32',        // Primary color
      'lime-dark': '#228B22',   // Accent color
    }
  }
}
```

### Currency Support

Add currencies in `backend/server.py`:
```python
currency: Literal["TTD", "USD", "EUR", "GBP"] = "TTD"
```

### PDF Certificate Template

Modify `generate_certificate_pdf()` function in `backend/server.py` to customize:
- Layout and spacing
- Logo and branding
- Colors and fonts
- Disclaimer text

---

## 🧪 Testing

### Manual Testing

**Backend:**
```bash
# Health check
curl http://localhost:8001/api/health

# Calculation test
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

**Frontend:**
1. Start both backend and frontend servers
2. Navigate to `http://localhost:3000`
3. Fill out the calculator form
4. Submit and verify results
5. Download PDF certificate

---

## 🔧 Troubleshooting

### Backend Won't Start
- Verify Python version: `python --version` (should be 3.9+)
- Check if port 8001 is available
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Frontend Build Fails
- Clear node_modules: `rm -rf node_modules && yarn install`
- Check Node version: `node --version` (should be 16+)
- Verify `.env` file exists with `REACT_APP_BACKEND_URL`

### CORS Errors
- Backend automatically allows Vercel, localhost, and emergentagent.com domains
- For custom domains, update `ALLOWED_PATTERNS` in `backend/server.py`

### PDF Generation Issues
- Ensure `certificates/` directory exists in backend folder
- Check write permissions: `chmod 755 backend/certificates`
- Verify ReportLab installation: `pip show reportlab`

---

## 📊 Key Terms

**DSR (Debt Service Ratio):** Percentage of gross income allocated to debt payments. Standard is 40%.

**Basis Point (bps):** 1/100th of 1%. So 200 bps = 2%.

**Stress Test:** Regulatory requirement to test affordability at higher interest rates.

**Amortization:** Process of paying off a loan through regular payments covering both principal and interest.

---

## 📝 License

Proprietary - All rights reserved © 2025 Pre-Qualification App

---

## 🤝 Support

For questions or issues, please contact the development team.

---

## 🚀 Quick Commands Reference

**Start Backend:**
```bash
cd backend && uvicorn server:app --reload --port 8001
```

**Start Frontend:**
```bash
cd frontend && yarn start
```

**Build Frontend for Production:**
```bash
cd frontend && yarn build
```

**Install All Dependencies:**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && yarn install
```

---

**Built with ❤️ using FastAPI and React**
