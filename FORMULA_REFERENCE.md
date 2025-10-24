# Quick Formula Reference - Pre-Qualification App

## 📐 Mathematical Formulas Used

### 1. Affordability Calculation (Income → Maximum Loan)

**Step 1: Affordable Monthly Payment**
```
Affordable_Payment = (Gross_Income × DSR_Ratio) - Monthly_Obligations

Where:
• DSR_Ratio = Debt Service Ratio (typically 0.40 or 40%)
• This represents the maximum % of income that can go to debt
```

**Step 2: Maximum Loan Amount (Present Value of Annuity)**
```
Max_Loan = P × [1 - (1 + r)^(-n)] / r

Where:
• P = Affordable Monthly Payment
• r = Monthly Interest Rate = Annual_Rate / 12
• n = Total Number of Payments = Years × 12
```

---

### 2. Payment Calculation (Loan → Monthly Payment)

**Monthly Payment (Annuity Payment Formula)**
```
Monthly_Payment = L × [r × (1 + r)^n] / [(1 + r)^n - 1]

Where:
• L = Loan Principal Amount
• r = Monthly Interest Rate = Annual_Rate / 12
• n = Total Number of Payments = Years × 12
```

**Total Interest Paid**
```
Total_Interest = (Monthly_Payment × n) - L

Where:
• n = Total Number of Payments
• L = Original Loan Amount
```

---

### 3. Stress Testing

**Stress Rate Calculation**
```
Stress_Rate = Base_Rate + (Stress_BPS / 10,000)

Where:
• Base_Rate = Annual interest rate (decimal form)
• Stress_BPS = Basis points to add (e.g., 200 for 2%)
• Divide by 10,000 because 1 basis point = 0.01%

Example:
• Base Rate: 6% = 0.06
• Stress: 200 bps
• Stress Rate = 0.06 + (200/10,000) = 0.06 + 0.02 = 0.08 (8%)
```

Then apply the stressed rate to either:
- **Affordability:** Recalculate Max_Loan with stress_rate
- **Payment:** Recalculate Monthly_Payment with stress_rate

---

### 4. Percentage Changes (Impact Analysis)

**Loan Reduction Under Stress**
```
Reduction_Amount = Base_Loan - Stressed_Loan
Reduction_Percent = (Reduction_Amount / Base_Loan) × 100
```

**Payment Increase Under Stress**
```
Increase_Amount = Stressed_Payment - Base_Payment
Increase_Percent = (Increase_Amount / Base_Payment) × 100
```

---

## 📊 Example Walkthrough

### Scenario: Home Buyer Pre-Qualification

**Inputs:**
- Gross Monthly Income: $10,000
- DSR Ratio: 40%
- Existing Monthly Obligations: $1,500
- Interest Rate: 6% per year
- Loan Term: 20 years
- Stress Test: 200 basis points (2%)

---

**AFFORDABILITY CALCULATION:**

**Step 1: Calculate Affordable Payment**
```
Affordable_Payment = ($10,000 × 0.40) - $1,500
                   = $4,000 - $1,500
                   = $2,500/month
```

**Step 2: Calculate Maximum Loan (Base Rate 6%)**
```
• Monthly rate: 6% ÷ 12 = 0.5% = 0.005
• Number of payments: 20 × 12 = 240

Max_Loan = $2,500 × [1 - (1.005)^(-240)] / 0.005
         = $2,500 × [1 - 0.3021] / 0.005
         = $2,500 × 0.6979 / 0.005
         = $2,500 × 139.58
         = $348,950
```

**Step 3: Stress Test (8% rate)**
```
• Stressed rate: 6% + 2% = 8%
• Monthly rate: 8% ÷ 12 = 0.667% = 0.00667

Stressed_Max_Loan = $2,500 × [1 - (1.00667)^(-240)] / 0.00667
                  = $2,500 × 123.38
                  = $308,450

Reduction = $348,950 - $308,450 = $40,500 (11.6% lower)
```

**RESULTS:**
- ✅ Maximum Loan (Base): $348,950
- ⚠️ Maximum Loan (Stressed): $308,450
- 📉 Stress Impact: -$40,500 (-11.6%)

---

**PAYMENT CALCULATION:**

Using the base qualification amount of $348,950:

**Step 1: Calculate Monthly Payment (Base Rate 6%)**
```
Monthly_Payment = $348,950 × [0.005 × (1.005)^240] / [(1.005)^240 - 1]
                = $348,950 × 0.007164
                = $2,499.90/month
```

**Step 2: Total Cost**
```
Total_Paid = $2,499.90 × 240 = $599,976
Total_Interest = $599,976 - $348,950 = $251,026
```

**Step 3: Stress Test Payment (8% rate)**
```
Stressed_Payment = $348,950 × [0.00667 × (1.00667)^240] / [(1.00667)^240 - 1]
                 = $348,950 × 0.008385
                 = $2,926.40/month

Increase = $2,926.40 - $2,499.90 = $426.50/month (17% higher)
```

**RESULTS:**
- ✅ Monthly Payment (Base): $2,499.90
- ⚠️ Monthly Payment (Stressed): $2,926.40
- 📈 Stress Impact: +$426.50/month (+17%)

---

## 🧮 Code Implementation (Python)

### Affordability: Max Loan Calculation
```python
def calculate_max_loan(affordable_payment, annual_rate, term_years):
    """Calculate maximum loan from affordable payment"""
    if annual_rate == 0:
        return affordable_payment * term_years * 12
    
    monthly_rate = annual_rate / 12
    num_payments = term_years * 12
    
    max_loan = affordable_payment * (1 - (1 + monthly_rate) ** (-num_payments)) / monthly_rate
    
    return round(max_loan, 2)
```

### Payment Calculation
```python
def calculate_monthly_payment(principal, annual_rate, term_years):
    """Calculate monthly payment using annuity formula"""
    if annual_rate == 0:
        return principal / (term_years * 12)
    
    monthly_rate = annual_rate / 12
    num_payments = term_years * 12
    
    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
              ((1 + monthly_rate) ** num_payments - 1)
    
    return round(payment, 2)
```

---

## 🔑 Key Terms Glossary

**DSR (Debt Service Ratio):** 
The percentage of gross income that can be allocated to debt payments. Standard is 40%.

**Basis Point (bp):** 
1/100th of 1%. So 200 basis points = 2%.

**Stress Test:** 
Regulatory requirement to test if borrower can afford higher rates. Usually +200-300 bps.

**Annuity Formula:** 
Mathematical formula for calculating equal periodic payments over time.

**Amortization:** 
The process of paying off a loan through regular payments that cover both principal and interest.

**Present Value (PV):** 
The current value of a future stream of payments (used in max loan calculation).

---

## 🎯 Why These Formulas Matter

### Business Impact:
1. **Accuracy:** Industry-standard formulas ensure correct calculations
2. **Compliance:** DSR and stress testing meet regulatory requirements
3. **Speed:** Mathematical precision without manual errors
4. **Trust:** Clients and regulators can verify the math

### Technical Impact:
1. **Performance:** Simple formulas = fast calculations (< 50ms)
2. **Reliability:** Well-tested mathematical principles
3. **Transparency:** Clear, auditable calculations
4. **Scalability:** No complex dependencies or external APIs needed

---

This is the mathematical foundation that makes the Pre-Qualification App both fast and trustworthy. 🎯
