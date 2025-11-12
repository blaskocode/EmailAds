/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // HiBid Brand Colors
        'hibid': {
          'blue': {
            '50': '#EFF6FF',
            '100': '#DBEAFE',
            '200': '#BFDBFE',
            '300': '#93C5FD',
            '400': '#60A5FA',
            '500': '#3B82F6', // Primary vibrant blue
            '600': '#2563EB', // Primary blue (main)
            '700': '#1D4ED8',
            '800': '#1E40AF',
            '900': '#1E3A8A',
          },
          'gray': {
            '50': '#F9FAFB',  // Light gray/white
            '100': '#F3F4F6',
            '200': '#E5E7EB',
            '300': '#D1D5DB',
            '400': '#9CA3AF',
            '500': '#6B7280',
            '600': '#4B5563',
            '700': '#374151',
            '800': '#1F2937',  // Dark gray for text
            '900': '#111827',  // Darker gray for headings
          },
        },
      },
      backgroundImage: {
        'gradient-hibid': 'linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)',
        'gradient-hibid-subtle': 'linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)',
      },
      boxShadow: {
        'hibid': '0 4px 6px -1px rgba(37, 99, 235, 0.1), 0 2px 4px -1px rgba(37, 99, 235, 0.06)',
        'hibid-lg': '0 10px 15px -3px rgba(37, 99, 235, 0.1), 0 4px 6px -2px rgba(37, 99, 235, 0.05)',
      },
    },
  },
  plugins: [],
}

