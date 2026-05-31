# backend/api/endpoints/stats.py
"""
Эндпоинты для получения расширенной статистики платформы
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc
from typing import Optional, List
from datetime import datetime, timedelta

from api.database import get_db
from api.schemas import PlatformStats

router = APIRouter(prefix="/api", tags=["Statistics"])

@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(db: Session = Depends(get_db)):
    """Общая статистика платформы"""
    try:
        # Всего объектов
        objects_query = text("SELECT COUNT(*) as count FROM public.objects WHERE id_status = 2")
        result = db.execute(objects_query).first()
        total_objects = result.count if result else 0
        
        # Проблемы (отзывы с категорией 'Проблема')
        problems_query = text("""
            SELECT COUNT(*) as count FROM public.reviews r
            INNER JOIN public.review_categories rc ON r.id_category_review = rc.id_category_review
            WHERE rc.name = 'Проблема' AND r.id_status = 2
        """)
        result = db.execute(problems_query).first()
        total_problems = result.count if result else 0
        
        # Пользователи
        users_query = text("""
            SELECT COUNT(*) as count FROM public.users u
            INNER JOIN public.roles r ON u.id_role = r.id_role
            WHERE r.name_role = 'Пользователь'
        """)
        result = db.execute(users_query).first()
        total_users = result.count if result else 0
        
        return PlatformStats(
            total_objects=total_objects,
            total_problems=total_problems,
            total_users=total_users
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/objects-by-type")
async def get_objects_by_type(db: Session = Depends(get_db)):
    """Распределение объектов по типам"""
    try:
        query = text("""
            SELECT t.name_type as type_name, COUNT(o.id_object) as count
            FROM public.type_object t
            LEFT JOIN public.objects o ON t.id_type = o.id_type AND o.id_status = 2
            GROUP BY t.id_type, t.name_type
            ORDER BY count DESC
        """)
        result = db.execute(query).all()
        return [{"label": row.type_name or "Не указан", "value": row.count} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/top-reviewed-objects")
async def get_top_reviewed_objects(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Топ объектов по количеству отзывов"""
    try:
        query = text("""
            SELECT o.id_object, o.name, t.name_type as type_name, 
                   COUNT(r.id_review) as review_count, AVG(r.rating) as avg_rating
            FROM public.objects o
            LEFT JOIN public.type_object t ON o.id_type = t.id_type
            LEFT JOIN public.reviews r ON o.id_object = r.id_object AND r.id_status = 2
            WHERE o.id_status = 2
            GROUP BY o.id_object, o.name, t.name_type
            HAVING COUNT(r.id_review) > 0
            ORDER BY review_count DESC
            LIMIT :limit
        """)
        result = db.execute(query, {"limit": limit}).all()
        return [{
            "id": row.id_object,
            "name": row.name,
            "type": row.type_name,
            "reviews": row.review_count,
            "rating": float(row.avg_rating) if row.avg_rating else None
        } for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/top-favorited-objects")
async def get_top_favorited_objects(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Топ объектов в избранном"""
    try:
        query = text("""
            SELECT o.id_object, o.name, t.name_type as type_name, 
                   COUNT(f.id_favorite) as favorite_count
            FROM public.objects o
            INNER JOIN public.type_object t ON o.id_type = t.id_type
            INNER JOIN public.favorites f ON o.id_object = f.id_object
            WHERE o.id_status = 2
            GROUP BY o.id_object, o.name, t.name_type
            ORDER BY favorite_count DESC
            LIMIT :limit
        """)
        result = db.execute(query, {"limit": limit}).all()
        return [{
            "id": row.id_object,
            "name": row.name,
            "type": row.type_name,
            "favorites": row.favorite_count
        } for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/favorite-types")
async def get_favorite_types(db: Session = Depends(get_db)):
    """Какие типы объектов чаще всего в избранном"""
    try:
        query = text("""
            SELECT t.name_type as type_name, COUNT(f.id_favorite) as favorite_count
            FROM public.type_object t
            INNER JOIN public.objects o ON t.id_type = o.id_type
            INNER JOIN public.favorites f ON o.id_object = f.id_object
            WHERE o.id_status = 2
            GROUP BY t.id_type, t.name_type
            ORDER BY favorite_count DESC
        """)
        result = db.execute(query).all()
        return [{"label": row.type_name, "value": row.favorite_count} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/reviews-by-category")
async def get_reviews_by_category(db: Session = Depends(get_db)):
    """Распределение отзывов по категориям с топ-3 объектами"""
    try:
        # Основной запрос для категорий
        query = text("""
            SELECT 
                rc.id_category_review,
                rc.name as category_name, 
                COUNT(r.id_review) as count
            FROM public.review_categories rc
            LEFT JOIN public.reviews r ON rc.id_category_review = r.id_category_review AND r.id_status = 2
            GROUP BY rc.id_category_review, rc.name
            ORDER BY count DESC
        """)
        categories_result = db.execute(query).all()
        
        result = []
        for category in categories_result:
            # Для каждой категории получаем топ-3 объекта с типами
            top_objects_query = text("""
                SELECT 
                    o.id_object,
                    o.name,
                    t.name_type as type_name,
                    COUNT(r.id_review) as review_count
                FROM public.reviews r
                INNER JOIN public.objects o ON r.id_object = o.id_object
                LEFT JOIN public.type_object t ON o.id_type = t.id_type
                WHERE r.id_category_review = :category_id 
                  AND r.id_status = 2 
                  AND o.id_status = 2
                GROUP BY o.id_object, o.name, t.name_type
                ORDER BY review_count DESC
                LIMIT 5
            """)
            top_objects = db.execute(top_objects_query, {"category_id": category.id_category_review}).all()
            
            result.append({
                "label": category.category_name or "Без категории",
                "value": category.count,
                "top_objects": [
                    {
                        "id": obj.id_object,
                        "name": obj.name,
                        "type": obj.type_name or "Не указан",
                        "count": obj.review_count
                    } for obj in top_objects
                ]
            })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/rating-distribution")
async def get_rating_distribution(db: Session = Depends(get_db)):
    """Распределение оценок (1-5 звёзд)"""
    try:
        query = text("""
            SELECT rating, COUNT(*) as count
            FROM public.reviews
            WHERE id_status = 2 AND rating IS NOT NULL
            GROUP BY rating
            ORDER BY rating ASC
        """)
        result = db.execute(query).all()
        # Заполняем пропущенные оценки нулями
        distribution = {str(i): 0 for i in range(1, 6)}
        for row in result:
            distribution[str(row.rating)] = row.count
        return [{"rating": k, "count": v} for k, v in distribution.items()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/activity-timeline")
async def get_activity_timeline(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Активность по дням (новые объекты + отзывы)"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        query = text("""
            SELECT DATE(created_at) as date, 
                   COUNT(CASE WHEN table_name = 'objects' THEN 1 END) as new_objects,
                   COUNT(CASE WHEN table_name = 'reviews' THEN 1 END) as new_reviews
            FROM (
                SELECT created_at, 'objects' as table_name FROM public.objects WHERE id_status = 2 AND created_at >= :start_date
                UNION ALL
                SELECT created_at, 'reviews' as table_name FROM public.reviews WHERE id_status = 2 AND created_at >= :start_date
            ) as combined
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        """)
        result = db.execute(query, {"start_date": start_date}).all()
        return [{"date": row.date.isoformat(), "objects": row.new_objects, "reviews": row.new_reviews} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))