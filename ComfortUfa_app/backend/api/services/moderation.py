# backend/api/services/moderation.py
import re
from detoxify import Detoxify

class TextModerator:
    # 🔥 Базовый список русских запрещённых слов (можно расширять)
    RUSSIAN_BAD_WORDS = {
        # Основные маты
        'бля', 'блядь', 'блять', 'ебать', 'еблан', 'ебуч', 'ху', 'хуй', 'хуё', 'пизд', 'мудак', 'мудак',
        'сука', 'суки', 'тварь', 'говно', 'дерьмо', 'ублюдок', 'заеб', 'наху', 'нахер', 'пошел', 'иди',
        # Заглушки и эвфемизмы
        'бл*', 'х*', 'пиз*', 'еб*', 'заеб', 'нах', 'сука', 'суч',
        # Оскорбления
        'долбо', 'кретин', 'идиот', 'дебил', 'туп', 'недоум',
    }
    
    # Паттерны для обхода фильтра (замена букв цифрами/символами)
    OBFUSCATION_PATTERNS = [
        r'[аа@4][хx][уy][\*\.\!\?\~]?[йя]?',  # хуй, х@й, х4й
        r'[п][и1][з3][д][ао\*\.\!\?]?[ао]?',  # пизда, п1зда, п3зда
        r'[б][л][я][д][ь\*\.\!\?]?[юя]?',     # блядь, бля*, бля.
        r'[е][б][ао][т][ь\*\.\!\?]?[ся]?',    # ебать, еб@ть
        r'[х][у][\*\.\!\?]?[её][б][ао]?[т]?', # хуёб, ху*б
        r'(.)\1{3,}',                          # повторы: аааа, бббб
    ]
    
    def __init__(self):
        print("[Moderation] Loading Detoxify model...")
        try:
            # Используем multilingual модель
            self.model = Detoxify('multilingual', device='cpu')
            print("[Moderation] ✓ Model loaded")
        except Exception as e:
            print(f"[Moderation] ✗ Failed to load model: {e}")
            raise
        
        # 🔥 Более строгие пороги для русского контента
        self.thresholds = {
            'toxicity': 0.5,          # было 0.7
            'severe_toxicity': 0.3,   # было 0.5
            'obscene': 0.4,           # было 0.6
            'threat': 0.3,            # было 0.5
            'insult': 0.4,            # было 0.6
            'identity_attack': 0.3    # было 0.5
        }
    
    def _normalize_text(self, text: str) -> str:
        """Нормализация текста: убираем лишние символы, приводим к нижнему регистру"""
        # Убираем лишние пробелы, символы
        text = re.sub(r'[\*\.\!\?\~\-\_]+', '', text)
        # Заменяем похожие символы на буквы (обход фильтра)
        replacements = {
            '0': 'о', '1': 'и', '3': 'з', '4': 'а', '5': 'с', '6': 'б', '7': 'т', '8': 'в', '9': 'д',
            '@': 'а', '$': 'с', '!': 'и', '?': 'з',
        }
        for char, repl in replacements.items():
            text = text.replace(char, repl)
        return text.lower().strip()
    
    def _check_profanity_list(self, text: str) -> bool:
        """Проверка по списку запрещённых слов"""
        normalized = self._normalize_text(text)
        
        # Прямое совпадение
        for word in self.RUSSIAN_BAD_WORDS:
            if word in normalized:
                return True
        
        # Проверка паттернов обхода
        for pattern in self.OBFUSCATION_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                return True
        
        return False
    
    def check_text(self, text: str, min_length: int = 5) -> dict:
        """
        Проверка текста на токсичность и спам
        Возвращает: {is_approved: bool, reasons: list, scores: dict}
        """
        result = {
            'is_approved': True,
            'reasons': [],
            'scores': {}
        }
        
        # Базовые валидации
        if not text or len(text.strip()) < min_length:
            result['is_approved'] = False
            result['reasons'].append(f'Текст слишком короткий (мин. {min_length} символов)')
            return result
        
        # 🔥 1. Проверка по списку матов (быстрая, до AI)
        if self._check_profanity_list(text):
            result['is_approved'] = False
            result['reasons'].append('Содержит недопустимую лексику')
            return result
        
        # 🔥 2. Проверка на спам-паттерны
        spam_patterns = [
            r'(.)\1{4,}',           # Повторы: ааааа
            r'[А-Я]{15,}',          # Длинный капслок
            r'(http|www\.)',        # Ссылки
            r'[\d]{10,}',           # Длинные числа
            r'[\u200b-\u200f]',     # Невидимые символы
        ]
        for pattern in spam_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                result['is_approved'] = False
                result['reasons'].append('Обнаружены признаки спама')
                break
        
        # 🔥 3. AI-анализ через Detoxify
        try:
            scores = self.model.predict(text)
            result['scores'] = scores
            
            for category, threshold in self.thresholds.items():
                if scores.get(category, 0) > threshold:
                    result['is_approved'] = False
                    reason_map = {
                        'toxicity': 'Токсичный контент',
                        'severe_toxicity': 'Очень токсичный контент',
                        'obscene': 'Нецензурная лексика',
                        'threat': 'Угрозы',
                        'insult': 'Оскорбления',
                        'identity_attack': 'Дискриминация'
                    }
                    result['reasons'].append(reason_map.get(category, f'Высокий уровень {category}'))
                    
        except Exception as e:
            print(f'[Moderation] Model error: {e}')
            # При ошибке модели НЕ блокируем, но логируем
            result['scores'] = {'error': str(e)}
        
        return result

# Глобальный инстанс
moderator = TextModerator()