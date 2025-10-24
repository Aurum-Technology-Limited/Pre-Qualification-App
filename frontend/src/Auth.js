import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useTheme } from './ThemeContext';
import './App.css';

function Auth() {
  const { darkMode, toggleDarkMode } = useTheme();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const { signIn, signUp } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      if (isLogin) {
        const { error } = await signIn(email, password);
        if (error) throw error;
      } else {
        const { error } = await signUp(email, password, fullName);
        if (error) throw error;
        setMessage('Account created! Please check your email to confirm your account.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-bg flex flex-col justify-center py-12 sm:px-6 lg:px-8 transition-colors duration-200">
      {/* Dark Mode Toggle */}
      <div className="absolute top-4 right-4">
        <button
          onClick={toggleDarkMode}
          className="text-lime-dark dark:text-lime hover:text-lime dark:hover:text-lime-light transition-colors p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-dark-card"
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
      </div>
      
      {/* Header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="bg-lime rounded-full p-4">
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-lime-dark">
          Pre-Qualification App
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          {isLogin ? 'Sign in to your account' : 'Create a new account'}
        </p>
      </div>

      {/* Form */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
          {error && (
            <div className="alert alert-error mb-4" data-testid="auth-error">
              <strong>Error:</strong> {error}
            </div>
          )}
          
          {message && (
            <div className="alert alert-success mb-4" data-testid="auth-message">
              {message}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {!isLogin && (
              <div>
                <label htmlFor="fullName" className="block text-sm font-medium text-lime-dark">
                  Full Name
                </label>
                <div className="mt-1">
                  <input
                    id="fullName"
                    name="fullName"
                    type="text"
                    required={!isLogin}
                    className="input-field"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    data-testid="fullname-input"
                  />
                </div>
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-lime-dark">
                Email Address
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className="input-field"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  data-testid="email-input"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-lime-dark">
                Password
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete={isLogin ? 'current-password' : 'new-password'}
                  required
                  className="input-field"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  data-testid="password-input"
                  minLength={6}
                />
              </div>
              {!isLogin && (
                <p className="mt-1 text-xs text-gray-500">Must be at least 6 characters</p>
              )}
            </div>

            <div>
              <button
                type="submit"
                className="btn-primary w-full"
                disabled={loading}
                data-testid="auth-submit-button"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="loading-spinner" style={{width: '20px', height: '20px', borderWidth: '3px'}}></div>
                    {isLogin ? 'Signing in...' : 'Creating account...'}
                  </span>
                ) : (
                  isLogin ? 'Sign In' : 'Sign Up'
                )}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or</span>
              </div>
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError(null);
                  setMessage(null);
                }}
                className="text-lime font-medium hover:text-lime-dark"
                data-testid="toggle-auth-mode"
              >
                {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Auth;