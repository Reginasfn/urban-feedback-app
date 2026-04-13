<template>
  <Dialog 
    v-model:visible="isVisible" 
    header="Добавить отзыв" 
    :modal="true" 
    :closable="true"
    :style="{ width: '480px' }"
    :pt="{
      header: { class: 'bg-white border-b border-gray-200' },
      content: { class: 'bg-white' },
      footer: { class: 'bg-white border-t border-gray-200' }
    }"
    @hide="onCancel"
    style="font-family: monospace;"
  >
    <div class="review-form">
      <!-- Информация об объекте -->
      <div v-if="selectedObject" class="object-info">
        <i :class="getCategoryIcon(selectedObject.type)"></i>
        <div>
          <strong>{{ selectedObject.name }}</strong>
          <span class="object-type">{{ selectedObject.type }}</span>
        </div>
      </div>

      <!-- Категория отзыва -->
      <div class="form-group">
        <label class="form-label">Категория отзыва</label>
        <div class="review-categories">
          <button 
            v-for="cat in reviewCategories" 
            :key="cat.value"
            @click="reviewForm.category = cat.value"
            :class="['category-chip', { active: reviewForm.category === cat.value }]"
            type="button"
          >
            <i :class="cat.icon"></i>
            {{ cat.label }}
          </button>
        </div>
      </div>

      <!-- Рейтинг -->
      <div class="form-group">
        <label class="form-label">Рейтинг</label>
        <div class="rating-stars">
          <button 
            v-for="star in 5" 
            :key="star"
            @click="reviewForm.rating = star"
            class="star-btn"
            :class="{ filled: star <= reviewForm.rating }"
            type="button"
            :aria-label="'Рейтинг ' + star + ' из 5'"
          >
            <i :class="star <= reviewForm.rating ? 'pi pi-star-fill' : 'pi pi-star'"></i>
          </button>
          <span class="rating-value">{{ reviewForm.rating }}/5</span>
        </div>
      </div>

      <!-- Текст отзыва -->
      <div class="form-group">
        <label class="form-label">Ваш отзыв</label>
        <Textarea 
          v-model="reviewForm.text" 
          placeholder="Напишите ваш отзыв..." 
          rows="4" 
          class="w-full"
          :maxlength="500"
        />
        <small class="text-hint">{{ reviewForm.text.length }}/500</small>
      </div>

      <!-- Загрузка фото (только 1 фото) -->
      <div class="form-group">
        <label class="form-label">Прикрепить фото (необязательно)</label>
        <div class="photo-upload">
          <!-- Превью выбранного фото -->
          <div v-if="selectedPhoto" class="photo-preview">
            <img :src="selectedPhoto.preview" alt="Preview" class="preview-image" />
            <button class="remove-photo" @click="removePhoto" type="button" title="Удалить фото">
              <i class="pi pi-times"></i>
            </button>
            <span class="photo-name" :title="selectedPhoto.name">{{ selectedPhoto.name }}</span>
          </div>
          
          <!-- Кнопка загрузки -->
          <FileUpload
            v-else
            ref="photoUploader"
            mode="basic"
            :auto="false"
            :maxFileSize="10000000"
            :accept="'image/*'"
            :chooseLabel="'📷 Выбрать фото'"
            @select="onPhotoSelect"
            class="photo-uploader"
            :pt="{
              root: { class: 'w-full' },
              input: { class: 'hidden' },
              chooseButton: { 
                class: 'w-full border-2 border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100 hover:border-green-500 transition-all rounded-xl py-6' 
              },
              chooseIcon: { class: 'hidden' },
              chooseLabel: { class: 'text-gray-600 font-medium' }
            }"
          />
          
          <!-- Подсказка -->
          <p class="upload-hint">
            <i class="pi pi-info-circle"></i>
            Можно загрузить 1 фото (JPG, PNG, до 10 МБ)
          </p>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="review-actions">
        <Button 
          label="Отмена" 
          severity="secondary" 
          @click="onCancel" 
          :disabled="submitting"
        />
        <Button 
          label="Сохранить" 
          @click="onSubmit" 
          :disabled="!canSubmit" 
          :loading="submitting" 
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import axios from 'axios'
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'

// ===== Props =====
const props = defineProps({
  // Управление видимостью (v-model:visible)
  modelValue: {
    type: Boolean,
    default: false
  },
  // Данные объекта для отзыва
  selectedObject: {
    type: Object,
    default: null
    // Ожидаемая структура: { id: string, name: string, type: string }
  },
  // Категории отзывов
  reviewCategories: {
    type: Array,
    default: () => [
      { value: 'praise', label: 'Похвала', icon: 'pi pi-thumbs-up' },
      { value: 'suggestion', label: 'Предложение', icon: 'pi pi-lightbulb' },
      { value: 'problem', label: 'Проблема', icon: 'pi pi-exclamation-circle' }
    ]
  },
  // Иконки для категорий объектов (опционально)
  categoryIcons: {
    type: Object,
    default: () => ({})
  },
  // Начальные данные формы (опционально)
  initialForm: {
    type: Object,
    default: null
  }
})

// ===== Emits =====
const emit = defineEmits([
  'update:modelValue',    // Для v-model:visible
  'submit',               // При успешной отправке: { formData, photo }
  'cancel',               // При отмене
  'photo-select',         // При выборе фото: { file, preview, name, size }
  'photo-remove',
  'error'          // При удалении фото
])

// ===== Внутреннее состояние =====
const isVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const reviewForm = ref({
  text: '',
  category: 'praise',
  rating: 5
})

const selectedPhoto = ref(null) // { file: File, preview: string, name: string, size: number }
const submitting = ref(false)
const photoUploader = ref(null)

// ===== Валидация =====
const canSubmit = computed(() => {
  return reviewForm.value.text.trim().length >= 10 && 
         reviewForm.value.rating > 0 && 
         !submitting.value
})

// ===== Иконки категорий =====
const defaultCategoryIcons = {
  'Камера видеонаблюдения': 'pi pi-video',
  'Кафе': 'pi pi-map-marker',
  'Фонарь': 'pi pi-lightbulb',
  'Скамейка': 'pi pi-map-marker',
  'Парк': 'pi pi-tree',
  'Беседка': 'pi pi-building-columns',
  'Остановка': 'pi pi-car',
  'Детская площадка': 'pi pi-face-smile'
}

const getCategoryIcon = (type) => {
  return props.categoryIcons[type] || defaultCategoryIcons[type] || 'pi pi-map-marker'
}

// ===== Обработчики =====
const onCancel = () => {
  if (submitting.value) return
  emit('cancel')
  resetForm()
  isVisible.value = false
}

const resetForm = () => {
  reviewForm.value = { text: '', category: 'praise', rating: 5 }
  removePhoto()
}

const onSubmit = async () => {
  if (!canSubmit.value || !props.selectedObject) return
  
  submitting.value = true
  
  try {
    // Подготовка FormData
    const formData = new FormData()
    formData.append('id_object', props.selectedObject.id)
    formData.append('text', reviewForm.value.text.trim())
    formData.append('rating', reviewForm.value.rating)
    formData.append('category', reviewForm.value.category)
    
    if (selectedPhoto.value?.file) {
      formData.append('photo', selectedPhoto.value.file)
    }
    
    // 👇 Получаем токен
    const token = localStorage.getItem('auth_token')
    
    if (!token) {
      emit('error', { message: 'Пользователь не авторизован' })
      return
    }
    
    console.log('[ReviewModal] Отправка отзыва...', {
      objectId: props.selectedObject.id,
      text: reviewForm.value.text,
      rating: reviewForm.value.rating,
      category: reviewForm.value.category,
      hasPhoto: !!selectedPhoto.value
    })
    
    // 👇 ОТПРАВКА НА БЭКЕНД (БЕЗ Content-Type!)
    const response = await axios.post(
      'http://localhost:8000/reviews/',
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`
          // ❌ НЕ УСТАНАВЛИВАЙ Content-Type вручную!
          // Axios сам установит 'multipart/form-data; boundary=...'
        }
      }
    )
    
    console.log('[ReviewModal] Ответ сервера:', response.data)
    
    // Если успешно - эмитим с reviewId
    emit('submit', {
      reviewId: response.data.id_review,
      message: response.data.message || 'Отзыв успешно добавлен!'
    })
    
    isVisible.value = false
    
  } catch (err) {
    console.error('[ReviewModal] Ошибка отправки:', err)
    console.error('[ReviewModal] Ответ сервера:', err.response?.data)
    const message = err.response?.data?.detail || 'Не удалось отправить отзыв'
    emit('error', { message })
  } finally {
    submitting.value = false
  }
}

// ===== Загрузка фото =====
const onPhotoSelect = (event) => {
  const file = event.files?.[0]
  if (!file) return
  
  // Валидация типа
  if (!file.type.startsWith('image/')) {
    emit('error', { message: 'Пожалуйста, выберите изображение (JPG, PNG, GIF)' })
    return
  }
  
  // Валидация размера (10 МБ)
  if (file.size > 10 * 1024 * 1024) {
    emit('error', { message: 'Фото слишком большое (макс. 10 МБ)' })
    return
  }
  
  // Создаём превью
  const reader = new FileReader()
  reader.onload = (e) => {
    const photoData = {
      file: file,
      preview: e.target.result,
      name: file.name,
      size: file.size
    }
    selectedPhoto.value = photoData
    emit('photo-select', photoData)
  }
  reader.readAsDataURL(file)
  
  // Очищаем инпут для повторного выбора
  event.clear()
}

const removePhoto = () => {
  selectedPhoto.value = null
  if (photoUploader.value) {
    photoUploader.value.clear()
  }
  emit('photo-remove')
}

// ===== Сброс при открытии =====
watch(() => props.modelValue, (newVal) => {
  if (newVal && props.initialForm) {
    reviewForm.value = { ...reviewForm.value, ...props.initialForm }
  } else if (newVal) {
    resetForm()
  }
})

// ===== Экспортируем методы для родителя (опционально) =====
defineExpose({
  resetForm,
  removePhoto
})
</script>

<style scoped>
/* === ФОРМА ОТЗЫВА === */
.review-form {font-family: monospace; display: flex; flex-direction: column; gap: 15px; padding: 8px 4px; }

/* Информация об объекте */
.object-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(22, 143, 4, 0.08);
  border-radius: 12px;
  border: 1px solid rgba(22, 143, 4, 0.2);
  margin-bottom: 8px;
}
.object-info i {
  font-size: 20px;
  color: #168f04;
  background: rgba(22, 143, 4, 0.15);
  padding: 8px;
  border-radius: 10px;
}
.object-info strong {
  display: block;
  font-size: 15px;
  color: #1a1a1a;
  padding: 2px 8px;
}
.object-type {
  font-size: 12px;
  font-weight: 600;
  color: #168f04;
  background: rgba(22, 143, 4, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
}

/* Группы полей */
.form-group { display: flex; flex-direction: column; gap: 5px; }
.form-label { 
  font-size: 16px; 
  font-weight: 600; 
  color: #334155;
  display: flex;
  align-items: center;
}
.text-hint {
  font-size: 12px;
  color: #858a93;
  text-align: right;
  margin-top: -5px;
}

/* Категории отзывов */
.review-categories { display: flex; gap: 8px; flex-wrap: wrap; }
.category-chip { 
  display: flex; 
  align-items: center; 
  gap: 6px; 
  padding: 8px 14px; 
  background: #f1f5f9; 
  border: 2px solid #e2e8f0; 
  border-radius: 20px; 
  font-size: 15px; 
  font-weight: 500; 
  color: #475569; 
  cursor: pointer; 
  transition: all 0.5s;
}
.category-chip:hover { 
  border-color: #168f04; 
  color: #168f04; 
  background: rgba(22,143,4,0.05); 
}
.category-chip.active { 
  background: linear-gradient(135deg, #168f04, #007306); 
  border-color: #168f04; 
  color: white; 
  box-shadow: 0 4px 12px rgba(22,143,4,0.3); 
}
.category-chip i { font-size: 14px; }

/* Рейтинг */
.rating-stars { display: flex; align-items: center; gap: 4px; }
.star-btn { 
  background: none; 
  border: none; 
  padding: 4px; 
  color: #cbd5e1; 
  font-size: 20px; 
  cursor: pointer; 
  transition: all 0.5s;
}
.star-btn:hover, .star-btn.filled { 
  color: #fbbf24; 
  transform: scale(1.1); 
}
.rating-value { 
  margin-left: 8px; 
  font-size: 15px; 
  font-weight: 600; 
  color: #64748b; 
}

/* Загрузка фото */
.photo-upload { display: flex; flex-direction: column; gap: 10px; }
.photo-preview {
  position: relative;
  width: 100%;
  max-width: 200px;
  aspect-ratio: 4/3;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border: 2px solid rgba(22,143,4,0.3);
}
.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.remove-photo {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(220,38,38,0.9);
  color: white;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.5s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  z-index: 2;
}
.remove-photo:hover { 
  background: #dc2626; 
  transform: scale(1.1); 
}
.photo-name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 6px 8px;
  background: rgba(0,0,0,0.6);
  color: white;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.upload-hint {
  font-size: 14px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}
.upload-hint i { font-size: 12px; }

/* Кнопки действий */
.review-actions { 
  display: flex; 
  justify-content: flex-end; 
  gap: 10px; 
  padding-top: 8px;
}

/* === СТИЛИ ДЛЯ PRIMEVUE COMPONENTS === */
:deep(.photo-uploader .p-fileupload-choose) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
}
:deep(.photo-uploader .p-fileupload-choose:hover) {
  background: transparent !important;
}
:deep(.photo-uploader .p-fileupload-input) {
  cursor: pointer;
}
:deep(.p-textarea) { 
  border-radius: 12px; 
  border: 2px solid #e2e8f0; 
  transition: border-color 0.5s; 
  font-size: 15px;
}
:deep(.p-textarea:focus) { 
  border-color: #168f04; 
  box-shadow: 0 0 0 4px rgba(22,143,4,0.12); 
}
:deep(.p-button) { 
  border-radius: 10px; 
  font-weight: 600;
  font-size: 14px;
  padding: 0.625rem 1.25rem;
}
:deep(.p-button:not(.p-button-secondary)) { 
  background: linear-gradient(135deg, #168f04, #007306); 
  border: none; 
}
:deep(.p-button:not(.p-button-secondary):hover) { 
  box-shadow: 0 4px 14px rgba(22,143,4,0.4); 
}
:deep(.p-button:disabled) { 
  opacity: 0.7; 
  cursor: not-allowed; 
}
</style>