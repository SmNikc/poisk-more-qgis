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
                id TEXT PRIMARY KEY,
                datetime TEXT,
                description TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_incidents_id ON incidents(id)")

        for item in root.findall(".//incident"):
            id_ = item.findtext("id")
            dt = item.findtext("datetime")
            desc = item.findtext("description")
            if id_ and dt and desc:
                cursor.execute(
                    "REPLACE INTO incidents (id, datetime, description) VALUES (?, ?, ?)",
                    (id_, dt, desc)
                )

        conn.commit()
        conn.close()

    except ET.ParseError as e:
        print(f"[Ошибка] Парсинг XML: {e}")
    except sqlite3.Error as e:
        print(f"[Ошибка] Импорт в SQLite: {e}")