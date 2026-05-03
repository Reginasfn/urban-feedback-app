# auth.py

"""
Эндпоинты для регистрации и входа (под твою БД)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta

from api.database import get_db
from api.models.user import User, Role
from api.schemas import UserCreate, UserLogin, Token, UserResponse
from api.utils.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
    get_current_active_user
)

router = APIRouter(prefix="/api/auth", tags=["Авторизация"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    
    # 🔍 Проверяем email
    existing_email = db.execute(
        text("SELECT id_user FROM users WHERE email = :email"),
        {"email": user_data.email}
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # 🔍 Проверяем nickname
    existing_nickname = db.execute(
        text("SELECT id_user FROM users WHERE nickname = :nickname"),
        {"nickname": user_data.nickname}
    ).first()
    if existing_nickname:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    
    # 🔐 Хешируем пароль
    hashed_password = get_password_hash(user_data.password)
    
    # 👤 Роль по умолчанию = 1 (пользователь)
    id_role = 2
    
    # 💾 Создаём пользователя
    query = text("""
        INSERT INTO users (email, nickname, phone, password_hash, id_role)
        VALUES (:email, :nickname, :phone, :password_hash, :id_role)
        RETURNING id_user, email, nickname, phone, id_role, created_at
    """)
    
    result = db.execute(
        query,
        {
            "email": user_data.email,
            "nickname": user_data.nickname,
            "phone": user_data.phone,
            "password_hash": hashed_password,
            "id_role": id_role
        }
    )
    db.commit()
    new_user = result.first()
    
    # Получаем название роли
    role_query = text("SELECT name_role FROM roles WHERE id_role = :id_role")
    role_result = db.execute(role_query, {"id_role": id_role}).first()
    role_name = role_result.name_role if role_result else None
    
    return {
        "id_user": new_user.id_user,
        "email": new_user.email,
        "nickname": new_user.nickname,
        "phone": new_user.phone,
        "id_role": new_user.id_role,
        "role_name": role_name,
        "created_at": new_user.created_at
    }


@router.post("/login", response_model=Token)
async def login(form_data: UserLogin, db: Session = Depends(get_db)):
    """Вход пользователя и получение токена"""
    
    # 🔍 Ищем пользователя по email + получаем роль
    query = text("""
        SELECT u.id_user, u.email, u.nickname, u.password_hash, u.id_role, r.name_role
        FROM users u
        LEFT JOIN roles r ON u.id_role = r.id_role
        WHERE u.email = :email
    """)
    user = db.execute(query, {"email": form_data.email}).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 🎫 Создаём JWT-токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id_user)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id_user,
        "nickname": user.nickname,
        "role": user.name_role
    }


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user),  # 👈 Теперь работает!
    db: Session = Depends(get_db)
):
    """Получение информации о текущем пользователе (защищённый маршрут)"""
    
    # Получаем название роли
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