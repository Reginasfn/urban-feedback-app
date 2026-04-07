<template>
  <div class="map-page">
    <header class="map-header">
      <h1>Карта благоустройства Уфы</h1>
      <p class="subtitle">Нажмите на категорию, чтобы увидеть определённые объекты</p>
    </header>
    
    <!-- Фильтры -->
    <div class="filters">
        <button 
            v-for="category in categories" 
            :key="category"
            @click="selectCategory(category)"
            :class="['filter-btn', { active: selectedCategory === category }]"
            :style="{ borderColor: getCategoryColor(category) }"
        >
            {{ category }}
        </button>
    </div>

    <!-- Статус -->
    <div v-if="loading" class="status">⏳ Загрузка...</div>
    <div v-else-if="error" class="status error">❌ {{ error }}</div>
    <div v-else-if="objectsCount" class="status success">
        Найдено: {{ objectsCount }}
    </div>

    <div ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'
    import axios from 'axios'

    // Состояние для загрузки
    const loading = ref(false)
    const error = ref(null)
    const objectsCount = ref(0)

    // Загрузка объектов
    const loadObjects = async (type) => {
        if (!clusterer) return

        loading.value = true
        error.value = null
        clusterer.removeAll()

        try {
            const response = await axios.get('http://localhost:8000/api/objects', {
                params: { type }
            })

            const objects = response.data
            console.log(`📦 Загружено объектов: ${objects.length}`)

            objectsCount.value = objects.length

        } 
        catch (err) {
            console.error('❌ Ошибка API:', err)
            error.value = 'Не удалось загрузить объекты'
        } 
        finally {
            loading.value = false
        }
    }

    const mapContainer = ref(null) 

    // Состояние
    const selectedCategory = ref(null)

    // Категории
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

    // Цвета категорий
    const categoryColors = {
        'Камера видеонаблюдения': '#1E40AF',
        'Кафе': '#DC2626',
        'Фонарь': '#F59E0B',
        'Скамейка': '#059669',
        'Парк': '#047857',
        'Беседка': '#7C3AED',
        'Остановка': '#2563EB',
        'Детская площадка': '#F97316'
    }

    function getCategoryColor(type) {
        return categoryColors[type] || '#64748B'
    }

    // Обновляем selectCategory
        function selectCategory(type) {
        selectedCategory.value = type
        loadObjects(type) 
    }

    let map = null
    let clusterer = null

    // Инициализация карты
    const initMap = () => {
        return new Promise((resolve) => {
            if (window.ymaps) {
                window.ymaps.ready(() => {
                    createMapInstance()
                    resolve()
                })
            } 
            else {
                const apiKey = import.meta.env.VITE_YANDEX_MAPS_KEY
            
                console.log('🔑 Ключ из .env:', apiKey) // ← добавь это
                console.log('📁 Все env:', import.meta.env) // ← и это

                if (!apiKey) {
                    console.error('Не найден API-ключ в файле .env!')
                    console.error('Проверь: 1) файл .env существует 2) переменная называется VITE_YANDEX_MAPS_KEY')
                    return
                }
               
                const script = document.createElement('script')
                script.src = `https://api-maps.yandex.ru/2.1/?apikey=${apiKey}&lang=ru_RU`
                script.async = true
                script.onload = () => {
                    window.ymaps.ready(() => {
                        createMapInstance()
                        resolve()
                    })
                }
                script.onerror = () => {
                    console.error('Ошибка загрузки Яндекс карты')
                }
                document.head.appendChild(script)
            }
        })
    }
    const createMapInstance = () => {
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
        console.log('✅ Яндекс.Карта инициализирована')
    }

    onMounted(async () => {
        await initMap()
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

    .map-container {
    width: 100%;
    height: 500px;
    background: #F1F5F9;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    }

    .filters {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        margin-bottom: 20px;
        padding: 15px;
        background: #F8FAFC;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }

    .filter-btn {
        padding: 10px 18px;
        border: 2px solid;
        border-radius: 25px;
        background: white;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #334155;
    }

    .filter-btn:hover {
        background: #1E40AF;
        color: white;
        transform: translateY(-2px);
    }

    .filter-btn.active {
        background: #1E40AF;
        color: white;
        font-weight: 600;
    }

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
    }
    .status.success {
        background: #F0FDF4;
        color: #059669;
    }
</style>