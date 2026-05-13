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
            label="Оставить отзыв"
            icon="pi pi-pencil"
            class="review-btn"
            style="height: 50px; width: 180px;"
            @click="openReviewForm"
          />
        </div>

        <Transition name="slide-fade">
          <div v-if="showReviewForm" class="review-form-card">
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
                @click="showReviewForm = false"
              />
              <Button
                label="Отправить"
                icon="pi pi-send"
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
                    severity="info"
                  />

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

const props = defineProps({
  object: { type: Object, default: null },
  visible: { type: Boolean, default: false }
})

const emit = defineEmits(['update:visible', 'close', 'go-to-map', 'review-submitted'])

const reviews = ref([])
const reviewsLoading = ref(false)
const showReviewForm = ref(false)
const submittingReview = ref(false)
const fileInput = ref(null)

const reviewCategories = [
  { label: 'Проблема', value: 'Проблема' },
  { label: 'Предложение', value: 'Предложение' },
  { label: 'Похвала', value: 'Похвала' }
]

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

const openReviewForm = () => {
  reviewForm.value = { category: null, rating: 0, text: '', photos: [] }
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

const loadReviews = async () => {
  if (!props.object?.id_object) return
  reviewsLoading.value = true
  try {
    const response = await fetch(`/api/objects/${props.object.id_object}/ratings?limit=50&offset=0`)
    const data = await response.json()
    reviews.value = data.items || data || []
  } catch (error) {
    console.error(error)
    reviews.value = []
  } finally {
    reviewsLoading.value = false
  }
}

const submitReview = async () => {
  emit('review-submitted', {
    ...reviewForm.value,
    photos: reviewForm.value.photos.map(p => p.file)
  })
  showReviewForm.value = false
}

const onGoToMap = () => {
  emit('go-to-map', props.object)
  emit('update:visible', false)
}

const onUpdateVisible = (value) => {
  emit('update:visible', value)
  if (!value) {
    showReviewForm.value = false
    reviewForm.value.photos = []
    emit('close')
  }
}

const getInitials = (name) => {
  if (!name) return 'U'
  return name.split(' ').map((word) => word[0]).join('').toUpperCase().slice(0, 2)
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU', {
    day: '2-digit', month: 'long', year: 'numeric'
  })
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

watch(() => props.visible, (value) => {
  if (value && props.object?.id_object) loadReviews()
})
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

/* === OBJECT TYPE BADGE — СТИЛЬНЫЙ ФИОЛЕТОВЫЙ === */
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

/* === BUTTON STYLES === */
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

.review-form-card {
  margin-bottom: 24px;
  padding: 24px;
  border-radius: 24px;
  background: #f8fffa;
  border: 1px solid rgba(16, 185, 129, 0.18);
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

/* === CATEGORY BUTTONS === */
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

/* Проблема — оранжево-красный */
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
/* Предложение — синий */
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

/* Похвала — зелёный */
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

/* === RATING === */
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

/* Photo upload */
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

/* === PRIMEVUE RATING — CSS VARIABLES (РАБОТАЕТ!) === */
:deep(.p-rating) {
  --p-rating-icon-active-color: #fbbf24 !important;
  --p-rating-icon-color: #cbd5e1 !important;
  --p-rating-icon-hover-color: #fbbf24 !important;
}

/* === УВЕЛИЧЕННЫЕ ЗВЁЗДЫ — SVG РАЗМЕР === */
:deep(.p-rating .p-rating-icon) {
  width: 35px !important;
  height: 25px !important;
  font-size: 40px !important;  /* на всякий случай, если шрифт */
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
}
</style>