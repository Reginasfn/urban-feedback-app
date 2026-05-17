<!-- frontend\src\components\modals\ObjectModal.vue -->
<template>
  <Dialog 
    v-model:visible="isVisible" 
    :header="null"
    :modal="true" 
    :closable="true"
    :style="{ width: '520px', maxWidth: '96vw' }"
    :contentStyle="{ padding: 0 }"
    :pt="{
      root: { class: 'rounded-2xl overflow-hidden shadow-2xl' },
      header: { class: 'hidden' },
      content: { class: 'p-0' },
      footer: { class: 'p-0' }
    }"
    class="object-add-modal"
  >
    <!-- Header Section -->
    <div class="modal-header">
      <div class="header-icon">
        <i class="pi pi-map-marker"></i>
      </div>
      <h2 class="modal-title">Добавить объект</h2>
      <p class="modal-subtitle">Укажите название и тип объекта на карте</p>
    </div>

    <!-- Form Section -->
    <div class="modal-body">
      
      <!-- Location Card -->
      <div class="location-card">
        <div class="location-row">
          <i class="pi pi-map-marker location-icon"></i>
          <div class="location-text">
            <span class="location-label">Координаты:</span>
            <span class="location-value">{{ formattedCoords }}</span>
          </div>
        </div>
        <div v-if="props.address" class="location-row">
          <i class="pi pi-home location-icon"></i>
          <div class="location-text">
            <span class="location-label">Адрес:</span>
            <span class="location-value">{{ props.address }}</span>
          </div>
        </div>
      </div>

      <!-- Name Field -->
      <div class="form-field">
        <label class="field-label" for="object-name">
          <i class="pi pi-tag"></i>
          Название объекта *
        </label>
        <InputText 
          id="object-name"
          v-model="formData.name" 
          placeholder="Например: Скамейка у входа в парк" 
          class="field-input"
          :class="{ 'input-error': errors.name }"
          :maxlength="100"
        />
        <small v-if="errors.name" class="error-message">
          <i class="pi pi-exclamation-circle"></i> {{ errors.name }}
        </small>
      </div>

      <!-- Type Field -->
      <div class="form-field">
        <label class="field-label" for="object-type">
          <i class="pi pi-list"></i>
          Тип объекта *
        </label>
        <Dropdown 
          id="object-type"
          v-model="formData.type" 
          :options="availableTypes"
          optionLabel="label"
          optionValue="value"
          placeholder="Выберите тип объекта..."
          class="field-dropdown"
          :class="{ 'input-error': errors.type }"
          :filter="true"
          filterPlaceholder="Поиск типа..."
          :showClear="true"
        >
          <template #value="slotProps">
            <div v-if="slotProps.value" class="dropdown-selected">
              <i :class="getTypeIcon(slotProps.value)" class="dropdown-icon"></i>
              <span>{{ getLabelByValue(slotProps.value) }}</span>
            </div>
            <span v-else class="dropdown-placeholder">{{ slotProps.placeholder }}</span>
          </template>
          <template #option="slotProps">
            <div class="dropdown-option">
              <i :class="getTypeIcon(slotProps.option.value)" class="dropdown-icon"></i>
              <span class="dropdown-label">{{ slotProps.option.label }}</span>
            </div>
          </template>
        </Dropdown>
        <small v-if="errors.type" class="error-message">
          <i class="pi pi-exclamation-circle"></i> {{ errors.type }}
        </small>
      </div>

    </div>

    <!-- Footer Section -->
    <div class="modal-footer">
      <div class="footer-actions">
        <Button
          label="Отмена"
          severity="secondary"
          text
          @click="onCancel"
          class="btn-cancel"
        />
        <Button
          label="Сохранить объект"
          icon="pi pi-check"
          :loading="submitting"
          :disabled="!canSubmit"
          @click="onSubmit"
          class="btn-submit"
        />
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'

// ===== Props =====
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  coordinates: {
    type: Array,
    required: false,
    validator: (val) => {
      if (val === null) return true
      return val.length === 2 && typeof val[0] === 'number' && typeof val[1] === 'number'
    }
  },
  address: { type: String, default: '' },
  availableTypes: {
    type: Array,
    default: () => [
      // 🔹 Оригинальные 8 типов (порядок сохранён)
      { label: 'Камера видеонаблюдения', value: 'Камера видеонаблюдения' },
      { label: 'Кафе', value: 'Кафе' },
      { label: 'Фонарь', value: 'Фонарь' },
      { label: 'Скамейка', value: 'Скамейка' },
      { label: 'Парк', value: 'Парк' },
      { label: 'Беседка', value: 'Беседка' },
      { label: 'Остановка', value: 'Остановка' },
      { label: 'Детская площадка', value: 'Детская площадка' },
      { label: 'Спортивная площадка', value: 'Спортивная площадка' },
      { label: 'Урна', value: 'Урна' },
      { label: 'Мусорный контейнер', value: 'Мусорный контейнер' },
      { label: 'Парковка', value: 'Парковка' },
      { label: 'Пешеходный переход', value: 'Пешеходный переход' },
      { label: 'Памятник', value: 'Памятник' },
      { label: 'Информационный стенд', value: 'Информационный стенд' },
      { label: 'Цветник', value: 'Цветник' },
      { label: 'Дорожка', value: 'Дорожка' },
      { label: 'Ограждение', value: 'Ограждение' }
    ]
  }
})

// ===== Emits =====
const emit = defineEmits([
  'update:modelValue',
  'submit',
  'cancel',
  'error'
])

// ===== Внутреннее состояние =====
const isVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formData = ref({
  name: '',
  type: null
})

const errors = ref({})
const submitting = ref(false)

// ===== Иконки для типов объектов (из categoryIcons) =====
const typeIcons = {
  'Камера видеонаблюдения': 'pi pi-video',
  'Кафе': 'pi pi-map-marker',
  'Фонарь': 'pi pi-lightbulb',
  'Скамейка': 'pi pi-map-marker',
  'Парк': 'pi pi-map-marker',
  'Беседка': 'pi pi-building-columns',
  'Остановка': 'pi pi-car',
  'Детская площадка': 'pi pi-face-smile',
  'Спортивная площадка': 'pi pi-bolt',
  'Урна': 'pi pi-trash',
  'Мусорный контейнер': 'pi pi-trash',
  'Парковка': 'pi pi-car',
  'Пешеходный переход': 'pi pi-directions-alt',
  'Памятник': 'pi pi-flag',
  'Информационный стенд': 'pi pi-info-circle',
  'Цветник': 'pi pi-star',
  'Дорожка': 'pi pi-arrow-right',
  'Ограждение': 'pi pi-th-large'
}

const getTypeIcon = (value) => typeIcons[value] || 'pi pi-map-marker'

const getLabelByValue = (value) => {
  const found = props.availableTypes.find(t => t.value === value)
  return found?.label || value
}

// ===== Форматирование координат =====
const formattedCoords = computed(() => {
  if (!props.coordinates || !Array.isArray(props.coordinates)) {
    return 'Координаты не определены'
  }
  const [lat, lon] = props.coordinates
  return `${lat.toFixed(6)}, ${lon.toFixed(6)}`
})

// ===== Валидация =====
const canSubmit = computed(() => {
  return formData.value.name?.trim().length >= 3 && 
         formData.value.type && 
         !submitting.value
})

const validate = () => {
  errors.value = {}
  
  const name = formData.value.name?.trim()

  if (!name) {
    errors.value.name = 'Введите название объекта'
  } else if (name.length < 3) {
    errors.value.name = 'Минимум 3 символа'
  } else if (/^\d+$/.test(name)) {
    errors.value.name = 'Название должно содержать буквы'
  }
  
  if (!formData.value.type) {
    errors.value.type = 'Выберите тип объекта'
  }
  
  return Object.keys(errors.value).length === 0
}

// ===== Обработчики =====
const onCancel = () => {
  emit('cancel')
  emit('update:modelValue', false) 
}

const resetForm = () => {
  formData.value = { name: '', type: null }
  errors.value = {}
}

const onSubmit = async () => {
  if (!validate()) return
  
  submitting.value = true
  
  try {
    const payload = {
      name: formData.value.name.trim(),
      type: formData.value.type,
      coords: props.coordinates
    }
    
    emit('submit', payload)
    isVisible.value = false
    resetForm()
    
  } catch (err) {
    console.error('[ObjectModal] Ошибка:', err)
    emit('error', { message: 'Не удалось сохранить объект' })
  } finally {
    submitting.value = false
  }
}

// ===== Сброс при открытии =====
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    resetForm()
  }
})

defineExpose({ resetForm })
</script>

<style scoped>
/* ===== MODAL HEADER ===== */
.modal-header {
  text-align: center;
  padding: 2rem 2rem 1.5rem;
  background: linear-gradient(135deg, #168f04 0%, #0d5a02 100%);
  position: relative;
  overflow: hidden;
}

.modal-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.header-icon {
  width: 70px;
  height: 70px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.header-icon i {
  font-size: 2rem;
  color: white;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: white;
  margin: 0 0 0.5rem 0;
  position: relative;
  z-index: 1;
}

.modal-subtitle {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  position: relative;
  z-index: 1;
  font-weight: 500;
}

/* ===== MODAL BODY ===== */
.modal-body {
  padding: 1.5rem 2rem;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ===== LOCATION CARD ===== */
.location-card {
  background: rgba(22, 143, 4, 0.08);
  border: 1px solid rgba(22, 143, 4, 0.2);
  border-radius: 14px;
  padding: 1rem 1.25rem;
}

.location-row {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.25rem 0;
}

.location-row:first-child {
  padding-bottom: 0.5rem;
  border-bottom: 1px dashed rgba(22, 143, 4, 0.2);
  margin-bottom: 0.5rem;
}

.location-icon {
  font-size: 1rem;
  color: #168f04;
  margin-top: 3px;
  flex-shrink: 0;
}

.location-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.location-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.location-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1e293b;
  word-break: break-all;
}

/* ===== FORM FIELDS ===== */
.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: #334155;
}

.field-label i {
  color: #168f04;
  font-size: 0.9rem;
}

.field-input,
.field-dropdown {
  height: 52px !important;
  border: 2px solid #e2e8f0 !important;
  border-radius: 12px !important;
  padding: 0 1rem !important;
  font-size: 1rem !important;
  transition: all 0.3s ease !important;
  background: #fff !important;
}

.field-input:hover,
.field-dropdown:hover {
  border-color: #cbd5e1 !important;
}

.field-input:focus,
.field-dropdown:focus-within {
  border-color: #168f04 !important;
  box-shadow: 0 0 0 4px rgba(22, 143, 4, 0.1) !important;
  outline: none !important;
}

.input-error {
  border-color: #ef4444 !important;
  background: #fef2f2 !important;
}

.input-error:focus {
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.1) !important;
}

.error-message {
  font-size: 0.8rem;
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: -0.25rem;
}

/* ===== DROPDOWN STYLES ===== */
:deep(.field-dropdown .p-dropdown) {
  height: 52px !important;
  width: 100% !important;
}

:deep(.field-dropdown .p-dropdown-label) {
  padding: 0 !important;
  height: 100% !important;
  display: flex !important;
  align-items: center !important;
}

.dropdown-selected,
.dropdown-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.dropdown-icon {
  font-size: 1.1rem;
  color: #168f04;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.dropdown-label {
  font-size: 0.95rem;
  color: #1e293b;
  font-weight: 500;
}

.dropdown-placeholder {
  color: #94a3b8;
  font-size: 0.95rem;
}

:deep(.p-dropdown-panel) {
  border-radius: 14px !important;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15) !important;
  border: 1px solid rgba(22, 143, 4, 0.2) !important;
  margin-top: 8px !important;
}

:deep(.p-dropdown-item) {
  padding: 0.75rem 1rem !important;
  font-size: 0.95rem !important;
  border-radius: 8px !important;
  margin: 2px 8px !important;
  transition: all 0.2s ease !important;
}

:deep(.p-dropdown-item:hover) {
  background: rgba(22, 143, 4, 0.08) !important;
  color: #168f04 !important;
}

:deep(.p-dropdown-item.p-highlight) {
  background: linear-gradient(135deg, #168f04, #0d5a02) !important;
  color: white !important;
}

:deep(.p-dropdown-filter-container) {
  padding: 0.75rem 1rem !important;
  border-bottom: 1px solid #e2e8f0 !important;
}

:deep(.p-dropdown-filter) {
  border-radius: 8px !important;
  border: 1px solid #cbd5e1 !important;
  padding: 0.5rem 0.75rem !important;
  font-size: 0.9rem !important;
}

/* ===== FOOTER ===== */
.modal-footer {
  padding: 1rem 2rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-cancel {
  height: 48px !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  padding: 0 1.5rem !important;
}

.btn-submit {
  height: 48px !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  font-size: 0.95rem !important;
  padding: 0 1.5rem !important;
  background: linear-gradient(135deg, #168f04 0%, #0d5a02 100%) !important;
  border: none !important;
  box-shadow: 0 4px 12px rgba(22, 143, 4, 0.25) !important;
  transition: all 0.3s ease !important;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(22, 143, 4, 0.35) !important;
}

.btn-submit:active:not(:disabled) {
  transform: translateY(0);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* ===== BUTTON OVERRIDES ===== */
:deep(.p-button) {
  transition: all 0.3s ease !important;
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

/* ===== ANIMATIONS ===== */
.modal-body {
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ===== RESPONSIVE ===== */
@media (max-width: 576px) {
  .modal-header {
    padding: 1.5rem 1.5rem 1rem;
  }
  
  .modal-body {
    padding: 1.25rem 1.5rem;
  }
  
  .modal-footer {
    padding: 0.75rem 1.5rem 1.25rem;
  }
  
  .footer-actions {
    flex-direction: column-reverse;
  }
  
  .btn-cancel,
  .btn-submit {
    width: 100% !important;
  }
  
  .modal-title {
    font-size: 1.25rem;
  }
  
  .header-icon {
    width: 60px;
    height: 60px;
  }
  
  .header-icon i {
    font-size: 1.5rem;
  }
}

/* ===== SCROLLBAR ===== */
.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: transparent;
}

.modal-body::-webkit-scrollbar-thumb {
  background: rgba(22, 143, 4, 0.3);
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: rgba(22, 143, 4, 0.5);
}
</style>