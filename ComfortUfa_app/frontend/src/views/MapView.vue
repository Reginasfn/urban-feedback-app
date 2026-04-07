<template>
  <div class="map-page">
    <header class="map-header">
      <h1>Карта благоустройства Уфы</h1>
      <p class="subtitle">Нажмите на категорию, чтобы увидеть определённые объекты</p>
    </header>
    
    <div ref="mapContainer" class="map-container"></div>
  </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'

    const mapContainer = ref(null) 

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
</style>