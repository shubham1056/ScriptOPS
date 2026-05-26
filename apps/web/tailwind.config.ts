import type { Config } from 'tailwindcss';

/**
 * TranscribeOP — Claude-inspired design tokens
 * Warm ivory canvas, terracotta accent, serif headings.
 */
const config: Config = {
  darkMode: ['class'],
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    container: { center: true, padding: '1.5rem', screens: { '2xl': '1320px' } },
    extend: {
      colors: {
        // Claude palette
        ivory: {
          50: '#FAF9F5',
          100: '#F5F3EE',
          200: '#EDEAE0',
          300: '#E2DDCC',
        },
        ink: {
          50: '#F5F4EF',
          100: '#E8E5DC',
          400: '#8C8674',
          600: '#5C5849',
          800: '#3D3929',
          900: '#1F1E1A',
        },
        accent: {
          50: '#FDF1EC',
          100: '#FADCCE',
          400: '#E08B66',
          500: '#C96442', // Claude orange
          600: '#B14F30',
          700: '#8F3F26',
        },
        border: 'rgb(229 226 215)',
        ring: 'rgb(201 100 66 / 0.4)',
        background: '#FAF9F5',
        foreground: '#1F1E1A',
        muted: { DEFAULT: '#F5F3EE', foreground: '#5C5849' },
        card: { DEFAULT: '#FFFFFF', foreground: '#1F1E1A' },
        popover: { DEFAULT: '#FFFFFF', foreground: '#1F1E1A' },
        primary: { DEFAULT: '#C96442', foreground: '#FFFFFF' },
        secondary: { DEFAULT: '#EDEAE0', foreground: '#3D3929' },
        destructive: { DEFAULT: '#B91C1C', foreground: '#FFFFFF' },
        input: '#E2DDCC',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'ui-sans-serif', 'system-ui'],
        serif: ['var(--font-serif)', 'Georgia', 'ui-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      borderRadius: {
        lg: '0.875rem',
        md: '0.625rem',
        sm: '0.375rem',
      },
      boxShadow: {
        soft: '0 1px 2px rgba(31, 30, 26, 0.04), 0 2px 8px rgba(31, 30, 26, 0.04)',
        lift: '0 8px 24px -8px rgba(31, 30, 26, 0.12)',
      },
      keyframes: {
        'fade-in': { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        shimmer: { '100%': { transform: 'translateX(100%)' } },
        blink: { '0%,50%': { opacity: '1' }, '50.01%,100%': { opacity: '0' } },
      },
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        'slide-up': 'slide-up 0.4s ease-out',
        blink: 'blink 1s steps(1) infinite',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};
export default config;
