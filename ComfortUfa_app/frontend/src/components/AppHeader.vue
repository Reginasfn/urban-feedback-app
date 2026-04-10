<script>
import LoginModal from '@/components/modals/LoginModal.vue'
import Toast from 'primevue/toast'

export default {
    name: 'AppHeader',
    components: {
        LoginModal,
        Toast
    },
    data() {
        return {
            navItems: [
                { label: 'КАРТА', path: '/map' },
                { label: 'О ПРОЕКТЕ', path: '/about' }
            ],
            isAuth: false,
            showLoginModal: false
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
    methods: {
        handleProfileClick() {
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
        async handleLogin(credentials) {
            if (!credentials.email || !credentials.password) {
                this.$toast.add({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Заполните email и пароль',
                    life: 3000
                })
                return
            }

            try {
                this.isAuth = true
                this.showLoginModal = false

                this.$toast.add({
                    severity: 'success',
                    summary: 'Успешно',
                    detail: 'Вы вошли в систему',
                    life: 3000
                })

                this.$router.push('/profile')

            } catch (error) {
                this.$toast.add({
                    severity: 'error',
                    summary: 'Ошибка входа',
                    detail: 'Неверный email или пароль',
                    life: 4000
                })
            }
        },
        handleCloseModal() {},
        handleRegisterClick() {
            this.showLoginModal = false
            this.$router.push('/register')
        }
    }
}
</script>

<template>
  <header :class="headerClass">
    <!-- ВЕРХНЯЯ ЧАСТЬ ШАПКИ -->
    <div class="header-top">
      <div class="container">
        
        <!-- Логотип с картинкой -->
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
          <button class="icon-btn" title="Избранное" @click="handleFavoritesClick">
            <i class="pi pi-bookmark"></i>
          </button>
          <button class="icon-btn" title="Профиль" @click="handleProfileClick">
            <i class="pi pi-user"></i>
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

  <!-- Уведомление -->
  <Toast/>

  <!-- Используем компонент LoginModal -->
  <LoginModal
    :visible="showLoginModal"
    @update:visible="showLoginModal = $event"
    @login="handleLogin"
    @close="handleCloseModal"
    @register="handleRegisterClick"
  />
</template>

<style>
/* Стили для портала Toast */
.p-toast .my-big-toast {
    background: #ffffffc8 !important;
    backdrop-filter: blur(20px) !important;
    border-left: 8px solid #f59e0b !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1) !important;
    border-radius: 12px !important;
    min-width: 400px !important;
}

.my-big-toast .p-toast-message-content {
    padding: 15px !important;
    align-items: center !important;
}

.my-big-toast .p-toast-summary {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #b45100 !important;
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    display: block;
    margin-bottom: 0px !important;
}

.my-big-toast .p-toast-detail {
    font-size: 16px !important;
    color: #b45100 !important;
}

.my-big-toast .p-toast-message-icon {
    height: 30px;
    width: 30px;
    color: #f59e0b !important;
    margin-right: 5px !important;
}

.my-big-toast .p-toast-icon-close {
    color: #9ca3af !important;
}
</style>

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

    /* Картинка логотипа */
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

    /* Активный пункт меню */
    .nav-link.active {
        color: #168f04;
        font-weight: 640;
        background: rgba(0, 146, 5, 0.08);
    }

    /* Подчеркивание (Анимация из центра) */
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

    /* Активируем анимацию */
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