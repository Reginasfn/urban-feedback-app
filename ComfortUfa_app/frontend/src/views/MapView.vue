<template>
  <div class="map-page">
    <header class="map-header">
      <h1>🗺️ Карта благоустройства Уфы</h1>
      <p class="subtitle">Нажми на категорию, чтобы увидеть объекты</p>
    </header>

    <!-- Кнопки-фильтры -->
    <div class="button-group">
      <button v-for="cat in categories" :key="cat" @click="loadObjects(cat)">
        {{ cat }}
      </button>
    </div>

    <!-- Статус -->
    <div v-if="loading" class="status">⏳ Загрузка...</div>
    <div v-else-if="error" class="status error">❌ {{ error }}</div>

    <!-- Карта -->
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
let map = null
let clusterer = null

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

// ===== Цвета (как в твоём HTML) =====
function getColorByType(type) {
  const colors = {
    "Кафе": "red",
    "Скамейка": "green",
    "Фонарь": "yellow",
    "Парк": "darkGreen",
    "Беседка": "violet",
    "Остановка": "blue",
    "Детская площадка": "orange",
    "Камера видеонаблюдения": "black"
  }
  return colors[type] || "gray"
}

// ===== Инициализация карты =====
const initMap = () => {
  return new Promise((resolve) => {
    if (window.ymaps) {
      window.ymaps.ready(() => createMap(resolve))
    } else {
      const apiKey = import.meta.env.VITE_YANDEX_MAPS_KEY || ''
      const script = document.createElement('script')
      script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=ru_RU`
      script.onload = () => window.ymaps.ready(() => createMap(resolve))
      script.onerror = () => {
        error.value = 'Не удалось загрузить Яндекс.Карты'
        console.error('Ошибка загрузки API Яндекс.Карт')
      }
      document.head.appendChild(script)
    }
  })
}

const createMap = (resolve) => {
  map = new window.ymaps.Map(mapContainer.value, {
    center: [54.7388, 55.9721], // Уфа
    zoom: 12,
    controls: ['zoomControl', 'geolocationControl']
  })

  clusterer = new window.ymaps.Clusterer({
    preset: 'islands#invertedBlueClusterIcons',
    clusterDisableClickZoom: false,
    clusterOpenBalloonOnClick: true
  })

  map.geoObjects.add(clusterer)
  console.log('✅ Карта готова')
  resolve()
}

// ===== ЗАГРУЗКА ОБЪЕКТОВ (главная функция!) =====
const loadObjects = async (type) => {
  if (!map || !clusterer) {
    error.value = 'Карта ещё не загрузилась'
    return
  }

  loading.value = true
  error.value = null
  clusterer.removeAll() // очищаем старые метки

  try {
    // Запрос к твоему бэкенду
    const response = await axios.get('http://localhost:8000/api/objects', {
      params: { type, limit: 1000 }
    })

    const objects = response.data

    // Создаём метки для каждого объекта
    const placemarks = objects.map(obj => {
      const color = getColorByType(obj.type_name || type)

      return new window.ymaps.Placemark(
        obj.coords, // [широта, долгота] — именно в таком порядке!
        {
          balloonContent: `
            <div style="font-size:14px; min-width:200px">
              <b>${obj.name}</b><br>
              <span style="color:#666">${obj.address || 'Адрес не указан'}</span><br><br>
              <button onclick="window.__rateObject?.('${obj.id_object}')" 
                      style="background:#007bff;color:white;border:none;padding:6px 12px;border-radius:4px;cursor:pointer">
                📝 Оценить
              </button>
            </div>
          `
        },
        {
          preset: `islands#icon`,
          iconColor: color
        }
      )
    })

    // Добавляем метки в кластеризатор
    clusterer.add(placemarks)
    console.log(`✅ Загружено ${placemarks.length} объектов типа "${type}"`)

  } catch (err) {
    console.error('❌ Ошибка:', err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить объекты'
  } finally {
    loading.value = false
  }
}

// ===== Глобальная функция для кнопки "Оценить" в балуне =====
window.__rateObject = (id) => {
  alert(`Вы хотите оценить объект #${id}\n(Функция в разработке)`)
}

// ===== Lifecycle =====
onMounted(async () => {
  await initMap()
})

onBeforeUnmount(() => {
  if (map) {
    map.destroy()
    map = null
    clusterer = null
  }
  delete window.__rateObject
})
</script>

<style scoped>
.map-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.map-header {
  text-align: center;
  margin-bottom: 20px;
}

.map-header h1 {
  color: #1E293B;
  font-size: 24px;
}

.subtitle {
  color: #64748B;
  font-size: 14px;
}

/* Кнопки-фильтры (как в твоём HTML) */
.button-group {
  margin: 10px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.button-group button {
  padding: 8px 16px;
  border: 1px solid #007bff;
  background-color: white;
  color: #007bff;
  font-size: 14px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.button-group button:hover {
  background-color: #007bff;
  color: white;
}

/* Статусы */
.status {
  text-align: center;
  padding: 10px;
  margin: 10px 0;
  border-radius: 8px;
  font-weight: 500;
}

.status.error {
  background: #FEF2F2;
  color: #DC2626;
  border: 1px solid #FECACA;
}

/* Карта */
.map-container {
  width: 100%;
  height: 600px;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  background: #F1F5F9;
}

/* Адаптив */
@media (max-width: 768px) {
  .button-group {
    overflow-x: auto;
    justify-content: flex-start;
    padding: 5px;
  }
  
  .button-group button {
    flex-shrink: 0;
  }
  
  .map-container {
    height: 400px;
  }
}
</style>