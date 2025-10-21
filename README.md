# Fraser Finance - Pre-Qualification Certificate Calculator

## Overview
A professional mortgage pre-qualification calculator for Fraser Finance that generates branded PDF certificates. The application supports two calculation paths:

1. **Affordability Assessment**: Calculate maximum loan amount based on income and debt obligations
2. **Payment Calculation**: Calculate monthly payments for a specified loan amount

## Features
- ✅ Dual calculation modes (Affordability & Payment)
- ✅ Stress testing with configurable basis points
- ✅ Multi-currency support (TTD, USD, CAD)
- ✅ Professional PDF certificate generation
- ✅ Fraser Finance lime green branding (#32CD32)
- ✅ MongoDB storage for audit trails
- ✅ Responsive design with Tailwind CSS
- ✅ Real-time form validation

## Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: React.js with Tailwind CSS
- **Database**: MongoDB
- **PDF Generation**: ReportLab

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB
- Yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
yarn install
```

## Running the Application

### Using Supervisor (Recommended)
```bash
sudo supervisorctl restart all
```

### Manual Start

**Backend:**
```bash
cd backend
python server.py
```

**Frontend:**
```bash
cd frontend
yarn start
```

## API Endpoints

### Health Check
```
GET /api/health
```

### Calculate Pre-Qualification
```
POST /api/calculate
```

**Request Body (Affordability):**
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
    "email": "john@example.com"
  },
  "currency": "TTD",
  "validity_days": 90
}
```

**Request Body (Payment):**
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

### Generate Certificate
```
POST /api/generate-certificate/{certificate_id}
```
Returns PDF file for download.

### Get Certificate Details
```
GET /api/certificates/{certificate_id}
```

### List Recent Certificates
```
GET /api/certificates?limit=10
```

## Sample Test Data

### Test Case 1: Standard Affordability
- Gross Monthly Income: TTD 30,000
- DSR Ratio: 40%
- Monthly Obligations: TTD 4,000
- Interest Rate: 12%
- Term: 20 years
- **Expected Result**: Max Loan ≈ TTD 821,201

### Test Case 2: Payment Calculation
- Principal: TTD 800,000
- Interest Rate: 12%
- Term: 20 years
- **Expected Result**: Monthly Payment ≈ TTD 8,808.69

## Color Scheme
- **Primary**: Lime Green (#32CD32)
- **Secondary**: White (#FFFFFF)
- **Accent**: Dark Green (#228B22)
- **Error**: Red (#DC3545)
- **Warning**: Orange (#FD7E14)

## Calculation Formulas

### Affordability Path
1. Affordable Payment = (Gross Income × DSR) - Existing Obligations
2. Max Loan = Affordable Payment × [(1 - (1 + r)^-n) / r]
   - r = monthly interest rate
   - n = number of monthly payments

### Payment Path
Monthly Payment = Principal × [r × (1 + r)^n / ((1 + r)^n - 1)]

### Stress Testing
Apply additional basis points to interest rate:
- Stressed Rate = Base Rate + (Stress BPS / 10000)

## Development

### Project Structure
```
/app
├── backend/
│   ├── server.py              # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   └── certificates/           # Generated PDF storage
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main React component
│   │   ├── App.css            # Styles
│   │   └── index.js           # Entry point
│   ├── public/
│   ├── package.json
│   └── .env
└── README.md
```

## Deployment

The application is deployment-ready with:
- Environment variable configuration
- Supervisor process management
- MongoDB connection handling
- CORS configured for production

## License
Copyright © 2024 Fraser Finance. All rights reserved.

## Support
For issues or questions, contact: info@fraserfinance.com