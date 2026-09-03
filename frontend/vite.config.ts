import react from '@vitejs/plugin-react'
import path from 'node:path'
import { defineConfig, loadEnv } from 'vite'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const rootEnv = loadEnv(mode, path.resolve(import.meta.dirname, '..'), '')

  return {
    plugins: [react(), tailwindcss()],
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          configure: (proxy) => {
            proxy.on('proxyReq', (request) => {
              if (rootEnv.ADMIN_API_KEY) {
                request.setHeader('X-API-Key', rootEnv.ADMIN_API_KEY)
              }
            })
          },
        },
      },
    },
  }
})
