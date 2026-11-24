import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ command, isPreview }) => ({
  plugins: [react()],
  // Dev server only: forward /api to the local FastAPI backend. `vite preview`
  // and production hosting need their own API routing.
  server:
    command === 'serve' && !isPreview
      ? {
          proxy: {
            '/api': 'http://127.0.0.1:8000',
          },
        }
      : undefined,
}))
