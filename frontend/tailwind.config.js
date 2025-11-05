/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        // Web3-inspired color palette
        primary: {
          50: '#f0fdfa',   // lightest teal
          100: '#ccfbf1',  
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',  // main teal
          500: '#14b8a6',  // darker teal
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',  // darkest teal
        },
        accent: {
          50: '#f0f9ff',   // lightest blue
          100: '#e0f2fe',
          200: '#bae6fd', 
          300: '#7dd3fc',
          400: '#38bdf8',  // electric blue
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',  // darkest blue
        },
        success: {
          50: '#f0fdf4',   // lightest green
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',  // neon green
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',  // darkest green
        },
        warning: {
          50: '#fefce8',   // lightest yellow
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',  // golden yellow
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',  // darkest orange
        },
        danger: {
          50: '#fef2f2',   // lightest red
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',  // coral red
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',  // darkest red
        },
        // Dark mode color scheme
        dark: {
          50: '#f8fafc',   // lightest
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',  // mid gray
          600: '#475569',
          700: '#334155',
          800: '#1e293b',  // dark card bg
          850: '#172033',  // darker bg
          900: '#0f172a',  // darkest bg
          950: '#020617',  // ultra dark
        },
        // Blockchain/Web3 specific colors
        crypto: {
          bitcoin: '#f7931a',
          ethereum: '#627eea', 
          polygon: '#8247e5',
          solana: '#00ffa3',
          cardano: '#0033ad',
        }
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['JetBrains Mono', 'Fira Code', 'ui-monospace'],
        display: ['Space Grotesk', 'Inter', 'ui-sans-serif'],
      },
      fontSize: {
        '2xs': '0.625rem',    // 10px
        '3xl': '1.953rem',    // ~31px
        '4xl': '2.441rem',    // ~39px  
        '5xl': '3.052rem',    // ~49px
      },
      spacing: {
        '18': '4.5rem',       // 72px
        '88': '22rem',        // 352px
        '112': '28rem',       // 448px
        '128': '32rem',       // 512px
      },
      borderRadius: {
        'xl': '0.75rem',      // 12px
        '2xl': '1rem',        // 16px
        '3xl': '1.5rem',      // 24px
        '4xl': '2rem',        // 32px
      },
      boxShadow: {
        'glow': '0 0 20px rgba(45, 212, 191, 0.3)',
        'glow-lg': '0 0 40px rgba(45, 212, 191, 0.4)',
        'danger-glow': '0 0 20px rgba(248, 113, 113, 0.3)',
        'success-glow': '0 0 20px rgba(74, 222, 128, 0.3)',
        'dark': '0 10px 25px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.1)',
        'inner-glow': 'inset 0 2px 4px 0 rgba(45, 212, 191, 0.1)',
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite alternate',
        'progress-fill': 'progressFill 1.5s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        glowPulse: {
          '0%': { boxShadow: '0 0 20px rgba(45, 212, 191, 0.3)' },
          '100%': { boxShadow: '0 0 40px rgba(45, 212, 191, 0.6)' },
        },
        progressFill: {
          '0%': { width: '0%' },
          '100%': { width: 'var(--progress-width)' },
        },
      },
      backdropBlur: {
        xs: '2px',
        '4xl': '72px',
      },
      gradientColorStops: theme => ({
        ...theme('colors'),
        'cyber-gradient-start': '#14b8a6',
        'cyber-gradient-end': '#0ea5e9', 
      }),
      screens: {
        'xs': '475px',
        '3xl': '1600px',
        '4xl': '2000px',
      }
    },
  },
  plugins: [
    // Custom plugin for Web3-specific utilities
    function({ addUtilities, theme }) {
      const newUtilities = {
        '.glass-effect': {
          'background': 'rgba(255, 255, 255, 0.05)',
          'backdrop-filter': 'blur(10px)',
          'border': '1px solid rgba(255, 255, 255, 0.1)',
        },
        '.glass-dark': {
          'background': 'rgba(0, 0, 0, 0.2)',
          'backdrop-filter': 'blur(16px)',
          'border': '1px solid rgba(255, 255, 255, 0.05)',
        },
        '.cyber-border': {
          'border': '1px solid transparent',
          'background': 'linear-gradient(90deg, #14b8a6, #0ea5e9) border-box',
          'border-image': 'linear-gradient(90deg, #14b8a6, #0ea5e9) 1',
        },
        '.text-gradient': {
          'background': 'linear-gradient(90deg, #14b8a6, #0ea5e9)',
          'background-clip': 'text',
          '-webkit-background-clip': 'text',
          'color': 'transparent',
        },
        '.btn-cyber': {
          'background': 'linear-gradient(135deg, #14b8a6, #0ea5e9)',
          'box-shadow': '0 4px 15px rgba(45, 212, 191, 0.3)',
          'transition': 'all 0.3s ease',
          '&:hover': {
            'transform': 'translateY(-2px)',
            'box-shadow': '0 8px 25px rgba(45, 212, 191, 0.4)',
          }
        },
        '.card-cyber': {
          'background': 'rgba(30, 41, 59, 0.9)',
          'backdrop-filter': 'blur(16px)',
          'border': '1px solid rgba(45, 212, 191, 0.2)',
          'box-shadow': '0 8px 32px rgba(0, 0, 0, 0.3)',
        },
        '.risk-bar-low': {
          'background': 'linear-gradient(90deg, #22c55e, #4ade80)',
        },
        '.risk-bar-medium': {
          'background': 'linear-gradient(90deg, #fbbf24, #f59e0b)',
        },
        '.risk-bar-high': {
          'background': 'linear-gradient(90deg, #f59e0b, #ef4444)',
        },
        '.risk-bar-critical': {
          'background': 'linear-gradient(90deg, #ef4444, #dc2626)',
        }
      }
      addUtilities(newUtilities)
    }
  ],
}