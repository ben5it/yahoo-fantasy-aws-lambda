import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/login': {
        target: 'http://localhost:3001',
        changeOrigin: true
      },
      '/check_auth': {
        target: 'http://localhost:3001',
        changeOrigin: true
      },
      '/api/leagues': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  }
})