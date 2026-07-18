import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // In local dev, the frontend (port 5173) and backend (port 8000) run as
  // separate processes. This proxy forwards any request starting with
  // /api straight to FastAPI, so the frontend code can always just call
  // fetch('/api/...') — no hardcoded localhost:8000, and no CORS headaches.
  //
  // In production (single-container deploy), FastAPI serves the built
  // frontend itself, so /api/* requests are same-origin anyway and this
  // proxy block is simply unused — no changes needed between environments.
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
