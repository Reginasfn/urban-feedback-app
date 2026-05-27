# backend/api/services/moderation.py
import re
from detoxify import Detoxify

class TextModerator:
    RUSSIAN_BAD_WORDS = {
        'бля', 'блядь', 'блять', 'ебать', 'еблан', 'ебуч', 'ху', 'хуй', 'хуё', 'пизд', 'мудак', 'мудак',
        'сука', 'суки', 'тварь', 'говно', 'дерьмо', 'ублюдок', 'заеб', 'наху', 'нахер', 'пошел', 'иди',
        'бл*', 'х*', 'пиз*', 'еб*', 'заеб', 'нах', 'сука', 'суч',
        'долбо', 'кретин', 'идиот', 'дебил', 'туп', 'недоум',
    }
    
    # Паттерны для обхода фильтра (замена букв цифрами/символами)
    OBFUSCATION_PATTERNS = [
        r'[аа@4][хx][уy][\*\.\!\?\~]?[йя]?', 
        r'[п][и1][з3][д][ао\*\.\!\?]?[ао]?', 
        r'[б][л][я][д][ь\*\.\!\?]?[юя]?',    
        r'[е][б][ао][т][ь\*\.\!\?]?[ся]?',   
        r'[х][у][\*\.\!\?]?[её][б][ао]?[т]?', 
        r'(.)\1{3,}',                         
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
        
        self.thresholds = {
            'toxicity': 0.5,         
            'severe_toxicity': 0.3,   
            'obscene': 0.4,      
            'threat': 0.3,          
            'insult': 0.4,          
            'identity_attack': 0.3    
        }
    
    def _normalize_text(self, text: str) -> str:
        """Нормализация текста: убираем лишние символы, приводим к нижнему регистру"""
        text = re.sub(r'[\*\.\!\?\~\-\_]+', '', text)
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
        
        for word in self.RUSSIAN_BAD_WORDS:
            if word in normalized:
                return True
        
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
        
        if not text or len(text.strip()) < min_length:
            result['is_approved'] = False
            result['reasons'].append(f'Текст слишком короткий (мин. {min_length} символов)')
            return result
        
        if self._check_profanity_list(text):
            result['is_approved'] = False
            result['reasons'].append('Содержит недопустимую лексику')
            return result
        
        spam_patterns = [
            r'(.)\1{4,}',           
            r'[А-Я]{15,}',         
            r'(http|www\.)',      
            r'[\d]{10,}',          
            r'[\u200b-\u200f]',  
        ]
        for pattern in spam_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                result['is_approved'] = False
                result['reasons'].append('Обнаружены признаки спама')
                break
        
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
            result['scores'] = {'error': str(e)}
        
        return result

moderator = TextModerator()