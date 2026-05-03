from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import engine, Base, get_db 
from api.endpoints import objects, stats, auth, users, reviews
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="ComfortUfa API",
    description="## API для платформы оценки благоустройства города Уфы",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Твой фронтенд
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(objects.router)
app.include_router(stats.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(reviews.router)

app.mount("/resources", StaticFiles(directory="resources"), name="resources")

@app.on_event("startup")
async def startup_event():
    # Создаём таблицы, если их нет
    Base.metadata.create_all(bind=engine)
    print("🔌 Подключение к БД: db_citycare@localhost:5432")

@app.get("/")
async def root():
    return {"message": "ComfortUfa API is running!"}