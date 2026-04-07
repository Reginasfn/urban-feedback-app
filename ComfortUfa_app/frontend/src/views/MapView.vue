<template>
  <div class="map-page">
    <h1> Карта проблем</h1>
    <div id="map" style="width: 100%; height: 500px;"></div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  // Здесь будет Яндекс карта
  console.log('Карта загружена')
})
</script>