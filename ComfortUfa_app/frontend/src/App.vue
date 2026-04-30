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
  <div id="app">
    <AppHeader />
    
    <main class="main-content" :class="{ 'map-page': $route.path === '/map'}">
      <router-view />
    </main>
    
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

  #app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #1a1a1a;
    background: url('@/assets/backgr1.jpg') center/cover no-repeat fixed;
  }
  
  html {
    scroll-behavior: smooth;
  }

  a {
    text-decoration: none;
    color: inherit;
  }

  button {
    font-family: inherit;
  }

  .main-content {
    flex: 1;
    padding: 20px;
  }

  .main-content:not(.map-page){
    padding-top: 140px;
  }

  .main-content.map-page{
    padding-top: 50px;
    padding-bottom: 300px;

  }

</style>