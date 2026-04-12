# schemas.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class ObjectResponse(BaseModel):
    """
    Схема ответа для объекта благоустройства.
    Соответствует структуре таблицы public.objects
    """
    id_object: int
    name: str = Field(..., min_length=1, max_length=200)
    id_type: int
    address: Optional[str] = Field(None, max_length=300)
    coords: List[float] = Field(..., min_length=2, max_length=2)
    id_status: Optional[int] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    osm_id: Optional[int] = None
    
    @field_validator('coords')
    @classmethod
    def validate_coords(cls, v):
        if len(v) != 2:
            raise ValueError('coords должен содержать ровно 2 значения [lat, lon]')
        lat, lon = v
        if not (-90 <= lat <= 90):
            raise ValueError(f'Широта {lat} вне диапазона [-90, 90]')
        if not (-180 <= lon <= 180):
            raise ValueError(f'Долгота {lon} вне диапазона [-180, 180]')
        return v
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_object": 1,
                "name": "Фонарь уличного освещения",
                "id_type": 3,
                "address": "ул. Ленина, 15",
                "coords": [54.7401, 55.9735],
                "id_status": 1,
                "created_by": 42,
                "created_at": "2024-01-15T10:30:00",
                "osm_id": 123456789
            }
        }

class ObjectWithTypeName(BaseModel):
    """
    Расширенная схема с названием типа (для фронтенда).
    """
    id_object: int
    name: str
    type_name: str
    address: Optional[str]
    coords: List[float]
    id_status: Optional[int]
    created_at: Optional[datetime]
    
    @field_validator('coords')
    @classmethod
    def validate_coords(cls, v):
        if len(v) != 2:
            raise ValueError('coords must have exactly 2 values')
        return v
    
    class Config:
        from_attributes = True

# ===== СХЕМА ДЛЯ СТАТИСТИКИ =====
class PlatformStats(BaseModel):
    total_objects: int = Field(..., description="Общее количество объектов на карте")
    total_problems: int = Field(..., description="Количество отзывов с категорией 'Проблема'")
    total_users: int = Field(..., description="Общее количество зарегистрированных пользователей")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_objects": 1234,
                "total_problems": 856,
                "total_users": 3421
            }
        }

# ===== СХЕМЫ ДЛЯ АВТОРИЗАЦИИ =====

class UserCreate(BaseModel):
    """Схема для регистрации нового пользователя"""
    email: str = Field(..., min_length=5, max_length=255, example="user@example.com")
    nickname: str = Field(..., min_length=3, max_length=100, example="ivan_ufa")
    phone: Optional[str] = Field(None, max_length=20, example="+79991234567")
    password: str = Field(..., min_length=6, max_length=72, example="SecurePass123")
    id_role: Optional[int] = Field(None, description="ID роли (по умолчанию 1 - пользователь)")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('Некорректный email')
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Пароль не должен превышать 72 символа')
        return v

class UserLogin(BaseModel):
    """Схема для входа"""
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="SecurePass123")

class Token(BaseModel):
    """Ответ с токеном после успешного входа"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    nickname: str
    role: Optional[str] = None

class UserResponse(BaseModel):
    """Информация о текущем пользователе"""
    id_user: int
    email: str
    nickname: str
    phone: Optional[str] = None
    id_role: Optional[int] = None
    role_name: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True