// src/main.js
import { createApp, ref, shallowRef } from 'vue'
import App from './App.vue'
import router from './router'

// PRIMEVUE CORE
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'

// ИКОНКИ
import 'primeicons/primeicons.css'

// ТЕМА
import Aura from '@primevue/themes/aura'

// PRIMEVUE COMPONENTS
import Button from 'primevue/button'
import Card from 'primevue/card'
import Toast from 'primevue/toast'
import ProgressSpinner from 'primevue/progressspinner'
import Avatar from 'primevue/avatar'
import IftaLabel from 'primevue/iftalabel'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import InputText from 'primevue/inputtext'
import InputMask from 'primevue/inputmask'
import Password from 'primevue/password'
import Tag from 'primevue/tag'
import Divider from 'primevue/divider'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'

// СТИЛИ УВЕДОМЛЕНИЙ
import './styles/toasts.css'

// СОСТОЯНИЕ МОДАЛКИ
export const modalState = {
  visible: ref(false),
  currentObject: shallowRef(null),
  
  async open(objectId) {
    try {
      const response = await fetch(`/api/objects/${objectId}`)
      if (!response.ok) throw new Error('Failed to fetch')
      const data = await response.json()
      this.currentObject.value = data
      this.visible.value = true
    } catch (err) {
      console.error('[Modal] Error loading object:', err)
      this.currentObject.value = { 
        id_object: objectId, 
        name: 'Объект #' + objectId, 
        address: 'Адрес не указан',
        type_name: 'Не указан'
      }
      this.visible.value = true
    }
  },
  
  close() {
    this.visible.value = false
    setTimeout(() => {
      this.currentObject.value = null
    }, 300)
  }
}

window.__openObjectDetails = (id) => {
  modalState.open(id)
}

// СОЗДАНИЕ ПРИЛОЖЕНИЯ
const app = createApp(App)

// НАСТРОЙКА PRIMEVUE
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: false,
    }
  }
})
import Popover from 'primevue/popover'
app.component('Popover', Popover)
app.use(ToastService)
app.use(router)

// РЕГИСТРАЦИЯ КОМПОНЕНТОВ
app.component('Button', Button)
app.component('Card', Card)
app.component('Toast', Toast)
app.component('ProgressSpinner', ProgressSpinner)
app.component('Avatar', Avatar)
app.component('IftaLabel', IftaLabel)
app.component('Dialog', Dialog)
app.component('Textarea', Textarea)
app.component('InputText', InputText)
app.component('InputMask', InputMask)
app.component('Password', Password)
app.component('Tag', Tag)
app.component('Divider', Divider)
app.component('TabView', TabView)
app.component('TabPanel', TabPanel)

// ===== МОНТАЖ =====
app.mount('#app')