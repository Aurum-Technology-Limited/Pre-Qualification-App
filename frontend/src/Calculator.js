import React, { useState } from 'react';
import './App.css';
import axios from 'axios';
import { useTheme } from './ThemeContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

function Calculator() {
  const { darkMode, toggleDarkMode } = useTheme();
  const [calculationType, setCalculationType] = useState('AFFORDABILITY');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  
  // Applicant Info
  const [applicantName, setApplicantName] = useState('');
  const [applicantEmail, setApplicantEmail] = useState('');
  const [applicantPhone, setApplicantPhone] = useState('');
  
  // Affordability Fields
  const [grossIncome, setGrossIncome] = useState('');
  const [dsrRatio, setDsrRatio] = useState(0.4);
  const [monthlyObligations, setMonthlyObligations] = useState('');
  
  // Payment Fields
  const [principalAmount, setPrincipalAmount] = useState('');
  
  // Common Fields
  const [interestRate, setInterestRate] = useState('');
  const [termYears, setTermYears] = useState('20');
  const [stressRateBps, setStressRateBps] = useState('');
  const [currency, setCurrency] = useState('TTD');
  const [validityDays, setValidityDays] = useState('90');
  
  const handleCalculate = async (e) => {
    e.preventDefault();
    setError(null);
    setResults(null);
    setLoading(true);
    
    try {
      const requestData = {
        calculation_type: calculationType,
        applicant: {
          name: applicantName,
          email: applicantEmail,
          phone: applicantPhone
        },
        currency: currency,
        validity_days: parseInt(validityDays)
      };
      
      if (calculationType === 'AFFORDABILITY') {
        requestData.affordability_input = {
          gross_monthly_income: parseFloat(grossIncome),
          dsr_ratio: parseFloat(dsrRatio),
          monthly_obligations: parseFloat(monthlyObligations || 0),
          annual_interest_rate: parseFloat(interestRate) / 100,
          term_years: parseInt(termYears),
          stress_rate_bps: parseInt(stressRateBps || 0)
        };
      } else {
        requestData.payment_input = {
          principal_amount: parseFloat(principalAmount),
          annual_interest_rate: parseFloat(interestRate) / 100,
          term_years: parseInt(termYears),
          stress_rate_bps: parseInt(stressRateBps || 0)
        };
      }
      
      const response = await axios.post(`${BACKEND_URL}/api/calculate`, requestData);
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.message || err.response?.data?.detail || 'An error occurred during calculation');
    } finally {
      setLoading(false);
    }
  };
  
  const handleDownloadCertificate = async () => {
    if (!results || !results.certificate_id) return;
    
    try {
      setLoading(true);
      
      const response = await axios.post(
        `${BACKEND_URL}/api/generate-certificate/${results.certificate_id}`,
        results,
        {
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Pre-Qualification_Certificate_${results.certificate_id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Failed to generate certificate. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-dark-bg' : 'bg-gray-50'} transition-colors duration-200`}>
      {/* Header */}
      <header className="bg-white dark:bg-dark-card shadow-sm transition-colors duration-200">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-lime rounded-full flex items-center justify-center">
              <span className="text-white text-xl font-bold">✓</span>
            </div>
            <h1 className="text-2xl font-bold text-lime">Pre-Qualification App</h1>
          </div>
          
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-border transition-colors"
            title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {darkMode ? '🌞' : '🌙'}
          </button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Calculation Type Tabs */}
        <div className="bg-white dark:bg-dark-card rounded-lg shadow-md p-6 mb-6 transition-colors duration-200">
          <h2 className="text-2xl font-bold text-lime mb-4">New Pre-Qualification</h2>
          
          <div className="flex space-x-2 mb-6">
            <button
              onClick={() => setCalculationType('AFFORDABILITY')}
              className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
                calculationType === 'AFFORDABILITY'
                  ? 'bg-lime text-white shadow-md'
                  : 'bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              Affordability Assessment
            </button>
            <button
              onClick={() => setCalculationType('PAYMENT')}
              className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
                calculationType === 'PAYMENT'
                  ? 'bg-lime text-white shadow-md'
                  : 'bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              Payment Calculation
            </button>
          </div>

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-lg mb-4">
              <p className="font-semibold">Error: {error}</p>
            </div>
          )}

          <form onSubmit={handleCalculate} className="space-y-6">
            {/* Applicant Information */}
            <div>
              <h3 className="text-lg font-semibold text-lime dark:text-lime mb-3">Applicant Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Full Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={applicantName}
                    onChange={(e) => setApplicantName(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                    placeholder="John Doe"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={applicantEmail}
                    onChange={(e) => setApplicantEmail(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                    placeholder="john@example.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={applicantPhone}
                    onChange={(e) => setApplicantPhone(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
              </div>
            </div>

            {/* Financial Details */}
            <div>
              <h3 className="text-lg font-semibold text-lime dark:text-lime mb-3">Financial Details</h3>
              
              {calculationType === 'AFFORDABILITY' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Gross Monthly Income <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="number"
                      required
                      step="0.01"
                      value={grossIncome}
                      onChange={(e) => setGrossIncome(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                      placeholder="5000.00"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      DSR Ratio <span className="text-red-500">*</span>
                    </label>
                    <select
                      required
                      value={dsrRatio}
                      onChange={(e) => setDsrRatio(parseFloat(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                    >
                      <option value="0.3">30%</option>
                      <option value="0.35">35%</option>
                      <option value="0.4">40%</option>
                      <option value="0.45">45%</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Existing Monthly Obligations
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={monthlyObligations}
                      onChange={(e) => setMonthlyObligations(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                      placeholder="500.00"
                    />
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Principal Loan Amount <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    required
                    step="0.01"
                    value={principalAmount}
                    onChange={(e) => setPrincipalAmount(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                    placeholder="250000.00"
                  />
                </div>
              )}

              {/* Common Fields */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Interest Rate (%) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    required
                    step="0.01"
                    value={interestRate}
                    onChange={(e) => setInterestRate(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                    placeholder="4.5"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Loan Term (Years) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="number"
                    required
                    value={termYears}
                    onChange={(e) => setTermYears(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                    placeholder="20"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Stress Test (bps)
                  </label>
                  <input
                    type="number"
                    value={stressRateBps}
                    onChange={(e) => setStressRateBps(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                    placeholder="200"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Currency
                  </label>
                  <select
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                  >
                    <option value="TTD">TTD</option>
                    <option value="USD">USD</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Certificate Validity (Days)
                  </label>
                  <input
                    type="number"
                    value={validityDays}
                    onChange={(e) => setValidityDays(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-lime focus:border-transparent dark:bg-dark-border dark:text-white"
                    placeholder="90"
                  />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-lime text-white py-3 px-6 rounded-lg font-semibold hover:bg-lime-dark transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
            >
              {loading ? 'Calculating...' : 'Calculate Pre-Qualification'}
            </button>
          </form>
        </div>

        {/* Results */}
        {results && (
          <div className="bg-white dark:bg-dark-card rounded-lg shadow-md p-6 transition-colors duration-200">
            <h3 className="text-2xl font-bold text-lime mb-4">Pre-Qualification Results</h3>
            
            <div className="bg-green-50 dark:bg-green-900/20 border-2 border-lime rounded-lg p-6 mb-4">
              <div className="flex justify-between items-center mb-4">
                <span className="text-sm text-gray-600 dark:text-gray-400">Certificate ID: {results.certificate_id}</span>
                <span className="text-sm text-gray-600 dark:text-gray-400">Valid until: {results.expiry_date}</span>
              </div>
              
              {results.calculation_type === 'AFFORDABILITY' ? (
                <div>
                  <div className="text-center mb-4">
                    <p className="text-gray-600 dark:text-gray-400 mb-1">Maximum Loan Amount</p>
                    <p className="text-4xl font-bold text-lime">{results.max_loan_formatted}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600 dark:text-gray-400">Monthly Payment</p>
                      <p className="font-semibold dark:text-white">{results.affordable_payment_formatted}</p>
                    </div>
                    <div>
                      <p className="text-gray-600 dark:text-gray-400">Interest Rate</p>
                      <p className="font-semibold dark:text-white">{results.interest_rate_percent}%</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div>
                  <div className="text-center mb-4">
                    <p className="text-gray-600 dark:text-gray-400 mb-1">Monthly Payment</p>
                    <p className="text-4xl font-bold text-lime">{results.monthly_payment_formatted}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600 dark:text-gray-400">Total Interest</p>
                      <p className="font-semibold dark:text-white">{results.total_interest_formatted}</p>
                    </div>
                    <div>
                      <p className="text-gray-600 dark:text-gray-400">Total Payments</p>
                      <p className="font-semibold dark:text-white">{results.total_payments_formatted}</p>
                    </div>
                  </div>
                </div>
              )}

              {results.stress_test && (
                <div className="mt-4 pt-4 border-t border-lime/30">
                  <p className="text-sm font-semibold text-orange-600 dark:text-orange-400 mb-2">
                    Stress Test (+{results.stress_test.stress_rate_bps} bps to {results.stress_test.stress_rate_percent}%)
                  </p>
                  {results.calculation_type === 'AFFORDABILITY' ? (
                    <p className="text-sm dark:text-gray-300">
                      Max Loan: {results.stress_test.stress_max_loan_formatted} 
                      <span className="text-red-600 dark:text-red-400"> ({results.stress_test.reduction_percent}% reduction)</span>
                    </p>
                  ) : (
                    <p className="text-sm dark:text-gray-300">
                      Monthly Payment: {results.stress_test.stress_payment_formatted}
                      <span className="text-red-600 dark:text-red-400"> (+{results.stress_test.increase_percent}% increase)</span>
                    </p>
                  )}
                </div>
              )}
            </div>

            <button
              onClick={handleDownloadCertificate}
              disabled={loading}
              className="w-full bg-lime text-white py-3 px-6 rounded-lg font-semibold hover:bg-lime-dark transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
            >
              {loading ? 'Generating...' : 'Download Certificate (PDF)'}
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-dark-card border-t border-gray-200 dark:border-dark-border py-6 mt-12 transition-colors duration-200">
        <div className="container mx-auto px-4 text-center">
          <p className="text-lime font-bold text-lg">Pre-Qualification App</p>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Your Mortgage Calculator</p>
          <p className="text-gray-500 dark:text-gray-500 text-xs mt-2">© 2025 Pre-Qualification App. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default Calculator;
