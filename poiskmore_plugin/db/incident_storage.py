import sqlite3
import json
import os

def save_incident_to_sqlite(data, db_path="poiskmore.db"):
    """Сохранение инцидента в SQLite с сериализацией JSON."""
    if not os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            conn.close()  # Создание пустой БД
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute(
            "INSERT INTO incidents (id, data) VALUES (?, ?) "
            "ON CONFLICT(id) DO UPDATE SET data=excluded.data, created_at=CURRENT_TIMESTAMP",
            (data["id"], json.dumps(data, ensure_ascii=False))
        )

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[Ошибка] Сохранение инцидента в SQLite: {e}")
        return False
    return True