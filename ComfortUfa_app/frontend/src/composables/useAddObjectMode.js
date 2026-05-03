import { ref, watch } from 'vue'
import axios from 'axios'

export function useAddObjectMode(
  mapRef,
  mapContainerRef,
  setError,
  setSuccess,
  createPlacemarkFn,
  apiPost
) {
  const isAddingMode = ref(false)
  const showAddConfirm = ref(false)
  const showObjectModal = ref(false)
  const pendingObjectCoords = ref(null)
  const pendingAddress = ref(null)
  const confirmPosition = ref({ top: '0px', left: '0px' })
  const isGeocoding = ref(false)

  const getAddressFromCoords = async (coords, apiKey) => {
    if (!coords || !Array.isArray(coords) || coords.length !== 2) {
      return null
    }

    if (!apiKey) {
      return null
    }

    isGeocoding.value = true
    try {
      const [lat, lon] = coords
      const { data } = await axios.get(
        'https://geocode-maps.yandex.ru/1.x/',
        {
          params: {
            apikey: apiKey,
            geocode: `${lon},${lat}`,
            results: 1,
            lang: 'ru_RU',
            format: 'json'
          }
        }
      )

      const geoObjects = data.response?.GeoObjectCollection?.featureMember || []
      return geoObjects[0]?.GeoObject?.metaDataProperty?.GeocoderMetaData?.text || null
    } catch (err) {
      console.error('[Geocoding] Ошибка:', err)
      return null
    } finally {
      isGeocoding.value = false
    }
  }

  const calculateConfirmPosition = (event) => {
    const containerRect = mapContainerRef.value?.getBoundingClientRect()
    if (!containerRect || !event) {
      return { top: '50%', left: '50%' }
    }

    const position = event.get?.('position')
    if (!position) {
      return { top: '50%', left: '50%' }
    }

    return {
      top: `${position[1] + 10}px`,
      left: `${position[0] + 10}px`
    }
  }

  const handleMapClick = async (event, yandexApiKey) => {
    if (!isAddingMode.value || !mapRef.value) {
      return false
    }

    const coords = event.get?.('coords')
    if (!coords || !Array.isArray(coords)) {
      setError('Не удалось определить координаты')
      return false
    }

    event.stopPropagation?.()
    event.preventDefault?.()

    pendingObjectCoords.value = coords
    confirmPosition.value = calculateConfirmPosition(event)

    if (yandexApiKey) {
      const address = await getAddressFromCoords(coords, yandexApiKey)
      if (address) {
        pendingAddress.value = address
        setSuccess(`Адрес: ${address}`, 4000)
      }
    }

    showAddConfirm.value = true
    return true
  }

  const toggleAddMode = (isAuthenticated) => {
    if (!isAuthenticated) {
      setError('Необходимо авторизоваться, чтобы добавлять объекты')
      return
    }

    isAddingMode.value = !isAddingMode.value
    
    if (!isAddingMode.value) {
      cancelAddObject()
    }

    updateMapBehavior()
  }

  const updateMapBehavior = () => {
    const map = mapRef.value
    if (!map) return

    if (isAddingMode.value) {
      map.behaviors.disable('drag')
      map.behaviors.disable('scrollZoom')
      if (mapContainerRef.value) {
        mapContainerRef.value.style.cursor = 'crosshair'
      }
    } else {
      map.behaviors.enable('drag')
      map.behaviors.enable('scrollZoom')
      if (mapContainerRef.value) {
        mapContainerRef.value.style.cursor = 'grab'
      }
    }
  }

  const cancelAddObject = () => {
    showAddConfirm.value = false
    pendingObjectCoords.value = null
    pendingAddress.value = null
  }

  const confirmAddObject = async (yandexApiKey) => {
    if (!pendingObjectCoords.value) {
      setError('Координаты не определены')
      return
    }

    showAddConfirm.value = false

    if (!pendingAddress.value && yandexApiKey) {
      const address = await getAddressFromCoords(pendingObjectCoords.value, yandexApiKey)
      if (address) {
        pendingAddress.value = address
      }
    }

    showObjectModal.value = true
  }

    const submitNewObject = async (payload) => {
    console.log('[AddObject] Отправка данных:', {
        ...payload,
        coords: pendingObjectCoords.value,
        address: pendingAddress.value || payload.address
    })

    if (!pendingObjectCoords.value) {
        throw new Error('Координаты объекта не определены')
    }

    const fullPayload = {
        ...payload,
        coords: pendingObjectCoords.value,
        address: pendingAddress.value || payload.address
    }

    try {
        console.log('[AddObject] Отправка POST запроса на /api/objects')
        const response = await apiPost('/api/objects', fullPayload)
        
        console.log('[AddObject] Ответ сервера:', response.data)
        
        // Добавляем маркер на карту
        if (createPlacemarkFn && mapRef.value) {
        const newPlacemark = createPlacemarkFn({
            ...fullPayload,
            id_object: response.data?.id_object || `temp_${Date.now()}`,
            type: payload.type || payload.type_name
        })
        
        // Правильный способ добавления на карту с Яндекс.Картами
        try {
            // Пробуем добавить в кластеризатор
            const allObjects = mapRef.value.geoObjects
            if (allObjects) {
            // Ищем кластеризатор среди объектов карты
            let foundClusterer = null
            
            allObjects.each(function(obj) {
                if (obj.constructor.name === 'Clusterer' || 
                    obj.constructor.name === 'Clusterer#active' ||
                    (obj.options && obj.options.get && obj.options.get('preset')?.includes('Cluster'))) {
                foundClusterer = obj
                }
            })
            
            if (foundClusterer) {
                console.log('[AddObject] Найден кластеризатор, добавляем в него')
                foundClusterer.add(newPlacemark)
            } else {
                console.log('[AddObject] Кластеризатор не найден, добавляем на карту')
                mapRef.value.geoObjects.add(newPlacemark)
            }
            }
        } catch (err) {
            console.error('[AddObject] Ошибка добавления на карту:', err)
            // Фолбэк: просто добавляем на карту
            mapRef.value.geoObjects.add(newPlacemark)
        }
        }

        return { success: true, data: response.data }
    } catch (err) {
        console.error('[AddObject] Ошибка сохранения:', err)
        console.error('[AddObject] Ответ сервера:', err.response?.data)
        throw err
    }
    }

  const resetAfterSubmit = () => {
    showObjectModal.value = false
    pendingObjectCoords.value = null
    pendingAddress.value = null
  }

  const cleanup = () => {
    isAddingMode.value = false
    cancelAddObject()
    showObjectModal.value = false
    if (mapRef.value) {
      updateMapBehavior()
    }
  }

  watch(isAddingMode, () => {
    updateMapBehavior()
  })

  return {
    isAddingMode,
    showAddConfirm,
    showObjectModal,
    pendingObjectCoords,
    pendingAddress,
    confirmPosition,
    isGeocoding,
    toggleAddMode,
    handleMapClick,
    cancelAddObject,
    confirmAddObject,
    submitNewObject,
    resetAfterSubmit,
    cleanup,
    getAddressFromCoords,
    updateMapBehavior
  }
}