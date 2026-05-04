import api from '@/services/api'

const DEFAULT_TTL = 5 * 60 * 1000 // 5 минут

export function useRatingsCache(ttl = DEFAULT_TTL) {
  const cache = new Map()

  const isExpired = (entry) => !entry || Date.now() >= entry.expiresAt

  const get = (objectId) => {
    const entry = cache.get(objectId)
    if (isExpired(entry)) {
      cache.delete(objectId)
      return null
    }
    return entry.data
  }

  const set = (objectId, data) => {
    cache.set(objectId, { data, expiresAt: Date.now() + ttl })
  }

  const invalidate = (objectId) => cache.delete(objectId)
  const clear = () => cache.clear()

  const fetch = async (objectId) => {
    const cached = get(objectId)
    if (cached !== null) return cached

    try {
      const response = await api.get(`/reviews/object/${objectId}`, {
        params: { limit: 100 }
      })
      
      // Гибкая обработка ответа сервера
      let reviews = []
      if (Array.isArray(response.data)) {
        reviews = response.data
      } else if (response.data?.reviews && Array.isArray(response.data.reviews)) {
        reviews = response.data.reviews
      } else if (response.data?.data && Array.isArray(response.data.data)) {
        reviews = response.data.data
      } else {
        reviews = []
      }

      const result = reviews.length === 0
        ? { avg: null, count: 0 }
        : {
            avg: parseFloat((reviews.reduce((sum, r) => sum + (r.rating || 0), 0) / reviews.length).toFixed(1)),
            count: reviews.length
          }

      set(objectId, result)
      return result
    } catch (err) {
      console.error(`[RatingsCache] Error for object ${objectId}:`, err)
      return { avg: null, count: 0 }
    }
  }

  return { get, set, invalidate, clear, fetch }
}