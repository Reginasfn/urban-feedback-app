from sqlalchemy import text
from typing import List, Optional
from api.schemas import ObjectWithTypeName

def get_user_preferences(db, user_id: int):
    """
    Получает предпочитаемые типы объектов на основе:
    - избранных объектов
    - отзывов с рейтингом 4-5
    """
    query = text("""
        SELECT DISTINCT t.name_type
        FROM objects o
        LEFT JOIN type_object t ON o.id_type = t.id_type
        LEFT JOIN favorites f ON f.id_object = o.id_object AND f.id_user = :user_id
        LEFT JOIN reviews r ON r.id_object = o.id_object 
            AND r.id_user = :user_id 
            AND r.id_status = 2
            AND r.rating >= 4
        WHERE (f.id_favorite IS NOT NULL OR r.id_review IS NOT NULL)
          AND o.id_status = 2
          AND t.name_type IS NOT NULL
    """)
    
    result = db.execute(query, {"user_id": user_id})
    return [row.name_type for row in result.fetchall()]


def get_seen_object_ids(db, user_id: int):
    """
    Получает ID объектов, с которыми пользователь уже взаимодействовал
    """
    query = text("""
        SELECT DISTINCT o.id_object
        FROM objects o
        LEFT JOIN favorites f ON f.id_object = o.id_object AND f.id_user = :user_id
        LEFT JOIN reviews r ON r.id_object = o.id_object AND r.id_user = :user_id
        WHERE (f.id_favorite IS NOT NULL OR r.id_review IS NOT NULL)
          AND o.id_status = 2
    """)
    
    result = db.execute(query, {"user_id": user_id})
    return [row.id_object for row in result.fetchall()]


def get_fallback_recommendations(db, limit: int = 8):
    """
    Для новых пользователей: популярные объекты по рейтингу
    """
    query = text("""
        SELECT 
            o.id_object, o.name, t.name_type as type_name, o.address,
            ST_Y(o.location::geometry) as lat, 
            ST_X(o.location::geometry) as lon,
            o.id_status, o.created_at,
            COALESCE(AVG(r.rating), 0) as rating_avg,
            COUNT(r.id_review) as rating_count
        FROM objects o
        LEFT JOIN type_object t ON o.id_type = t.id_type
        LEFT JOIN reviews r ON r.id_object = o.id_object AND r.id_status = 2
        WHERE o.id_status = 2
        GROUP BY o.id_object, t.name_type
        ORDER BY rating_avg DESC, rating_count DESC
        LIMIT :limit
    """)
    
    result = db.execute(query, {"limit": limit})
    return result.fetchall()


def get_personalized_recommendations(db, user_id: int, liked_types: List[str], seen_ids: List[int], limit: int = 8):
    """
    Персонализированные рекомендации с весовым скорингом
    """
    query = text("""
        SELECT 
            o.id_object, o.name, t.name_type as type_name, o.address,
            ST_Y(o.location::geometry) as lat, 
            ST_X(o.location::geometry) as lon,
            o.id_status, o.created_at,
            COALESCE(AVG(r.rating), 0) as rating_avg,
            COUNT(r.id_review) as rating_count,
            (
                CASE WHEN t.name_type = ANY(:liked_types) THEN 5 ELSE 0 END +
                CASE WHEN AVG(r.rating) >= 4.0 THEN 3 
                     WHEN AVG(r.rating) >= 3.0 THEN 1 
                     ELSE 0 
                END
            ) as recommendation_score
        FROM objects o
        LEFT JOIN type_object t ON o.id_type = t.id_type
        LEFT JOIN reviews r ON r.id_object = o.id_object AND r.id_status = 2
        WHERE o.id_status = 2
          AND o.id_object != ALL(:seen_ids)
        GROUP BY o.id_object, t.name_type
        HAVING (
            CASE WHEN t.name_type = ANY(:liked_types) THEN 5 ELSE 0 END +
            CASE WHEN AVG(r.rating) >= 4.0 THEN 3 
                 WHEN AVG(r.rating) >= 3.0 THEN 1 
                 ELSE 0 
            END
        ) > 0
        ORDER BY recommendation_score DESC, rating_avg DESC, rating_count DESC
        LIMIT :limit
    """)
    
    result = db.execute(
        query,
        {
            "liked_types": liked_types,
            "seen_ids": seen_ids,
            "limit": limit
        }
    )
    return result.fetchall()


def format_recommendation_row(row) -> dict:
    """
    Преобразует строку результата в словарь для ответа API
    """
    return {
        "id_object": row.id_object,
        "name": row.name,
        "type_name": row.type_name or "Не указан",
        "address": row.address,
        "coords": [float(row.lat), float(row.lon)],
        "id_status": row.id_status,
        "created_at": row.created_at,
        "rating_avg": float(row.rating_avg) if row.rating_avg else None,
        "rating_count": row.rating_count
    }