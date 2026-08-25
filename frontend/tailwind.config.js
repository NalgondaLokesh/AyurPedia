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
        primary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#2d6a4f',
          600: '#1a4d2e',
          700: '#143d24',
          800: '#0f2e1b',
          900: '#0a1f12',
          DEFAULT: '#1a4d2e',
        },
        secondary: {
          50: '#e8f5e9',
          100: '#c8e6c9',
          500: '#2d6a4f',
          600: '#1b4332',
          DEFAULT: '#2d6a4f',
        },
        accent: {
          50: '#fdfbf7',
          100: '#faedcd',
          400: '#e9d8a6',
          500: '#d4a373',
          600: '#bc6c25',
          DEFAULT: '#d4a373',
        },
        herbal: {
          sage: '#84a98c',
          forest: '#1b4332',
          leaf: '#52b788',
          mint: '#74c69d',
          gold: '#dda15e'
        },
        confidence: {
          high: '#16a34a',
          medium: '#ca8a04',
          low: '#dc2626'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        devanagari: ['Noto Sans Devanagari', 'sans-serif'],
        serif: ['Merriweather', 'serif']
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.08)',
        'glass-dark': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'subtle': '0 2px 10px rgba(26, 77, 46, 0.08)',
      }
    },
  },
  plugins: [],
}
