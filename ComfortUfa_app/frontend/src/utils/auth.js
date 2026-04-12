// utils/auth.js

/**
 * Проверяет, авторизован ли пользователь
 * @returns {boolean}
 */
export const isAuthenticated = () => {
  const token = localStorage.getItem('auth_token')
  if (!token) return false
  
  // 👇 Опционально: проверка срока действия JWT
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const now = Date.now() / 1000
    if (payload.exp && payload.exp < now) {
      // Токен истёк — удаляем
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      return false
    }
    return true
  } catch {
    // Если токен не валидный — удаляем
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    return false
  }
}

/**
 * Получает данные текущего пользователя
 * @returns {Object|null}
 */
export const getCurrentUser = () => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

/**
 * Выход из системы
 */
export const logout = () => {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user')
  // 👇 Сообщаем всем компонентам об изменении статуса
  window.dispatchEvent(new CustomEvent('auth-change', { detail: { isAuthenticated: false } }))
}