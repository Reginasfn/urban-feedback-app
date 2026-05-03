// composables/useRatingsCache.js
import api from '@/services/api'

const DEFAULT_TTL = 5 * 60 * 1000 // 5 минут

export function useRatingsCache(ttl = DEFAULT_TTL) {
  // Используем обычный Map (без ref), так как кэш не должен триггерить реактивные обновления UI
  const cache = new Map()

  const isExpired = (entry) => !entry || Date.now() >= entry.expiresAt

  const get = (objectId) => {
    const entry = cache.get(objectId)
    if (isExpired(entry)) {
      cache.delete(objectId) // Ленивая очистка при чтении
      return null
    }
    return entry.data
  }

  const set = (objectId, data) => {
    cache.set(objectId, {
      data,
      expiresAt: Date.now() + ttl
    })
  }

  const invalidate = (objectId) => cache.delete(objectId)
  const clear = () => cache.clear()

  const fetch = async (objectId) => {
    // 1. Отдаём из кэша, если запись жива
    const cached = get(objectId)
    if (cached !== null) return cached

    // 2. Загружаем с сервера
    try {
      const response = await api.get(`/reviews/object/${objectId}`, {
        params: { limit: 100 }
      })
      const reviews = response.data.reviews || []

      const result = reviews.length === 0
        ? { avg: null, count: 0 }
        : {
            avg: parseFloat((reviews.reduce((sum, r) => sum + (r.rating || 0), 0) / reviews.length).toFixed(1)),
            count: reviews.length
          }

      // 3. Сохраняем с TTL
      set(objectId, result)
      return result
    } catch (err) {
      console.error(`[RatingsCache] Ошибка для объекта ${objectId}:`, err)
      return { avg: null, count: 0 }
    }
  }

  return {
    get,
    set,
    invalidate,
    clear,
    fetch
  }
}