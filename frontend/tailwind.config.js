module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        'lime': '#32CD32',
        'lime-dark': '#228B22',
        'lime-light': '#90EE90',
        'error': '#DC3545',
        'warning': '#FD7E14',
        'success': '#228B22'
      }
    },
  },
  plugins: [],
}