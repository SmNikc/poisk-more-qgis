# Загрузка XML. Улучшен:
# - Добавлена try-except
# - Переписано на SQLite
# - Сохраняет XML-данные в таблицу xml_data

import sqlite3
import xml.etree.ElementTree as ET

def load_xml_to_sqlite(xml_path, db_path="poiskmore.db"):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS xml_data (
                id TEXT,
                content TEXT
            )
        """)

        for element in root.findall(".//record"):
            rec_id = element.findtext("id") or ""
            rec_data = ET.tostring(element, encoding="unicode")
            cursor.execute(
                "INSERT INTO xml_data (id, content) VALUES (?, ?)",
                (rec_id, rec_data)
            )

        conn.commit()
        conn.close()
    except ET.ParseError as e:
        print(f"[Ошибка] Парсинг XML: {e}")
    except Exception as e:
        print(f"[Ошибка] Загрузка XML в SQLite: {e}")
