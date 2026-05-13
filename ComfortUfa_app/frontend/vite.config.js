// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],

  envDir: '../..', 
  
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  
  // 🔥 ДОБАВЬ ЭТУ СЕКЦИЮ:
  server: {
    port: 5173, // порт, на котором работает фронтенд
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // ⚠️ ПОРТ ТВОЕГО FASTAPI БЭКЕНДА!
        changeOrigin: true,
        secure: false,
        // Если бэкенд не ожидает префикс /api — раскомментируй:
        // rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})