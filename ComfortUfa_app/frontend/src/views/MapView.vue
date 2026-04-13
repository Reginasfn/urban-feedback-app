<template>
  <div class="map-page">
    
    <!-- ===== ЛЕВЫЙ ПЛАВАЮЩИЙ САЙДБАР ===== -->
    <div class="sidebar">
      <!-- 🔍 Поиск по названию/адресу -->
      <div class="sidebar-section">
        <label class="sidebar-label">Поиск объектов</label>
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

      <!-- Топ-5 категорий -->
      <div class="sidebar-section">
        <label class="sidebar-label">Топ-5 объектов</label>
        <div class="top-categories">
          <button 
            v-for="(cat, idx) in topCategories" 
            :key="cat"
            @click="loadObjects(cat)"
            :class="{ active: selectedCategory === cat }"
            class="top-category-btn"
          >
            <span class="rank">#{{ idx + 1 }}</span>
            <span class="name">{{ cat }}</span>
          </button>
        </div>
      </div>

      <!-- Все категории -->
      <div class="sidebar-section">
        <label class="sidebar-label">Все типы объектов</label>
        <div class="categories-list">
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
    </div>

    <!-- Информационная панель -->
    <Transition name="fade-slide">
      <div v-if="objectsCount > 0" class="info-panel">
        <i class="pi pi-map-marker"></i>
        <span>Объектов: <strong>{{ objectsCount }}</strong></span>
        <span v-if="selectedCategory" class="category-badge">{{ selectedCategory }}</span>
      </div>
    </Transition>

    <!-- ===== ПРАВАЯ ПАНЕЛЬ: Слои + Геолокация + ДОБАВИТЬ ОБЪЕКТ ===== -->
    <div class="map-controls-right">
      <!-- Переключатель слоёв -->
      <div class="layer-switcher">
        <button 
          v-for="layer in mapLayers" 
          :key="layer.id"
          @click="switchLayer(layer.id)"
          :class="{ active: currentLayer === layer.id }"
          class="layer-btn"
          :title="layer.title"
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

      <!-- 👇 КНОПКА ДОБАВЛЕНИЯ ОБЪЕКТА (только для авторизованных) -->
      <button 
        v-if="isAuthenticated"
        class="add-object-btn" 
        :class="{ active: isAddingMode }"
        @click="toggleAddMode"
        :disabled="loading"
        title="Добавить объект на карту"
      >
        <i class="pi" :class="isAddingMode ? 'pi-times' : 'pi-plus'"></i>
      </button>
    </div>

    <!-- 👇 ПОДСКАЗКА ПРИ ДОБАВЛЕНИИ -->
    <Transition name="fade-slide">
      <div v-if="isAddingMode" class="add-mode-hint">
        <i class="pi pi-map-marker"></i>
        <span>Нажмите на карту, чтобы добавить объект</span>
        <button class="hint-close" @click="toggleAddMode"><i class="pi pi-times"></i></button>
      </div>
    </Transition>

    <!-- 👇 ПОДТВЕРЖДЕНИЕ ДОБАВЛЕНИЯ (маленькое всплывающее окно) -->
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
      <div v-if="loading" class="loading-overlay">
        <i class="pi pi-spin pi-spinner spinner-icon"></i>
        <span>Определяем местоположение...</span>
      </div>
    </Transition>

    <!-- Сообщение об ошибке -->
    <Transition name="fade-slide">
      <div v-if="error" class="error-overlay">
        <i class="pi pi-exclamation-triangle"></i>
        <span>{{ error }}</span>
        <button @click="error = null" class="close-btn"><i class="pi pi-times"></i></button>
      </div>
    </Transition>

    <!-- Сообщение об успехе -->
    <Transition name="fade-slide">
      <div v-if="success" class="success-overlay">
        <i class="pi pi-check-circle"></i>
        <span>{{ success }}</span>
      </div>
    </Transition>

    <!-- ===== МОДАЛЬНОЕ ОКНО ОТЗЫВА ===== -->
    <ReviewModal
      v-model:visible="showReviewModal"
      :selected-object="selectedObjectForReview"
      :review-categories="reviewCategories"
      :category-icons="categoryIcons"
      @submit="handleReviewSubmit"
      @cancel="handleReviewCancel"
      @error="handleReviewError"
    />

    <!-- 👇 МОДАЛЬНОЕ ОКНО ДОБАВЛЕНИЯ ОБЪЕКТА -->
    <ObjectModal
      v-model:visible="showObjectModal"
      :coordinates="pendingObjectCoords"
      :available-types="objectTypeOptions"
      @submit="handleObjectSubmit"
      @cancel="handleObjectCancel"
      @error="handleObjectError"
    />

    <!-- ===== КАРТА ===== -->
    <div ref="mapContainer" class="map-container"></div>

  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import axios from 'axios'
import AutoComplete from 'primevue/autocomplete'
import ReviewModal from '@/components/modals/ReviewModal.vue'
import ObjectModal from '@/components/modals/ObjectModal.vue'

// 👇 ИМПОРТ С ПЕРЕИМЕНОВАНИЕМ, чтобы не было конфликта имён
import { 
  isAuthenticated as checkAuth,
  getCurrentUser 
} from '@/utils/auth'

// ===== Состояние =====
const mapContainer = ref(null)
const loading = ref(false)
const error = ref(null)
const success = ref(null)
const selectedCategory = ref(null)
const objectsCount = ref(0)
const debugInfo = ref('')
const isMapInitialized = ref(false)
const searchQuery = ref('')
const searchResults = ref([])
const currentLayer = ref('map')

// 👇 Аутентификация
const isAuthenticated = ref(checkAuth())

// 👇 Слушаем изменения авторизации
onMounted(() => {
  const handleAuthChange = (event) => {
    isAuthenticated.value = event.detail.isAuthenticated
  }
  
  window.addEventListener('auth-change', handleAuthChange)
  
  onBeforeUnmount(() => {
    window.removeEventListener('auth-change', handleAuthChange)
  })
})

const bookmarkedObjects = ref(new Set())
const showReviewModal = ref(false)
const selectedObjectForReview = ref(null)

// 👇 ДОБАВЛЕНИЕ ОБЪЕКТОВ
const isAddingMode = ref(false)
const showAddConfirm = ref(false)
const showObjectModal = ref(false)
const pendingObjectCoords = ref(null)
const confirmPosition = ref({ top: '0px', left: '0px' })

// Категории отзывов
const reviewCategories = [
  { value: 'praise', label: 'Похвала', icon: 'pi pi-thumbs-up' },
  { value: 'suggestion', label: 'Предложение', icon: 'pi pi-lightbulb' },
  { value: 'problem', label: 'Проблема', icon: 'pi pi-exclamation-circle' }
]

// Типы объектов для добавления
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
let userLocationPlacemark = null
let activePlacemark = null
let balloonTimeout = null
let removeTimeout = null

// ===== Константы =====
const UFA_CENTER = [54.7388, 55.9721]
const DEFAULT_ZOOM = 12

// ===== Категории =====
const categories = [
    'Камера видеонаблюдения', 'Кафе', 'Фонарь', 'Скамейка',
    'Парк', 'Беседка', 'Остановка', 'Детская площадка'
]

const topCategories = ['Кафе', 'Скамейка', 'Детская площадка', 'Парк', 'Остановка']

// ===== Слои карты =====
const mapLayers = [
    { id: 'map', title: 'Схема', icon: 'pi pi-hashtag' },
    { id: 'satellite', title: 'Спутник', icon: 'pi pi-globe' },
    { id: 'hybrid', title: 'Гибрид', icon: 'pi pi-map' }
]

// ===== Настройки маркеров =====
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

// ===== PrimeIcons для категорий =====
const categoryIcons = {
    'Камера видеонаблюдения': 'pi pi-video',
    'Кафе': 'pi pi-map-marker',
    'Фонарь': 'pi pi-lightbulb',
    'Скамейка': 'pi pi-map-marker',
    'Парк': 'pi pi-map-marker',
    'Беседка': 'pi pi-building-columns',
    'Остановка': 'pi pi-car',
    'Детская площадка': 'pi pi-face-smile'
}

const getCategoryIcon = (cat) => categoryIcons[cat] || 'pi pi-map-marker'

// 🔍 ===== ПОИСК: теперь делаем запрос к API =====
const searchCategories = async (event) => {
  const query = event.query.trim()
  
  // Если запрос короткий — не делаем запрос
  if (query.length < 2) {
    searchResults.value = []
    return
  }
  
  try {
    // 👇 Запрос к бэкенду с параметром search
    const response = await axios.get('http://localhost:8000/api/objects', {
      params: { 
        search: query, 
        limit: 15  // показываем топ-15 результатов
      }
    })
    
    // 👇 Форматируем результаты для AutoComplete
    searchResults.value = response.data.map(obj => ({
      label: `${obj.name} — ${obj.address || 'Адрес не указан'}`,
      ...obj, // 👈 ВСЕ ДАННЫЕ В ОДНОМ ОБЪЕКТЕ
      type: obj.type_name
    }))
    
  } catch (err) {
    console.error('[Search] Ошибка:', err)
    searchResults.value = []
  }
}

// ===== Плавное перемещение к объекту (унифицированная функция) =====
const navigateToObject = async (obj) => {
  if (!map || !obj.coords) {
    console.error('[Navigate] Карта или координаты не найдены')
    error.value = 'Не удалось перейти к объекту'
    setTimeout(() => { error.value = null }, 3000)
    return
  }
  
  console.log('[Navigate] Переход к объекту:', obj)
  
  // 👇 Очищаем предыдущую метку и таймеры
  clearTimeout(balloonTimeout)
  clearTimeout(removeTimeout)

  if (activePlacemark && map.geoObjects) {
    map.geoObjects.remove(activePlacemark)
    activePlacemark = null
  }
  
  try {
    // Плавное перемещение камеры карты с анимацией
    await map.panTo(obj.coords, {
      flying: true,
      duration: 1200
    })
    
    // Устанавливаем зум после перемещения
    await map.setZoom(16, { duration: 400 })
    
    // 👇 Создаем и добавляем метку с ПОЛНЫМИ данными
    const placemark = new window.ymaps.Placemark(
      obj.coords,
      { 
        balloonContent: createBalloonContent({
          id_object: obj.id_object,
          name: obj.name,
          address: obj.address,
          type_name: obj.type_name
        }, 0, obj.type_name),
        hintContent: obj.name || 'Объект'
      },
      { 
        preset: markerConfig[obj.type_name]?.preset || 'islands#grayCircleIcon',
        isOurObject: true,
        zIndex: 1000,
        balloonCloseButton: true,
        balloonMaxWidth: 350,
        balloonMinWidth: 280
      }
    )
    
    // Сохраняем ссылку на активную метку
    activePlacemark = placemark
    
    // Добавляем метку на карту
    map.geoObjects.add(placemark)
    
    // 👇 Добавляем обработчик закрытия балуна - удаляем метку с карты
    placemark.events.add('balloonclose', () => {
      if (map.geoObjects && activePlacemark === placemark) {
        map.geoObjects.remove(placemark)
        activePlacemark = null
      }
    })
    
    // Открываем балун с небольшой задержкой
    balloonTimeout = setTimeout(() => {
      if (placemark.balloon) {
        placemark.balloon.open()
      }
    }, 300)
    
    success.value = `Найден: ${obj.name || 'Объект'}`
    setTimeout(() => { success.value = null }, 2500)
    
  } catch (err) {
    console.error('[Navigate] Ошибка:', err)
    error.value = 'Ошибка при переходе к объекту'
    setTimeout(() => { error.value = null }, 3000)
  }
}

// ===== КАРТОЧКА ОБЪЕКТА В БАЛУНЕ =====
const createBalloonContent = (obj, index, type) => {
  console.log('[Balloon] Полученные данные:', obj) // 👈 Лог для отладки
  
  const isBookmarked = bookmarkedObjects.value.has(obj.id_object)
  const displayName = obj.name || `Объект #${obj.id_object || (index + 1)}`
  const displayAddress = obj.address || 'Адрес не указан'
  const displayType = obj.type_name || type || 'Не указан'
  
  console.log('[Balloon] Отображение:', { displayName, displayAddress, displayType })
  
  return `
    <div class="object-card">
      <button class="bookmark-btn ${isBookmarked ? 'active' : ''}" 
              onclick="window.__toggleBookmark?.('${obj.id_object}', this)"
              title="${isBookmarked ? 'Убрать из избранного' : 'Добавить в избранное'}">
        <i class="pi ${isBookmarked ? 'pi-bookmark-fill' : 'pi-bookmark'}"></i>
      </button>
      <div class="object-card-header">
        <i class="pi ${getCategoryIcon(displayType)}"></i>
        <h4>${displayName}</h4>
      </div>
      <p class="object-address"><i class="pi pi-map-marker"></i> ${displayAddress}</p>
      <div class="object-card-footer">
        <span class="object-type">${displayType}</span>
        <button class="review-btn" onclick="window.__openReview?.('${obj.id_object}', '${displayName.replace(/'/g, "\\'")}', '${displayType}')">
          <i class="pi pi-pencil"></i> Добавить отзыв
        </button>
      </div>
    </div>
    <style>
      .object-card { font-family: Inter, system-ui, sans-serif; min-width: 280px; background: linear-gradient(135deg, #fff 0%, #f8fafc 100%); border-radius: 16px; padding: 16px 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.12); border: 1px solid rgba(22,143,4,0.15); position: relative; }
      .bookmark-btn { position: absolute; top: 12px; right: 12px; width: 32px; height: 32px; border: none; background: rgba(22,143,4,0.1); color: #168f04; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.3s; z-index: 10; }
      .bookmark-btn:hover { background: rgba(22,143,4,0.2); transform: scale(1.1); }
      .bookmark-btn.active { background: #168f04; color: white; }
      .object-card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid rgba(22,143,4,0.1); }
      .object-card-header i { font-size: 20px; color: #168f04; background: rgba(22,143,4,0.1); padding: 8px; border-radius: 10px; }
      .object-card-header h4 { margin: 0; font-size: 16px; font-weight: 700; color: #1a1a1a; }
      .object-address { margin: 0 0 16px 0; font-size: 13px; color: #64748b; display: flex; align-items: center; gap: 6px; }
      .object-card-footer { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
      .object-type { font-size: 11px; font-weight: 600; color: #168f04; background: rgba(22,143,4,0.1); padding: 4px 10px; border-radius: 20px; text-transform: uppercase; }
      .review-btn { display: flex; align-items: center; gap: 6px; background: linear-gradient(135deg, #168f04 0%, #007306 100%); color: white; border: none; padding: 10px 18px; border-radius: 10px; font-size: 12px; font-weight: 600; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 14px rgba(22,143,4,0.3); }
      .review-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(22,143,4,0.45); }
    </style>
  `
}

// 👇 Обработка нажатия Enter в поле поиска
const handleSearchKeydown = (event) => {
  if (event.key === 'Enter' && searchResults.value.length > 0) {
    const firstResult = searchResults.value[0]

    if (firstResult?.id_object) {
      event.preventDefault()
      navigateToObject(firstResult)
      searchQuery.value = ''
      searchResults.value = []
    }
  }
}

// 👇 При выборе результата из поиска (клик мышью или выбор из списка)
// 👈 ИСПРАВЛЕНИЕ: используем правильный доступ к выбранному элементу
const onCategorySelect = async (event) => {
  const selected = event.value

  console.log('[Select] Выбран элемент:', selected)

  if (selected && selected.id_object) {
    await navigateToObject(selected)
    searchQuery.value = ''
    searchResults.value = []
    return
  }
}

// ===== Блокировка стандартных объектов Яндекса =====
const blockDefaultObjects = (e) => {
    const target = e.target
    if (target.classList?.contains('ymaps-2-1-79-object-balloon') || 
        target.classList?.contains('ymaps-2-1-79-placemark') ||
        target.closest?.('.ymaps-2-1-79-object-balloon') ||
        target.closest?.('.ymaps-2-1-79-placemark')) {
        e.stopPropagation()
        e.preventDefault()
        return false
    }
}

// ===== Переключение слоёв =====
const switchLayer = (layerId) => {
    if (!map) return
    currentLayer.value = layerId
    const layerMap = { 'map': 'yandex#map', 'satellite': 'yandex#satellite', 'hybrid': 'yandex#hybrid' }
    map.setType(layerMap[layerId])
    success.value = `Слой: ${mapLayers.find(l => l.id === layerId)?.title}`
    setTimeout(() => { success.value = null }, 1500)
}

// ===== Инициализация карты =====
const initMap = () => {
    debugInfo.value = 'Загрузка API Яндекс.Карт...'
    return new Promise((resolve, reject) => {
        if (!mapContainer.value) {
            reject(new Error('Контейнер карты не найден'))
            return
        }
        
        const setupMap = () => createMapInstance().then(resolve).catch(reject)
        
        if (window.ymaps) {
            window.ymaps.ready(setupMap)
        } else {
            const existingScript = document.querySelector('script[src*="api-maps.yandex.ru"]')
            if (existingScript) {
                existingScript.onload = () => window.ymaps?.ready(setupMap)
                existingScript.onerror = () => reject(new Error('Script load error'))
                return
            }
            
            const apiKey = import.meta.env.VITE_YANDEX_MAPS_KEY || ''
            const script = document.createElement('script')
            script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=ru_RU`
            script.async = true
            
            script.onload = () => window.ymaps?.ready(setupMap)
            script.onerror = () => reject(new Error('Не удалось загрузить Яндекс.Карты'))
            document.head.appendChild(script)
        }
    })
}

const createMapInstance = () => {
    return new Promise((resolve, reject) => {
        if (!window.ymaps) {
            reject(new Error('ymaps не определён'))
            return
        }
        
        window.ymaps.ready(() => {
            try {
                map = new window.ymaps.Map(mapContainer.value, {
                    center: UFA_CENTER,
                    zoom: DEFAULT_ZOOM,
                    controls: []
                })
                
                const zoomControl = new window.ymaps.control.ZoomControl({
                    options: {
                        size: 'large',
                        float: 'none',
                        position: { top: '110px', right: '25px' },
                        maxWidth: '48px',
                        maxHeight: '120px'
                    }
                })
                map.controls.add(zoomControl)
                
                map.options.set('balloonEnabled', false)
                map.options.set('hintEnabled', false)
                map.options.set('suppressMapOpenBlock', true)
                map.behaviors.disable('dblClickZoom')
                
                map.events.add('click', (e) => {
                    if (isAddingMode.value) {
                        handleMapClick(e)
                    }
                })
                
                map.events.add('balloonopen', (e) => {
                    const target = e.get('target')
                    if (!target?.options?.get('isOurObject')) {
                        map.balloon.close()
                        e.stopPropagation()
                        return false
                    }
                })
                
                map.events.add('click', (e) => {
                    const target = e.get('target')
                    if (isAddingMode.value) return
                    if (!target?.options?.get('isOurObject') && target !== clusterer) {
                        e.stopPropagation()
                        return false
                    }
                })
                
                clusterer = new window.ymaps.Clusterer({
                    preset: 'islands#invertedDarkGreenClusterIcons',
                    clusterDisableClickZoom: false,
                    clusterOpenBalloonOnClick: true,
                    clusterHasBalloon: true
                })
                map.geoObjects.add(clusterer)
                
                isMapInitialized.value = true
                debugInfo.value = ''
                resolve()
            } catch (err) {
                reject(err)
            }
        })
    })
}

// ===== ГЕОЛОКАЦИЯ =====
const goToMyLocation = () => {
    if (loading.value) return
    loading.value = true
    error.value = null
    
    if (!navigator.geolocation) {
        error.value = 'Геолокация не поддерживается браузером'
        loading.value = false
        return
    }
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude
            const lon = position.coords.longitude
            const accuracy = position.coords.accuracy
            
            if (!map) {
                error.value = 'Карта не готова'
                loading.value = false
                return
            }
            
            map.setCenter([lat, lon], 18, { duration: 600 })
            
            if (userLocationPlacemark) {
                map.geoObjects.remove(userLocationPlacemark)
            }
            
            userLocationPlacemark = createCustomUserMarker([lat, lon])
            map.geoObjects.add(userLocationPlacemark)
            
            const accText = accuracy < 100 ? `±${Math.round(accuracy)}м` : 'приблизительно'
            success.value = `Вы находитесь здесь (точность: ${accText})`
            setTimeout(() => { success.value = null }, 3000)
            loading.value = false
        },
        (err) => {
            const errors = { 1: 'Доступ запрещён', 2: 'Недоступна', 3: 'Тайм-аут' }
            error.value = `Геолокация: ${errors[err.code] || 'Ошибка'}`
            loading.value = false
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    )
}

// ===== КАСТОМНАЯ МЕТКА ПОЛЬЗОВАТЕЛЯ =====
const createCustomUserMarker = (coords) => {
    const svgString = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
            <ellipse cx="24" cy="44" rx="10" ry="3" fill="rgba(0,0,0,0.2)"/>
            <path d="M24 2C15.16 2 8 9.16 8 18c0 13.5 16 28 16 28s16-14.5 16-28c0-8.84-7.16-16-16-16z" 
                  fill="#168f04" stroke="#ffffff" stroke-width="2.5"/>
            <path d="M18 24l4 4 8-8" fill="none" stroke="#ffffff" stroke-width="3.5" stroke-linecap="round"/>
        </svg>
    `.trim()
    
    try {
        return new window.ymaps.Placemark(
            coords,
            { hintContent: 'Вы здесь', balloonContent: '<b>Ваше местоположение</b>' },
            {
                iconLayout: 'default#image',
                iconImageHref: `data:image/svg+xml,${encodeURIComponent(svgString)}`,
                iconImageSize: [48, 48],
                iconImageOffset: [-24, -48],
                zIndex: 2000,
                isOurObject: true
            }
        )
    } catch {
        return new window.ymaps.Placemark(coords, { hintContent: 'Вы здесь' }, {
            preset: 'islands#greenCircleDotIcon', zIndex: 2000, isOurObject: true
        })
    }
}

// ===== ЗАГРУЗКА ОБЪЕКТОВ =====
const loadObjects = async (type) => {
    if (!map || !clusterer) { error.value = 'Карта ещё не загрузилась'; return }
    loading.value = true; error.value = null; success.value = null
    selectedCategory.value = type; clusterer.removeAll(); objectsCount.value = 0

    try {
        const response = await axios.get('http://localhost:8000/api/objects', { params: { type, limit: 1000 } })
        const objects = response.data || []
        if (objects.length === 0) { error.value = `Объектов типа "${type}" не найдено`; loading.value = false; return }
        
        const config = markerConfig[type] || { preset: 'islands#grayCircleIcon' }
        const placemarks = objects.map((obj, index) => new window.ymaps.Placemark(
            obj.coords,
            { balloonContent: createBalloonContent(obj, index, type), hintContent: obj.name || type },
            { preset: config.preset, isOurObject: true, zIndex: 100 }
        ))
        clusterer.add(placemarks)
        objectsCount.value = placemarks.length
        success.value = `Загружено ${placemarks.length} объектов`
        setTimeout(() => { success.value = null }, 1500)
    } catch (err) {
        error.value = err.response?.data?.detail || `Ошибка: ${err.message}`
    } finally { loading.value = false }
}

// ===== ГЛОБАЛЬНЫЕ ФУНКЦИИ =====
window.__toggleBookmark = (objectId, btnElement) => {
    if (!isAuthenticated.value) {
        error.value = '🔐 Пожалуйста, авторизуйтесь, чтобы добавлять в избранное'
        setTimeout(() => { error.value = null }, 3000)
        return
    }
    if (bookmarkedObjects.value.has(objectId)) {
        bookmarkedObjects.value.delete(objectId)
        if (btnElement) { 
            btnElement.classList.remove('active')
            btnElement.querySelector('i').className = 'pi pi-bookmark'
            btnElement.title = 'Добавить в избранное' 
        }
        success.value = 'Убрано из избранного'
    } else {
        bookmarkedObjects.value.add(objectId)
        if (btnElement) { 
            btnElement.classList.add('active')
            btnElement.querySelector('i').className = 'pi pi-bookmark-fill'
            btnElement.title = 'Убрать из избранного' 
        }
        success.value = 'Добавлено в избранное'
    }
    setTimeout(() => { success.value = null }, 2000)
}

// ===== ОБРАБОТЧИКИ ДЛЯ REVIEWMODAL =====
// Добавьте обработчик для отправки отзыва
const handleReviewSubmit = async (payload) => {
  console.log('[Review] Получен payload:', payload)
  
  // payload содержит: { formData, photo }
  // Здесь можно отправить данные на бэкенд если нужно
  
  success.value = 'Отзыв успешно отправлен!'
  showReviewModal.value = false
  setTimeout(() => { success.value = null }, 2500)
}

// В глобальной функции открытия модалки передавайте корректные данные:
window.__openReview = (objectId, objectName, objectType) => {
  console.log('[__openReview] Вызов:', { objectId, objectName, objectType })
  console.log('[__openReview] isAuthenticated:', isAuthenticated.value)
  
  if (!isAuthenticated.value) {
    console.warn('[__openReview] Пользователь не авторизован!')
    error.value = 'Необходимо авторизоваться, чтобы оставить отзыв'
    setTimeout(() => { error.value = null }, 3000)
    return
  }
  
  selectedObjectForReview.value = { 
    id: parseInt(objectId),
    name: objectName, 
    type: objectType 
  }
  console.log('[__openReview] selectedObjectForReview:', selectedObjectForReview.value)
  console.log('[__openReview] showReviewModal = true')
  
  showReviewModal.value = true
}

const handleReviewError = ({ message }) => {
  error.value = message
  setTimeout(() => { error.value = null }, 3000)
}

const handleReviewCancel = () => { console.log('[ReviewModal] Отменено') }

// ===== WATCHERS =====
watch(isAddingMode, (newValue) => {
  if (!map) return
  if (newValue) {
    map.behaviors.disable('drag')
    map.behaviors.disable('scrollZoom')
    if (mapContainer.value) mapContainer.value.style.cursor = 'crosshair'
  } else {
    map.behaviors.enable('drag')
    map.behaviors.enable('scrollZoom')
    if (mapContainer.value) mapContainer.value.style.cursor = 'grab'
  }
})

// ===== ФУНКЦИИ ДЛЯ ДОБАВЛЕНИЯ ОБЪЕКТОВ =====
const toggleAddMode = () => {
  if (!isAuthenticated.value) {
    error.value = 'Необходимо авторизоваться, чтобы добавлять объекты'
    setTimeout(() => { error.value = null }, 3000)
    return
  }
  isAddingMode.value = !isAddingMode.value
  if (!isAddingMode.value) showAddConfirm.value = false
}

const getAddressFromCoords = async (coords) => {
  try {
    const apiKey = import.meta.env.VITE_YANDEX_MAPS_KEY || ''
    const [lat, lon] = coords
    const response = await axios.get(
      `https://geocode-maps.yandex.ru/1.x/?apikey=${apiKey}&geocode=${lon},${lat}&results=1&lang=ru_RU&format=json`
    )
    const geoObjects = response.data.response.GeoObjectCollection.featureMember
    if (geoObjects.length > 0) {
      return geoObjects[0].GeoObject.metaDataProperty.GeocoderMetaData.text
    }
    return null
  } catch (err) {
    console.error('[Geocoding] Ошибка:', err)
    return null
  }
}

const handleMapClick = async (e) => {
  if (!isAddingMode.value || !map) return
  const coords = e.get('coords')
  if (!coords) return
  e.stopPropagation()
  e.preventDefault()
  pendingObjectCoords.value = coords
  const address = await getAddressFromCoords(coords)
  const containerRect = mapContainer.value?.getBoundingClientRect()
  if (containerRect) {
    const position = e.get('position')
    confirmPosition.value = {
      top: `${position[1] + 10}px`,
      left: `${position[0] + 10}px`
    }
  }
  if (address) {
    success.value = `Адрес: ${address}`
    setTimeout(() => { success.value = null }, 4000)
  }
  showAddConfirm.value = true
}

const cancelAddObject = () => {
  showAddConfirm.value = false
  pendingObjectCoords.value = null
  isAddingMode.value = false
}

const confirmAddObject = async () => {
  if (!pendingObjectCoords.value || !Array.isArray(pendingObjectCoords.value)) {
    error.value = 'Координаты не определены'
    setTimeout(() => { error.value = null }, 3000)
    return
  }
  showAddConfirm.value = false
  await getAddressFromCoords(pendingObjectCoords.value)
  showObjectModal.value = true
}

const handleObjectSubmit = async (payload) => {
  console.log('📦 [ObjectModal] Сохранение объекта:', payload)
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    const newPlacemark = new window.ymaps.Placemark(
      payload.coords,
      { 
        balloonContent: createBalloonContent({ ...payload, id_object: `temp_${Date.now()}` }, 0, payload.type),
        hintContent: payload.name 
      },
      { 
        preset: markerConfig[payload.type]?.preset || 'islands#grayCircleIcon',
        isOurObject: true,
        zIndex: 100
      }
    )
    if (clusterer) clusterer.add(newPlacemark)
    else if (map) map.geoObjects.add(newPlacemark)
    success.value = `Объект "${payload.name}" добавлен!`
    setTimeout(() => { success.value = null }, 2500)
    showObjectModal.value = false
    isAddingMode.value = false
  } catch (err) {
    console.error('[ObjectSubmit] Ошибка:', err)
    error.value = 'Не удалось добавить объект. Попробуйте позже.'
  } finally {
    loading.value = false
  }
}

const handleObjectCancel = () => {
  pendingObjectCoords.value = null
  isAddingMode.value = false
  showObjectModal.value = false
}

const handleObjectError = ({ message }) => {
  error.value = message
  setTimeout(() => { error.value = null }, 3000)
}

// ===== LIFE CYCLE =====
onMounted(async () => {
    try {
        await initMap()
        if (categories.length > 0) await loadObjects(categories[0])
    } catch (err) {
        error.value = `Ошибка: ${err.message}`
    }
})

onBeforeUnmount(() => {
    if (activePlacemark && map?.geoObjects) {
        map.geoObjects.remove(activePlacemark)
        activePlacemark = null
    }
    clearTimeout(balloonTimeout)
    clearTimeout(removeTimeout)
    if (map) { map.destroy(); map = null; clusterer = null; userLocationPlacemark = null }
    delete window.__toggleBookmark
    delete window.__openReview
})
</script>

<style scoped>
/* === БАЗОВЫЕ СТИЛИ === */
.map-page { position: relative; width: 97vw; height: 96vh; overflow: hidden; margin: 0; padding: 0; outline: 1px solid rgba(22,143,4,0.3); border-radius: 5px; font-family: Inter, system-ui, sans-serif; box-sizing: border-box; }
.map-container { position: absolute; inset: 0px; z-index: 1; background: #f1f5f9; cursor: grab; }
.map-container:active { cursor: grabbing; }
.sidebar { position: absolute; left: 5px; top: 5px; bottom: 500px; width: 330px; z-index: 15; display: flex; flex-direction: column; gap: 2px; pointer-events: none; box-sizing: border-box; }
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
.categories-list { display: flex; flex-direction: column; gap: 6px; max-height: 200px; overflow-y: auto; padding-right: 4px; }
.categories-list::-webkit-scrollbar { width: 4px; }
.categories-list::-webkit-scrollbar-thumb { background: rgba(22,143,4,0.3); border-radius: 4px; }
.category-btn { display: flex; align-items: center; gap: 10px; width: 100%; padding: 10px 14px; background: rgba(255,255,255,0.5); border: 1px solid #e2e8f0; border-radius: 10px; font-size: 12px; color: #334155; cursor: pointer; transition: all 0.5s; text-align: left; font-weight: 600; }
.category-btn:hover { border-color: #168f04; color: #168f04; background: rgba(22,143,4,0.06); padding-left: 18px; }
.category-btn.active { background: linear-gradient(135deg, #168f04, #007306); border-color: #168f04; color: #fff; font-weight: 700; }
.info-panel { position: absolute; left: 340px; bottom: 4px; z-index: 15; background: rgb(255, 255, 255); backdrop-filter: blur(20px); color: #1a1a1a; padding: 8px 13px; border-radius: 16px; font-size: 13px; font-weight: 600; border: 1px solid rgba(18, 131, 0, 0.447); display: flex; align-items: center; gap: 5px; animation: slideUp 0.5s; }
.category-badge { background: rgba(22,143,4,0.12); color: #168f04; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.map-controls-right { position: absolute; top: 330px; right: 10px; z-index: 20; display: flex; flex-direction: column; gap: 12px; pointer-events: none; align-items: center; }
.map-controls-right * { pointer-events: auto; }
.layer-switcher { display: flex; flex-direction: column; gap: 5px; background: rgba(255,255,255,0.92); backdrop-filter: blur(20px); padding: 7px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); border: 1px solid rgba(22,143,4,0.15); }
.layer-btn { width: 40px; height: 40px; border: 2px solid #e2e8f0; background: #fff; border-radius: 12px; color: #64748b; cursor: pointer; transition: all 0.5s; display: flex; align-items: center; justify-content: center; }
.layer-btn:hover { border-color: #168f04; background: rgba(22,143,4,0.08); color: #168f04; }
.layer-btn.active { background: linear-gradient(135deg, #168f04, #007306); border-color: #168f04; color: #fff; box-shadow: 0 6px 20px rgba(22,143,4,0.35); }
.geo-btn { width: 43px; height: 43px; border: 2px solid #e2e8f0; background: rgba(255,255,255,0.92); backdrop-filter: blur(20px); color: #64748b; font-size: 18px; border-radius: 12px; cursor: pointer; transition: all 0.5s; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.geo-btn:hover:not(:disabled) { border-color: #168f04; background: rgba(22,143,4,0.08); color: #168f04; box-shadow: 0 8px 24px rgba(22,143,4,0.25); }
.geo-btn:active:not(:disabled) { transform: scale(0.96); }
.geo-btn:disabled { opacity: 0.6; cursor: not-allowed; }

/* 👇 КНОПКА ДОБАВЛЕНИЯ ОБЪЕКТА */
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

/* 👇 ПОДСКАЗКА ПРИ ДОБАВЛЕНИИ */
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
  animation: slideDown 0.5s;
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

/* 👇 ПОПАП ПОДТВЕРЖДЕНИЯ ДОБАВЛЕНИЯ */
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

/* Индикатор загрузки */
.loading-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 25; background: rgba(255,255,255,0.95); backdrop-filter: blur(20px); padding: 18px 32px; border-radius: 16px; box-shadow: 0 12px 40px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 14px; color: #1a1a1a; font-weight: 600; border: 1px solid rgba(22,143,4,0.2); }
.spinner-icon { font-size: 22px; color: #168f04; }
.error-overlay, .success-overlay { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); z-index: 25; padding: 14px 22px; border-radius: 14px; display: flex; align-items: center; gap: 10px; font-weight: 600; font-size: 13px; backdrop-filter: blur(20px); box-shadow: 0 8px 32px rgba(0,0,0,0.12); border: 1px solid; animation: slideDown 0.4s; max-width: 400px; }
.error-overlay { background: rgba(254,242,242,0.95); border-color: #fecaca; color: #dc2626; }
.success-overlay { background: rgba(220,252,231,0.95); border-color: #86efac; color: #16a34a; }
.close-btn { background: none; border: none; color: inherit; font-size: 16px; cursor: pointer; padding: 4px; margin-left: 8px; border-radius: 8px; transition: all 0.2s; display: flex; align-items: center; }
.close-btn:hover { background: rgba(0,0,0,0.08); transform: scale(1.1); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.5s; }
.fade-slide-enter-from, .fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes slideDown { from { opacity: 0; transform: translate(-50%, -20px); } to { opacity: 1; transform: translate(-50%, 0); } }
@media (max-width: 768px) {
  .sidebar { width: 260px; left: 12px; top: 12px; bottom: 90px; }
  .info-panel { left: 12px; bottom: 12px; flex-wrap: wrap; gap: 8px; }
  .map-controls-right { top: 12px; right: 12px; gap: 10px; }
  .layer-btn, .geo-btn, .add-object-btn { width: 44px; height: 44px; }
  .add-confirm-popup { left: 50% !important; transform: translateX(-50%) !important; top: 50% !important; }
}
</style>