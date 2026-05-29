from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.user import User
from api.utils.auth import get_optional_current_user
from api.services import recommendations as recommendations_service
from api.schemas import ObjectWithTypeName

router = APIRouter(prefix="/api/recommendations", tags=["Рекомендации"])


@router.get("/{user_id}", response_model=list[ObjectWithTypeName])
async def get_recommendations(
    user_id: int,
    limit: int = 8,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user)
):
    """
    Персонализированные рекомендации объектов
    """
    
    if not current_user or current_user.id_user != user_id:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    
    try:
        # Получаем предпочтения пользователя
        liked_types = recommendations_service.get_user_preferences(db, user_id)
        seen_ids = recommendations_service.get_seen_object_ids(db, user_id)
        
        # Если нет предпочтений — отдаём популярные объекты
        if not liked_types:
            rows = recommendations_service.get_fallback_recommendations(db, limit)
            return [recommendations_service.format_recommendation_row(row) for row in rows]
        
        # Иначе — персонализированные рекомендации
        rows = recommendations_service.get_personalized_recommendations(
            db, user_id, liked_types, seen_ids, limit
        )
        
        return [recommendations_service.format_recommendation_row(row) for row in rows]
        
    except Exception as e:
        print(f"[Recommendations] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)[:200]}")