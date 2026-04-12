# mainApi.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import objects, stats, auth  # Импортируем роутер объектов

# 🎯 Создаём приложение FastAPI
app = FastAPI(
    title="ComfortUfa API",
    description="""
    ## API для платформы оценки благоустройства города Уфы""",
    version="1.0.0",
    docs_url="/docs",
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
app.include_router(stats.router)
app.include_router(auth.router)

@app.get("/", tags=["Главная"])
async def root():
    return {"message": "🎉 ComfortUfa API работает!"}

#  Запуск: uvicorn mainApi:app --reload