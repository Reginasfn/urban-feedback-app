<template>
  <div class="home">
    <!-- ===================== ГЕРОЙ-СЕКЦИЯ ===================== -->
    <section class="hero">

      <div class="hero-container">
        
        <!-- ЛЕВАЯ ЧАСТЬ: Текст -->
        <div class="hero-content">
          <h1 class="hero-title">
            Вместе делаем Уфу<br>
            <span class="highlight">комфортнее!</span>
          </h1>
          <h2 class="hero-subtitle">
            Система для улучшения <br> городской среды.<br>
            Сообщайте о проблемах, вносите предложения, выражайте благодарность!
          </h2>
          
          <div class="hero-actions">
            <router-link to="/map" class="btn btn-large btn-primary">
              Оценить объект
            </router-link>
          </div>

        </div>

        <!-- ПРАВАЯ ЧАСТЬ: Изображение Салавата -->
        <div class="hero-image">
          <img src="/images/salavat.png" alt="Салават Юлаев" class="salavat-img">
        </div>

      </div>

      <!-- Статистика портала (снизу на всю ширину) -->
      <div class="hero-stats">

        <div class="stat-card">
          <div class="stat-number">
            <span v-if="loadingStats" class="loading">...</span>
            <span v-else>{{ stats.marks.toLocaleString() }}</span>
          </div>

          <div class="stat-label">Объектов на карте</div>
        </div>

        <div class="stat-card">
          <div class="stat-number">
            <span v-if="loadingStats" class="loading">...</span>
            <span v-else>{{ stats.solved.toLocaleString() }}</span>
          </div>

          <div class="stat-label">Выявлено проблем</div>
        </div>

        <div class="stat-card">
          <div class="stat-number">
            <span v-if="loadingStats" class="loading">...</span>
            <span v-else>{{ stats.users.toLocaleString() }}</span>
          </div>

          <div class="stat-label">Пользователей присоединилось</div>
        </div>

      </div>
    </section>

    <!-- ===================== АКТИВНЫЕ ТЕМЫ ===================== -->
    <section class="active-topics">
      <div class="topics-container">
        <h2 class="section-title">Актуальные проблемы</h2>
        <p class="section-subtitle">Какие категории волнуют жителей Уфы прямо сейчас?</p>
        
        <div class="topics-grid">
          
          <!-- К1 - Парки и скверы -->
          <div class="topic-card">
            <div class="topic-icon-wrapper">
              <svg class="topic-svg-icon" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" xml:space="preserve">
                <g>
                  <path class="st0" d="M422.969,193.281c2.313-7.922,3.594-16.313,3.594-24.969c0-42.469-29.375-78.063-68.875-87.844 C346.813,34.406,305.438,0,256,0s-90.813,34.406-101.75,80.469c-39.438,9.781-68.813,45.375-68.813,87.844 c0,8.656,1.281,17.047,3.594,24.969C64.313,212.469,48.406,242.313,48.406,276c0,57.75,46.781,104.563,104.563,104.563 c14.625,0,28.563-2.969,41.188-8.406c1.922,1.594,3.844,3.125,5.844,4.563V512h112V376.641c2-1.438,3.922-2.891,5.75-4.484 c12.719,5.438,26.656,8.406,41.281,8.406c57.781,0,104.563-46.813,104.563-104.563 C463.594,242.313,447.688,212.469,422.969,193.281z M280,480h-48v-88.156c7.688,2,15.688,3.031,24,3.031s16.313-1.031,24-3.031V480 z M359.031,348.563c-9.906,0-19.5-1.922-28.625-5.844l-18.156-7.844l-0.25,0.25l-14.875,12.625 c-5.203,4.328-10.969,7.844-17.125,10.328c-7.594,3.125-15.688,4.797-24,4.797s-16.406-1.672-24-4.797 c-6.156-2.484-11.922-6-17.125-10.328L200,335.125l-0.25-0.25l-18.156,7.844c-9.125,3.922-18.719,5.844-28.625,5.844 c-40,0-72.563-32.563-72.563-72.563c0-22.563,10.234-43.438,28.234-57.359l17.109-13.281l-6-20.891 c-1.5-5.438-2.313-10.875-2.313-16.156c0-26.953,18.313-50.313,44.484-56.719l18.953-4.719l4.563-19.031 C193.188,54.969,222.25,32,256,32s62.813,22.969,70.563,55.844l4.469,19.031l19.047,4.719 c26.172,6.406,44.484,29.766,44.484,56.719c0,5.281-0.813,10.719-2.313,16.156l-6,20.891l17.109,13.281 c18,13.922,28.234,34.797,28.234,57.359C431.594,316,399.031,348.563,359.031,348.563z"></path>
                </g>
              </svg>
            </div>
            <div class="topic-content">
              <h4>Парки и скверы</h4>
              <p>Некачественное содержание территорий, мусор, старые дорожки</p>
            </div>
          </div>

          <!-- К2 - Дороги и тротуары -->
          <div class="topic-card">
            <div class="topic-icon-wrapper">
              <i class="pi pi-directions"></i>
            </div>
            <div class="topic-content">
              <h4>Дороги и тротуары</h4>
              <p>Ямы, выбоины, повреждение асфальтового покрытия</p>
            </div>
          </div>

          <!-- К3 - Дворовые территории -->
          <div class="topic-card">
            <div class="topic-icon-wrapper">
              <i class="pi pi-home"></i>
            </div>
            <div class="topic-content">
              <h4>Дворовые территории</h4>
              <p>Неубранные дворы, проблемы с освещением и шумом</p>
            </div>
          </div>

          <!-- К4 - Уличное освещение -->
          <div class="topic-card">
            <div class="topic-icon-wrapper">
              <i class="pi pi-lightbulb"></i>
            </div>
            <div class="topic-content">
              <h4>Уличное освещение</h4>
              <p>Неисправные фонари, тёмные участки во дворах</p>
            </div>
          </div>

        </div>
      </div>
    </section>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HomeView',
  data() {
    return {
      stats: { marks: 0, solved: 0, users: 0 },
      loadingStats: true,
      statsError: null
    }
  }, 

  async mounted() {
    await this.fetchStats()
    
    // 👇 Слушаем событие обновления статистики
    window.addEventListener('stats-refresh', this.fetchStats)
  },
  
  beforeUnmount() {
    // 👇 Очищаем слушатель при уходе со страницы
    window.removeEventListener('stats-refresh', this.fetchStats)
  },

  methods: {
    async fetchStats() {
      try {
        this.loadingStats = true
        this.statsError = null

        const response = await axios.get('http://localhost:8000/api/stats')
        this.stats = {
          marks: response.data.total_objects,
          solved: response.data.total_problems,
          users: response.data.total_users
        }
        console.log('✅ Статистика обновлена:', this.stats)
      }
      catch (error) {
        console.error('❌ Ошибка:', error)
        this.statsError = 'Не удалось загрузить статистику'
      }
      finally {
        this.loadingStats = false
      }
    }
  }
}

</script>

<style scoped>
/* ===================== ОБЩИЕ СТИЛИ ===================== */
.loading {
  display: inline-block;
  width: 40px;
  text-align: center;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}
.home {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #1a1a1a;
  line-height: 1.6;
}

/* ===================== КНОПКИ ===================== */
.btn {
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
}

.btn-primary {
  background: transparent;
  border-color: #168f04;
  color: #168f04;
}

.btn-primary:hover {
  background: #168f04;
  color: white;
  box-shadow: 0 8px 20px rgba(22, 143, 4, 0.4);
}

.btn-primary:active {
  box-shadow: 0 4px 10px rgba(22, 143, 4, 0.3);
}

.btn-large {
  padding: 20px 30px;
  font-size: 18px;
  font-weight: 700;
}

/* ===================== ГЕРОЙ-СЕКЦИЯ ===================== */
.hero {
  position: relative;
}

.hero-container {
  max-width: 1200px;
  margin: -140px auto 0;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 60px;
  min-height: 500px;
  position: relative;
  overflow: visible;
}

/* ЛЕВАЯ ЧАСТЬ: Текст */
.hero-content {
  flex: 1;
  max-width: 600px;
  color: rgb(0, 83, 40);
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 0 0 20px;
}

.hero-title {
  font-size: 52px;
  font-weight: 900;
  margin: 60px 0px 0px 0px;
  line-height: 1.1;
  color: rgb(28, 25, 88);
  text-transform: uppercase;
}

.highlight {
  color: #007306;
  display: block;
}

.hero-subtitle {
  font-size: 22px;
  margin-bottom: 0px;
  opacity: 0.95;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  justify-content: flex-start;
  margin-top: 20px;
  z-index: 10;
}

/* ПРАВАЯ ЧАСТЬ: Изображение */
.hero-image {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  z-index: 1;
}

.salavat-img {
  max-height: 700px;
  width: auto;
  filter: drop-shadow(0 20px 40px rgba(0, 0, 0, 0.3));
  transform: translateY(50px);
}

/* Статистика (снизу) */
.hero-stats {
  max-width: 1200px;
  margin: -60px auto 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  padding: 0 40px 60px;
  position: relative;
  z-index: 3;
}

.stat-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(70px);
  padding: 30px 20px;
  border-radius: 16px;
  border: 1px solid rgba(2, 142, 0, 0.2);
  text-align: center;
  color: rgba(4, 67, 0, 0.941);
}

.stat-number {
  font-size: 27px;
  font-weight: 800;
}

.stat-label{
  font-family: monospace;
  font-size: 20px;
}


/* ===================== АКТУАЛЬНЫЕ ПРОБЛЕМЫ ===================== */
.active-topics {
  padding: 30px 20px 100px 20px;
  background: transparent;
}

.topics-container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 36px;
  font-weight: 800;
  color: rgb(0, 83, 40);
  margin-bottom: 10px;
}

.section-subtitle {
  text-align: center;
  color: #00540e;
  font-size: 18px;
  margin-bottom: 50px;
}

.topics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 25px;
}

/* Карточка */
.topic-card {
  background: rgba(30, 95, 63, 0.358);
  border-radius: 20px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: relative;
  border: 1px solid #e2e8f0;
  transition: all 0.9s cubic-bezier(0.25, 0.8, 0.25, 1);
  cursor: pointer;
  color: white;
}

/* Эффект при наведении */
.topic-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e1;
}

/* Иконка в кружочке */
.topic-icon-wrapper {
  width: 55px;
  height: 55px;
  background: #174a1c4a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  transition: background 0.3s;
}

.topic-card:hover .topic-icon-wrapper {
  background: #dcfce7;
}

.topic-icon-wrapper i {
  font-size: 28px;
  color: #003a16;
}

.topic-content {
  text-align: center;
  width: 100%;
}

/* Текст */
.topic-content h4 {
  font-size: 18px;
  font-weight: 900;
  color: #1b462b;
  margin-bottom: 10px;
}

.topic-content p {
  color: #003a16;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 25px;
  flex-grow: 1;
  font-weight: 600;
}

/* Стили для SVG иконки */
.topic-svg-icon {
  width: 32px;
  height: 32px;
  fill: #003a16;
  transition: fill 0.3s;
}

</style>