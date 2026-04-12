from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sys
sys.path.append('.')
from utils.database import get_db_connection

router = APIRouter(prefix="/reviews", tags=["Reviews"])

class ReviewCreate(BaseModel):
    id_object: int
    id_user: int
    text: str
    rating: int
    id_category_review: Optional[int] = None
    id_status: int = 1  # По умолчанию активен

@router.post("/")
async def create_review(review: ReviewCreate):
    """Добавить новый отзыв"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Валидация рейтинга
        if not (1 <= review.rating <= 5):
            raise HTTPException(status_code=400, detail="Рейтинг должен быть от 1 до 5")
        
        # Проверка существования объекта
        cursor.execute("SELECT id_object FROM objects WHERE id_object = %s", (review.id_object,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Объект не найден")
        
        # Проверка существования пользователя
        cursor.execute("SELECT id_user FROM users WHERE id_user = %s", (review.id_user,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Проверка категории (если указана)
        if review.id_category_review:
            cursor.execute(
                "SELECT id_category_review FROM review_categories WHERE id_category_review = %s",
                (review.id_category_review,)
            )
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Категория отзыва не найдена")
        
        # Создание отзыва
        cursor.execute("""
            INSERT INTO reviews 
            (id_object, id_user, text, rating, id_category_review, id_status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_review
        """, (
            review.id_object,
            review.id_user,
            review.text,
            review.rating,
            review.id_category_review,
            review.id_status,
            datetime.now()
        ))
        
        review_id = cursor.fetchone()[0]
        conn.commit()
        
        return {
            "success": True,
            "message": "Отзыв успешно добавлен",
            "id_review": review_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")
    finally:
        if conn:
            cursor.close()
            conn.close()

@router.get("/categories")
async def get_review_categories():
    """Получить список категорий отзывов"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id_category_review, name 
            FROM review_categories 
            ORDER BY name
        """)
        
        categories = [
            {"id": row[0], "name": row[1]}
            for row in cursor.fetchall()
        ]
        
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
    finally:
        if conn:
            cursor.close()
            conn.close()