import sqlite3

def initialize_schema(db_path="poiskmore.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                datetime TEXT,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_log (
                id TEXT PRIMARY KEY,
                name TEXT,
                date TEXT,
                duration INTEGER,
                notes TEXT
            )
        """)
        # Проверка версии схемы (добавлена для будущих миграций)
        cursor.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)")
        cursor.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (1)")
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"[Ошибка] Инициализация схемы БД: {e}")