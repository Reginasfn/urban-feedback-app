<template>
  <Dialog 
    v-model:visible="isVisible" 
    header="Добавить объект" 
    :modal="true" 
    :closable="true"
    :style="{ width: '480px' }"
    :pt="{
      header: { class: 'bg-white border-b border-gray-200' },
      content: { class: 'bg-white' },
      footer: { class: 'bg-white border-t border-gray-200' }
    }"
    @hide="onCancel"
    style="font-family: monospace"
  >
    <div class="object-form">
      <!-- Информация о локации -->
<!-- Информация о локации -->
      <div class="location-info">
        <i class="pi pi-map-marker"></i>
        <div>
          <strong>Координаты:</strong>
          <span class="coords">{{ formattedCoords }}</span>
          <span v-if="props.address" class="address-text">
            <i class="pi pi-home"></i> {{ props.address }}
          </span>
        </div>
      </div>

      <!-- Название объекта -->
      <div class="form-group">
        <label class="form-label">Название объекта *</label>
        <InputText 
          v-model="formData.name" 
          placeholder="Введите название.." 
          class="w-full"
          :maxlength="100"
          @keyup.enter="onSubmit"
        />
        <small v-if="errors.name" class="error-text">{{ errors.name }}</small>
      </div>

      <!-- Тип объекта -->
      <div class="form-group">
        <label class="form-label">Тип объекта *</label>
        <Dropdown 
          v-model="formData.type" 
          :options="availableTypes"
          optionLabel="label"
          optionValue="value"
          placeholder="Выберите тип..."
          class="w-full"
          :class="{ 'p-invalid': errors.type }"
          style="font-family: monospace;"
        />
        <small v-if="errors.type" class="error-text">{{ errors.type }}</small>
      </div>
    </div>

    <template #footer>
      <div class="object-actions">
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
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'

// ===== Props =====
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  coordinates: {
    type: Array,
    required: false,  // Сделай необязательным
    validator: (val) => {
      // Разрешаем null или массив из 2 чисел
      if (val === null) return true
      return val.length === 2 && typeof val[0] === 'number' && typeof val[1] === 'number'
    }
  },
  address: { type: String, default: '' },
  availableTypes: {
    type: Array,
    default: () => [
      { label: 'Камера видеонаблюдения', value: 'Камера видеонаблюдения' },
      { label: 'Кафе', value: 'Кафе' },
      { label: 'Фонарь', value: 'Фонарь' },
      { label: 'Скамейка', value: 'Скамейка' },
      { label: 'Парк', value: 'Парк' },
      { label: 'Беседка', value: 'Беседка' },
      { label: 'Остановка', value: 'Остановка' },
      { label: 'Детская площадка', value: 'Детская площадка' }
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
  type: null,
  description: ''
})

const errors = ref({})
const submitting = ref(false)

// ===== Форматирование координат =====
const formattedCoords = computed(() => {
  // 👇 ДОБАВЬ ПРОВЕРКУ НА NULL
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

  if (name) {
    errors.value.name = 'Введите корректное название'
  } 
  
  else if (name.length < 3) {
    errors.value.name = 'Минимум 3 символа'
  }

  else if (/^\d+$/.test(name)) {
    errors.value.name = 'Название должно содержать буквы'
  }
  
  if (!formData.value.type) {
    errors.value.type = 'Выберите тип объекта'
  }
  
  return Object.keys(errors.value).length === 0
}

// ===== Обработчики =====
const onCancel = () => {
  if (submitting.value) return
  emit('cancel')
  resetForm()
  isVisible.value = false
}

const resetForm = () => {
  formData.value = { name: '', type: null, description: '' }
  errors.value = {}
}

const onSubmit = async () => {
  if (!validate()) return
  
  submitting.value = true
  
  try {
    // Подготовка данных для отправки
    const payload = {
      name: formData.value.name.trim(),
      type: formData.value.type,
      description: formData.value.description?.trim() || null,
      coords: props.coordinates // [lat, lon]
    }
    
    // Отправляем данные родителю
    emit('submit', payload)
    
    // Закрываем модалку после успешной отправки
    isVisible.value = false
    
  } catch (err) {
    console.error('[ObjectModal] Ошибка при подготовке данных:', err)
    emit('error', { message: 'Не удалось подготовить данные' })
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

// ===== Экспортируем методы для родителя =====
defineExpose({
  resetForm
})
</script>

<style scoped>
/* === ФОРМА ДОБАВЛЕНИЯ ОБЪЕКТА === */
.object-form { font-family: monospace; display: flex; flex-direction: column; gap: 18px; padding: 8px 4px; }

/* Информация о локации */
.location-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(22, 143, 4, 0.08);
  border-radius: 12px;
  border: 1px solid rgba(22, 143, 4, 0.2);
}
.location-info i {
  font-size: 22px;
  color: #168f04;
  background: rgba(22, 143, 4, 0.15);
  padding: 8px;
  border-radius: 10px;
}
.location-info strong {
  display: block;
  font-size: 16px;
  color: #334155;
}
.coords {
  font-size: 14px;
  color: #168f04;
  font-weight: 600;
  font-family: monospace;
}

/* Группы полей */
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { 
  font-size: 15px; 
  font-weight: 600; 
  color: #334155;
}
.error-text {
  font-size: 14px;
  color: #dc2626;
  margin-top: -4px;
}

/* === СТИЛИ ДЛЯ PRIMEVUE === */
:deep(.p-inputtext) { 
  border-radius: 12px; 
  border: 2px solid #e2e8f0; 
  transition: border-color 0.5s; 
  padding: 0.75rem 1rem;
}
:deep(.p-inputtext:focus) { 
  border-color: #168f04; 
  box-shadow: 0 0 0 4px rgba(22,143,4,0.12); 
}
:deep(.p-inputtext.p-invalid) {
  border-color: #dc2626;
}
:deep(.p-dropdown) { 
  border-radius: 12px; 
  border: 2px solid #e2e8f0;
}
:deep(.p-dropdown:focus-within) { 
  border-color: #168f04; 
  box-shadow: 0 0 0 4px rgba(22,143,4,0.12); 
}
:deep(.p-dropdown.p-invalid) {
  border-color: #dc2626;
}
:deep(.p-button) { 
  border-radius: 10px; 
  font-weight: 600;
  font-size: 16px;
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