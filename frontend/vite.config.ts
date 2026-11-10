import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 4173,
    strictPort: true,
    proxy: {
      '/api/assistant/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/health/',
      },
      '/api/assistant': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/assistant/, '/v1'),
      },
      '/api/v1/health': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        rewrite: () => '/health',
      },
      '/api/v1': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
})
