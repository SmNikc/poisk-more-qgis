# Хранение инцидентов в SQLite. Обновлено:
# - Переход с MySQL на SQLite
# - Автоматическое создание таблицы
# - Использование `sqlite3.connect('poiskmore.db')`

import sqlite3

def save_incident_to_sqlite(data, db_path="poiskmore.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT,
                datetime TEXT,
                description TEXT
            )
        """)

        cursor.execute(
            "INSERT INTO incidents (id, datetime, description) VALUES (?, ?, ?)",
            (data["id"], data["datetime"], data["description"])
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Ошибка] Сохранение инцидента: {e}")
