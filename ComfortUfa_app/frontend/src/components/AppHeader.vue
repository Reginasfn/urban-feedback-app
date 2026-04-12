<script>
import LoginModal from '@/components/modals/LoginModal.vue'
import RegisterModal from '@/components/modals/RegisterModal.vue'
import Toast from 'primevue/toast'

export default {
    name: 'AppHeader',
    components: {
        LoginModal,
        RegisterModal,
        Toast
    },
    data() {
        return {
            navItems: [
                { label: 'КАРТА', path: '/map' },
                { label: 'О ПРОЕКТЕ', path: '/about' }
            ],
            isAuth: false,
            showLoginModal: false,
            showRegisterModal: false,
            currentUser: null
        }
    },
    computed: {
        headerClass() {
            const isMapPage = this.$route.path === '/map'
            return {
                'header': true,
                'header--fixed': !isMapPage,
                'header--sticky': isMapPage
            }
        }
    },
    mounted() {
        // 👇 ПРОВЕРЯЕМ АВТОРИЗАЦИЮ ПРИ ЗАГРУЗКЕ
        this.checkAuth()
        
        // 👇 Слушаем события изменения авторизации (для других компонентов)
        window.addEventListener('auth-change', this.handleAuthChange)
    },
    
    beforeUnmount() {
        // 👇 Очищаем слушатель
        window.removeEventListener('auth-change', this.handleAuthChange)
    },

    methods: {
        // 👇 Проверка авторизации при загрузке
        checkAuth() {
            const token = localStorage.getItem('auth_token')
            const user = localStorage.getItem('user')
            
            if (token && user) {
                this.isAuth = true
                try {
                    this.currentUser = JSON.parse(user)
                } catch {
                    this.currentUser = null
                }
                console.log('✅ Пользователь авторизован:', this.currentUser)
            } else {
                this.isAuth = false
                this.currentUser = null
                console.log('❌ Пользователь не авторизован')
            }
        },

        // 👇 Обработчик события изменения авторизации (для синхронизации с другими компонентами)
        handleAuthChange(event) {
            const newAuthState = event.detail.isAuthenticated
            
            // Обновляем только если состояние реально изменилось
            if (this.isAuth !== newAuthState) {
                this.isAuth = newAuthState
                
                if (!newAuthState) {
                    // При выходе очищаем данные
                    this.currentUser = null
                    if (this.$route.path !== '/' && this.$route.path !== '/map') {
                        this.$router.push('/')
                    }
                }
                // При входе currentUser уже установлен в handleLogin — не перезаписываем
            }
        },

        handleProfileClick() {
            console.log('👤 handleProfileClick, isAuth:', this.isAuth)
            
            if (!this.isAuth) {
                this.showLoginModal = true
            } else {
                this.$router.push('/profile')
            }
        },
        
        handleFavoritesClick() {
            if (!this.isAuth) {
                this.$toast.add({
                    severity: 'warn',
                    summary: 'Требуется авторизация',
                    detail: 'Чтобы перейти в избранное, войдите в систему',
                    life: 3000,
                    styleClass: 'my-big-toast'
                })
            } else {
                this.$router.push('/favorites')
            }
        },

        // 👇 ОБНОВЛЁННЫЙ handleLogin — гарантированное обновление состояния
        async handleLogin(credentials) {
            console.log('🔑 handleLogin вызван с:', credentials)
            
            try {
                // 🔐 Данные уже сохранены в LoginModal, берём из localStorage
                const token = localStorage.getItem('auth_token')
                const userData = localStorage.getItem('user')
                
                if (!token || !userData) {
                    throw new Error('Токен или данные пользователя не сохранены')
                }
                
                const user = JSON.parse(userData)
                
                // 👇 ПРЯМО обновляем локальное состояние
                this.isAuth = true
                this.currentUser = user
                
                // 👇 Ждём обновления Vue
                await this.$nextTick()
                
                // 👇 Сообщаем другим компонентам
                window.dispatchEvent(new CustomEvent('auth-change', { 
                    detail: { isAuthenticated: true } 
                }))
                
                this.showLoginModal = false

                this.$router.push('/profile')
                
            } catch (error) {
                console.error('Login error:', error)
                this.$toast.add({
                    severity: 'error',
                    summary: 'Ошибка входа',
                    detail: error.message || 'Неверный email или пароль',
                    life: 4000,
                    styleClass: 'my-error-toast'
                })
            }
        },

        // 👇 ОБНОВЛЁННЫЙ handleLogout — тоже с $nextTick
        handleLogout() {
            localStorage.removeItem('auth_token')
            localStorage.removeItem('user')
            
            // 👇 1. Сначала обновляем локальное состояние
            this.isAuth = false
            this.currentUser = null
            
            // 👇 2. Ждём обновления шаблона
            this.$nextTick(() => {
                // 👇 3. Потом сообщаем другим компонентам
                window.dispatchEvent(new CustomEvent('auth-change', { 
                    detail: { isAuthenticated: false } 
                }))
            })
            
            this.$toast.add({
                severity: 'info',
                summary: 'Выход',
                detail: 'Вы вышли из системы',
                life: 2000,
                styleClass: 'my-info-toast'
            })
            
            if (this.$route.path !== '/' && this.$route.path !== '/map') {
                this.$router.push('/')
            }
        },

        handleCloseModal() {
            this.showLoginModal = false
            this.showRegisterModal = false
        },
        
        handleRegisterClick() {
            this.showLoginModal = false
            this.$router.push('/register')
        },
        
        handleSwitchToRegister() {
            this.showLoginModal = false
            setTimeout(() => {
                this.showRegisterModal = true
            }, 180)
        },
        
        handleSwitchToLogin() {
            this.showRegisterModal = false
            setTimeout(() => {
                this.showLoginModal = true
            }, 180)
        },
        
        handleRegister(credentials) {
            console.log('REGISTER:', credentials)
            this.showRegisterModal = false
            this.showLoginModal = true
        }
    }
}
</script>

<template>
    <header :class="headerClass">
        <!-- ВЕРХНЯЯ ЧАСТЬ ШАПКИ -->
        <div class="header-top">
            <div class="container">
                
                <!-- Логотип -->
                <div class="logo" @click="$router.push('/')">
                    <img src="@/assets/icons/logoIcon.svg" alt="ComfortUfa" class="logo-img">
                    <div class="logo-text">
                        <span class="logo-title">Комфортная</span>
                        <span class="logo-subtitle">Уфа</span>
                    </div>
                </div>

                <!-- Навигация -->
                <nav class="nav">
                    <router-link 
                        v-for="item in navItems" 
                        :key="item.path"
                        :to="item.path" 
                        class="nav-link"
                        active-class="active"
                    >
                        {{ item.label }}
                    </router-link>
                </nav>

                <!-- Иконки справа -->
                <div class="header-icons">
                    <!-- Кнопка "Избранное" — всегда видна -->
                    <button class="icon-btn" title="Избранное" @click="handleFavoritesClick">
                        <i class="pi pi-bookmark"></i>
                    </button>

                    <!-- Кнопка "Профиль" — всегда видна, но разное поведение -->
                    <button class="icon-btn" :title="isAuth ? 'Мой профиль' : 'Войти'" @click="handleProfileClick">
                        <i class="pi pi-user"></i>
                    </button>

                    <!-- Кнопка "Выйти" — только если авторизован -->
                    <button 
                        v-if="isAuth" 
                        class="icon-btn" 
                        title="Выйти" 
                        @click="handleLogout"
                    >
                        <i class="pi pi-sign-out"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- НИЖНЯЯ ПОЛОСКА -->
        <div class="header-bottom">
            <div class="container">
                <div class="bottom-text">
                    <p>ПЛАТФОРМА ДЛЯ ОЦЕНКИ БЛАГОУСТРОЙСТВА ГОРОДА УФЫ</p>
                </div>
            </div>
        </div>
    </header>

    <!-- Уведомления -->
    <Toast/>

    <!-- Модальные окна -->
    <LoginModal
        :visible="showLoginModal"
        @update:visible="showLoginModal = $event"
        @login="handleLogin"
        @close="handleCloseModal"
        @register="handleRegisterClick"
        @switch-to-register="handleSwitchToRegister"
    />

    <RegisterModal
        :visible="showRegisterModal"
        @update:visible="showRegisterModal = $event"
        @register="handleRegister"
        @switch-to-login="handleSwitchToLogin"
    />
</template>

<style scoped>
/* ===================== ОБЩИЕ СТИЛИ ===================== */
.header {
    background: rgba(170, 182, 177, 0.2); 
    backdrop-filter: blur(20px);
    z-index: 1000;
    border-bottom: 1px solid rgba(30, 58, 95, 0.1);
}

.header--fixed{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
}

.header--sticky {
    position: static;
    top: 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

/* ===================== ВЕРХНЯЯ ЧАСТЬ ===================== */
.header-top {
    padding: 15px 0px 0px 0px;
}

.header-top .container {
    display: flex;
    align-items: center;
    gap: 40px;
}

/* Логотип */
.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
}

.logo-img {
    width: 70px;
    height: 70px;
}

.logo-text {
    display: flex;
    flex-direction: column;
    line-height: 1.2;
}

.logo-title {
    font-size: 21px;
    font-weight: 800;
    color: #1e3a5f;
    letter-spacing: 1px;
}

.logo-subtitle {
    font-size: 22px;
    font-weight: 900;
    color: #1e5f39;
    letter-spacing: 1px;
}

/* ===================== НИЖНЯЯ ПОЛОСКА ===================== */
.header-bottom {
    position: relative;
    padding: 9px 0px;
    margin-top: 10px;
    margin-bottom: 2px;
}

.header-bottom::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 85%; 
    height: 2px;
    background-color: #0b4a00;
}

.bottom-text p {
    color: #1e3a5f;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin: 0;
    line-height: 1.4;
}

/* ===================== НАВИГАЦИЯ ===================== */
.nav {
    display: flex;
    gap: 25px;
    flex: 1;
    justify-content: center;
    padding: 0px 80px 0px 0px;
}

.nav-link {
    text-decoration: none;
    color: #1e3a5f;
    font-weight: 645;
    font-size: 15px;
    letter-spacing: 0.5px;
    padding: 8px 16px;
    border-radius: 50px;
    position: relative;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    background: transparent;
}

.nav-link:hover {
    color: #168f04;
    background: rgba(0, 146, 5, 0.08);
    transform: translateY(-1px);
}

.nav-link.active {
    color: #168f04;
    font-weight: 640;
    background: rgba(0, 146, 5, 0.08);
}

.nav-link.active::after {
    content: '';
    position: absolute;
    bottom: 4px;
    left: 50%;
    transform: translateX(-50%) scaleX(0);
    width: 60%;
    height: 2px;
    background: #168f04;
    border-radius: 2px;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-link.active::after {
    transform: translateX(-50%) scaleX(1);
}

/* ===================== ИКОНКИ ===================== */
.header-icons {
    display: flex;
    gap: 30px;
}

.icon-btn {
    width: 40px;
    height: 40px;
    border: 2px solid #1e3a5f;
    background: transparent;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.5s;
    color: #1e3a5f;
}

.icon-btn:hover {
    background: #025f09;
    color: white;
}

.icon-btn i {
    font-size: 19px;
}
</style>