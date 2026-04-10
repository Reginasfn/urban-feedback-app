<script>
    import Dialog from 'primevue/dialog'
    import InputText from 'primevue/inputtext'
    import Password from 'primevue/password'
    import Button from 'primevue/button'
    import Toast from 'primevue/toast'
    import IftaLabel from 'primevue/iftalabel';

    export default {
        name: 'AppHeader',

        components:{
            Dialog,
            InputText,
            Password,
            Button,
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

                email: '',
                password: ''
            }
        },

        computed:{
            //динамический класс
            headerClass(){
                const isMapPage = this.$route.path === '/map'
                console.log('Текущий путь:', this.$route.path, '| Карта?', isMapPage)

                return {
                    'header': true,
                    'header--fixed': !isMapPage, //на всех страницах кроме карты
                    'header--sticky': isMapPage
                }
            }
        },

        methods:{
            handleProfileClick(){
                if (!this.isAuth){
                    this.showLoginModal = true
                }
                else{
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
                        styleClass: 'my-big-toast' // Твой личный класс
                    })
                } 
                else {
                    this.$router.push('/favorites')
                }
            },

            login(){
                if (!this.email || !this.password){
                    this.$toast.add({
                        severity: 'error',
                        summary: 'Ошибка',
                        detail: 'Заполните email и пароль',
                        life: 3000
                    })
                    return
                }
                this.isAuth = true;

                this.$toast.add({
                    severity: 'success',
                    summary: 'Успешно',
                    detail: 'Вы вошли в систему',
                    life: 3000
                })

                this.showLoginModal = false
                this.$router.push('/profile')
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

    <!-- Модальное окно авторизации -->
<!-- Модальное окно авторизации -->

    <Dialog 
        v-model:visible="showLoginModal" 
        modal 
        header="Вход в ComfortUfa"
        :style="{ width: '420px' }"
        :pt="{
            root: { class: 'custom-dialog' },
            header: { class: 'dialog-header' },
            content: { class: 'dialog-content' },
            footer: { class: 'dialog-footer' }
        }"
    >
        <form @submit.prevent="login" class="login-form">
            
            <!-- Email поле -->
            <div class="form-group">
                <label for="email">Email</label>
                <InputText 
                    id="email" 
                    v-model="email" 
                    type="email"
                    placeholder="vash@email.ru"
                    class="custom-input"
                    :class="{ 'error': !email && submitted }"
                />
                <span v-if="!email && submitted" class="error-msg">Введите email</span>
            </div>

            <!-- Пароль поле -->
            <div class="form-group">
                <label for="password">Пароль</label>
                <Password 
                    id="password"
                    v-model="password" 
                    toggleMask 
                    placeholder="••••••••"
                    class="custom-input"
                    :class="{ 'error': !password && submitted }"
                    :feedback="false"
                />
                <span v-if="!password && submitted" class="error-msg">Введите пароль</span>
            </div>

            <!-- Запомнить меня + Забыли пароль -->
            <div class="form-options">
                <label class="checkbox-label">
                    <input type="checkbox" v-model="rememberMe">
                    <span>Запомнить меня</span>
                </label>
                <a href="#" class="forgot-link">Забыли пароль?</a>
            </div>

            <!-- Кнопка входа -->
            <Button 
                type="submit"
                label="Войти" 
                class="btn-login"
                :loading="loggingIn"
                :disabled="loggingIn"
            />

            <!-- Ссылка на регистрацию -->
            <div class="register-link">
                <span>Нет аккаунта?</span>
                <a @click.prevent="goToRegister">Зарегистрироваться</a>
            </div>

        </form>
    </Dialog>

</template>

<style>
/* Стили для портала Toast */
.p-toast .my-big-toast {
    background: #ffffffc8 !important; /* Чистый белый фон для современности */
    backdrop-filter: blur(20px) !important;
    border-left: 8px solid #f59e0b !important; /* Жирная золотистая полоса слева */
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1) !important; /* Глубокая мягкая тень */
    border-radius: 12px !important; /* Скругленные углы */
    min-width: 400px !important; /* Делаем его широким */
}

/* Контейнер внутри тоста */
.my-big-toast .p-toast-message-content {
    padding: 15px !important; /* Увеличиваем внутренние отступы */
    align-items: center !important; /* Центрируем иконку и текст */
}

/* Заголовок (Summary) */
.my-big-toast .p-toast-summary {
    font-size: 18px !important; /* Крупный размер */
    font-weight: 700 !important; /* Очень жирный шрифт */
    color: #b45100 !important; /* Почти черный цвет */
    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important; /* Современный шрифт */
    display: block;
    margin-bottom: 0px !important; /* Отступ от описания */
}

/* Описание (Detail) */
.my-big-toast .p-toast-detail {
    font-size: 16px !important; /* Увеличиваем текст */
    color: #b45100 !important; /* Темно-серый */
}

/* Иконка (если используешь) */
.my-big-toast .p-toast-message-icon {
    height: 30px;
    width: 30px;
    color: #f59e0b !important; /* Золотой цвет под полоску */
    margin-right: 5px !important;
}

/* Кнопка закрытия (крестик) */
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
        transform: translateX(-50%); /* Центрируем линию */
        
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

    .login-form {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }

    .register-link {
        margin-top: 15px;
        text-align: center;
        font-size: 14px;
    }

    .register-link a {
        color: #168f04;
        cursor: pointer;
        margin-left: 5px;
        font-weight: 600;
    }

    .register-link a:hover {
        text-decoration: underline;
    }

    /* ===================== МОДАЛЬНОЕ ОКНО (PrimeVue Dialog) ===================== */

/* Глобальные стили для Dialog (вне scoped) */
:deep(.custom-dialog.p-dialog) {
    border-radius: 20px !important;
    border: none !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25) !important;
    overflow: hidden;
}

/* Заголовок модального окна */
:deep(.dialog-header.p-dialog-header) {
    background: linear-gradient(135deg, #168f04 0%, #1e5f39 100%) !important;
    color: white !important;
    padding: 20px 24px !important;
    font-weight: 700 !important;
    font-size: 18px !important;
    border-bottom: none !important;
}

:deep(.dialog-header .p-dialog-title) {
    color: white !important;
}

:deep(.dialog-header .p-dialog-header-close) {
    color: rgba(255, 255, 255, 0.9) !important;
    width: 32px !important;
    height: 32px !important;
    border-radius: 8px !important;
    transition: background 0.3s !important;
}

:deep(.dialog-header .p-dialog-header-close:hover) {
    background: rgba(255, 255, 255, 0.2) !important;
}

/* Контент модального окна */
:deep(.dialog-content.p-dialog-content) {
    padding: 24px !important;
    background: #ffffff !important;
}

/* ===================== ФОРМА ВХОДА ===================== */
.login-form {
    display: flex;
    flex-direction: column;
    gap: 18px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.form-group label {
    font-size: 14px;
    font-weight: 600;
    color: #1e3a5f;
    margin-left: 4px;
}

/* Кастомные инпуты */
:deep(.custom-input.p-inputtext) {
    border: 2px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    background: #f8fafc !important;
}

:deep(.custom-input.p-inputtext:hover) {
    border-color: #cbd5e1 !important;
}

:deep(.custom-input.p-inputtext:focus) {
    border-color: #168f04 !important;
    background: white !important;
    box-shadow: 0 0 0 4px rgba(22, 143, 4, 0.1) !important;
}

:deep(.custom-input.error.p-inputtext) {
    border-color: #ef4444 !important;
    background: #fef2f2 !important;
}

/* Сообщения об ошибках */
.error-msg {
    font-size: 12px;
    color: #ef4444;
    margin-left: 4px;
    font-weight: 500;
}

/* Password toggle button */
:deep(.custom-input .p-password-toggle-mask-icon) {
    color: #64748b !important;
}

/* Опции формы (запомнить + забыли пароль) */
.form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 4px;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: #64748b;
    cursor: pointer;
    user-select: none;
}

.checkbox-label input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: #168f04;
    cursor: pointer;
    border-radius: 4px;
}

.forgot-link {
    font-size: 14px;
    color: #168f04;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s;
}

.forgot-link:hover {
    color: #1e5f39;
    text-decoration: underline;
}

/* Кнопка входа */
:deep(.btn-login.p-button) {
    background: linear-gradient(135deg, #168f04 0%, #1e5f39 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    color: white !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 14px rgba(22, 143, 4, 0.3) !important;
    margin-top: 8px !important;
}

:deep(.btn-login.p-button:hover) {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(22, 143, 4, 0.4) !important;
    background: linear-gradient(135deg, #147a03 0%, #1a5233 100%) !important;
}

:deep(.btn-login.p-button:active) {
    transform: translateY(0) !important;
    box-shadow: 0 2px 8px rgba(22, 143, 4, 0.3) !important;
}

:deep(.btn-login.p-button:disabled) {
    opacity: 0.7 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* Ссылка на регистрацию */
.register-link {
    text-align: center;
    font-size: 14px;
    color: #64748b;
    padding-top: 8px;
    border-top: 1px solid #e2e8f0;
}

.register-link a {
    color: #168f04;
    cursor: pointer;
    margin-left: 4px;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.3s;
}

.register-link a:hover {
    color: #1e5f39;
    text-decoration: underline;
}

/* ===================== АДАПТИВНОСТЬ ===================== */
@media (max-width: 480px) {
    :deep(.custom-dialog.p-dialog) {
        width: 95% !important;
        margin: 20px !important;
    }
    
    .form-options {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
    }
}
</style>