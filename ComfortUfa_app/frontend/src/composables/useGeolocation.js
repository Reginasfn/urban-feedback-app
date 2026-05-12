// src/composables/useGeolocation.js
import { ref, shallowRef } from 'vue'

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
      timeout = 15000,
      maximumAge = 0,
      onPositionReceived = null,
      ymaps = null,
      mapInstance = null,
      createMarkerFn = null,
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
      error.value = 'Геолокация не поддерживается браузером'
      loading.value = false
      console.error('[Geo] Геолокация не поддерживается')
      return null
    }

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
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
            console.log('[GeoMarker] Маркер добавлен на карту, geoObjects count:', mapInstance.geoObjects.getLength())
          } else {
            console.error('[GeoMarker] Не удалось создать маркер')
          }

          const accText = accuracy < 100 ? `±${Math.round(accuracy)}м` : 'приблизительно'
          success.value = `Вы находитесь здесь (точность: ${accText})`
          console.log('[Geo] Успех:', success.value)

          if (typeof onPositionReceived === 'function') {
            onPositionReceived({ coords, accuracy })
          }

          loading.value = false
          resolve({ coords, accuracy })
        },
        (err) => {
          const errors = {
            1: 'Доступ запрещён',
            2: 'Позиция недоступна',
            3: 'Тайм-аут запроса'
          }
          error.value = `Геолокация: ${errors[err.code] || 'Ошибка'}`
          console.error('[Geo] Ошибка геолокации:', error.value, err)
          loading.value = false
          resolve(null)
        },
        { enableHighAccuracy, timeout, maximumAge }
      )
    })
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