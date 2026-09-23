/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#070F19',
          900: '#0B1929', // Main background
          850: '#0E2137',
          800: '#132B45', // Card/Surface background
          750: '#173656',
          700: '#1D446C', // Hover / elevated surface
          600: '#255685',
        },
        teal: {
          brand: '#0FB5AE', // Primary interactive accent & cooling
          hover: '#0DA09A',
          muted: 'rgba(15, 181, 174, 0.15)',
          glow: 'rgba(15, 181, 174, 0.3)',
        },
        heat: {
          hot: '#E8543E', // Heat indicators, warming drivers, high LST
          extreme: '#D63031',
          moderate: '#F59E0B',
          mild: '#EAB308',
          cool: '#0FB5AE',
          muted: 'rgba(232, 84, 62, 0.15)',
        },
        gis: {
          border: '#1E3A5F',
          borderSubtle: '#152E4D',
          grid: '#0F253E',
          textMuted: '#94A3B8',
          textMain: '#E2E8F0',
          textHeading: '#F8FAFC',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Roboto Mono', 'monospace'],
        sans: ['Inter', 'Segoe UI', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'panel': '0 4px 20px -2px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(30, 58, 95, 0.6)',
        'modal': '0 20px 40px -10px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(30, 58, 95, 0.8)',
      }
    },
  },
  plugins: [],
}
