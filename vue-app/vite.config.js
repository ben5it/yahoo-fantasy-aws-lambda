import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
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
      },
      '/api/getdata': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  }
})