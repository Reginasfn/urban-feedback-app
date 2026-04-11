// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// PrimeVue
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import ToastService from 'primevue/toastservice'

// Компоненты
import Avatar from 'primevue/avatar'
import IftaLabel from 'primevue/iftalabel'

// Глобальные стили
import './styles/toasts.css'

// ✅ Добавляем Vue в global для vuefy
import * as VueLib from 'vue'
window.Vue = VueLib

const app = createApp(App)

app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: { darkModeSelector: false }
    }
})
app.use(ToastService)
app.use(router)

app.component('Avatar', Avatar)
app.component('IftaLabel', IftaLabel)

app.mount('#app')