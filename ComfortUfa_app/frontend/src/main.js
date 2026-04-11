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

const app = createApp(App)

app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: false
        }
    }
})

app.use(ToastService)
app.use(router)

// Глобальная регистрация
app.component('Avatar', Avatar)
app.component('IftaLabel', IftaLabel)

app.mount('#app')