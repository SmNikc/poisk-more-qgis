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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_training_id ON training_log(id)")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[Ошибка] Инициализация training_log: {e}")

def insert_training_entry(entry, db_path="poiskmore.db"):
    try:
        if not all(key in entry for key in ["id", "name", "date"]):
            raise ValueError("Отсутствуют обязательные поля: id, name, date")
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
    except sqlite3.Error as e:
        print(f"[Ошибка] Сохранение записи об учении: {e}")
    except ValueError as e:
        print(f"[Ошибка] Валидация данных: {e}")