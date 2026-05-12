<template>
  <div class="map-page">
    <!-- ===== ЛЕВЫЙ ПЛАВАЮЩИЙ САЙДБАР ===== -->
    <div class="sidebar">
      <!-- 🔍 Поиск по названию/адресу -->
      <div class="sidebar-section">
        <label class="sidebar-label">Поиск</label>
        <AutoComplete 
          v-model="searchQuery" 
          :suggestions="searchResults" 
          @complete="searchCategories"
          @item-select="onCategorySelect"
          @keydown="handleSearchKeydown"
          placeholder="Название или адрес..."
          class="w-full"
          :dropdown="true"
          optionLabel="label"
        >
          <template #item="{ item }">
            <div class="flex flex-col">
              <span class="font-semibold text-sm">{{ item.label }}</span>
              <span class="text-xs text-gray-500">{{ item.type }}</span>
            </div>
          </template>
        </AutoComplete>
      </div>

      <!-- Все категории -->
      <div class="sidebar-section categories-section">
        <label class="sidebar-label">Объекты</label>
        <div class="categories-list">

          <!-- 🔥 Кнопка "ВСЕ" -->
          <button 
            @click="loadObjects('all')"
            :class="{ active: selectedCategory === 'all' }"
            class="category-btn all-btn"
          >
            <i class="pi pi-th-large"></i>
            Все объекты
          </button>

          <button 
            v-for="cat in categories" 
            :key="cat" 
            @click="loadObjects(cat)"
            :class="{ active: selectedCategory === cat }"
            class="category-btn"
          >
            <i :class="getCategoryIcon(cat)"></i>
            {{ cat }}
          </button>
        </div>
      </div>

      <!-- ===== ФИЛЬТРЫ ===== -->
      <div class="sidebar-section filters-section">
        <div class="filters-header">
          <label class="sidebar-label" style="padding-left: 10px;">Фильтры</label>
          <button v-if="activeFilter" class="filters-clear" @click="clearFilters">
            <i class="pi pi-times"></i>
          </button>
        </div>
        
        <!-- Список фильтров со скроллом -->
        <div class="filters-list">
          <button 
            @click="toggleFilter('nearby')"
            :class="{ active: activeFilter === 'nearby' }"
            class="filter-chip"
            :disabled="!isFilterAvailable('nearby')"
            :title="getFilterTitle('nearby')"
          >
            <i class="pi pi-location"></i>
            <span>Рядом со мной (1 км)</span>
          </button>
          
          <!-- Избранное (только для авторизованных) -->
          <button 
            @click="toggleFilter('bookmarked')"
            :class="{ active: activeFilter === 'bookmarked' }"
            class="filter-chip"
            :disabled="!isFilterAvailable('bookmarked')"
            :title="getFilterTitle('bookmarked')"
          >
            <i class="pi pi-bookmark"></i>
            <span>Избранное</span>
            <i v-if="!isAuthenticated" class="pi pi-lock" style="margin-left: auto; font-size: 10px;"></i>
          </button>
          
          <!-- Мои объекты (только для авторизованных) -->
          <button 
            @click="toggleFilter('mine')"
            :class="{ active: activeFilter === 'mine' }"
            class="filter-chip"
            :disabled="!isFilterAvailable('mine')"
            :title="getFilterTitle('mine')"
          >
            <i class="pi pi-user"></i>
            <span>Мои объекты</span>
            <i v-if="!isAuthenticated" class="pi pi-lock" style="margin-left: auto; font-size: 10px;"></i>
          </button>
          
          <!-- Проблемные -->
          <button 
            @click="toggleFilter('problems')"
            :class="{ active: activeFilter === 'problems' }"
            class="filter-chip"
            :disabled="!isFilterAvailable('problems')"
            :title="getFilterTitle('problems')"
          >
            <i class="pi pi-exclamation-triangle"></i>
            <span>Проблемное</span>
          </button>
          
          <!-- Высокий рейтинг -->
          <button 
            @click="toggleFilter('high_rating')"
            :class="{ active: activeFilter === 'high_rating' }"
            class="filter-chip"
            :disabled="!isFilterAvailable('high_rating')"
            :title="getFilterTitle('high_rating')"
          >
            <i class="pi pi-star"></i>
            <span>С высоким рейтингом</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Информационная панель -->
    <div v-if="objectsCount > 0" class="info-panel">
      <i class="pi pi-map-marker"></i>
      <span>Объектов: <strong>{{ objectsCount }}</strong></span>
      <span v-if="selectedCategory" class="category-badge">{{ selectedCategory }}</span>
      <span v-if="activeFilter" class="filters-badge">+ {{ getFilterLabel(activeFilter) }}</span>
    </div>

    <!-- ===== ПРАВАЯ ПАНЕЛЬ ===== -->
    <div class="map-controls-right">
      <!-- Переключатель слоёв -->
      <div class="layer-switcher">
        <button 
          v-for="layer in availableLayers" 
          :key="layer.id"
          @click="handleLayerSwitch(layer.id)"
          :class="{ active: isLayerActive(layer.id), disabled: layerSwitching }"
          class="layer-btn"
          :title="layer.title"
          :disabled="layerSwitching"
        >
          <i :class="layer.icon"></i>
        </button>
      </div>

      <!-- Кнопка геолокации -->
      <button 
        class="geo-btn" 
        @click="goToMyLocation" 
        :disabled="loading"
        title="Моё местоположение"
      >
        <i class="pi pi-send"></i>
      </button>

      <!-- Кнопка добавления объекта -->
      <button 
        v-if="isAuthenticated"
        class="add-object-btn" 
        :class="{ active: isAddingMode }"
        @click="() => toggleAddMode(isAuthenticated)"
        :disabled="loading || isGeocoding"
        title="Добавить объект на карту"
      >
        <i class="pi" :class="isAddingMode ? 'pi-times' : 'pi-plus'"></i>
      </button>
    </div>

    <!-- Подсказка при добавлении -->
    <Transition name="fade-slide">
      <div v-if="isAddingMode" class="add-mode-hint">
        <i class="pi pi-map-marker"></i>
        <span>Нажмите на карту, чтобы добавить объект</span>
        <button class="hint-close" @click="toggleAddMode"><i class="pi pi-times"></i></button>
      </div>
    </Transition>

    <!-- Подтверждение добавления -->
    <Transition name="fade-slide">
      <div v-if="showAddConfirm" class="add-confirm-popup" :style="confirmPosition">
        <div class="confirm-content">
          <i class="pi pi-question-circle"></i>
          <span>Добавить объект сюда?</span>
          <div class="confirm-actions">
            <button class="confirm-btn cancel" @click="cancelAddObject">Нет</button>
            <button class="confirm-btn confirm" @click="confirmAddObject">Да</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Индикатор загрузки -->
    <Transition name="fade">
      <div v-if="loading || isGeocoding" class="loading-overlay">
        <i class="pi pi-spin pi-spinner spinner-icon"></i>
        <span>{{ isGeocoding ? 'Определяем адрес...' : 'Определяем местоположение...' }}</span>
      </div>
    </Transition>

    <!-- Сообщения -->
    <Transition name="fade-slide">
      <div v-if="error" class="error-overlay">
        <i class="pi pi-exclamation-triangle"></i>
        <span>{{ error }}</span>
        <button @click="error = null" class="close-btn"><i class="pi pi-times"></i></button>
      </div>
    </Transition>

    <Transition name="fade-slide">
      <div v-if="success" class="success-overlay">
        <i class="pi pi-check-circle"></i>
        <span>{{ success }}</span>
      </div>
    </Transition>

    <!-- Модальные окна -->
    <ReviewModal
      v-model:visible="showReviewModal"
      :selected-object="selectedObjectForReview"
      :review-categories="reviewCategories"
      :category-icons="categoryIcons"
      @submit="handleReviewSubmit"
      @cancel="handleReviewCancel"
      @error="handleReviewError"
    />

    <ObjectModal
      v-model:visible="showObjectModal"
      :coordinates="pendingObjectCoords"
      :available-types="objectTypeOptions"
      @submit="handleObjectSubmit"
      @cancel="handleObjectCancel"
      @error="handleObjectError"
    />

    <!-- Карта -->
    <div ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, toRef } from 'vue'
import AutoComplete from 'primevue/autocomplete'
import ReviewModal from '@/components/modals/ReviewModal.vue'
import ObjectModal from '@/components/modals/ObjectModal.vue'

import { useGeolocation } from '@/composables/useGeolocation'
import { useMapLayers } from '@/composables/useMapLayers'
import { useAutoClear } from '@/composables/useAutoClear'
import { useRatingsCache } from '@/composables/useRatingsCache'
import { useAddObjectMode } from '@/composables/useAddObjectMode'
import { useSearch } from '@/composables/useSearch'
import { useObjectLoad } from '@/composables/useObjectLoad'
import { useFilter } from '@/composables/useFilter'

import { createBalloonContent } from '@/utils/map/balloonRenderer'
import api from '@/services/api' 
import { isAuthenticated as checkAuth } from '@/utils/auth'

const YANDEX_API_KEY = import.meta.env.VITE_YANDEX_MAPS_KEY || ''
const { fetch: fetchRating, invalidate: invalidateRating, clear: clearRatingsCache } = useRatingsCache()

const mapContainer = ref(null)
const { value: error, set: setError } = useAutoClear(null, 3000)
const { value: success, set: setSuccess } = useAutoClear(null, 2500) 

const selectedCategory = ref(null)
const isMapInitialized = ref(false)
const isAuthenticated = ref(checkAuth())

const { loading: geoLoading, error: geoError, success: geoSuccess, goToMyLocation: performGeolocation, destroy: destroyGeolocation, removeUserMarker: clearUserMarker } = useGeolocation()

// ===== ИНИЦИАЛИЗАЦИЯ useFilter =====
const loadObjectsRef = ref(null)

const {
  activeFilter,
  userCoords,
  NEARBY_RADIUS,
  AUTH_FILTERS,
  isFilterAvailable,
  getFilterTitle,
  getFilterLabel,
  toggleFilter,
  clearFilters,
  applyFilters,
  updateUserCoords
} = useFilter({
  isAuthenticated: toRef(() => isAuthenticated.value),
  geoSuccess: toRef(() => geoSuccess.value),
  selectedCategory,
  loadObjectsRef,
  setError: (msg, duration) => setError(msg, duration),
  setSuccess: (msg, duration) => setSuccess(msg, duration),
  map: toRef(() => map)
})

const bookmarkedObjects = ref(new Set())
const showReviewModal = ref(false)
const selectedObjectForReview = ref(null)

const reviewCategories = [
  { value: 'praise', label: 'Похвала', icon: 'pi pi-thumbs-up' },
  { value: 'suggestion', label: 'Предложение', icon: 'pi pi-lightbulb' },
  { value: 'problem', label: 'Проблема', icon: 'pi pi-exclamation-circle' }
]

const objectTypeOptions = [
  { label: 'Камера видеонаблюдения', value: 'Камера видеонаблюдения' },
  { label: 'Кафе', value: 'Кафе' },
  { label: 'Фонарь', value: 'Фонарь' },
  { label: 'Скамейка', value: 'Скамейка' },
  { label: 'Парк', value: 'Парк' },
  { label: 'Беседка', value: 'Беседка' },
  { label: 'Остановка', value: 'Остановка' },
  { label: 'Детская площадка', value: 'Детская площадка' }
]

let map = null
let clusterer = null
let activePlacemark = null
let balloonTimeout = null
let removeTimeout = null
let searchTimeout = null
let boundsTimeout = null
let suppressBoundsReload = false

const UFA_CENTER = [54.7388, 55.9721]
const DEFAULT_ZOOM = 12

const categories = ['Камера видеонаблюдения', 'Кафе', 'Фонарь', 'Скамейка', 'Парк', 'Беседка', 'Остановка', 'Детская площадка']
const markerConfig = {
  "Кафе": { preset: 'islands#redFoodCircleIcon' },
  "Скамейка": { preset: 'islands#brownCircleIcon' },
  "Фонарь": { preset: 'islands#yellowInfoCircleIcon' },
  "Парк": { preset: 'islands#greenParkCircleIcon' },
  "Беседка": { preset: 'islands#brownLeisureCircleIcon' },
  "Остановка": { preset: 'islands#blueMassTransitCircleIcon' },
  "Детская площадка": { preset: 'islands#orangeFamilyCircleIcon' },
  "Камера видеонаблюдения": { preset: 'islands#blackVideoCircleIcon' }
}
const categoryIcons = {
  'Камера видеонаблюдения': 'pi pi-video', 'Кафе': 'pi pi-map-marker', 'Фонарь': 'pi pi-lightbulb',
  'Скамейка': 'pi pi-map-marker', 'Парк': 'pi pi-map-marker', 'Беседка': 'pi pi-building-columns',
  'Остановка': 'pi pi-car', 'Детская площадка': 'pi pi-face-smile'
}
const getCategoryIcon = (cat) => categoryIcons[cat] || 'pi pi-map-marker'

const { currentLayer: activeLayer, isSwitching: layerSwitching, layers: availableLayers, switchLayer: changeLayer, isLayerActive } = useMapLayers({ onSuccess: (msg) => setSuccess(msg, 1500), onError: (msg) => setError(msg, 3000) })
const handleLayerSwitch = async (layerId) => await changeLayer(layerId, map)

const createCustomUserMarker = (coords) => {
  // ✅ Правильный SVG с data: префиксом
  const svgString = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
    <ellipse cx="24" cy="44" rx="10" ry="3" fill="rgba(0,0,0,0.2)"/>
    <path d="M24 2C15.16 2 8 9.16 8 18c0 13.5 16 28 16 28s16-14.5 16-28c0-8.84-7.16-16-16-16z" 
          fill="#168f04" stroke="#ffffff" stroke-width="2.5"/>
    <path d="M18 24l4 4 8-8" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/>
  </svg>`
  
  try {
    console.log('[Marker] Создаём SVG-маркер...', coords)
    const marker = new window.ymaps.Placemark(
      coords, 
      { hintContent: 'Вы здесь' }, 
      { 
        // ✅ ВАЖНО: data:image/svg+xml, а не просто image/svg+xml
        iconLayout: 'default#image',
        iconImageHref: `data:image/svg+xml,${encodeURIComponent(svgString)}`,
        iconImageSize: [48, 48],
        iconImageOffset: [-24, -48],
        zIndex: 2000,
        isOurObject: true
      }
    )
    console.log('[Marker] SVG-маркер создан успешно:', marker)
    return marker
  } catch (e) {
    console.error('[Marker] Ошибка создания SVG-маркера:', e)
    // Фолбэк на стандартный маркер
    try {
      const fallback = new window.ymaps.Placemark(
        coords, 
        { hintContent: 'Вы здесь' }, 
        { 
          preset: 'islands#greenCircleDotIcon', 
          zIndex: 2000, 
          isOurObject: true 
        }
      )
      console.log('[Marker] Использован фолбэк-маркер')
      return fallback
    } catch (e2) {
      console.error('[Marker] Ошибка даже фолбэка:', e2)
      return null
    }
  }
}

const syncGeoState = () => {
  if (geoError.value) { setError(geoError.value, 3000); geoError.value = null; loading.value = false }
  if (geoSuccess.value) { setSuccess(geoSuccess.value, 3000); geoSuccess.value = null; loading.value = false }
}

const goToMyLocation = async () => {
  if (!map) { setError('Карта ещё не инициализирована'); return }

  loading.value = true

  suppressBoundsReload = true
  setTimeout(() => { suppressBoundsReload = false }, 2000)

  try {
    // ✅ Получаем результат с координатами из performGeolocation
    const result = await performGeolocation({ 
      zoom: 18, 
      ymaps: window.ymaps, 
      mapInstance: map, 
      createMarkerFn: createCustomUserMarker, 
      onPositionReceived: ({ coords }) => {
        console.log(`[Geo] Позиция получена:`, coords)
      } 
    })

    syncGeoState()
    
    // ✅ Обновляем координаты для фильтра "Рядом", если есть результат
    if (activeFilter.value === 'nearby' && result?.coords) {
      console.log('[Filter] Updating userCoords for nearby:', result.coords)
      updateUserCoords(result.coords)
    }

  } catch (err) {
    console.error('[goToMyLocation] Error:', err)
    setError('Не удалось определить местоположение')
  
  } finally { 
    loading.value = false 
  }
}

const navigateToObject = async (obj) => {
  if (!map || !obj.coords) {
    setError('Не удалось перейти к объекту')
    return
  }

  clearTimeout(balloonTimeout)
  clearTimeout(removeTimeout)
  clearTimeout(boundsTimeout)

  if (activePlacemark && map.geoObjects) {
    map.geoObjects.remove(activePlacemark)
    activePlacemark = null
  }

  try {
    suppressBoundsReload = true

    await map.panTo(obj.coords, {
      flying: true,
      duration: 1200
    })

    await map.setZoom(16, {
      duration: 400
    })

    const placemark = new window.ymaps.Placemark(
      obj.coords,
      {
        balloonContent: createBalloonContent(
          { ...obj, rating: 'loading', ratingCount: 0 },
          0,
          obj.type_name,
          {
            isBookmarked: bookmarkedObjects.value.has(Number(obj.id_object)),
            iconClass: getCategoryIcon(obj.type_name)
          }
        ),
        hintContent: obj.name
      },
      {
        preset: markerConfig[obj.type_name]?.preset || 'islands#grayCircleIcon',
        isOurObject: true,
        zIndex: 10000
      }
    )

    activePlacemark = placemark
    map.geoObjects.add(placemark)

    await new Promise((resolve) => {
      setTimeout(() => {
        placemark.balloon.open()
        resolve()
      }, 200)
    })

    fetchRating(obj.id_object)
      .then((rating) => {
        if (!placemark.balloon || !placemark.balloon.isOpen()) return
        placemark.properties.set(
          'balloonContent',
          createBalloonContent(
            { ...obj, rating: rating.avg, ratingCount: rating.count },
            0,
            obj.type_name,
            {
              isBookmarked: bookmarkedObjects.value.has(Number(obj.id_object)),
              iconClass: getCategoryIcon(obj.type_name)
            }
          )
        )
        setTimeout(() => {
          if (placemark.balloon) placemark.balloon.open()
        }, 50)
      })
      .catch(() => {
        if (!placemark.balloon || !placemark.balloon.isOpen()) return
        placemark.properties.set(
          'balloonContent',
          createBalloonContent(
            { ...obj, rating: null, ratingCount: 0 },
            0,
            obj.type_name,
            {
              isBookmarked: bookmarkedObjects.value.has(Number(obj.id_object)),
              iconClass: getCategoryIcon(obj.type_name)
            }
          )
        )
        setTimeout(() => {
          if (placemark.balloon) placemark.balloon.open()
        }, 50)
      })

    placemark.events.add('balloonclose', () => {
      if (map?.geoObjects && activePlacemark === placemark) {
        map.geoObjects.remove(placemark)
        activePlacemark = null
      }
    })

    setSuccess(`Найден: ${obj.name || 'Объект'}`)
  } catch (err) {
    console.error('[navigateToObject]', err)
    setError('Ошибка при переходе к объекту')
  } finally {
    setTimeout(() => { suppressBoundsReload = false }, 2500)
  }
}

const {
  searchQuery,
  searchResults,
  searchCategories,
  handleSearchKeydown,
  onCategorySelect
} = useSearch({
  api,
  navigateToObject,
  setError
})

const initMap = () => new Promise((resolve, reject) => {
  if (!mapContainer.value) { reject(new Error('Контейнер карты не найден')); return }
  const setupMap = () => createMapInstance().then(resolve).catch(reject)
  if (window.ymaps) window.ymaps.ready(setupMap)
  else {
    const script = document.createElement('script')
    script.src = `https://api-maps.yandex.ru/2.1/?apikey=${YANDEX_API_KEY}&lang=ru_RU`
    script.async = true
    script.onload = () => window.ymaps?.ready(setupMap)
    document.head.appendChild(script)
  }
})

const createMapInstance = () => new Promise((resolve, reject) => {
  if (!window.ymaps) { reject(new Error('ymaps не определён')); return }
  window.ymaps.ready(() => {
    try {
      map = new window.ymaps.Map(mapContainer.value, { center: UFA_CENTER, zoom: DEFAULT_ZOOM, controls: [] })
      map.controls.add(new window.ymaps.control.ZoomControl({ options: { size: 'large', float: 'none', position: { top: '110px', right: '25px' } } }))
      map.options.set('balloonEnabled', false)
      map.options.set('hintEnabled', false)
      map.behaviors.disable('dblClickZoom')
      
      map.events.add('click', (e) => {
        if (isAddingMode.value) { handleMapClick(e, YANDEX_API_KEY); return }
        const target = e.get('target')
        if (!target?.options?.get('isOurObject') && target !== clusterer) e.preventDefault()
      })
      
      map.events.add('balloonopen', (e) => {
        const target = e.get('target')
        if (!target?.options?.get('isOurObject')) { map.balloon.close(); e.preventDefault() }
      })
      
      map.events.add('actionend', () => {
        if (suppressBoundsReload) return
        if (boundsTimeout) clearTimeout(boundsTimeout)
        boundsTimeout = setTimeout(() => {
          if (selectedCategory.value) loadObjects(selectedCategory.value)
        }, 300)
      })

      clusterer = new window.ymaps.Clusterer({
        preset: 'islands#invertedDarkGreenClusterIcons',
        clusterDisableClickZoom: false,
        clusterOpenBalloonOnClick: true,
        clusterHasBalloon: true,
        gridSize: 80
      })
      map.geoObjects.add(clusterer)
      isMapInitialized.value = true
      resolve()
    } catch (err) { reject(err) }
  })
})

const fetchWithTimeout = async (promise, timeoutMs = 10000, errorMsg = 'Запрос превысил время ожидания') => {
  const timeout = new Promise((_, reject) => setTimeout(() => reject(new Error(errorMsg)), timeoutMs))
  return Promise.race([promise, timeout])
}

const getMapBbox = () => {
  if (!map) return null
  try {
    const bounds = map.getBounds()
    if (!bounds || !bounds[0] || !bounds[1]) return null
    const [minLat, minLon] = bounds[0]
    const [maxLat, maxLon] = bounds[1]
    return `${minLon},${minLat},${maxLon},${maxLat}`
  } catch (e) {
    console.error('[BBox] Error getting bounds:', e)
    return null
  }
}

// 🔥 ИСПРАВЛЕННЫЙ __toggleBookmark - ВСЕ ID как числа!
window.__toggleBookmark = async (objectId, btnElement) => {
  // 🔥 Конвертируем в число СРАЗУ!
  const numericId = Number(objectId)
  
  if (!isAuthenticated.value) { 
    setError('Пожалуйста, авторизуйтесь, чтобы добавлять в избранное')
    return 
  }
  
  const wasBookmarked = bookmarkedObjects.value.has(numericId)
  
  try {
    if (wasBookmarked) {
      await api.delete(`/api/objects/${numericId}/favorite`)
      bookmarkedObjects.value.delete(numericId)
      
      if (btnElement) { 
        btnElement.classList.remove('active')
        btnElement.querySelector('i').className = 'pi pi-bookmark'
        btnElement.title = 'Добавить в избранное' 
      }
      setSuccess('Убрано из избранного')
    } else {
      await api.post(`/api/objects/${numericId}/favorite`)
      bookmarkedObjects.value.add(numericId)
      
      if (btnElement) { 
        btnElement.classList.add('active')
        btnElement.querySelector('i').className = 'pi pi-bookmark-fill'
        btnElement.title = 'Убрать из избранного' 
      }
      setSuccess('Добавлено в избранное')
    }
    
    // 🔥 Обновляем ВСЕ placemark этого объекта
    const updatePlacemarkBookmark = (placemark) => {
      const pid = placemark.options?.get('objectId')
      // 🔥 Сравниваем как числа!
      if (Number(pid) !== numericId) return
      
      const objectData = placemark.__objectData
      if (!objectData) return
      
      const objectType = placemark.options.get('objectType')
      const objectIndex = placemark.__objectIndex || 0
      
      // 🔥 Генерируем контент с АКТУАЛЬНЫМ isBookmarked (число!)
      const updatedContent = createBalloonContent(
        objectData,
        objectIndex,
        objectType,
        {
          isBookmarked: bookmarkedObjects.value.has(numericId),
          iconClass: getCategoryIcon(objectType)
        }
      )
      
      placemark.properties.set('balloonContent', updatedContent)
      
      if (placemark.balloon?.isOpen()) {
        const balloonData = placemark.balloon.getData()
        if (balloonData?.properties) {
          balloonData.properties.set('balloonContent', updatedContent)
        }
      }
    }
    
    if (clusterer?.getGeoObjects) {
      clusterer.getGeoObjects().forEach(updatePlacemarkBookmark)
    }
    if (activePlacemark && Number(activePlacemark.options?.get('objectId')) === numericId) {
      updatePlacemarkBookmark(activePlacemark)
    }
    
    if (activeFilter.value === 'bookmarked' && selectedCategory.value) {
      applyFilters()
    }
    
  } catch (err) {
    console.error('[Bookmark] Error:', err)
    setError(err.response?.data?.detail || 'Не удалось изменить избранное')
    // Откат при ошибке
    if (wasBookmarked) {
      bookmarkedObjects.value.add(numericId)
    } else {
      bookmarkedObjects.value.delete(numericId)
    }
  }
}

window.__openReview = (objectId, objectName, objectType) => {
  if (!isAuthenticated.value) { setError('Необходимо авторизоваться'); return }
  selectedObjectForReview.value = { id: parseInt(objectId), name: objectName, type: objectType }
  showReviewModal.value = true
}

const handleReviewSubmit = async (payload) => {
  try {
    const formData = new FormData()
    formData.append('id_object', payload.id_object)
    formData.append('text', payload.text)
    formData.append('rating', payload.rating)
    formData.append('category', payload.category)
    if (payload.photo) formData.append('photo', payload.photo)
    await api.post('/reviews/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    invalidateRating(payload.id_object)
    if (selectedCategory.value) await loadObjects(selectedCategory.value)
    setSuccess('Отзыв успешно добавлен!')
  } catch (err) { setError(err.response?.data?.detail || err.message || 'Не удалось отправить отзыв') }
  showReviewModal.value = false
}

const handleReviewError = ({ message }) => setError(message)
const handleReviewCancel = () => {}

const createNewObjectPlacemark = (obj) => new window.ymaps.Placemark(obj.coords, { balloonContent: createBalloonContent({ ...obj, rating: null, ratingCount: 0 }, 0, obj.type, { isBookmarked: bookmarkedObjects.value.has(Number(obj.id_object)), iconClass: getCategoryIcon(obj.type) }), hintContent: obj.name }, { preset: markerConfig[obj.type]?.preset || 'islands#grayCircleIcon', isOurObject: true, zIndex: 100 })

const { isAddingMode, showAddConfirm, showObjectModal, pendingObjectCoords, pendingAddress, confirmPosition, isGeocoding, toggleAddMode, handleMapClick, cancelAddObject, confirmAddObject, submitNewObject, resetAfterSubmit, cleanup: cleanupAddMode } = useAddObjectMode(toRef(() => map), mapContainer, (msg, duration) => setError(msg, duration), (msg, duration) => setSuccess(msg, duration), createNewObjectPlacemark, (endpoint, data) => api.post(endpoint, data))

const handleObjectSubmit = async (payload) => {
  loading.value = true
  try {
    await submitNewObject(payload)
    cleanupAddMode()
    setSuccess(`Объект "${payload.name}" добавлен!`)
    const newObjectType = payload.type || payload.type_name
    selectedCategory.value = newObjectType
    await loadObjects(newObjectType)
  } catch (err) {
    console.error('[ObjectSubmit] Ошибка:', err)
    if (err.message !== 'duplicate_object') setError('Не удалось добавить объект.')
  } finally { loading.value = false }
}

const handleObjectCancel = () => cancelAddObject()
const handleObjectError = ({ message }) => setError(message)

onMounted(async () => {
  // 🔥 Загрузка избранного с конвертацией ID в числа
  const loadUserFavorites = async () => {
    if (!isAuthenticated.value) return
    try {
      const response = await api.get('/api/objects/me/favorites/ids')
      // 🔥 Конвертируем ВСЕ ID в числа!
      const favoriteIds = (response.data.favorite_ids || []).map(id => Number(id))
      bookmarkedObjects.value = new Set(favoriteIds)
      console.log('[Favorites] Loaded as NUMBERS:', Array.from(bookmarkedObjects.value))
    } catch (err) {
      console.error('[Favorites] Error loading:', err)
    }
  }

  const handleAuthChange = (event) => { 
    isAuthenticated.value = event.detail.isAuthenticated
    if (event.detail.isAuthenticated) {
      loadUserFavorites()
    } else {
      bookmarkedObjects.value.clear()
    }
  }
  
  window.addEventListener('auth-change', handleAuthChange)
  
  try {
    await initMap()
    await loadUserFavorites() // 👈 Загружаем избранное при старте
    if (categories.length > 0) await loadObjects(categories[0])
  } catch (err) { 
    setError(`Ошибка инициализации: ${err.message}`) 
  }
  
  return () => window.removeEventListener('auth-change', handleAuthChange)
})

onBeforeUnmount(() => {
  clearTimeout(balloonTimeout); clearTimeout(removeTimeout); clearTimeout(searchTimeout); clearTimeout(boundsTimeout)
  setError.clear?.(); setSuccess.clear?.()
  if (activePlacemark && map?.geoObjects) map.geoObjects.remove(activePlacemark)
  clearUserMarker(); destroyGeolocation()
  if (map) { map.destroy(); map = null; clusterer = null }
  clearRatingsCache(); cleanupAddMode()
  delete window.__toggleBookmark; delete window.__openReview
})

const {
  loadObjects,
  loading,
  objectsCount
} = useObjectLoad({
  api,
  map: toRef(() => map),
  clusterer: toRef(() => clusterer),
  fetchWithTimeout,
  getMapBbox,
  createBalloonContent,
  markerConfig,
  bookmarkedObjects,
  getCategoryIcon,
  setError,
  setSuccess,
  fetchRating,
  activePlacemarkRef: toRef(() => activePlacemark),
  activeFilterRef: activeFilter,
  userCoordsRef: userCoords,
  selectedCategoryRef: selectedCategory,
  isAuthenticatedRef: isAuthenticated
})

loadObjectsRef.value = loadObjects
</script>

<style scoped>
.map-page { position: relative; width: 97vw; height: 96vh; overflow: hidden; margin: 0; padding: 0; outline: 1px solid rgba(22,143,4,0.3); border-radius: 5px; font-family: Inter, system-ui, sans-serif; box-sizing: border-box; }
.map-container { position: absolute; inset: 0px; z-index: 1; background: #f1f5f9; cursor: grab; }
.map-container:active { cursor: grabbing; }
.sidebar {
  position: absolute;
  left: 5px;
  top: 5px;
  bottom: 5px;
  width: 330px;
  z-index: 15;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}
.sidebar * { pointer-events: auto; box-sizing: border-box; }
.sidebar-section { background: rgb(255, 255, 255); backdrop-filter: blur(20px); border-radius: 20px; padding: 18px 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border: 1px solid rgba(10, 73, 0, 0.436); }
.sidebar-label { display: block; font-size: 12px; font-weight: 700; color: #143200; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px; padding-left: 4px; }
:deep(.p-autocomplete) { width: 100%; }
:deep(.p-autocomplete .p-inputtext) { font-size: 13px; padding: 11px 14px; border-radius: 12px; border: 2px solid #e2e8f0; transition: all 0.5s; background: rgba(255,255,255,0.9); }
:deep(.p-autocomplete .p-inputtext:focus) { border-color: #168f04; box-shadow: 0 0 0 4px rgba(22,143,4,0.12); outline: none; background: #fff; }
:deep(.p-autocomplete-panel) { border-radius: 14px; box-shadow: 0 12px 40px rgba(0,0,0,0.15); border: 1px solid rgba(22,143,4,0.15); }
:deep(.p-autocomplete-item) { font-size: 13px; padding: 12px 16px; cursor: pointer; transition: all 0.5s; }
:deep(.p-autocomplete-item:hover) { background: rgba(22,143,4,0.08); color: #168f04; padding-left: 20px; }
:deep(.p-autocomplete-item.p-highlight) { background: linear-gradient(135deg, #168f04, #007306); color: #fff; }
.top-categories { display: flex; flex-direction: column; gap: 8px; }
.top-category-btn { display: flex; align-items: center; gap: 12px; width: 100%; padding: 12px 14px; background: rgba(255,255,255,0.6); border: 2px solid #e2e8f0; border-radius: 12px; font-size: 12px; font-weight: 600; color: #334155; cursor: pointer; transition: all 0.3s; text-align: left; }
.top-category-btn:hover { border-color: #168f04; background: rgba(22,143,4,0.08); color: #168f04; transform: translateX(4px); }
.top-category-btn.active { background: linear-gradient(135deg, #168f04, #007306); border-color: #168f04; color: #fff; box-shadow: 0 4px 16px rgba(22,143,4,0.3); }
.top-category-btn .rank { background: rgba(22,143,4,0.15); color: #168f04; font-size: 10px; font-weight: 800; padding: 3px 10px; border-radius: 20px; min-width: 32px; text-align: center; }
.top-category-btn.active .rank { background: rgba(255,255,255,0.25); color: #fff; }

/* ===== КАТЕГОРИИ СО СКРОЛЛОМ ===== */
.categories-section { 
  flex: 1; 
  display: flex; 
  flex-direction: column;
  overflow: hidden;
}

.categories-list { 
  flex: 1; 
  overflow-y: auto; 
  overflow-x: hidden;
  display: flex;
  flex-direction: column; 
  gap: 8px; 
  padding-right: 6px;
  max-height: 300px;
}

/* Стилизация скролла для категорий */
.categories-list::-webkit-scrollbar { 
  width: 6px; 
}

.categories-list::-webkit-scrollbar-track { 
  background: rgba(22, 143, 4, 0.05);
  border-radius: 4px;
}

.categories-list::-webkit-scrollbar-thumb { 
  background: rgba(22, 143, 4, 0.4); 
  border-radius: 4px;
  transition: background 0.3s;
}

.categories-list::-webkit-scrollbar-thumb:hover { 
  background: rgba(22, 143, 4, 0.6); 
}

/* Для Firefox */
.categories-list {
  scrollbar-width: thin;
  scrollbar-color: rgba(22, 143, 4, 0.4) rgba(22, 143, 4, 0.05);
}

.category-btn { display: flex; align-items: center; gap: 10px; width: 100%; padding: 10px 14px; background: rgba(255,255,255,0.5); border: 1px solid #e2e8f0; border-radius: 10px; font-size: 12px; color: #334155; cursor: pointer; transition: all 0.9s; text-align: left; font-weight: 600; }
.category-btn:hover { border-color: #168f04; color: #168f04; background: rgba(22,143,4,0.06); padding-left: 18px; }
.category-btn.active { background: linear-gradient(135deg, #168f04, #007306); border-color: #168f04; color: #fff; font-weight: 700; }

/* ===== ФИЛЬТРЫ ===== */
.filters-section { 
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  max-height: 250px;
  overflow: hidden;
}
.filters-header { 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  margin-bottom: 10px; 
}
.filters-header .sidebar-label { margin-bottom: 0; }
.filters-clear {
  background: none;
  border: none;
  color: #64748b;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
}
.filters-clear:hover {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.filters-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-right: 4px;
}

.filters-list::-webkit-scrollbar { 
  width: 6px; 
}
.filters-list::-webkit-scrollbar-track { 
  background: rgba(22, 143, 4, 0.05);
  border-radius: 4px;
}
.filters-list::-webkit-scrollbar-thumb { 
  background: rgba(22, 143, 4, 0.4); 
  border-radius: 4px;
  transition: background 0.3s;
}
.filters-list::-webkit-scrollbar-thumb:hover { 
  background: rgba(22, 143, 4, 0.6); 
}
.filters-list {
  scrollbar-width: thin;
  scrollbar-color: rgba(22, 143, 4, 0.4) rgba(22, 143, 4, 0.05);
}

.filter-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  background: rgba(255,255,255,0.5);
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 12px;
  color: #334155;
  cursor: pointer;
  transition: all 0.9s;
  text-align: left;
  font-weight: 600;
}

.filter-chip i { 
  font-size: 13px;
}

.filter-chip:hover {
  border-color: #168f04;
  color: #168f04;
  background: rgba(22,143,4,0.06);
  padding-left: 18px;
}

.filter-chip.active {
  background: linear-gradient(135deg, #168f04, #007306);
  border-color: #168f04;
  color: #fff;
  font-weight: 700;
}

.filter-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.3);
}

.filter-chip:disabled:hover {
  border-color: #e2e8f0;
  background: rgba(255, 255, 255, 0.3);
  color: #94a3b8;
  padding-left: 10px;
}

.filter-chip .pi-lock {
  color: #94a3b8;
}

.info-panel { position: absolute; left: 340px; bottom: 4px; z-index: 15; background: rgb(255, 255, 255); backdrop-filter: blur(20px); color: #1a1a1a; padding: 8px 13px; border-radius: 16px; font-size: 13px; font-weight: 600; border: 1px solid rgba(18, 131, 0, 0.447); display: flex; align-items: center; gap: 5px;}
.category-badge { background: rgba(22,143,4,0.12); color: #168f04; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.filters-badge { 
  background: rgba(59, 130, 246, 0.15); 
  color: #2563eb; 
  padding: 4px 8px; 
  border-radius: 20px; 
  font-size: 10px; 
  font-weight: 700; 
  text-transform: uppercase; 
  margin-left: 4px;
}
.map-controls-right { position: absolute; top: 330px; right: 10px; z-index: 20; display: flex; flex-direction: column; gap: 12px; pointer-events: none; align-items: center; }
.map-controls-right * { pointer-events: auto; }
.layer-switcher { display: flex; flex-direction: column; gap: 5px; background: rgba(255,255,255,0.92); backdrop-filter: blur(20px); padding: 7px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); border: 1px solid rgba(22,143,4,0.15); }
.layer-btn { width: 40px; height: 40px; border: 2px solid #e2e8f0; background: #fff; border-radius: 12px; color: #64748b; cursor: pointer; transition: all 0.5s; display: flex; align-items: center; justify-content: center; }
.layer-btn:hover { border-color: #168f04; background: rgba(22,143,4,0.08); color: #168f04; }
.layer-btn.active { background: linear-gradient(135deg, #168f04, #007306); border-color: #168f04; color: #fff; box-shadow: 0 6px 20px rgba(22,143,4,0.35); }
.geo-btn { width: 43px; height: 43px; border: 2px solid #e2e8f0; background: rgba(255,255,255,0.92); backdrop-filter: blur(20px); color: #64748b; font-size: 18px; border-radius: 12px; cursor: pointer; transition: all 0.9s; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.geo-btn:hover:not(:disabled) { border-color: #168f04; background: rgba(22,143,4,0.08); color: #168f04; box-shadow: 0 8px 24px rgba(22,143,4,0.25); }
.geo-btn:active:not(:disabled) { transform: scale(0.96); }
.geo-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.add-object-btn {
  width: 43px; height: 43px;
  border: 2px solid #e2e8f0;
  background: linear-gradient(135deg, #168f04, #007306);
  color: white;
  font-size: 18px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.5s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.add-object-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(22,143,4,0.45);
}
.add-object-btn.active {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  border-color: #dc2626;
  box-shadow: 0 4px 16px rgba(220,38,38,0.3);
}
.add-object-btn.active:hover {
  box-shadow: 0 8px 24px rgba(220,38,38,0.45);
}
.add-mode-hint {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 25;
  background: rgba(22, 143, 4, 0.95);
  color: white;
  padding: 10px 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 15px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.hint-close {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  margin-left: 8px;
}
.add-confirm-popup {
  position: absolute;
  z-index: 30;
  pointer-events: none;
}
.add-confirm-popup * { pointer-events: auto; }
.confirm-content {
  background: white;
  border-radius: 12px;
  padding: 14px 18px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.418);
  border: 1px solid rgba(22,143,4,0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  min-width: 220px;
}
.confirm-content i {
  font-size: 18px;
  color: #168f04;
}
.confirm-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}
.confirm-btn {
  padding: 6px 14px;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.5s;
}
.confirm-btn.cancel {
  background: #f1f5f9;
  color: #64748b;
}
.confirm-btn.cancel:hover {
  background: #e2e8f0;
  color: #475569;
}
.confirm-btn.confirm {
  background: linear-gradient(135deg, #168f04, #007306);
  color: white;
}
.loading-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 25; background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); padding: 18px 32px; border-radius: 16px; box-shadow: 0 12px 40px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 14px; color: #1a1a1a; font-weight: 600; border: 1px solid rgba(22,143,4,0.2); }
.spinner-icon { font-size: 22px; color: #168f04; }
.error-overlay, .success-overlay { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); z-index: 25; padding: 14px 22px; border-radius: 14px; display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 13px; backdrop-filter: blur(20px); box-shadow: 0 8px 32px rgba(0,0,0,0.12); border: 1px solid; max-width: 400px; }
.error-overlay { background: rgba(254,242,242,0.95); border-color: #fecaca; color: #dc2626; }
.success-overlay { background: rgba(220,252,231,0.95); border-color: #86efac; color: #16a34a; }
.close-btn { background: none; border: none; color: inherit; font-size: 16px; cursor: pointer; padding: 4px; margin-left: 8px; border-radius: 8px; transition: all 0.2s; display: flex; align-items: center; }
.close-btn:hover { background: rgba(0,0,0,0.08); transform: scale(1.1); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.9s; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideDown { from { opacity: 0; transform: translate(-50%, -20px); } to { opacity: 1; transform: translate(-50%, 0); } }
@media (max-width: 768px) {
  .sidebar { width: 260px; left: 12px; top: 12px; bottom: 90px; }
  .info-panel { left: 12px; bottom: 12px; flex-wrap: wrap; gap: 8px; }
  .map-controls-right { top: 12px; right: 12px; gap: 10px; }
  .layer-btn, .geo-btn, .add-object-btn { width: 44px; height: 44px; }
  .add-confirm-popup { left: 50% !important; transform: translateX(-50%) !important; top: 50% !important; }
  .filters-list { max-height: 150px; }
}
.categories-section { flex: 1; display: flex; flex-direction: column; }
</style>