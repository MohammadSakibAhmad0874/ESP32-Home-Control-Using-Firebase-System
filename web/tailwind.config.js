/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0E14',
        surface: 'rgba(26, 31, 46, 0.65)',
        surfaceBorder: 'rgba(255, 255, 255, 0.1)',
        neonCyan: '#00D9FF',
        neonMagenta: '#FF2E93',
        neonPurple: '#8B5CF6',
        neonYellow: '#EAAA00',
        textPrimary: '#DDE3E8',
        textSecondary: '#8B9BB4',
        textMuted: '#58677E'
      },
      fontFamily: {
        sans: ['"Space Grotesk"', 'Outfit', 'Inter', 'sans-serif'],
      },
      animation: {
        'float-slow': 'floatSlow 4s ease-in-out infinite',
        'pulse-glow': 'pulseGlow 2.5s infinite',
      },
      keyframes: {
        floatSlow: {
          '0%, 100%': { transform: 'translateY(0px) rotateX(4deg) rotateY(-4deg)' },
          '50%': { transform: 'translateY(-14px) rotateX(0deg) rotateY(0deg)' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '0.6', filter: 'drop-shadow(0 0 15px rgba(0,217,255,0.4))' },
          '50%': { opacity: '1', filter: 'drop-shadow(0 0 30px rgba(0,217,255,0.8))' },
        }
      }
    },
  },
  plugins: [],
}
