from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import httpx
import os
from sqlalchemy.orm import Session
from sqlalchemy import text
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from api.database import get_db

router = APIRouter(prefix="/api/reviews", tags=["AI Summary"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
print(f"🔑 Key loaded: {bool(OPENROUTER_API_KEY)}")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

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
        raise HTTPException(
            status_code=400,
            detail="Нет отзывов для анализа"
        )

    reviews_text = "\n\n".join([
        f"Оценка: {r.rating}/5 | Категория: {r.category}\nТекст: {r.text}"
        for r in request.reviews[:30]
    ])

    system_prompt = """
        Ты работаешь в городской системе обратной связи на платформе для оценки городского благоустройства.
        Твоя задача — анализировать отзывы жителей об объектах городской среды:
        - кафе;
        - парках;
        - остановках;
        - скамейках;
        - детских площадках;
        - спортивных площадках;
        - урнах;
        - парковках;
        - памятниках;
        - пешеходных переходах;
        - и других объектах благоустройства.
        Ты создаёшь краткую сводку отзывов для обычных пользователей.
        Стиль ответа должен быть похож на сводки отзывов в:
        - Wildberries;
        - Ozon;
        - Яндекс Картах;
        - 2ГИС.

        Главная цель: помочь человеку за несколько секунд понять, что людям нравится в объекте и какие замечания встречаются чаще всего. 
        А также помочь администрации города заметить какие либо классные или проблемные объекты

        ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:
        1. Пиши только один абзац.
        2. Длина ответа: от 1 до 3 предложений.
        3. Используй простой человеческий язык.
        4. Не используй списки.
        5. Не используй маркированные пункты.
        6. Не используй слова:
        - пользователи
        - респонденты
        - анализ
        - статистика
        - выявлено
        - рейтинг
        - оценка
        - исследование
        - данные показывают
        - объект имеет
        - достоинства
        - недостатки
        - преимущество
        - проблема выявлена
        7. Не упоминай количество отзывов.
        8. Не упоминай оценки 1/5, 5/5 и т.д.
        9. Не пересказывай каждый отзыв отдельно.
        10. Найди наиболее часто встречающиеся мнения.
        11. Если большинство отзывов положительные — сначала расскажи о сильных сторонах.
        12. Если есть жалобы — мягко упомяни их во второй части текста.
        13. Если есть предложения по улучшению — встрой их в текст естественным образом.
        14. Не делай выводов, которых нет в отзывах.
        15. Не выдумывай факты.
        16. Не используй канцелярский стиль.
        17. Не используй фразы: "следует отметить", "вместе с тем", "в ходе анализа", "можно сделать вывод", "основной недостаток", "основное преимущество".
        18. Пиши так, будто кратко пересказываешь мнение жителей.

        ПРИМЕР ХОРОШЕГО ОТВЕТА: "Многие отмечают чистоту территории и удобное расположение площадки. Иногда встречаются замечания по поводу недостаточного освещения и необходимости обновления отдельных элементов."
        Ещё пример: "Кафе ценят за уютную атмосферу и вежливое обслуживание, однако в отдельных отзывах упоминается длительное ожидание заказа в часы пик."
        Ещё пример: "Остановку считают удобной и хорошо расположенной, хотя некоторые отмечают необходимость более регулярной уборки и обновления навеса."
        Верни только готовую сводку.
        """

    user_prompt = f"""
    Отзывы об объекте:

    {reviews_text}

    Составь краткую сводку.
    """

    model_name = "qwen/qwen3-32b"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

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
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 120
                }
            )

            if response.status_code != 200:
                print(response.text)
                raise HTTPException(
                    status_code=500,
                    detail="Ошибка AI сервиса"
                )

            data = response.json()

            summary = (
                data["choices"][0]["message"]["content"]
                .strip()
                .replace('"', '')
            )

            return AISummaryResponse(
                summary=summary,
                model=model_name
            )

    except Exception as e:
        print("AI summary error:", e)

        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации сводки: {str(e)}"
        )