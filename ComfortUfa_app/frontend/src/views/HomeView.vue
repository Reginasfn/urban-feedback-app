<template>
  <div class="home">
    <h1>🏙 ComfortUfa</h1>
    <p>Платформа для оценки благоустройства Уфы</p>
    <router-link to="/map" class="btn">Открыть карту</router-link>
  </div>
</template>

<style scoped>
.home {
  text-align: center;
  padding: 50px;
}
.btn {
  display: inline-block;
  margin-top: 20px;
  padding: 10px 20px;
  background: #1E40AF;
  color: white;
  text-decoration: none;
  border-radius: 5px;
}
</style>