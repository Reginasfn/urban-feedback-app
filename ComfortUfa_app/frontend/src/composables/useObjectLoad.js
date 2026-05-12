// useObjectLoad.js
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
  selectedCategoryRef,
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

    if (activePlacemarkRef.value && map.value.geoObjects) {
      map.value.geoObjects.remove(activePlacemarkRef.value)
      activePlacemarkRef.value = null
    }

    clusterer.value.removeAll()
    loading.value = true
    selectedCategoryRef.value = type
    objectsCount.value = 0

    try {
      const bbox = getMapBbox()

      let limit = 1500  // по умолчанию
      
      if (type === 'all') {
        limit = 2000  // больше для режима "ВСЕ"
      }
      
      if (activeFilterRef.value === 'bookmarked') {
        limit = 5000  // ещё больше для избранного
      }
      
      if (activeFilterRef.value === 'mine') {
        limit = 3000  // для "мои объекты"
      }
      

      const params = { limit }

      if (type && type !== 'all') {
        params.type = type
      }

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

      if (activeFilterRef.value === 'high_rating') params.min_rating = 4.5

      const response = await fetchWithTimeout(
        api.get('/api/objects', { params }),
        10000,
        'Сервер не отвечает'
      )

      const objects = response.data || []

      const placemarks = objects.map((obj, index) => {
        const objectType = obj.type_name || obj.type || type

        const config = markerConfig[objectType] || { preset: 'islands#grayCircleIcon' }

        const isMine = obj.created_by && isAuthenticatedRef.value && obj.created_by === 123
        const preset = isMine
          ? config.preset?.replace('CircleIcon', 'DotIcon') || 'islands#blueCircleDotIcon'
          : config.preset

        // 🔥 Нормализуем рейтинг сразу
        const initialRating = obj.rating_avg ?? obj.rating ?? null
        const initialRatingCount = obj.rating_count ?? obj.ratingCount ?? 0

        const numericId = Number(obj.id_object)

        const placemark = new window.ymaps.Placemark(
          obj.coords,
          {
            balloonContent: createBalloonContent(
              { ...obj, rating: initialRating, ratingCount: initialRatingCount },
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
            preset,
            isOurObject: true,
            zIndex: isMine ? 150 : 100,
            objectId: numericId,
            objectType: objectType
          }
        )

        // 🔥 Сохраняем данные с нормализованными полями рейтинга
        placemark.__objectData = { 
          ...obj, 
          id_object: numericId,
          rating: initialRating,
          ratingCount: initialRatingCount,
          rating_avg: initialRating,    // 🔥 Дублируем для совместимости
          rating_count: initialRatingCount
        }
        placemark.__objectIndex = index
        placemark.__ratingLoaded = initialRating !== null && initialRating !== undefined
        placemark.__ratingLoading = false

        placemark.events.add('balloonopen', async () => {
          const currentIsBookmarked = bookmarkedObjects.value.has(numericId)
          
          const currentRating = placemark.__objectData.rating ?? null
          const currentRatingCount = placemark.__objectData.ratingCount ?? 0

          const displayType = placemark.options?.get('objectType') || objectType

          const freshContent = createBalloonContent(
            { 
              ...placemark.__objectData, 
              rating: currentRating, 
              ratingCount: currentRatingCount 
            },
            placemark.__objectIndex,
            type,
            {
              isBookmarked: currentIsBookmarked,
              iconClass: getCategoryIcon(type)
            }
          )
          
          placemark.properties.set('balloonContent', freshContent)

          if (placemark.__ratingLoaded || placemark.__ratingLoading) {
            return
          }
          
          placemark.__ratingLoading = true

          try {
            const rating = await fetchRating(numericId)

            if (!placemark.balloon || !placemark.balloon.isOpen()) return

            placemark.__objectData = {
              ...placemark.__objectData,
              rating: rating.avg,
              ratingCount: rating.count,
              rating_avg: rating.avg,      // 🔥 Для совместимости
              rating_count: rating.count
            }
            placemark.__ratingLoaded = true

            const updatedContent = createBalloonContent(
              placemark.__objectData,
              placemark.__objectIndex,
              type,
              {
                isBookmarked: bookmarkedObjects.value.has(numericId),
                iconClass: getCategoryIcon(type)
              }
            )

            placemark.properties.set('balloonContent', updatedContent)
            
            const balloonData = placemark.balloon.getData()
            if (balloonData?.properties) {
              balloonData.properties.set('balloonContent', updatedContent)
            }

          } catch (err) {
            console.error(`[Rating] Error for ${numericId}:`, err)
            placemark.__ratingLoaded = true
            placemark.__objectData = {
              ...placemark.__objectData,
              rating: null,
              ratingCount: 0,
              rating_avg: null,
              rating_count: 0
            }
          } finally {
            placemark.__ratingLoading = false
          }
        })

        return placemark
      })

      clusterer.value.add(placemarks)
      objectsCount.value = placemarks.length
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Ошибка загрузки объектов')
    } finally {
      loading.value = false
    }
  }

  return { loadObjects, loading, objectsCount }
}