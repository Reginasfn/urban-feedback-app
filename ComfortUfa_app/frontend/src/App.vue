<script>
  import AppHeader from './components/AppHeader.vue'
  import AppFooter from './components/AppFooter.vue'

  export default {
    name: 'App',
    components: {
      AppHeader,
      AppFooter
    }
  }

</script>

<template>
  <!-- <nav class="navbar">
    <router-link to="/" class="logo">ComfortUfa</router-link>
    <div class="links">
      <router-link to="/">Главная</router-link>
      <router-link to="/map">Карта</router-link>
      <router-link to="/profile">Профиль</router-link>
    </div>
  </nav> -->
  <div id="app">
    <AppHeader />
    
    <!-- Основной контент (меняется через router-view) -->
    <main class="main-content">
      <router-view />
    </main>
    
    <!-- Подключаем футер -->
    <AppFooter />
  </div>
</template>

<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  #app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #1a1a1a;

    
  }
  
  /* Плавная прокрутка */
  html {
    scroll-behavior: smooth;
  }

  /* Убираем стандартные отступы у ссылок */
  a {
    text-decoration: none;
    color: inherit;
  }

  /* Убираем стандартные стили кнопок */
  button {
    font-family: inherit;
  }

  .main-content {
    padding: 160px 20px 20px 20px;
    background-image: url('@/assets/backgr1.jpg');
    background-size: cover;           /* Растягивает на весь экран */
    background-repeat: no-repeat;     /* Убирает повторение */
    background-position: center;      /* Центрирует изображение */
    min-height: 100vh;                /* Минимальная высота = высота экрана */
    background-attachment: fixed;     /* Фиксирует фон при прокрутке (опционально) */
    flex: 1;
  }
</style>