import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()
CREATED_BY = 1

# база данных
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

# AMENITY = "cafe"
AMENITY = "bench"

# Уфа
CITY_BBOX = (54.68, 55.90, 55.02, 56.12)
STEP = 0.05
MIN_STEP = 0.02

# всякие ссылки другие
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

REQUEST_TIMEOUT = 300
SLEEP_BETWEEN_REQUESTS = 30

# файл для отслеживания уде прошедших квадратов
PROCESSED_FILE = "processed_bboxes.txt"
if os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE, "r") as f:
        processed_bboxes = set(tuple(map(float, line.strip().split(","))) for line in f)
else:
    processed_bboxes = set()

# функции
def save_processed_bbox(bbox):
    with open(PROCESSED_FILE, "a") as f:
        f.write(",".join(map(str, bbox)) + "\n")
    processed_bboxes.add(bbox)

def fetch_from_servers(query, max_retries=3):
    for attempt in range(max_retries):
        for url in OVERPASS_SERVERS:
            try:
                response = requests.post(url, data=query, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Ошибка на {url}: {e} (попытка {attempt+1})")
                time.sleep(SLEEP_BETWEEN_REQUESTS)
    return None

def generate_bboxes(bbox, step):
    min_lat, min_lon, max_lat, max_lon = bbox
    lat = min_lat
    while lat < max_lat:
        lon = min_lon
        while lon < max_lon:
            yield (lat, lon, min(lat+step, max_lat), min(lon+step, max_lon))
            lon += step
        lat += step

def process_bbox(bbox, step):
    if bbox in processed_bboxes:
        print(f"Квадрат обработан: {bbox}")
        return []

    min_lat, min_lon, max_lat, max_lon = bbox
    query = f"""
    [out:json][timeout:60];
    (
      node["amenity"="{AMENITY}"]({min_lat},{min_lon},{max_lat},{max_lon});
      way["amenity"="{AMENITY}"]({min_lat},{min_lon},{max_lat},{max_lon});
      relation["amenity"="{AMENITY}"]({min_lat},{min_lon},{max_lat},{max_lon});
    );
    out center;
    """
    print(f"Запрос к OSM для квадрата: {bbox} (step={step})")
    data = fetch_from_servers(query)
    if not data:
        if step / 2 >= MIN_STEP:
            print(f"Делим квадрат на 4 части для уменьшения нагрузки")
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
                results.extend(process_bbox(sub, step/2))
            save_processed_bbox(bbox)
            return results
        else:
            print(f"Не удалось получить данные для квадрата {bbox}")
            save_processed_bbox(bbox)
            return []

    elements = data.get("elements", [])
    print(f"Найдено: {len(elements)}")

    objects = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue

        if el["type"] == "node":
            lon = el.get("lon")
            lat = el.get("lat")
        else:
            center = el.get("center", {})
            lon = center.get("lon")
            lat = center.get("lat")
        if not lon or not lat:
            continue

        point = f"POINT({lon} {lat})"
        street = tags.get("addr:street", "")
        house = tags.get("addr:housenumber", "")
        address = f"{street} {house}".strip() if street or house else None

        objects.append((
            "Скамейки",
            name,
            address,
            point,
            CREATED_BY,
            el.get("id")
        ))

    save_processed_bbox(bbox)
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    return objects

# цикл
all_objects = []
for bbox in generate_bboxes(CITY_BBOX, STEP):
    objs = process_bbox(bbox, STEP)
    all_objects.extend(objs)

# вставить в бдшку
if all_objects:
    try:
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
        print(f"Всего объектов: {len(all_objects)}")
    except Exception as e:
        print("Ошибка при вставке:", e)
else:
    print("Нет данных для вставки")

cur.close()
conn.close()
print("КОНЕЦ БЛИН")