/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#0f172a",
        accent: "#7c3aed",
        success: "#22c55e",
        warning: "#f59e0b",
        danger: "#ef4444",
        neutral: {
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          900: "#0f172a",
        },
      },
      borderRadius: {
        "game": "1rem",
        "game-lg": "1.5rem",
      },
      boxShadow: {
        "game-soft": "0 12px 30px rgba(15, 23, 42, 0.18)",
      },
      transitionDuration: {
        150: "150ms",
        200: "200ms",
        250: "250ms",
      },
      fontFamily: {
        heading: ["Fira Code", "Nunito", "sans-serif"],
        body: ["Fira Sans", "Nunito", "sans-serif"],
      },
    },
  },
  plugins: [],
}

