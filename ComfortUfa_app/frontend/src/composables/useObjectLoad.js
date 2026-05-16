// frontend\src\composables\useObjectLoad.js
import { ref } from 'vue'

export function useObjectLoad({
  api,
  map,
  clusterer,
  fetchWithTimeout,
  getMapBbox,
  createBalloonContent,
  markerConfig,
  bookmarkedObjects,
  getCategoryIcon,
  setError,
  fetchRating,
  activePlacemarkRef,
  activeFilterRef,
  userCoordsRef,
  // ❌ УБРАНО: selectedCategoryRef - не используется
  isAuthenticatedRef,
  NEARBY_RADIUS = 1000
}) {
  const loading = ref(false)
  const objectsCount = ref(0)

  const loadObjects = async (type) => {
    if (!map.value || !clusterer.value) {
      setError('Карта ещё не загрузилась')
      return
    }

    if (activePlacemarkRef && map.value.geoObjects) {
      map.value.geoObjects.remove(activePlacemarkRef)
      activePlacemarkRef = null
    }

    clusterer.value.removeAll()
    loading.value = true
    objectsCount.value = 0

    try {
      const bbox = getMapBbox()

      let limit = 1500
      if (type === 'all') limit = 2000
      if (activeFilterRef.value === 'bookmarked') limit = 5000
      if (activeFilterRef.value === 'mine') limit = 3000

      const params = { limit }

      if (type && type !== 'all') params.type = type
      if (bbox) params.bbox = bbox

      if (activeFilterRef.value === 'nearby' && userCoordsRef.value) {
        params.near_lat = userCoordsRef.value[0]
        params.near_lon = userCoordsRef.value[1]
        params.near_radius = NEARBY_RADIUS
      }

      if (activeFilterRef.value === 'bookmarked') {
        params.bookmarked_ids = Array.from(bookmarkedObjects.value).join(',')
      }

      if (activeFilterRef.value === 'mine') params.mine = true

      if (activeFilterRef.value === 'problems') {
        params.min_problems = 1
        params.max_rating = 3.0
      }

      if (activeFilterRef.value === 'high_rating') {
        params.min_rating = 4.5
      }

      const response = await fetchWithTimeout(
        api.get('/api/objects', { params }),
        10000,
        'Сервер не отвечает'
      )

      const objects = response.data || []

      const placemarks = objects.map((obj, index) => {
        const objectType = obj.type_name || obj.type || type
        const config = markerConfig[objectType] || {
          preset: 'islands#grayCircleIcon'
        }

        const numericId = Number(obj.id_object)

        const initialRating = obj.rating_avg ?? obj.rating ?? null
        const initialRatingCount = obj.rating_count ?? 0

        const placemark = new window.ymaps.Placemark(
          obj.coords,
          {
            balloonContent: createBalloonContent(
              {
                ...obj,
                id_object: numericId,
                rating: initialRating,
                ratingCount: initialRatingCount
              },
              index,
              objectType,
              {
                isBookmarked: bookmarkedObjects.value.has(numericId),
                iconClass: getCategoryIcon(objectType)
              }
            ),
            hintContent: obj.name || objectType
          },
          {
            preset: config.preset,
            objectId: numericId,
            objectType
          }
        )

        placemark.__objectData = {
          ...obj,
          id_object: numericId,
          rating: initialRating,
          ratingCount: initialRatingCount
        }

        placemark.__objectIndex = index
        placemark.__ratingLoaded = false

        placemark.events.add('balloonopen', async () => {
          const id = numericId

          const freshRating = await fetchRating(id)

          placemark.__objectData = {
            ...placemark.__objectData,
            rating: freshRating.avg,
            ratingCount: freshRating.count
          }

          const updated = createBalloonContent(
            placemark.__objectData,
            placemark.__objectIndex,
            objectType,
            {
              isBookmarked: bookmarkedObjects.value.has(id),
              iconClass: getCategoryIcon(objectType)
            }
          )

          placemark.properties.set('balloonContent', updated)
        })

        return placemark
      })

      clusterer.value.add(placemarks)
      objectsCount.value = placemarks.length
    } catch (err) {
      setError(err.message || 'Ошибка загрузки объектов')
    } finally {
      loading.value = false
    }
  }

  return { loadObjects, loading, objectsCount }
}