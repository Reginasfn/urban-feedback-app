// frontend/src/services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 
    'Content-Type': 'application/json' 
  },
  timeout: 15000,
  withCredentials: false 
})

// Автоматически добавляем токен ко всем запросам
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Обработка ошибок
api.interceptors.response.use(
  response => response,
  error => {
    // 401 — токен истёк
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      sessionStorage.removeItem('auth_token')
    }
    
    if (!error.response) {
      console.error('[API] Network error:', error.message)
    }
    
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      console.error('[API] Request timeout')
    }
    
    return Promise.reject(error)
  }
)

export default api