import { ref } from 'vue'

/**
 * Composable для управления фильтрами объектов на карте
 * @param {Object} deps - Зависимости
 * @param {import('vue').Ref<boolean>} deps.isAuthenticated - Реактивная ссылка на статус авторизации
 * @param {import('vue').Ref<string|null>} deps.geoSuccess - Сообщение об успешной геолокации (для подсказок)
 * @param {import('vue').Ref<string|null>} deps.selectedCategory - Выбранная категория объектов
 * @param {Function} deps.loadObjects - Функция загрузки объектов по категории
 * @param {Function} deps.setError - Функция показа ошибок
 * @param {Function} deps.setSuccess - Функция показа успешных сообщений
 * @param {import('vue').Ref<Object|null>} deps.map - Реактивная ссылка на экземпляр карты
 */
export function useFilter({
  isAuthenticated,
  geoSuccess,
  selectedCategory,
  loadObjectsRef,
  setError,
  setSuccess,
  map
}) {
  // ===== STATE =====
  const activeFilter = ref(null) // Только один активный фильтр
  const userCoords = ref(null)
  
  // ===== CONSTANTS =====
  const NEARBY_RADIUS = 5000 // Фиксированный радиус 5 км
  const AUTH_FILTERS = ['mine', 'bookmarked'] // Фильтры, требующие авторизации

  // ===== CONFIG =====
  const FILTER_TITLES = {
    nearby: () => geoSuccess.value 
      ? 'Объекты в радиусе 5 км от вас' 
      : 'Определите местоположение для этого фильтра',
    bookmarked: () => isAuthenticated.value 
      ? 'Только избранные объекты' 
      : 'Только для авторизованных',
    mine: () => isAuthenticated.value 
      ? 'Объекты, которые вы добавили' 
      : 'Только для авторизованных',
    problems: () => 'Объекты с жалобами и низким рейтингом',
    high_rating: () => 'Объекты с рейтингом 4.5+'
  }

  const FILTER_LABELS = {
    nearby: 'рядом',
    bookmarked: 'избранное',
    mine: 'мои',
    problems: 'проблемные',
    high_rating: '4.5+'
  }

  // ===== METHODS =====

  /**
   * Проверка доступности фильтра для текущего пользователя
   * @param {string} filterId - Идентификатор фильтра
   * @returns {boolean}
   */
  const isFilterAvailable = (filterId) => {
    if (AUTH_FILTERS.includes(filterId)) {
      return isAuthenticated.value
    }
    return true
  }

  /**
   * Получение подсказки (title) для фильтра
   * @param {string} filterId - Идентификатор фильтра
   * @returns {string}
   */
  const getFilterTitle = (filterId) => {
    const getter = FILTER_TITLES[filterId]
    return getter ? getter() : filterId
  }

  /**
   * Получение короткой метки фильтра для отображения в UI
   * @param {string} filterId - Идентификатор фильтра
   * @returns {string}
   */
  const getFilterLabel = (filterId) => {
    return FILTER_LABELS[filterId] || filterId
  }

  /**
   * Переключение фильтра (только один может быть активен)
   * @param {string} filterId - Идентификатор фильтра
   */
  const toggleFilter = (filterId) => {
    // Проверка доступности
    if (!isFilterAvailable(filterId)) {
      setError('Этот фильтр доступен только авторизованным пользователям', 2000)
      return
    }
    
    // Если нажали на уже активный фильтр — снимаем его
    if (activeFilter.value === filterId) {
      activeFilter.value = null
      applyFilters()
      return
    }
    
    // Устанавливаем новый активный фильтр
    activeFilter.value = filterId
    
    // Для фильтра "Рядом" — получаем координаты если нужно
    if (filterId === 'nearby' && !userCoords.value && map.value) {
      userCoords.value = map.value.getCenter()
    }
    
    applyFilters()
  }

  /**
   * Сброс всех фильтров
   */
  const clearFilters = () => {
    activeFilter.value = null
    userCoords.value = null
    applyFilters()
    setSuccess?.('Фильтры сброшены', 2000)
  }

  /**
   * Применение текущих фильтров — перезагрузка объектов
   */
    const applyFilters = () => {
    // 👈 Проверяем, что функция уже установлена
    if (selectedCategory?.value && loadObjectsRef?.value) {
        loadObjectsRef.value(selectedCategory.value)
    }
    }

  /**
   * Обновление координат пользователя (для фильтра "Рядом")
   * @param {[number, number]} coords - Координаты [широта, долгота]
   */
  const updateUserCoords = (coords) => {
    if (activeFilter.value === 'nearby') {
      userCoords.value = coords
      applyFilters()
    }
  }

  // ===== PUBLIC API =====
  return {
    // State
    activeFilter,
    userCoords,
    
    // Constants
    NEARBY_RADIUS,
    AUTH_FILTERS,
    
    // Methods
    isFilterAvailable,
    getFilterTitle,
    getFilterLabel,
    toggleFilter,
    clearFilters,
    applyFilters,
    updateUserCoords
  }
}