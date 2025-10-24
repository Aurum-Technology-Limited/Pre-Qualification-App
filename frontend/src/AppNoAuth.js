import React from 'react';
import Calculator from './CalculatorNoAuth';
import { ThemeProvider } from './ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <Calculator />
    </ThemeProvider>
  );
}

export default App;
