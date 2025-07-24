import mysql.connector
from qgis.core import QgsMessageLog
import json

def store_incident(incident_data):
    """Сохранение инцидента в MySQL с сериализацией JSON."""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='poiskmore'
        )
        cursor = conn.cursor()
        query = """
            INSERT INTO incidents (data, created_at)
            VALUES (%s, NOW())
            ON DUPLICATE KEY UPDATE data=VALUES(data), created_at=NOW()
        """
        cursor.execute(query, (json.dumps(incident_data),))
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as e:
        QgsMessageLog.logMessage(f"Ошибка MySQL: {e}", "PoiskMore", Qgis.Critical)
        return -1
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def update_incident(incident_id, incident_data):
    """Обновление данных инцидента."""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='poiskmore'
        )
        cursor = conn.cursor()
        query = "UPDATE incidents SET data = %s, updated_at = NOW() WHERE id = %s"
        cursor.execute(query, (json.dumps(incident_data), incident_id))
        conn.commit()
        return cursor.rowcount > 0
    except mysql.connector.Error as e:
        QgsMessageLog.logMessage(f"Ошибка MySQL: {e}", "PoiskMore", Qgis.Critical)
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
