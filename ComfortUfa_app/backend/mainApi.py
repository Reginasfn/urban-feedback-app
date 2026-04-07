from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import objects  # Импортируем роутер объектов

# 🎯 Создаём приложение FastAPI
app = FastAPI(
    title="ComfortUfa API",
    description="""
    ## API для платформы оценки благоустройства города Уфы
    
    ### Функционал:
    - 🗺️ **Объекты**: получение объектов благоустройства с координатами
    - 📝 **Отзывы**: создание и просмотр отзывов жителей
    - 👤 **Пользователи**: регистрация и авторизация
    - 📊 **Статистика**: аналитика по состоянию городской среды
    """,
    version="1.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc (альтернативная документация)
    openapi_url="/openapi.json"
)

# 🔐 CORS — разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite (разработка)
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # Если будешь использовать другой порт
    ],
    allow_credentials=True,   # Разрешаем отправку cookies и токенов
    allow_methods=["*"],      # Разрешаем все HTTP-методы (GET, POST, PUT, DELETE)
    allow_headers=["*"],      # Разрешаем все заголовки
)

# 📦 Подключаем роутеры (эндпоинты)
app.include_router(objects.router)

# 🏠 Root endpoint — проверка работоспособности
@app.get("/", tags=["Главная"])
async def root():
    """
    Корневой эндпоинт. Показывает базовую информацию об API.
    """
    return {
        "message": "🎉 ComfortUfa API работает!",
        "version": "1.0.0",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "objects_list": "/api/objects?type=Фонарь&limit=100",
            "object_types": "/api/objects/types",
            "object_by_id": "/api/objects/{id}"
        }
    }

# 🩺 Health check — для мониторинга работоспособности
@app.get("/api/health", tags=["Системные"])
async def health_check():
    """
    Проверка состояния API.
    Используется для мониторинга и readiness/liveness probes.
    """
    return {
        "status": "ok",
        "service": "comfortufa-api",
        "timestamp": "2024-01-01T00:00:00Z"  # Здесь можно добавить реальное время
    }

#  Запуск: uvicorn mainApi:app --reload