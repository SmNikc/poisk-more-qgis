# Инициализация схемы SQLite. Новое:
# - Отдельный модуль для создания структуры таблиц
# - Используется при первом запуске

import sqlite3

def initialize_schema(db_path="poiskmore.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                datetime TEXT,
                description TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[Ошибка] Инициализация схемы БД: {e}")
