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
    search: Optional[str] = Query(None, description="Поиск по названию или адресу"),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db)
):
    """Получение объектов для карты с фильтрацией и поиском"""
    try:
        # 👇 Динамически строим WHERE-условия
        where_conditions = ["o.id_status = 2"]  # только одобренные
        params = {"limit": limit}
        
        if type:
            where_conditions.append("t.name_type = :type")
            params["type"] = type
            
        if search:
            where_conditions.append("(o.name ILIKE :q OR o.address ILIKE :q)")
            params["q"] = f"%{search}%"
        
        query_text = f"""
            SELECT 
                o.id_object, o.name, t.name_type as type_name, o.address,
                ST_Y(o.location::geometry) as lat, ST_X(o.location::geometry) as lon,
                o.id_status, o.created_at
            FROM public.objects o
            LEFT JOIN public.type_object t ON o.id_type = t.id_type
            WHERE {" AND ".join(where_conditions)}
            ORDER BY o.created_at DESC
            LIMIT :limit
        """
        
        query = text(query_text)
        result = db.execute(query, params)
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

@router.get("/objects/top-categories", response_model=List[dict])
async def get_top_categories(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Возвращает топ категорий по количеству объектов в БД"""
    try:
        query = text("""
            SELECT 
                t.name_type as category,
                COUNT(o.id_object) as count
            FROM public.objects o
            LEFT JOIN public.type_object t ON o.id_type = t.id_type
            WHERE o.id_status = 2  -- только одобренные объекты
              AND t.name_type IS NOT NULL
            GROUP BY t.name_type
            ORDER BY count DESC
            LIMIT :limit
        """)
        
        result = db.execute(query, {"limit": limit})
        rows = result.fetchall()
        
        return [
            {"category": row.category, "count": row.count}
            for row in rows
        ]
        
    except Exception as e:
        print(f"❌ Ошибка при получении топ-категорий: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)[:200]}"
        )