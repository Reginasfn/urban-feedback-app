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
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  ::-webkit-scrollbar {
    width: 0;
    background: transparent;
  }

 #app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #1a1a1a;
  
  /* 👇 ФОН ПЕРЕНОСИМ СЮДА. Он будет на весь экран, включая область под футером */
  background: url('@/assets/backgr1.jpg') center/cover no-repeat fixed;
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
    padding: 140px 20px 20px;
    flex: 1;
  }
</style>