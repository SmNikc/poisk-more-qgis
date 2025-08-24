#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль: weather_conditions.py
Описание: Расширенные погодные условия для поисково-спасательных операций
Автор: Claude AI
Дата создания: 2025-08-24
Версия: 1.0.0

Содержит классификации видимости, осадков, облачности и других метеоусловий
согласно стандартам IAMSAR и WMO
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


# Классификация видимости (согласно WMO)
VISIBILITY_SCALE = {
    "excellent": {
        "code": 9,
        "description": "Отличная",
        "range_nm": (10, 999),  # морские мили
        "range_m": (18520, 999999),
        "search_factor": 1.0,
        "flying_conditions": "VFR",
        "description_en": "Excellent visibility"
    },
    "very_good": {
        "code": 8,
        "description": "Очень хорошая",
        "range_nm": (5, 10),
        "range_m": (9260, 18520),
        "search_factor": 0.9,
        "flying_conditions": "VFR",
        "description_en": "Very good visibility"
    },
    "good": {
        "code": 7,
        "description": "Хорошая",
        "range_nm": (2, 5),
        "range_m": (3704, 9260),
        "search_factor": 0.75,
        "flying_conditions": "VFR",
        "description_en": "Good visibility"
    },
    "moderate": {
        "code": 6,
        "description": "Умеренная",
        "range_nm": (1, 2),
        "range_m": (1852, 3704),
        "search_factor": 0.5,
        "flying_conditions": "MVFR",
        "description_en": "Moderate visibility"
    },
    "poor": {
        "code": 5,
        "description": "Плохая",
        "range_nm": (0.5, 1),
        "range_m": (926, 1852),
        "search_factor": 0.3,
        "flying_conditions": "IFR",
        "description_en": "Poor visibility"
    },
    "very_poor": {
        "code": 4,
        "description": "Очень плохая",
        "range_nm": (0.25, 0.5),
        "range_m": (463, 926),
        "search_factor": 0.15,
        "flying_conditions": "IFR",
        "description_en": "Very poor visibility"
    },
    "fog": {
        "code": 3,
        "description": "Туман",
        "range_nm": (0, 0.25),
        "range_m": (0, 463),
        "search_factor": 0.05,
        "flying_conditions": "IFR",
        "description_en": "Fog"
    },
    "thick_fog": {
        "code": 2,
        "description": "Густой туман",
        "range_nm": (0, 0.05),
        "range_m": (0, 100),
        "search_factor": 0.01,
        "flying_conditions": "NO FLY",
        "description_en": "Thick fog"
    }
}

# Типы осадков
PRECIPITATION_TYPES = {
    "none": {
        "code": "RA0",
        "description": "Без осадков",
        "visibility_impact": 1.0,
        "search_impact": 1.0,
        "symbol": "☀",
        "description_en": "No precipitation"
    },
    "drizzle": {
        "code": "DZ",
        "description": "Морось",
        "visibility_impact": 0.8,
        "search_impact": 0.9,
        "symbol": "🌦",
        "description_en": "Drizzle"
    },
    "light_rain": {
        "code": "RA1",
        "description": "Небольшой дождь",
        "visibility_impact": 0.7,
        "search_impact": 0.85,
        "symbol": "🌧",
        "description_en": "Light rain"
    },
    "moderate_rain": {
        "code": "RA2",
        "description": "Умеренный дождь",
        "visibility_impact": 0.5,
        "search_impact": 0.7,
        "symbol": "🌧",
        "description_en": "Moderate rain"
    },
    "heavy_rain": {
        "code": "RA3",
        "description": "Сильный дождь",
        "visibility_impact": 0.3,
        "search_impact": 0.5,
        "symbol": "⛈",
        "description_en": "Heavy rain"
    },
    "light_snow": {
        "code": "SN1",
        "description": "Небольшой снег",
        "visibility_impact": 0.6,
        "search_impact": 0.7,
        "symbol": "🌨",
        "description_en": "Light snow"
    },
    "moderate_snow": {
        "code": "SN2",
        "description": "Умеренный снег",
        "visibility_impact": 0.4,
        "search_impact": 0.5,
        "symbol": "❄",
        "description_en": "Moderate snow"
    },
    "heavy_snow": {
        "code": "SN3",
        "description": "Сильный снег",
        "visibility_impact": 0.2,
        "search_impact": 0.3,
        "symbol": "❄",
        "description_en": "Heavy snow"
    },
    "hail": {
        "code": "GR",
        "description": "Град",
        "visibility_impact": 0.4,
        "search_impact": 0.3,
        "symbol": "🌨",
        "description_en": "Hail"
    },
    "thunderstorm": {
        "code": "TS",
        "description": "Гроза",
        "visibility_impact": 0.3,
        "search_impact": 0.2,
        "symbol": "⛈",
        "description_en": "Thunderstorm"
    }
}

# Облачность (в октах - восьмых долях неба)
CLOUD_COVER = {
    0: {
        "code": "SKC",
        "description": "Ясно",
        "octas": "0/8",
        "percentage": 0,
        "symbol": "☀",
        "description_en": "Clear sky"
    },
    1: {
        "code": "FEW",
        "description": "Малооблачно",
        "octas": "1/8",
        "percentage": 12.5,
        "symbol": "🌤",
        "description_en": "Few clouds"
    },
    2: {
        "code": "FEW",
        "description": "Небольшая облачность",
        "octas": "2/8",
        "percentage": 25,
        "symbol": "⛅",
        "description_en": "Few clouds"
    },
    3: {
        "code": "SCT",
        "description": "Переменная облачность",
        "octas": "3/8",
        "percentage": 37.5,
        "symbol": "⛅",
        "description_en": "Scattered clouds"
    },
    4: {
        "code": "SCT",
        "description": "Облачно с прояснениями",
        "octas": "4/8",
        "percentage": 50,
        "symbol": "🌥",
        "description_en": "Scattered clouds"
    },
    5: {
        "code": "BKN",
        "description": "Облачно",
        "octas": "5/8",
        "percentage": 62.5,
        "symbol": "☁",
        "description_en": "Broken clouds"
    },
    6: {
        "code": "BKN",
        "description": "Значительная облачность",
        "octas": "6/8",
        "percentage": 75,
        "symbol": "☁",
        "description_en": "Broken clouds"
    },
    7: {
        "code": "BKN",
        "description": "Почти сплошная облачность",
        "octas": "7/8",
        "percentage": 87.5,
        "symbol": "☁",
        "description_en": "Broken clouds"
    },
    8: {
        "code": "OVC",
        "description": "Сплошная облачность",
        "octas": "8/8",
        "percentage": 100,
        "symbol": "☁",
        "description_en": "Overcast"
    }
}

# Шкала Бофорта (для справки и корреляции)
BEAUFORT_SCALE = {
    0: {
        "description": "Штиль",
        "wind_speed_knots": (0, 1),
        "wind_speed_ms": (0, 0.5),
        "wind_speed_kmh": (0, 1.8),
        "sea_conditions": "Зеркально гладкое море",
        "on_land": "Дым поднимается вертикально",
        "description_en": "Calm"
    },
    1: {
        "description": "Тихий",
        "wind_speed_knots": (1, 3),
        "wind_speed_ms": (0.5, 1.5),
        "wind_speed_kmh": (1.8, 5.4),
        "sea_conditions": "Рябь без барашков",
        "on_land": "Дым слегка отклоняется",
        "description_en": "Light air"
    },
    2: {
        "description": "Легкий",
        "wind_speed_knots": (4, 6),
        "wind_speed_ms": (1.6, 3.3),
        "wind_speed_kmh": (5.8, 11.9),
        "sea_conditions": "Небольшие волны без барашков",
        "on_land": "Листья шелестят",
        "description_en": "Light breeze"
    },
    3: {
        "description": "Слабый",
        "wind_speed_knots": (7, 10),
        "wind_speed_ms": (3.4, 5.4),
        "wind_speed_kmh": (12.2, 19.4),
        "sea_conditions": "Небольшие волны, редкие барашки",
        "on_land": "Листья и тонкие ветки в движении",
        "description_en": "Gentle breeze"
    },
    4: {
        "description": "Умеренный",
        "wind_speed_knots": (11, 16),
        "wind_speed_ms": (5.5, 7.9),
        "wind_speed_kmh": (19.8, 28.4),
        "sea_conditions": "Волны с многочисленными барашками",
        "on_land": "Ветки в движении, поднимается пыль",
        "description_en": "Moderate breeze"
    },
    5: {
        "description": "Свежий",
        "wind_speed_knots": (17, 21),
        "wind_speed_ms": (8.0, 10.7),
        "wind_speed_kmh": (28.8, 38.5),
        "sea_conditions": "Умеренные волны, много барашков",
        "on_land": "Качаются тонкие стволы деревьев",
        "description_en": "Fresh breeze"
    },
    6: {
        "description": "Сильный",
        "wind_speed_knots": (22, 27),
        "wind_speed_ms": (10.8, 13.8),
        "wind_speed_kmh": (38.9, 49.7),
        "sea_conditions": "Крупные волны с пенистыми гребнями",
        "on_land": "Качаются толстые ветки",
        "description_en": "Strong breeze"
    },
    7: {
        "description": "Крепкий",
        "wind_speed_knots": (28, 33),
        "wind_speed_ms": (13.9, 17.1),
        "wind_speed_kmh": (50.0, 61.6),
        "sea_conditions": "Волны громоздятся, пена ложится полосами",
        "on_land": "Качаются деревья, трудно идти",
        "description_en": "Near gale"
    },
    8: {
        "description": "Очень крепкий",
        "wind_speed_knots": (34, 40),
        "wind_speed_ms": (17.2, 20.7),
        "wind_speed_kmh": (61.9, 74.5),
        "sea_conditions": "Высокие волны, полосы пены",
        "on_land": "Ломаются ветки деревьев",
        "description_en": "Gale"
    },
    9: {
        "description": "Шторм",
        "wind_speed_knots": (41, 47),
        "wind_speed_ms": (20.8, 24.4),
        "wind_speed_kmh": (74.9, 87.8),
        "sea_conditions": "Высокие волны, гребни опрокидываются",
        "on_land": "Срываются черепицы и трубы",
        "description_en": "Strong gale"
    },
    10: {
        "description": "Сильный шторм",
        "wind_speed_knots": (48, 55),
        "wind_speed_ms": (24.5, 28.4),
        "wind_speed_kmh": (88.2, 102.2),
        "sea_conditions": "Очень высокие волны, море белое от пены",
        "on_land": "Вырываются деревья с корнем",
        "description_en": "Storm"
    },
    11: {
        "description": "Жестокий шторм",
        "wind_speed_knots": (56, 63),
        "wind_speed_ms": (28.5, 32.6),
        "wind_speed_kmh": (102.6, 117.4),
        "sea_conditions": "Исключительно высокие волны",
        "on_land": "Большие разрушения",
        "description_en": "Violent storm"
    },
    12: {
        "description": "Ураган",
        "wind_speed_knots": (64, 999),
        "wind_speed_ms": (32.7, 999),
        "wind_speed_kmh": (117.7, 999),
        "sea_conditions": "Воздух наполнен пеной и брызгами",
        "on_land": "Опустошительные разрушения",
        "description_en": "Hurricane"
    }
}

# Дополнительные погодные явления
WEATHER_PHENOMENA = {
    "mist": {
        "code": "BR",
        "description": "Дымка",
        "visibility_impact": 0.7,
        "description_en": "Mist"
    },
    "haze": {
        "code": "HZ",
        "description": "Мгла",
        "visibility_impact": 0.6,
        "description_en": "Haze"
    },
    "smoke": {
        "code": "FU",
        "description": "Дым",
        "visibility_impact": 0.5,
        "description_en": "Smoke"
    },
    "dust": {
        "code": "DU",
        "description": "Пыль",
        "visibility_impact": 0.4,
        "description_en": "Dust"
    },
    "sand": {
        "code": "SA",
        "description": "Песок",
        "visibility_impact": 0.3,
        "description_en": "Sand"
    },
    "spray": {
        "code": "PY",
        "description": "Водяная пыль",
        "visibility_impact": 0.6,
        "description_en": "Spray"
    }
}


class WeatherConditions:
    """Класс для работы с погодными условиями"""
    
    def __init__(self):
        self.visibility = None
        self.precipitation = None
        self.cloud_cover = None
        self.wind_beaufort = None
        self.phenomena = []
        self.air_temp_c = None
        self.water_temp_c = None
        self.humidity_percent = None
        self.pressure_hpa = None
    
    def set_visibility(self, visibility_code: str):
        """Установить видимость"""
        if visibility_code in VISIBILITY_SCALE:
            self.visibility = VISIBILITY_SCALE[visibility_code]
    
    def set_precipitation(self, precip_type: str):
        """Установить тип осадков"""
        if precip_type in PRECIPITATION_TYPES:
            self.precipitation = PRECIPITATION_TYPES[precip_type]
    
    def set_cloud_cover(self, octas: int):
        """Установить облачность в октах"""
        if octas in CLOUD_COVER:
            self.cloud_cover = CLOUD_COVER[octas]
    
    def set_wind(self, beaufort: int):
        """Установить ветер по Бофорту"""
        if beaufort in BEAUFORT_SCALE:
            self.wind_beaufort = BEAUFORT_SCALE[beaufort]
    
    def add_phenomenon(self, phenomenon: str):
        """Добавить погодное явление"""
        if phenomenon in WEATHER_PHENOMENA:
            self.phenomena.append(WEATHER_PHENOMENA[phenomenon])
    
    def calculate_search_effectiveness(self) -> float:
        """
        Рассчитать эффективность поиска на основе погодных условий
        
        Returns:
            Коэффициент эффективности (0-1)
        """
        effectiveness = 1.0
        
        # Влияние видимости
        if self.visibility:
            effectiveness *= self.visibility.get("search_factor", 1.0)
        
        # Влияние осадков
        if self.precipitation:
            effectiveness *= self.precipitation.get("search_impact", 1.0)
        
        # Влияние явлений
        for phenomenon in self.phenomena:
            effectiveness *= phenomenon.get("visibility_impact", 1.0)
        
        # Влияние ветра (сильный ветер снижает эффективность)
        if self.wind_beaufort:
            wind_speed = self.wind_beaufort["wind_speed_knots"][1]
            if wind_speed > 30:
                effectiveness *= 0.5
            elif wind_speed > 20:
                effectiveness *= 0.7
            elif wind_speed > 15:
                effectiveness *= 0.85
        
        return max(0.01, min(1.0, effectiveness))
    
    def get_flight_conditions(self) -> str:
        """
        Определить условия для полетов
        
        Returns:
            VFR, MVFR, IFR или NO FLY
        """
        if self.visibility:
            return self.visibility.get("flying_conditions", "UNKNOWN")
        return "UNKNOWN"
    
    def format_weather_report(self) -> str:
        """
        Сформировать погодный отчет
        
        Returns:
            Форматированный отчет
        """
        report_lines = ["ПОГОДНЫЕ УСЛОВИЯ", "=" * 40]
        
        if self.visibility:
            report_lines.append(f"Видимость: {self.visibility['description']} "
                              f"({self.visibility['range_nm'][0]}-{self.visibility['range_nm'][1]} миль)")
        
        if self.precipitation:
            report_lines.append(f"Осадки: {self.precipitation['description']} "
                              f"{self.precipitation['symbol']}")
        
        if self.cloud_cover:
            report_lines.append(f"Облачность: {self.cloud_cover['description']} "
                              f"({self.cloud_cover['octas']})")
        
        if self.wind_beaufort:
            report_lines.append(f"Ветер: {self.wind_beaufort['description']} "
                              f"({self.wind_beaufort['wind_speed_knots'][0]}-"
                              f"{self.wind_beaufort['wind_speed_knots'][1]} узлов)")
        
        if self.phenomena:
            phenomena_str = ", ".join([p['description'] for p in self.phenomena])
            report_lines.append(f"Явления: {phenomena_str}")
        
        if self.air_temp_c is not None:
            report_lines.append(f"Температура воздуха: {self.air_temp_c}°C")
        
        if self.water_temp_c is not None:
            report_lines.append(f"Температура воды: {self.water_temp_c}°C")
        
        if self.humidity_percent is not None:
            report_lines.append(f"Влажность: {self.humidity_percent}%")
        
        if self.pressure_hpa is not None:
            report_lines.append(f"Давление: {self.pressure_hpa} гПа")
        
        effectiveness = self.calculate_search_effectiveness()
        report_lines.append(f"\nЭффективность поиска: {effectiveness:.0%}")
        report_lines.append(f"Условия для полетов: {self.get_flight_conditions()}")
        
        return "\n".join(report_lines)


def get_visibility_by_distance(distance_nm: float) -> str:
    """
    Определить категорию видимости по расстоянию
    
    Args:
        distance_nm: Видимость в морских милях
        
    Returns:
        Код категории видимости
    """
    if distance_nm >= 10:
        return "excellent"
    elif distance_nm >= 5:
        return "very_good"
    elif distance_nm >= 2:
        return "good"
    elif distance_nm >= 1:
        return "moderate"
    elif distance_nm >= 0.5:
        return "poor"
    elif distance_nm >= 0.25:
        return "very_poor"
    elif distance_nm > 0.05:
        return "fog"
    else:
        return "thick_fog"


def get_beaufort_by_wind_speed(speed_knots: float) -> int:
    """
    Определить балл по шкале Бофорта по скорости ветра
    
    Args:
        speed_knots: Скорость ветра в узлах
        
    Returns:
        Балл по шкале Бофорта
    """
    for beaufort, data in BEAUFORT_SCALE.items():
        min_speed, max_speed = data["wind_speed_knots"]
        if min_speed <= speed_knots <= max_speed:
            return beaufort
    
    # Если скорость выше максимальной - ураган
    if speed_knots > 64:
        return 12
    
    return 0


def calculate_wind_chill(air_temp_c: float, wind_speed_knots: float) -> float:
    """
    Рассчитать ощущаемую температуру (wind chill)
    
    Args:
        air_temp_c: Температура воздуха в °C
        wind_speed_knots: Скорость ветра в узлах
        
    Returns:
        Ощущаемая температура в °C
    """
    # Конвертируем узлы в км/ч
    wind_speed_kmh = wind_speed_knots * 1.852
    
    # Формула wind chill (для температур ниже 10°C и ветра выше 4.8 км/ч)
    if air_temp_c <= 10 and wind_speed_kmh >= 4.8:
        wind_chill = (13.12 + 0.6215 * air_temp_c - 
                     11.37 * (wind_speed_kmh ** 0.16) + 
                     0.3965 * air_temp_c * (wind_speed_kmh ** 0.16))
        return round(wind_chill, 1)
    else:
        return air_temp_c


def estimate_icing_risk(air_temp_c: float, 
                        precipitation: str,
                        wind_speed_knots: float) -> str:
    """
    Оценить риск обледенения
    
    Args:
        air_temp_c: Температура воздуха
        precipitation: Тип осадков
        wind_speed_knots: Скорость ветра
        
    Returns:
        Уровень риска: none, low, moderate, high, severe
    """
    if air_temp_c > 2:
        return "none"
    
    # Проверяем наличие осадков
    has_precipitation = precipitation not in ["none", None]
    
    if air_temp_c <= -20:
        return "severe" if has_precipitation else "high"
    elif air_temp_c <= -10:
        if has_precipitation and wind_speed_knots > 20:
            return "severe"
        elif has_precipitation:
            return "high"
        else:
            return "moderate"
    elif air_temp_c <= -5:
        if has_precipitation:
            return "high"
        else:
            return "moderate"
    elif air_temp_c <= 0:
        if has_precipitation:
            return "moderate"
        else:
            return "low"
    else:  # 0 < temp <= 2
        return "low" if has_precipitation else "none"


def calculate_heat_index(air_temp_c: float, humidity_percent: float) -> float:
    """
    Рассчитать тепловой индекс
    
    Args:
        air_temp_c: Температура воздуха в °C
        humidity_percent: Относительная влажность в %
        
    Returns:
        Тепловой индекс в °C
    """
    # Конвертируем в Фаренгейты для расчета
    temp_f = air_temp_c * 9/5 + 32
    
    # Формула теплового индекса (упрощенная)
    if temp_f >= 80 and humidity_percent >= 40:
        heat_index_f = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity_percent
                       - 0.22475541 * temp_f * humidity_percent
                       - 0.00683783 * temp_f * temp_f
                       - 0.05481717 * humidity_percent * humidity_percent
                       + 0.00122874 * temp_f * temp_f * humidity_percent
                       + 0.00085282 * temp_f * humidity_percent * humidity_percent
                       - 0.00000199 * temp_f * temp_f * humidity_percent * humidity_percent)
        
        # Конвертируем обратно в Цельсий
        heat_index_c = (heat_index_f - 32) * 5/9
        return round(heat_index_c, 1)
    else:
        return air_temp_c


# Константы для экспорта
WEATHER_CONDITIONS = {
    "visibility": VISIBILITY_SCALE,
    "precipitation": PRECIPITATION_TYPES,
    "cloud_cover": CLOUD_COVER,
    "beaufort": BEAUFORT_SCALE,
    "phenomena": WEATHER_PHENOMENA
}


# Экспорт основных элементов
__all__ = [
    'WEATHER_CONDITIONS',
    'VISIBILITY_SCALE',
    'PRECIPITATION_TYPES',
    'CLOUD_COVER',
    'BEAUFORT_SCALE',
    'WEATHER_PHENOMENA',
    'WeatherConditions',
    'get_visibility_by_distance',
    'get_beaufort_by_wind_speed',
    'calculate_wind_chill',
    'estimate_icing_risk',
    'calculate_heat_index'
]


# Тестирование модуля
if __name__ == "__main__":
    print("Тестирование модуля weather_conditions.py")
    print("=" * 50)
    
    # Создаем объект погодных условий
    weather = WeatherConditions()
    weather.set_visibility("moderate")
    weather.set_precipitation("light_rain")
    weather.set_cloud_cover(6)
    weather.set_wind(5)
    weather.add_phenomenon("mist")
    weather.air_temp_c = 10
    weather.water_temp_c = 8
    weather.humidity_percent = 85
    weather.pressure_hpa = 1013
    
    # Выводим отчет
    print(weather.format_weather_report())
    
    # Тесты функций
    print("\n" + "=" * 50)
    print("Тесты вспомогательных функций:")
    
    # Тест определения видимости
    print(f"\n5 миль видимость: {get_visibility_by_distance(5)}")
    print(f"0.3 мили видимость: {get_visibility_by_distance(0.3)}")
    
    # Тест Бофорта
    print(f"\n15 узлов ветер: Бофорт {get_beaufort_by_wind_speed(15)}")
    print(f"35 узлов ветер: Бофорт {get_beaufort_by_wind_speed(35)}")
    
    # Тест wind chill
    print(f"\nWind chill (0°C, 20 узлов): {calculate_wind_chill(0, 20)}°C")
    print(f"Wind chill (-10°C, 30 узлов): {calculate_wind_chill(-10, 30)}°C")
    
    # Тест риска обледенения
    print(f"\nРиск обледенения (-5°C, дождь, 25 узлов): "
          f"{estimate_icing_risk(-5, 'light_rain', 25)}")
    
    # Тест теплового индекса
    print(f"\nТепловой индекс (30°C, 70% влажность): "
          f"{calculate_heat_index(30, 70)}°C")
