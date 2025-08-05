import sqlite3
import xml.etree.ElementTree as ET

def load_xml_to_sqlite(xml_path, db_path="poiskmore.db"):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        if root.tag != "records":
            raise ValueError("Корневой элемент должен быть 'records'")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS xml_data (
                id TEXT,
                content TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_xml_id ON xml_data(id)")

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
    except ValueError as e:
        print(f"[Ошибка] Неверная структура XML: {e}")
    except sqlite3.Error as e:
        print(f"[Ошибка] Загрузка XML в SQLite: {e}")