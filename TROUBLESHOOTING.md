# Troubleshooting Guide - Fraser Finance Calculator

## Common Issues and Solutions

### 1. "ERR_CONNECTION_REFUSED" or "An error occurred during calculation"

**Symptoms:**
- Red error message: "Error: An error occurred during calculation"
- Browser console shows: `Failed to load resource: net::ERR_CONNECTION_REFUSED`
- Calculation button doesn't work

**Root Cause:**
Frontend cannot connect to the backend API.

**Solution:**
✅ **Already Fixed!** The application now uses a proxy configuration.

**How it works:**
- `package.json` includes: `"proxy": "http://localhost:8001"`
- Frontend makes relative API calls (e.g., `/api/calculate`)
- React dev server forwards these to the backend

**Verification:**
```bash
# 1. Check backend is running
sudo supervisorctl status backend

# 2. Test backend directly
curl http://localhost:8001/api/health

# 3. Restart services if needed
sudo supervisorctl restart all
```

---

### 2. Services Not Starting

**Check Status:**
```bash
sudo supervisorctl status
```

**Restart All Services:**
```bash
sudo supervisorctl restart all
```

**View Logs:**
```bash
# Backend logs
tail -50 /var/log/supervisor/backend.err.log
tail -50 /var/log/supervisor/backend.out.log

# Frontend logs
tail -50 /var/log/supervisor/frontend.err.log
tail -50 /var/log/supervisor/frontend.out.log
```

---

### 3. Frontend Not Loading

**Symptoms:**
- Blank page or webpack errors
- CSS not loading properly

**Solutions:**

1. **Check if frontend is running:**
```bash
sudo supervisorctl status frontend
```

2. **Restart frontend:**
```bash
sudo supervisorctl restart frontend
```

3. **Wait for compilation** (takes 15-20 seconds):
```bash
sleep 20 && curl -s http://localhost:3000 | head -10
```

4. **Check for compilation errors:**
```bash
tail -30 /var/log/supervisor/frontend.out.log
```

---

### 4. PDF Generation Failing

**Symptoms:**
- Certificate downloads as 0 bytes
- Error when clicking "Download Certificate (PDF)"

**Solutions:**

1. **Check backend logs:**
```bash
tail -50 /var/log/supervisor/backend.err.log | grep -i pdf
```

2. **Verify certificate directory exists:**
```bash
ls -la /app/backend/certificates/
```

3. **Test PDF generation directly:**
```bash
# First, create a certificate
CERT_ID=$(curl -s -X POST http://localhost:8001/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"calculation_type":"PAYMENT","payment_input":{"principal_amount":500000,"annual_interest_rate":0.12,"term_years":20},"applicant":{"name":"Test User"},"currency":"TTD","validity_days":90}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['certificate_id'])")

# Then generate PDF
curl -X POST http://localhost:8001/api/generate-certificate/$CERT_ID -o test.pdf
ls -lh test.pdf
```

---

### 5. MongoDB Connection Issues

**Symptoms:**
- Calculations work but results aren't saved
- Backend logs show MongoDB errors

**Solutions:**

1. **Check MongoDB status:**
```bash
sudo supervisorctl status mongodb
```

2. **Restart MongoDB:**
```bash
sudo supervisorctl restart mongodb
```

3. **Test MongoDB connection:**
```bash
mongosh mongodb://localhost:27017/fraser_finance --eval "db.stats()"
```

---

### 6. Port Already in Use

**Symptoms:**
- Service fails to start
- Error: "Address already in use"

**Solutions:**

1. **Check what's using the port:**
```bash
# For backend (port 8001)
lsof -i :8001

# For frontend (port 3000)
lsof -i :3000
```

2. **Kill the process (if necessary):**
```bash
# Replace PID with actual process ID
kill -9 <PID>
```

3. **Restart the service:**
```bash
sudo supervisorctl restart backend  # or frontend
```

---

### 7. Calculation Returns Wrong Results

**Symptoms:**
- Max loan amount seems incorrect
- Monthly payment doesn't match expectations

**Solutions:**

1. **Verify input values:**
   - Interest rate should be entered as percentage (e.g., 12 for 12%)
   - All financial amounts should be positive numbers
   - DSR ratio is between 10% and 80%

2. **Run test suite:**
```bash
python3 /app/tests/test_calculations.py
```

3. **Test known values:**
   - Income: TTD 30,000
   - DSR: 40%
   - Obligations: TTD 4,000
   - Rate: 12%
   - Term: 20 years
   - **Expected Max Loan**: ~TTD 726,555

---

### 8. CORS Errors

**Symptoms:**
- Browser console shows CORS policy errors
- API requests blocked by browser

**Solutions:**

✅ **Already configured!** The backend has CORS enabled for all origins.

If issues persist:

1. **Check backend CORS configuration:**
```bash
grep -A 5 "CORSMiddleware" /app/backend/server.py
```

2. **Verify response headers:**
```bash
curl -v http://localhost:8001/api/health 2>&1 | grep -i cors
```

---

### 9. Slow Performance

**Symptoms:**
- Calculations take more than 5 seconds
- PDF generation is slow

**Solutions:**

1. **Check system resources:**
```bash
top -bn1 | head -20
```

2. **Check MongoDB performance:**
```bash
mongosh mongodb://localhost:27017/fraser_finance --eval "db.certificates.stats()"
```

3. **Clear old certificates (if database is large):**
```bash
mongosh mongodb://localhost:27017/fraser_finance --eval "db.certificates.countDocuments()"
```

---

### 10. Environment Variables Not Loading

**Symptoms:**
- Application uses wrong URLs
- Configuration not being applied

**Solutions:**

1. **Check environment files:**
```bash
cat /app/backend/.env
cat /app/frontend/.env
```

2. **Verify variables are set:**
```bash
# From backend directory
cd /app/backend && python3 -c "import os; print(os.getenv('MONGO_URL'))"
```

3. **Restart services after changing .env:**
```bash
sudo supervisorctl restart all
```

---

## Quick Diagnostic Commands

### Run Health Check Script
```bash
/app/scripts/health_check.sh
```

### Test All Calculations
```bash
python3 /app/tests/test_calculations.py
```

### Check All Service Logs
```bash
for service in backend frontend mongodb; do
  echo "=== $service Logs ===" 
  tail -20 /var/log/supervisor/$service.*.log
  echo ""
done
```

### View Recent Certificates
```bash
curl -s http://localhost:8001/api/certificates?limit=5 | python3 -m json.tool
```

---

## Getting Help

If you're still experiencing issues:

1. **Gather diagnostic information:**
```bash
/app/scripts/health_check.sh > diagnostic.txt
sudo supervisorctl status >> diagnostic.txt
tail -100 /var/log/supervisor/*.log >> diagnostic.txt
```

2. **Check the logs** for specific error messages

3. **Try the automated test suite** to isolate the issue:
```bash
python3 /app/tests/test_calculations.py
```

---

## Prevention Tips

1. **Always use the health check script** after making changes:
```bash
/app/scripts/health_check.sh
```

2. **Monitor logs** when testing new features:
```bash
tail -f /var/log/supervisor/backend.err.log
```

3. **Run tests regularly:**
```bash
python3 /app/tests/test_calculations.py
```

4. **Keep services updated:**
```bash
sudo supervisorctl update
sudo supervisorctl restart all
```
