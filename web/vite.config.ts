import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, // Expose to Docker network
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://api:8000', // Docker internal DNS
        changeOrigin: true,
      }
    },
    watch: {
      usePolling: true, // Bulletproof HMR inside Docker volumes
    }
  }
})