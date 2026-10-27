/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        rage: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          950: '#450a0a',
        },
        obsidian: {
          950: '#060608',
          900: '#09090b',
          850: '#0d0d12',
          800: '#121217',
          750: '#181820',
          700: '#22222d',
          600: '#2e2e3d',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'rage-glow': '0 0 25px -5px rgba(239, 68, 68, 0.35)',
        'rage-glow-sm': '0 0 15px -3px rgba(239, 68, 68, 0.25)',
        'rage-glow-lg': '0 0 35px -5px rgba(239, 68, 68, 0.45)',
        'panel': '0 10px 30px -10px rgba(0, 0, 0, 0.6)',
      },
    },
  },
  plugins: [],
}
