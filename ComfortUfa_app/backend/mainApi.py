from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import engine, Base, get_db  # 👈 Импортируем Base и engine
from api.endpoints import objects, stats, auth, users

app = FastAPI(
    title="ComfortUfa API",
    description="## API для платформы оценки благоустройства города Уфы",
    version="1.0.0",
    docs_url="/docs",
)

# 🔐 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Роутеры
app.include_router(objects.router)
app.include_router(stats.router)
app.include_router(auth.router)
app.include_router(users.router)

@app.on_event("startup")
async def startup_event():
    # Создаём таблицы, если их нет
    Base.metadata.create_all(bind=engine)
    print("🔌 Подключение к БД: db_citycare@localhost:5432")

@app.get("/")
async def root():
    return {"message": "ComfortUfa API is running!"}