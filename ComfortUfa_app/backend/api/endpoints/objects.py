# objects.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from api.database import get_db
from api.schemas import ObjectWithTypeName

# Создаём роутер
router = APIRouter(prefix="/api", tags=["Объекты"])

@router.get("/objects", response_model=List[ObjectWithTypeName])
async def get_objects(
    type: Optional[str] = Query(None, description="Тип объекта: Фонарь, Скамейка и т.д."),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db)
):
    """Получение объектов для карты с фильтрацией по типу"""
    try:
        query = text("""
            SELECT 
                o.id_object,
                o.name,
                t.name_type as type_name,
                o.address,
                ST_Y(o.location::geometry) as lat,
                ST_X(o.location::geometry) as lon,
                o.id_status,
                o.created_at
            FROM public.objects o
            LEFT JOIN public.type_object t ON o.id_type = t.id_type
            WHERE (:type IS NULL OR t.name_type = :type)
            ORDER BY o.created_at DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"type": type, "limit": limit})
        rows = result.fetchall()
        
        objects = [
            {
                "id_object": row.id_object,
                "name": row.name,
                "type_name": row.type_name or "Не указан",
                "address": row.address,
                "coords": [row.lat, row.lon],  # [широта, долгота] для Яндекс.Карт
                "id_status": row.id_status,
                "created_at": row.created_at
            }
            for row in rows
        ]
        
        return objects
        
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)[:200]}"
        )


@router.get("/objects/types", response_model=List[str])
async def get_object_types(db: Session = Depends(get_db)):
    """Список всех типов объектов для фильтров"""
    try:
        query = text("""
            SELECT DISTINCT name_type
            FROM public.type_object
            WHERE name_type IS NOT NULL
            ORDER BY name_type
        """)
        result = db.execute(query)
        return [row[0] for row in result.fetchall()]
    except:
        # Запасной вариант, если таблица не найдена
        return [
            "Камера видеонаблюдения", "Кафе", "Фонарь", "Скамейка",
            "Парк", "Беседка", "Остановка", "Детская площадка"
        ]