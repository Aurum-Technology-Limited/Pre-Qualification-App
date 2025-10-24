import requests
import sys
import json
from datetime import datetime

class FraserFinanceAPITester:
    def __init__(self, base_url="https://mortgage-preapp.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test_name": name,
            "success": success,
            "details": details
        })

    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Response: {data}"
            self.log_test("Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False

    def test_affordability_calculation(self):
        """Test affordability calculation with expected values"""
        test_data = {
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
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/calculate", json=test_data, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Expected max loan ~TTD 726,555 (as per requirements)
                max_loan = data.get('max_loan_amount', 0)
                expected_range = (720000, 730000)  # Allow some tolerance
                
                if expected_range[0] <= max_loan <= expected_range[1]:
                    details = f"Max loan: TTD {max_loan:,.2f} (within expected range)"
                    self.log_test("Affordability Calculation - Amount Check", True, details)
                else:
                    details = f"Max loan: TTD {max_loan:,.2f} (expected ~726,555)"
                    self.log_test("Affordability Calculation - Amount Check", False, details)
                
                # Check stress test
                if 'stress_test' in data:
                    stress_loan = data['stress_test'].get('stress_max_loan', 0)
                    reduction = data['stress_test'].get('reduction_percent', 0)
                    details = f"Stress loan: TTD {stress_loan:,.2f}, Reduction: {reduction}%"
                    self.log_test("Affordability Stress Test", True, details)
                else:
                    self.log_test("Affordability Stress Test", False, "No stress test data")
                    
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                self.log_test("Affordability Calculation", False, details)
                
            return success
        except Exception as e:
            self.log_test("Affordability Calculation", False, str(e))
            return False

    def test_payment_calculation(self):
        """Test payment calculation with expected values"""
        test_data = {
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
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/calculate", json=test_data, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                # Expected monthly payment TTD 8,808.69 (as per requirements)
                monthly_payment = data.get('monthly_payment', 0)
                expected_payment = 8808.69
                tolerance = 1.0  # ±$1 tolerance as mentioned
                
                if abs(monthly_payment - expected_payment) <= tolerance:
                    details = f"Monthly payment: TTD {monthly_payment:,.2f} (expected {expected_payment:,.2f})"
                    self.log_test("Payment Calculation - Amount Check", True, details)
                else:
                    details = f"Monthly payment: TTD {monthly_payment:,.2f} (expected {expected_payment:,.2f})"
                    self.log_test("Payment Calculation - Amount Check", False, details)
                
                # Check stress test
                if 'stress_test' in data:
                    stress_payment = data['stress_test'].get('stress_monthly_payment', 0)
                    increase = data['stress_test'].get('increase_percent', 0)
                    details = f"Stress payment: TTD {stress_payment:,.2f}, Increase: {increase}%"
                    self.log_test("Payment Stress Test", True, details)
                else:
                    self.log_test("Payment Stress Test", False, "No stress test data")
                    
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                self.log_test("Payment Calculation", False, details)
                
            return success
        except Exception as e:
            self.log_test("Payment Calculation", False, str(e))
            return False

    def test_negative_affordability(self):
        """Test negative affordability case"""
        test_data = {
            "calculation_type": "AFFORDABILITY",
            "affordability_input": {
                "gross_monthly_income": 10000,
                "dsr_ratio": 0.4,
                "monthly_obligations": 5000,
                "annual_interest_rate": 0.12,
                "term_years": 20
            },
            "applicant": {
                "name": "Test User",
                "email": "test@example.com"
            },
            "currency": "TTD"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/calculate", json=test_data, timeout=15)
            # Should return 400 for negative affordability
            success = response.status_code == 400
            
            if success:
                data = response.json()
                details = f"Correctly rejected: {data.get('message', 'Negative affordability')}"
            else:
                details = f"Unexpected status: {response.status_code}"
                
            self.log_test("Negative Affordability Handling", success, details)
            return success
        except Exception as e:
            self.log_test("Negative Affordability Handling", False, str(e))
            return False

    def test_form_validation(self):
        """Test form validation with invalid inputs"""
        # Test invalid DSR ratio
        test_data = {
            "calculation_type": "AFFORDABILITY",
            "affordability_input": {
                "gross_monthly_income": 30000,
                "dsr_ratio": 0.9,  # Above 80% limit
                "monthly_obligations": 4000,
                "annual_interest_rate": 0.12,
                "term_years": 20
            },
            "applicant": {"name": "Test User"},
            "currency": "TTD"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/calculate", json=test_data, timeout=15)
            success = response.status_code == 422  # Validation error
            details = f"Status: {response.status_code} for invalid DSR (90%)"
            self.log_test("Form Validation - Invalid DSR", success, details)
        except Exception as e:
            self.log_test("Form Validation - Invalid DSR", False, str(e))

        # Test negative values
        test_data["affordability_input"]["gross_monthly_income"] = -1000
        try:
            response = requests.post(f"{self.base_url}/api/calculate", json=test_data, timeout=15)
            success = response.status_code == 422
            details = f"Status: {response.status_code} for negative income"
            self.log_test("Form Validation - Negative Income", success, details)
        except Exception as e:
            self.log_test("Form Validation - Negative Income", False, str(e))

    def test_multi_currency(self):
        """Test multi-currency support"""
        currencies = ["TTD", "USD", "CAD"]
        
        for currency in currencies:
            test_data = {
                "calculation_type": "PAYMENT",
                "payment_input": {
                    "principal_amount": 100000,
                    "annual_interest_rate": 0.05,
                    "term_years": 15
                },
                "applicant": {"name": "Test User"},
                "currency": currency
            }
            
            try:
                response = requests.post(f"{self.base_url}/api/calculate", json=test_data, timeout=15)
                success = response.status_code == 200
                
                if success:
                    data = response.json()
                    formatted_payment = data.get('monthly_payment_formatted', '')
                    currency_correct = currency in formatted_payment
                    details = f"Currency {currency}: {formatted_payment}"
                    self.log_test(f"Multi-Currency Support - {currency}", currency_correct, details)
                else:
                    self.log_test(f"Multi-Currency Support - {currency}", False, f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Multi-Currency Support - {currency}", False, str(e))

    def test_certificate_generation(self):
        """Test certificate generation workflow"""
        # First, create a calculation
        test_data = {
            "calculation_type": "AFFORDABILITY",
            "affordability_input": {
                "gross_monthly_income": 25000,
                "dsr_ratio": 0.35,
                "monthly_obligations": 3000,
                "annual_interest_rate": 0.10,
                "term_years": 25
            },
            "applicant": {
                "name": "Certificate Test User",
                "email": "cert@example.com"
            },
            "currency": "TTD"
        }
        
        try:
            # Step 1: Create calculation
            response = requests.post(f"{self.base_url}/api/calculate", json=test_data, timeout=15)
            if response.status_code != 200:
                self.log_test("Certificate Generation - Create Calculation", False, f"Status: {response.status_code}")
                return False
                
            data = response.json()
            cert_id = data.get('certificate_id')
            
            if not cert_id:
                self.log_test("Certificate Generation - Get Certificate ID", False, "No certificate ID returned")
                return False
                
            self.log_test("Certificate Generation - Create Calculation", True, f"Certificate ID: {cert_id}")
            
            # Step 2: Generate PDF certificate
            response = requests.post(f"{self.base_url}/api/generate-certificate/{cert_id}", timeout=20)
            success = response.status_code == 200 and response.headers.get('content-type') == 'application/pdf'
            
            if success:
                pdf_size = len(response.content)
                details = f"PDF generated, size: {pdf_size} bytes"
            else:
                details = f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}"
                
            self.log_test("Certificate Generation - PDF Creation", success, details)
            
            # Step 3: Retrieve certificate data
            response = requests.get(f"{self.base_url}/api/certificates/{cert_id}", timeout=15)
            success = response.status_code == 200
            
            if success:
                cert_data = response.json()
                details = f"Certificate retrieved, type: {cert_data.get('calculation_type')}"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Certificate Generation - Data Retrieval", success, details)
            
            return True
            
        except Exception as e:
            self.log_test("Certificate Generation", False, str(e))
            return False

    def test_certificates_list(self):
        """Test certificates listing endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/certificates", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                count = data.get('count', 0)
                certificates = data.get('certificates', [])
                details = f"Retrieved {count} certificates"
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Certificates List", success, details)
            return success
        except Exception as e:
            self.log_test("Certificates List", False, str(e))
            return False

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Fraser Finance API Tests")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_health_endpoint():
            print("❌ Health check failed - stopping tests")
            return False
            
        # Run all test scenarios
        self.test_affordability_calculation()
        self.test_payment_calculation()
        self.test_negative_affordability()
        self.test_form_validation()
        self.test_multi_currency()
        self.test_certificate_generation()
        self.test_certificates_list()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = FraserFinanceAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": tester.tests_run,
        "passed_tests": tester.tests_passed,
        "success_rate": (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0,
        "test_details": tester.test_results
    }
    
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())