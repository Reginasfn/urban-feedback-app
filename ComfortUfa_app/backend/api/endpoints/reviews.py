from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os

# 👇 Относительные импорты
from ..database import get_db_connection
from ..utils.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

# ===== Модели =====
class ReviewCreate(BaseModel):
    id_object: int
    text: str
    rating: int
    category: str
    photo: Optional[str] = None

class ReviewResponse(BaseModel):
    success: bool
    message: str
    id_review: Optional[int] = None

# ===== Маппинг категорий =====
CATEGORY_MAP = {
    'praise': 3,        # Похвала
    'suggestion': 2,    # Предложение  
    'problem': 1        # Проблема
}

# ===== Эндпоинт создания отзыва =====
@router.post("/", response_model=ReviewResponse)
async def create_review(
    id_object: int = Form(...),
    text: str = Form(..., min_length=10, max_length=500),
    rating: int = Form(..., ge=1, le=5),
    category: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    current_user = Depends(get_current_user)
):
    """Добавить новый отзыв с опциональным фото"""
    
    # Валидация категории
    if category not in CATEGORY_MAP:
        raise HTTPException(status_code=400, detail="Неверная категория отзыва")
    
    id_category_review = CATEGORY_MAP[category]
    
    # 👇 ИСПРАВЛЕНО: обращаемся через точку (User объект, не словарь)
    id_user = current_user.id_user
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Проверка существования объекта
        cursor.execute("SELECT id_object, name FROM objects WHERE id_object = %s", (id_object,))
        obj = cursor.fetchone()
        if not obj:
            raise HTTPException(status_code=404, detail="Объект не найден")
        
        # Обработка фото
        photo_path = None
        if photo and photo.filename:
            upload_dir = "resources/pic_obj"
            os.makedirs(upload_dir, exist_ok=True)
            
            import uuid
            ext = os.path.splitext(photo.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            photo_path = os.path.join(upload_dir, filename)
            
            with open(photo_path, "wb") as f:
                f.write(await photo.read())
            
            photo_path = photo_path.replace("\\", "/")
        
        # Создание отзыва
        cursor.execute("""
            INSERT INTO reviews 
            (id_object, id_user, text, rating, id_category_review, id_status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id_review
        """, (
            id_object,
            id_user,
            text.strip(),
            rating,
            id_category_review,
            2,
            datetime.now()
        ))
        
        review_id = cursor.fetchone()[0]
        
        if photo_path:
            cursor.execute("""
                INSERT INTO photos (review_id, file_path)
                VALUES (%s, %s)
            """, (review_id, photo_path))
        
        conn.commit()
        
        return ReviewResponse(
            success=True,
            message="Отзыв успешно добавлен",
            id_review=review_id
        )
        
    except HTTPException:
        if conn: conn.rollback()
        raise
    except Exception as e:
        if conn: conn.rollback()
        print(f"[ReviewCreate] Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера при создании отзыва")
    finally:
        if conn:
            cursor.close()
            conn.close()

# ===== Получение категорий =====
@router.get("/categories")
async def get_review_categories():
    """Получить список категорий отзывов с иконками"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id_category_review, name 
            FROM review_categories 
            ORDER BY id_category_review
        """)
        
        categories = [
            {
                "id": row[0], 
                "name": row[1],
                "value": "problem" if row[0] == 1 else "suggestion" if row[0] == 2 else "praise",
                "icon": "pi pi-exclamation-circle" if row[0] == 1 else "pi pi-lightbulb" if row[0] == 2 else "pi pi-thumbs-up"
            }
            for row in cursor.fetchall()
        ]
        
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
    finally:
        if conn:
            cursor.close()
            conn.close()

# ===== Получение отзывов для объекта =====
@router.get("/object/{object_id}")
async def get_object_reviews(object_id: int, limit: int = 10, offset: int = 0):
    """Получить отзывы для конкретного объекта"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                r.id_review,
                r.text,
                r.rating,
                r.created_at,
                rc.name as category_name,
                u.nickname,
                p.file_path as photo_path
            FROM reviews r
            JOIN review_categories rc ON r.id_category_review = rc.id_category_review
            JOIN users u ON r.id_user = u.id_user
            LEFT JOIN photos p ON r.id_review = p.review_id
            WHERE r.id_object = %s AND r.id_status = 2
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
        """, (object_id, limit, offset))
        
        reviews = []
        for row in cursor.fetchall():
            reviews.append({
                "id": row[0],
                "text": row[1],
                "rating": row[2],
                "created_at": row[3].isoformat() if row[3] else None,
                "category": row[4],
                "author": row[5] or "Аноним",
                "photo": f"http://localhost:8000/{row[6]}" if row[6] else None
            })
        
        cursor.execute("""
            SELECT COUNT(*) FROM reviews 
            WHERE id_object = %s AND id_status = 2
        """, (object_id,))
        total = cursor.fetchone()[0]
        
        return {
            "reviews": reviews,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")
    finally:
        if conn:
            cursor.close()
            conn.close()