import React from 'react';
import { AuthProvider, useAuth } from './AuthContext';
import { ThemeProvider } from './ThemeContext';
import Auth from './Auth';
import Calculator from './Calculator';

function AppContent() {
  const { user, loading, signOut } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-dark-bg flex items-center justify-center transition-colors duration-200">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4" style={{width: '50px', height: '50px', borderWidth: '4px'}}></div>
          <p className="text-lime-dark dark:text-lime font-semibold">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Auth />;
  }

  return <Calculator user={user} onSignOut={signOut} />;
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
