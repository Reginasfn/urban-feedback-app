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
      {
        hintContent: 'Вы здесь'
      },
      {
        preset: 'islands#greenCircleDotIcon'
      }
    )
  }

  const removeUserMarker = (mapInstance) => {
    if (userMarker.value && mapInstance?.geoObjects) {
      try {
        mapInstance.geoObjects.remove(userMarker.value)
      } catch (e) {
        // Игнорируем ошибки удаления
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

    if (loading.value) return
    loading.value = true
    error.value = null

    if (!ymaps || !mapInstance) {
      error.value = 'Карта или API не готовы'
      loading.value = false
      return null
    }

    currentMapInstance.value = mapInstance

    if (!navigator.geolocation) {
      error.value = 'Геолокация не поддерживается браузером'
      loading.value = false
      return null
    }

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude: lat, longitude: lon, accuracy } = position.coords
          const coords = [lat, lon]

          userPosition.value = { lat, lon, accuracy }

          mapInstance.setCenter(coords, zoom, {
            flying: true,
            duration: 600
          })

          removeUserMarker(mapInstance)

          const markerCreator = createMarkerFn || createDefaultUserMarker
          const newMarker = markerCreator(coords, ymaps)
          
          if (newMarker) {
            userMarker.value = newMarker
            mapInstance.geoObjects.add(newMarker)
          }

          const accText = accuracy < 100 ? `±${Math.round(accuracy)}м` : 'приблизительно'
          success.value = `Вы находитесь здесь (точность: ${accText})`

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