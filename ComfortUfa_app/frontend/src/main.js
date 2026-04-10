import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura' // Тема
import ToastService from 'primevue/toastservice'

// Импорт компонентов (можно импортировать всё или по отдельности)
import Avatar from 'primevue/avatar'

import 'primeicons/primeicons.css'

const app = createApp(App)

app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: false // или 'system' для авто-темы
        }
    }
})

app.use(ToastService)
app.use(router)

app.component('Avatar', Avatar)

app.mount('#app')