<script>
    export default {
        name: 'HomeView',
        data() {
            return {
            // Здесь можно добавить реактивные данные для статистики
            stats: {
                marks: 1234,
                solved: 856,
                users: 3421
            }
            }
        }
    }
</script>

<template>
  <div class="home">
    <!-- ===================== ГЕРОЙ-СЕКЦИЯ ===================== -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">
          Вместе делаем Уфу<br>
          <span class="highlight">комфортнее!</span>
        </h1>
        <p class="hero-subtitle">
          Платформа для оценки благоустройства города.<br>
          Сообщайте о проблемах и предлагайте улучшения
        </p>
        
        <!-- Основные кнопки действий -->
        <div class="hero-actions">
          <router-link to="/map" class="btn btn-large btn-primary">
            📍 Открыть карту
          </router-link>
          <button class="btn btn-large btn-outline">
            ℹ️ Как это работает?
          </button>
        </div>
      </div>

      <!-- Статистика портала -->
      <div class="hero-stats">
        <div class="stat-card">
          <div class="stat-number">1,234</div>
          <div class="stat-label">Отметок на карте</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">856</div>
          <div class="stat-label">Решено проблем</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">3,421</div>
          <div class="stat-label">Пользователей</div>
        </div>
      </div>
    </section>

    <!-- ===================== ВОЗМОЖНОСТИ ПОРТАЛА ===================== -->
    <section class="features">
      <h2 class="section-title">Возможности платформы</h2>
      
      <div class="features-grid">
        <!-- Карточка 1 -->
        <div class="feature-card">
          <div class="feature-icon">📍</div>
          <h3 class="feature-title">Отмечайте на карте</h3>
          <p class="feature-text">
            Найдите объект на интерактивной карте Яндекса и оставьте отметку о проблеме
          </p>
        </div>

        <!-- Карточка 2 -->
        <div class="feature-card">
          <div class="feature-icon">📝</div>
          <h3 class="feature-title">Оставляйте отзывы</h3>
          <p class="feature-text">
            Опишите проблему подробно, добавьте фотографии и оценку состояния
          </p>
        </div>

        <!-- Карточка 3 -->
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3 class="feature-title">Следите за решением</h3>
          <p class="feature-text">
            Отслеживайте статус рассмотрения вашей заявки в реальном времени
          </p>
        </div>

        <!-- Карточка 4 -->
        <div class="feature-card">
          <div class="feature-icon">🏆</div>
          <h3 class="feature-title">Участвуйте в рейтинге</h3>
          <p class="feature-text">
            Зарабатывайте баллы за активность и поднимайтесь в топе пользователей
          </p>
        </div>
      </div>
    </section>

    <!-- ===================== АКТИВНЫЕ ТЕМЫ ===================== -->
    <section class="active-topics">
      <h2 class="section-title">Актуальные проблемы</h2>
      
      <div class="topics-grid">
        <div class="topic-card">
          <div class="topic-icon">🌳</div>
          <div class="topic-content">
            <h4>Парки и скверы</h4>
            <p>Некачественное содержание территорий</p>
            <span class="topic-count">124 проблемы</span>
          </div>
        </div>

        <div class="topic-card">
          <div class="topic-icon">🛣</div>
          <div class="topic-content">
            <h4>Дороги и тротуары</h4>
            <p>Ямы, выбоины, повреждения покрытия</p>
            <span class="topic-count">89 проблем</span>
          </div>
        </div>

        <div class="topic-card">
          <div class="topic-icon">🏡</div>
          <div class="topic-content">
            <h4>Дворовые территории</h4>
            <p>Неубранные дворы, освещение</p>
            <span class="topic-count">156 проблем</span>
          </div>
        </div>

        <div class="topic-card">
          <div class="topic-icon">💡</div>
          <div class="topic-content">
            <h4>Уличное освещение</h4>
            <p>Неисправные фонари, темные участки</p>
            <span class="topic-count">67 проблем</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===================== КАК ЭТО РАБОТАЕТ ===================== -->
    <section class="how-it-works">
      <h2 class="section-title">Как это работает?</h2>
      
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <h4>Найдите объект</h4>
          <p>Откройте карту и найдите проблемный объект в Уфе</p>
        </div>

        <div class="step">
          <div class="step-number">2</div>
          <h4>Оставьте отметку</h4>
          <p>Добавьте фото, описание и категорию проблемы</p>
        </div>

        <div class="step">
          <div class="step-number">3</div>
          <h4>Ожидайте решения</h4>
          <p>Администрация рассмотрит и примет меры</p>
        </div>
      </div>
    </section>

    <!-- ===================== ПРИЗЫВ К ДЕЙСТВИЮ ===================== -->
    <section class="cta">
      <div class="cta-content">
        <h2>Готовы сделать Уфу лучше?</h2>
        <p>Присоединяйтесь к тысячам активных жителей города</p>
        <router-link to="/map" class="btn btn-large btn-white">
          Начать прямо сейчас
        </router-link>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ===================== ОБЩИЕ СТИЛИ ===================== */
.home {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #1a1a1a;
  line-height: 1.6;
}

/* ===================== КНОПКИ ===================== */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-outline {
  background: transparent;
  color: #2563eb;
  border: 2px solid #2563eb;
}

.btn-outline:hover {
  background: #2563eb;
  color: white;
}

.btn-large {
  padding: 15px 30px;
  font-size: 16px;
}

.btn-white {
  background: white;
  color: #2563eb;
}

.btn-white:hover {
  background: #f3f4f6;
  transform: translateY(-2px);
}

/* ===================== ГЕРОЙ-СЕКЦИЯ ===================== */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto 60px;
}

.hero-title {
  font-size: 48px;
  font-weight: 800;
  margin-bottom: 20px;
  line-height: 1.2;
}

.highlight {
  color: #fbbf24;
}

.hero-subtitle {
  font-size: 20px;
  margin-bottom: 40px;
  opacity: 0.95;
}

.hero-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

/* Статистика */
.hero-stats {
  max-width: 1000px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  padding: 30px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-number {
  font-size: 42px;
  font-weight: 800;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 16px;
  opacity: 0.9;
}

/* ===================== СЕКЦИИ ===================== */
.features,
.active-topics,
.how-it-works {
  padding: 80px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 50px;
  color: #1a1a1a;
}

/* ===================== КАРТОЧКИ ВОЗМОЖНОСТЕЙ ===================== */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 16px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 15px;
  color: #1a1a1a;
}

.feature-text {
  color: #6b7280;
  line-height: 1.6;
}

/* ===================== АКТИВНЫЕ ТЕМЫ ===================== */
.active-topics {
  background: #f9fafb;
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.topic-card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  display: flex;
  gap: 20px;
  align-items: flex-start;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s;
}

.topic-card:hover {
  transform: translateX(5px);
}

.topic-icon {
  font-size: 40px;
}

.topic-content h4 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 5px;
  color: #1a1a1a;
}

.topic-content p {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 10px;
}

.topic-count {
  display: inline-block;
  background: #fee2e2;
  color: #dc2626;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

/* ===================== КАК ЭТО РАБОТАЕТ ===================== */
.steps {
  display: flex;
  justify-content: space-between;
  gap: 40px;
  flex-wrap: wrap;
}

.step {
  flex: 1;
  min-width: 250px;
  text-align: center;
  position: relative;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  margin: 0 auto 20px;
}

.step h4 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #1a1a1a;
}

.step p {
  color: #6b7280;
  line-height: 1.6;
}

/* ===================== ПРИЗЫВ К ДЕЙСТВИЮ ===================== */
.cta {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 100px 20px;
  text-align: center;
  color: white;
}

.cta-content h2 {
  font-size: 42px;
  font-weight: 800;
  margin-bottom: 15px;
}

.cta-content p {
  font-size: 20px;
  margin-bottom: 30px;
  opacity: 0.95;
}


/* ===================== АДАПТИВНОСТЬ ===================== */
@media (max-width: 768px) {
  .header-container {
    flex-direction: column;
    gap: 15px;
  }

  .nav {
    flex-wrap: wrap;
    justify-content: center;
    gap: 15px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .section-title {
    font-size: 28px;
  }

  .features-grid,
  .topics-grid {
    grid-template-columns: 1fr;
  }

  .steps {
    flex-direction: column;
  }
}
</style>