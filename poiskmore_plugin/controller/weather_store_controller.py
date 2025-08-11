import os
from threading import Thread
class WeatherManageContext:
def __init__(self):
self.weather_data = []
self.weather_store = None
def set_weather_store(self, store):
self.weather_store = store
class WeatherStore:
def __init__(self, path):
self.path = path
class IWeatherStoreView:
def __init__(self):
self.database_download = None
self.database_remove = None
self.database_select = None
def set_data_source(self, data):
pass
class WeatherStoreController:
def __init__(self, context):
if context is None:
raise ValueError("context")
self.data_context = context
self.view = None
@property
def data_context(self):
return self._data_context
def open_database(self, path):
store = WeatherStore(path)
self.data_context.set_weather_store(store)
def attach_view(self, view):
if view is None:
raise ValueError("view")
self.view = view
self.view.database_download = self.on_download_database
self.view.database_remove = self.on_database_remove
self.view.database_select = self.on_database_select
self.view.set_data_source(self.data_context.weather_data)
def on_download_database(self):
Thread(target=lambda: print("Downloading database")).start()
def on_database_remove(self):
print("Removing database")
def on_database_select(self):
print("Selecting database")