// src/composables/useSearch.js

import { ref } from 'vue'

export function useSearch({ api, navigateToObject, setError }) {
  const searchQuery = ref('')
  const searchResults = ref([])
  let searchTimeout = null

  const searchCategories = async (event) => {
    if (searchTimeout) clearTimeout(searchTimeout)

    const query = event.query.trim()
    if (query.length < 2) {
      searchResults.value = []
      return
    }

    searchTimeout = setTimeout(async () => {
      try {
        const response = await api.get('/api/objects', {
          params: { search: query, limit: 15 }
        })

        searchResults.value = response.data.map(obj => ({
          label: `${obj.name} — ${obj.address || 'Адрес не указан'}`,
          ...obj,
          type: obj.type_name
        }))
      } catch (err) {
        console.error('[Search] Ошибка:', err)
        searchResults.value = []
        setError?.('Ошибка поиска')
      }
    }, 300)
  }

  const handleSearchKeydown = (event) => {
    if (event.key === 'Enter' && searchResults.value.length > 0) {
      const firstResult = searchResults.value[0]

      if (firstResult?.id_object) {
        event.preventDefault()
        navigateToObject(firstResult)

        searchQuery.value = ''
        searchResults.value = []
      }
    }
  }

  const onCategorySelect = async (event) => {
    const selected = event.value

    if (selected?.id_object) {
      await navigateToObject(selected)

      searchQuery.value = ''
      searchResults.value = []
    }
  }

  return {
    searchQuery,
    searchResults,
    searchCategories,
    handleSearchKeydown,
    onCategorySelect
  }
}