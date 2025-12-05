import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
    },
    // For production builds: use VITE_API_URL environment variable
    define: {
        'import.meta.env.VITE_API_URL': JSON.stringify(
            process.env.VITE_API_URL || ''
        )
    }
})
