import requests
import json
from qgis.core import QgsProject, QgsSettings
from PyQt5.QtCore import QDateTime
import math
class WeatherService:
    """Сервис для получения и обработки метеорологических данных"""
    def __init__(self):
        self.api_sources = {
            'openweather': {
                'url': 'https://api.openweathermap.org/data/2.5/weather',
                'key_param': 'appid'
            },
            'marine_weather': {
                'url': 'https://api.marine.weather.gov/gridpoints',
                'key_param': None
            }
        }
        self.settings = QgsSettings()
    def get_weather_data(self, lat, lon, source='openweather'):
        """Получение данных о погоде для указанных координат"""
        try:
            if source == 'openweather':
                return self._get_openweather_data(lat, lon)
            elif source == 'marine_weather':
                return self._get_marine_weather_data(lat, lon)
            else:
                return self._get_default_weather_data()
        except Exception as e:
            return self._get_default_weather_data(error=str(e))
    def _get_openweather_data(self, lat, lon):
        """Получение данных от OpenWeatherMap API"""
        api_key = self.settings.value("PoiskMore/openweather_api_key", "")
        if not api_key:
            return self._get_default_weather_data(error="API ключ не настроен")
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric'
        }
        response = requests.get(self.api_sources['openweather']['url'],
                              params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return self._parse_openweather_response(data)
        else:
            return self._get_default_weather_data(error=f"HTTP {response.status_code}")
    def _parse_openweather_response(self, data):
        """Парсинг ответа от OpenWeatherMap"""
        try:
            wind_speed_ms = data['wind'].get('speed', 0)
            wind_direction = data['wind'].get('deg', 0)
            return {
                'wind_speed_ms': wind_speed_ms,
                'wind_speed_knots': wind_speed_ms * 1.944,
                'wind_direction': wind_direction,
                'air_temp': data['main'].get('temp', 15),
                'humidity': data['main'].get('humidity', 70),
                'pressure': data['main'].get('pressure', 1013),
                'visibility': data.get('visibility', 10000) / 1000,  # км
                'weather_desc': data['weather'][0]['description'],
                'clouds': data['clouds'].get('all', 0),
                'timestamp': QDateTime.currentDateTime(),
                'source': 'OpenWeatherMap',
                'status': 'success'
            }
        except KeyError as e:
            return self._get_default_weather_data(error=f"Ошибка парсинга: {str(e)}")
    def _get_marine_weather_data(self, lat, lon):
        """Получение морских метеоданных"""
        # Заглушка для морского API
        return {
            'wind_speed_ms': 5.0,
            'wind_speed_knots': 9.7,
            'wind_direction': 270,
            'wave_height': 1.5,
            'wave_period': 6,
            'wave_direction': 280,
            'water_temp': 16.0,
            'current_speed': 0.8,
            'current_direction': 90,
            'air_temp': 18.0,
            'timestamp': QDateTime.currentDateTime(),
            'source': 'Marine Weather Service',
            'status': 'success'
        }
    def _get_default_weather_data(self, error=None):
        """Получение данных по умолчанию"""
        return {
            'wind_speed_ms': 3.0,
            'wind_speed_knots': 5.8,
            'wind_direction': 270,
            'wave_height': 1.0,
            'wave_period': 5,
            'air_temp': 15.0,
            'water_temp': 14.0,
            'current_speed': 0.5,
            'current_direction': 90,
            'visibility': 10,
            'timestamp': QDateTime.currentDateTime(),
            'source': 'Default values',
            'status': 'default',
            'error': error
        }
    def calculate_sea_state(self, wave_height):
        """Расчет состояния моря по шкале Бофорта"""
        if wave_height < 0.1:
            return {'state': 0, 'description': 'Штиль'}
        elif wave_height < 0.5:
            return {'state': 1, 'description': 'Слабое волнение'}
        elif wave_height < 1.25:
            return {'state': 2, 'description': 'Легкое волнение'}
        elif wave_height < 2.5:
            return {'state': 3, 'description': 'Умеренное волнение'}
        elif wave_height < 4.0:
            return {'state': 4, 'description': 'Неспокойное море'}
        elif wave_height < 6.0:
            return {'state': 5, 'description': 'Бурное море'}
        elif wave_height < 9.0:
            return {'state': 6, 'description': 'Очень бурное море'}
        elif wave_height < 14.0:
            return {'state': 7, 'description': 'Исключительно бурное море'}
        else:
            return {'state': 8, 'description': 'Ураганное море'}
    def get_weather_forecast(self, lat, lon, hours=24):
        """Получение прогноза погоды"""
        # Заглушка для прогноза
        forecast = []
        base_time = QDateTime.currentDateTime()
        for i in range(0, hours, 3):  # Каждые 3 часа
            forecast_time = base_time.addSecs(i * 3600)
            forecast.append({
                'time': forecast_time,
                'wind_speed': 5.0 + math.sin(i * 0.1) * 2,
                'wind_direction': 270 + math.sin(i * 0.05) * 30,
                'wave_height': 1.5 + math.sin(i * 0.08) * 0.5,
                'air_temp': 15 + math.sin(i * 0.02) * 5
            })
        return forecast
def save_weather_data(weather_data):
    """Сохранение метеоданных в проект"""
    project = QgsProject.instance()
    # Сохранение текущих данных
    for key, value in weather_data.items():
        if isinstance(value, QDateTime):
            value = value.toString("yyyy-MM-dd hh:mm:ss")
        project.writeEntry("PoiskMore/Weather", key, str(value))
    return True
def load_weather_data():
    """Загрузка сохраненных метеоданных"""
    project = QgsProject.instance()
    weather_data = {}
    keys = [
        'wind_speed_ms', 'wind_direction', 'wave_height', 'wave_period',
        'air_temp', 'water_temp', 'current_speed', 'current_direction'
    ]
    for key in keys:
        value = project.readEntry("PoiskMore/Weather", key, "0")[0]
        try:
            weather_data[key] = float(value)
        except ValueError:
            weather_data[key] = 0.0
    return weather_data
def calculate_wind_effect_on_search(wind_speed, wind_direction, search_pattern):
    """Расчет влияния ветра на эффективность поиска"""
    # Базовая эффективность поиска
    base_efficiency = 1.0
    # Влияние скорости ветра
    if wind_speed < 5:
        wind_factor = 1.0  # Отличные условия
    elif wind_speed < 10:
        wind_factor = 0.9  # Хорошие условия
    elif wind_speed < 15:
        wind_factor = 0.7  # Удовлетворительные условия
    elif wind_speed < 20:
        wind_factor = 0.5  # Плохие условия
    else:
        wind_factor = 0.3  # Очень плохие условия
    # Влияние направления ветра на различные схемы поиска
    if search_pattern == 'parallel_track':
        # Для параллельных галсов важно направление относительно курса
        direction_factor = 0.8 + 0.2 * abs(math.cos(math.radians(wind_direction)))
    elif search_pattern == 'expanding_square':
        # Для расширяющихся квадратов ветер влияет меньше
        direction_factor = 0.9
    else:
        direction_factor = 0.85
    total_efficiency = base_efficiency * wind_factor * direction_factor
    return {
        'efficiency': total_efficiency,
        'wind_factor': wind_factor,
        'direction_factor': direction_factor,
        'recommendations': get_wind_recommendations(wind_speed, total_efficiency)
    }
def get_wind_recommendations(wind_speed, efficiency):
    """Рекомендации по поиску в зависимости от ветра"""
    recommendations = []
    if wind_speed > 15:
        recommendations.append("Рассмотреть отложение поиска до улучшения погоды")
        recommendations.append("Использовать более крупные поисковые суда")
    elif wind_speed > 10:
        recommendations.append("Увеличить интервалы между галсами")
        recommendations.append("Снизить скорость поиска для лучшего обнаружения")
    elif efficiency < 0.7:
        recommendations.append("Рассмотреть корректировку схемы поиска")
    if wind_speed < 5:
        recommendations.append("Отличные условия для визуального поиска")
    return recommendations
def interpolate_weather_data(weather_points, target_lat, target_lon):
    """Интерполяция метеоданных между точками"""
    if not weather_points:
        return None
    if len(weather_points) == 1:
        return weather_points[0]['data']
    # Простая интерполяция по расстоянию
    total_weight = 0
    weighted_data = {}
    for point in weather_points:
        # Расчет расстояния
        lat_diff = target_lat - point['lat']
        lon_diff = target_lon - point['lon']
        distance = math.sqrt(lat_diff**2 + lon_diff**2)
        # Вес обратно пропорционален расстоянию
        weight = 1.0 / (distance + 0.001)  # Избегаем деления на ноль
        total_weight += weight
        # Взвешенное суммирование
        for key, value in point['data'].items():
            if isinstance(value, (int, float)):
                if key not in weighted_data:
                    weighted_data[key] = 0
                weighted_data[key] += value * weight
    # Нормализация
    for key in weighted_data:
        weighted_data[key] /= total_weight
    return weighted_data