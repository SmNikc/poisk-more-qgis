# Импорт XML в SQLite. Обновлено:
# - Переход с MySQL на SQLite
# - Автоматическое создание таблицы
# - Парсинг XML с проверкой

import sqlite3
import xml.etree.ElementTree as ET

def xml_to_sqlite(xml_path, db_path="poiskmore.db"):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT,
                datetime TEXT,
                description TEXT
            )
        """)

        for item in root.findall(".//incident"):
            id_ = item.findtext("id")
            dt = item.findtext("datetime")
            desc = item.findtext("description")
            if id_ and dt and desc:
                cursor.execute(
                    "INSERT INTO incidents (id, datetime, description) VALUES (?, ?, ?)",
                    (id_, dt, desc)
                )

        conn.commit()
        conn.close()

    except ET.ParseError as e:
        print(f"[Ошибка] Парсинг XML: {e}")
    except Exception as e:
        print(f"[Ошибка] Импорт в SQLite: {e}")
