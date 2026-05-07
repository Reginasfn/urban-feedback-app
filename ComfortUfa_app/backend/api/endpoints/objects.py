from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from api.database import get_db
from api.schemas import ObjectWithTypeName, ObjectCreate, ObjectResponse

router = APIRouter(prefix="/api", tags=["Объекты"])

# ===== ПРОВЕРКА НА ДУБЛИ (только тот же тип!) =====
def check_duplicate_object(db: Session, name: str, coords: list, type_name: str, radius_meters: float = 15):
    """
    Проверяет дубли ТОЛЬКО в рамках одного типа объекта.
    """
    lat, lon = coords
    
    query = text("""
        SELECT 
            o.id_object, o.name, o.address,
            ST_Y(o.location::geometry) as lat, 
            ST_X(o.location::geometry) as lon,
            t.name_type as type_name,
            ST_Distance(
                o.location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            ) as distance_m
        FROM public.objects o
        LEFT JOIN public.type_object t ON o.id_type = t.id_type
        WHERE 
            o.id_status = 2
            AND t.name_type = :check_type  -- 👇 ПРОВЕРЯЕМ ТОЛЬКО ЭТОТ ТИП!
            AND ST_DWithin(
                o.location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius
            )
        ORDER BY distance_m ASC
        LIMIT 5
    """)
    
    results = db.execute(query, {
        "lat": lat, 
        "lon": lon, 
        "radius": radius_meters,
        "check_type": type_name  # 👇 Фильтр по типу
    }).fetchall()
    
    name_lower = name.lower().strip()
    
    for row in results:
        existing_name = row.name.lower().strip()
        if (name_lower == existing_name or 
            name_lower in existing_name or 
            existing_name in name_lower):
            return {
                "id_object": row.id_object,
                "name": row.name,
                "type_name": row.type_name,
                "address": row.address,
                "distance_m": round(row.distance_m, 1)
            }
    return None

# ===== GET ОБЪЕКТОВ (без bbox - как раньше) =====
@router.get("/objects", response_model=List[ObjectWithTypeName])
async def get_objects(
    type: Optional[str] = Query(None, description="Тип объекта"),
    search: Optional[str] = Query(None, description="Поиск"),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db)
):
    try:
        where_conditions = ["o.id_status = 2"]
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
                "coords": [row.lat, row.lon],
                "id_status": row.id_status,
                "created_at": row.created_at
            }
            for row in rows
        ]
        
        return objects
        
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)[:200]}")


@router.get("/objects/types", response_model=List[str])
async def get_object_types(db: Session = Depends(get_db)):
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
        return [
            "Камера видеонаблюдения", "Кафе", "Фонарь", "Скамейка",
            "Парк", "Беседка", "Остановка", "Детская площадка"
        ]

# ===== POST: СОЗДАНИЕ ОБЪЕКТА С ПРОВЕРКОЙ НА ДУБЛИ =====
@router.post("/objects", response_model=ObjectResponse, status_code=201)
async def create_object(
    obj_data: ObjectCreate,
    db: Session = Depends(get_db)
):
    try:
        print(f"📥 Создание объекта: {obj_data.name}, type: {obj_data.type_name}, coords: {obj_data.coords}")
        
        # 🔍 ПРОВЕРКА НА ДУБЛИ (только тот же тип!)
        duplicate = check_duplicate_object(
            db=db,
            name=obj_data.name,
            coords=obj_data.coords,
            type_name=obj_data.type_name,  # 👇 Передаём тип!
            radius_meters=15
        )
        
        if duplicate:
            print(f"⚠️ Найден дубль: {duplicate['name']} ({duplicate['type_name']}) на расстоянии {duplicate['distance_m']}м")
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "duplicate_object",
                    "message": f"Объект '{duplicate['name']}' ({duplicate['type_name']}) уже существует поблизости ({duplicate['distance_m']}м)",
                    "existing_object": duplicate
                }
            )
        
        # Находим id_type
        type_query = text("SELECT id_type FROM public.type_object WHERE name_type = :type_name")
        type_result = db.execute(type_query, {"type_name": obj_data.type_name}).first()
        
        if not type_result:
            all_types = db.execute(text("SELECT name_type FROM public.type_object")).fetchall()
            available_types = [t[0] for t in all_types]
            raise HTTPException(
                status_code=400,
                detail=f"Тип '{obj_data.type_name}' не найден. Доступные: {available_types}"
            )
        
        id_type = type_result.id_type
        lat, lon = obj_data.coords
        
        # Создаём объект
        insert_query = text("""
            INSERT INTO public.objects (
                name, id_type, address, location, id_status, created_by
            ) VALUES (
                :name, :id_type, :address, 
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                2, 1
            )
            RETURNING 
                id_object, name, id_type, address,
                ST_Y(location::geometry) as lat,
                ST_X(location::geometry) as lon,
                id_status, created_by, created_at, osm_id
        """)
        
        result = db.execute(
            insert_query,
            {
                "name": obj_data.name,
                "id_type": id_type,
                "address": obj_data.address,
                "lat": float(lat),
                "lon": float(lon)
            }
        )
        
        new_object = result.first()
        db.commit()
        
        print(f"✅ Объект создан: id={new_object.id_object}")
        
        return {
            "id_object": new_object.id_object,
            "name": new_object.name,
            "id_type": new_object.id_type,
            "address": new_object.address,
            "coords": [float(new_object.lat), float(new_object.lon)],
            "id_status": new_object.id_status,
            "created_by": new_object.created_by,
            "created_at": new_object.created_at,
            "osm_id": new_object.osm_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)[:200]}")