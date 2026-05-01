// composables/useAutoClear.js
import { ref, onBeforeUnmount } from 'vue'  // ✅ Добавьте onBeforeUnmount!

export function useAutoClear(initialValue = null, defaultTimeout = 2500) {
  const value = ref(initialValue)
  let timer = null

  const set = (newValue, timeout = null) => {
    // Очищаем предыдущий таймер если есть
    if (timer) clearTimeout(timer)
    
    value.value = newValue
    
    // Устанавливаем новый таймер только если есть значение
    if (newValue) {
      timer = setTimeout(() => {
        value.value = null
      }, timeout ?? defaultTimeout)
    }
  }

  const clear = () => {
    if (timer) clearTimeout(timer)
    value.value = null
  }

  // Автоматическая очистка при размонтировании компонента
  onBeforeUnmount(() => {
    if (timer) {
      clearTimeout(timer)
      timer = null
    }
  })

  return {
    value,
    set,
    clear
  }
}