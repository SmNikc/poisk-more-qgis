# -*- coding: utf-8 -*-
"""
Расчет дрейфа. Полная обработка: от ввода weather (validate_weather_data) до вычисления/загрузки в БД (log_drift/save_to_db); от выборки из БД (load_weather_from_db) до обработки (calculate_drift с geospatial).
"""

from qgis.core import QgsPointXY
from math import radians, cos, sin
from ..db.incident_storage import IncidentStorage

def calculate_drift(weather_data, time_hours=1.0):
    if not validate_weather_data(weather_data):
        raise ValueError("Invalid weather data")
    wind_speed = float(weather_data['wind_speed'])
    wind_dir = radians(float(weather_data['wind_dir']))
    current_speed = float(weather_data['current_speed'])
    current_dir = radians(float(weather_data['current_dir']))
    
    drift_x = (wind_speed * cos(wind_dir) + current_speed * cos(current_dir)) * time_hours
    drift_y = (wind_speed * sin(wind_dir) + current_speed * sin(current_dir)) * time_hours
    
    drift = QgsPointXY(drift_x, drift_y)
    
    # Загрузка в БД после вычисления (новое)
    storage = IncidentStorage()
    update_data = {'drift_error': drift.x()}  # Пример
    storage.save_incident(update_data)
    
    return drift

def validate_weather_data(data: dict) -> bool:
    required = ['wind_speed', 'wind_dir', 'current_speed', 'current_dir']
    return all(key in data and isinstance(data[key], (int, float)) for key in required)

# Выборка из БД и обработка (новое)
def load_and_calculate(incident_id: str, time_hours: float = 1.0) -> QgsPointXY:
    storage = IncidentStorage()
    data = storage.get_by_id(incident_id)
    if data:
        weather = {
            'wind_speed': data['wind_speed'],
            'wind_dir': data['wind_dir'],
            'current_speed': data['current_speed'],
            'current_dir': data['current_dir']
        }
        return calculate_drift(weather, time_hours)
    return QgsPointXY(0, 0)