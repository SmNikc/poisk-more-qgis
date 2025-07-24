# Импорт XML в MySQL. Улучшен: Try-except, проверка элементов, миграция на MySQL.

import mysql.connector
import xml.etree.ElementTree as ET
from mysql.connector import Error

def xml_to_mysql(xml_path, host='localhost', user='root', password='password', db='poiskmore'):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db
        )
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id VARCHAR(255),
                datetime VARCHAR(255),
                description TEXT
            )
        """)

        for item in root.findall(".//incident"):
            id_ = item.findtext("id")
            dt = item.findtext("datetime")
            desc = item.findtext("description")
            if id_ and dt and desc:
                c.execute("INSERT INTO incidents VALUES (%s, %s, %s)", (id_, dt, desc))

        conn.commit()
        conn.close()

    except ET.ParseError as e:
        print(f"Ошибка парсинга XML: {e}")
    except Error as e:
        print(f"Ошибка работы с MySQL: {e}")
