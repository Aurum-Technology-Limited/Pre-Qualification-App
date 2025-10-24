import React, { useState } from 'react';
import './App.css';
import axios from 'axios';
import { supabase } from './supabaseClient';
import { useTheme } from './ThemeContext';

// In development, proxy handles routing to backend (see package.json proxy setting)
// In production, use environment variable or empty string for same-origin requests
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';

function Calculator({ user, onSignOut }) {
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
      // Get auth token
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        setError('Not authenticated. Please log in again.');
        setLoading(false);
        return;
      }
      
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
      
      const response = await axios.post(`${BACKEND_URL}/api/calculate`, requestData, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });
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
      
      // Get auth token
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        setError('Not authenticated. Please log in again.');
        setLoading(false);
        return;
      }
      
      const response = await axios.post(
        `${BACKEND_URL}/api/generate-certificate/${results.certificate_id}`,
        {},
        { 
          responseType: 'blob',
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
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
  
  const handleReset = () => {
    setResults(null);
    setError(null);
    setApplicantName('');
    setApplicantEmail('');
    setApplicantPhone('');
    setGrossIncome('');
    setDsrRatio(0.4);
    setMonthlyObligations('');
    setPrincipalAmount('');
    setInterestRate('');
    setTermYears('20');
    setStressRateBps('');
  };
  
  const formatCurrency = (value) => {
    if (!value) return '';
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };
  
  return (
    <div className="App min-h-screen bg-gray-50 dark:bg-dark-bg transition-colors duration-200">
      {/* Navigation Bar */}
      <nav className="nav-bar py-4 px-6 shadow-lg dark:bg-gradient-to-r dark:from-lime-dark dark:to-lime">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center">
            <h1 className="text-3xl font-bold text-white" data-testid="app-title">Pre-Qualification App</h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-white text-sm">
              <span data-testid="user-email">{user?.email}</span>
            </div>
            <button
              onClick={toggleDarkMode}
              className="text-white hover:text-lime-light transition-colors p-2 rounded-lg hover:bg-white/10"
              data-testid="dark-mode-toggle"
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {darkMode ? (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
            <button
              onClick={onSignOut}
              className="bg-white text-lime hover:bg-lime-light hover:text-white border-2 border-white rounded-lg py-2 px-4 font-semibold transition-colors text-sm"
              data-testid="logout-button"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>
      
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {!results ? (
          <div className="card p-8 fade-in bg-white dark:bg-dark-card transition-colors duration-200" data-testid="calculation-form">
            <h2 className="text-2xl font-bold text-lime-dark dark:text-lime mb-6">New Pre-Qualification</h2>
            
            {/* Calculation Type Tabs */}
            <div className="flex border-b border-gray-200 mb-8">
              <button
                className={`tab-button ${calculationType === 'AFFORDABILITY' ? 'active' : ''}`}
                onClick={() => setCalculationType('AFFORDABILITY')}
                data-testid="affordability-tab"
              >
                Affordability Assessment
              </button>
              <button
                className={`tab-button ${calculationType === 'PAYMENT' ? 'active' : ''}`}
                onClick={() => setCalculationType('PAYMENT')}
                data-testid="payment-tab"
              >
                Payment Calculation
              </button>
            </div>
            
            {error && (
              <div className="alert alert-error" data-testid="error-message">
                <strong>Error:</strong> {error}
              </div>
            )}
            
            <form onSubmit={handleCalculate}>
              {/* Applicant Information */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-lime mb-4">Applicant Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-lime-dark dark:text-lime font-semibold mb-2">
                      Full Name <span className="text-lime">*</span>
                    </label>
                    <input
                      type="text"
                      className="input-field bg-white dark:bg-dark-bg dark:text-dark-text dark:border-dark-border"
                      value={applicantName}
                      onChange={(e) => setApplicantName(e.target.value)}
                      required
                      data-testid="applicant-name-input"
                    />
                  </div>
                  <div>
                    <label className="block text-lime-dark font-semibold mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      className="input-field"
                      value={applicantEmail}
                      onChange={(e) => setApplicantEmail(e.target.value)}
                      data-testid="applicant-email-input"
                    />
                  </div>
                  <div>
                    <label className="block text-lime-dark font-semibold mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      className="input-field"
                      value={applicantPhone}
                      onChange={(e) => setApplicantPhone(e.target.value)}
                      data-testid="applicant-phone-input"
                    />
                  </div>
                </div>
              </div>
              
              {/* Calculation-Specific Fields */}
              {calculationType === 'AFFORDABILITY' ? (
                <div className="mb-8">
                  <h3 className="text-xl font-semibold text-lime mb-4">Financial Details</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-lime-dark font-semibold mb-2">
                        Gross Monthly Income ({currency}) <span className="text-lime">*</span>
                      </label>
                      <input
                        type="number"
                        className="input-field"
                        value={grossIncome}
                        onChange={(e) => setGrossIncome(e.target.value)}
                        min="0"
                        step="0.01"
                        required
                        data-testid="gross-income-input"
                      />
                    </div>
                    <div>
                      <label className="block text-lime-dark font-semibold mb-2">
                        Monthly Debt Obligations ({currency})
                      </label>
                      <input
                        type="number"
                        className="input-field"
                        value={monthlyObligations}
                        onChange={(e) => setMonthlyObligations(e.target.value)}
                        min="0"
                        step="0.01"
                        data-testid="monthly-obligations-input"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-6">
                    <label className="block text-lime-dark font-semibold mb-2">
                      Debt Service Ratio (DSR): {(dsrRatio * 100).toFixed(0)}%
                    </label>
                    <div className="slider-container">
                      <input
                        type="range"
                        min="0.1"
                        max="0.8"
                        step="0.05"
                        value={dsrRatio}
                        onChange={(e) => setDsrRatio(parseFloat(e.target.value))}
                        data-testid="dsr-ratio-slider"
                      />
                      <div className="flex justify-between text-sm text-gray-600 mt-1">
                        <span>10%</span>
                        <span>40%</span>
                        <span>80%</span>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="mb-8">
                  <h3 className="text-xl font-semibold text-lime mb-4">Loan Details</h3>
                  <div>
                    <label className="block text-lime-dark font-semibold mb-2">
                      Principal Loan Amount ({currency}) <span className="text-lime">*</span>
                    </label>
                    <input
                      type="number"
                      className="input-field"
                      value={principalAmount}
                      onChange={(e) => setPrincipalAmount(e.target.value)}
                      min="0"
                      step="0.01"
                      required
                      data-testid="principal-amount-input"
                    />
                  </div>
                </div>
              )}
              
              {/* Common Loan Parameters */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-lime mb-4">Loan Terms</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div>
                    <label className="block text-lime-dark font-semibold mb-2">
                      Annual Interest Rate (%) <span className="text-lime">*</span>
                    </label>
                    <input
                      type="number"
                      className="input-field"
                      value={interestRate}
                      onChange={(e) => setInterestRate(e.target.value)}
                      min="0.1"
                      max="50"
                      step="0.1"
                      required
                      data-testid="interest-rate-input"
                    />
                  </div>
                  <div>
                    <label className="block text-lime-dark font-semibold mb-2">
                      Loan Term (Years) <span className="text-lime">*</span>
                    </label>
                    <select
                      className="input-field"
                      value={termYears}
                      onChange={(e) => setTermYears(e.target.value)}
                      required
                      data-testid="term-years-select"
                    >
                      {[5, 10, 15, 20, 25, 30].map(year => (
                        <option key={year} value={year}>{year} years</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-lime-dark font-semibold mb-2">
                      Currency
                    </label>
                    <select
                      className="input-field"
                      value={currency}
                      onChange={(e) => setCurrency(e.target.value)}
                      data-testid="currency-select"
                    >
                      <option value="TTD">TTD - Trinidad & Tobago Dollar</option>
                      <option value="USD">USD - US Dollar</option>
                      <option value="CAD">CAD - Canadian Dollar</option>
                    </select>
                  </div>
                </div>
              </div>
              
              {/* Optional Parameters */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-lime mb-4">Optional Parameters</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-lime-dark font-semibold mb-2">
                      Stress Test Rate (basis points)
                    </label>
                    <input
                      type="number"
                      className="input-field"
                      value={stressRateBps}
                      onChange={(e) => setStressRateBps(e.target.value)}
                      min="0"
                      max="1000"
                      placeholder="e.g., 200 for +2%"
                      data-testid="stress-rate-input"
                    />
                  </div>
                  <div>
                    <label className="block text-lime-dark font-semibold mb-2">
                      Certificate Validity (Days)
                    </label>
                    <select
                      className="input-field"
                      value={validityDays}
                      onChange={(e) => setValidityDays(e.target.value)}
                      data-testid="validity-days-select"
                    >
                      <option value="60">60 days</option>
                      <option value="90">90 days</option>
                      <option value="120">120 days</option>
                    </select>
                  </div>
                </div>
              </div>
              
              {/* Submit Button */}
              <div className="flex justify-end gap-4">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleReset}
                  data-testid="reset-button"
                >
                  Reset Form
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={loading}
                  data-testid="calculate-button"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <div className="loading-spinner" style={{width: '20px', height: '20px', borderWidth: '3px'}}></div>
                      Calculating...
                    </span>
                  ) : (
                    'Calculate'
                  )}
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="fade-in" data-testid="results-section">
            {/* Results Display */}
            <div className="card p-8 mb-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-lime mb-2">Assessment Results</h2>
                  <p className="text-gray-600">Certificate ID: <span className="font-mono font-semibold" data-testid="certificate-id">{results.certificate_id}</span></p>
                </div>
                <button
                  onClick={handleReset}
                  className="btn-secondary"
                  data-testid="new-calculation-button"
                >
                  New Calculation
                </button>
              </div>
              
              {calculationType === 'AFFORDABILITY' ? (
                <div>
                  <div className="results-card p-6 rounded-lg mb-6">
                    <h3 className="text-lg font-semibold text-lime-dark mb-4">Affordability Summary</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <p className="text-gray-600 mb-1">Affordable Monthly Payment</p>
                        <p className="text-2xl font-bold text-lime-dark" data-testid="affordable-payment">{results.affordable_payment_formatted}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Maximum Loan Amount</p>
                        <p className="amount-highlight" data-testid="max-loan-amount">{results.max_loan_formatted}</p>
                      </div>
                    </div>
                  </div>
                  
                  {results.stress_test && (
                    <div className="alert alert-warning mb-6" data-testid="stress-test-results">
                      <h4 className="font-bold mb-2">Stress Test Results (+ {results.stress_test.stress_rate_bps} bps)</h4>
                      <p>At stressed rate of {results.stress_test.stress_rate_percent}%, maximum loan reduces to:</p>
                      <p className="text-xl font-bold mt-2">{results.stress_test.stress_max_loan_formatted}</p>
                      <p className="text-sm mt-1">Reduction: {results.stress_test.reduction_percent}% ({results.currency} ${formatCurrency(results.stress_test.reduction_amount)})</p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Gross Monthly Income</p>
                      <p className="text-lg font-semibold text-lime-dark">{currency} ${formatCurrency(results.gross_monthly_income)}</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">DSR Ratio</p>
                      <p className="text-lg font-semibold text-lime-dark">{(results.dsr_ratio * 100).toFixed(0)}%</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Monthly Obligations</p>
                      <p className="text-lg font-semibold text-lime-dark">{currency} ${formatCurrency(results.monthly_obligations)}</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div>
                  <div className="results-card p-6 rounded-lg mb-6">
                    <h3 className="text-lg font-semibold text-lime-dark mb-4">Payment Summary</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <p className="text-gray-600 mb-1">Principal Loan Amount</p>
                        <p className="text-2xl font-bold text-lime-dark" data-testid="principal-display">{results.principal_formatted}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Monthly Payment</p>
                        <p className="amount-highlight" data-testid="monthly-payment-display">{results.monthly_payment_formatted}</p>
                      </div>
                    </div>
                  </div>
                  
                  {results.stress_test && (
                    <div className="alert alert-warning mb-6" data-testid="stress-test-payment-results">
                      <h4 className="font-bold mb-2">Stress Test Results (+ {results.stress_test.stress_rate_bps} bps)</h4>
                      <p>At stressed rate of {results.stress_test.stress_rate_percent}%, monthly payment increases to:</p>
                      <p className="text-xl font-bold mt-2">{results.stress_test.stress_payment_formatted}</p>
                      <p className="text-sm mt-1">Increase: {results.stress_test.increase_percent}% ({results.currency} ${formatCurrency(results.stress_test.increase_amount)})</p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Total Amount Paid</p>
                      <p className="text-lg font-semibold text-lime-dark">{results.total_payments_formatted}</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Total Interest Paid</p>
                      <p className="text-lg font-semibold text-lime-dark">{results.total_interest_formatted}</p>
                    </div>
                  </div>
                </div>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Interest Rate</p>
                  <p className="text-lg font-semibold text-lime-dark">{results.interest_rate_percent}% per annum</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Loan Term</p>
                  <p className="text-lg font-semibold text-lime-dark">{results.term_years} years</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Valid Until</p>
                  <p className="text-lg font-semibold text-lime-dark">{results.expiry_date}</p>
                </div>
              </div>
            </div>
            
            {/* Certificate Generation */}
            <div className="card p-8">
              <h3 className="text-xl font-semibold text-lime mb-4">Generate Certificate</h3>
              <p className="text-gray-600 mb-6">
                Download a professional pre-qualification certificate for {results.applicant.name}.
              </p>
              
              <div className="alert alert-success mb-6">
                <p><strong>✓ Calculation Complete</strong></p>
                <p>Your pre-qualification assessment has been completed and saved.</p>
                <p className="text-sm mt-2">Issue Date: {results.issue_date} | Expiry Date: {results.expiry_date}</p>
              </div>
              
              <div className="flex justify-center">
                <button
                  onClick={handleDownloadCertificate}
                  className="btn-primary"
                  disabled={loading}
                  data-testid="download-certificate-button"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <div className="loading-spinner" style={{width: '20px', height: '20px', borderWidth: '3px'}}></div>
                      Generating PDF...
                    </span>
                  ) : (
                    '📄 Download Certificate (PDF)'
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Footer */}
      <footer className="bg-white dark:bg-dark-card border-t border-gray-200 dark:border-dark-border py-6 mt-12 transition-colors duration-200">
        <div className="container mx-auto px-4 text-center">
          <p className="text-lime font-bold text-lg">Pre-Qualification App</p>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">Your Mortgage Calculator</p>
          <p className="text-gray-500 dark:text-gray-500 text-xs mt-2">© 2024 Pre-Qualification App. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default Calculator;