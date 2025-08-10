import sqlite3

def fetch_all_from_sqlite(db_path="poiskmore.db"):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, data, created_at FROM incidents ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [(row[0], json.loads(row[1]), row[2]) for row in rows]
    except sqlite3.Error as e:
        print(f"[Ошибка] Загрузка данных из SQLite: {e}")
        return []