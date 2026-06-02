<template>
  <div class="profile-page">
    
    <!-- Заголовок страницы -->
    <div class="profile-header">
      <div class="container">
        <h1 class="page-title">Личный профиль</h1>
      </div>
    </div>

    <!-- Основное содержимое -->
    <div class="container">
      
      <!-- Верхняя секция: Профиль + Статистика -->
      <div class="profile-grid">
        
        <!-- Карточка профиля (левая колонка) -->
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
                />
                <small v-if="errors.current_password" class="p-error">{{ errors.current_password }}</small>
              </div>
              
              <div class="form-group">
                <label for="new_password">Новый пароль</label>
                <Password 
                  id="new_password"
                  v-model="form.new_password"
                  toggleMask
                  promptLabel="Введите пароль"
                  weakLabel="Слабый"
                  mediumLabel="Средний"
                  strongLabel="Сильный"
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

        <!-- Правая колонка: Статистика + Выход -->
        <div class="profile-sidebar">
          
          <!-- Статистика пользователя (кликабельная) -->
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
                <div class="stat-item clickable" @click="switchToTab(0)">
                  <span class="stat-value">{{ activity.total_reviews }}</span>
                  <span class="stat-label">Отзывов</span>
                </div>
                <div class="stat-item clickable" @click="goToFavorites">
                  <span class="stat-value">{{ activity.total_favorites }}</span>
                  <span class="stat-label">В избранном</span>
                </div>
                <div class="stat-item clickable" @click="switchToTab(1)">
                  <span class="stat-value">{{ activity.total_objects_added }}</span>
                  <span class="stat-label">Объектов добавлено</span>
                </div>
              </div>
            </template>
          </Card>

          <!-- Опасная зона -->
          <Card class="danger-card">
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

      <!-- ВКЛАДКИ: ДЭШБОРД ПОЛЬЗОВАТЕЛЯ -->
      <div class="dashboard-section">
        <TabView v-model:activeIndex="activeTabIndex" class="profile-tabs" @update:activeIndex="onTabChange">
          
          <!-- Вкладка: Мои отзывы -->
          <TabPanel header="Мои отзывы">
            <!-- Фильтры и поиск -->
            <div class="filters-bar">
              <div class="filter-group">
                <i class="pi pi-search filter-icon"></i>
                <InputText 
                  v-model="reviewsSearch" 
                  placeholder="Поиск по названию или адресу..." 
                  class="filter-input"
                  @input="applyReviewsFilters"
                />
              </div>
              
              <div class="filter-group">
                <Dropdown 
                  v-model="reviewsTypeFilter" 
                  :options="uniqueReviewTypes" 
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Все типы" 
                  class="filter-dropdown"
                  @change="applyReviewsFilters"
                />
              </div>
              
              <div class="filter-group">
                <Dropdown 
                  v-model="reviewsSort" 
                  :options="sortOptions" 
                  optionLabel="label"
                  optionValue="value"
                  class="filter-dropdown"
                  @change="applyReviewsFilters"
                />
              </div>
              
              <Button 
                v-if="hasReviewsFilters"
                icon="pi pi-times" 
                label="Сбросить" 
                @click="resetReviewsFilters"
                class="filter-reset"
                severity="secondary"
                text
                size="small"
              />
            </div>
            
            <div v-if="loadingReviews" class="tab-loading">
              <i class="pi pi-spin pi-spinner"></i> Загрузка отзывов...
            </div>
            
            <div v-else-if="filteredReviews.length === 0" class="tab-empty">
              <i class="pi pi-comment"></i>
              <p>{{ reviewsSearch || reviewsTypeFilter ? 'Ничего не найдено' : 'Пока нет оставленных отзывов' }}</p>
              <Button label="Оставить первый отзыв" @click="$router.push('/map')" severity="success" size="small" />
            </div>
            
            <div v-else class="cards-grid">
              <Card v-for="review in filteredReviews" :key="review.id_review" class="data-card review-card">
                <template #content>
                  <!-- КЛИКАБЕЛЬНЫЙ ОБЪЕКТ -->
                  <div class="object-link-wrapper" @click="openObjectFromReview(review)">
                    <div class="card-header">
                      <div class="object-info">
                        <div class="object-preview">
                          <div class="object-icon-large">
                            <i :class="getTypeIcon(review.type_name || review.object_type)"></i>
                          </div>

                          <div class="object-meta-info">
                            <span class="object-type-badge">{{ review.type_name || review.object_type || 'Объект' }}</span>
                            <h4 class="object-name">{{ review.object_name }}</h4>
                            <p class="object-address">
                              <i class="pi pi-map-marker"></i> {{ review.object_address || 'Адрес не указан' }}
                            </p>
                          </div>

                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Текст отзыва -->
                  <p class="card-text">{{ review.text }}</p>
                  
                  <!-- Рейтинг + дата -->
                  <div class="card-meta">
                    <span class="rating-badge">
                      <i class="pi pi-star-fill"></i> {{ (review.rating_avg ?? review.rating ?? 0).toFixed(1) }}/5
                    </span>
                    <span class="date"><i class="pi pi-calendar"></i> {{ formatDate(review.created_at) }}</span>
                  </div>
                  
                  <!-- Действия -->
                  <div class="card-actions">
                    <Button icon="pi pi-map" label="На карте" text size="small" @click.stop="showOnMap(review)" />
                    <Button icon="pi pi-pencil" label="Изменить" text size="small" @click.stop="editReview(review)" />
                    <Button icon="pi pi-trash" label="Удалить" text severity="danger" size="small" @click.stop="confirmDeleteReview(review.id_review)" />
                  </div>
                </template>
              </Card>
            </div>
            
            <div v-if="!loadingReviews && filteredReviews.length > 0" class="results-count">
              Показано {{ filteredReviews.length }} из {{ userReviews.length }}
            </div>
          </TabPanel>

          <!-- Вкладка: Мои объекты -->
          <TabPanel header="Мои объекты">
            <!-- Фильтры и поиск -->
            <div class="filters-bar">
              <div class="filter-group">
                <i class="pi pi-search filter-icon"></i>
                <InputText 
                  v-model="objectsSearch" 
                  placeholder="Поиск по названию или адресу..." 
                  class="filter-input"
                  @input="applyObjectsFilters"
                />
              </div>
              
              <div class="filter-group">
                <Dropdown 
                  v-model="objectsTypeFilter" 
                  :options="uniqueObjectTypes" 
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Все типы" 
                  class="filter-dropdown"
                  @change="applyObjectsFilters"
                />
              </div>
              
              <div class="filter-group">
                <Dropdown 
                  v-model="objectsSort" 
                  :options="sortOptions" 
                  optionLabel="label"
                  optionValue="value"
                  class="filter-dropdown"
                  @change="applyObjectsFilters"
                />
              </div>
              
              <Button 
                v-if="hasObjectsFilters"
                icon="pi pi-times" 
                label="Сбросить" 
                @click="resetObjectsFilters"
                class="filter-reset"
                severity="secondary"
                text
                size="small"
              />
            </div>
            
            <div v-if="loadingObjects" class="tab-loading">
              <i class="pi pi-spin pi-spinner"></i> Загрузка объектов...
            </div>
            
            <div v-else-if="filteredObjects.length === 0" class="tab-empty">
              <i class="pi pi-map-marker"></i>
              <p>{{ objectsSearch || objectsTypeFilter ? 'Ничего не найдено' : 'Вы ещё не добавляли объекты' }}</p>
              <Button label="Добавить объект" @click="$router.push('/map')" severity="success" size="small" />
            </div>
            
            <div v-else class="cards-grid">
              <Card v-for="obj in filteredObjects" :key="obj.id_object" class="data-card review-card">
                <template #content>
                  <div class="card-header">
                    <div class="object-info">
                      <div class="object-preview">
                        <div class="object-icon-large">
                          <i :class="getTypeIcon(obj.type_name)"></i>
                        </div>

                        <div class="object-meta-info">
                          <span class="object-type-badge">{{ obj.type_name || 'Объект' }}</span>
                          <h4 class="object-name">{{ obj.name }}</h4>
                          <p v-if="obj.address" class="object-address">
                            <i class="pi pi-map-marker"></i> {{ obj.address }}
                          </p>
                        </div>

                      </div>
                    </div>
                  </div>
                  
                  <div class="card-meta">
                    <span class="rating-badge">
                      <i class="pi pi-star-fill"></i> {{ (obj.rating_avg ?? 0).toFixed(1) }}/5
                    </span>
                    <span class="date">
                      <i class="pi pi-calendar"></i> {{ formatDate(obj.created_at) }}
                    </span>
                  </div>
                  
                  <div class="card-actions">
                    <Button icon="pi pi-map" label="На карте" text size="small" @click="showObjectOnMap(obj)" />
                    <Button icon="pi pi-info-circle" label="Подробнее" text size="small" @click="openObjectDetails(obj)" />
                  </div>
                </template>
              </Card>
            </div>
            
            <div v-if="!loadingObjects && filteredObjects.length > 0" class="results-count">
              Показано {{ filteredObjects.length }} из {{ userObjects.length }}
            </div>
          </TabPanel>
          
        </TabView>
      </div>

    </div>

    <!-- ✅ ИСПРАВЛЕННАЯ МОДАЛКА: v-show + v-model:visible -->
    <ObjectDetailsModal
      v-show="true"
      :object="modalObject"
      v-model:visible="modalVisible"
      :review-to-edit="reviewToEdit"
      @review-submitted="onReviewSubmitted"
      @review-updated="onReviewUpdated"
      @go-to-map="showOnMapFromModal"
    />

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
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Dropdown from 'primevue/dropdown'
import ObjectDetailsModal from '@/components/modals/ObjectDetailsModal.vue'

export default {
  name: 'ProfileView',
  components: { 
    Card, InputText, InputMask, Password, Button, Tag, Divider, TabView, TabPanel, Dropdown, ObjectDetailsModal
  },
  
  data() {
    return {
      // Данные профиля пользователя
      profile: {
        id_user: null,
        email: '',
        nickname: '',
        phone: '',
        role_name: '',
        created_at: null
      },
      
      // Статистика активности
      activity: {
        total_reviews: 0,
        total_favorites: 0,
        total_objects_added: 0
      },
      
      // Форма для редактирования профиля
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
      loadingActivity: true,
      
      // Данные для вкладок
      userReviews: [],
      userObjects: [],
      loadingReviews: false,
      loadingObjects: false,
      
      // Активная вкладка
      activeTabIndex: 0,
      
      // ✅ НОВОЕ: Управление видимостью модалки через v-model
      modalVisible: false,
      
      // Модальный объект
      modalObject: null,
      
      // Отзыв для редактирования
      reviewToEdit: null,
      
      // Настройка позиции скролла
      mapScrollPosition: 165,
      
      // Фильтры и сортировка для отзывов
      reviewsSearch: '',
      reviewsTypeFilter: null,
      reviewsSort: 'newest',
      
      // Фильтры и сортировка для объектов
      objectsSearch: '',
      objectsTypeFilter: null,
      objectsSort: 'newest',
      
      // Опции сортировки
      sortOptions: [
        { label: 'Сначала новые', value: 'newest' },
        { label: 'Сначала старые', value: 'oldest' },
        { label: 'По рейтингу', value: 'rating' },
        { label: 'По названию', value: 'name' }
      ]
    }
  },
  
  computed: {
    uniqueReviewTypes() {
      const types = [...new Set(this.userReviews.map(r => r.type_name || r.object_type).filter(t => t))]
      return [
        { label: 'Все типы', value: null },
        ...types.map(t => ({ label: t, value: t }))
      ]
    },
    
    uniqueObjectTypes() {
      const types = [...new Set(this.userObjects.map(o => o.type_name).filter(t => t))]
      return [
        { label: 'Все типы', value: null },
        ...types.map(t => ({ label: t, value: t }))
      ]
    },
    
    hasReviewsFilters() {
      return this.reviewsSearch || this.reviewsTypeFilter || this.reviewsSort !== 'newest'
    },
    
    hasObjectsFilters() {
      return this.objectsSearch || this.objectsTypeFilter || this.objectsSort !== 'newest'
    },
    
    filteredReviews() {
      let result = [...this.userReviews]
      
      if (this.reviewsSearch) {
        const query = this.reviewsSearch.toLowerCase()
        result = result.filter(r => 
          (r.object_name && r.object_name.toLowerCase().includes(query)) ||
          (r.object_address && r.object_address.toLowerCase().includes(query)) ||
          (r.text && r.text.toLowerCase().includes(query))
        )
      }
      
      if (this.reviewsTypeFilter) {
        result = result.filter(r => (r.type_name || r.object_type) === this.reviewsTypeFilter)
      }
      
      switch (this.reviewsSort) {
        case 'newest':
          result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          break
        case 'oldest':
          result.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
          break
        case 'rating':
          result.sort((a, b) => (b.rating_avg || b.rating || 0) - (a.rating_avg || a.rating || 0))
          break
        case 'name':
          result.sort((a, b) => (a.object_name || '').localeCompare(b.object_name || ''))
          break
      }
      
      return result
    },
    
    filteredObjects() {
      let result = [...this.userObjects]
      
      if (this.objectsSearch) {
        const query = this.objectsSearch.toLowerCase()
        result = result.filter(o => 
          (o.name && o.name.toLowerCase().includes(query)) ||
          (o.address && o.address.toLowerCase().includes(query))
        )
      }
      
      if (this.objectsTypeFilter) {
        result = result.filter(o => o.type_name === this.objectsTypeFilter)
      }
      
      switch (this.objectsSort) {
        case 'newest':
          result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          break
        case 'oldest':
          result.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
          break
        case 'rating':
          result.sort((a, b) => (b.rating_avg || 0) - (a.rating_avg || 0))
          break
        case 'name':
          result.sort((a, b) => (a.name || '').localeCompare(b.name || ''))
          break
      }
      
      return result
    }
  },
  
  async mounted() {
    const token = localStorage.getItem('auth_token')
    if (!token) {
      this.$router.push('/auth')
      return
    }
    
    await Promise.all([
      this.fetchProfile(),
      this.fetchActivity(),
      this.fetchUserReviews(),
      this.fetchUserObjects()
    ])
  },
  
  methods: {
    onTabChange(index) {
      if (index === 0) {
        this.resetReviewsFilters()
      } else if (index === 1) {
        this.resetObjectsFilters()
      }
    },
    
    applyReviewsFilters() {},
    applyObjectsFilters() {},
    
    resetReviewsFilters() {
      this.reviewsSearch = ''
      this.reviewsTypeFilter = null
      this.reviewsSort = 'newest'
    },
    
    resetObjectsFilters() {
      this.objectsSearch = ''
      this.objectsTypeFilter = null
      this.objectsSort = 'newest'
    },
    
    async fetchProfile() {
      try {
        this.loading = true
        const response = await axios.get('http://localhost:8000/api/users/me', {
          headers: { 'Authorization': 'Bearer ' + localStorage.getItem('auth_token') }
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
          life: 3000,
          styleClass: 'my-error-toast'
        })
      } finally {
        this.loading = false
      }
    },
    
    async fetchActivity() {
      try {
        this.loadingActivity = true
        const response = await axios.get('http://localhost:8000/api/users/me/activity', {
          headers: { 'Authorization': 'Bearer ' + localStorage.getItem('auth_token') }
        })
        this.activity = response.data
      } catch (error) {
        console.error('Ошибка загрузки активности:', error)
        this.activity = {
          total_reviews: 0,
          total_favorites: 0,
          total_objects_added: 0
        }
      } finally {
        this.loadingActivity = false
      }
    },
    
    async fetchUserReviews() {
      try {
        this.loadingReviews = true
        const response = await axios.get('http://localhost:8000/api/users/me/reviews', {
          headers: { 'Authorization': 'Bearer ' + localStorage.getItem('auth_token') }
        })
        
        const reviews = response.data.map(review => ({
          ...review,
          id_object: review.object?.id_object,
          object_name: review.object?.name,
          object_type: review.object?.type,
          type_name: review.object?.type,
          object_address: null,  
          coords: review.object?.coords,
          latitude: review.object?.coords?.[0],
          longitude: review.object?.coords?.[1],
          rating_avg: review.object?.rating_avg,
          rating_count: review.object?.rating_count
        }))
        
        const reviewsWithAddresses = await Promise.all(
          reviews.map(async (review) => {
            if (review.id_object && !review.object?.address) {
              try {
                const response = await axios.get('http://localhost:8000/api/objects/' + review.id_object)
                const fullObject = response.data
                return {
                  ...review,
                  object_address: fullObject.address || 'Адрес не указан',
                  coords: fullObject.coords || review.coords,
                  latitude: fullObject.coords?.[0] || review.latitude,
                  longitude: fullObject.coords?.[1] || review.longitude,
                  rating_avg: fullObject.rating_avg || review.rating_avg,
                  rating_count: fullObject.rating_count || review.rating_count
                }
              } catch (error) {
                console.error('Не удалось загрузить объект ' + review.id_object + ':', error)
                return { ...review, object_address: 'Адрес не указан' }
              }
            }
            return {
              ...review,
              object_address: review.object?.address || review.address || 'Адрес не указан'
            }
          })
        )
        
        this.userReviews = reviewsWithAddresses
      } catch (error) {
        console.error('Ошибка загрузки отзывов:', error)
        this.$toast?.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить отзывы', life: 3000, styleClass: 'my-error-toast' })
      } finally {
        this.loadingReviews = false
      }
    },
    
    async fetchUserObjects() {
      try {
        this.loadingObjects = true
        const response = await axios.get('http://localhost:8000/api/users/me/objects', {
          headers: { 'Authorization': 'Bearer ' + localStorage.getItem('auth_token') }
        })
        this.userObjects = response.data.map(obj => ({
          ...obj,
          type_name: obj.type_name || obj.type || 'Объект',
          rating_avg: obj.rating_avg ?? obj.rating ?? null,
          rating_count: obj.rating_count ?? 0
        }))
      } catch (error) {
        console.error('Ошибка загрузки объектов:', error)
        this.$toast?.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить объекты', life: 3000, styleClass: 'my-error-toast' })
      } finally {
        this.loadingObjects = false
      }
    },
    
    startEditing() {
      this.isEditing = true
      this.errors = {}
      this.form.current_password = ''
      this.form.new_password = ''
    },
    
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
    
    validateForm() {
      this.errors = {}
      
      if (!this.form.nickname?.trim()) {
        this.errors.nickname = 'Введите никнейм'
      } else if (this.form.nickname.length < 3) {
        this.errors.nickname = 'Минимум 3 символа'
      } else if (!/^[a-zA-Zа-яА-ЯёЁ0-9]+$/.test(this.form.nickname.trim())) {
        this.errors.nickname = 'Только буквы и цифры, без пробелов и спецсимволов'
      }
      
      if (!this.form.email?.trim()) {
        this.errors.email = 'Введите email'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.form.email)) {
        this.errors.email = 'Некорректный email'
      }
      
      if (this.form.new_password && !this.form.current_password) {
        this.errors.current_password = 'Введите текущий пароль для подтверждения'
      }
      
      return Object.keys(this.errors).length === 0
    },
    
    async saveProfile() {
      if (!this.validateForm()) {
        this.$toast?.add({
          severity: 'warn',
          summary: 'Проверьте форму',
          detail: 'Исправьте ошибки в полях',
          life: 3000,
          styleClass: 'my-big-toast'
        })
        return
      }
      
      this.saving = true
      
      try {
        const payload = {}
        
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
        
        if (Object.keys(payload).length === 0) {
          this.$toast?.add({
            severity: 'info',
            summary: 'Информация',
            detail: 'Нет изменений для сохранения',
            life: 2000,
            styleClass: 'my-info-toast'
          })
          this.cancelEditing()
          return
        }
        
        const response = await axios.put(
          'http://localhost:8000/api/users/me',
          new URLSearchParams(payload),
          {
            headers: { 
              'Authorization': 'Bearer ' + localStorage.getItem('auth_token'),
              'Content-Type': 'application/x-www-form-urlencoded'
            }
          }
        )
        
        this.profile = response.data
        localStorage.setItem('user', JSON.stringify({
          id: response.data.id_user,
          nickname: response.data.nickname,
          role: response.data.role_name
        }))
        
        window.dispatchEvent(new CustomEvent('user-updated', {
          detail: { user: response.data }
        }))
        
        this.isEditing = false
        this.$toast?.add({
          severity: 'success',
          summary: 'Успешно',
          detail: 'Данные профиля обновлены',
          life: 3000,
          styleClass: 'my-success-toast'
        })
        
      } catch (error) {
        console.error('Ошибка сохранения:', error)
        const message = error.response?.data?.detail || 'Не удалось сохранить изменения'
        this.$toast?.add({
          severity: 'error',
          summary: 'Ошибка',
          detail: message,
          life: 4000,
          styleClass: 'my-error-toast'
        })
      } finally {
        this.saving = false
      }
    },
    
    switchToTab(index) {
      this.activeTabIndex = index
      this.$nextTick(() => {
        const dashboard = document.querySelector('.dashboard-section')
        if (dashboard) {
          const rect = dashboard.getBoundingClientRect()
          const offsetTop = rect.top + window.pageYOffset - 150
          window.scrollTo({ top: offsetTop, behavior: 'smooth' })
        }
      })
    },
    
    goToFavorites() {
      this.$router.push('/favorites')
    },
    
    // ✅ ИСПРАВЛЕНО: Открытие модалки с редактированием
    async openObjectFromReview(review) {
      const objectId = review.id_object || review.object?.id_object || review.object_id
      
      if (objectId) {
        try {
          const response = await axios.get('http://localhost:8000/api/objects/' + objectId)
          this.modalObject = response.data
          return true
        } catch (error) {
          console.error('Ошибка загрузки объекта по ID ' + objectId + ':', error)
        }
      }
      
      const objectName = review.object_name || review.object?.name
      if (objectName) {
        try {
          const response = await axios.get('http://localhost:8000/api/objects', {
            params: { search: objectName, limit: 1, type: review.object_type || review.object?.type }
          })
          if (response.data && response.data.length > 0) {
            this.modalObject = response.data[0]
            return true
          }
        } catch (error) {
          console.error('Ошибка поиска объекта по названию:', error)
        }
      }
      
      this.$toast?.add({ 
        severity: 'error', 
        summary: 'Ошибка', 
        detail: 'Не удалось найти объект. Возможно, он был удалён.', 
        life: 4000, 
        styleClass: 'my-error-toast' 
      })
      return false
    },
    
    async openObjectDetails(obj) {
      try {
        const response = await axios.get('http://localhost:8000/api/objects/' + obj.id_object)
        this.modalObject = response.data
        this.modalVisible = true
      } catch (error) {
        console.error('Ошибка загрузки объекта:', error)
        this.$toast?.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить объект', life: 3000, styleClass: 'my-error-toast' })
      }
    },
    
    async showOnMap(review) {
      const objectId = review.id_object || review.object?.id_object || review.object_id
      
      if (!objectId) {
        this.$toast?.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось найти ID объекта', life: 3000, styleClass: 'my-error-toast' })
        return
      }
      
      let coords = review.coords || review.object?.coords
      if (!coords && review.latitude && review.longitude) {
        coords = [review.latitude, review.longitude]
      }
      
      if (!coords) {
        try {
          const response = await axios.get('http://localhost:8000/api/objects/' + objectId, {
            headers: { 'Authorization': 'Bearer ' + localStorage.getItem('auth_token') }
          })
          const fullObject = response.data
          coords = fullObject.coords || [fullObject.latitude, fullObject.longitude]
          review.object_name = fullObject.name
          review.object_type = fullObject.type_name
          review.object_address = fullObject.address
          review.rating_avg = fullObject.rating_avg
          review.rating_count = fullObject.rating_count
        } catch (error) {
          console.error('Ошибка загрузки объекта:', error)
          this.$toast?.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось загрузить данные объекта', life: 3000, styleClass: 'my-error-toast' })
          return
        }
      }
      
      await this.$router.push({
        path: '/map',
        query: { 
          focus: coords ? coords[0] + ',' + coords[1] : null,
          zoom: 17,
          id: objectId,
          type: review.object_type || review.type_name,
          name: review.object_name,
          address: review.object_address || '',
          rating_avg: review.rating_avg,
          rating_count: review.rating_count
        }
      })
      
      this.$nextTick(() => {
        setTimeout(() => {
          if (this.mapScrollPosition >= 0) {
            window.scrollTo({ top: this.mapScrollPosition, behavior: 'auto' })
          }
        }, 100)
      })
    },
    
    async showOnMapFromModal(obj) {
      await this.$router.push({
        path: '/map',
        query: { 
          focus: obj.latitude + ',' + obj.longitude,
          zoom: 17,
          id: obj.id_object,
          type: obj.type_name,
          name: obj.name,
          address: obj.address,
          rating_avg: obj.rating_avg,
          rating_count: obj.rating_count
        }
      })
      
      this.$nextTick(() => {
        setTimeout(() => {
          if (this.mapScrollPosition >= 0) {
            window.scrollTo({ top: this.mapScrollPosition, behavior: 'auto' })
          }
        }, 100)
      })
    },
    
    async showObjectOnMap(obj) {
      await this.$router.push({
        path: '/map',
        query: { 
          focus: obj.latitude + ',' + obj.longitude,
          zoom: 17,
          id: obj.id_object,
          type: obj.type_name,
          name: obj.name,
          address: obj.address,
          rating_avg: obj.rating_avg,
          rating_count: obj.rating_count
        }
      })
      
      this.$nextTick(() => {
        setTimeout(() => {
          if (this.mapScrollPosition >= 0) {
            window.scrollTo({ top: this.mapScrollPosition, behavior: 'auto' })
          }
        }, 100)
      })
    },
    
    // ✅ ИСПРАВЛЕНО: Редактирование отзыва с правильным порядком
    async editReview(review) {
      console.log('✏️ editReview вызван:', review.id_review)
      
      // 1. Сначала сохраняем отзыв для редактирования
      this.reviewToEdit = { ...review }
      
      // 2. Загружаем полный объект
      const loaded = await this.openObjectFromReview(review)
      
      if (!loaded || !this.modalObject) {
        console.error('❌ Не удалось загрузить объект для редактирования')
        this.reviewToEdit = null
        return
      }
      
      console.log('✅ modalObject загружен:', this.modalObject.id_object)
      console.log('✅ reviewToEdit установлен:', this.reviewToEdit.id_review)
      
      // 3. ✅ ВАЖНО: Сначала показываем модалку, потом в nextTick
      this.modalVisible = true
      
      // 4. Ждём рендер модалки
      this.$nextTick(() => {
        console.log('🎯 $nextTick: модалка должна быть в DOM и видима')
      })
    },
    
    async confirmDeleteReview(reviewId) {
      if (!confirm('Вы уверены, что хотите удалить этот отзыв?')) return
      
      try {
        const response = await axios.delete('http://localhost:8000/api/reviews/' + reviewId, {
          headers: { 'Authorization': 'Bearer ' + localStorage.getItem('auth_token') }
        })
        
        if (response.data?.success) {
          this.userReviews = this.userReviews.filter(r => r.id_review !== reviewId)
          this.$toast?.add({ severity: 'success', summary: 'Удалено', detail: 'Отзыв успешно удалён', life: 2000, styleClass: 'my-success-toast' })
        }
      } catch (error) {
        console.error('Ошибка удаления:', error)
        const message = error.response?.data?.detail || 'Не удалось удалить отзыв'
        this.$toast?.add({ severity: 'error', summary: 'Ошибка', detail: message, life: 3000, styleClass: 'my-error-toast' })
      }
    },
    
    editObject(obj) {
      this.$toast?.add({ severity: 'info', summary: 'Редактирование', detail: 'Функция редактирования объекта в разработке', life: 3000, styleClass: 'my-info-toast' })
    },
    
    onReviewSubmitted(result) {
      if (result.success) {
        this.fetchUserReviews()
        this.reviewToEdit = null
      }
    },
    
    // ✅ ИСПРАВЛЕНО: Обработка обновления отзыва
    onReviewUpdated(result) {
      console.log('🔄 onReviewUpdated:', result)
      
      if (result.success) {
        // Обновляем отзыв в локальном массиве
        const idx = this.userReviews.findIndex(r => r.id_review === result.id_review)
        if (idx !== -1) {
          this.userReviews[idx] = { 
            ...this.userReviews[idx], 
            ...result,
            // Сохраняем поля объекта, если они пришли отдельно
            object_name: result.object_name || this.userReviews[idx].object_name,
            object_address: result.object_address || this.userReviews[idx].object_address,
            type_name: result.type_name || this.userReviews[idx].type_name
          }
        }
        
        this.$toast?.add({ 
          severity: 'success', 
          summary: 'Обновлено', 
          detail: 'Отзыв успешно изменён', 
          life: 2000,
          styleClass: 'my-success-toast'
        })
      }
      
      // ✅ Сбрасываем состояние редактирования
      this.reviewToEdit = null
      this.modalVisible = false
      this.modalObject = null
    },
    
    // ✅ Обработчик закрытия модалки
    onModalClose(val) {
      if (!val) {
        this.modalObject = null
        this.reviewToEdit = null
        this.modalVisible = false
      }
    },
    
    getTypeIcon(typeName) {
      const map = {
        'камера видеонаблюдения': 'pi pi-video', 
        'кафе': 'pi pi-map-marker', 
        'фонарь': 'pi pi-lightbulb',
        'скамейка': 'pi pi-map-marker', 
        'парк': 'pi pi-map-marker', 
        'беседка': 'pi pi-building-columns',
        'остановка': 'pi pi-car', 
        'детская площадка': 'pi pi-face-smile',
        'спортивная площадка': 'pi pi-bolt',
        'урна': 'pi pi-trash',
        'мусорный контейнер': 'pi pi-trash',
        'парковка': 'pi pi-car',
        'пешеходный переход': 'pi pi-directions-alt',
        'памятник': 'pi pi-flag',
        'информационный стенд': 'pi pi-info-circle',
        'цветник': 'pi pi-star',
        'дорожка': 'pi pi-arrow-right',
        'ограждение': 'pi pi-th-large'
      }
      
      if (!typeName) return 'pi pi-map-marker'
      
      const key = Object.keys(map).find(k => typeName.toLowerCase().includes(k))
      return map[key] || 'pi pi-map-marker'
    },
    
    getCategorySeverity(category) {
      const map = {
        'проблема': 'danger', 'предложение': 'info', 'похвала': 'success', 'вопрос': 'warn',
        'problem': 'danger', 'suggestion': 'info', 'praise': 'success'
      }
      return map[category?.toLowerCase()] || 'secondary'
    },
    
    getStatusLabel(status) {
      const map = { 'approved': 'Одобрен', 'pending': 'На модерации', 'rejected': 'Отклонён' }
      return map[status] || status
    },
    
    getStatusSeverity(status) {
      const map = { 'approved': 'success', 'pending': 'warn', 'rejected': 'danger' }
      return map[status] || 'secondary'
    },
    
    formatDate(dateString) {
      if (!dateString) return '—'
      return new Date(dateString).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })
    },
    
    handleLogout() {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.dispatchEvent(new CustomEvent('auth-change', { detail: { isAuthenticated: false } }))
      this.$toast?.add({ severity: 'info', summary: 'Выход', detail: 'Вы вышли из системы', life: 2000, styleClass: 'my-info-toast' })
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
/* Общие стили страницы */
.profile-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #003b08;
  background: transparent;
  padding-bottom: 100px;
}
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

/* Стили заголовка */
.profile-header {
  background: transparent;
  backdrop-filter: blur(20px);
  padding: 60px 0px 0px;
  margin-bottom: 20px;
}
.page-title {
  font-size: 33px;
  font-weight: 800;
  color: #014f00;
  margin: 0 0 8px;
  text-align: center;
}

/* Сетка профиля */
.profile-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 15px;
  align-items: start;
}

/* Стили карточек PrimeVue */
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
:deep(.p-card-content) { padding: 24px !important; }

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
  color: #014f00;
}
.card-title i { font-size: 20px; color: #168f04; }

/* Просмотр профиля */
.profile-view { display: flex; flex-direction: column; gap: 16px; }
.profile-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(22, 143, 4, 0.1);
}
.profile-field:last-child { border-bottom: none; }
.profile-field label { font-size: 14px; font-weight: 500; color: #64748b; }
.field-value { font-size: 15px; font-weight: 600; color: #1a1a1a; text-align: right; margin: 0; }
.btn-edit { margin-top: 8px; width: 100%; border-radius: 12px !important; }

/* Редактирование профиля */
.profile-edit { display: flex; flex-direction: column; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-group label { font-size: 14px; font-weight: 500; color: #334155; }

:deep(.p-inputtext), :deep(.p-inputmask), :deep(.p-password) {
  width: 100%;
  border-radius: 12px !important;
  border: 2px solid #e2e8f0 !important;
  transition: border-color 0.3s !important;
}
:deep(.p-inputtext:focus), :deep(.p-inputmask:focus), :deep(.p-password :focus) {
  border-color: #168f04 !important;
  box-shadow: 0 0 0 4px rgba(22, 143, 4, 0.1) !important;
}
.p-error { color: #dc2626 !important; font-size: 12px !important; }
.hint-text { color: #64748b; font-size: 11px; margin-top: 4px; }
.edit-actions { display: flex; gap: 12px; margin-top: 8px; }
.btn-save, .btn-cancel { flex: 1; border-radius: 12px !important; }

/* Статистика */
.loading-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #64748b;
  padding: 20px 0;
}
.loading-stats i { font-size: 20px; color: #168f04; }
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
  transition: all 0.2s ease;
  border-radius: 12px;
  padding: 10px 4px;
  cursor: pointer;
}
.stat-item:hover { background-color: rgba(22, 143, 4, 0.08); transform: translateY(-2px); }
.stat-item:active { transform: translateY(0); background-color: rgba(22, 143, 4, 0.15); }
.stat-value { font-size: 24px; font-weight: 800; color: #168f04; }
.stat-label { font-size: 12px; color: #64748b; font-weight: 500; }

/* Опасная зона */
.danger-card :deep(.p-card) { border-color: rgba(220, 38, 38, 0.2) !important; }
.btn-logout { width: 100%; border-radius: 12px !important; }

/* Divider */
:deep(.p-divider .p-divider-content) { background: #fff !important; padding: 0 12px !important; }
.divider-text { color: #64748b; font-size: 13px; font-weight: 500; }
:deep(.p-divider) { border-color: rgba(22, 143, 4, 0.1) !important; margin: 8px 0 !important; }

/* ===== ВКЛАДКИ: ОБНОВЛЁННЫЙ СТИЛЬ ===== */
.dashboard-section { 
  margin-top: 100px; 
  background: transparent; 
}

:deep(.p-tabview) { 
  width: 100%; 
}

/* Навигация вкладок */
:deep(.p-tabview-nav) {
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(20px) !important;
  border: 1px solid rgba(22, 143, 4, 0.2) !important;
  border-radius: 16px 16px 0 0 !important;
  padding: 8px !important;
  gap: 6px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
}

/* Ссылки вкладок */
:deep(.p-tabview-nav-link) {
  border: none !important;
  border-radius: 12px !important;
  color: #64748b !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  padding: 12px 28px !important;
  transition: all 0.3s ease !important;
  background: transparent !important;
  position: relative;
}

/* Эффект при наведении */
:deep(.p-tabview-nav-link:hover) {
  color: #168f04 !important;
  background: rgba(22, 143, 4, 0.08) !important;
  transform: translateY(-1px);
}

/* Активная вкладка */
:deep(.p-tabview-nav-link.p-highlight) {
  color: #fff !important;
  background: linear-gradient(135deg, #168f04, #0d6f03) !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 16px rgba(22, 143, 4, 0.3) !important;
}

/* Панель контента вкладок */
:deep(.p-tabview-panels) {
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(20px) !important;
  border: 1px solid rgba(22, 143, 4, 0.15) !important;
  border-top: none !important;
  border-radius: 0 0 16px 16px !important;
  padding: 24px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06) !important;
}

/* Анимация появления контента */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
:deep(.p-tabview-panels) {
  animation: fadeIn 0.3s ease;
}

/* ===== ПАНЕЛЬ ФИЛЬТРОВ ===== */
.filters-bar {
  display: flex;
  /* flex-wrap: wrap; */
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(22, 143, 4, 0.15);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 340px;
}

.filter-icon {
  color: #64748b;
  font-size: 14px;
}

.filter-input {
  flex: 1;
  min-width: 180px;
  border-radius: 10px !important;
  border: 1px solid rgba(22, 143, 4, 0.2) !important;
}

.filter-input:focus {
  border-color: #168f04 !important;
  box-shadow: 0 0 0 3px rgba(22, 143, 4, 0.1) !important;
}

.filter-dropdown {
  width: 200px;
  border-radius: 10px !important;
}

.filter-dropdown :deep(.p-dropdown) {
  width: 100%;
  border-radius: 10px !important;
  border: 1px solid rgba(22, 143, 4, 0.2) !important;
}

.filter-dropdown :deep(.p-dropdown:focus) {
  border-color: #168f04 !important;
  box-shadow: 0 0 0 3px rgba(22, 143, 4, 0.1) !important;
}

.filter-reset {
  margin-left: auto;
  color: #64748b !important;
}

.filter-reset:hover {
  color: #168f04 !important;
}

/* Счётчик результатов */
.results-count {
  text-align: center;
  padding: 12px;
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
}

/* Сетка карточек */
.cards-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 18px; }
.data-card {
  border-radius: 16px !important;
  border: 1px solid rgba(22, 143, 4, 0.15) !important;
  background: #fff !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.data-card:hover {
  box-shadow: 0 12px 40px rgba(22, 143, 4, 0.15) !important;
  border-color: rgba(22, 143, 4, 0.35) !important;
  transform: translateY(-3px);
}
.data-card :deep(.p-card-content) { padding: 20px !important; }

/* Карточка отзыва/объекта */
.review-card,
.object-card { 
  border-left: 4px solid #168f04 !important;
}
.object-link-wrapper {
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 12px;
  padding: 4px;
  margin: -4px;
}
.object-link-wrapper:hover { background: rgba(22, 143, 4, 0.06); }
.object-link-wrapper:active { background: rgba(22, 143, 4, 0.12); }
.review-card .card-header,
.object-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed rgba(22, 143, 4, 0.2);
}
.object-info { flex: 1; min-width: 0; }
.object-preview { display: flex; align-items: flex-start; gap: 14px; }
.object-icon-large {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(22, 143, 4, 0.2), rgba(22, 143, 4, 0.08));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #168f04;
  font-size: 26px;
}
.object-meta-info { flex: 1; min-width: 0; }
.object-type-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  color: #168f04;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  background: rgba(22, 143, 4, 0.12);
  padding: 4px 10px;
  border-radius: 20px;
  margin-bottom: 6px;
}
.object-name {
  font-weight: 700;
  color: #014f00;
  font-size: 16px;
  margin: 0 0 4px 0;
  line-height: 1.3;
}
.object-address {
  font-size: 12px;
  color: #64748b;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}
.object-address i { font-size: 11px; color: #168f04; }
.category-tag { flex-shrink: 0; }
.card-text {
  color: #475569;
  font-size: 14px;
  line-height: 1.6;
  margin: 0 0 14px 0;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.rating-badge {
  color: #f59e0b;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(245, 158, 11, 0.1);
  padding: 4px 10px;
  border-radius: 20px;
}
.rating-badge i { font-size: 11px; }
.date { display: flex; align-items: center; gap: 4px; }

/* Рейтинг объекта */
.object-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #f59e0b;
  font-weight: 700;
  font-size: 14px;
  background: rgba(245, 158, 11, 0.1);
  padding: 4px 10px;
  border-radius: 20px;
}
.object-rating i {
  font-size: 12px;
}
.object-rating small {
  color: #64748b;
  font-weight: 400;
  font-size: 11px;
}

.card-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding-top: 14px;
  border-top: 1px solid rgba(22, 143, 4, 0.12);
  flex-wrap: wrap;
}

/* Пустое состояние */
.tab-empty, .tab-loading {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
  background: rgba(22, 143, 4, 0.03);
  border-radius: 12px;
  border: 1px dashed rgba(22, 143, 4, 0.2);
}
.tab-empty i, .tab-loading i {
  font-size: 3rem;
  color: #168f04;
  margin-bottom: 16px;
  display: block;
  opacity: 0.8;
}
.tab-empty p { margin: 0 0 20px; font-size: 15px; }
</style>