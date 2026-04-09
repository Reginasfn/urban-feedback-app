<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-content">
        <!-- О проекте -->
        <div class="footer-section">
          <h4 class="section-title">ComfortUfa</h4>
          <p class="section-desc">Платформа для оценки благоустройства города Уфы</p>
        </div>
        
        <!-- Разделы -->
        <div class="footer-section">
          <h4 class="section-title">Разделы</h4>
          <router-link to="/map" class="footer-link">Карта</router-link>
          <router-link to="/objects" class="footer-link">Объекты</router-link>
          <router-link to="/rating" class="footer-link">Рейтинг</router-link>
          <router-link to="/admin" class="footer-link">Админ-панель</router-link>
        </div>
        
        <!-- Информация -->
        <div class="footer-section">
          <h4 class="section-title">Информация</h4>
          <router-link to="/about" class="footer-link">О проекте</router-link>
          <router-link to="/rules" class="footer-link">Правила</router-link>
          <router-link to="/faq" class="footer-link">Вопросы</router-link>
          <router-link to="/contacts" class="footer-link">Контакты</router-link>
        </div>
        
        <!-- Контакты -->
        <div class="footer-section">
          <h4 class="section-title">Контакты</h4>
          <div class="contact-item">
            <i class="pi pi-envelope"></i>
            <span>info@comfortufa.ru</span>
          </div>
          <div class="contact-item">
            <i class="pi pi-phone"></i>
            <span>+7 (000) 000-00-00</span>
          </div>
          <div class="contact-item">
            <i class="pi pi-map-marker"></i>
            <span>г. Уфа, ул. Кирова, 65/2</span>
          </div>
        </div>
      </div>
      
      <!-- Нижняя строка -->
      <div class="footer-bottom">
        <div class="bottom-line"></div>
        <p class="copyright">&copy; 2026 ComfortUfa. Все права защищены.</p>
        <p class="disclaimer">Проект создан в рамках дипломной работы</p>
      </div>
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
  backdrop-filter: blur(50px);
  padding: 60px 0 30px;
  border-top: 1px solid rgba(10, 113, 19, 0.3); /* Тонкая линия сверху */
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 50px;
}

/* ===================== СЕКЦИИ ===================== */
.footer-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.section-title {
  font-size: 18px;
  font-weight: 800;
  color: #02541f; /* Оранжево-жёлтый как на референсе */
  margin-bottom: 10px;
  letter-spacing: 0.5px;
}

.section-desc {
  color: #007338;
  line-height: 1.6;
  font-size: 14px;
}

/* ===================== ССЫЛКИ ===================== */
.footer-link {
  color: #007338;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 4px 0;
  position: relative;
  display: inline-block;
  width: fit-content;
}

.footer-link:hover {
  color: #26a413; /* Зелёный как в хедере */
  transform: translateX(5px); /* Сдвиг вправо при наведении */
}

.footer-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 1px;
  background: #26a413;
  transition: width 0.3s ease;
}

.footer-link:hover::after {
  width: 100%;
}

/* ===================== КОНТАКТЫ ===================== */
.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #007338;
  font-size: 14px;
  transition: color 0.3s;
}

.contact-item:hover {
  color: #2ab415;
}

.contact-item i {
  font-size: 16px;
  color: #002109;
  transition: color 0.3s;
}

.contact-item:hover i {
  color: #168f04;
}

/* ===================== НИЖНЯЯ ЧАСТЬ ===================== */
.footer-bottom {
  text-align: center;
  padding-top: 30px;
}

.bottom-line {
  width: 100%;
  height: 2px;
  background: rgba(0, 87, 19, 0.5);
  margin: 0 auto 25px;
}

.copyright {
  color: #003f0b;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.disclaimer {
  color: #005e1b;
  font-size: 12px;
  opacity: 0.7;
}

</style>