<template>
  <nav class="navbar">
    <router-link to="/" class="logo">ComfortUfa</router-link>
    <div class="links">
      <router-link to="/">Главная</router-link>
      <router-link to="/map">Карта</router-link>
      <router-link to="/admin">Админка</router-link>
    </div>
  </nav>
  
  <main>
    <router-view />
  </main>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 30px;
  background: #1E40AF;
  color: white;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.links a {
  margin-left: 20px;
  color: white;
  text-decoration: none;
}

.links a:hover {
  text-decoration: underline;
}

main {
  padding: 20px;
}
</style>