/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#0f172a",
                primary: "#06b6d4", // cyan-500
                secondary: "#8b5cf6", // violet-500
                accent: "#f472b6", // pink-400
                surface: "rgba(30, 41, 59, 0.7)", // slate-800 with opacity
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
