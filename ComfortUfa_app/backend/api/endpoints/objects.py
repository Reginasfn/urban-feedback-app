from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List

from api.database import get_db
from api.schemas import ObjectWithTypeName, ObjectCreate, ObjectResponse
from api.models.user import User
from api.utils.auth import get_current_active_user

router = APIRouter(prefix="/api", tags=["Объекты"])


async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Получает текущего пользователя или None если не авторизован"""
    try:
        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if not token:
            return None
            
        # Пробуем получить пользователя через оригинальную функцию
        return await get_current_active_user(request=request, db=db)
    except Exception as e:
        print(f"[get_optional_current_user] Not authenticated: {e}")
        return None


def check_duplicate_object(db: Session, name: str, coords: list, type_name: str, radius_meters: float = 15):
    """
    Проверяет наличие дублирующего объекта того же типа в указанном радиусе.
    Сравнивает названия (точное совпадение или частичное).
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
            AND t.name_type = :check_type
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
        "check_type": type_name
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


@router.get("/objects", response_model=List[ObjectWithTypeName])
async def get_objects(
    # Основные параметры
    type: Optional[str] = Query(None, description="Тип объекта"),
    search: Optional[str] = Query(None, description="Поиск по названию/адресу"),
    limit: int = Query(1000, ge=1, le=1500),
    bbox: Optional[str] = Query(None, description="BBOX: min_lon,min_lat,max_lon,max_lat"),
    
    # Фильтр: рядом со мной
    near_lat: Optional[float] = Query(None, description="Широта пользователя"),
    near_lon: Optional[float] = Query(None, description="Долгота пользователя"),
    near_radius: Optional[int] = Query(500, ge=100, le=5000, description="Радиус в метрах"),
    
    # Фильтр: избранное
    bookmarked_ids: Optional[str] = Query(None, description="Список ID избранных: 123,456,789"),
    
    # Фильтр: мои объекты
    mine: Optional[bool] = Query(None, description="Только мои объекты"),
    current_user: Optional[User] = Depends(get_optional_current_user),
    
    # Фильтр: проблемные объекты
    min_problems: Optional[int] = Query(None, ge=1, description="Мин. количество жалоб"),
    max_rating: Optional[float] = Query(None, ge=0, le=5, description="Макс. рейтинг"),
    
    # Фильтр: высокий рейтинг
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Мин. рейтинг"),
    
    db: Session = Depends(get_db)
):
    try:
        where_conditions = ["o.id_status = 2"]
        params = {"limit": limit}
        
        # 1. BBOX фильтрация (видимая область карты)
        if bbox:
            try:
                min_lon, min_lat, max_lon, max_lat = map(float, bbox.split(','))
                where_conditions.append("""
                    ST_Intersects(
                        o.location::geometry,
                        ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326)
                    )
                """)
                params.update({
                    "min_lon": min_lon, 
                    "min_lat": min_lat,
                    "max_lon": max_lon, 
                    "max_lat": max_lat
                })
            except ValueError as e:
                print(f"Ошибка парсинга bbox: {e}")
        
        # 2. Рядом со мной (геолокация)
        if near_lat is not None and near_lon is not None:
            where_conditions.append("""
                ST_DWithin(
                    o.location::geography,
                    ST_SetSRID(ST_MakePoint(:near_lon, :near_lat), 4326)::geography,
                    :near_radius
                )
            """)
            params.update({
                "near_lat": near_lat,
                "near_lon": near_lon,
                "near_radius": near_radius
            })
        
        # 3. Избранное (фильтрация по списку ID)
        if bookmarked_ids:
            ids = [int(x.strip()) for x in bookmarked_ids.split(',') if x.strip().isdigit()]
            if ids:
                where_conditions.append("o.id_object = ANY(:bookmarked_ids)")
                params["bookmarked_ids"] = ids
        
        # 4. Мои объекты (требует авторизации)
        if mine:
            if not current_user:
                raise HTTPException(
                    status_code=401, 
                    detail="Требуется авторизация для фильтра 'Мои объекты'"
                )
            where_conditions.append("o.created_by = :user_id")
            params["user_id"] = current_user.id_user
        
        # 5. Проблемные объекты (жалобы + низкий рейтинг)
        if min_problems is not None:
            where_conditions.append("""
                (SELECT COUNT(*) FROM reviews r 
                 JOIN review_categories rc ON r.id_category_review = rc.id_category_review
                 WHERE r.id_object = o.id_object 
                   AND r.id_status = 2 
                   AND rc.name = 'Проблема') >= :min_problems
            """)
            params["min_problems"] = min_problems
        
        if max_rating is not None:
            where_conditions.append("""
                COALESCE(
                    (SELECT AVG(r.rating) FROM reviews r 
                     WHERE r.id_object = o.id_object AND r.id_status = 2), 
                    5
                ) <= :max_rating
            """)
            params["max_rating"] = max_rating
        
        # 6. Высокий рейтинг
        if min_rating is not None:
            where_conditions.append("""
                (SELECT AVG(r.rating) FROM reviews r 
                 WHERE r.id_object = o.id_object AND r.id_status = 2) >= :min_rating
            """)
            params["min_rating"] = min_rating
        
        # 7. Тип объекта
        if type:
            where_conditions.append("t.name_type = :type")
            params["type"] = type
        
        # 8. Поиск
        if search:
            where_conditions.append("(o.name ILIKE :q OR o.address ILIKE :q)")
            params["q"] = f"%{search}%"
        
        # Формируем итоговый SQL запрос
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
        
        # 🔥 ВАЖНО: Получаем избранные объекты для текущего пользователя
        user_favorite_ids = set()
        if current_user:
            try:
                print(f"[get_objects] User {current_user.id_user} authenticated, loading favorites...")
                fav_query = text("""
                    SELECT id_object FROM favorites 
                    WHERE id_user = :user_id
                """)
                fav_result = db.execute(fav_query, {"user_id": current_user.id_user})
                user_favorite_ids = {row.id_object for row in fav_result.fetchall()}
                print(f"[get_objects] User has {len(user_favorite_ids)} favorites: {user_favorite_ids}")
            except Exception as e:
                print(f"[get_objects] Error loading favorites: {e}")
                user_favorite_ids = set()

        # Формируем ответ с полем is_bookmarked
        response_data = []
        for row in rows:
            is_bookmarked = row.id_object in user_favorite_ids
            response_data.append({
                "id_object": row.id_object, 
                "name": row.name,
                "type_name": row.type_name or "Не указан", 
                "address": row.address,
                "coords": [row.lat, row.lon], 
                "id_status": row.id_status,
                "created_at": row.created_at,
                "is_bookmarked": is_bookmarked,  # 🔥 Добавляем поле
                "rating_avg": None,  # Эти поля будут заполнены при загрузке рейтинга
                "rating_count": 0
            })
        
        print(f"[get_objects] Returning {len(response_data)} objects, user favorites: {len(user_favorite_ids)}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ошибка БД: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка сервера: {str(e)[:200]}"
        )


@router.get("/objects/types", response_model=List[str])
async def get_object_types(db: Session = Depends(get_db)):
    """Получение списка всех типов объектов"""
    try:
        query = text("""
            SELECT DISTINCT name_type 
            FROM public.type_object 
            WHERE name_type IS NOT NULL 
            ORDER BY name_type
        """)
        result = db.execute(query)
        return [row[0] for row in result.fetchall()]
    except Exception as e:
        print(f"Ошибка получения типов: {e}")
        return [
            "Камера видеонаблюдения", "Кафе", "Фонарь", "Скамейка",
            "Парк", "Беседка", "Остановка", "Детская площадка"
        ]


@router.post("/objects", response_model=ObjectResponse, status_code=201)
async def create_object(
    obj_data: ObjectCreate, 
    db: Session = Depends(get_db)
):
    """Создание нового объекта с проверкой на дубли"""
    try:
        print(f"Создание объекта: {obj_data.name}, тип: {obj_data.type_name}")
        
        # Проверка на дубликаты
        duplicate = check_duplicate_object(
            db=db, 
            name=obj_data.name, 
            coords=obj_data.coords,
            type_name=obj_data.type_name, 
            radius_meters=15
        )
        
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "duplicate_object",
                    "message": f"Объект '{duplicate['name']}' ({duplicate['type_name']}) уже существует поблизости ({duplicate['distance_m']}м)",
                    "existing_object": duplicate
                }
            )
        
        # Поиск ID типа объекта
        type_query = text(
            "SELECT id_type FROM public.type_object WHERE name_type = :type_name"
        )
        type_result = db.execute(
            type_query, {"type_name": obj_data.type_name}
        ).first()
        
        if not type_result:
            raise HTTPException(
                status_code=400, 
                detail=f"Тип объекта '{obj_data.type_name}' не найден"
            )
        
        id_type = type_result.id_type
        lat, lon = obj_data.coords
        
        # Создание объекта
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
            insert_query, {
                "name": obj_data.name, 
                "id_type": id_type, 
                "address": obj_data.address,
                "lat": float(lat), 
                "lon": float(lon)
            }
        )
        
        new_object = result.first()
        db.commit()
        
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
        print(f"Ошибка создания объекта: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка сервера: {str(e)[:200]}"
        )


# ===== ИЗБРАННОЕ =====

@router.get("/objects/me/favorites/ids")
async def get_my_favorite_ids(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить список ID избранных объектов текущего пользователя"""
    try:
        print(f"[favorites/ids] User {current_user.id_user} requesting favorites")
        query = text("""
            SELECT id_object 
            FROM favorites 
            WHERE id_user = :user_id
        """)
        result = db.execute(query, {"user_id": current_user.id_user})
        favorite_ids = [row.id_object for row in result.fetchall()]
        print(f"[favorites/ids] Found {len(favorite_ids)} favorites: {favorite_ids}")
        return {"favorite_ids": favorite_ids}
    except Exception as e:
        print(f"Ошибка получения избранного: {e}")
        return {"favorite_ids": []}


@router.post("/objects/{object_id}/favorite")
async def add_to_favorites(
    object_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Добавить объект в избранное"""
    try:
        print(f"[POST favorite] User {current_user.id_user} adding object {object_id}")
        
        # Проверяем существование объекта
        obj_check = db.execute(
            text("SELECT id_object FROM objects WHERE id_object = :id AND id_status = 2"),
            {"id": object_id}
        ).first()
        
        if not obj_check:
            raise HTTPException(status_code=404, detail="Объект не найден")
        
        # Проверяем, нет ли уже в избранном
        exists = db.execute(
            text("""
                SELECT id_favorite FROM favorites 
                WHERE id_user = :user_id AND id_object = :obj_id
            """),
            {"user_id": current_user.id_user, "obj_id": object_id}
        ).first()
        
        if exists:
            print(f"[POST favorite] Object {object_id} already in favorites")
            return {"message": "Уже в избранном", "id_favorite": exists.id_favorite}
        
        # Добавляем в избранное
        insert_query = text("""
            INSERT INTO favorites (id_user, id_object) 
            VALUES (:user_id, :obj_id)
            RETURNING id_favorite
        """)
        
        result = db.execute(
            insert_query,
            {"user_id": current_user.id_user, "obj_id": object_id}
        )
        
        db.commit()
        new_id = result.first().id_favorite
        
        print(f"[POST favorite] Object {object_id} added to favorites with id {new_id}")
        return {"message": "Добавлено в избранное", "id_favorite": new_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Ошибка добавления в избранное: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@router.delete("/objects/{object_id}/favorite")
async def remove_from_favorites(
    object_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удалить объект из избранного"""
    try:
        print(f"[DELETE favorite] User {current_user.id_user} removing object {object_id}")
        
        # Удаляем из избранного
        delete_query = text("""
            DELETE FROM favorites 
            WHERE id_user = :user_id AND id_object = :obj_id
        """)
        
        result = db.execute(
            delete_query,
            {"user_id": current_user.id_user, "obj_id": object_id}
        )
        
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Не найдено в избранном")
        
        print(f"[DELETE favorite] Object {object_id} removed from favorites")
        return {"message": "Удалено из избранного"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Ошибка удаления из избранного: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")