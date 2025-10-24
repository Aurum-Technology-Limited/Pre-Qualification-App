import React from 'react';
import Calculator from './Calculator';
import { ThemeProvider } from './ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <Calculator />
    </ThemeProvider>
  );
}

export default App;
