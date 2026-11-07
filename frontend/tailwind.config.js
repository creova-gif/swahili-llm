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
        canvas: {
          DEFAULT: '#090d16',
          surface: '#0f1726',
          elevated: '#152033',
          subtle: '#1c2a42',
          input: '#0b111c',
          border: 'rgba(255, 255, 255, 0.08)',
          'border-medium': 'rgba(255, 255, 255, 0.16)',
        },
        lugha: {
          emerald: '#10b981',
          'emerald-dim': 'rgba(16, 185, 129, 0.12)',
          'emerald-border': 'rgba(16, 185, 129, 0.35)',
          amber: '#f59e0b',
          'amber-dim': 'rgba(245, 158, 11, 0.12)',
          cyan: '#06b6d4',
          'cyan-dim': 'rgba(6, 182, 212, 0.12)',
          rose: '#f43f5e',
          'rose-dim': 'rgba(244, 63, 94, 0.12)',
        },
        whatsapp: {
          header: '#202c33',
          chatbg: '#0b141a',
          bubbleIn: '#202c33',
          bubbleOut: '#005c4b',
          bubbleInLight: '#ffffff',
          bubbleOutLight: '#d9fdd3',
          accent: '#00a884',
          subtext: '#8696a0',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      animation: {
        'pulse-subtle': 'pulse 2.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        }
      }
    },
  },
  plugins: [],
}
