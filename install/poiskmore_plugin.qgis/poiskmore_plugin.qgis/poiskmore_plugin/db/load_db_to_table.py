# Загрузка из БД в таблицу. Улучшен:
# Добавлена try-except, использование with
# для conn.

import sqlite3

def fetch_all_from_db(db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, datetime, description FROM incidents")
            rows = c.fetchall()
            return rows
    except Exception as e:
        print(f"[Ошибка] Загрузка данных: {e}")
        return []
