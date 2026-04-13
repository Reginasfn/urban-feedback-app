# database.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path
from dotenv import load_dotenv

# 🔍 Ищем .env файл
# Сначала пробуем загрузить из текущей директории, потом из родительской
env_path = Path('.') / '.env'
if not env_path.exists():
    env_path = Path('..') / '.env'

# Загружаем переменные окружения
load_dotenv(dotenv_path=env_path, override=True)

# 📋 Читаем настройки БД с дефолтными значениями
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "27022006")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "db_citycare")  # Твоя база данных

# 🔗 Формируем URL подключения к PostgreSQL
DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASS}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"🔌 Подключение к БД: {DB_NAME}@{DB_HOST}:{DB_PORT}")

# 🚀 Создаём движок SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Поставь True, чтобы видеть SQL-запросы в консоли (для отладки)
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_size=5,  # Размер пула соединений
    max_overflow=10  # Максимум дополнительных соединений
)

# 🏭 Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,  # Не сохраняем автоматически — контролируем сами
    autoflush=False,   # Не очищаем автоматически
    bind=engine
)

# 📐 Базовый класс для моделей
Base = declarative_base()

# 🔄 Зависимость для получения сессии БД (используется в эндпоинтах)
def get_db():
    """
    Генератор сессии БД.
    Создаёт новую сессию для каждого запроса и гарантирует её закрытие.
    """
    db = SessionLocal()
    try:
        yield db  # Отдаём сессию в эндпоинт
    except Exception:
        db.rollback()  # Отменяем все изменения при ошибке
        raise
    finally:
        db.close()  # Обязательно закрываем сессию

def get_db_connection():
    """
    Возвращает raw psycopg2 connection для прямых SQL-запросов.
    """
    import psycopg2
    from dotenv import load_dotenv
    import os
    
    # Читаем настройки (если .env ещё не загружен)
    load_dotenv()
    
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "db_citycare"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "27022006")
    )
    return conn