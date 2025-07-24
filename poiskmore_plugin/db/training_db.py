import mysql.connector
from qgis.core import QgsMessageLog
import configparser

config = configparser.ConfigParser()
config.read('config/default.ini')
db_config = {
    'host': config.get('MySQL', 'host', fallback='localhost'),
    'user': config.get('MySQL', 'user', fallback='root'),
    'password': config.get('MySQL', 'password', fallback=''),
    'database': config.get('MySQL', 'database', fallback='poiskmore')
}

def save_training_data(incident_id, lat, lon, timestamp, status):
    """Сохранение данных учений в MySQL."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
            INSERT INTO training_data (incident_id, latitude, longitude, timestamp, status)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE latitude=VALUES(latitude), longitude=VALUES(longitude),
            timestamp=VALUES(timestamp), status=VALUES(status)
        """
        cursor.execute(query, (incident_id, lat, lon, timestamp, status))
        conn.commit()
    except mysql.connector.Error as e:
        QgsMessageLog.logMessage(f"Ошибка MySQL: {e}", "PoiskMore", Qgis.Critical)
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    return True

def get_training_data(incident_id):
    """Получение данных учений по incident_id."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT * FROM training_data WHERE incident_id = %s"
        cursor.execute(query, (incident_id,))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        QgsMessageLog.logMessage(f"Ошибка MySQL: {e}", "PoiskMore", Qgis.Critical)
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
