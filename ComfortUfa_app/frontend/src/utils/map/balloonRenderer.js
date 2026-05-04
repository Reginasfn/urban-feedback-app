/**
 * Генерирует HTML-контент для балуна Яндекс.Карт
 * Чистая функция: принимает данные → возвращает строку
 */
export const createBalloonContent = (obj, index, type, options = {}) => {
  const { isBookmarked = false, iconClass = 'pi pi-map-marker' } = options

  const displayName = obj.name || `Объект #${obj.id_object || (index + 1)}`
  const displayAddress = obj.address || 'Адрес не указан'
  const displayType = obj.type_name || type || 'Не указан'
  
  // ===== РАБОТА С РЕЙТИНГОМ =====
  const rating = obj.rating
  const ratingCount = obj.ratingCount || 0
  
  let ratingStars = ''
  let ratingDisplay = ''
  
  if (rating !== null && rating !== undefined && !isNaN(rating)) {
    const roundedRating = Math.round(rating * 2) / 2
    const fullStars = Math.floor(roundedRating)
    const hasHalfStar = roundedRating % 1 >= 0.5
    
    ratingStars = '★'.repeat(fullStars)
    if (hasHalfStar) ratingStars += '½'
    ratingStars += '☆'.repeat(5 - fullStars - (hasHalfStar ? 1 : 0))
    
    ratingDisplay = `<span class="rating-value">${rating.toFixed(1)}</span>/5`
    if (ratingCount > 0) {
      ratingDisplay += ` <span class="rating-count">(${ratingCount} ${getRatingWord(ratingCount)})</span>`
    }
  } else {
    ratingStars = '☆☆☆☆☆'
    ratingDisplay = '<span class="no-rating">Нет оценок</span>'
  }
  
  // 🔒 Экранирование
  const safeId = String(obj.id_object).replace(/'/g, "\\'")
  const safeName = displayName.replace(/'/g, "\\'")
  const safeType = displayType.replace(/'/g, "\\'")

  return `
    <div class="object-card">
      <button class="bookmark-btn ${isBookmarked ? 'active' : ''}" 
              onclick="window.__toggleBookmark?.('${safeId}', this)"
              title="${isBookmarked ? 'Убрать из избранного' : 'Добавить в избранное'}">
        <i class="pi ${isBookmarked ? 'pi-bookmark-fill' : 'pi-bookmark'}"></i>
      </button>
      
      <div class="object-card-header">
        <i class="pi ${iconClass}"></i>
        <h4>${displayName}</h4>
      </div>
      
      <p class="object-address">
        <i class="pi pi-map-marker"></i> ${displayAddress}
      </p>
      
      <div class="object-rating">
        <span class="stars">${ratingStars}</span>
        <span class="rating-text">${ratingDisplay}</span>
      </div>
      
      <div class="object-card-footer">
        <span class="object-type">${displayType}</span>
        <button class="review-btn" onclick="window.__openReview?.('${safeId}', '${safeName}', '${safeType}')">
          <i class="pi pi-pencil"></i> Добавить отзыв
        </button>
      </div>
    </div>
    <style>
      .object-card { 
        font-family: Inter, system-ui, sans-serif; 
        min-width: 280px; 
        max-width: 350px;
        background: linear-gradient(135deg, #fff 0%, #f8fafc 100%); 
        border-radius: 16px; 
        padding: 16px 20px; 
        box-shadow: 0 8px 30px rgba(0,0,0,0.12); 
        border: 1px solid rgba(22,143,4,0.15); 
        position: relative; 
      }
      .bookmark-btn { 
        position: absolute; top: 12px; right: 12px; 
        width: 32px; height: 32px; border: none; 
        background: rgba(22,143,4,0.1); color: #168f04; 
        border-radius: 8px; cursor: pointer; 
        display: flex; align-items: center; justify-content: center; 
        transition: all 0.3s; z-index: 10; 
      }
      .bookmark-btn:hover { background: rgba(22,143,4,0.2); transform: scale(1.1); }
      .bookmark-btn.active { background: #168f04; color: white; }
      .object-card-header { 
        display: flex; align-items: center; gap: 10px; 
        margin-bottom: 12px; padding-bottom: 12px; 
        border-bottom: 1px solid rgba(22,143,4,0.1); 
      }
      .object-card-header i { 
        font-size: 20px; color: #168f04; 
        background: rgba(22,143,4,0.1); padding: 8px; border-radius: 10px; 
      }
      .object-card-header h4 { margin: 0; font-size: 16px; font-weight: 700; color: #1a1a1a; }
      .object-address { 
        margin: 0 0 12px 0; font-size: 13px; color: #64748b; 
        display: flex; align-items: flex-start; gap: 6px; line-height: 1.4;
      }
      .object-rating { 
        display: flex; flex-direction: column; gap: 6px; 
        margin-bottom: 12px; padding: 12px; 
        background: rgba(22,143,4,0.08); border-radius: 10px; align-items: center;
      }
      .object-rating .stars { 
        color: #fbbf24; font-size: 18px; letter-spacing: 2px; text-shadow: 0 1px 2px rgba(0,0,0,0.1);
      }
      .object-rating .rating-text { 
        font-size: 13px; font-weight: 600; color: #168f04; display: flex; align-items: center; gap: 4px;
      }
      .object-rating .rating-value { font-size: 16px; font-weight: 700; }
      .object-rating .rating-count { font-size: 12px; color: #64748b; font-weight: 500; }
      .object-rating .no-rating { color: #94a3b8; font-style: italic; }
      .object-card-footer { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
      .object-type { 
        font-size: 11px; font-weight: 600; color: #168f04; 
        background: rgba(22,143,4,0.1); padding: 4px 10px; border-radius: 20px; text-transform: uppercase; 
      }
      .review-btn { 
        display: flex; align-items: center; gap: 6px; 
        background: linear-gradient(135deg, #168f04 0%, #007306 100%); 
        color: white; border: none; padding: 10px 18px; border-radius: 10px; 
        font-size: 12px; font-weight: 600; cursor: pointer; 
        transition: all 0.3s; box-shadow: 0 4px 14px rgba(22,143,4,0.3); 
      }
      .review-btn:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(22,143,4,0.45); }
    </style>
  `
}

function getRatingWord(count) {
  if (count % 10 === 1 && count % 100 !== 11) return 'оценка'
  if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) return 'оценки'
  return 'оценок'
}