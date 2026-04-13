"""
Эндпоинты для получения статистики платформы
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from api.database import get_db
from api.schemas import PlatformStats  # Импортируем схему из ШАГА 1

# Создаём роутер
router = APIRouter(prefix="/api", tags=["Statistics"])

@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(db: Session = Depends(get_db)):
    """
    Получение общей статистики платформы для главной страницы
    """
    try:
        # 📊 Запрос 1: Общее количество объектов
        objects_query = text("SELECT COUNT(*) as count FROM public.objects")
        objects_result = db.execute(objects_query).first()
        total_objects = objects_result.count if objects_result else 0
        
        # 📊 Запрос 2: Количество проблем (отзывы с category='problem')
        problems_query = text("""
            SELECT COUNT(*) as count 
            FROM public.reviews r
            INNER JOIN public.review_categories rc 
                ON r.id_category_review = rc.id_category_review
            WHERE rc.name = 'Проблема'
        """)
        try:
            problems_result = db.execute(problems_query).first()
            total_problems = problems_result.count if problems_result else 0
            print(f"✅ Найдено проблем: {total_problems}")
        except:
            print(f"⚠️ Ошибка подсчёта проблем: {e}")
            total_problems = 0  # Таблицы ещё нет
        
        # 📊 Запрос 3: Количество пользователей
        users_query = text("""
            SELECT COUNT(*) as count 
            FROM public.users r 
            INNER JOIN public.roles rc 
                ON r.id_role = rc.id_role
            WHERE rc.name_role = 'Пользователь'
        """)
        try:
            users_result = db.execute(users_query).first()
            total_users = users_result.count if users_result else 0
            print(f"✅ Найдено пользователей: {total_users}")
        except Exception as e:
            print(f"⚠️ Ошибка подсчёта пользователей: {e}")
            total_users = 0
        
        # ✅ Возвращаем статистику
        return PlatformStats(
            total_objects=total_objects,
            total_problems=total_problems,
            total_users=total_users
        )
        
    except Exception as e:
        print(f"❌ Ошибка статистики: {e}")
        raise HTTPException(status_code=500, detail=str(e))