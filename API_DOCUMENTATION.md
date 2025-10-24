# API Documentation - Pre-Qualification App

## Base URL

```
Production: https://your-domain.com
Development: http://localhost:8001
```

## Authentication

All endpoints except `/api/health` require authentication using JWT tokens.

### Headers

```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### Getting a Token

Sign up or sign in through the frontend application. The JWT token is automatically managed by the Supabase client.

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint**: `GET /api/health`

**Authentication**: None required

**Response**: `200 OK`

```json
{
  "status": "healthy",
  "service": "Pre-Qualification App API"
}
```

**Example**:
```bash
curl http://localhost:8001/api/health
```

---

### 2. Calculate Pre-Qualification

Perform an affordability assessment or payment calculation.

**Endpoint**: `POST /api/calculate`

**Authentication**: Required

#### Request Body - Affordability Assessment

```json
{
  "calculation_type": "AFFORDABILITY",
  "affordability_input": {
    "gross_monthly_income": 30000.00,
    "dsr_ratio": 0.40,
    "monthly_obligations": 4000.00,
    "annual_interest_rate": 0.12,
    "term_years": 20,
    "stress_rate_bps": 200
  },
  "applicant": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-868-555-0123"
  },
  "currency": "TTD",
  "validity_days": 90
}
```

#### Request Body - Payment Calculation

```json
{
  "calculation_type": "PAYMENT",
  "payment_input": {
    "principal_amount": 800000.00,
    "annual_interest_rate": 0.12,
    "term_years": 20,
    "stress_rate_bps": 200
  },
  "applicant": {
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "phone": "+1-868-555-0456"
  },
  "currency": "TTD",
  "validity_days": 90
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `calculation_type` | string | Yes | Either "AFFORDABILITY" or "PAYMENT" |
| `affordability_input` | object | Conditional | Required if calculation_type is AFFORDABILITY |
| `payment_input` | object | Conditional | Required if calculation_type is PAYMENT |
| `applicant` | object | Yes | Applicant information |
| `applicant.name` | string | Yes | Full name of applicant |
| `applicant.email` | string | No | Email address |
| `applicant.phone` | string | No | Phone number |
| `currency` | string | Yes | Currency code (TTD, USD, CAD) |
| `validity_days` | integer | Yes | Certificate validity (60-180 days) |

#### Affordability Input Fields

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `gross_monthly_income` | float | 0 - 1,000,000 | Monthly income before taxes |
| `dsr_ratio` | float | 0.1 - 0.8 | Debt Service Ratio (10% - 80%) |
| `monthly_obligations` | float | >= 0 | Existing monthly debt payments |
| `annual_interest_rate` | float | 0.001 - 0.50 | Interest rate as decimal (0.12 = 12%) |
| `term_years` | integer | 1 - 50 | Loan term in years |
| `stress_rate_bps` | integer | 0 - 1000 | Additional basis points for stress test |

#### Payment Input Fields

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `principal_amount` | float | 0 - 50,000,000 | Loan amount |
| `annual_interest_rate` | float | 0.001 - 0.50 | Interest rate as decimal |
| `term_years` | integer | 1 - 50 | Loan term in years |
| `stress_rate_bps` | integer | 0 - 1000 | Additional basis points for stress test |

#### Response - Affordability: `200 OK`

```json
{
  "certificate_id": "A1B2C3D4",
  "calculation_type": "AFFORDABILITY",
  "applicant": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1-868-555-0123"
  },
  "currency": "TTD",
  "issue_date": "2024-10-22",
  "expiry_date": "2025-01-20",
  "validity_days": 90,
  "gross_monthly_income": 30000.00,
  "dsr_ratio": 0.4,
  "monthly_obligations": 4000.00,
  "affordable_payment": 8000.00,
  "affordable_payment_formatted": "TTD $8,000.00",
  "max_loan_amount": 726555.33,
  "max_loan_formatted": "TTD $726,555.33",
  "annual_interest_rate": 0.12,
  "interest_rate_percent": 12.0,
  "term_years": 20,
  "monthly_payment": 8000.00,
  "stress_test": {
    "stress_rate_bps": 200,
    "stress_annual_rate": 0.14,
    "stress_rate_percent": 14.0,
    "stress_max_loan": 643334.63,
    "stress_max_loan_formatted": "TTD $643,334.63",
    "reduction_amount": 83220.70,
    "reduction_percent": 11.45
  }
}
```

#### Response - Payment: `200 OK`

```json
{
  "certificate_id": "E5F6G7H8",
  "calculation_type": "PAYMENT",
  "applicant": {
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "phone": "+1-868-555-0456"
  },
  "currency": "TTD",
  "issue_date": "2024-10-22",
  "expiry_date": "2025-01-20",
  "validity_days": 90,
  "principal_amount": 800000.00,
  "principal_formatted": "TTD $800,000.00",
  "monthly_payment": 8808.69,
  "monthly_payment_formatted": "TTD $8,808.69",
  "annual_interest_rate": 0.12,
  "interest_rate_percent": 12.0,
  "term_years": 20,
  "total_payments": 2114085.60,
  "total_payments_formatted": "TTD $2,114,085.60",
  "total_interest": 1314085.60,
  "total_interest_formatted": "TTD $1,314,085.60",
  "stress_test": {
    "stress_rate_bps": 200,
    "stress_annual_rate": 0.14,
    "stress_rate_percent": 14.0,
    "stress_monthly_payment": 9948.17,
    "stress_payment_formatted": "TTD $9,948.17",
    "increase_amount": 1139.48,
    "increase_percent": 12.94
  }
}
```

#### Error Responses

**400 Bad Request** - Negative affordability
```json
{
  "error": "Negative affordability",
  "message": "Monthly obligations exceed affordable debt service. Cannot generate certificate.",
  "affordable_payment": -1000.00
}
```

**401 Unauthorized** - Missing or invalid token
```json
{
  "detail": "No authorization header"
}
```

**422 Validation Error** - Invalid input
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

**Example**:
```bash
curl -X POST http://localhost:8001/api/calculate \
  -H "Authorization: Bearer your_token_here" \
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
      "name": "John Doe",
      "email": "john@example.com"
    },
    "currency": "TTD",
    "validity_days": 90
  }'
```

---

### 3. Generate Certificate PDF

Generate a PDF certificate for a completed calculation.

**Endpoint**: `POST /api/generate-certificate/{certificate_id}`

**Authentication**: Required

**URL Parameters**:
- `certificate_id` (string, required): The unique certificate ID from a calculation

**Response**: `200 OK` (Binary PDF file)

**Headers**:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="PreQualification_Certificate_ABC123.pdf"
```

**Error Responses**:

**404 Not Found** - Certificate doesn't exist or not owned by user
```json
{
  "detail": "Certificate not found"
}
```

**Example**:
```bash
curl -X POST http://localhost:8001/api/generate-certificate/A1B2C3D4 \
  -H "Authorization: Bearer your_token_here" \
  -o certificate.pdf
```

---

### 4. Get Certificate Details

Retrieve details of a specific certificate.

**Endpoint**: `GET /api/certificates/{certificate_id}`

**Authentication**: Required

**URL Parameters**:
- `certificate_id` (string, required): The unique certificate ID

**Response**: `200 OK`

Returns the same structure as the calculate endpoint response.

**Error Responses**:

**404 Not Found**
```json
{
  "detail": "Certificate not found"
}
```

**Example**:
```bash
curl http://localhost:8001/api/certificates/A1B2C3D4 \
  -H "Authorization: Bearer your_token_here"
```

---

### 5. List User Certificates

List all certificates for the authenticated user.

**Endpoint**: `GET /api/certificates`

**Authentication**: Required

**Query Parameters**:
- `limit` (integer, optional): Number of certificates to return (default: 10, max: 100)

**Response**: `200 OK`

```json
{
  "certificates": [
    {
      "certificate_id": "A1B2C3D4",
      "calculation_type": "AFFORDABILITY",
      "max_loan_formatted": "TTD $726,555.33",
      "issue_date": "2024-10-22",
      "expiry_date": "2025-01-20",
      "created_at": "2024-10-22T10:30:00Z",
      ...
    },
    {
      "certificate_id": "E5F6G7H8",
      "calculation_type": "PAYMENT",
      "monthly_payment_formatted": "TTD $8,808.69",
      "issue_date": "2024-10-21",
      "expiry_date": "2025-01-19",
      "created_at": "2024-10-21T15:45:00Z",
      ...
    }
  ],
  "count": 2
}
```

**Example**:
```bash
curl "http://localhost:8001/api/certificates?limit=5" \
  -H "Authorization: Bearer your_token_here"
```

---

## Calculation Formulas

### Affordability Assessment

**Step 1**: Calculate Affordable Payment
```
Affordable Payment = (Gross Monthly Income × DSR Ratio) - Monthly Obligations
```

**Step 2**: Calculate Maximum Loan (Annuity Formula)
```
Max Loan = Affordable Payment × [(1 - (1 + r)^-n) / r]

Where:
  r = monthly interest rate (annual rate ÷ 12)
  n = number of monthly payments (years × 12)
```

**Special Case** (Zero Interest Rate):
```
Max Loan = Affordable Payment × n
```

**Example**:
- Income: $30,000
- DSR: 40% (0.4)
- Obligations: $4,000
- Rate: 12% (0.12)
- Term: 20 years

```
Affordable Payment = ($30,000 × 0.4) - $4,000 = $8,000
r = 0.12 / 12 = 0.01
n = 20 × 12 = 240

Max Loan = $8,000 × [(1 - (1.01)^-240) / 0.01]
         = $8,000 × 90.819416
         = $726,555.33
```

### Payment Calculation

**Formula**:
```
Monthly Payment = Principal × [r × (1 + r)^n] / [(1 + r)^n - 1]

Where:
  r = monthly interest rate
  n = number of monthly payments
```

**Special Case** (Zero Interest Rate):
```
Monthly Payment = Principal / n
```

**Example**:
- Principal: $800,000
- Rate: 12% (0.12)
- Term: 20 years

```
r = 0.12 / 12 = 0.01
n = 20 × 12 = 240

Monthly Payment = $800,000 × [0.01 × (1.01)^240] / [(1.01)^240 - 1]
                = $800,000 × 0.011011
                = $8,808.69
```

### Stress Testing

**Stressed Rate**:
```
Stressed Rate = Base Annual Rate + (Stress BPS / 10,000)
```

**Example**:
- Base: 12% (0.12)
- Stress: 200 bps

```
Stressed Rate = 0.12 + (200 / 10,000)
              = 0.12 + 0.02
              = 0.14 (14%)
```

Then recalculate max loan or payment using the stressed rate.

**Impact Calculation**:
```
Reduction % = [(Base Amount - Stressed Amount) / Base Amount] × 100
Increase % = [(Stressed Amount - Base Amount) / Base Amount] × 100
```

---

## Rate Limits

Currently no rate limiting is implemented. For production, consider:
- 100 requests per minute per user
- 10 calculations per minute per user
- 5 PDF generations per minute per user

---

## Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input, negative affordability |
| 401 | Unauthorized | Missing or invalid JWT token |
| 404 | Not Found | Certificate ID doesn't exist |
| 422 | Validation Error | Input fields out of range or invalid |
| 500 | Server Error | Unexpected server error |

---

## Best Practices

### 1. Token Management
- Store tokens securely
- Implement token refresh logic
- Handle 401 errors by redirecting to login

### 2. Input Validation
- Validate inputs on frontend before API calls
- Handle validation errors gracefully
- Display user-friendly error messages

### 3. Error Handling
```javascript
try {
  const response = await axios.post('/api/calculate', data, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  // Handle success
} catch (error) {
  if (error.response) {
    // Server responded with error
    if (error.response.status === 401) {
      // Redirect to login
    } else if (error.response.status === 422) {
      // Show validation errors
    }
  } else {
    // Network error
  }
}
```

### 4. Rate Limiting
- Implement exponential backoff for retries
- Cache calculations when possible
- Batch requests if needed

---

## Webhooks (Future)

Potential webhook events for future implementation:
- `calculation.created`
- `certificate.generated`
- `certificate.expired`

---

## Changelog

### Version 1.0 (October 2024)
- Initial release
- Affordability and payment calculations
- Stress testing support
- PDF certificate generation
- Multi-currency support
- User authentication

---

## Support

For API issues or questions:
- Check server logs: `/var/log/supervisor/backend.err.log`
- Interactive API docs: `http://localhost:8001/docs`
- Health check: `http://localhost:8001/api/health`

---

**API Version**: 1.0  
**Last Updated**: October 2024
