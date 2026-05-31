# mainApi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.database import engine, Base, get_db 
from api.endpoints import objects, stats, auth, users, reviews, recommendations, ai_summary
from fastapi.staticfiles import StaticFiles
import logging

app = FastAPI(
    title="ComfortUfa API",
    description="## API для платформы оценки благоустройства города Уфы",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(objects.router)
app.include_router(stats.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(reviews.router)
app.include_router(recommendations.router)
app.include_router(ai_summary.router)

app.mount("/resources", StaticFiles(directory="resources"), name="resources")

@app.on_event("startup")
async def startup_event():
    print("- MAIN API LOADED")
    Base.metadata.create_all(bind=engine)
    print("Подключение к БД: db_citycare@localhost:5432")
    logging.basicConfig(level=logging.DEBUG)

@app.get("/")
async def root():
    return {"message": "ComfortUfa API is running!"}