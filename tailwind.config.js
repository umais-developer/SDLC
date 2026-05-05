/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        alive: '#10b981',
        dead: '#f3f4f6',
        grid: '#e5e7eb',
      },
    },
  },
  plugins: [],
}
