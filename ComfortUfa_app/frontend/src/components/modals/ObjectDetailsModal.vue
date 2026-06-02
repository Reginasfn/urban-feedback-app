<!-- frontend\src\components\modals\ObjectDetailsModal.vue -->
<template>
  <Dialog
    :visible="visible"
    @update:visible="onUpdateVisible"
    modal
    :header="''"
    :style="{
      width: '1100px',
      maxWidth: '96vw'
    }"
    :contentStyle="{
      minHeight: '780px',
      maxHeight: '88vh',
      overflow: 'hidden'
    }"
    :closable="true"
    :close-on-escape="true"
    :dismissable-mask="true"
    class="object-details-modal"
    style="font-family: Inter, system-ui, sans-serif"
  >
    <div v-if="!object" class="modal-loading">
      <ProgressSpinner style="width: 48px; height: 48px" />
      <p class="loading-text">Загрузка информации...</p>
    </div>

    <div v-else class="details-wrapper">
      <!-- HERO HEADER -->
      <section class="hero-header">
        <div class="hero-title-block">
          <h1 class="hero-title">{{ object.name }}</h1>
        </div>

        <div class="hero-rating">
          <i class="pi pi-star-fill"></i>
          <span v-if="object.rating_avg !== null && object.rating_avg !== undefined">
            {{ Number(object.rating_avg).toFixed(1) }}
          </span>
          <span v-else>Нет оценок</span>
          <small>({{ object.rating_count || 0 }})</small>
        </div>
      </section>

      <!-- OBJECT CARD -->
      <section class="object-card" style="min-width: 1040px;">
        <div class="object-info-row">
          <div class="object-info-left">
            <div class="object-type-badge">
              {{ object.type_name || 'Тип не указан' }}
            </div>

            <div v-if="object.address" class="info-row">
              <i class="pi pi-map-marker"></i>
              <span>{{ object.address }}</span>
            </div>

            <div v-if="object.description" class="description-box">
              {{ object.description }}
            </div>

            <div v-if="object.extra_info" class="extra-grid">
              <div
                v-for="(value, key) in object.extra_info"
                :key="key"
                class="extra-item"
              >
                <span class="extra-label">{{ formatExtraKey(key) }}</span>
                <span class="extra-value">{{ value }}</span>
              </div>
            </div>
          </div>

          <div class="object-info-right">
            <Button
              label="Показать на карте"
              icon="pi pi-map"
              class="btn-map"
              severity="success"
              @click="onGoToMap"
              style="height: 50px; width: 180px;"
            />
          </div>
        </div>
      </section>

      <!-- REVIEWS -->
      <section class="reviews-section">
        <div class="section-header">
          <div>
            <h3>Отзывы</h3>
            <p>{{ reviews.length }} шт.</p>
          </div>

          <Button
            :label="showReviewForm ? 'Скрыть форму' : (props.reviewToEdit?.id_review ? 'Редактировать отзыв' : 'Оставить отзыв')"
            :icon="showReviewForm ? 'pi pi-times' : (props.reviewToEdit?.id_review ? 'pi pi-pencil' : 'pi pi-comment')"
            class="review-btn"
            style="height: 50px; width: 180px;"
            @click="toggleReviewForm"
          />
        </div>

        <!-- 🔥 СТАТИСТИКА ПО КАТЕГОРИЯМ И ОЦЕНКАМ -->
        <div v-if="totalReviews > 0" class="review-stats-wrapper">
          <!-- Категории -->
          <div class="review-stats">
            <div class="stat-item problem" title="Отзывы с категорией 'Проблема'">
              <i class="pi pi-exclamation-triangle"></i>
              <span>Проблемы: <strong>{{ reviewStats.problem }}</strong></span>
            </div>
            <div class="stat-item suggestion" title="Отзывы с категорией 'Предложение'">
              <i class="pi pi-lightbulb"></i>
              <span>Предложения: <strong>{{ reviewStats.suggestion }}</strong></span>
            </div>
            <div class="stat-item praise" title="Отзывы с категорией 'Похвала'">
              <i class="pi pi-thumbs-up"></i>
              <span>Похвала: <strong>{{ reviewStats.praise }}</strong></span>
            </div>
          </div>

          <!-- Двухколоночный layout: оценки + AI сводка -->
          <div class="stats-grid">
            <!-- Оценки (слева) -->
            <div class="rating-stats">
              <div class="rating-stats-title">Распределение оценок:</div>
              <div class="rating-bars">
                <div v-for="star in [5, 4, 3, 2, 1]" :key="star" class="rating-bar-item">
                  <div class="rating-bar-label">
                    <i class="pi pi-star-fill"></i> {{ star }}
                  </div>
                  <div class="rating-bar-track">
                    <div 
                      class="rating-bar-fill" 
                      :style="{ width: totalReviews > 0 ? (ratingStats[star] / totalReviews * 100) + '%' : '0%' }"
                    ></div>
                  </div>
                  <div class="rating-bar-count">{{ ratingStats[star] }}</div>
                </div>
              </div>
            </div>

            <!-- AI сводка (справа) -->
            <div class="ai-summary-card">
              <div class="ai-summary-header">
                <i class="pi pi-sparkles ai-icon"></i>
                <h4>Важное из отзывов</h4>
              </div>

              <div v-if="aiSummaryLoading" class="ai-loading">
                <ProgressSpinner style="width: 32px; height: 32px" />
                <span>Анализируем отзывы...</span>
              </div>

              <div v-else-if="aiSummary" class="ai-summary-content">
                <p class="typing-text">
                  {{ displayedText }}
                  <span v-if="isTyping" class="typing-cursor">|</span>
                </p>
                <div class="ai-footer">
                  <span class="ai-badge">Текст составила нейросеть Gemini</span>
                </div>
              </div>

              <div v-else class="ai-empty">
                <p>Недостаточно отзывов для анализа</p>
              </div>
            </div>

          </div>
        </div>

        <Transition name="slide-fade">
          <div v-if="showReviewForm" class="review-form-card">
            <!-- 🔥 Заголовок формы -->
            <div class="form-title">
              <h4>{{ formTitle }}</h4>
              <p v-if="props.reviewToEdit?.id_review" class="form-subtitle">
                Вы редактируете свой отзыв от {{ formatDate(props.reviewToEdit.created_at) }}
              </p>
            </div>

            <div class="form-group">
              <label class="form-label">Категория отзыва *</label>
              <div class="category-buttons">
                <button
                  v-for="cat in reviewCategories"
                  :key="cat.value"
                  type="button"
                  class="category-btn"
                  :class="{ active: reviewForm.category === cat.value }"
                  @click="reviewForm.category = cat.value"
                >
                  {{ cat.label }}
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Оценка *</label>
              <div class="rating-wrapper">
                <Rating 
                  v-model="reviewForm.rating" 
                  :cancel="false"
                  class="custom-rating"
                  :pt="{
                        icon: { 
                        style: 'width: 40px; height: 40px;' 
                        }
                    }"
                />
                <span class="rating-value">{{ reviewForm.rating }} из 5</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Текст отзыва *</label>
              <Textarea
                v-model="reviewForm.text"
                rows="4"
                autoResize
                class="w-full"
                placeholder="Опишите ваше мнение об объекте..."
              />
              <small class="form-hint">
                Отзывы проходят автоматическую проверку на соответствие правилам (угрозы, дескриминация, спам)
              </small>
            </div>

            <div class="form-group">
              <label class="form-label">Фотографии объекта</label>
              <div class="photo-upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  multiple
                  class="file-input"
                  @change="handleFileSelect"
                />
                <div v-if="reviewForm.photos?.length" class="photo-preview-grid">
                  <div v-for="(photo, index) in reviewForm.photos" :key="index" class="photo-preview-item">
                    <img :src="photo.preview" :alt="photo.name" class="photo-preview" />
                    <button type="button" class="photo-remove-btn" @click.stop="removePhoto(index)">
                      <i class="pi pi-times"></i>
                    </button>
                  </div>
                </div>
                <div v-else class="photo-upload-placeholder">
                  <i class="pi pi-image"></i>
                  <span>Перетащите фото или нажмите для выбора</span>
                  <small>Макс. 5 фото, до 10 МБ каждое</small>
                </div>
              </div>
            </div>

            <div class="form-actions">
              <Button
                label="Отмена"
                severity="secondary"
                text
                @click="cancelReviewForm"
              />
              <Button
                :label="submitButtonText"
                :icon="props.reviewToEdit?.id_review ? 'pi pi-check' : 'pi pi-send'"
                :loading="submittingReview"
                :disabled="!canSubmitReview"
                @click="submitReview"
              />
            </div>
          </div>
        </Transition>

        <div v-if="reviewsLoading" class="reviews-loading">
          <ProgressSpinner style="width: 42px; height: 42px" />
        </div>

        <div v-else-if="reviews.length" class="reviews-list">
          <article
            v-for="review in reviews"
            :key="review.id_review || review.id"
            class="review-card"
          >
            <div class="review-header">
              <Avatar
                :label="getInitials(review.user_name || review.nickname)"
                shape="circle"
                class="review-avatar"
              />

              <div class="review-meta">
                <div class="review-author">
                  {{ review.user_name || review.nickname || 'Пользователь' }}
                </div>

                <div class="review-submeta">
                  <Tag 
                    v-if="review.category_name" 
                    :value="review.category_name" 
                    :severity="getCategoryColor(review.category).severity"
                    :class="getCategoryColor(review.category).class"
                  >
                    {{ review.category_name }}
                  </Tag>

                  <Rating
                    :modelValue="review.rating"
                    readonly
                    :cancel="false"
                  />

                  <span class="review-date">
                    {{ formatDate(review.created_at) }}
                  </span>
                </div>
              </div>
            </div>

            <p class="review-text">{{ review.text }}</p>

            <div v-if="review.photos?.length" class="review-photos">
              <img 
                v-for="(photo, index) in review.photos" 
                :key="index"
                :src="photo.url || photo" 
                :alt="`Фото ${index + 1}`"
                class="review-photo"
                @click="openPhotoViewer(photo.url || photo)"
              />
            </div>
          </article>
        </div>

        <div v-else class="empty-state">
          <i class="pi pi-comments"></i>
          <h4>Пока нет отзывов</h4>
          <p>Будьте первым, кто поделится своим мнением.</p>
        </div>
      </section>
    </div>

    <!-- УВЕДОМЛЕНИЯ -->
    <Toast />
  </Dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import ProgressSpinner from 'primevue/progressspinner'
import Avatar from 'primevue/avatar'
import Rating from 'primevue/rating'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import api from '@/services/api'

import { useToast } from 'primevue/usetoast'
const toast = useToast()

const props = defineProps({
  object: { type: Object, default: null },
  visible: { type: Boolean, default: false },
  reviewToEdit: { type: Object, default: null } 
})

const emit = defineEmits([
  'update:visible', 
  'close', 
  'go-to-map', 
  'review-submitted',
  'review-updated',
  'object-updated'
])

const reviews = ref([])
const reviewsLoading = ref(false)
const showReviewForm = ref(false)
const submittingReview = ref(false)
const fileInput = ref(null)

const reviewCategories = [
  { label: 'Проблема', value: 'problem' },    
  { label: 'Предложение', value: 'suggestion' }, 
  { label: 'Похвала', value: 'praise' }          
]

// Цвета для категорий отзывов
const categoryColors = {
  problem: { severity: 'danger', class: 'category-problem' },
  suggestion: { severity: 'info', class: 'category-suggestion' },
  praise: { severity: 'success', class: 'category-praise' }
}

const getCategoryColor = (categoryValue) => {
  return categoryColors[categoryValue] || { severity: 'secondary', class: '' }
}

// 🔥 Вычисляемые свойства для формы
const submitButtonText = computed(() => 
  props.reviewToEdit?.id_review ? 'Редактировать' : 'Отправить'
)

const formTitle = computed(() => 
  props.reviewToEdit?.id_review ? 'Редактировать отзыв' : 'Оставить отзыв'
)

// 🔥 Статистика по категориям отзывов
const reviewStats = computed(() => {
  const stats = { problem: 0, suggestion: 0, praise: 0 }
  
  if (reviews.value && reviews.value.length > 0) {
    reviews.value.forEach(review => {
      const category = review.category?.toLowerCase()
      if (category === 'problem' || category === 'проблема') {
        stats.problem++
      } else if (category === 'suggestion' || category === 'предложение') {
        stats.suggestion++
      } else if (category === 'praise' || category === 'похвала') {
        stats.praise++
      }
    })
  }
  
  return stats
})

// 🔥 Статистика по оценкам (1-5 звезд)
const ratingStats = computed(() => {
  const stats = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 }
  
  if (reviews.value && reviews.value.length > 0) {
    reviews.value.forEach(review => {
      const rating = Math.round(review.rating)
      if (rating >= 1 && rating <= 5) {
        stats[rating]++
      }
    })
  }
  
  return stats
})

// 🔥 Общее количество отзывов
const totalReviews = computed(() => reviews.value?.length || 0)

// Реактивный счётчик отзывов
const reviewsCount = computed(() => reviews.value.length)

const reviewForm = ref({
  category: null,
  rating: 0,
  text: '',
  photos: []
})

const canSubmitReview = computed(() =>
  reviewForm.value.category &&
  reviewForm.value.rating > 0 &&
  reviewForm.value.text.trim().length >= 5 &&
  !submittingReview.value
)

// 🔥 Переключение формы (открыть/закрыть)
const toggleReviewForm = () => {
  if (showReviewForm.value) {
    // Закрываем форму
    showReviewForm.value = false
    // Сбрасываем форму только если не редактируем
    if (!props.reviewToEdit?.id_review) {
      reviewForm.value = { category: null, rating: 0, text: '', photos: [] }
    }
  } else {
    // Открываем форму
    openReviewForm()
  }
}

// 🔥 Отмена редактирования
const cancelReviewForm = () => {
  showReviewForm.value = false
  // Сбрасываем форму только если не редактируем
  if (!props.reviewToEdit?.id_review) {
    reviewForm.value = { category: null, rating: 0, text: '', photos: [] }
  }
}

const openReviewForm = () => {
  if (props.reviewToEdit?.id_review) {
    // 🔥 Редактирование: предзаполняем форму
    console.log('✏️ Заполняем форму для редактирования:', props.reviewToEdit)
    
    reviewForm.value = {
      category: props.reviewToEdit.category || props.reviewToEdit.category_value || null,
      rating: typeof props.reviewToEdit.rating === 'number' ? props.reviewToEdit.rating : 0,
      text: props.reviewToEdit.text || '',
      photos: []
    }
  } else {
    // 🔥 Новый отзыв: пустая форма
    reviewForm.value = { category: null, rating: 0, text: '', photos: [] }
  }
  showReviewForm.value = true
}

const triggerFileInput = () => fileInput.value?.click()

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  addPhotos(files)
  event.target.value = ''
}

const handleDrop = (event) => {
  const files = Array.from(event.dataTransfer.files || [])
  const imageFiles = files.filter(file => file.type.startsWith('image/'))
  addPhotos(imageFiles)
}

const addPhotos = (files) => {
  const maxPhotos = 5
  const maxSize = 10 * 1024 * 1024
  
  for (const file of files) {
    if (reviewForm.value.photos.length >= maxPhotos) break
    if (file.size > maxSize) continue
    
    const reader = new FileReader()
    reader.onload = (e) => {
      reviewForm.value.photos.push({
        file,
        name: file.name,
        size: file.size,
        preview: e.target.result
      })
    }
    reader.readAsDataURL(file)
  }
}

const removePhoto = (index) => reviewForm.value.photos.splice(index, 1)

// Загрузка отзывов
const loadReviews = async () => {
  if (!props.object?.id_object) return

  reviewsLoading.value = true

  try {
    const response = await api.get(
      `/api/reviews/object/${props.object.id_object}`,
      {
        params: { limit: 50, offset: 0 }
      }
    )

    const data = response.data
    let reviewsData = []
    
    if (Array.isArray(data)) {
      reviewsData = data
    } else if (data?.reviews && Array.isArray(data.reviews)) {
      reviewsData = data.reviews
    } else if (data?.items && Array.isArray(data.items)) {
      reviewsData = data.items
    } else if (data?.data && Array.isArray(data.data)) {
      reviewsData = data.data
    }

    // Словари для категорий
    const categoryLabels = {
      problem: 'Проблема',
      suggestion: 'Предложение',
      praise: 'Похвала'
    }
    const categoryValues = {
      'Проблема': 'problem', 'проблема': 'problem',
      'Предложение': 'suggestion', 'предложение': 'suggestion',
      'Похвала': 'praise', 'похвала': 'praise'
    }

    reviews.value = reviewsData.map(review => {
      let categoryValue = review.category || review.category_value
      if (!categoryValue && review.category_name) {
        categoryValue = categoryValues[review.category_name] || 
                       categoryValues[review.category_name.toLowerCase()] || null
      }
      
      let categoryName = categoryValue ? 
        (categoryLabels[categoryValue] || review.category_name) : 
        review.category_name

      return {
        id: review.id_review || review.id || review.review_id,
        user_name: review.user_name || review.nickname || review.author || 'Пользователь',
        nickname: review.nickname || review.user_name || review.author,
        rating: review.rating !== undefined ? review.rating : 0,
        text: review.text || review.comment || review.content || '',
        created_at: review.created_at || review.date || review.timestamp,
        category: categoryValue,
        category_name: categoryName,
        photos: review.photos || review.images || [],
        ...review
      }
    })

  } catch (error) {
    console.error('[LoadReviews] Error:', error)
    reviews.value = []
  } finally {
    reviewsLoading.value = false
  }
}

// Обновление данных объекта
const refreshObjectData = async () => {
  if (!props.object?.id_object) return
  try {
    const response = await api.get(`/api/objects/${props.object.id_object}`)
    emit('object-updated', response.data)
  } catch (error) {
    console.error('[ObjectDetails] Error refreshing object:', error)
  }
}

// Отправка отзыва с обработкой модерации
const submitReview = async () => {
  if (!props.object?.id_object) return
  submittingReview.value = true
  
  try {
    const token = localStorage.getItem('auth_token') || ''
    
    if (props.reviewToEdit?.id_review) {
      // 🔥 ОБНОВЛЕНИЕ существующего отзыва (PUT)
      console.log('✏️ Отправка обновления отзыва:', props.reviewToEdit.id_review)
      
      const formData = new FormData()
      formData.append('category', reviewForm.value.category)
      formData.append('rating', reviewForm.value.rating)
      formData.append('text', reviewForm.value.text.trim())
      
      if (reviewForm.value.photos?.length) {
        reviewForm.value.photos.forEach((photo) => {
          formData.append('photo', photo.file)
        })
      }
      
      const response = await api.put(
        `/reviews/${props.reviewToEdit.id_review}`, 
        formData, 
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      // Сброс формы и закрытие
      reviewForm.value = { category: null, rating: 0, text: '', photos: [] }
      showReviewForm.value = false
      
      // Перезагрузка данных
      await loadReviews()
      await refreshObjectData()
      
      // Уведомление родителя
      emit('review-updated', { 
        success: true, 
        id_review: props.reviewToEdit.id_review,
        ...response.data 
      })
      
      toast.add({
        severity: 'success',
        summary: 'Обновлено!',
        detail: 'Отзыв успешно изменён',
        life: 3000,
        styleClass: 'my-success-toast'
      })
      
    } else {
      // 🔥 СОЗДАНИЕ нового отзыва (POST)
      console.log('✍️ Отправка нового отзыва')
      
      const formData = new FormData()
      formData.append('id_object', props.object.id_object)
      formData.append('category', reviewForm.value.category)
      formData.append('rating', reviewForm.value.rating)
      formData.append('text', reviewForm.value.text.trim())
      
      if (reviewForm.value.photos?.length) {
        reviewForm.value.photos.forEach((photo) => {
          formData.append('photo', photo.file)
        })
      }
      
      const response = await api.post('/api/reviews/', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      })

      // Очистка формы
      reviewForm.value = { category: null, rating: 0, text: '', photos: [] }
      showReviewForm.value = false
      
      // Перезагрузка данных
      await loadReviews()
      await refreshObjectData()
      
      // Уведомление родителя
      emit('review-submitted', { success: true, ...response.data })
      
      // Тост
      toast.add({
        severity: 'success',
        summary: 'Успешно!',
        detail: 'Отзыв опубликован',
        life: 3000,
        styleClass: 'my-success-toast'
      })
    }
    
  } catch (error) {
    console.error('[SubmitReview] Error:', error)
    
    // Обработка ошибок модерации
    const moderationError = error.response?.data?.detail
    
    if (moderationError?.moderation_failed) {
      toast.add({
        severity: 'warn',
        summary: 'Отзыв не прошёл проверку',
        detail: moderationError.reasons?.join(', ') || 'Содержит недопустимый контент',
        life: 6000,
        styleClass: 'my-error-toast'
      })
    } else if (error.message?.includes('Not authenticated')) {
      toast.add({
        severity: 'error',
        summary: 'Ошибка авторизации',
        detail: 'Пожалуйста, войдите в систему',
        life: 4000,
        styleClass: 'my-error-toast'
      })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Ошибка',
        detail: error.response?.data?.detail || error.message || 'Не удалось отправить отзыв',
        life: 4000,
        styleClass: 'my-error-toast'
      })
    }
    
    emit('review-submitted', { success: false, error: error.message })
    
  } finally {
    submittingReview.value = false
  }
}

// AI сводка отзывов
const aiSummary = ref(null)
const aiSummaryLoading = ref(false)
const displayedText = ref('') // Текст, который отображается постепенно
const isTyping = ref(false) // Флаг, что текст печатается

const fullSummaryText = "Покупатели обращают внимание на то, что объект отличается ярким светом, многофункциональностью, качественным материалом, хорошей емкостью аккумулятора и удобным расположением в руке."

// Функция печатающей машинки
const typeText = (text, speed = 30) => {
  return new Promise((resolve) => {
    isTyping.value = true
    displayedText.value = ''
    let index = 0
    
    const type = () => {
      if (index < text.length) {
        displayedText.value += text.charAt(index)
        index++
        setTimeout(type, speed)
      } else {
        isTyping.value = false
        resolve()
      }
    }
    
    type()
  })
}

// Загрузка AI сводки
const loadAiSummary = async () => {
  // Проверяем, что отзывы уже загружены
  if (!reviews.value || reviews.value.length === 0) {
    aiSummary.value = null
    return
  }
  
  aiSummaryLoading.value = true
  displayedText.value = ''
  

  try {
    // Готовим данные для отправки
    const reviewsData = reviews.value.map(review => ({
      text: review.text,
      rating: review.rating,
      category: review.category || 'unknown'
    }))
    
    console.log('[AI] Отправка запроса с', reviewsData.length, 'отзывами')
    
    // Вызываем наш бэкенд
    const response = await api.post('/api/reviews/ai-summary', {
      object_id: props.object.id_object,
      reviews: reviewsData
    })
    
    console.log('[AI] Получен ответ:', response.data)
    
    aiSummary.value = response.data.summary
    
    await typeText(aiSummary.value, 25)
    
  } catch (error) {
    console.error('[AI Summary] Error:', error)
    aiSummary.value = "Не удалось сгенерировать сводку. Попробуйте позже."
  } finally {
    aiSummaryLoading.value = false
  }
}

// Триггер загрузки отзывов
watch(
  () => [props.visible, props.object?.id_object],
  async ([isVisible, objectId]) => {
    if (isVisible && objectId) {
      await loadReviews()  // Ждём загрузки отзывов
      await loadAiSummary()  // Потом загружаем AI сводку
      await loadReviews()      // Сначала загружаем отзывы
      await loadAiSummary()    // Потом AI сводку
    }
  },
  { immediate: true }
)

// 🔥 Watch для reviewToEdit — открывает форму при редактировании
watch(
  () => props.reviewToEdit,
  (newReview, oldReview) => {
    // Открываем форму только если reviewToEdit появился (не пропал)
    if (newReview?.id_review && !oldReview?.id_review) {
      console.log('🔥 Edit mode: открываем форму для отзыва', newReview.id_review)
      
      // Предзаполняем форму
      reviewForm.value = {
        category: newReview.category || newReview.category_value || null,
        rating: typeof newReview.rating === 'number' ? newReview.rating : 0,
        text: newReview.text || '',
        photos: []
      }
      
      // Открываем форму с небольшой задержкой для анимации
      setTimeout(() => {
        showReviewForm.value = true
        console.log('✅ Форма редактирования открыта')
      }, 100)
    }
  },
  { immediate: false, deep: true }
)

// 🔥 Watch для visible — если модалка открыта + есть reviewToEdit, открываем форму
watch(
  () => [props.visible, props.reviewToEdit],
  ([isVisible, review], [wasVisible]) => {
    if (isVisible && !wasVisible && review?.id_review) {
      // Модалка только что открылась + есть отзыв для редактирования
      setTimeout(() => {
        if (!showReviewForm.value) {
          console.log('🔍 Авто-открытие формы при открытии модалки')
          openReviewForm()
        }
      }, 200)
    }
  }
)

const onGoToMap = () => {
  emit('go-to-map', props.object)
  emit('update:visible', false)
}

const onUpdateVisible = (value) => {
  emit('update:visible', value)
  if (!value) {
    showReviewForm.value = false
    reviewForm.value.photos = []
    // Сбрасываем reviewToEdit при закрытии
    if (props.reviewToEdit?.id_review) {
      emit('review-updated', null)
    }
    emit('close')
  }
}

const getInitials = (name) => {
  if (!name) return 'U'
  return name.split(' ').map((word) => word[0]).join('').toUpperCase().slice(0, 2)
}

const formatDate = (date) => {
  if (!date) return ''
  try {
    return new Date(date).toLocaleDateString('ru-RU', {
      day: '2-digit', month: 'long', year: 'numeric'
    })
  } catch {
    return date
  }
}

const formatExtraKey = (key) => {
  const labels = {
    phone: 'Телефон',
    hours: 'Часы работы',
    website: 'Сайт',
    price_range: 'Ценовой диапазон'
  }
  return labels[key] || key
}

const openPhotoViewer = (url) => window.open(url, '_blank')

// Триггер загрузки отзывов
watch(
  () => [props.visible, props.object?.id_object],
  ([isVisible, objectId]) => {
    if (isVisible && objectId) loadReviews()
  },
  { immediate: true }
)

watch(
  () => props.object?.id_object,
  (id) => {
    if (props.visible && id && reviews.value.length === 0 && !reviewsLoading.value) {
      loadReviews()
    }
  }
)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

.details-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 0px 28px 20px 28px;
  background: linear-gradient(180deg, #ffffff 0%, #d1d7d1 100%);
  overflow-y: auto;
  max-height: calc(97vh - 100px);
}

.hero-header {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 50px;
  flex-wrap: wrap;
  text-align: center;
}

.hero-title {
  margin: 0;
  font-size: 32px;
  font-weight: 900;
  color: #192219;
}

.hero-rating {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 14px;
  background: rgba(218, 176, 79, 0.312);
  color: #d39312;
  font-weight: 800;
}

.object-card, .reviews-section {
  background: rgba(255, 255, 255, 0.763);
  border-radius: 10px;
  padding: 36px 32px 20px 32px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.08);
}

.object-info-row {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.object-info-left {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 80px;
}

.object-info-right {
  display: flex;
  align-items: flex-start;
  margin-top: -7px;
}

.object-type-badge {
  display: inline-block;
  margin-bottom: 18px;
  padding: 10px 20px;
  border-radius: 12px;
  color: #3e7c48;
  font-weight: 700;
  font-size: 13px;
  border: 1px solid #007306;
}

.info-row {
  display: flex;
  gap: 12px;
  margin-bottom: 18px;
  color: #475569;
}

.description-box {
  padding: 18px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  line-height: 1.8;
  margin-bottom: 20px;
}

.extra-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}

.extra-item {
  padding: 14px;
  border-radius: 16px;
  background: #f8fafc;
}

.extra-label {
  display: block;
  margin-bottom: 4px;
  font-size: 11px;
  font-weight: 800;
  color: #94a3b8;
  text-transform: uppercase;
}

.extra-value {
  font-weight: 600;
  color: #0f172a;
}

.form-hint {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
  display: block;
}

:deep(.p-button) { 
  border-radius: 10px !important; 
  font-weight: 600 !important;
  font-size: 16px !important;
  padding: 0.625rem 1.25rem !important;
}

:deep(.p-button:not(.p-button-secondary)) { 
  background: linear-gradient(135deg, #168f04, #007306) !important; 
  border: none !important; 
  color: #fff !important;
}

:deep(.p-button:not(.p-button-secondary):hover) { 
  box-shadow: 0 4px 14px rgba(22,143,4,0.4) !important; 
}

:deep(.p-button:disabled) { 
  opacity: 0.7 !important; 
  cursor: not-allowed !important; 
}

:deep(.p-button.p-button-secondary) {
  background-color: #f1f5f9 !important;
  border: 1px solid #cbd5e1 !important;
  color: #334155 !important;
}

:deep(.p-button.p-button-secondary:hover) {
  background-color: #e2e8f0 !important;
  border-color: #94a3b8 !important;
  color: #1e293b !important;
}

:deep(.p-button.p-button-text) {
  color: #64748b !important;
}

:deep(.p-button.p-button-text:hover) {
  background-color: rgba(0,0,0,0.04) !important;
  color: #334155 !important;
}

:deep(.p-button .p-button-loading-icon) {
  margin-right: 6px !important;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.section-header h3 {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 800;
}




/* 🔥 Обертка для всей статистики */
.review-stats-wrapper {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Статистика по категориям */
.review-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 14px;
  border: 1px solid rgba(22, 143, 4, 0.15);
}

.stat-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-item.problem {
  background: linear-gradient(135deg, #fee2e2, #fecaca);
  color: #b91c1c;
}

.stat-item.problem i {
  font-size: 16px;
}

.stat-item.suggestion {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #1e40af;
}

.stat-item.suggestion i {
  font-size: 16px;
}

.stat-item.praise {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #047857;
}

.stat-item.praise i {
  font-size: 16px;
}

/* Grid для оценок и AI сводки */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 16px;
}

/* Статистика по оценкам (компактная) */
.rating-stats {
  padding: 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 14px;
  border: 1px solid rgba(22, 143, 4, 0.15);
  height: fit-content;
}

.rating-stats-title {
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  margin-bottom: 12px;
  text-align: center;
}

.rating-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rating-bar-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rating-bar-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  font-weight: 600;
  color: #fbbf24;
  min-width: 30px;
}

.rating-bar-label i {
  font-size: 9px;
}

.rating-bar-track {
  flex: 1;
  height: 6px;
  background: rgba(251, 191, 36, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.rating-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #fbbf24, #f59e0b);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.rating-bar-count {
  font-size: 11px;
  font-weight: 700;
  color: #64748b;
  min-width: 20px;
  text-align: right;
}





/* Эффект печатающегося текста */
.typing-text {
  margin: 0 0 14px 0;
  font-size: 14px;
  line-height: 1.6;
  color: #334155;
  min-height: 60px; /* Чтобы не прыгало */
}

.typing-cursor {
  display: inline-block;
  color: #8b5cf6;
  font-weight: 700;
  animation: blink 0.8s ease-in-out infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}

/* AI сводка */
.ai-summary-card {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05), rgba(139, 92, 246, 0.1));
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 14px;
  padding: 18px;
  position: relative;
  overflow: hidden;
}

.ai-summary-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #8b5cf6, #a78bfa, #8b5cf6);
}

.ai-summary-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.ai-icon {
  font-size: 20px;
  color: #8b5cf6;
  animation: sparkle 2s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.ai-summary-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #1e293b;
}

.ai-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
  color: #64748b;
}

.ai-loading span {
  font-size: 13px;
}

.ai-summary-content p {
  margin: 0 0 14px 0;
  font-size: 14px;
  line-height: 1.6;
  color: #334155;
}

.ai-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid rgba(139, 92, 246, 0.15);
}

.ai-badge {
  font-size: 11px;
  color: #8b5cf6;
  font-weight: 500;
}

.ai-actions {
  display: flex;
  gap: 8px;
}

.ai-action-btn {
  width: 32px;
  height: 32px;
  border: 1px solid rgba(139, 92, 246, 0.3);
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: #8b5cf6;
}

.ai-action-btn:hover {
  background: rgba(139, 92, 246, 0.1);
  border-color: #8b5cf6;
  transform: translateY(-2px);
}

.ai-empty {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
  font-size: 13px;
}







.review-form-card {
  margin-bottom: 24px;
  padding: 24px;
  border-radius: 24px;
  background: #f8fffa;
  border: 1px solid rgba(16, 185, 129, 0.18);
}

/* 🔥 Стили для заголовка формы */
.form-title {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(22, 143, 4, 0.15);
}

.form-title h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 700;
  color: #168f04;
}

.form-subtitle {
  margin: 0;
  font-size: 12px;
  color: #64748b;
  font-style: italic;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.form-label {
  font-size: 13px;
  font-weight: 700;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.category-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.category-btn {
  padding: 12px 24px;
  border-radius: 12px;
  border: 2px solid transparent;
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.category-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.category-btn:nth-child(1) {
  background: linear-gradient(135deg, #fec7c71a, #fd8a8af0);
  color: #92400e;
}

.category-btn:nth-child(1):hover {
  box-shadow: 0 4px 14px rgba(245, 11, 11, 0.2);
}

.category-btn:nth-child(1).active {
  background: linear-gradient(135deg, #f50b0b4c, #d90606e9);
  color: #fff;
  box-shadow: 0 4px 14px rgba(245, 11, 11, 0.388);
}

.category-btn:nth-child(2) {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe);
  color: #1e40af;
}

.category-btn:nth-child(2):hover {
  background: linear-gradient(135deg, #bfdbfe, #93c5fd);
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.35);
}

.category-btn:nth-child(2).active {
  background: linear-gradient(135deg, #3b83f68c, #2564ebe2);
  color: #fff;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.45);
}

.category-btn:nth-child(3) {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0);
  color: #047857;
}

.category-btn:nth-child(3):hover {
  background: linear-gradient(135deg, #a7f3d0, #6ee7b7);
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
}

.category-btn:nth-child(3).active {
  background: linear-gradient(135deg, #10b98183, #059669);
  color: #fff;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.45);
}

.rating-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rating-value {
  font-weight: 700;
  font-size: 16px;
  color: #fbbf24;
}

.photo-upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 14px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fff;
}

.photo-upload-area:hover {
  border-color: #10b981;
  background: #f0fdf4;
}

.file-input { display: none; }

.photo-upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #64748b;
}

.photo-upload-placeholder i {
  font-size: 32px;
  color: #10b981;
}

.photo-upload-placeholder small { color: #94a3b8; }

.photo-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
}

.photo-preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 12px;
  overflow: hidden;
}

.photo-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(0,0,0,0.6);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.photo-remove-btn:hover { background: rgba(0,0,0,0.8); }

.review-photos {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.review-photo {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s;
}

.review-photo:hover { transform: scale(1.05); }

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-card {
  padding: 20px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  background: #fff;
}

.review-header {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.review-avatar {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.review-author {
  font-weight: 800;
  margin-bottom: 6px;
}

.review-submeta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.review-text {
  margin: 0;
  line-height: 1.8;
  color: #334155;
}

.empty-state {
  text-align: center;
  padding: 56px 24px;
  color: #64748b;
}

.empty-state i {
  font-size: 56px;
  margin-bottom: 16px;
}

.modal-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 80px;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

:deep(.p-dialog) {
  border-radius: 32px;
  overflow: hidden;
}

:deep(.p-dialog-header) { display: none; }
:deep(.p-dialog-content) { padding: 0; }

:deep(.p-inputtext),
:deep(.p-dropdown),
:deep(.p-inputtextarea) {
  border-radius: 10px;
  border: 1px solid #cbd5e1;
}

:deep(.p-inputtext:focus),
:deep(.p-dropdown:focus),
:deep(.p-inputtextarea:focus) {
  border-color: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.15);
}

:deep(.p-rating) {
  --p-rating-icon-active-color: #fbbf24 !important;
  --p-rating-icon-color: #cbd5e1 !important;
  --p-rating-icon-hover-color: #fbbf24 !important;
}

:deep(.p-rating .p-rating-icon) {
  width: 35px !important;
  height: 25px !important;
  font-size: 40px !important;
}

@media (max-width: 768px) {
  .details-wrapper { padding: 16px; }
  .object-card, .reviews-section { padding: 20px; border-radius: 22px; }
  .hero-header, .section-header, .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
  .object-info-row { flex-direction: column; }
  .object-info-right { width: 100%; justify-content: center; }
  .btn-map :deep(.p-button),
  .review-btn :deep(.p-button),
  :deep(.form-actions .p-button) {
    width: 100% !important;
    min-width: unset !important;
  }
  .category-buttons { flex-direction: column; }
  .category-btn { width: 100%; }
  .hero-title { font-size: 1.5rem; }
  
  /* Адаптив для статистики */
  .review-stats {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .rating-bar-item {
    gap: 6px;
  }
  
  .rating-bar-label {
    min-width: 28px;
    font-size: 11px;
  }
  
  .rating-bar-count {
    min-width: 20px;
    font-size: 11px;
  }
}

:deep(.my-big-toast) {
  min-width: 320px !important;
  font-size: 14px !important;
}

:deep(.my-error-toast) {
  border-left: 4px solid #dc2626 !important;
}

:deep(.my-info-toast) {
  border-left: 4px solid #3b82f6 !important;
}

.review-card :deep(.p-rating .p-rating-icon) {
  width: 20px !important;
  height: 20px !important;
  font-size: 18px !important;
}

.review-card :deep(.p-rating) {
  gap: 2px !important;
}

/* Цвета для категорий отзывов */
:deep(.p-tag.category-problem) {
  background: linear-gradient(135deg, #fee2e2, #fecaca) !important;
  color: #b91c1c !important;
  border: 1px solid #f87171 !important;
  font-weight: 600 !important;
}

:deep(.p-tag.category-suggestion) {
  background: linear-gradient(135deg, #dbeafe, #bfdbfe) !important;
  color: #1e40af !important;
  border: 1px solid #60a5fa !important;
  font-weight: 600 !important;
}

:deep(.p-tag.category-praise) {
  background: linear-gradient(135deg, #d1fae5, #a7f3d0) !important;
  color: #047857 !important;
  border: 1px solid #34d399 !important;
  font-weight: 600 !important;
}

:deep(.p-tag.p-tag-danger),
:deep(.p-tag.p-tag-info),
:deep(.p-tag.p-tag-success) {
  background: transparent !important;
}

.section-header p {
  transition: all 0.2s ease;
  font-weight: 500;
  color: #64748b;
}

</style>