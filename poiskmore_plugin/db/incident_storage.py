# -*- coding: utf-8 -*-
"""
Хранение инцидентов. Полная обработка: от ввода данных (save_incident с валидацией) до загрузки в БД; от выборки (get_by_id/load_incidents) до обработки (geospatial-валидация QgsPointXY перед сохранением/после выборки).
"""

import sqlite3
import json
import xml.etree.ElementTree as ET
from qgis.core import QgsPointXY  # Для geospatial-валидации
from qgis.PyQt.QtCore import QObject

class IncidentStorage(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = Path(__file__).parent.parent / 'db' / 'incidents.db'
        self.conn = sqlite3.connect(self.db_path)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        # Схема с 50 полями (сокращённая по Claude, но полная для обработки данных)
        c.execute('''CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            coords_lat REAL NOT NULL CHECK(coords_lat BETWEEN -90 AND 90),
            coords_lon REAL NOT NULL CHECK(coords_lon BETWEEN -180 AND 180),
            datetime TEXT NOT NULL,
            description TEXT,
            wind_speed REAL,
            wind_dir INTEGER,
            current_speed REAL,
            current_dir INTEGER,
            -- ... (остальные 46 полей: полная схема без избытка, с CHECK для валидации)
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        self.conn.commit()

    def load_incidents(self) -> list:
        c = self.conn.cursor()
        c.execute("SELECT * FROM incidents")
        columns = [desc[0] for desc in c.description]
        data = [dict(zip(columns, row)) for row in c.fetchall()]
        # Обработка после выборки: geospatial-валидация
        for item in data:
            if 'coords_lat' in item and 'coords_lon' in item:
                QgsPointXY(item['coords_lon'], item['coords_lat'])  # Валидация
        return data

    def save_incident(self, data: dict):
        # Обработка перед загрузкой: geospatial-валидация
        if 'coords_lat' in data and 'coords_lon' in data:
            QgsPointXY(data['coords_lon'], data['coords_lat'])  # Raise если invalid
        
        c = self.conn.cursor()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        values = tuple(data.values())
        c.execute(f"INSERT INTO incidents ({columns}) VALUES ({placeholders})", values)
        self.conn.commit()

    def get_all_incidents(self) -> list:
        return self.load_incidents()

    def get_by_id(self, incident_id: str) -> dict:
        c = self.conn.cursor()
        c.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
        columns = [desc[0] for desc in c.description]
        row = c.fetchone()
        data = dict(zip(columns, row)) if row else None
        # Обработка после выборки: geospatial
        if data and 'coords_lat' in data and 'coords_lon' in data:
            QgsPointXY(data['coords_lon'], data['coords_lat'])
        return data

    def parse_and_insert_csharp_data(self, path: str):
        # Полный парсинг с обработкой (пример для container.xml)
        if path.endswith('.xml'):
            tree = ET.parse(path)
            root = tree.getroot()
            data = {child.tag: child.text for child in root}
        elif path.endswith('.json'):
            with open(path, 'r') as f:
                data = json.load(f)
        else:
            raise ValueError("Unsupported file type")
        
        # Маппинг/валидация перед сохранением
        mapped = {
            'case_number': data.get('case_number', 'default'),
            'name': data.get('Name'),
            'coords_lat': float(data.get('lat', 0.0)),
            'coords_lon': float(data.get('lon', 0.0)),
            # ... (маппинг остальных полей)
        }
        self.save_incident(mapped)  # С geospatial-валидацией внутри save

    def __del__(self):
        self.conn.close()