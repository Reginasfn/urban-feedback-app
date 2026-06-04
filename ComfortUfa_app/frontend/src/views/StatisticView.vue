<!-- src/views/StatisticsView.vue -->
<template>
  <div class="statistics-page">
    <div class="page-header">
      <h1 class="page-title">Статистика платформы</h1>
      <p class="page-subtitle">Аналитика объектов, отзывов и активности пользователей</p>
      
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

    <div v-if="loading" class="loading-state">
      <ProgressSpinner style="width: 60px; height: 60px" />
      <span>Загружаем аналитику...</span>
    </div>

    <div v-else-if="error" class="error-state">
      <i class="pi pi-exclamation-triangle"></i>
      <span>{{ error }}</span>
      <Button label="Повторить" severity="success" @click="loadAllStats" />
    </div>

    <div v-else class="dashboard">
      
      <div class="metrics-grid">
        <div class="metric-card primary" @click="toggleObjectsPopover">
          <div class="metric-icon"><i class="pi pi-map-marker"></i></div>
          <div class="metric-content">
            <span class="metric-value">{{ stats.total_objects?.toLocaleString('ru-RU') || '0' }}</span>
            <span class="metric-label">Всего объектов</span>
          </div>
          
          <Popover ref="objectsPopover" class="objects-popover">
            <div class="popover-header">
              <i class="pi pi-map-marker"></i>
              <span>Объекты по типам</span>
            </div>
            <div class="objects-list">
              <div 
                v-for="(item, index) in objectsByTypeDetails" 
                :key="index"
                class="object-item"
              >
                <div class="object-info">
                  <span class="object-name">{{ item.name }}</span>
                  <span class="object-count">{{ item.count }}</span>
                </div>
                <div class="object-bar">
                  <div 
                    class="object-fill" 
                    :style="{ width: item.percentage + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </Popover>
        </div>
        
        <div class="metric-card warning" @click="toggleProblemsPopover">
          <div class="metric-icon"><i class="pi pi-exclamation-triangle"></i></div>
          <div class="metric-content">
            <span class="metric-value">{{ stats.total_problems?.toLocaleString('ru-RU') || '0' }}</span>
            <span class="metric-label">Сообщено проблем</span>
          </div>
          
          <Popover ref="problemsPopover" class="problems-popover">
            <div class="popover-header">
              <i class="pi pi-exclamation-triangle"></i>
              <span>Детализация проблем</span>
            </div>
            <div class="problems-list">
              <div 
                v-for="(problem, index) in problemDetails" 
                :key="index"
                class="problem-item"
              >
                <div class="problem-info">
                  <span class="problem-name">{{ problem.name }}</span>
                  <span class="problem-count">{{ problem.count }}</span>
                </div>
                <div class="problem-bar">
                  <div 
                    class="problem-fill" 
                    :style="{ width: problem.percentage + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </Popover>
        </div>
        
        <div class="metric-card info">
          <div class="metric-icon"><i class="pi pi-users"></i></div>
          <div class="metric-content">
            <span class="metric-value">{{ stats.total_users?.toLocaleString('ru-RU') || '0' }}</span>
            <span class="metric-label">Пользователей</span>
          </div>
        </div>
        <div class="metric-card success" @click="toggleFavoritesPopover">
          <div class="metric-icon"><i class="pi pi-heart"></i></div>
          <div class="metric-content">
            <span class="metric-value">{{ favoriteStats?.total || '0' }}</span>
            <span class="metric-label">В избранном</span>
          </div>
          
          <Popover ref="favoritesPopover" class="favorites-popover">
            <div class="popover-header">
              <i class="pi pi-heart"></i>
              <span>Объекты в избранном по типам</span>
            </div>
            <div class="favorites-list">
              <div 
                v-for="(item, index) in favoritesByTypeDetails" 
                :key="index"
                class="favorite-item"
              >
                <div class="favorite-info">
                  <span class="favorite-name">{{ item.name }}</span>
                  <span class="favorite-count">{{ item.count }}</span>
                </div>
                <div class="favorite-bar">
                  <div 
                    class="favorite-fill" 
                    :style="{ width: item.percentage + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </Popover>
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-card">
          <h3 class="chart-title">Объекты по типам</h3>
          <Bar :data="objectsByTypeChart" :options="chartOptions" />
        </div>
        
        <div class="chart-card">
          <h3 class="chart-title">Отзывы по категориям</h3>
          <Pie :data="reviewsByCategoryChart" :options="reviewsByCategoryChartOptions" />
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-card wide">
          <h3 class="chart-title">Топ объектов в избранном</h3>
          <Bar :data="topFavoritedChart" :options="{ ...chartOptions, indexAxis: 'y' }" />
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-card">
          <h3 class="chart-title">Распределение оценок</h3>
          <Doughnut :data="ratingDistributionChart" :options="ratingDistributionChartOptions" />
        </div>
        
        <div class="chart-card">
          <h3 class="chart-title">Топ объектов по отзывам</h3>
          <Bar :data="topReviewedChart" :options="{ ...chartOptions, indexAxis: 'y' }" />
        </div>
      </div>

      <div class="chart-card full-width">
        <h3 class="chart-title">Активность за период</h3>
        <Line :data="activityTimelineChart" :options="timelineChartOptions" />
      </div>

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
import Popover from 'primevue/popover'
import api from '@/services/api'

ChartJS.register(
  CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend,
  ArcElement, PointElement, LineElement, Filler
)

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

const objectsPopover = ref(null)
const problemsPopover = ref(null)
const favoritesPopover = ref(null)

const periodOptions = [
  { label: 'За всё время', value: 'all' },
  { label: 'За месяц', value: 'month' },
  { label: 'За неделю', value: 'week' }
]

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
    }
  },
  scales: {
    x: { ticks: { font: { family: 'Inter', size: 10 } }, grid: { color: 'rgba(0,0,0,0.05)' } },
    y: { beginAtZero: true, ticks: { font: { family: 'Inter', size: 10 } }, grid: { color: 'rgba(0,0,0,0.05)' } }
  }
}

const reviewsByCategoryChartOptions = {
  ...chartOptions,
  plugins: {
    ...chartOptions.plugins,
    tooltip: {
      ...chartOptions.plugins.tooltip,
      callbacks: {
        afterBody: function(context) {
          const index = context[0].dataIndex
          const category = reviewsByCategory.value[index]
          
          if (!category || !category.top_objects || category.top_objects.length === 0) {
            return []
          }
          
          const lines = ['']
          lines.push('Топ-5 объектов:')
          
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

const ratingDistributionChartOptions = {
  ...chartOptions,
  plugins: {
    ...chartOptions.plugins,
    tooltip: {
      ...chartOptions.plugins.tooltip,
      callbacks: {
        afterBody: function(context) {
          const index = context[0].dataIndex
          const ratingData = ratingDistribution.value[index]
          
          if (!ratingData || !ratingData.top_types || ratingData.top_types.length === 0) {
            return []
          }
          
          const lines = ['']
          lines.push('Топ-5 типов объектов:')
          
          ratingData.top_types.forEach((item, idx) => {
            lines.push(`  ${idx + 1}. ${item.type} (${item.count})`)
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
  labels: ratingDistribution.value.map(i => `${i.rating}.0 ★`),
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

const objectsByTypeDetails = computed(() => {
  if (!objectsByType.value.length) return []
  
  const total = objectsByType.value.reduce((sum, item) => sum + item.value, 0)
  
  return objectsByType.value
    .slice(0, 8)
    .map(item => ({
      name: item.label,
      count: item.value,
      percentage: total > 0 ? Math.round((item.value / total) * 100) : 0
    }))
    .sort((a, b) => b.count - a.count)
})

const problemDetails = computed(() => {
  const problemCategory = reviewsByCategory.value.find(c => c.label === 'Проблема')
  if (!problemCategory || !problemCategory.top_objects) return []
  
  const grouped = {}
  problemCategory.top_objects.forEach(obj => {
    const type = obj.type || 'Не указан'
    if (grouped[type]) {
      grouped[type] += obj.count
    } else {
      grouped[type] = obj.count
    }
  })
  
  const total = Object.values(grouped).reduce((sum, count) => sum + count, 0)
  
  return Object.entries(grouped)
    .map(([name, count]) => ({
      name,
      count,
      percentage: total > 0 ? Math.round((count / total) * 100) : 0
    }))
    .sort((a, b) => b.count - a.count)
})

const favoritesByTypeDetails = computed(() => {
  if (!favoriteTypes.value.length) return []
  
  const total = favoriteStats.value.total || 0
  
  return favoriteTypes.value
    .slice(0, 8)
    .map(item => ({
      name: item.label,
      count: item.value,
      percentage: total > 0 ? Math.round((item.value / total) * 100) : 0
    }))
    .sort((a, b) => b.count - a.count)
})

const toggleObjectsPopover = (event) => {
  if (objectsPopover.value) {
    objectsPopover.value.toggle(event)
  }
}

const toggleProblemsPopover = (event) => {
  if (problemsPopover.value) {
    problemsPopover.value.toggle(event)
  }
}

const toggleFavoritesPopover = (event) => {
  if (favoritesPopover.value) {
    favoritesPopover.value.toggle(event)
  }
}

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
    
    favoriteStats.value.total = favTypes.data.reduce((sum, i) => sum + i.value, 0)
    
  } catch (err) {
    console.error('[Statistics] Error:', err)
    error.value = err.response?.data?.detail || 'Не удалось загрузить статистику'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAllStats()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.statistics-page {
  min-height: 100vh;
  background: transparent;
  padding: 42px 120px 100px 120px;
  font-family: Inter, system-ui, sans-serif;
  color: #1a1a1a;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.dashboard {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

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

.metric-card.primary,
.metric-card.warning,
.metric-card.success {
  cursor: pointer;
}

.metric-card.primary:hover {
  box-shadow: 0 12px 40px rgba(22, 143, 4, 0.2);
}

.metric-card.warning:hover {
  box-shadow: 0 12px 40px rgba(239, 68, 68, 0.2);
}

.metric-card.success:hover {
  box-shadow: 0 12px 40px rgba(16, 185, 129, 0.2);
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

.objects-popover :deep(.p-popover-content),
.problems-popover :deep(.p-popover-content),
.favorites-popover :deep(.p-popover-content) {
  padding: 0 !important;
  border-radius: 12px !important;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15) !important;
  overflow: hidden;
  width: 320px !important;
}

.objects-popover :deep(.p-popover-content) {
  border: 1px solid rgba(22, 143, 4, 0.2) !important;
}

.problems-popover :deep(.p-popover-content) {
  border: 1px solid rgba(239, 68, 68, 0.2) !important;
}

.favorites-popover :deep(.p-popover-content) {
  border: 1px solid rgba(16, 185, 129, 0.2) !important;
}

.popover-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  font-weight: 600;
  font-size: 15px;
}

.objects-popover .popover-header {
  background: rgba(22, 143, 4, 0.1);
  border-bottom: 1px solid rgba(22, 143, 4, 0.2);
  color: #168f04;
}

.problems-popover .popover-header {
  background: rgba(239, 68, 68, 0.1);
  border-bottom: 1px solid rgba(239, 68, 68, 0.2);
  color: #dc2626;
}

.favorites-popover .popover-header {
  background: rgba(16, 185, 129, 0.1);
  border-bottom: 1px solid rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.popover-header i {
  font-size: 18px;
}

.objects-list,
.problems-list,
.favorites-list {
  padding: 12px 20px;
  max-height: 280px;
  overflow-y: auto;
}

.object-item,
.problem-item,
.favorite-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 0;
  border-bottom: 1px dashed rgba(0, 0, 0, 0.1);
}

.object-item:last-child,
.problem-item:last-child,
.favorite-item:last-child {
  border-bottom: none;
}

.object-info,
.problem-info,
.favorite-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.object-name,
.problem-name,
.favorite-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
}

.object-count,
.problem-count,
.favorite-count {
  font-size: 15px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 20px;
  min-width: 32px;
  text-align: center;
}

.object-count {
  color: #168f04;
  background: rgba(22, 143, 4, 0.1);
}

.problem-count {
  color: #dc2626;
  background: rgba(239, 68, 68, 0.1);
}

.favorite-count {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.object-bar,
.problem-bar,
.favorite-bar {
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.object-fill {
  height: 100%;
  background: linear-gradient(90deg, #168f04, #22c55e);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.problem-fill {
  height: 100%;
  background: linear-gradient(90deg, #dc2626, #f97316);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.favorite-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #34d399);
  border-radius: 4px;
  transition: width 0.5s ease;
}

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

:deep(.p-popover) {
  z-index: 1000 !important;
}

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
  
  .objects-popover :deep(.p-popover-content),
  .problems-popover :deep(.p-popover-content),
  .favorites-popover :deep(.p-popover-content) {
    width: 280px !important;
  }
}
</style>