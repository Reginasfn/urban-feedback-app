# utils/auth.py

"""
Утилиты для авторизации: хеширование паролей и JWT
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.database import get_db
from api.models.user import User

# 🔐 НАСТРОЙКИ
SECRET_KEY = "your-super-secret-key-change-in-production-please"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# 🔑 Хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔗 OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли пароль с хешем"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширует пароль через bcrypt"""
    # 👇 ОБЯЗАТЕЛЬНО обрезаем до 72 байт!
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создаёт JWT-токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Зависимость для получения текущего пользователя из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учётные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    query = text("SELECT * FROM users WHERE id_user = :user_id")
    user = db.execute(query, {"user_id": user_id}).first()
    
    if user is None:
        raise credentials_exception
    
    user_obj = User(
        id_user=user.id_user,
        email=user.email,
        password_hash=user.password_hash,
        nickname=user.nickname,
        phone=user.phone,
        id_role=user.id_role,
        created_at=user.created_at
    )
    
    return user_obj


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Доп. проверка: пользователь должен существовать"""
    return current_user