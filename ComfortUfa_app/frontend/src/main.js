// src/main.js
import { createApp, ref, shallowRef } from 'vue'
import App from './App.vue'
import router from './router'

// ===== PRIMEVUE CORE =====
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import Aura from '@primeuix/themes/aura'

// ===== PRIMEVUE COMPONENTS =====
import Button from 'primevue/button'
import Card from 'primevue/card'
import Toast from 'primevue/toast'
import ProgressSpinner from 'primevue/progressspinner'
import Avatar from 'primevue/avatar'
import IftaLabel from 'primevue/iftalabel'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'

// ===== ГЛОБАЛЬНЫЕ СТИЛИ =====
import './styles/toasts.css'

// ===== 🔥 ГЛОБАЛЬНОЕ СОСТОЯНИЕ МОДАЛКИ =====
export const modalState = {
  visible: ref(false),
  currentObject: shallowRef(null),
  
  // Открыть модалку с загрузкой данных
  async open(objectId) {
    try {
      // Загружаем полные данные объекта (замените URL на ваш API)
      const response = await fetch(`/api/objects/${objectId}`)
      if (!response.ok) throw new Error('Failed to fetch')
      const data = await response.json()
      
      this.currentObject.value = data
      this.visible.value = true
    } catch (err) {
      console.error('[Modal] Error loading object:', err)
      // Показываем заглушку с минимальными данными
      this.currentObject.value = { 
        id_object: objectId, 
        name: 'Объект #' + objectId, 
        address: 'Адрес не указан',
        type_name: 'Не указан'
      }
      this.visible.value = true
    }
  },
  
  // Закрыть модалку
  close() {
    this.visible.value = false
    // Не очищаем currentObject сразу — для плавной анимации закрытия
    setTimeout(() => {
      this.currentObject.value = null
    }, 300)
  }
}

// 🔥 Глобальный колбэк для balloonRenderer.js
window.__openObjectDetails = (id) => {
  modalState.open(id)
}

// ===== СОЗДАНИЕ ПРИЛОЖЕНИЯ =====
const app = createApp(App)

// ===== НАСТРОЙКА PRIMEVUE =====
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: false,
      cssLayer: {
        name: 'primevue',
        order: 'tailwind-base, primevue, tailwind-utilities'
      }
    }
  }
})

app.use(ToastService)
app.use(router)

// ===== ГЛОБАЛЬНАЯ РЕГИСТРАЦИЯ КОМПОНЕНТОВ =====
app.component('Button', Button)
app.component('Card', Card)
app.component('Toast', Toast)
app.component('ProgressSpinner', ProgressSpinner)
app.component('Avatar', Avatar)
app.component('IftaLabel', IftaLabel)
app.component('Dialog', Dialog)
app.component('Textarea', Textarea)

// ===== МОНТАЖ =====
app.mount('#app')