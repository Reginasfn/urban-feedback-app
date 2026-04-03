import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
import time
import json

#-----общие настройки-----
load_dotenv()
CREATED_BY = 1

TARGET_TYPE = "surveillance"

#-----подключение к бдшке-----
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

# словарь для названия на русском в бд
DICT_NAMES = {
    "playground": "Детская площадка",
    "park": "Парк",
    "cafe": "Кафе",
    "bench": "Скамейка",
    "parking": "Парковка",
    "bus_stop": "Остановка",
    "street_lamp": "Фонарь",
    "traffic_signals": "Светофор",
    "surveillance": "Камера видеонаблюдения",
    "crossing": "Пешеходный переход",
    "monument": "Памятник",
    "shelter": "Беседка",
    "toilet": "Туалет"
}

# словарь с ключами для ОСМ
OSM_KEYS = {
    # для досуга
    "playground": "leisure",
    "park": "leisure",
    "garden": "leisure",
    
    # благоустройство
    "cafe": "amenity",
    "bench": "amenity",
    "parking": "amenity",
    "shelter": "amenity",
    "toilet": "amenity",
    
    # дорога=*
    "bus_stop": "highway",
    "crossing": "highway",
    
    # искусственные сооружения
    "street_lamp": "man_made",
    "surveillance": "man_made",
    
    # историческое
    "monument": "historic",
}

# НАСТРОЙКИ 
# границы города УФА (min_lat, min_lon, max_lat, max_lon)
CITY_BBOX = (54.68, 55.90, 55.02, 56.12)

# размер квадрата для разбиения (в градусах)
STEP = 0.05
MIN_STEP = 0.02 # минимальный размер квадрата

# запросы к разным серверам Overpass API
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

# паузы между запросами (чтоб не забанили)
REQUEST_TIMEOUT = 300 
SLEEP_BETWEEN_REQUESTS = 45
MAX_RETRIES = 3  # попытки на каждый сервак

# файл для отслеживания обработанных квадратов
PROCESSED_FILE = "processed_bboxes.txt"

processed_bboxes = set()

# ФУНКЦИИ
def load_processed_bboxes():
    """Загрузка множества уже обработанных bbox из файла"""
    processed = set()
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        bbox = tuple(map(float, line.split(",")))
                        processed.add(bbox)
                    except ValueError:
                        continue  # пропускаем битые строки
    return processed

# функции
def save_processed_bbox(bbox):
    """Сохранение обработанного bbox в файл"""
    with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
        f.write(",".join(map(str, bbox)) + "\n")
    processed_bboxes.add(bbox)

def fetch_from_servers(query, max_retries=MAX_RETRIES):
    """Отправка запроса к Overpass API с перебором серверов и повторами"""
    for attempt in range(max_retries):
        for url in OVERPASS_SERVERS:
            try:
                response = requests.post(url, data=query, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                print(f"Таймаут на {url} (попытка {attempt+1}/{max_retries})")
            except requests.exceptions.RequestException as e:
                print(f"Ошибка на {url}: {e} (попытка {attempt+1}/{max_retries})")
            time.sleep(SLEEP_BETWEEN_REQUESTS)
    return None

def generate_bboxes(bbox, step):
    """Генерация сетки квадратов для покрытия области bbox"""
    min_lat, min_lon, max_lat, max_lon = bbox
    lat = min_lat
    while lat < max_lat:
        lon = min_lon
        while lon < max_lon:
            yield (lat, lon, min(lat+step, max_lat), min(lon+step, max_lon))
            lon += step
        lat += step

def get_osm_query(min_lat, min_lon, max_lat, max_lon, osm_key, osm_value):
    """Формирование запроса для параметров"""
    return f"""
        [out:json][timeout:60];
        (
        node["{osm_key}"="{osm_value}"]({min_lat},{min_lon},{max_lat},{max_lon});
        way["{osm_key}"="{osm_value}"]({min_lat},{min_lon},{max_lat},{max_lon});
        relation["{osm_key}"="{osm_value}"]({min_lat},{min_lon},{max_lat},{max_lon});
        );
        out center;
    """

def extract_address(tags):
    """Формирование читаемого адреса из тегов"""
    street = tags.get("addr:street", "")
    house = tags.get("addr:housenumber", "")
    city = tags.get("addr:city", "")
    
    parts = [p for p in [street, house, city] if p]
    return ", ".join(parts) if parts else None


def process_bbox(bbox, step, osm_key, osm_value, object_type_name):
    """Обрабатывает один квадрат: запрашивает данные, парсит, возвращает список объектов"""
    
    if bbox in processed_bboxes:
        print(f"Квадрат обработан: {bbox}")
        return []

    min_lat, min_lon, max_lat, max_lon = bbox
    query = get_osm_query(min_lat, min_lon, max_lat, max_lon, osm_key, osm_value)

    print(f"Запрос: {osm_key}={osm_value} в квадрате {bbox} (step={step:.3f})")

    data = fetch_from_servers(query)

    # если не удалось получить данные - делим на 4 части для уменьшения нагрузки
    if not data:
        if step / 2 >= MIN_STEP:
            print(f"Делим квадрат на части")
            mid_lat = (min_lat + max_lat) / 2
            mid_lon = (min_lon + max_lon) / 2
            sub_bboxes = [
                (min_lat, min_lon, mid_lat, mid_lon),
                (min_lat, mid_lon, mid_lat, max_lon),
                (mid_lat, min_lon, max_lat, mid_lon),
                (mid_lat, mid_lon, max_lat, max_lon)
            ]
            results = []
            for sub in sub_bboxes:
                results.extend(process_bbox(sub, step/2, osm_key, osm_value, object_type_name))
            save_processed_bbox(bbox)
            return results
        else:
            print(f"Не удалось получить данные для {bbox}")
            save_processed_bbox(bbox)
            return []

    elements = data.get("elements", [])
    print(f"Найдено: {len(elements)}")

    objects = []
    for el in elements:
        tags = el.get("tags", {})

        name = tags.get("name") or tags.get("alt_name") or tags.get("name:ru") or "Без названия"

        # координаты
        if el["type"] == "node":
            lon = el.get("lon")
            lat = el.get("lat")
        else:
            center = el.get("center", {})
            lon = center.get("lon")
            lat = center.get("lat")

        if not lon or not lat:
            continue

        # формирование точки для ПОСТГИС(4326)
        point = f"POINT({lon} {lat})"
        address = extract_address(tags)
        osm_id = el.get("id")

        objects.append((
            object_type_name,
            name,
            address,
            point,
            CREATED_BY,
            osm_id
        ))

    save_processed_bbox(bbox)
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    return objects


# ОСНОВНАЯ ЧАСТЬ

if __name__ == "__main__":
    print(f"Парсинг: {DICT_NAMES.get(TARGET_TYPE, TARGET_TYPE)} (OSM: {OSM_KEYS.get(TARGET_TYPE, 'amenity')}={TARGET_TYPE})")  # ← 2. OBJECT_NAMES → DICT_NAMES
    print(f"Область: Уфа {CITY_BBOX}")
    print(f"Шаг: {STEP}, мин. шаг: {MIN_STEP}")
    print("-" * 60)

    osm_key = OSM_KEYS[TARGET_TYPE]
    object_type_name = DICT_NAMES.get(TARGET_TYPE, TARGET_TYPE.title())

    # Загружаем уже обработанные квадраты
    processed_bboxes = load_processed_bboxes()
    print(f"📁 Загружено {len(processed_bboxes)} обработанных квадратов")

    # Счётчики для статистики
    total_objects = 0
    total_bboxes = 0

    # ← 5. Список для сбора всех объектов перед вставкой в БД
    all_objects = []

    # Главный цикл: перебор всех квадратов
    for bbox in generate_bboxes(CITY_BBOX, STEP):
        total_bboxes += 1
        objs = process_bbox(bbox, STEP, osm_key, TARGET_TYPE, object_type_name)
        total_objects += len(objs)
        all_objects.extend(objs)  # ← 6. Накопление объектов

        # Прогресс каждые 7 квадратов
        if total_bboxes % 7 == 0:
            print(f"Обработано {total_bboxes} квадратов, найдено {total_objects} объектов...")

    # Вставка в базу данных
    print("-" * 60)
    if total_objects > 0:
        try:
            print(f"Вставка {total_objects} объектов в БД...")
            execute_values(
                cur,
                """
                INSERT INTO public.objects(
                    name_type_object,
                    name_objects,
                    address,
                    location,
                    created_by,
                    osm_id
                )
                VALUES %s
                ON CONFLICT(osm_id) DO NOTHING
                """,
                all_objects
            )          
            conn.commit()
            print(f"Успешно сохранено {total_objects} объектов!")
        except Exception as e:
            print(f"Ошибка при вставке в БД: {e}")
            conn.rollback()
    else:
        print("Нет данных для вставки")


    cur.close()
    conn.close()
    print("КОНЕЦ БЛИН")