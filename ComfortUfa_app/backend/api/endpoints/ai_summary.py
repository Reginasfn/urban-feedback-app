from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import httpx
import os
from sqlalchemy.orm import Session
from sqlalchemy import text
import requests
import json
from dotenv import load_dotenv

from api.database import get_db

router = APIRouter(prefix="/api/reviews", tags=["AI Summary"])

# 🔥 Твой API ключ OpenRouter (добавь в .env!)
OPENROUTER_API_KEY = ""
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

print("KEY =", OPENROUTER_API_KEY)
print("AUTH =", f"Bearer {OPENROUTER_API_KEY}")

class ReviewData(BaseModel):
    text: str
    rating: int
    category: str

class AISummaryRequest(BaseModel):
    object_id: int
    reviews: List[ReviewData]

class AISummaryResponse(BaseModel):
    summary: str
    model: str

@router.post("/ai-summary", response_model=AISummaryResponse)
async def generate_ai_summary(
    request: AISummaryRequest,
    db: Session = Depends(get_db)
):
    """Генерация AI-сводки отзывов"""
    
    if not request.reviews:
        raise HTTPException(status_code=400, detail="Нет отзывов для анализа")
    
    # Формируем промпт
    reviews_text = "\n\n".join([
        f"⭐ {r.rating}/5 | Категория: {r.category}\n{r.text}"
        for r in request.reviews[:20]  # Берём максимум 20 отзывов
    ])
    
    prompt = f"""Проанализируй все отзывы об объекте и составь краткую сводку (2-3 предложения) на русском языке. 
                Выдели основные преимущества и недостатки, которые упоминают пользователи.

Отзывы:
{reviews_text}

Сводка:"""

    # Выбираем модель
    model_name = "qwen/qwen3-32b"


    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:5173",  # Твой фронтенд
                    "X-Title": "ComfortUfa App"
                },
                json={
                    "model": model_name,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 200,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                print(f"OpenRouter error: {response.text}")
                raise HTTPException(status_code=500, detail="Ошибка AI сервиса")
            
            data = response.json()
            summary = data["choices"][0]["message"]["content"].strip()
            
            return AISummaryResponse(
                summary=summary,
                model=model_name
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Превышено время ожидания AI")
    except Exception as e:
        print(f"AI summary error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации сводки: {str(e)}")