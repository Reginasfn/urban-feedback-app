// frontend/src/services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 
    'Content-Type': 'application/json' 
  }
})

// Автоматически добавляем токен ко всем запросам
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Обработка ошибок (опционально)
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Токен истёк или неверный
      localStorage.removeItem('auth_token')
      // Можно добавить редирект на страницу входа
      // window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api