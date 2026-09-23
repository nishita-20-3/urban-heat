import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/cities': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/grid': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/predict': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/shap': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/recommendations': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/interventions': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
