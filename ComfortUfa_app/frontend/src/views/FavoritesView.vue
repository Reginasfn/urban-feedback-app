<!-- src/views/FavoritesView.vue -->
<template>
  <div class="favorites-page">
    <!-- ===== ХЕДЕР ===== -->
    <div class="favorites-header">
      <Button 
        class="back-btn" 
        @click="$router.back()" 
        title="Назад"
        icon="pi pi-arrow-left"
        text
        rounded
      />
      <h1 class="page-title">Избранные места</h1>
      <div class="header-actions">
        <Button 
          v-if="favorites.length > 0" 
          class="clear-all-btn" 
          @click="clearAllFavorites"
          icon="pi pi-trash"
          label="Очистить всё"
          severity="danger"
          text
          size="small"
        />
      </div>
    </div>

    <!-- ===== ЗАГРУЗКА ===== -->
    <div v-if="loading" class="loading-state">
      <ProgressSpinner style="width: 50px; height: 50px" />
      <span>Загружаем избранное...</span>
    </div>

    <!-- ===== ПУСТО ===== -->
    <div v-else-if="favorites.length === 0" class="empty-state">
      <i class="pi pi-heart" style="font-size: 3rem; color: var(--p-primary-color)"></i>
      <h3>Пока пусто</h3>
      <p>Добавляйте места в избранное на карте — они появятся здесь</p>
      <Button 
        class="go-to-map-btn" 
        @click="$router.push('/map')"
        icon="pi pi-map"
        label="Перейти к карте"
        severity="success"
      />
    </div>

    <!-- ===== СПИСОК КАРТОЧЕК ===== -->
    <div v-else class="favorites-list">
      <Card 
        v-for="obj in favorites" 
        :key="obj.id_object" 
        class="favorite-card"
      >
        <template #content>
          <div class="card-inner">
            <!-- Левая часть: иконка типа -->
            <div class="card-icon">
              <i :class="getTypeIcon(obj.type_name)"></i>
            </div>
            
            <!-- Центральная часть: контент -->
            <div class="card-body">
              <div class="card-top">
                <span class="card-type">{{ obj.type_name }}</span>
                <h3 class="card-name">{{ obj.name }}</h3>
              </div>
              
              <p v-if="obj.address" class="card-address">
                <i class="pi pi-map-marker"></i> {{ obj.address }}
              </p>
              
              <!-- Рейтинг -->
              <div v-if="obj.rating_avg !== null" class="card-rating">
                <i class="pi pi-star-fill"></i>
                <span>{{ obj.rating_avg.toFixed(1) }}</span>
                <span class="rating-count" v-if="obj.rating_count">
                  ({{ obj.rating_count }} оценок)
                </span>
              </div>
              <div v-else class="card-rating no-rating">
                <i class="pi pi-star"></i>
                <span>Пока нет оценок</span>
              </div>
            </div>
            
            <!-- Правая часть: 3 кнопки -->
            <div class="card-actions">
              <Button 
                class="btn-action btn-map" 
                @click="showOnMap(obj)"
                icon="pi pi-map"
                label="На карте"
                severity="success"
                size="small"
              />
              <Button 
                class="btn-action btn-details" 
                @click="openDetailsModal(obj)"
                icon="pi pi-info-circle"
                label="Подробнее"
                severity="secondary"
                outlined
                size="small"
              />
              <!-- Кнопка убрать из избранного (как в примере с bookmark) -->
              <button 
                class="bookmark-btn active" 
                @click="removeFromFavorites(obj.id_object)"
                title="Убрать из избранного"
              >
                <i class="pi pi-bookmark-fill"></i>
              </button>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- ===== МОДАЛЬНОЕ ОКНО ДЕТАЛЕЙ ОБЪЕКТА ===== -->
    <ObjectDetailsModal
        v-if="modalObject"
        :object="modalObject"
        :visible="!!modalObject"
        @update:visible="val => { if (!val) modalObject = null }"
        @review-submitted="onReviewSubmitted"
        @go-to-map="showOnMap"
    />

    <!-- ===== TOAST ===== -->
    <Toast position="top-center" group="favorites" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import api from '@/services/api'
import { isAuthenticated } from '@/utils/auth'
import ObjectDetailsModal from '@/components/modals/ObjectDetailsModal.vue'

const router = useRouter()
const toast = useToast()
const favorites = ref([])
const loading = ref(true)
const modalObject = ref(null)

// ===== ИКОНКИ ПО ТИПАМ ОБЪЕКТОВ =====
const getTypeIcon = (typeName) => {
  const typeMap = {
    'кафе': 'pi pi-coffee',
    'ресторан': 'pi pi-utensils',
    'парк': 'pi pi-tree',
    'музей': 'pi pi-landmark',
    'отель': 'pi pi-building',
    'магазин': 'pi pi-shopping-bag',
    'аптека': 'pi pi-bolt',
    'больница': 'pi pi-heart',
    'заправка': 'pi pi-gas-pump',
    'парковка': 'pi pi-car',
  }
  const key = Object.keys(typeMap).find(k => typeName?.toLowerCase().includes(k))
  return typeMap[key] || 'pi pi-map-marker'
}

// ===== ЗАГРУЗКА ИЗБРАННОГО =====
const loadFavorites = async () => {
  if (!isAuthenticated()) {
    router.push('/auth')
    return
  }

  loading.value = true

  try {
    const idsResp = await api.get('/api/objects/me/favorites/ids')
    const favoriteIds = idsResp.data.favorite_ids || []

    if (favoriteIds.length === 0) {
      favorites.value = []
      loading.value = false
      return
    }

    const objectsResp = await api.get('/api/objects', {
      params: {
        bookmarked_ids: favoriteIds.join(','),
        limit: 1000
      }
    })

    favorites.value = objectsResp.data || []
    
  } catch (err) {
    console.error('[Favorites] Error loading:', err)
    toast.add({
      group: 'favorites',
      severity: 'error',
      summary: 'Ошибка',
      detail: err.response?.data?.detail || 'Не удалось загрузить избранное',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

// ===== УДАЛЕНИЕ ИЗ ИЗБРАННОГО =====
const removeFromFavorites = async (objectId) => {
  const numericId = Number(objectId)
  
  try {
    await api.delete(`/api/objects/${numericId}/favorite`)
    
    favorites.value = favorites.value.filter(o => o.id_object !== numericId)
    
    if (window.__toggleBookmark) {
      window.__toggleBookmark(numericId, null)
    }
    
    window.dispatchEvent(new CustomEvent('favorites-updated', { 
      detail: { removedId: numericId } 
    }))
    
    toast.add({
      group: 'favorites',
      severity: 'success',
      summary: 'Готово',
      detail: 'Убрано из избранного',
      life: 2000
    })
    
  } catch (err) {
    console.error('[Favorites] Error removing:', err)
    toast.add({
      group: 'favorites',
      severity: 'error',
      summary: 'Ошибка',
      detail: err.response?.data?.detail || 'Не удалось удалить',
      life: 3000
    })
  }
}

// ===== ОЧИСТИТЬ ВСЁ =====
const clearAllFavorites = async () => {
  if (!confirm('Уверены, что хотите очистить всё избранное?')) return
  
  try {
    const removePromises = favorites.value.map(obj => 
      api.delete(`/api/objects/${obj.id_object}/favorite`).catch(() => {})
    )
    await Promise.all(removePromises)
    
    favorites.value = []
    window.dispatchEvent(new CustomEvent('favorites-cleared'))
    
    toast.add({
      group: 'favorites',
      severity: 'success',
      summary: 'Готово',
      detail: 'Избранное очищено',
      life: 2000
    })
    
  } catch (err) {
    console.error('[Favorites] Error clearing:', err)
    toast.add({
      group: 'favorites',
      severity: 'error',
      summary: 'Ошибка',
      detail: 'Не удалось очистить избранное',
      life: 3000
    })
  }
}

// ===== ПОКАЗАТЬ НА КАРТЕ =====
const showOnMap = (obj) => {
  router.push({
    path: '/map',
    query: { 
      focus: `${obj.coords[0]},${obj.coords[1]}`,
      zoom: 16,
      id: obj.id_object
    }
  })
}

// ===== ОТКРЫТЬ МОДАЛКУ ДЕТАЛЕЙ =====
const openDetailsModal = (obj) => {
  modalObject.value = obj
}

// ===== ЗАКРЫТЬ МОДАЛКУ =====
const closeDetailsModal = () => {
  modalObject.value = null
}

// ===== ОБНОВЛЕНИЕ ПОСЛЕ ОТЗЫВА =====
const onReviewSubmitted = (updatedObj) => {
  // Обновляем данные в списке, если объект ещё в избранном
  const idx = favorites.value.findIndex(o => o.id_object === updatedObj.id_object)
  if (idx !== -1) {
    favorites.value[idx] = { ...favorites.value[idx], ...updatedObj }
  }
  toast.add({
    group: 'favorites',
    severity: 'success',
    summary: 'Готово',
    detail: 'Отзыв отправлен',
    life: 2000
  })
}

// ===== МОНТАЖ =====
onMounted(() => {
  loadFavorites()
})
</script>

<style scoped>
/* ===== БАЗОВЫЕ СТИЛИ ===== */
.favorites-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #ecfdf5 100%);
  padding: 24px;
  font-family: var(--font-family, Inter, system-ui, -apple-system, sans-serif);
  color: var(--text-color, #1a1a1a);
}

/* ===== ХЕДЕР ===== */
.favorites-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(22, 143, 4, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
}

.page-title {
  flex: 1;
  font-size: 20px;
  font-weight: 700;
  color: var(--p-primary-color, #168f04);
  margin: 0;
}

/* ===== ЗАГРУЗКА / ПУСТО ===== */
.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(22, 143, 4, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
}

.loading-state span {
  margin-top: 16px;
  font-size: 14px;
  color: var(--text-color-secondary, #64748b);
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 16px 0 8px 0;
}

.empty-state p {
  font-size: 13px;
  color: var(--text-color-secondary, #64748b);
  margin: 0 0 20px 0;
  max-width: 280px;
}

/* ===== СПИСОК КАРТОЧЕК ===== */
.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 40px;
}

/* ===== КАРТОЧКА ===== */
.favorite-card {
  width: 100%;
  max-width: 1200px; /* УВЕЛИЧЕНО до 1200px */
  margin: 0 auto;
  border-radius: 12px;
  border: 1px solid rgba(22, 143, 4, 0.2);
  transition: all 0.2s ease;
}

.favorite-card:hover {
  border-color: rgba(22, 143, 4, 0.4);
  box-shadow: 0 8px 32px rgba(22, 143, 4, 0.12);
}

.favorite-card :deep(.p-card-content) {
  padding: 0;
}

.card-inner {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px 24px;
}

/* Иконка типа */
.card-icon {
  flex: 0 0 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(22, 143, 4, 0.1);
  border-radius: 16px;
  color: var(--p-primary-color, #168f04);
  font-size: 2rem;
}

/* Тело карточки */
.card-body {
  flex: 1;
  min-width: 0;
}

.card-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.card-type {
  font-size: 11px;
  font-weight: 700;
  color: var(--p-primary-color, #168f04);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: rgba(22, 143, 4, 0.15);
  padding: 4px 12px;
  border-radius: 20px;
  white-space: nowrap;
}

.card-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color, #1a1a1a);
  margin: 0;
  line-height: 1.3;
}

.card-address {
  font-size: 14px;
  color: var(--text-color-secondary, #64748b);
  margin: 8px 0 0 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.card-rating {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--p-amber-500, #f59e0b);
}

.card-rating.no-rating {
  color: var(--text-color-secondary, #94a3b8);
}

.card-rating i {
  font-size: 14px;
}

.rating-count {
  font-size: 12px;
  color: var(--text-color-secondary, #94a3b8);
  font-weight: 400;
}

/* ===== КНОПКИ ДЕЙСТВИЙ ===== */
.card-actions {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-action {
  min-width: 110px;
}

/* ===== КНОПКА ЗАКЛАДКИ (как в примере) ===== */
.bookmark-btn {
  width: 44px;
  height: 44px;
  border: 2px solid #fecaca;
  background: rgba(220, 38, 38, 0.08);
  border-radius: 12px;
  color: #dc2626;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  transition: all 0.2s ease;
  padding: 0;
}

.bookmark-btn:hover {
  background: rgba(220, 38, 38, 0.15);
  border-color: #f87171;
  transform: scale(1.05);
}

.bookmark-btn:active {
  transform: scale(0.98);
}

.bookmark-btn i {
  pointer-events: none;
}

/* ===== АДАПТИВ ===== */
@media (max-width: 1024px) {
  .favorite-card {
    max-width: 100%;
  }
  
  .card-inner {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .card-icon {
    flex: 0 0 64px;
    height: 64px;
    font-size: 1.75rem;
  }
  
  .card-body {
    flex: 1 1 calc(100% - 90px);
  }
  
  .card-actions {
    width: 100%;
    justify-content: flex-end;
    padding-top: 8px;
    border-top: 1px solid rgba(0, 0, 0, 0.06);
  }
}

@media (max-width: 768px) {
  .favorites-page {
    padding: 16px;
  }
  
  .favorites-header {
    flex-wrap: wrap;
    padding: 12px 16px;
  }
  
  .page-title {
    font-size: 18px;
    order: 3;
    width: 100%;
    margin-top: 12px;
    text-align: center;
  }
  
  .card-inner {
    padding: 16px;
  }
  
  .card-name {
    font-size: 16px;
  }
  
  .card-actions {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .btn-action {
    flex: 1;
    min-width: auto;
    max-width: 140px;
  }
  
  .bookmark-btn {
    width: 40px;
    height: 40px;
  }
}

@media (max-width: 480px) {
  .card-icon {
    flex: 0 0 56px;
    height: 56px;
    font-size: 1.5rem;
  }
  
  .card-name {
    font-size: 15px;
  }
  
  .card-address {
    font-size: 13px;
  }
  
  .btn-action {
    --p-button-padding: 6px 10px;
    font-size: 12px;
  }
}
</style>