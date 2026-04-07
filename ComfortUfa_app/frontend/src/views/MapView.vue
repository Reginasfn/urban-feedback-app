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

onMounted(() => {
  console.log('MapView mounted')
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