from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import httpx
import os
import random
import hashlib
from sqlalchemy.orm import Session
from pathlib import Path
from dotenv import load_dotenv
from collections import OrderedDict

from api.database import get_db

router = APIRouter(
    prefix="/api/reviews",
    tags=["AI Summary"]
)

# Путь к корню проекта для загрузки переменных окружения
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
# Логируем загрузку ключа для отладки при старте
if OPENROUTER_API_KEY:
    print("API key loaded successfully")
else:
    print("WARNING: OPENROUTER_API_KEY not found in .env")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Список моделей для перебора (основная -> резервные)
# Важно: проверять актуальные названия в документации OpenRouter
MODELS = [
    "google/gemini-2.0-flash-lite-001",
    "qwen/qwen-2.5-72b-instruct",
    "meta-llama/llama-3.1-8b-instruct:free"
]

# Простой in-memory кэш с LRU-вытеснением
SUMMARY_CACHE = OrderedDict()
MAX_CACHE_SIZE = 500  # Лимит записей, чтобы не забивать память


# --- Схемы данных ---

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


# --- Эндпоинт генерации сводки ---

@router.post("/ai-summary", response_model=AISummaryResponse)
async def generate_ai_summary(
    request: AISummaryRequest,
    db: Session = Depends(get_db)
):
    """
    Генерирует краткую сводку отзывов с использованием внешних AI-моделей.
    Реализует кэширование, случайную выборку и fallback-логику.
    """
    
    if not request.reviews:
        raise HTTPException(
            status_code=400,
            detail="Нет отзывов для анализа"
        )

    # 1. Случайная выборка отзывов (максимум 20), чтобы не перегружать контекст
    if len(request.reviews) > 20:
        selected_reviews = random.sample(request.reviews, 20)
    else:
        selected_reviews = request.reviews

    # 2. Формирование ключа кэша
    # Сортируем отзывы перед хешированием, чтобы порядок не влиял на ключ
    sorted_reviews = sorted(
        selected_reviews,
        key=lambda r: (r.text, r.rating, r.category)
    )
    
    reviews_signature = "".join(
        f"{r.text}{r.rating}{r.category}" for r in sorted_reviews
    )
    reviews_hash = hashlib.md5(reviews_signature.encode("utf-8")).hexdigest()
    cache_key = f"{request.object_id}_{reviews_hash}"

    # 3. Проверка кэша (LRU logic)
    if cache_key in SUMMARY_CACHE:
        SUMMARY_CACHE.move_to_end(cache_key)  # Помечаем как недавно использованный
        print(f"Cache hit for object {request.object_id}")
        return AISummaryResponse(
            summary=SUMMARY_CACHE[cache_key]["summary"],
            model=SUMMARY_CACHE[cache_key]["model"]
        )

    # 4. Подготовка промпта
    reviews_text = "\n\n".join([
        f"Оценка: {r.rating}/5 | Категория: {r.category}\nТекст: {r.text}"
        for r in selected_reviews
    ])

    system_prompt = """
Ты работаешь в городской системе обратной связи на платформе для оценки городского благоустройства.

Твоя задача — анализировать отзывы жителей об объектах городской среды:
кафе, парках, остановках, скамейках, детских площадках,
спортивных площадках, урнах, парковках, памятниках,
пешеходных переходах и других объектах благоустройства.

Ты создаёшь краткую сводку отзывов для пользователей.

Стиль ответа должен быть похож на сводки отзывов в:
Wildberries, Ozon, Яндекс Картах и 2ГИС.

ПРАВИЛА:

1. Один абзац.
2. От 1 до 3 предложений.
3. Простой человеческий язык.
4. Без списков.
5. Без перечислений.
6. Не упоминай количество отзывов.
7. Не упоминай оценки.
8. Не пересказывай каждый отзыв отдельно.
9. Выделяй самые частые мнения.
10. Сначала сильные стороны.
11. Затем замечания и предложения.
12. Не выдумывай факты.
13. Не используй канцелярский стиль.
14. Верни только итоговую сводку.

Пример:

Многие отмечают чистоту территории и удобное расположение площадки. Иногда встречаются замечания по поводу недостаточного освещения и необходимости обновления отдельных элементов.
"""

    user_prompt = f"Отзывы об объекте:\n\n{reviews_text}\n\nСоставь сводку:"

    last_error = None

    # 5. Перебор моделей (fallback-цепочка)
    for model_name in MODELS:
        print(f"Trying model: {model_name}")
        
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                response = await client.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:5173",
                        "X-Title": "ComfortUfa App"
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 70
                    }
                )

                # Обработка перегрузки (429) - пробуем следующую модель
                if response.status_code == 429:
                    print(f"Rate limit (429) for {model_name}, skipping...")
                    continue

                if response.status_code != 200:
                    print(f"Error {response.status_code} from {model_name}")
                    last_error = f"{model_name}: {response.status_code}"
                    continue

                # Парсинг ответа
                try:
                    data = response.json()
                    summary = data.get("choices", [{}])[0].get("message", {}).get("content")
                except Exception:
                    print(f"Failed to parse JSON from {model_name}")
                    continue

                # Валидация контента
                if not summary or len(summary.strip()) < 10:
                    print(f"Empty or too short response from {model_name}")
                    continue

                summary = summary.strip().replace('"', "")

                # 6. Сохранение в кэш
                if cache_key in SUMMARY_CACHE:
                    SUMMARY_CACHE.move_to_end(cache_key)
                SUMMARY_CACHE[cache_key] = {
                    "summary": summary,
                    "model": model_name
                }

                # Очистка старых записей при переполнении (LRU)
                if len(SUMMARY_CACHE) > MAX_CACHE_SIZE:
                    SUMMARY_CACHE.popitem(last=False)

                print(f"Success with {model_name}")
                return AISummaryResponse(summary=summary, model=model_name)

        except Exception as e:
            print(f"Exception in {model_name}: {e}")
            last_error = str(e)
            continue

    # 7. Если все модели не сработали — возвращаем безопасный ответ
    print(f"All models failed. Last error: {last_error}")
    return AISummaryResponse(
        summary="Анализ отзывов временно недоступен. Попробуйте обновить страницу.",
        model="fallback"
    )