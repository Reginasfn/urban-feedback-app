from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from ..database import get_db
from ..schemas import ObjectWithTypeName

# Создаём роутер с префиксом /api
router = APIRouter(prefix="/api", tags=["Объекты благоустройства"])

@router.get("/objects", response_model=List[ObjectWithTypeName])
async def get_objects(
    type: Optional[str] = Query(None, description="Фильтр по типу объекта"),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db)
):
    """Получение объектов для карты"""
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
                "coords": [row.lat, row.lon],
                "id_status": row.id_status,
                "created_at": row.created_at
            }
            for row in rows
        ]
        
        return objects
        
    except Exception as e:
        # 🛡️ Безопасная обработка ошибок
        error_msg = str(e)
        print(f"❌ Ошибка БД: {error_msg}")
        
        # Проверяем тип ошибки и возвращаем понятный ответ
        if "password" in error_msg.lower() or "fe_sendauth" in error_msg:
            return {"error": "Не удалось подключиться к базе данных. Проверьте пароль в .env"}
        
        if "relation" in error_msg.lower() and "does not exist" in error_msg:
            return {"error": "Таблица не найдена. Проверьте наличие таблиц 'objects' и 'types'"}
        
        # Для остальных ошибок
        raise HTTPException(
            status_code=500,
            detail={"error": "Внутренняя ошибка сервера", "message": error_msg[:200]}
        )

async def get_objects(
    type: Optional[str] = Query(
        None, 
        description="Название типа объекта для фильтрации (например, 'Фонарь', 'Скамейка')",
        example="Фонарь"
    ),
    limit: int = Query(
        1000, 
        ge=1, 
        le=5000, 
        description="Максимальное количество возвращаемых объектов"
    ),
    db: Session = Depends(get_db)
):
    """
    🔍 Получение объектов с фильтрацией по типу.
    
    Делает JOIN с таблицей types для получения названия типа объекта.
    Использует PostGIS функции ST_X и ST_Y для извлечения координат.
    
    **Параметры:**
    - `type`: фильтр по названию типа (опционально)
    - `limit`: лимит выдачи (по умолчанию 1000)
    
    **Возвращает:**
    Массив объектов с полями: id_object, name, type_name, address, coords, id_status, created_at
    """
    try:
        # 🗄️ SQL-запрос с JOIN к таблице types
        # Предполагаем, что есть таблица public.types с полями: id_type, name_type
        query = text("""
            SELECT 
                o.id_object,
                o.name,
                t.name_type as type_name,  -- Получаем название типа из таблицы types
                o.address,
                ST_Y(o.location::geometry) as lat,  # Извлекаем широту (Y)
                ST_X(o.location::geometry) as lon,  # Извлекаем долготу (X)
                o.id_status,
                o.created_at
            FROM public.objects o
            LEFT JOIN public.types t ON o.id_type = t.id_type  # JOIN с таблицей типов
            WHERE (:type IS NULL OR t.name_type = :type)  # Фильтр по названию типа
            ORDER BY o.created_at DESC
            LIMIT :limit
        """)
        
        # Выполняем запрос с параметрами
        result = db.execute(query, {"type": type, "limit": limit})
        rows = result.fetchall()
        
        # 🔧 Преобразуем строки БД в список словарей
        objects = []
        for row in rows:
            objects.append({
                "id_object": row.id_object,
                "name": row.name,
                "type_name": row.type_name or "Не указан",  # Если типа нет — ставим заглушку
                "address": row.address,
                "coords": [row.lat, row.lon],  # [широта, долгота] для Яндекс.Карт
                "id_status": row.id_status,
                "created_at": row.created_at
            })
        
        print(f"✅ Найдено объектов: {len(objects)} (тип: {type or 'все'})")
        return objects
        
    except Exception as e:
        # 🚨 Обработка ошибок
        print(f"❌ Ошибка при загрузке объектов: {e}")
        print(f"   Тип ошибки: {type(e).__name__}")
        
        # Проверяем, есть ли таблица types
        if "relation \"public.types\" does not exist" in str(e):
            raise HTTPException(
                status_code=500,
                detail="Таблица 'types' не найдена. Создайте таблицу public.types с полями: id_type, name_type"
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера при загрузке объектов: {str(e)}"
        )

@router.get(
    "/objects/types",
    response_model=List[str],
    summary="Получить список типов объектов",
    description="Возвращает все доступные типы объектов для фильтров"
)
async def get_object_types(
    db: Session = Depends(get_db)
):
    """
    📋 Получение списка всех типов объектов.
    Используется для заполнения кнопок-фильтров на фронтенде.
    """
    try:
        query = text("""
            SELECT DISTINCT name_type
            FROM public.type_object
            WHERE name_type IS NOT NULL
            ORDER BY name_type
        """)
        
        result = db.execute(query)
        types = [row[0] for row in result.fetchall()]
        
        return types
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке типов: {e}")
        # Если таблицы types нет — возвращаем хардкод (для тестирования)
        return [
            "Камера видеонаблюдения",
            "Кафе",
            "Фонарь",
            "Скамейка",
            "Парк",
            "Беседка",
            "Остановка",
            "Детская площадка"
        ]

@router.get("/objects/{object_id}", response_model=ObjectWithTypeName)
async def get_object_by_id(
    object_id: int,
    db: Session = Depends(get_db)
):
    """
    🔎 Получение одного объекта по ID.
    """
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
        LEFT JOIN public.types t ON o.id_type = t.id_type
        WHERE o.id_object = :id
    """)
    
    result = db.execute(query, {"id": object_id})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Объект не найден")
    
    return {
        "id_object": row.id_object,
        "name": row.name,
        "type_name": row.type_name,
        "address": row.address,
        "coords": [row.lat, row.lon],
        "id_status": row.id_status,
        "created_at": row.created_at
    }