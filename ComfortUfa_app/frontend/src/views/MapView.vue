<template>
  <div class="map-page">
    
    <!-- ===== ЛЕВЫЙ ПЛАВАЮЩИЙ САЙДБАР ===== -->
    <div class="sidebar">
      <!-- Поиск по категориям -->
      <div class="sidebar-section">
        <label class="sidebar-label">Поиск объектов</label>
        <AutoComplete 
          v-model="searchQuery" 
          :suggestions="filteredCategories" 
          @complete="searchCategories"
          placeholder="Введите название..."
          class="w-full"
          :dropdown="true"
          @item-select="onCategorySelect"
        />
      </div>

      <!-- Топ-5 категорий -->
      <div class="sidebar-section">
        <label class="sidebar-label">Топ-3 категории</label>
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
        <label class="sidebar-label">Все категории</label>
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

    <!-- ===== ПРАВАЯ ПАНЕЛЬ: Слои + Геолокация ===== -->
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
    </div>

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

    <!-- ===== КАРТА ===== -->
    <div ref="mapContainer" class="map-container" @click="blockDefaultObjects"></div>

  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import axios from 'axios'
import AutoComplete from 'primevue/autocomplete'

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

let map = null
let clusterer = null
let userLocationPlacemark = null

// ===== Константы =====
const UFA_CENTER = [54.7388, 55.9721]
const DEFAULT_ZOOM = 12

// ===== Категории =====
const categories = [
    'Камера видеонаблюдения',
    'Кафе',
    'Фонарь',
    'Скамейка',
    'Парк',
    'Беседка',
    'Остановка',
    'Детская площадка'
]

const topCategories = [
    'Кафе',
    'Скамейка',
    'Детская площадка',
    'Парк',
    'Остановка'
]

// ===== Слои карты =====
const mapLayers = [
    { id: 'map', title: 'Схема', icon: 'pi pi-hashtag' },
    { id: 'satellite', title: 'Спутник', icon: 'pi pi-globe' },
    { id: 'hybrid', title: 'Гибрид', icon: 'pi pi-map' }
]

// ===== Настройки маркеров =====
const markerConfig = {
    "Кафе": { preset: 'islands#redCircleIcon' },
    "Скамейка": { preset: 'islands#greenCircleIcon' },
    "Фонарь": { preset: 'islands#yellowCircleIcon' },
    "Парк": { preset: 'islands#greenCircleDotIcon' },
    "Беседка": { preset: 'islands#violetCircleIcon' },
    "Остановка": { preset: 'islands#blueCircleIcon' },
    "Детская площадка": { preset: 'islands#orangeCircleIcon' },
    "Камера видеонаблюдения": { preset: 'islands#blackCircleIcon' }
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

// ===== Фильтрация для поиска =====
const filteredCategories = computed(() => {
    if (!searchQuery.value) return []
    return categories.filter(cat => 
        cat.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
})

const searchCategories = (event) => {
    setTimeout(() => {
        searchResults.value = categories.filter(cat => 
            cat.toLowerCase().includes(event.query.toLowerCase())
        )
    }, 100)
}

const onCategorySelect = (event) => {
    loadObjects(event.value)
    searchQuery.value = ''
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
                        position: {
                            top: '110px',
                            right: '25px'
                        },
                        maxWidth: '48px',
                        maxHeight: '120px'
                    }
                })
                map.controls.add(zoomControl)
                
                // Блокируем стандартные балуны
                map.options.set('balloonEnabled', false)
                map.options.set('hintEnabled', false)
                map.options.set('suppressMapOpenBlock', true)
                map.behaviors.disable('dblClickZoom')
                
                // Перехват чужих балунов
                map.events.add('balloonopen', (e) => {
                    const target = e.get('target')
                    if (!target?.options?.get('isOurObject')) {
                        map.balloon.close()
                        e.stopPropagation()
                        return false
                    }
                })
                
                // Перехват кликов
                map.events.add('click', (e) => {
                    const target = e.get('target')
                    if (!target?.options?.get('isOurObject') && target !== clusterer) {
                        e.stopPropagation()
                        return false
                    }
                })
                
                // Кластеризатор
                clusterer = new window.ymaps.Clusterer({
                    preset: 'islands#invertedVioletClusterIcons',
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

// ===== ГЕОЛОКАЦИЯ ЧЕРЕЗ БРАУЗЕР =====
const goToMyLocation = () => {
    if (loading.value) return
    
    loading.value = true
    error.value = null
    
    // есть ли поддержка геолокации
    if (!navigator.geolocation) {
        error.value = 'Геолокация не поддерживается браузером'
        loading.value = false
        return
    }
    
    console.log('[goToMyLocation] 🔄 Запрашиваем координаты через браузер...')
    
    // БРАУЗЕРНАЯ ГЕОЛОКАЦИЯ
    navigator.geolocation.getCurrentPosition(
        // УСПЕХ
        (position) => {
            const lat = position.coords.latitude
            const lon = position.coords.longitude
            const accuracy = position.coords.accuracy
            
            console.log('[goToMyLocation] Координаты:', { lat, lon, accuracy })
            
            if (!map) {
                error.value = 'Карта не готова'
                loading.value = false
                return
            }
            
            // Плавный перелёт к точке
            map.setCenter([lat, lon], 18, { duration: 600 })
            
            if (userLocationPlacemark) {
                map.geoObjects.remove(userLocationPlacemark)
            }
            
            // Создаём и ставим галочку
            userLocationPlacemark = createCustomUserMarker([lat, lon])
            map.geoObjects.add(userLocationPlacemark)
            
            const accText = accuracy < 100 ? `±${Math.round(accuracy)}м` : 'приблизительно'
            success.value = `Вы находитесь здесь (точность: ${accText})`
            setTimeout(() => { success.value = null }, 3000)
            
            loading.value = false
        },
        // ОШИБКА
        (err) => {
            console.error('[goToMyLocation] Ошибка:', err)
            const errors = {
                1: 'Доступ к геолокации запрещён',
                2: 'Геолокация недоступна',
                3: 'Превышено время ожидания'
            }
            error.value = `Геолокация: ${errors[err.code] || 'Ошибка'}`
            loading.value = false
        },
        // ОПЦИИ ДЛЯ МАКСИМАЛЬНОЙ ТОЧНОСТИ
        {
            enableHighAccuracy: true,
            timeout: 15000,         
            maximumAge: 0            
        }
    )
}

// КАСТОМНАЯ МЕТКА С ГАЛОЧКОЙ (С ОТЛАДКОЙ)
const createCustomUserMarker = (coords) => {
    
    const svgString = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
            <!-- Тень -->
            <ellipse cx="24" cy="44" rx="10" ry="3" fill="rgba(0,0,0,0.2)"/>
            <!-- Зелёный пин -->
            <path d="M24 2C15.16 2 8 9.16 8 18c0 13.5 16 28 16 28s16-14.5 16-28c0-8.84-7.16-16-16-16z" 
                  fill="#168f04" stroke="#ffffff" stroke-width="2.5"/>
            <!-- Белая галочка -->
            <path d="M18 24l4 4 8-8" 
                  fill="none" stroke="#ffffff" stroke-width="3.5" 
                  stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    `.trim()

    const encodedSvg = encodeURIComponent(svgString)
    const iconHref = `data:image/svg+xml,${encodedSvg}`
    
    try {
        const placemark = new window.ymaps.Placemark(
            coords,
            { 
                hintContent: 'Вы здесь', 
                balloonContent: '<b>Ваше местоположение</b>' 
            },
            {
                iconLayout: 'default#image',
                iconImageHref: iconHref,
                iconImageSize: [48, 48],
                iconImageOffset: [-24, -48], 
                zIndex: 2000,
                isOurObject: true
            }
        )

        
        placemark.events.add('load', () => {
            console.log('[createCustomUserMarker] 🖼️ Иконка метки загружена')
        })
        
        placemark.events.add('error', (e) => {
            console.error('[createCustomUserMarker] ❌ Ошибка загрузки иконки:', e)
        })
        
        return placemark
        
    } catch (err) {
        console.error('[createCustomUserMarker] ❌ Ошибка создания метки:', err)
        
        console.log('[createCustomUserMarker] 🔄 Используем fallback-метку')
        return new window.ymaps.Placemark(
            coords,
            { hintContent: 'Вы здесь' },
            {
                preset: 'islands#greenCircleDotIcon',
                zIndex: 2000,
                isOurObject: true
            }
        )
    }
}

// ===== ЗАГРУЗКА ОБЪЕКТОВ =====
const loadObjects = async (type) => {
    if (!map || !clusterer) {
        error.value = 'Карта ещё не загрузилась'
        return
    }

    loading.value = true
    error.value = null
    success.value = null
    selectedCategory.value = type
    clusterer.removeAll()
    objectsCount.value = 0

    try {
        const response = await axios.get('http://localhost:8000/api/objects', {
            params: { type, limit: 1000 }
        })
        const objects = response.data || []
        
        if (objects.length === 0) {
            error.value = `Объектов типа "${type}" не найдено`
            loading.value = false
            return
        }

        const config = markerConfig[type] || { preset: 'islands#grayCircleIcon' }
        
        const placemarks = objects.map((obj, index) => {
            return new window.ymaps.Placemark(
                obj.coords,
                {
                    balloonContent: createBalloonContent(obj, index, type),
                    hintContent: obj.name || type
                },
                {
                    preset: config.preset,
                    isOurObject: true,
                    zIndex: 100
                }
            )
        })

        clusterer.add(placemarks)
        objectsCount.value = placemarks.length
        success.value = `Загружено ${placemarks.length} объектов`
        setTimeout(() => { success.value = null }, 1500)

    } catch (err) {
        error.value = err.response?.data?.detail || `Ошибка: ${err.message}`
    } finally {
        loading.value = false
    }
}

// ===== Карточка объекта в балуне =====
const createBalloonContent = (obj, index, type) => `
    <div class="object-card">
        <div class="object-card-header">
            <i class="pi ${getCategoryIcon(type)}"></i>
            <h4>${obj.name || 'Объект #' + (index + 1)}</h4>
        </div>
        <p class="object-address"><i class="pi pi-map-marker"></i> ${obj.address || 'Адрес не указан'}</p>
        <div class="object-card-footer">
            <span class="object-type">${type}</span>
            <button class="review-btn" onclick="window.__rateObject?.('${obj.id_object}')">
                <i class="pi pi-pencil"></i> Добавить отзыв
            </button>
        </div>
    </div>
    <style>
        .object-card { font-family: Inter, system-ui, sans-serif; min-width: 280px; background: linear-gradient(135deg, #fff 0%, #f8fafc 100%); border-radius: 16px; padding: 16px 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.12); border: 1px solid rgba(22,143,4,0.15); }
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

window.__rateObject = (id) => alert(`Оценка объекта #${id}\n(Функция в разработке)`)

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
    if (map) { map.destroy(); map = null; clusterer = null; userLocationPlacemark = null }
    delete window.__rateObject
})
</script>

<style scoped>
.map-page {
  position: relative;
  width: 97vw;
  height: 96vh;
  overflow: hidden; 
  margin: 0;
  padding: 0;
  outline: 1px solid rgba(22,143,4,0.3);
  border-radius: 5px;
  font-family: Inter, system-ui, sans-serif;
  box-sizing: border-box;
}

/* КОНТЕЙНЕР КАРТЫ*/
.map-container {
  position: absolute;
  inset: 0px;
  z-index: 1;
  background: #f1f5f9;
}

.sidebar {
  position: absolute;
  left: 5px;
  top: 5px;
  bottom: 500px;
  width: 330px;
  z-index: 15;
  display: flex;
  flex-direction: column;
  gap: 2px;
  pointer-events: none;
  box-sizing: border-box;
}
.sidebar * {
  pointer-events: auto;
  box-sizing: border-box;
}
.sidebar-section {
  background: rgb(255, 255, 255);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 18px 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
  border: 1px solid rgba(10, 73, 0, 0.436);
}

.sidebar-label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: #143200;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 12px;
  padding-left: 4px;
}

:deep(.p-autocomplete) {
  width: 100%;
}

:deep(.p-autocomplete .p-inputtext) {
  font-size: 13px;
  padding: 11px 14px;
  border-radius: 12px;
  border: 2px solid #e2e8f0;
  transition: all 0.5s;
  background: rgba(255,255,255,0.9);
}
:deep(.p-autocomplete .p-inputtext:focus) {
  border-color: #168f04;
  box-shadow: 0 0 0 4px rgba(22,143,4,0.12);
  outline: none;
  background: #fff;
}
:deep(.p-autocomplete-panel) {
  border-radius: 14px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
  border: 1px solid rgba(22,143,4,0.15);
}
:deep(.p-autocomplete-item) {
  font-size: 13px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.5s;
}
:deep(.p-autocomplete-item:hover) {
  background: rgba(22,143,4,0.08);
  color: #168f04;
  padding-left: 20px;
}
:deep(.p-autocomplete-item.p-highlight) {
  background: linear-gradient(135deg, #168f04, #007306);
  color: #fff;
}

.top-categories {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.top-category-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  background: rgba(255,255,255,0.6);
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
}
.top-category-btn:hover {
  border-color: #168f04;
  background: rgba(22,143,4,0.08);
  color: #168f04;
  transform: translateX(4px);
}

.top-category-btn.active {
  background: linear-gradient(135deg, #168f04, #007306);
  border-color: #168f04;
  color: #fff;
  box-shadow: 0 4px 16px rgba(22,143,4,0.3);
}

.top-category-btn .rank {
  background: rgba(22,143,4,0.15);
  color: #168f04;
  font-size: 10px;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 20px;
  min-width: 32px;
  text-align: center;
}

.top-category-btn.active .rank {
  background: rgba(255,255,255,0.25);
  color: #fff;
}

.categories-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 4px;
}
.categories-list::-webkit-scrollbar {
  width: 4px;
}
.categories-list::-webkit-scrollbar-thumb {
  background: rgba(22,143,4,0.3);
  border-radius: 4px;
}
.category-btn {
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
  transition: all 0.5s;
  text-align: left;
  font-weight: 600;
}
.category-btn:hover {
  border-color: #168f04;
  color: #168f04;
  background: rgba(22,143,4,0.06);
  padding-left: 18px;
}
.category-btn.active {
  background: linear-gradient(135deg, #168f04, #007306);
  border-color: #168f04;
  color: #fff;
  font-weight: 700;
}

.info-panel {
  position: absolute;
  left: 340px;
  bottom: 4px;
  z-index: 15;
  background: rgb(255, 255, 255);
  backdrop-filter: blur(20px);
  color: #1a1a1a;
  padding: 8px 13px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(18, 131, 0, 0.447);
  display: flex;
  align-items: center;
  gap: 5px;
  animation: slideUp 0.5s;
}
.category-badge {
  background: rgba(22,143,4,0.12);
  color: #168f04;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

.map-controls-right {
  position: absolute;
  top: 330px;
  right: 10px;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 12px;
  pointer-events: none;
  align-items: center;
}
.map-controls-right * {
  pointer-events: auto;
}
.layer-switcher {
  display: flex;
  flex-direction: column;
  gap: 5px;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(20px);
  padding: 7px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(22,143,4,0.15);
}
.layer-btn {
  width: 40px;
  height: 40px;
  border: 2px solid #e2e8f0;
  background: #fff;
  border-radius: 12px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.5s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.layer-btn:hover {
  border-color: #168f04;
  background: rgba(22,143,4,0.08);
  color: #168f04;
}
.layer-btn.active {
  background: linear-gradient(135deg, #168f04, #007306);
  border-color: #168f04;
  color: #fff;
  box-shadow: 0 6px 20px rgba(22,143,4,0.35);
}
.geo-btn {
  width: 43px;
  height: 43px;
  border: 2px solid #e2e8f0;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(20px);
  color: #64748b;
  font-size: 18px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.5s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.geo-btn:hover:not(:disabled) {
  border-color: #168f04;
  background: rgba(22,143,4,0.08);
  color: #168f04;
  box-shadow: 0 8px 24px rgba(22,143,4,0.25);
}
.geo-btn:active:not(:disabled) {
  transform: scale(0.96);
}
.geo-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 25;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  padding: 18px 32px;
  border-radius: 16px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  gap: 14px;
  color: #1a1a1a;
  font-weight: 600;
  border: 1px solid rgba(22,143,4,0.2);
}
.spinner-icon {
  font-size: 22px;
  color: #168f04;
}
.error-overlay, .success-overlay {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 25;
  padding: 14px 22px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 13px;
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  border: 1px solid;
  animation: slideDown 0.4s;
  max-width: 400px;
}
.error-overlay {
  background: rgba(254,242,242,0.95);
  border-color: #fecaca;
  color: #dc2626;
}
.success-overlay {
  background: rgba(220,252,231,0.95);
  border-color: #86efac;
  color: #16a34a;
}
.close-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  margin-left: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
}
.close-btn:hover {
  background: rgba(0,0,0,0.08);
  transform: scale(1.1);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.4s;
}
.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes slideDown {
  from { opacity: 0; transform: translate(-50%, -20px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}

/* ТИЛИ ДЛЯ НАТИВНОГО ЗУМА ЯНДЕКСА */
:global(.ymaps-2-1-79-zoom-control) {
  border-radius: 16px !important;
  overflow: visible !important;
  box-shadow: 0 8px 32px rgba(255, 0, 0, 0.15) !important;
  z-index: 1000 !important; 
  opacity: 1 !important;  
  display: block !important;  
}
:global(.ymaps-2-1-79-zoom-control .ymaps-2-1-79-zoom-control__button) {
  background: rgba(255,255,255,0.95) !important;
  border: 1px solid rgba(22,143,4,0.2) !important;
  color: #64748b !important;
  transition: all 0.3s !important;
  width: 48px !important;
  height: 48px !important;
}
:global(.ymaps-2-1-79-zoom-control .ymaps-2-1-79-zoom-control__button:hover) {
  background: rgba(22,143,4,0.1) !important;
  color: #168f04 !important;
}
:global(.ymaps-2-1-79-zoom-control .ymaps-2-1-79-zoom-control__zoom-scale) {
  background: rgba(22,143,4,0.15) !important;
  border-radius: 4px !important;
}

@media (max-width: 768px) {
  .sidebar {
    width: 260px;
    left: 12px;
    top: 12px;
    bottom: 90px;
  }
  .info-panel {
    left: 12px;
    bottom: 12px;
    flex-wrap: wrap;
    gap: 8px;
  }
  .map-controls-right {
    top: 12px;
    right: 12px;
    gap: 10px;
  }
  .layer-btn, .geo-btn {
    width: 44px;
    height: 44px;
  }
}
</style>