/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        alpine: {
          950: '#0b0f14',
          900: '#111827',
          850: '#151e2e',
          800: '#1f293d',
          700: '#334155',
          600: '#475569',
          400: '#94a3b8',
          300: '#cbd5e1',
          100: '#f1f5f9',
          50: '#f8fafc',
        },
        sage: '#4a614e',
        terracotta: '#d47c59',
      },
      fontFamily: {
        heading: ['Fraunces', 'serif'],
        sans: ['Plus Jakarta Sans', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
