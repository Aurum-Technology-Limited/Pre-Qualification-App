# Fraser Finance - Deployment Guide

## 🚀 Quick Start

The application is **already running** and deployment-ready!

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

---

## 📦 What's Included

### Backend (FastAPI + Python)
- ✅ Two calculation modes (Affordability & Payment)
- ✅ Stress testing with configurable basis points
- ✅ Multi-currency support (TTD, USD, CAD)
- ✅ PDF certificate generation with Fraser Finance branding
- ✅ MongoDB storage for audit trails
- ✅ Comprehensive input validation
- ✅ RESTful API with automatic documentation

### Frontend (React + Tailwind CSS)
- ✅ Clean, professional lime green theme (#32CD32)
- ✅ Dual-tab interface for calculation types
- ✅ Real-time form validation
- ✅ Interactive DSR slider
- ✅ Responsive design
- ✅ Results display with stress test comparison
- ✅ One-click PDF certificate download
- ✅ Sample data included for testing

---

## 🔧 Service Management

### Check Service Status
```bash
sudo supervisorctl status
```

### Restart All Services
```bash
sudo supervisorctl restart all
```

### Restart Individual Services
```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart mongodb
```

### View Logs
```bash
# Backend logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log

# Frontend logs
tail -f /var/log/supervisor/frontend.out.log
tail -f /var/log/supervisor/frontend.err.log
```

---

## 🧪 Testing

### Run Automated Tests
```bash
python3 /app/tests/test_calculations.py
```

### Run Health Check
```bash
/app/scripts/health_check.sh
```

### Manual API Testing

**Test Affordability Calculation:**
```bash
curl -X POST http://localhost:8001/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
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
      "name": "Test User",
      "email": "test@example.com"
    },
    "currency": "TTD",
    "validity_days": 90
  }'
```

**Test Payment Calculation:**
```bash
curl -X POST http://localhost:8001/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "calculation_type": "PAYMENT",
    "payment_input": {
      "principal_amount": 800000,
      "annual_interest_rate": 0.12,
      "term_years": 20,
      "stress_rate_bps": 200
    },
    "applicant": {
      "name": "Test User",
      "email": "test@example.com"
    },
    "currency": "TTD",
    "validity_days": 90
  }'
```

---

## 📊 Sample Test Data

Sample calculations are available in `/app/tests/sample_data.json`, including:

1. **Standard Affordability** - Young Professional
2. **High Income Professional**
3. **First Time Home Buyer**
4. **Luxury Property Purchase**
5. **Investment Property**
6. **Short Term Loan**
7. **Refinancing Assessment**
8. **Conservative Borrower**

---

## 🎨 Branding Colors

The application uses Fraser Finance's signature colors:

- **Primary**: Lime Green (#32CD32)
- **Secondary**: White (#FFFFFF)
- **Accent**: Dark Green (#228B22)
- **Error**: Red (#DC3545)
- **Warning**: Orange (#FD7E14)
- **Success**: Dark Green (#228B22)

---

## 📁 Project Structure

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
├── tests/
│   ├── test_calculations.py   # Automated tests
│   └── sample_data.json       # Sample test data
├── scripts/
│   └── health_check.sh        # Health check script
└── README.md
```

---

## 🔐 Environment Variables

### Backend (`/app/backend/.env`)
```env
MONGO_URL=mongodb://localhost:27017/fraser_finance
BACKEND_PORT=8001
FRONTEND_URL=http://localhost:3000
```

### Frontend (`/app/frontend/.env`)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
PORT=3000
```

**⚠️ Important**: Do not modify these URLs for local development. They are pre-configured for the deployment environment.

---

## 📈 Key Features

### 1. Affordability Assessment
- Calculate maximum loan based on income and debt obligations
- Uses Debt Service Ratio (DSR) from 10% to 80%
- Accounts for existing monthly obligations
- Provides stress-tested scenarios

### 2. Payment Calculation
- Calculate monthly payments for a specified loan amount
- Shows total interest paid over loan term
- Includes stress test payment comparison
- Displays amortization summary

### 3. Stress Testing
- Apply additional basis points to interest rate
- Shows impact on affordability or payments
- Percentage change visualization
- Helps assess loan viability under adverse conditions

### 4. Multi-Currency Support
- Trinidad & Tobago Dollar (TTD)
- United States Dollar (USD)
- Canadian Dollar (CAD)
- Proper currency formatting for all calculations

### 5. PDF Certificate Generation
- Professional Fraser Finance branding
- Unique certificate IDs
- Configurable validity periods (60-180 days)
- Includes all calculation details and disclaimers
- Downloadable directly from the interface

---

## 🧮 Calculation Formulas

### Affordability Path
1. **Affordable Payment** = (Gross Income × DSR) - Existing Obligations
2. **Maximum Loan** = Affordable Payment × [(1 - (1 + r)^-n) / r]
   - Where: r = monthly interest rate, n = number of payments

### Payment Path
**Monthly Payment** = Principal × [r × (1 + r)^n / ((1 + r)^n - 1)]

### Stress Testing
**Stressed Rate** = Base Rate + (Stress BPS / 10000)

---

## 🐛 Troubleshooting

### Backend Not Starting
```bash
# Check backend logs
tail -50 /var/log/supervisor/backend.err.log

# Restart backend
sudo supervisorctl restart backend
```

### Frontend Not Loading
```bash
# Check frontend logs
tail -50 /var/log/supervisor/frontend.err.log

# Restart frontend
sudo supervisorctl restart frontend
```

### MongoDB Connection Issues
```bash
# Check MongoDB status
sudo supervisorctl status mongodb

# Restart MongoDB
sudo supervisorctl restart mongodb
```

### Port Already in Use
```bash
# Check what's using port 8001
lsof -i :8001

# Check what's using port 3000
lsof -i :3000
```

---

## 📝 API Endpoints

### Health Check
```
GET /api/health
```

### Calculate Pre-Qualification
```
POST /api/calculate
```

### Generate Certificate PDF
```
POST /api/generate-certificate/{certificate_id}
```

### Get Certificate Details
```
GET /api/certificates/{certificate_id}
```

### List Recent Certificates
```
GET /api/certificates?limit=10
```

---

## 🎯 Production Deployment Checklist

- [ ] Update environment variables for production URLs
- [ ] Configure proper MongoDB credentials
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Configure backup strategy for MongoDB
- [ ] Set up monitoring and alerts
- [ ] Enable rate limiting on API endpoints
- [ ] Review and update CORS settings
- [ ] Set up CDN for static assets (optional)

---

## 📞 Support

For issues or questions:
- Review logs in `/var/log/supervisor/`
- Check API documentation at http://localhost:8001/docs
- Run health check: `/app/scripts/health_check.sh`

---

## 🎉 Success Metrics

The application has been tested and verified with:
- ✅ All calculation tests passing
- ✅ PDF generation working correctly
- ✅ Multi-currency support validated
- ✅ Stress testing functioning as expected
- ✅ Error handling for edge cases
- ✅ Responsive design across devices
- ✅ Fraser Finance branding consistently applied

**The application is deployment-ready and fully functional!**
