from flask import Flask, jsonify, request, render_template
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='.')

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

@app.route("/")
def index():
    api_key = os.getenv("YANDEX_API_KEY")
    return render_template("index.html", api_key=api_key)
    
@app.route("/objects")
def get_objects():
    obj_type = request.args.get("type")  # получаем тип объекта из запроса

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT 
            name_objects,
            address,
            ST_Y(location) as lat,
            ST_X(location) as lon
        FROM public.objects
        WHERE name_type_object = %s
        LIMIT 1000
    """
    cur.execute(query, (obj_type,))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "name": r[0],
            "address": r[1],
            "coords": [r[2], r[3]]
        })

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)