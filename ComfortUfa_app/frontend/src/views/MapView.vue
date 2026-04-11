<template>
  <div class="map-page">
    
    <div class="map-overlay">
      <header class="map-header">
        <h3>🗺️ Карта благоустройства города Уфа</h3>
      </header>

      <!-- Контролы управления -->
      <div class="controls-panel">
        <div class="controls-group">
          <button class="control-btn zoom-in" @click="zoomIn" title="Приблизить (Ctrl + +)">
            🔍+
          </button>
          <button class="control-btn zoom-out" @click="zoomOut" title="Отдалить (Ctrl + -)">
            🔍−
          </button>
          <button class="control-btn location-btn" @click="goToMyLocation" title="Мое местоположение">
            📍
          </button>
          <button class="control-btn reset-btn" @click="resetView" title="Вернуться в Уфу">
            🏠
          </button>
        </div>

        <div class="zoom-info">
          Зум: {{ currentZoom }}
        </div>
      </div>

      <!-- Кнопки-фильтры -->
      <div class="button-group">
        <div class="category-title">Категории:</div>
        <button 
          v-for="cat in categories" 
          :key="cat" 
          @click="loadObjects(cat)"
          :class="{ active: selectedCategory === cat }"
          class="category-btn"
        >
          {{ cat }}
        </button>
      </div>

      <!-- Информация об объектах -->
      <div v-if="objectsCount > 0" class="info-panel">
        <span>Объектов: {{ objectsCount }}</span>
      </div>
    </div>

    <!-- Индикатор загрузки -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <span>Загрузка объектов...</span>
    </div>

    <!-- Сообщение об ошибке -->
    <div v-if="error" class="error-overlay">
      <span>⚠️ {{ error }}</span>
      <button @click="error = null" class="close-btn">✕</button>
    </div>

    <!-- Сообщение о успехе -->
    <div v-if="success" class="success-overlay">
      <span>✅ {{ success }}</span>
    </div>

    <!-- КАРТА -->
    <div ref="mapContainer" class="map-container"></div>

  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

// ===== Состояние =====
const mapContainer = ref(null)
const loading = ref(false)
const error = ref(null)
const success = ref(null)
const selectedCategory = ref(null)
const currentZoom = ref(12)
const objectsCount = ref(0)

let map = null
let dataSource = null

// ===== Константы =====
const UFA_CENTER = [55.9721, 54.7388]
const DEFAULT_ZOOM = 12

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

function getColorByType(type) {
    const colors = {
        "Кафе": "#FF0000",
        "Скамейка": "#00AA00",
        "Фонарь": "#FFFF00",
        "Парк": "#006600",
        "Беседка": "#AA00FF",
        "Остановка": "#0000FF",
        "Детская площадка": "#FF8800",
        "Камера видеонаблюдения": "#000000"
    }
    return colors[type] || "#808080"
}

// ===== Загрузка Yandex Maps =====
const loadYmaps = (key) =>
  new Promise((resolve, reject) => {
    if (window.ymaps3) return resolve()

    console.log('📡 Загружаем Yandex Maps v3...')
    const script = document.createElement('script')
    script.src = `https://api-maps.yandex.ru/v3/?apikey=${key}&lang=ru_RU`
    script.async = true

    script.onload = async () => {
      try {
        await window.ymaps3.ready
        console.log('✅ Yandex Maps v3 загружены')
        resolve()
      } catch (e) {
        reject(e)
      }
    }

    script.onerror = () => {
      reject(new Error('Ошибка загрузки Yandex Maps v3'))
    }
    
    document.head.appendChild(script)
  })

// ===== Инициализация карты =====
const initMap = async () => {
  console.log('🗺️ Инициализируем карту...')
  
  await window.ymaps3.ready

  const { 
    YMap, 
    YMapDefaultSchemeLayer,
    YMapDefaultFeaturesLayer,
    YMapFeatureDataSource,
    YMapListener
  } = window.ymaps3

  map = new YMap(mapContainer.value, {
    location: {
      center: UFA_CENTER,
      zoom: DEFAULT_ZOOM
    }
  })

  // ✅ FIX: правильные события
  const listener = new YMapListener({
    onUpdate: ({ location }) => {
      if (location && location.zoom !== undefined) {
        currentZoom.value = Math.round(location.zoom)
      }
    }
  })

  map.addChild(listener)

  // Добавляем слой схемы
  map.addChild(new YMapDefaultSchemeLayer({ theme: 'light' }))

  // DataSource
  dataSource = new YMapFeatureDataSource()
  const featuresLayer = new YMapDefaultFeaturesLayer()
  featuresLayer.addChild(dataSource)
  map.addChild(featuresLayer)

  console.log('✅ Карта инициализирована')
}

// ===== Управление картой =====
const zoomIn = () => {
  if (map && map.location) {
    map.setLocation({
      center: map.location.center,
      zoom: map.location.zoom + 1
    })
  }
}

const zoomOut = () => {
  if (map && map.location) {
    map.setLocation({
      center: map.location.center,
      zoom: Math.max(0, map.location.zoom - 1)
    })
  }
}

const resetView = () => {
  if (map) {
    map.setLocation({
      center: UFA_CENTER,
      zoom: DEFAULT_ZOOM
    })
    success.value = '🏠 Вернулись в Уфу'
    setTimeout(() => { success.value = null }, 2000)
  }
}

const goToMyLocation = () => {
  console.log('📍 Получаем геолокацию...')
  loading.value = true
  
  if (!navigator.geolocation) {
    error.value = 'Геолокация не поддерживается вашим браузером'
    loading.value = false
    return
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords
      const accuracy = position.coords.accuracy
      
      console.log(`✅ Геолокация найдена: ${latitude}, ${longitude} (±${accuracy}м)`)
      
      if (map) {
        map.setLocation({
          center: [longitude, latitude],
          zoom: 15
        })
        
        success.value = `📍 Вы здесь (точность: ±${Math.round(accuracy)}м)`
        setTimeout(() => { success.value = null }, 3000)
      }
      
      loading.value = false
    },
    (err) => {
      let errorMsg = 'Неизвестная ошибка'
      if (err.code === 1) errorMsg = 'Доступ к геолокации запрещён'
      if (err.code === 2) errorMsg = 'Геолокация недоступна'
      if (err.code === 3) errorMsg = 'Превышено время ожидания'
      
      error.value = errorMsg
      loading.value = false
      console.error('Ошибка геолокации:', err)
    }
  )
}

// ===== LOAD OBJECTS =====
const loadObjects = async (type) => {
  loading.value = true
  error.value = null
  success.value = null
  selectedCategory.value = type

  try {
    console.log(`\n📍 Загружаем объекты типа: ${type}`)
    
    const res = await axios.get('http://localhost:8000/api/objects', {
      params: { type }
    })

    const objects = res.data
    console.log(`✅ Получено ${objects.length} объектов`)

    // ✅ Очищаем старые маркеры
// 🔥 Полная очистка через пересоздание



    objectsCount.value = 0

    if (!objects || objects.length === 0) {
      console.warn('⚠️ Объектов не найдено')
      error.value = `Объектов типа "${type}" не найдено`
      loading.value = false
      return
    }

    const color = getColorByType(type)
    const features = []

    // ✅ Формируем features
    objects.forEach((obj, index) => {
      try {
        const feature = {
          type: 'Feature',
          id: `marker-${index}`,
          geometry: {
            type: 'Point',
            coordinates: [obj.coords[0], obj.coords[1]]
          },
          properties: {
            title: obj.name || `Объект ${index + 1}`,
            description: obj.address || 'Адрес не указан',
            color: color
          }
        }
        features.push(feature)
      } catch (e) {
        console.warn(`⚠️ Ошибка при обработке объекта #${index}`)
      }
    })

    // ✅ Добавляем все features в DataSource
    if (features.length > 0) {
      dataSource.update({
            features
        })
      objectsCount.value = features.length
      success.value = `✅ Загружено ${features.length} объектов`
      console.log(`✅ Успешно добавлено ${features.length} маркеров`)
      setTimeout(() => { success.value = null }, 2000)
    }

  } 
  catch (e) {
    error.value = `Ошибка загрузки: ${e.message}`
    console.error('❌ Полная ошибка:', e)
  } 
  finally {
    loading.value = false
  }
}

// ===== LIFE CYCLE =====
onMounted(async () => {
  console.clear()
  console.log("=" .repeat(60))
  console.log("🗺️  ИНИЦИАЛИЗАЦИЯ КАРТЫ УФЫ")
  console.log("=" .repeat(60))

  try {
    const apiKey = import.meta.env.VITE_YANDEX_MAPS_KEY
    if (!apiKey) {
      throw new Error('API ключ не найден (VITE_YANDEX_MAPS_KEY)')
    }

    console.log('1️⃣  Загружаем Yandex Maps...')
    await loadYmaps(apiKey)

    console.log('2️⃣  Инициализируем карту...')
    await initMap()

    console.log('3️⃣  Загружаем первую категорию...')
    await loadObjects(categories[0])
    
    console.log("=" .repeat(60))
    console.log("✅ ВСЁ ГОТОВО! КАРТА РАБОТАЕТ!")
    console.log("=" .repeat(60))
  } catch (e) {
    error.value = `Критическая ошибка: ${e.message}`
    console.error('❌ Ошибка при инициализации:', e)
  }
})

onBeforeUnmount(() => {
  if (map) {
    map.destroy()
    map = null
  }
  dataSource = null
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
  outline: 1px solid rgb(0, 66, 7);
  border-radius: 5px;
}

.map-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  pointer-events: none;
  padding: 10px 20px;
  display: flex;           
  flex-direction: column;  
  align-items: center;     
}

.map-overlay * {
  pointer-events: auto;
}

.map-header {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px);
  padding: 12px 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  margin: 0 auto 12px;
  text-align: center;
}

.map-header h3 {
  color: #1E293B;
  font-size: 22px;
  font-weight: 700;
  margin: 0;
}

.controls-panel {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.controls-group {
  display: flex;
  gap: 8px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 10px 12px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.control-btn {
  width: 44px;
  height: 44px;
  border: 2px solid #007bff;
  background: white;
  color: #007bff;
  font-size: 18px;
  font-weight: 700;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover {
  background: #007bff;
  color: white;
  transform: scale(1.08);
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.4);
}

.control-btn:active {
  transform: scale(0.95);
}

.zoom-info {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #1E293B;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  min-width: 80px;
  text-align: center;
}

.button-group {
  position: absolute;      
  left: 20px;              
  top: 140px;              
  
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 14px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 240px;       
  
  overflow-y: auto;
  max-height: 55vh;
}

.button-group::-webkit-scrollbar {
  width: 6px;
}

.button-group::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.button-group::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.category-title {
  font-size: 12px;
  font-weight: 700;
  color: #64748B;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.category-btn {
  width: 100%;
  padding: 8px 12px;
  border: 2px solid #cbd5e1;
  background: white;
  color: #334155;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.category-btn:hover {
  border-color: #007bff;
  color: #007bff;
  background: #f0f9ff;
}

.category-btn.active {
  background: #007bff;
  border-color: #007bff;
  color: white;
  font-weight: 600;
}

.info-panel {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(34, 197, 94, 0.92);
  color: white;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.loading-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 20;
  background: rgba(255, 255, 255, 0.96);
  padding: 20px 32px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 16px;
  color: #1E293B;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e2e8f0;
  border-top-color: #007bff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-overlay {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  background: #fef2f2;
  border: 2px solid #fecaca;
  color: #dc2626;
  padding: 12px 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 16px rgba(220, 38, 38, 0.15);
  max-width: 400px;
  flex-wrap: wrap;
  backdrop-filter: blur(10px);
}

.close-btn {
  background: none;
  border: none;
  color: #dc2626;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  margin-left: 8px;
  transition: transform 0.2s;
}

.close-btn:hover {
  transform: scale(1.2);
}

.success-overlay {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 20;
  background: #dcfce7;
  border: 2px solid #86efac;
  color: #16a34a;
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(22, 163, 74, 0.15);
  animation: slideIn 0.3s ease-out;
  backdrop-filter: blur(10px);
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.map-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}

/* ===== CUSTOM MARKER ===== */
.custom-marker {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  box-shadow: 0 0 10px rgba(0,0,0,0.3);
}

.dot {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
}
</style>