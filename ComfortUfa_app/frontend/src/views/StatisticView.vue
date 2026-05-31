<!-- src/views/StatisticsView.vue -->
<template>
  <div class="statistics-page">
    <!-- ===== ЗАГОЛОВОК ===== -->
    <div class="page-header">
      <h1 class="page-title">Статистика платформы</h1>
      <p class="page-subtitle">Аналитика объектов, отзывов и активности пользователей</p>
      
      <!-- Фильтр периода -->
      <div class="header-controls">
        <Dropdown 
          v-model="selectedPeriod" 
          :options="periodOptions"
          optionLabel="label"
          optionValue="value"
          class="period-select"
          @change="loadAllStats"
          style="width: 150px; height: 30px" 
        />
        <Button 
          label="Обновить" 
          icon="pi pi-refresh" 
          severity="success" 
          size="small"
          :loading="loading"
          @click="loadAllStats"
          style="width: 150px; height: 50px" 
        />
      </div>
    </div>

    <!-- ===== ЗАГРУЗКА / ОШИБКА ===== -->
    <div v-if="loading" class="loading-state">
      <ProgressSpinner style="width: 60px; height: 60px" />
      <span>Загружаем аналитику...</span>
    </div>

    <div v-else-if="error" class="error-state">
      <i class="pi pi-exclamation-triangle"></i>
      <span>{{ error }}</span>
      <Button label="Повторить" severity="success" @click="loadAllStats" />
    </div>

    <!-- ===== ДАШБОРД ===== -->
    <div v-else class="dashboard">
      
      <!-- Карточки метрик -->
      <div class="metrics-grid">
        <div class="metric-card primary">
          <div class="metric-icon"><i class="pi pi-map-marker"></i></div>
          <div class="metric-content">
            <span class="metric-value">{{ stats.total_objects?.toLocaleString('ru-RU') || '0' }}</span>
            <span class="metric-label">Всего объектов</span>
          </div>
        </div>
        <div class="metric-card warning">
          <div class="metric-icon"><i class="pi pi-exclamation-triangle"></i></div>
          <div class="metric-content">
            <span class="metric-value">{{ stats.total_problems?.toLocaleString('ru-RU') || '0' }}</span>
            <span class="metric-label">Сообщено проблем</span>
          </div>
        </div>
        <div class="metric-card info">
          <div class="metric-icon"><i class="pi pi-users"></i></div>
          <div class="metric-content">
            <span class="metric-value">{{ stats.total_users?.toLocaleString('ru-RU') || '0' }}</span>
            <span class="metric-label">Пользователей</span>
          </div>
        </div>
        <div class="metric-card success">
          <div class="metric-icon"><i class="pi pi-heart"></i></div>
          <div class="metric-content">
            <span class="metric-value">{{ favoriteStats?.total || '0' }}</span>
            <span class="metric-label">В избранном</span>
          </div>
        </div>
      </div>

      <!-- Графики: верхний ряд -->
      <div class="charts-row">
        <!-- Объекты по типам (Bar) -->
        <div class="chart-card">
          <h3 class="chart-title">Объекты по типам</h3>
          <!-- ⚠️ Используем обычные настройки -->
          <Bar :data="objectsByTypeChart" :options="chartOptions" />
        </div>
        
        <!-- Отзывы по категориям (Pie) -->
        <div class="chart-card">
          <h3 class="chart-title">Отзывы по категориям</h3>
          <!-- ⚠️ Используем специальные настройки с Топ-5 -->
          <Pie :data="reviewsByCategoryChart" :options="reviewsByCategoryChartOptions" />
        </div>
      </div>

      <!-- Графики: средний ряд -->
      <div class="charts-row">
        <!-- Топ объектов в избранном (Horizontal Bar) -->
        <div class="chart-card wide">
          <h3 class="chart-title">Топ объектов в избранном</h3>
          <!-- ⚠️ Используем обычные настройки -->
          <Bar :data="topFavoritedChart" :options="{ ...chartOptions, indexAxis: 'y' }" />
        </div>
      </div>

      <!-- Графики: нижний ряд -->
      <div class="charts-row">
        <!-- Распределение оценок (Doughnut) -->
        <div class="chart-card">
          <h3 class="chart-title">Распределение оценок</h3>
          <!-- ⚠️ Используем обычные настройки -->
          <Doughnut :data="ratingDistributionChart" :options="chartOptions" />
        </div>
        
        <!-- Топ по отзывам (Bar) -->
        <div class="chart-card">
          <h3 class="chart-title">Топ объектов по отзывам</h3>
          <!-- ⚠️ Используем обычные настройки -->
          <Bar :data="topReviewedChart" :options="{ ...chartOptions, indexAxis: 'y' }" />
        </div>
      </div>

      <!-- Активность по времени (Line) -->
      <div class="chart-card full-width">
        <h3 class="chart-title">Активность за период</h3>
        <!-- ⚠️ Используем обычные настройки -->
        <Line :data="activityTimelineChart" :options="timelineChartOptions" />
      </div>

      <!-- Таблица: Топ типов в избранном -->
      <div class="table-card">
        <h3 class="chart-title">Типы объектов в избранном</h3>
        <div class="stats-table">
          <div class="table-header">
            <span>Тип объекта</span>
            <span>Доля</span>
          </div>
          <div 
            v-for="(item, index) in favoriteTypesData" 
            :key="item.label"
            class="table-row"
          >
            <span class="rank">#{{ index + 1 }}</span>
            <span class="type-name">{{ item.label }}</span>
            <span class="count">{{ item.value }}</span>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: `${(item.value / favoriteTypesData[0]?.value) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement,
  Filler
} from 'chart.js'
import { Bar, Pie, Doughnut, Line } from 'vue-chartjs'
import ProgressSpinner from 'primevue/progressspinner'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import api from '@/services/api'

// Регистрация компонентов Chart.js
ChartJS.register(
  CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend,
  ArcElement, PointElement, LineElement, Filler
)

// ===== Состояние =====
const stats = ref({ total_objects: 0, total_problems: 0, total_users: 0 })
const favoriteStats = ref({ total: 0 })
const objectsByType = ref([])
const reviewsByCategory = ref([])
const topFavorited = ref([])
const favoriteTypes = ref([])
const ratingDistribution = ref([])
const topReviewed = ref([])
const activityTimeline = ref([])

const loading = ref(true)
const error = ref(null)
const selectedPeriod = ref('all')

const periodOptions = [
  { label: 'За всё время', value: 'all' },
  { label: 'За месяц', value: 'month' },
  { label: 'За неделю', value: 'week' }
]

// ===== Настройки графиков =====
const chartColors = {
  primary: '#168f04',
  primaryLight: '#22c55e',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#3b82f6',
  success: '#10b981',
  gray: '#64748b',
  bg: 'rgba(22, 143, 4, 0.1)'
}

// 1. ГЛОБАЛЬНЫЕ НАСТРОЙКИ (БЕЗ топ-5 объектов)
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { font: { family: 'Inter', size: 11 } } },
    tooltip: { 
      backgroundColor: 'rgba(255,255,255,0.95)',
      titleColor: '#1a1a1a',
      bodyColor: '#475569',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      padding: 12,
      displayColors: true
      // Здесь НЕТ callbacks.afterBody
    }
  },
  scales: {
    x: { ticks: { font: { family: 'Inter', size: 10 } }, grid: { color: 'rgba(0,0,0,0.05)' } },
    y: { beginAtZero: true, ticks: { font: { family: 'Inter', size: 10 } }, grid: { color: 'rgba(0,0,0,0.05)' } }
  }
}

// 2. СПЕЦИАЛЬНЫЕ НАСТРОЙКИ ТОЛЬКО ДЛЯ PIE CHART (С топ-5 объектами)
const reviewsByCategoryChartOptions = {
  ...chartOptions, // Копируем базовые стили
  plugins: {
    ...chartOptions.plugins,
    tooltip: {
      ...chartOptions.plugins.tooltip,
      callbacks: {
        // ⚠️ ЭТО ТОЛЬКО ДЛЯ ОТЗЫВОВ ПО КАТЕГОРИЯМ
        afterBody: function(context) {
          const index = context[0].dataIndex
          const category = reviewsByCategory.value[index]
          
          if (!category || !category.top_objects || category.top_objects.length === 0) {
            return []
          }
          
          const lines = [''] // Отступ
          lines.push('📍 Топ-5 объектов:')
          
          category.top_objects.forEach((obj, idx) => {
            const name = obj.name && obj.name.trim() ? 
              (obj.name.length > 20 ? obj.name.slice(0, 20) + '...' : obj.name) : 
              'Без названия'
            const type = obj.type || 'Не указан'
            lines.push(`  ${idx + 1}. ${name} (${obj.count}) (${type})`)
          })
          
          return lines
        }
      }
    }
  }
}

const timelineChartOptions = {
  ...chartOptions,
  plugins: {
    ...chartOptions.plugins,
    legend: { position: 'top' }
  },
  scales: {
    x: { 
      ticks: { 
        font: { family: 'Inter', size: 9 },
        maxRotation: 45,
        minRotation: 45
      },
      grid: { color: 'rgba(0,0,0,0.05)' }
    },
    y: { beginAtZero: true, ticks: { font: { family: 'Inter', size: 10 } }, grid: { color: 'rgba(0,0,0,0.05)' } }
  }
}

// ===== Данные для графиков =====
const objectsByTypeChart = computed(() => ({
  labels: objectsByType.value.slice(0, 8).map(i => i.label),
  datasets: [{
    label: 'Объектов',
    data: objectsByType.value.slice(0, 8).map(i => i.value),
    backgroundColor: chartColors.primary,
    borderRadius: 6
  }]
}))

const reviewsByCategoryChart = computed(() => ({
  labels: reviewsByCategory.value.map(i => i.label),
  datasets: [{
    data: reviewsByCategory.value.map(i => i.value),
    backgroundColor: [chartColors.danger, chartColors.info, chartColors.success],
    borderWidth: 2,
    borderColor: '#fff'
  }]
}))

const topFavoritedChart = computed(() => ({
  labels: topFavorited.value.slice(0, 10).map(i => i.name.length > 25 ? i.name.slice(0, 25) + '...' : i.name),
  datasets: [{
    label: 'В избранном',
    data: topFavorited.value.slice(0, 10).map(i => i.favorites),
    backgroundColor: chartColors.primary,
    borderRadius: 4
  }]
}))

const ratingDistributionChart = computed(() => ({
  labels: ratingDistribution.value.map(i => `${i.rating}★`),
  datasets: [{
    data: ratingDistribution.value.map(i => i.count),
    backgroundColor: [
      chartColors.danger, '#f97316', chartColors.warning, chartColors.primaryLight, chartColors.primary
    ],
    borderWidth: 2,
    borderColor: '#fff'
  }]
}))

const topReviewedChart = computed(() => ({
  labels: topReviewed.value.slice(0, 10).map(i => i.name.length > 25 ? i.name.slice(0, 25) + '...' : i.name),
  datasets: [{
    label: 'Отзывов',
    data: topReviewed.value.slice(0, 10).map(i => i.reviews),
    backgroundColor: chartColors.info,
    borderRadius: 4
  }]
}))

const activityTimelineChart = computed(() => {
  const dates = activityTimeline.value.map(i => new Date(i.date).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' }))
  return {
    labels: dates,
    datasets: [
      {
        label: 'Новые объекты',
        data: activityTimeline.value.map(i => i.objects),
        borderColor: chartColors.primary,
        backgroundColor: chartColors.bg,
        fill: true,
        tension: 0.4
      },
      {
        label: 'Новые отзывы',
        data: activityTimeline.value.map(i => i.reviews),
        borderColor: chartColors.info,
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      }
    ]
  }
})

const favoriteTypesData = computed(() => favoriteTypes.value.slice(0, 10))

// ===== Загрузка данных =====
const loadAllStats = async () => {
  loading.value = true
  error.value = null
  
  try {
    const [
      baseStats,
      byType,
      byCategory,
      favObjects,
      favTypes,
      ratings,
      reviewed,
      timeline
    ] = await Promise.all([
      api.get('/api/stats'),
      api.get('/api/stats/objects-by-type'),
      api.get('/api/stats/reviews-by-category'),
      api.get('/api/stats/top-favorited-objects?limit=10'),
      api.get('/api/stats/favorite-types'),
      api.get('/api/stats/rating-distribution'),
      api.get('/api/stats/top-reviewed-objects?limit=10'),
      api.get('/api/stats/activity-timeline?days=30')
    ])
    
    stats.value = baseStats.data
    objectsByType.value = byType.data
    reviewsByCategory.value = byCategory.data
    topFavorited.value = favObjects.data
    favoriteTypes.value = favTypes.data
    ratingDistribution.value = ratings.data
    topReviewed.value = reviewed.data
    activityTimeline.value = timeline.data
    
    // Считаем общее количество в избранном
    favoriteStats.value.total = favTypes.data.reduce((sum, i) => sum + i.value, 0)
    
  } catch (err) {
    console.error('[Statistics] Error:', err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить статистику'
  } finally {
    loading.value = false
  }
}

// ===== МОНТАЖ =====
onMounted(() => {
  loadAllStats()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ===== БАЗОВЫЕ СТИЛИ ===== */
.statistics-page {
  min-height: 100vh;
  background: transparent;
  padding: 42px 120px 100px 120px;
  font-family: Inter, system-ui, sans-serif;
  color: #1a1a1a;
}

/* ===== ЗАГОЛОВОК ===== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  align-content: center;
  gap: 20px;
  margin-bottom: 24px;
  padding: 24px 32px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(22, 143, 4, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
}

.page-title {
  margin: 0;
  font-size: 23px;
  font-weight: 800;
  color: rgb(30, 101, 21);
}

.page-subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #64748b;
  max-width: 500px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.period-select :deep(.p-dropdown) {
  min-width: 180px;
  border-radius: 12px !important;
}

/* ===== ЗАГРУЗКА / ОШИБКА ===== */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(22, 143, 4, 0.2);
}

.loading-state span,
.error-state span {
  margin: 20px 0;
  font-size: 15px;
  color: #64748b;
}

.error-state {
  border-color: #fecaca;
  background: rgba(254, 242, 242, 0.9);
}

.error-state i {
  font-size: 2.5rem;
  color: #dc2626;
}

/* ===== ДАШБОРД ===== */
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* Карточки метрик */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 50px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(22, 143, 4, 0.2);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(22, 143, 4, 0.15);
}

.metric-card.primary .metric-icon { background: rgba(22, 143, 4, 0.15); color: #168f04; }
.metric-card.warning .metric-icon { background: rgba(239, 68, 68, 0.15); color: #dc2626; }
.metric-card.info .metric-icon { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
.metric-card.success .metric-icon { background: rgba(16, 185, 129, 0.15); color: #10b981; }

.metric-icon {
  flex: 0 0 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  font-size: 1.5rem;
}

.metric-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-value {
  font-size: 26px;
  font-weight: 800;
  color: #1a1a1a;
  line-height: 1.1;
}

.metric-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

/* ===== ГРАФИКИ ===== */
.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.chart-card {
  padding: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(22, 143, 4, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
}

.chart-card.wide { grid-column: 1 / -1; }
.chart-card.full-width { grid-column: 1 / -1; }

.chart-title {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 700;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-card :deep(canvas) {
  max-height: 300px;
}

/* ===== ТАБЛИЦА ===== */
.table-card {
  padding: 24px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  border: 1px solid rgba(22, 143, 4, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
}

.stats-table {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-header {
  display: grid;
  grid-template-columns: 1000px 0px 0px 0px;
  gap: 12px;
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  border-bottom: 2px solid #e2e8f0;
}

.table-row {
  display: grid;
  grid-template-columns: 40px 1fr 80px 100px;
  gap: 12px;
  align-items: center;
  padding: 14px 16px;
  background: #f8fafc;
  border-radius: 10px;
  transition: all 0.2s ease;
}

.table-row:hover {
  background: #f1f5f9;
  transform: translateX(4px);
}

.rank {
  font-weight: 700;
  color: #168f04;
  background: rgba(22, 143, 4, 0.1);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  text-align: center;
}

.type-name {
  font-weight: 600;
  color: #334155;
}

.count {
  font-weight: 700;
  color: #1a1a1a;
  text-align: right;
}

.progress-bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #168f04, #22c55e);
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* ===== СТИЛИ ДЛЯ PRIMEVUE ===== */
:deep(.p-button) {
  border-radius: 10px !important;
  font-weight: 600 !important;
}

:deep(.p-button:not(.p-button-secondary)) {
  background: linear-gradient(135deg, #168f04, #007306) !important;
}

:deep(.p-dropdown) {
  border-radius: 12px !important;
}

/* ===== АДАПТИВ ===== */
@media (max-width: 1024px) {
  .statistics-page { padding: 16px; }
  
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-controls {
    justify-content: flex-end;
  }
  
  .charts-row {
    grid-template-columns: 1fr;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 40px 1fr 70px;
  }
  
  .table-header span:last-child,
  .table-row .progress-bar {
    display: none;
  }
}

</style>