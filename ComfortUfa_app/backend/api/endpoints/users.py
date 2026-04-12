"""
Эндпоинты для управления профилем пользователя
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.database import get_db
from api.models.user import User
from api.schemas import UserResponse
from api.utils.auth import get_current_active_user, get_password_hash, verify_password

router = APIRouter(prefix="/api/users", tags=["Пользователи"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение данных текущего пользователя"""
    print(f"\n{'='*60}")
    print(f"🔍 [GET /me] Запрос профиля пользователя ID: {current_user.id_user}")
    print(f"   Email: {current_user.email}")
    print(f"   Nickname: {current_user.nickname}")
    
    role_query = text("SELECT name_role FROM roles WHERE id_role = :id_role")
    role_result = db.execute(role_query, {"id_role": current_user.id_role}).first()
    role_name = role_result.name_role if role_result else None
    
    print(f"   Роль: {role_name}")
    print(f"✅ [GET /me] Данные успешно получены\n")
    
    return {
        "id_user": current_user.id_user,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "phone": current_user.phone,
        "id_role": current_user.id_role,
        "role_name": role_name,
        "created_at": current_user.created_at
    }


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    nickname: str | None = Form(None),
    phone: str | None = Form(None),
    email: str | None = Form(None),
    current_password: str | None = Form(None),
    new_password: str | None = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление данных текущего пользователя"""
    print(f"\n{'='*60}")
    print(f"📝 [PUT /me] Начало обновления профиля")
    print(f"   User ID: {current_user.id_user}")
    print(f"   Текущий email: {current_user.email}")
    print(f"   Полученные данные:")
    print(f"     - nickname: {nickname}")
    print(f"     - phone: {phone}")
    print(f"     - email: {email}")
    print(f"     - current_password: {'***' if current_password else 'None'}")
    print(f"     - new_password: {'***' if new_password else 'None'}")
    
    updates = {}
    
    # Обновление никнейма
    if nickname is not None and nickname != current_user.nickname:
        print(f"\n   🔄 Проверка никнейма: '{nickname}'")
        exists = db.execute(
            text("SELECT id_user FROM users WHERE nickname = :nickname AND id_user != :id_user"),
            {"nickname": nickname, "id_user": current_user.id_user}
        ).first()
        if exists:
            print(f"   ❌ Никнейм уже занят!")
            raise HTTPException(status_code=400, detail="Никнейм уже занят")
        updates["nickname"] = nickname.strip()
        print(f"   ✅ Никнейм добавлен в обновления")
    
    # Обновление телефона
    if phone is not None:
        phone_value = phone.strip() if phone.strip() else None
        updates["phone"] = phone_value
        print(f"   🔄 Телефон: '{phone_value}'")
    
    # Обновление email (требует подтверждения паролем)
    if email is not None and email != current_user.email:
        print(f"\n   🔄 Попытка смены email с '{current_user.email}' на '{email}'")
        
        # 👇 ВАЖНО: Получаем АКТУАЛЬНЫЙ хеш пароля из БД (не из current_user!)
        password_check_query = text("SELECT password_hash FROM users WHERE id_user = :id_user")
        password_result = db.execute(password_check_query, {"id_user": current_user.id_user}).first()
        current_hash = password_result.password_hash if password_result else None
        
        print(f"   🔐 Проверка пароля...")
        print(f"     - Текущий пароль предоставлен: {'Да' if current_password else 'Нет'}")
        print(f"     - Хеш из БД: {current_hash[:30] if current_hash else 'None'}...")
        
        if not current_password or not verify_password(current_password, current_hash):
            print(f"   ❌ ОШИБКА: Неверный пароль для подтверждения смены email!")
            raise HTTPException(
                status_code=400, 
                detail="Для смены email подтвердите текущий пароль"
            )
        
        # Проверка уникальности email
        exists = db.execute(
            text("SELECT id_user FROM users WHERE email = :email AND id_user != :id_user"),
            {"email": email, "id_user": current_user.id_user}
        ).first()
        if exists:
            print(f"   ❌ Email '{email}' уже зарегистрирован!")
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
        
        updates["email"] = email.lower().strip()
        print(f"   ✅ Email добавлен в обновления: '{updates['email']}'")
    
    # Смена пароля
    if new_password:
        print(f"\n   🔄 Попытка смены пароля")
        
        # 👇 ВАЖНО: Получаем АКТУАЛЬНЫЙ хеш пароля из БД
        password_check_query = text("SELECT password_hash FROM users WHERE id_user = :id_user")
        password_result = db.execute(password_check_query, {"id_user": current_user.id_user}).first()
        current_hash = password_result.password_hash if password_result else None
        
        print(f"   🔐 Проверка текущего пароля...")
        if not current_password or not verify_password(current_password, current_hash):
            print(f"   ❌ ОШИБКА: Неверный текущий пароль!")
            raise HTTPException(
                status_code=400,
                detail="Для смены пароля подтвердите текущий пароль"
            )
        
        if len(new_password) < 6:
            print(f"   ❌ ОШИБКА: Пароль слишком короткий (менее 6 символов)")
            raise HTTPException(status_code=400, detail="Пароль должен быть не менее 6 символов")
        
        updates["password_hash"] = get_password_hash(new_password)
        print(f"   ✅ Новый пароль захеширован и добавлен в обновления")
    
    # Применяем изменения
    if updates:
        print(f"\n   💾 Применение обновлений к БД...")
        print(f"   Поля для обновления: {list(updates.keys())}")
        
        # Динамически формируем SET часть запроса
        set_parts = []
        params = {"id_user": current_user.id_user}
        
        for field, value in updates.items():
            set_parts.append(f"{field} = :{field}")
            params[field] = value
        
        query = text(f"""
            UPDATE users 
            SET {', '.join(set_parts)}
            WHERE id_user = :id_user
        """)
        
        print(f"   SQL: {query}")
        print(f"   Параметры: { {k: ('***' if 'password' in k else v) for k, v in params.items()} }")
        
        db.execute(query, params)
        db.commit()
        print(f"   ✅ Данные успешно сохранены в БД!")
        
        # Получаем обновлённые данные
        select_query = text("""
            SELECT id_user, email, nickname, phone, id_role, created_at
            FROM users WHERE id_user = :id_user
        """)
        updated_user = db.execute(select_query, {"id_user": current_user.id_user}).first()
        
        role_query = text("SELECT name_role FROM roles WHERE id_role = :id_role")
        role_result = db.execute(role_query, {"id_role": updated_user.id_role}).first()
        role_name = role_result.name_role if role_result else None
        
        print(f"\n   📤 Возврат обновлённых данных:")
        print(f"     - Email: {updated_user.email}")
        print(f"     - Nickname: {updated_user.nickname}")
        print(f"     - Phone: {updated_user.phone}")
        print(f"     - Role: {role_name}")
        print(f"✅ [PUT /me] Профиль успешно обновлён!\n{'='*60}\n")
        
        return {
            "id_user": updated_user.id_user,
            "email": updated_user.email,
            "nickname": updated_user.nickname,
            "phone": updated_user.phone,
            "id_role": updated_user.id_role,
            "role_name": role_name,
            "created_at": updated_user.created_at
        }
    
    print(f"   ⚠️ Нет изменений для сохранения")
    print(f"✅ [PUT /me] Возврат текущих данных без изменений\n{'='*60}\n")
    
    # Если ничего не меняли
    role_query = text("SELECT name_role FROM roles WHERE id_role = :id_role")
    role_result = db.execute(role_query, {"id_role": current_user.id_role}).first()
    role_name = role_result.name_role if role_result else None
    
    return {
        "id_user": current_user.id_user,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "phone": current_user.phone,
        "id_role": current_user.id_role,
        "role_name": role_name,
        "created_at": current_user.created_at
    }


# ===== ЭНДПОИНТЫ АКТИВНОСТИ =====

@router.get("/me/activity")
async def get_user_activity(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение статистики активности пользователя"""
    print(f"\n{'='*60}")
    print(f"📊 [GET /me/activity] Запрос активности пользователя ID: {current_user.id_user}")
    
    # 👇 Отзывы (id_user в таблице reviews)
    total_reviews = 0
    try:
        print(f"   🔍 Запрос к таблице reviews...")
        reviews_query = text("""
            SELECT COUNT(*) as count 
            FROM reviews 
            WHERE id_user = :user_id
        """)
        reviews_result = db.execute(reviews_query, {"user_id": current_user.id_user}).first()
        total_reviews = reviews_result.count if reviews_result else 0
        print(f"   ✅ Найдено отзывов: {total_reviews}")
    except Exception as e:
        print(f"   ❌ Ошибка при получении отзывов: {e}")
        total_reviews = 0
    
    # 👇 Избранное (id_user в таблице favorites)
    total_favorites = 0
    try:
        print(f"   🔍 Запрос к таблице favorites...")
        fav_query = text("""
            SELECT COUNT(*) as count 
            FROM favorites 
            WHERE id_user = :user_id
        """)
        fav_result = db.execute(fav_query, {"user_id": current_user.id_user}).first()
        total_favorites = fav_result.count if fav_result else 0
        print(f"   ✅ Найдено в избранном: {total_favorites}")
    except Exception as e:
        print(f"   ❌ Ошибка при получении избранного: {e}")
        total_favorites = 0
    
    # 👇 Добавленные объекты (created_by в таблице objects)
    total_objects = 0
    try:
        print(f"   🔍 Запрос к таблице objects...")
        obj_query = text("""
            SELECT COUNT(*) as count 
            FROM objects 
            WHERE created_by = :user_id
        """)
        obj_result = db.execute(obj_query, {"user_id": current_user.id_user}).first()
        total_objects = obj_result.count if obj_result else 0
        print(f"   ✅ Найдено добавленных объектов: {total_objects}")
    except Exception as e:
        print(f"   ❌ Ошибка при получении объектов: {e}")
        total_objects = 0
    
    result = {
        "total_reviews": total_reviews,
        "total_favorites": total_favorites,
        "total_objects_added": total_objects
    }
    
    print(f"   📤 Отправка результата: {result}")
    print(f"✅ [GET /me/activity] Завершено\n{'='*60}\n")
    return result


@router.get("/me/reviews")
async def get_user_reviews(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение списка отзывов пользователя"""
    print(f"\n{'='*60}")
    print(f"📝 [GET /me/reviews] Запрос отзывов пользователя ID: {current_user.id_user}")
    print(f"   Limit: {limit}, Offset: {offset}")
    
    try:
        query = text("""
            SELECT 
                r.id_review, r.text, rc.name as category_name, r.rating, r.created_at,
                o.id_object, o.name as object_name, t.name_type as object_type
            FROM reviews r
            LEFT JOIN objects o ON r.id_object = o.id_object
            LEFT JOIN type_object t ON o.id_type = t.id_type
            LEFT JOIN review_categories rc ON r.id_category_review = rc.id_category_review
            WHERE r.id_user = :user_id
            ORDER BY r.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.execute(query, {
            "user_id": current_user.id_user,
            "limit": limit,
            "offset": offset
        })
        
        reviews = [
            {
                "id_review": row.id_review,
                "text": row.text,
                "category": row.category_name,
                "rating": row.rating,
                "created_at": row.created_at,
                "object": {
                    "id_object": row.id_object,
                    "name": row.object_name,
                    "type": row.object_type
                } if row.id_object else None
            }
            for row in result.fetchall()
        ]
        
        print(f"   ✅ Найдено отзывов: {len(reviews)}")
        print(f"✅ [GET /me/reviews] Завершено\n{'='*60}\n")
        return reviews
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        print(f"✅ [GET /me/reviews] Возврат пустого списка\n{'='*60}\n")
        return []


@router.get("/me/favorites")
async def get_user_favorites(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение списка избранных объектов"""
    print(f"\n{'='*60}")
    print(f"⭐ [GET /me/favorites] Запрос избранного пользователя ID: {current_user.id_user}")
    print(f"   Limit: {limit}, Offset: {offset}")
    
    try:
        query = text("""
            SELECT 
                f.id_favorite, o.id_object, o.name, o.address,
                ST_Y(o.location::geometry) as lat, ST_X(o.location::geometry) as lon,
                t.name_type as object_type
            FROM favorites f
            INNER JOIN objects o ON f.id_object = o.id_object
            LEFT JOIN type_object t ON o.id_type = t.id_type
            WHERE f.id_user = :user_id
            ORDER BY f.id_favorite DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.execute(query, {
            "user_id": current_user.id_user,
            "limit": limit,
            "offset": offset
        })
        
        favorites = [
            {
                "id_favorite": row.id_favorite,
                "object": {
                    "id_object": row.id_object,
                    "name": row.name,
                    "address": row.address,
                    "coords": [row.lat, row.lon],
                    "type": row.object_type
                }
            }
            for row in result.fetchall()
        ]
        
        print(f"   ✅ Найдено в избранном: {len(favorites)}")
        print(f"✅ [GET /me/favorites] Завершено\n{'='*60}\n")
        return favorites
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        print(f"✅ [GET /me/favorites] Возврат пустого списка\n{'='*60}\n")
        return []


@router.get("/me/objects")
async def get_user_added_objects(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение объектов, добавленных пользователем"""
    print(f"\n{'='*60}")
    print(f"📍 [GET /me/objects] Запрос объектов пользователя ID: {current_user.id_user}")
    print(f"   Limit: {limit}, Offset: {offset}")
    
    query = text("""
        SELECT 
            o.id_object, o.name, o.address,
            ST_Y(o.location::geometry) as lat, ST_X(o.location::geometry) as lon,
            t.name_type as object_type, o.created_at
        FROM objects o
        LEFT JOIN type_object t ON o.id_type = t.id_type
        WHERE o.created_by = :user_id
        ORDER BY o.created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    
    result = db.execute(query, {
        "user_id": current_user.id_user,
        "limit": limit,
        "offset": offset
    })
    
    objects = [
        {
            "id_object": row.id_object,
            "name": row.name,
            "address": row.address,
            "coords": [row.lat, row.lon],
            "type": row.object_type,
            "created_at": row.created_at
        }
        for row in result.fetchall()
    ]
    
    print(f"   ✅ Найдено объектов: {len(objects)}")
    print(f"✅ [GET /me/objects] Завершено\n{'='*60}\n")
    return objects