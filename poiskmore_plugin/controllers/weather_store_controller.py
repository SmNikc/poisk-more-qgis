from typing import List
from qgis.core import QgsProject, QgsVectorLayer
from .models import WeatherDataItem  # Предполагается, что модели в models.py
class WeatherManageContext:
    def __init__(self):
        self.weather_data: List[WeatherDataItem] = []
    def set_weather_store(self, store):
        self.weather_data.clear()
class WeatherStoreController:
    def __init__(self, context: WeatherManageContext):
        if context is None:
            raise ValueError("context cannot be None")
        self.data_context = context
        self.view = None
    def open_database(self, path: str):
        store = QgsVectorLayer(path, "weather_store", "ogr")
        if not store.isValid():
            raise ValueError("Invalid layer")
        self.data_context.set_weather_store(store)
    def attach_view(self, view):
        if view is None:
            raise ValueError("view cannot be None")
        self.view = view