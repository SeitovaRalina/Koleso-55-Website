/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0B8ED8',
        brand: {
          sky: '#0B8ED8',
          deep: '#0A3F9A',
          mist: '#D9EEF7',
        },
        nature: {
          green: '#6FA36B',
        },
        heritage: {
          cream: '#F4EFE6',
          brick: '#9B4A31',
        },
        neutral: {
          ink: '#172033',
          text: '#4B5563',
          line: '#E5E7EB',
          surface: '#FFFFFF',
        },
      },
      maxWidth: {
        content: '1180px',
      },
      borderRadius: {
        card: '8px',
      },
      boxShadow: {
        editorial: '0 18px 45px rgba(23, 32, 51, 0.08)',
      },
    },
  },
  plugins: [],
}
