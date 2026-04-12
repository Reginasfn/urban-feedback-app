<template>
  <div class="profile-page">
    
    <!-- Заголовок страницы -->
    <div class="profile-header">
      <div class="container">
        <h1 class="page-title">Личный профиль</h1>
        <p class="page-subtitle">Управляйте своими данными и настройками</p>
      </div>
    </div>

    <!-- Основной контент -->
    <div class="container">
      <div class="profile-grid">
        
        <!-- Карточка профиля -->
        <Card class="profile-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-user"></i>
              <span>Мои данные</span>
            </div>
          </template>
          
          <template #content>
            <!-- Режим просмотра -->
            <div v-if="!isEditing" class="profile-view">
              <div class="profile-field">
                <label>Никнейм</label>
                <p class="field-value">{{ profile.nickname || 'Не указан' }}</p>
              </div>
              
              <div class="profile-field">
                <label>Email</label>
                <p class="field-value">{{ profile.email }}</p>
              </div>
              
              <div class="profile-field">
                <label>Телефон</label>
                <p class="field-value">{{ profile.phone || 'Не указан' }}</p>
              </div>
              
              <div class="profile-field">
                <label>Роль</label>
                <Tag :value="profile.role_name || 'user'" severity="success" />
              </div>
              
              <div class="profile-field">
                <label>Дата регистрации</label>
                <p class="field-value">{{ formatDate(profile.created_at) }}</p>
              </div>
              
              <Button 
                label="Редактировать" 
                @click="startEditing" 
                class="btn-edit"
                severity="secondary"
              />
            </div>

            <!-- Режим редактирования -->
            <div v-else class="profile-edit">
              <div class="form-group">
                <label for="nickname">Никнейм *</label>
                <InputText 
                  id="nickname" 
                  v-model="form.nickname" 
                  placeholder="Ваш никнейм"
                  :class="{ 'p-invalid': errors.nickname }"
                />
                <small v-if="errors.nickname" class="p-error">{{ errors.nickname }}</small>
              </div>
              
              <div class="form-group">
                <label for="email">Email *</label>
                <InputText 
                  id="email" 
                  v-model="form.email" 
                  type="email"
                  placeholder="your@email.com"
                  :class="{ 'p-invalid': errors.email }"
                />
                <small v-if="errors.email" class="p-error">{{ errors.email }}</small>
              </div>
              
              <div class="form-group">
                <label for="phone">Телефон</label>
                <InputMask 
                  id="phone" 
                  v-model="form.phone" 
                  mask="+7 (999) 999-99-99"
                  placeholder="+7 (___) ___-__-__"
                />
              </div>

              <!-- Блок смены пароля -->
              <Divider align="left">
                <span class="divider-text">Сменить пароль</span>
              </Divider>
              
              <div class="form-group">
                <label for="current_password">Текущий пароль</label>
                <Password 
                  id="current_password"
                  v-model="form.current_password"
                  toggleMask
                  :feedback="false"
                  placeholder="••••••••"
                />
                <small v-if="errors.current_password" class="p-error">{{ errors.current_password }}</small>
              </div>
              
              <div class="form-group">
                <label for="new_password">Новый пароль</label>
                <Password 
                  id="new_password"
                  v-model="form.new_password"
                  toggleMask
                  weakLabel="Слабый"
                  mediumLabel="Средний"
                  strongLabel="Сильный"
                  placeholder="Минимум 6 символов"
                />
                <small class="hint-text">Оставьте пустым, если не меняете пароль</small>
              </div>
              
              <div class="edit-actions">
                <Button 
                  label="Сохранить" 
                  @click="saveProfile" 
                  :loading="saving"
                  class="btn-save"
                />
                <Button 
                  label="Отмена" 
                  @click="cancelEditing" 
                  severity="secondary"
                  class="btn-cancel"
                />
              </div>
            </div>
          </template>
        </Card>

        <!-- Боковая панель: статистика и действия -->
        <div class="profile-sidebar">
          
          <!-- Статистика пользователя -->
          <Card class="stats-card">
            <template #title>
              <div class="card-title">
                <i class="pi pi-chart-bar"></i>
                <span>Моя активность</span>
              </div>
            </template>
            <template #content>
              <div v-if="loadingActivity" class="loading-stats">
                <i class="pi pi-spin pi-spinner"></i>
                <span>Загрузка...</span>
              </div>
              <div v-else class="stats-grid">
                <div class="stat-item">
                  <span class="stat-value">{{ activity.total_reviews }}</span>
                  <span class="stat-label">Отзывов</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ activity.total_favorites }}</span>
                  <span class="stat-label">В избранном</span>
                </div>
                <div class="stat-item">
                  <span class="stat-value">{{ activity.total_objects_added }}</span>
                  <span class="stat-label">Объектов добавлено</span>
                </div>
              </div>
            </template>
          </Card>

          <!-- Опасная зона -->
          <Card class="danger-card">
            <template #title>
              <div class="card-title danger">
                <i class="pi pi-exclamation-triangle"></i>
                <span>Безопасность</span>
              </div>
            </template>
            <template #content>
              <Button 
                label="Выйти из аккаунта" 
                @click="handleLogout" 
                severity="danger" 
                class="btn-logout"
              />
            </template>
          </Card>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import InputMask from 'primevue/inputmask'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Divider from 'primevue/divider'

export default {
  name: 'ProfileView',
  components: { Card, InputText, InputMask, Password, Button, Tag, Divider },
  
  data() {
    return {
      profile: {
        id_user: null,
        email: '',
        nickname: '',
        phone: '',
        role_name: '',
        created_at: null
      },
      activity: {
        total_reviews: 0,
        total_favorites: 0,
        total_objects_added: 0
      },
      form: {
        nickname: '',
        email: '',
        phone: '',
        current_password: '',
        new_password: ''
      },
      errors: {},
      isEditing: false,
      saving: false,
      loading: true,
      loadingActivity: true
    }
  },
  
  async mounted() {
    // 🔐 Проверка авторизации
    const token = localStorage.getItem('auth_token')
    if (!token) {
      this.$router.push('/auth')
      return
    }
    
    await Promise.all([
      this.fetchProfile(),
      this.fetchActivity()
    ])
  },
  
  methods: {
    // 👇 Загрузка данных профиля
    async fetchProfile() {
      try {
        this.loading = true
        const response = await axios.get('http://localhost:8000/api/users/me', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
        })
        
        this.profile = response.data
        this.form = {
          nickname: response.data.nickname,
          email: response.data.email,
          phone: response.data.phone,
          current_password: '',
          new_password: ''
        }
      } catch (error) {
        console.error('Ошибка загрузки профиля:', error)
        
        if (error.response?.status === 401) {
          this.handleLogout()
          return
        }
        
        this.$toast?.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: 'Не удалось загрузить данные профиля',
          life: 3000
        })
      } finally {
        this.loading = false
      }
    },
    
    // 👇 Загрузка статистики активности
    async fetchActivity() {
      try {
        this.loadingActivity = true
        const response = await axios.get('http://localhost:8000/api/users/me/activity', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
        })
        
        this.activity = response.data
      } catch (error) {
        console.error('Ошибка загрузки активности:', error)
        // Если таблица ещё не создана — ставим нули
        this.activity = {
          total_reviews: 0,
          total_favorites: 0,
          total_objects_added: 0
        }
      } finally {
        this.loadingActivity = false
      }
    },
    
    // 👇 Начало редактирования
    startEditing() {
      this.isEditing = true
      this.errors = {}
      this.form.current_password = ''
      this.form.new_password = ''
    },
    
    // 👇 Отмена редактирования
    cancelEditing() {
      this.isEditing = false
      this.errors = {}
      this.form = {
        nickname: this.profile.nickname,
        email: this.profile.email,
        phone: this.profile.phone,
        current_password: '',
        new_password: ''
      }
    },
    
    // 👇 Валидация формы
    validateForm() {
      this.errors = {}
      
      if (!this.form.nickname?.trim()) {
        this.errors.nickname = 'Введите никнейм'
      } 
      else if (this.form.nickname.length < 3) {
        this.errors.nickname = 'Минимум 3 символа'
      } 
      // 👇 НОВАЯ ПРОВЕРКА: только буквы (кириллица/латиница) и цифры
      else if (!/^[a-zA-Zа-яА-ЯёЁ0-9]+$/.test(this.form.nickname.trim())) {
        this.errors.nickname = 'Только буквы и цифры, без пробелов и спецсимволов'
      }
      
      if (!this.form.email?.trim()) {
        this.errors.email = 'Введите email'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.form.email)) {
        this.errors.email = 'Некорректный email'
      }
      
      // Если меняем пароль — нужен текущий
      if (this.form.new_password && !this.form.current_password) {
        this.errors.current_password = 'Введите текущий пароль для подтверждения'
      }
      
      return Object.keys(this.errors).length === 0
    },
    
    // 👇 Сохранение изменений
    async saveProfile() {
      if (!this.validateForm()) {
        this.$toast?.add({
          severity: 'warn',
          summary: 'Проверьте форму',
          detail: 'Исправьте ошибки в полях',
          life: 3000
        })
        return
      }
      
      this.saving = true
      
      try {
        const payload = {}
        
        // Отправляем только изменённые поля
        if (this.form.nickname !== this.profile.nickname) {
          payload.nickname = this.form.nickname.trim()
        }
        if (this.form.email !== this.profile.email) {
          payload.email = this.form.email.trim().toLowerCase()
        }
        if (this.form.phone !== this.profile.phone) {
          payload.phone = this.form.phone || null
        }
        if (this.form.current_password) {
          payload.current_password = this.form.current_password
        }
        if (this.form.new_password) {
          payload.new_password = this.form.new_password
        }
        
        // Если ничего не меняем
        if (Object.keys(payload).length === 0) {
          this.$toast?.add({
            severity: 'info',
            summary: 'Информация',
            detail: 'Нет изменений для сохранения',
            life: 2000
          })
          this.cancelEditing()
          return
        }
        
        // Запрос к бэкенду
        const response = await axios.put(
          'http://localhost:8000/api/users/me',
          new URLSearchParams(payload),
          {
            headers: { 
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
              'Content-Type': 'application/x-www-form-urlencoded'
            }
          }
        )
        
        // Обновляем локальные данные
        this.profile = response.data
        
        // Обновляем localStorage
        localStorage.setItem('user', JSON.stringify({
          id: response.data.id_user,
          nickname: response.data.nickname,
          role: response.data.role_name
        }))
        
        // Сообщаем другим компонентам
        window.dispatchEvent(new CustomEvent('user-updated', {
          detail: { user: response.data }
        }))
        
        this.isEditing = false
        this.$toast?.add({
          severity: 'success',
          summary: 'Успешно',
          detail: 'Данные профиля обновлены',
          life: 3000
        })
        
      } catch (error) {
        console.error('Ошибка сохранения:', error)
        
        const message = error.response?.data?.detail || 'Не удалось сохранить изменения'
        
        this.$toast?.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: message,
          life: 4000
        })
      } finally {
        this.saving = false
      }
    },
    
    // 👇 Выход из системы
    handleLogout() {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      
      window.dispatchEvent(new CustomEvent('auth-change', { 
        detail: { isAuthenticated: false } 
      }))
      
      this.$toast?.add({
        severity: 'info',
        summary: 'Выход',
        detail: 'Вы вышли из системы',
        life: 2000
      })
      
      this.$router.push('/')
    },
    
    // 👇 Форматирование даты
    formatDate(dateString) {
      if (!dateString) return '—'
      return new Date(dateString).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }
  }
}
</script>

<style scoped>
/* ===================== ОБЩИЕ СТИЛИ ===================== */
.profile-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #1a1a1a;
  min-height: 100vh;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  padding-bottom: 60px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* ===================== ЗАГОЛОВОК ===================== */
.profile-header {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  padding: 40px 0;
  border-bottom: 1px solid rgba(22, 143, 4, 0.15);
  margin-bottom: 40px;
}

.page-title {
  font-size: 36px;
  font-weight: 800;
  color: #1e3a5f;
  margin: 0 0 8px;
  text-align: center;
}

.page-subtitle {
  color: #64748b;
  font-size: 16px;
  margin: 0;
  text-align: center;
}

/* ===================== СЕТКА ПРОФИЛЯ ===================== */
.profile-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  align-items: start;
}

@media (max-width: 900px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

/* ===================== КАРТОЧКИ ===================== */
:deep(.p-card) {
  border-radius: 20px !important;
  border: 1px solid rgba(22, 143, 4, 0.15) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08) !important;
  background: rgba(255, 255, 255, 0.9) !important;
}

:deep(.p-card-title) {
  padding: 20px 24px !important;
  border-bottom: 1px solid rgba(22, 143, 4, 0.1) !important;
}

:deep(.p-card-content) {
  padding: 24px !important;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #1e3a5f;
}

.card-title i {
  font-size: 20px;
  color: #168f04;
}

.card-title.danger i {
  color: #dc2626;
}

/* ===================== ПРОСМОТР ПРОФИЛЯ ===================== */
.profile-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.profile-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(22, 143, 4, 0.1);
}

.profile-field:last-child {
  border-bottom: none;
}

.profile-field label {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
}

.field-value {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a1a;
  text-align: right;
  margin: 0;
}

.btn-edit {
  margin-top: 8px;
  width: 100%;
  border-radius: 12px !important;
}

/* ===================== РЕДАКТИРОВАНИЕ ===================== */
.profile-edit {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

:deep(.p-inputtext),
:deep(.p-inputmask),
:deep(.p-password) {
  width: 100%;
  border-radius: 12px !important;
  border: 2px solid #e2e8f0 !important;
  transition: border-color 0.3s !important;
}

:deep(.p-inputtext:focus),
:deep(.p-inputmask:focus),
:deep(.p-password :focus) {
  border-color: #168f04 !important;
  box-shadow: 0 0 0 4px rgba(22, 143, 4, 0.1) !important;
}

.p-error {
  color: #dc2626 !important;
  font-size: 12px !important;
}

.hint-text {
  color: #64748b;
  font-size: 11px;
  margin-top: 4px;
}

.edit-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.btn-save,
.btn-cancel {
  flex: 1;
  border-radius: 12px !important;
}

/* ===================== СТАТИСТИКА ===================== */
.loading-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #64748b;
  padding: 20px 0;
}

.loading-stats i {
  font-size: 20px;
  color: #168f04;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: #168f04;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
}

/* ===================== ОПАСНАЯ ЗОНА ===================== */
.danger-card :deep(.p-card) {
  border-color: rgba(220, 38, 38, 0.2) !important;
}

.btn-logout {
  width: 100%;
  border-radius: 12px !important;
}

/* ===================== DIVIDER ===================== */
:deep(.p-divider .p-divider-content) {
  background: #fff !important;
  padding: 0 12px !important;
}

.divider-text {
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
}

:deep(.p-divider) {
  border-color: rgba(22, 143, 4, 0.1) !important;
  margin: 8px 0 !important;
}
</style>