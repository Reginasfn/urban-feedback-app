import requests
import psycopg2
import time
import os
from dotenv import load_dotenv

load_dotenv()

DADATA_TOKEN = os.getenv("DADATA_TOKEN")
DADATA_SECRET = os.getenv("DADATA_SECRET")

if not DADATA_TOKEN or not DADATA_SECRET:
    print("Ошибка: DADATA_TOKEN или DADATA_SECRET не найден в .env файле!")
    exit(1)

headers = {
    "Authorization": f"Token {DADATA_TOKEN}",
    "X-Secret": DADATA_SECRET,
    "Content-Type": "application/json"
}

# Подключение к БД
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

# Пример координат
cur.execute("""
    SELECT id_object, 
           ST_Y(location) as lat, 
           ST_X(location) as lon,
           ST_AsText(location) as wkt
    FROM objects
    LIMIT 3
""")
test_rows = cur.fetchall()
print("Пример координат из БД:")
for row in test_rows:
    print(f"  ID {row[0]}: lat={row[1]}, lon={row[2]}, WKT={row[3]}")

cur.execute("""
    SELECT id_object, ST_Y(location), ST_X(location)
    FROM objects
    WHERE address IS NULL OR address = ''
    LIMIT 3000
""")
rows = cur.fetchall()
print(f"Тест: найдено объектов {len(rows)}")

updated = 0

for obj_id, lat, lon in rows:
    try:
        if not lat or not lon:
            print(f"Пропуск {obj_id}: нет координат")
            continue

        payload = {"lat": lat, "lon": lon}
        url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/geolocate/address"
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"HTTP {response.status_code} для {obj_id}: {response.text}")
            time.sleep(1)
            continue

        data = response.json()
        suggestions = data.get("suggestions")
        if not suggestions:
            print(f"Нет адреса для {obj_id}")
            time.sleep(0.2)
            continue

        final_address = suggestions[0]["value"]  # полный адрес

        cur.execute("UPDATE objects SET address=%s WHERE id_object=%s", (final_address, obj_id))
        conn.commit()
        updated += 1
        print(f"✔ {obj_id} → {final_address}")

        time.sleep(0.3)  # пауза для стабильности

    except Exception as e:
        print(f"Ошибка {obj_id}: {e}")
        conn.rollback()

print(f"Обновлено: {updated}")

cur.close()
conn.close()





# ЯНДЕКС АПИ ГЕОКОДИРОВАНИЕ
# import requests
# import psycopg2
# import time
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # ПРОВЕРКА КЛЮЧА
# YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
# print(f"API ключ: {'НАЙДЕН ✓' if YANDEX_API_KEY else 'НЕ НАЙДЕН ✗'}")
# print(f"Длина ключа: {len(YANDEX_API_KEY) if YANDEX_API_KEY else 0} символов")

# if not YANDEX_API_KEY:
#     print("ОШИБКА: YANDEX_API_KEY не найден в .env файле!")
#     exit(1)

# YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")

# conn = psycopg2.connect(
#     dbname=os.getenv("DB_NAME"),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASS"),
#     host=os.getenv("DB_HOST"),
#     port=os.getenv("DB_PORT")
# )

# cur = conn.cursor()
# # Добавьте в скрипт проверку:
# cur.execute("""
#     SELECT id_objects, 
#            ST_Y(location) as lat, 
#            ST_X(location) as lon,
#            ST_AsText(location) as wkt
#     FROM objects
#     LIMIT 3
# """)
# test_rows = cur.fetchall()
# print("Пример координат из БД:")
# for row in test_rows:
#     print(f"  ID {row[0]}: lat={row[1]}, lon={row[2]}, WKT={row[3]}")

# cur.execute("""
#     SELECT id_objects, ST_Y(location), ST_X(location)
#     FROM objects
#     LIMIT 100
# """)

# rows = cur.fetchall()

# print(f"Тест: найдено объектов {len(rows)}")

# updated = 0

# for obj_id, lat, lon in rows:
#     try:
#         if not lat or not lon:
#             print(f"Пропуск {obj_id}: нет координат")
#             continue

#         url = f"https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_API_KEY}&geocode={lon},{lat}&format=json"
#         response = requests.get(url, timeout=10)
        
#         if response.status_code != 200:
#             print(f"HTTP {response.status_code} для {obj_id}: {response.text}")
#             time.sleep(1)
#             continue

#         data = response.json()

#         if "response" not in data:
#             print(f"Яндекс вернул ошибку: {data}")
#             time.sleep(1)
#             continue

#         feature = data["response"]["GeoObjectCollection"]["featureMember"]
#         if not feature:
#             print(f"Нет адреса для {obj_id}")
#             time.sleep(0.2)
#             continue

#         geo = feature[0]["GeoObject"]
#         meta = geo["metaDataProperty"]["GeocoderMetaData"]
#         full_address = meta.get("text")
#         components = meta.get("Address", {}).get("Components", [])

#         street = next((c["name"] for c in components if c["kind"] == "street"), None)
#         house = next((c["name"] for c in components if c["kind"] == "house"), None)

#         final_address = f"{street}, {house}" if street and house else (street or full_address)

#         cur.execute("UPDATE objects SET address=%s WHERE id_objects=%s", (final_address, obj_id))
#         conn.commit()
#         updated += 1
#         print(f"✔ {obj_id} → {final_address}")

#         time.sleep(0.3)  # чуть больше паузы для стабильности

#     except Exception as e:
#         print(f"Ошибка {obj_id}: {e}")
#         conn.rollback()

# print(f"Обновлено: {updated}")

# cur.close()
# conn.close()