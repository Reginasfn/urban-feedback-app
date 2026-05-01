// src/composables/useMapLayers.js
import { ref } from 'vue'

export const MAP_LAYERS = [
  { id: 'map', title: 'Схема', icon: 'pi pi-hashtag', yandexType: 'yandex#map' },
  { id: 'satellite', title: 'Спутник', icon: 'pi pi-globe', yandexType: 'yandex#satellite' },
  { id: 'hybrid', title: 'Гибрид', icon: 'pi pi-map', yandexType: 'yandex#hybrid' }
]

export const DEFAULT_LAYER = 'map'

export function useMapLayers({ onSuccess, onError } = {}) {
  const currentLayer = ref(DEFAULT_LAYER)
  const isSwitching = ref(false)
  const lastSwitchTime = ref(0)
  const SWITCH_DEBOUNCE = 300

  const switchLayer = async (layerId, mapInstance) => {
    const now = Date.now()
    if (isSwitching.value || now - lastSwitchTime.value < SWITCH_DEBOUNCE) {
      return false
    }

    const layer = MAP_LAYERS.find(l => l.id === layerId)
    if (!layer) {
      onError?.(`Слой "${layerId}" не найден`)
      return false
    }

    if (currentLayer.value === layerId) return true

    isSwitching.value = true
    lastSwitchTime.value = now

    try {
      if (mapInstance && typeof mapInstance.setType === 'function') {
        mapInstance.setType(layer.yandexType)
      }

      currentLayer.value = layerId
      onSuccess?.(`Слой: ${layer.title}`)
      return true
    } catch (err) {
      console.error('[MapLayers] Ошибка:', err)
      onError?.(`Не удалось переключить слой: ${err.message}`)
      return false
    } finally {
      setTimeout(() => { isSwitching.value = false }, 200)
    }
  }

  const isLayerActive = (layerId) => currentLayer.value === layerId

  return {
    currentLayer,
    isSwitching,
    layers: MAP_LAYERS,
    switchLayer,
    isLayerActive
  }
}