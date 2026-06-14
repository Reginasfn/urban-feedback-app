// src/composables/useGeolocation.js
import { ref, shallowRef } from 'vue'

// 🔥 ФИКСИРОВАННЫЕ КООРДИНАТЫ (заглушка)
const FALLBACK_COORDS = [54.728259, 55.969300] // Уфа, центр
const FALLBACK_ADDRESS = 'г. Уфа, Кирова 65'

export function useGeolocation() {
  const loading = ref(false)
  const error = ref(null)
  const success = ref(null)
  const userPosition = ref(null)
  const userMarker = shallowRef(null)
  const currentMapInstance = shallowRef(null)

  const createDefaultUserMarker = (coords, ymaps) => {
    if (!ymaps) {
      console.error('[GeoMarker] ymaps не определён')
      return null
    }

    return new ymaps.Placemark(
      coords,
      { hintContent: 'Вы здесь' },
      {
        preset: 'islands#greenCircleDotIcon',
        zIndex: 2000,
        isOurObject: true
      }
    )
  }

  const removeUserMarker = (mapInstance) => {
    if (userMarker.value && mapInstance?.geoObjects) {
      try {
        mapInstance.geoObjects.remove(userMarker.value)
        console.log('[GeoMarker] Маркер удалён')
      } catch (e) {
        console.warn('[GeoMarker] Ошибка удаления:', e)
      }
      userMarker.value = null
    }
  }

  const goToMyLocation = async (options = {}) => {
    const {
      zoom = 18,
      enableHighAccuracy = true,
      timeout = 10000, // 🔥 Уменьшили таймаут до 10 сек
      maximumAge = 0,
      onPositionReceived = null,
      ymaps = null,
      mapInstance = null,
      createMarkerFn = null,
      useFallback = true, // 🔥 Использовать заглушку если не получилось
    } = options

    if (loading.value) {
      console.log('[Geo] Уже выполняется запрос геолокации')
      return
    }
    
    loading.value = true
    error.value = null
    console.log('[Geo] Запрос геолокации...')

    if (!ymaps || !mapInstance) {
      error.value = 'Карта или API не готовы'
      loading.value = false
      console.error('[Geo] Ошибка: карта или ymaps не готовы')
      return null
    }

    currentMapInstance.value = mapInstance

    if (!navigator.geolocation) {
      console.warn('[Geo] Геолокация не поддерживается браузером')
      if (useFallback) {
        return await useFallbackCoords({ zoom, mapInstance, ymaps, createMarkerFn })
      }
      error.value = 'Геолокация не поддерживается браузером'
      loading.value = false
      return null
    }

    // 🔥 Пробуем получить реальную геолокацию
    return new Promise((resolve) => {
      const timeoutId = setTimeout(() => {
        console.warn('[Geo] Тайм-аут геолокации, используем заглушку')
        if (useFallback) {
          useFallbackCoords({ zoom, mapInstance, ymaps, createMarkerFn }).then(resolve)
        } else {
          error.value = 'Превышено время ожидания'
          loading.value = false
          resolve(null)
        }
      }, timeout)

      navigator.geolocation.getCurrentPosition(
        (position) => {
          clearTimeout(timeoutId)
          console.log('[Geo] Позиция получена:', position.coords)
          const { latitude: lat, longitude: lon, accuracy } = position.coords
          const coords = [lat, lon]

          userPosition.value = { lat, lon, accuracy }

          // Плавное перемещение карты
          mapInstance.setCenter(coords, zoom, {
            flying: true,
            duration: 600
          })

          // Удаляем старый маркер перед созданием нового
          removeUserMarker(mapInstance)

          // Создаём маркер
          const markerCreator = createMarkerFn || createDefaultUserMarker
          const newMarker = markerCreator(coords, ymaps)
          
          if (newMarker) {
            userMarker.value = newMarker
            mapInstance.geoObjects.add(newMarker)
            console.log('[GeoMarker] Маркер добавлен на карту')
          }

          const accText = accuracy < 100 ? `±${Math.round(accuracy)}м` : 'приблизительно'
          success.value = `Вы находитесь здесь (точность: ${accText})`
          console.log('[Geo] Успех:', success.value)

          if (typeof onPositionReceived === 'function') {
            onPositionReceived({ coords, accuracy })
          }

          loading.value = false
          resolve({ coords, accuracy, isFallback: false })
        },
        async (err) => {
          clearTimeout(timeoutId)
          const errors = {
            1: 'Доступ запрещён',
            2: 'Позиция недоступна',
            3: 'Тайм-аут запроса'
          }
          
          console.warn('[Geo] Ошибка геолокации:', errors[err.code])
          
          // 🔥 Если не получилось и включена заглушка
          if (useFallback) {
            console.log('[Geo] Используем фиксированные координаты')
            const result = await useFallbackCoords({ zoom, mapInstance, ymaps, createMarkerFn })
            resolve(result)
          } else {
            error.value = `Геолокация: ${errors[err.code] || 'Ошибка'}`
            loading.value = false
            resolve(null)
          }
        },
        { enableHighAccuracy, timeout: 20000, maximumAge } // 🔥 Увеличили таймаут для браузера
      )
    })
  }

  // 🔥 Функция использования заглушки
  const useFallbackCoords = async ({ zoom, mapInstance, ymaps, createMarkerFn }) => {
    console.log('[Geo] 🔧 Используем заглушку:', FALLBACK_COORDS)
    
    userPosition.value = { 
      lat: FALLBACK_COORDS[0], 
      lon: FALLBACK_COORDS[1], 
      accuracy: null 
    }

    // Перемещаем карту
    mapInstance.setCenter(FALLBACK_COORDS, zoom, {
      flying: true,
      duration: 600
    })

    // Удаляем старый маркер
    removeUserMarker(mapInstance)

    // Создаём маркер
    const markerCreator = createMarkerFn || createDefaultUserMarker
    const newMarker = markerCreator(FALLBACK_COORDS, ymaps)
    
    if (newMarker) {
      userMarker.value = newMarker
      mapInstance.geoObjects.add(newMarker)
      console.log('[GeoMarker] Маркер-заглушка добавлен')
    }

    success.value = `Примерное местоположение: ${FALLBACK_ADDRESS}`
    console.log('[Geo] Заглушка активирована')

    loading.value = false
    
    return { 
      coords: FALLBACK_COORDS, 
      accuracy: null, 
      isFallback: true 
    }
  }

  const clearMessages = () => {
    error.value = null
    success.value = null
  }

  const destroy = () => {
    console.log('[Geo] Уничтожение геолокации')
    removeUserMarker(currentMapInstance.value)
    clearMessages()
    currentMapInstance.value = null
  }

  return {
    loading,
    error,
    success,
    userPosition,
    userMarker,
    goToMyLocation,
    removeUserMarker,
    destroy,
    createDefaultUserMarker
  }
}