from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class ObjectResponse(BaseModel):
    """
    Схема ответа для объекта благоустройства.
    Соответствует структуре таблицы public.objects
    """
    id_object: int  # Первичный ключ
    name: str = Field(..., min_length=1, max_length=200)  # Название объекта
    id_type: int  # ID типа объекта (внешний ключ на таблицу types)
    address: Optional[str] = Field(None, max_length=300)  # Адрес
    coords: List[float] = Field(..., min_length=2, max_length=2)  # [широта, долгота]
    id_status: Optional[int] = None  # ID статуса
    created_by: Optional[int] = None  # Кто создал
    created_at: Optional[datetime] = None  # Дата создания
    osm_id: Optional[int] = None  # ID из OpenStreetMap (если есть)
    
    # 🔍 Валидация координат
    @field_validator('coords')
    @classmethod
    def validate_coords(cls, v):
        """Проверка: координаты должны быть в допустимых диапазонах"""
        if len(v) != 2:
            raise ValueError('coords должен содержать ровно 2 значения [lat, lon]')
        lat, lon = v
        if not (-90 <= lat <= 90):
            raise ValueError(f'Широта {lat} вне диапазона [-90, 90]')
        if not (-180 <= lon <= 180):
            raise ValueError(f'Долгота {lon} вне диапазона [-180, 180]')
        return v
    
    class Config:
        from_attributes = True  # Разрешаем создание из SQLAlchemy моделей
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
    Использует JOIN с таблицей types.
    """
    id_object: int
    name: str
    type_name: str  # Название типа (например, "Фонарь")
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