/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: '#10233F',
        blue: '#3478F6',
        surface: '#F5F7FB',
        card: '#FFFFFF',
        text: '#172B4D',
        muted: '#64748B',
        border: '#E2E8F0',
        success: '#16A36A',
        warning: '#E9A23B',
        danger: '#DC4545',
      },
      boxShadow: {
        soft: '0 12px 30px rgba(15, 23, 42, 0.08)',
      },
    },
  },
  plugins: [],
};
