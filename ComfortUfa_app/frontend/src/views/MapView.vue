<template>
  <div class="map-page">
    
    <!-- ===== ПЛАВАЮЩАЯ ПАНЕЛЬ УПРАВЛЕНИЯ ===== -->
    <div class="map-overlay">
      <header class="map-header">
        <h3>Карта благоустройства города Уфа</h3>
        <!-- <p class="subtitle">Выберите категорию, чтобы увидеть объекты</p> -->
      </header>

      <!-- Кнопки-фильтры -->
      <div class="button-group">
        <button 
          v-for="cat in categories" 
          :key="cat" 
          @click="loadObjects(cat)"
          :class="{ active: selectedCategory === cat }"
        >
          {{ cat }}
        </button>
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
      <button @click="error = null">Закрыть</button>
    </div>

    <!-- ===== САМА КАРТА (на весь экран) ===== -->
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
const selectedCategory = ref(null)

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

// ===== Цвета =====
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

const loadYmaps = (key) =>
  new Promise((resolve, reject) => {
    if (window.ymaps3) return resolve()

    const script = document.createElement('script')
    script.src = `https://api-maps.yandex.ru/v3/?apikey=${key}&lang=ru_RU`

    script.onload = resolve
    script.onerror = reject

    document.head.appendChild(script)
  })

// ===== Инициализация карты версии 3 =====
const initMap = async () => {
    
  await window.ymaps3.ready

  const {
    YMap,
    YMapDefaultSchemeLayer,
    YMapMarker
  } = window.ymaps3

  map = new YMap(mapContainer.value, {
    location: {
      center: [55.9721, 54.7388],
      zoom: 12
    }
  })

  // стиль карты (твой JSON можно сюда вставить)
  map.addChild(new YMapDefaultSchemeLayer({
    theme: 'light'
  }))
}

// ===== Инициализация карты версии 2 =====
// const initMap = () => {
//     return new Promise((resolve) => {
//         if (window.ymaps) {
//             window.ymaps.ready(() => createMap(resolve))
//         } else {
//             const apiKey = import.meta.env.VITE_YANDEX_MAPS_KEY || ''
//             const script = document.createElement('script')
//             script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=ru_RU`
//             script.onload = () => window.ymaps.ready(() => createMap(resolve))
//             script.onerror = () => {
//                 error.value = 'Не удалось загрузить Яндекс.Карты'
//             }
//             document.head.appendChild(script)
//         }
//     })
// }
// const createMap = (resolve) => {
//     map = new window.ymaps.Map(mapContainer.value, {
//         center: [54.7388, 55.9721], // Уфа
//         zoom: 12,
//         controls: []
//     })

//     const geoControl = new window.ymaps.control.GeolocationControl({
//         options: {
//             float: 'none',
//             position: {
//                 top: 100,
//                 right: 20
//             }
//         }
//     })

//     const zoomControl = new window.ymaps.control.ZoomControl({
//         options: {
//             float: 'none',
//             position: {
//                 top: 160,
//                 right: 20
//             }
//         }
//     })

//     clusterer = new window.ymaps.Clusterer({
//         preset: 'islands#invertedBlueClusterIcons',
//         clusterDisableClickZoom: false,
//         clusterOpenBalloonOnClick: true
//     })

//     map.controls.add(geoControl)
//     map.controls.add(zoomControl)
//     map.geoObjects.add(clusterer)
//     resolve()
// }
// ===== ЗАГРУЗКА ОБЪЕКТОВ =====
// const loadObjects = async (type) => {
//     if (!map || !clusterer) {
//         error.value = 'Карта ещё не загрузилась'
//         return
//     }

//     selectedCategory.value = type
//     loading.value = true
//     error.value = null
//     clusterer.removeAll()

//     try {
//         const response = await axios.get('http://localhost:8000/api/objects', {
//             params: { type, limit: 1000 }
//         })

//         const objects = response.data
//         const placemarks = objects.map(obj => {
//             const color = getColorByType(obj.type_name || type)
//             return new window.ymaps.Placemark(
//                 obj.coords,
//                 {
//                     balloonContent: `
//                         <div style="font-size:14px; min-width:200px; font-family: sans-serif;">
//                             <b style="font-size:16px; color:#1E293B;">${obj.name}</b><br>
//                             <span style="color:#666; display:block; margin:4px 0;">📍 ${obj.address || 'Адрес не указан'}</span>
//                             <span style="background:#e2e8f0; padding:2px 8px; border-radius:4px; font-size:12px;">${obj.type_name}</span>
//                             <br><br>
//                             <button onclick="window.__rateObject?.('${obj.id_object}')" 
//                                     style="background:#007bff; color:white; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; font-weight:500;">
//                                 📝 Оценить объект
//                             </button>
//                         </div>
//                     `
//                 },
//                 {
//                     preset: `islands#icon`,
//                     iconColor: color
//                 }
//             )
//         })

//         clusterer.add(placemarks)
//         console.log(`✅ Загружено ${placemarks.length} объектов типа "${type}"`)

//     } catch (err) {
//         console.error('❌ Ошибка:', err)
//         error.value = err.response?.data?.detail || 'Не удалось загрузить объекты'
//     } finally {
//         loading.value = false
//     }
// }

// ===== Глобальная функция для кнопки "Оценить" =====
// window.__rateObject = (id) => {
//     alert(`Вы хотите оценить объект #${id}\n(Функция в разработке)`)
// }

// ===== Lifecycle =====
// onMounted(async () => {
//     await initMap()
//     // Загружаем объекты по умолчанию (первая категория)
//     if (categories.length > 0) {
//         await loadObjects(categories[0])
//     }
// })

// onBeforeUnmount(() => {
//     if (map) {
//         map.destroy()
//         map = null
//         clusterer = null
//     }
//     delete window.__rateObject
// })

// ===== LOAD OBJECTS =====



//
// ===== LOAD OBJECTS (FIXED) =====
//
const loadObjects = async (type) => {
  loading.value = true
  error.value = null
  selectedCategory.value = type

  try {
    const res = await axios.get('http://localhost:8000/api/objects', {
      params: { type }
    })

    const objects = res.data

    //
    // ✅ FIX 2: безопасное удаление clusterer
    //
    if (clusterer) {
      map.removeChild(clusterer)
      clusterer = null
    }

    const features = objects.map(obj => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: obj.coords
      },
      properties: obj
    }))

    const { YMapClusterer, clusterByGrid, YMapMarker } = window.ymaps3

    clusterer = new YMapClusterer({
      method: clusterByGrid({ gridSize: 64 }),
      features,

      marker: (feature) => {
        const el = document.createElement('div')

        //
        // ❌ FIX 3: getColor → getColorByType
        //
        el.innerHTML = `
          <div style="
            width:14px;
            height:14px;
            background:${getColorByType(feature.properties.type_name || type)};
            border-radius:50%;
            border:2px solid white;
            box-shadow:0 0 8px rgba(0,0,0,0.3);
            cursor:pointer;
          "></div>
        `

        el.onclick = () => {
          alert(
            `${feature.properties.name}\n${feature.properties.address || ''}`
          )
        }

        return new YMapMarker(
          { coordinates: feature.geometry.coordinates },
          el
        )
      },

      cluster: (coordinates, features) => {
        const el = document.createElement('div')

        el.innerHTML = `
          <div style="
            width:34px;
            height:34px;
            border-radius:50%;
            background:#007aff;
            color:white;
            display:flex;
            align-items:center;
            justify-content:center;
            font-weight:700;
            box-shadow:0 0 10px rgba(0,0,0,0.3);
          ">
            ${features.length}
          </div>
        `

        return new YMapMarker({ coordinates }, el)
      }
    })

    map.addChild(clusterer)

  } catch (e) {
    error.value = 'Ошибка загрузки объектов'
    console.error(e)
  } finally {
    loading.value = false
  }
}

// ===== LIFE CYCLE =====
onMounted(async () => {
    console.log("тууууууут YANDEX KEY =", import.meta.env.VITE_YANDEX_MAPS_KEY)

  await loadYmaps(import.meta.env.VITE_YANDEX_MAPS_KEY)
  
  await initMap()
  await loadObjects(categories[0])
})

onBeforeUnmount(() => {
  if (map) map.destroy()
})
</script>

<style scoped>
/* ===================== ОСНОВНОЙ КОНТЕЙНЕР ===================== */
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

/* ===================== ПЛАВАЮЩАЯ ПАНЕЛЬ (ОВЕРЛЕЙ) ===================== */
.map-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10;
  pointer-events: none;
  padding: 5px 40px;
  display: flex;           /* 👈 Добавил: флекс-контейнер */
  flex-direction: column;  /* 👈 Элементы друг под другом */
  align-items: center;     /* 👈 Заголовок по центру */
}

/* Включаем клики внутри панели */
.map-overlay * {
  pointer-events: auto;
}

/* Шапка */
.map-header {
  background: rgba(255, 255, 255, 0.766);
  backdrop-filter: blur(20px);
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  margin: 0 auto 12px;  /* 👈 auto центрирует */
  text-align: center;
  pointer-events: auto; /* 👈 Включаем клики */
}

.map-header h1 {
  color: #1E293B;
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 4px;
}

.subtitle {
  color: #64748B;
  font-size: 13px;
  margin: 0;
}

/* Кнопки-фильтры */
.button-group {
  position: absolute;      
  left: 40px;              
  top: 75px;              
  
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 220px;        /* 👈 Ограничиваем ширину */
  margin: 0;               /* 👈 Убираем auto */
  
  pointer-events: auto;    /* 👈 Включаем клики */
}

.button-group button {
  padding: 8px 16px;
  border: 2px solid #007bff;
  background: white;
  color: #007bff;
  font-size: 13px;
  font-weight: 500;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.button-group button:hover {
  background: #007bff;
  color: white;
  transform: translateY(-2px);
}

.button-group button.active {
  background: #0056b3;
  border-color: #0056b3;
  color: white;
  font-weight: 600;
}

/* ===================== ИНДИКАТОР ЗАГРУЗКИ ===================== */
.loading-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 20;
  background: rgba(255, 255, 255, 0.95);
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 12px;
  color: #1E293B;
  font-weight: 500;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #e2e8f0;
  border-top-color: #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===================== СООБЩЕНИЕ ОБ ОШИБКЕ ===================== */
.error-overlay {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 12px 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-width: 400px;
}

.error-overlay button {
  background: #dc2626;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}

.error-overlay button:hover {
  background: #b91c1c;
}
</style>