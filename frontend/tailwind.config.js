module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'lime': '#32CD32',
        'lime-dark': '#228B22',
        'lime-light': '#90EE90',
        'error': '#DC3545',
        'warning': '#FD7E14',
        'success': '#228B22',
        'dark-bg': '#1a1a1a',
        'dark-card': '#2d2d2d',
        'dark-border': '#404040',
        'dark-text': '#e0e0e0'
      }
    },
  },
  plugins: [],
}