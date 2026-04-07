from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ComfortUfa API",
    description="API для оценки благоустройства Уфы",
    version="1.0.0"
)

# Разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ComfortUfa API работает! 🎉"}

@app.get("/api/feedback")
async def get_feedback():
    return {"feedbacks": []}

@app.post("/api/feedback")
async def create_feedback():
    return {"message": "Отзыв создан"}