# Загрузка из SQLite в таблицу. Обновлено:
# - Переход с MySQL на SQLite
# - Обработка ошибок с try-except
# - Поддержка параметра пути к .db

import sqlite3

def fetch_all_from_sqlite(db_path="poiskmore.db"):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, datetime, description FROM incidents")
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        print(f"[Ошибка] Загрузка данных из SQLite: {e}")
        return []
