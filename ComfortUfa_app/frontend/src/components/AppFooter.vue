<template>
  <footer class="footer">
    <div class="footer-content">
      <!-- О проекте -->
      <div class="footer-section">
        <h4>ComfortUfa</h4>
        <p>Платформа для оценки благоустройства города Уфы</p>
      </div>
      
      <!-- Разделы -->
      <div class="footer-section">
        <h4>Разделы</h4>
        <router-link to="/map">Карта</router-link>
        <router-link to="/objects">Объекты</router-link>
        <router-link to="/rating">Рейтинг</router-link>
        <router-link to="/admin">Админ-панель</router-link>
      </div>
      
      <!-- Информация -->
      <div class="footer-section">
        <h4>Информация</h4>
        <router-link to="/about">О проекте</router-link>
        <router-link to="/rules">Правила</router-link>
        <router-link to="/faq">Вопросы</router-link>
        <router-link to="/contacts">Контакты</router-link>
      </div>
      
      <!-- Контакты -->
      <div class="footer-section">
        <h4>Контакты</h4>
        <p>📧 info@comfortufa.ru</p>
        <p>📞 +7 (347) 000-00-00</p>
        <p>📍 г. Уфа, ул. Ленина, 10</p>
      </div>
    </div>
    
    <!-- Нижняя строка -->
    <div class="footer-bottom">
      <p>&copy; 2026 ComfortUfa. Все права защищены.</p>
      <p class="disclaimer">Проект создан в рамках дипломной работы</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter'
}
</script>

<style scoped>
/* ===================== ФУТЕР ===================== */
.footer {
  background: #1a1a1a;
  color: white;
  padding: 60px 20px 30px;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 40px;
}

.footer-section h4 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 20px;
  color: #fbbf24;
}

.footer-section p,
.footer-section a {
  color: #9ca3af;
  text-decoration: none;
  display: block;
  margin-bottom: 10px;
  transition: color 0.3s;
  line-height: 1.6;
}

.footer-section a:hover {
  color: white;
}

.footer-bottom {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 30px;
  border-top: 1px solid #374151;
  text-align: center;
  color: #6b7280;
}

.footer-bottom .disclaimer {
  font-size: 13px;
  margin-top: 10px;
  opacity: 0.7;
}

/* ===================== АДАПТИВНОСТЬ ===================== */
@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .footer-section a,
  .footer-section p {
    display: inline-block;
    margin: 5px 10px;
  }
}
</style>