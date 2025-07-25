# База данных учебных операций. Переписано:
# - С MySQL на SQLite
# - Поддержка автоинициализации

import sqlite3

def init_training_db(db_path="poiskmore.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_log (
                id TEXT PRIMARY KEY,
                name TEXT,
                date TEXT,
                duration INTEGER,
                notes TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Ошибка] Инициализация training_log: {e}")

def insert_training_entry(entry, db_path="poiskmore.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO training_log (id, name, date, duration, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            entry["id"],
            entry["name"],
            entry["date"],
            entry.get("duration", 0),
            entry.get("notes", "")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Ошибка] Сохранение записи об учении: {e}")
