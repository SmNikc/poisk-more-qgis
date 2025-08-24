#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль: search_object_types.py
Описание: Классификация объектов поиска для SAR операций
Автор: Claude AI
Дата создания: 2025-08-24
Версия: 1.0.0

Содержит типы судов, плавсредств, характеристики людей в воде,
коэффициенты обнаружения согласно IAMSAR Manual
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


# Типы судов и плавательных средств
VESSEL_TYPES = {
    "merchant_large": {
        "description": "Крупное торговое судно",
        "description_en": "Large merchant vessel",
        "length_m": (150, 400),
        "draft_m": (8, 20),
        "freeboard_m": (5, 15),
        "radar_cross_section": "excellent",
        "visual_detection_nm": 10,
        "leeway_factor": 0.02,
        "typical_crew": (15, 30),
        "survival_equipment": "full",
        "color_typical": ["grey", "black", "blue", "red"]
    },
    "merchant_medium": {
        "description": "Среднее торговое судно",
        "description_en": "Medium merchant vessel",
        "length_m": (50, 150),
        "draft_m": (4, 8),
        "freeboard_m": (3, 5),
        "radar_cross_section": "good",
        "visual_detection_nm": 7,
        "leeway_factor": 0.025,
        "typical_crew": (8, 15),
        "survival_equipment": "full",
        "color_typical": ["grey", "white", "blue"]
    },
    "merchant_small": {
        "description": "Малое торговое судно",
        "description_en": "Small merchant vessel",
        "length_m": (20, 50),
        "draft_m": (2, 4),
        "freeboard_m": (1, 3),
        "radar_cross_section": "moderate",
        "visual_detection_nm": 5,
        "leeway_factor": 0.03,
        "typical_crew": (3, 8),
        "survival_equipment": "basic",
        "color_typical": ["white", "blue", "grey"]
    },
    "fishing_trawler": {
        "description": "Рыболовный траулер",
        "description_en": "Fishing trawler",
        "length_m": (20, 80),
        "draft_m": (3, 6),
        "freeboard_m": (2, 4),
        "radar_cross_section": "good",
        "visual_detection_nm": 6,
        "leeway_factor": 0.035,
        "typical_crew": (5, 20),
        "survival_equipment": "moderate",
        "color_typical": ["white", "blue", "green", "rust"]
    },
    "fishing_small": {
        "description": "Малое рыболовное судно",
        "description_en": "Small fishing vessel",
        "length_m": (5, 20),
        "draft_m": (0.5, 3),
        "freeboard_m": (0.5, 2),
        "radar_cross_section": "poor",
        "visual_detection_nm": 3,
        "leeway_factor": 0.04,
        "typical_crew": (1, 5),
        "survival_equipment": "minimal",
        "color_typical": ["white", "blue", "wood"]
    },
    "yacht_sail": {
        "description": "Парусная яхта",
        "description_en": "Sailing yacht",
        "length_m": (8, 25),
        "draft_m": (1.5, 3),
        "freeboard_m": (0.5, 1.5),
        "radar_cross_section": "poor",
        "visual_detection_nm": 4,
        "leeway_factor": 0.05,
        "typical_crew": (1, 8),
        "survival_equipment": "moderate",
        "color_typical": ["white", "blue"]
    },
    "yacht_motor": {
        "description": "Моторная яхта",
        "description_en": "Motor yacht",
        "length_m": (8, 50),
        "draft_m": (1, 3),
        "freeboard_m": (1, 3),
        "radar_cross_section": "moderate",
        "visual_detection_nm": 5,
        "leeway_factor": 0.035,
        "typical_crew": (2, 10),
        "survival_equipment": "good",
        "color_typical": ["white", "cream", "blue"]
    },
    "speedboat": {
        "description": "Скоростной катер",
        "description_en": "Speedboat",
        "length_m": (4, 12),
        "draft_m": (0.3, 1),
        "freeboard_m": (0.3, 0.8),
        "radar_cross_section": "poor",
        "visual_detection_nm": 2,
        "leeway_factor": 0.04,
        "typical_crew": (1, 6),
        "survival_equipment": "minimal",
        "color_typical": ["white", "red", "blue", "yellow"]
    },
    "submarine": {
        "description": "Подводная лодка",
        "description_en": "Submarine",
        "length_m": (50, 170),
        "draft_m": (5, 15),
        "freeboard_m": (0.5, 2),  # На поверхности
        "radar_cross_section": "poor",  # На поверхности
        "visual_detection_nm": 3,
        "leeway_factor": 0.02,
        "typical_crew": (20, 150),
        "survival_equipment": "specialized",
        "color_typical": ["black", "dark_grey"]
    },
    "warship": {
        "description": "Военный корабль",
        "description_en": "Warship",
        "length_m": (50, 350),
        "draft_m": (4, 12),
        "freeboard_m": (3, 10),
        "radar_cross_section": "excellent",
        "visual_detection_nm": 8,
        "leeway_factor": 0.025,
        "typical_crew": (50, 500),
        "survival_equipment": "full",
        "color_typical": ["grey", "dark_grey"]
    }
}

# Спасательные средства
SURVIVAL_CRAFT = {
    "life_raft_20": {
        "description": "Спасательный плот на 20+ человек",
        "description_en": "20+ person life raft",
        "size_m": (4, 6),
        "height_m": 0.8,
        "color": ["orange", "yellow"],
        "radar_reflector": True,
        "visual_detection_nm": 2,
        "radar_cross_section": "moderate",
        "leeway_factor": 0.05,
        "drift_factor": 0.03,
        "survival_time_hours": 168  # 7 дней
    },
    "life_raft_10": {
        "description": "Спасательный плот на 10 человек",
        "description_en": "10 person life raft",
        "size_m": (3, 4),
        "height_m": 0.6,
        "color": ["orange", "yellow"],
        "radar_reflector": True,
        "visual_detection_nm": 1.5,
        "radar_cross_section": "poor",
        "leeway_factor": 0.055,
        "drift_factor": 0.035,
        "survival_time_hours": 168
    },
    "life_raft_4": {
        "description": "Спасательный плот на 4 человека",
        "description_en": "4 person life raft",
        "size_m": (2, 2.5),
        "height_m": 0.5,
        "color": ["orange", "yellow"],
        "radar_reflector": False,
        "visual_detection_nm": 1,
        "radar_cross_section": "very_poor",
        "leeway_factor": 0.06,
        "drift_factor": 0.04,
        "survival_time_hours": 72
    },
    "lifeboat": {
        "description": "Спасательная шлюпка",
        "description_en": "Lifeboat",
        "size_m": (4, 8),
        "height_m": 2,
        "color": ["orange", "white"],
        "radar_reflector": True,
        "visual_detection_nm": 3,
        "radar_cross_section": "moderate",
        "leeway_factor": 0.04,
        "drift_factor": 0.025,
        "survival_time_hours": 240  # 10 дней
    },
    "dinghy": {
        "description": "Надувная лодка",
        "description_en": "Inflatable dinghy",
        "size_m": (2, 4),
        "height_m": 0.4,
        "color": ["grey", "black", "orange"],
        "radar_reflector": False,
        "visual_detection_nm": 1,
        "radar_cross_section": "very_poor",
        "leeway_factor": 0.06,
        "drift_factor": 0.045,
        "survival_time_hours": 48
    }
}

# Люди в воде
PERSON_IN_WATER = {
    "with_lifejacket": {
        "description": "Человек в спасательном жилете",
        "description_en": "Person in lifejacket",
        "profile_m2": 0.5,
        "color": ["orange", "yellow", "red"],
        "visual_detection_nm": 0.5,
        "radar_cross_section": "none",
        "leeway_factor": 0.07,
        "drift_factor": 0.05,
        "survival_time": {
            # Температура воды -> время выживания (часы)
            -2: 0.25,
            0: 0.5,
            5: 1,
            10: 2,
            15: 6,
            20: 12,
            25: 24,
            30: 48
        }
    },
    "without_lifejacket": {
        "description": "Человек без спасательного жилета",
        "description_en": "Person without lifejacket",
        "profile_m2": 0.3,
        "color": ["skin", "clothing"],
        "visual_detection_nm": 0.25,
        "radar_cross_section": "none",
        "leeway_factor": 0.06,
        "drift_factor": 0.04,
        "survival_time": {
            -2: 0.08,
            0: 0.25,
            5: 0.5,
            10: 1,
            15: 2,
            20: 6,
            25: 12,
            30: 24
        }
    },
    "with_immersion_suit": {
        "description": "Человек в гидрокостюме",
        "description_en": "Person in immersion suit",
        "profile_m2": 0.6,
        "color": ["orange", "red"],
        "visual_detection_nm": 0.75,
        "radar_cross_section": "very_poor",
        "leeway_factor": 0.065,
        "drift_factor": 0.045,
        "survival_time": {
            -2: 2,
            0: 6,
            5: 12,
            10: 24,
            15: 48,
            20: 72,
            25: 96,
            30: 120
        }
    }
}

# Обломки и прочие объекты
DEBRIS_TYPES = {
    "large_debris": {
        "description": "Крупные обломки",
        "description_en": "Large debris",
        "size_m": (2, 10),
        "visual_detection_nm": 2,
        "radar_cross_section": "poor",
        "leeway_factor": 0.04,
        "drift_factor": 0.03
    },
    "small_debris": {
        "description": "Мелкие обломки",
        "description_en": "Small debris",
        "size_m": (0.5, 2),
        "visual_detection_nm": 0.5,
        "radar_cross_section": "very_poor",
        "leeway_factor": 0.05,
        "drift_factor": 0.04
    },
    "oil_slick": {
        "description": "Нефтяное пятно",
        "description_en": "Oil slick",
        "size_m": (10, 1000),
        "visual_detection_nm": 3,
        "radar_cross_section": "none",
        "leeway_factor": 0.02,
        "drift_factor": 0.02
    },
    "cargo_container": {
        "description": "Грузовой контейнер",
        "description_en": "Cargo container",
        "size_m": (6, 12),
        "visual_detection_nm": 3,
        "radar_cross_section": "good",
        "leeway_factor": 0.03,
        "drift_factor": 0.025
    },
    "floating_object": {
        "description": "Плавающий предмет",
        "description_en": "Floating object",
        "size_m": (0.1, 1),
        "visual_detection_nm": 0.25,
        "radar_cross_section": "none",
        "leeway_factor": 0.06,
        "drift_factor": 0.05
    }
}

# Воздушные суда
AIRCRAFT_TYPES = {
    "airliner": {
        "description": "Пассажирский самолет",
        "description_en": "Airliner",
        "length_m": (30, 80),
        "wingspan_m": (30, 80),
        "typical_passengers": (100, 500),
        "debris_field_nm": 5,
        "survival_equipment": "slides_rafts",
        "color_typical": ["white", "blue", "grey"]
    },
    "small_aircraft": {
        "description": "Малый самолет",
        "description_en": "Small aircraft",
        "length_m": (6, 15),
        "wingspan_m": (8, 20),
        "typical_passengers": (1, 10),
        "debris_field_nm": 1,
        "survival_equipment": "minimal",
        "color_typical": ["white", "blue", "red"]
    },
    "helicopter": {
        "description": "Вертолет",
        "description_en": "Helicopter",
        "length_m": (10, 20),
        "rotor_diameter_m": (10, 20),
        "typical_passengers": (2, 20),
        "debris_field_nm": 0.5,
        "survival_equipment": "moderate",
        "color_typical": ["red", "yellow", "blue", "military"]
    }
}

# Коэффициенты обнаружения (POD - Probability of Detection)
DETECTION_FACTORS = {
    "visual": {
        # Визуальное обнаружение с высоты (вертолет/самолет)
        "excellent_conditions": {
            "large_vessel": 0.95,
            "medium_vessel": 0.90,
            "small_vessel": 0.80,
            "life_raft": 0.70,
            "person_with_lifejacket": 0.40,
            "person_without_lifejacket": 0.20,
            "debris": 0.60
        },
        "good_conditions": {
            "large_vessel": 0.85,
            "medium_vessel": 0.75,
            "small_vessel": 0.65,
            "life_raft": 0.50,
            "person_with_lifejacket": 0.25,
            "person_without_lifejacket": 0.10,
            "debris": 0.40
        },
        "moderate_conditions": {
            "large_vessel": 0.70,
            "medium_vessel": 0.60,
            "small_vessel": 0.45,
            "life_raft": 0.35,
            "person_with_lifejacket": 0.15,
            "person_without_lifejacket": 0.05,
            "debris": 0.25
        },
        "poor_conditions": {
            "large_vessel": 0.40,
            "medium_vessel": 0.30,
            "small_vessel": 0.20,
            "life_raft": 0.15,
            "person_with_lifejacket": 0.05,
            "person_without_lifejacket": 0.01,
            "debris": 0.10
        }
    },
    "radar": {
        # Радиолокационное обнаружение
        "excellent": 0.95,
        "good": 0.80,
        "moderate": 0.60,
        "poor": 0.30,
        "very_poor": 0.10,
        "none": 0.00
    },
    "infrared": {
        # Инфракрасное обнаружение (FLIR)
        "person_in_water": {
            "day": 0.60,
            "night": 0.80
        },
        "life_raft": {
            "day": 0.70,
            "night": 0.85
        },
        "vessel": {
            "day": 0.90,
            "night": 0.95
        }
    }
}

# Объединенный словарь всех объектов поиска
SEARCH_OBJECTS = {
    "vessels": VESSEL_TYPES,
    "survival_craft": SURVIVAL_CRAFT,
    "persons": PERSON_IN_WATER,
    "debris": DEBRIS_TYPES,
    "aircraft": AIRCRAFT_TYPES
}


class SearchObject:
    """Класс для работы с объектами поиска"""
    
    def __init__(self, object_type: str, category: str = "vessels"):
        """
        Инициализация объекта поиска
        
        Args:
            object_type: Тип объекта
            category: Категория (vessels, survival_craft, persons, debris, aircraft)
        """
        self.category = category
        self.object_type = object_type
        self.characteristics = None
        
        if category in SEARCH_OBJECTS and object_type in SEARCH_OBJECTS[category]:
            self.characteristics = SEARCH_OBJECTS[category][object_type]
    
    def get_leeway_factor(self) -> float:
        """Получить коэффициент сноса ветром"""
        if self.characteristics and "leeway_factor" in self.characteristics:
            return self.characteristics["leeway_factor"]
        return 0.03  # Значение по умолчанию
    
    def get_drift_factor(self) -> float:
        """Получить коэффициент дрейфа"""
        if self.characteristics and "drift_factor" in self.characteristics:
            return self.characteristics["drift_factor"]
        return 0.02  # Значение по умолчанию
    
    def get_visual_detection_range(self) -> float:
        """Получить дальность визуального обнаружения в милях"""
        if self.characteristics and "visual_detection_nm" in self.characteristics:
            return self.characteristics["visual_detection_nm"]
        return 1.0  # Значение по умолчанию
    
    def get_radar_cross_section(self) -> str:
        """Получить радиолокационную заметность"""
        if self.characteristics and "radar_cross_section" in self.characteristics:
            return self.characteristics["radar_cross_section"]
        return "poor"
    
    def calculate_drift(self, wind_speed: float, current_speed: float, 
                       hours: float) -> Tuple[float, float]:
        """
        Рассчитать снос объекта
        
        Args:
            wind_speed: Скорость ветра (узлы)
            current_speed: Скорость течения (узлы)
            hours: Время дрейфа (часы)
            
        Returns:
            (снос от ветра, снос от течения) в милях
        """
        leeway = wind_speed * self.get_leeway_factor() * hours
        current_drift = current_speed * self.get_drift_factor() * hours
        
        return (leeway, current_drift)
    
    def get_survival_time(self, water_temp_c: float) -> float:
        """
        Получить время выживания (для людей в воде)
        
        Args:
            water_temp_c: Температура воды в °C
            
        Returns:
            Время выживания в часах
        """
        if self.category != "persons":
            return 999  # Не применимо
        
        if "survival_time" not in self.characteristics:
            return 1.0
        
        survival_times = self.characteristics["survival_time"]
        
        # Находим ближайшие температуры
        temps = sorted(survival_times.keys())
        
        for i, temp in enumerate(temps):
            if water_temp_c <= temp:
                if i == 0:
                    return survival_times[temp]
                else:
                    # Интерполяция
                    temp_low = temps[i-1]
                    temp_high = temp
                    time_low = survival_times[temp_low]
                    time_high = survival_times[temp_high]
                    
                    ratio = (water_temp_c - temp_low) / (temp_high - temp_low)
                    return time_low + ratio * (time_high - time_low)
        
        # Если температура выше максимальной
        return survival_times[temps[-1]]


def get_object_characteristics(object_type: str, category: str = None) -> Dict:
    """
    Получить характеристики объекта поиска
    
    Args:
        object_type: Тип объекта
        category: Категория (если None, ищет во всех)
        
    Returns:
        Словарь с характеристиками
    """
    if category:
        if category in SEARCH_OBJECTS and object_type in SEARCH_OBJECTS[category]:
            return SEARCH_OBJECTS[category][object_type]
    else:
        # Поиск во всех категориях
        for cat, objects in SEARCH_OBJECTS.items():
            if object_type in objects:
                return objects[object_type]
    
    return {}


def calculate_search_area(object_type: str, 
                         elapsed_hours: float,
                         wind_speed: float,
                         current_speed: float,
                         position_error_nm: float = 1.0) -> float:
    """
    Рассчитать площадь района поиска
    
    Args:
        object_type: Тип объекта
        elapsed_hours: Прошедшее время (часы)
        wind_speed: Скорость ветра (узлы)
        current_speed: Скорость течения (узлы)
        position_error_nm: Ошибка начальной позиции (мили)
        
    Returns:
        Площадь района поиска (кв. мили)
    """
    # Создаем объект
    search_obj = SearchObject(object_type)
    
    # Рассчитываем дрейф
    leeway, current_drift = search_obj.calculate_drift(
        wind_speed, current_speed, elapsed_hours
    )
    
    # Общий дрейф
    total_drift = (leeway**2 + current_drift**2) ** 0.5
    
    # Добавляем ошибку позиции и неопределенность дрейфа
    uncertainty = position_error_nm + total_drift * 0.3
    
    # Площадь круга поиска
    import math
    radius = total_drift + uncertainty
    area = math.pi * radius ** 2
    
    return area


def get_detection_probability(object_type: str,
                             conditions: str,
                             detection_method: str = "visual") -> float:
    """
    Получить вероятность обнаружения
    
    Args:
        object_type: Тип объекта
        conditions: Условия (excellent, good, moderate, poor)
        detection_method: Метод обнаружения (visual, radar, infrared)
        
    Returns:
        Вероятность обнаружения (0-1)
    """
    if detection_method == "visual":
        conditions_key = f"{conditions}_conditions"
        if conditions_key in DETECTION_FACTORS["visual"]:
            # Упрощенное соответствие типов объектов
            if "vessel" in object_type:
                if "large" in object_type:
                    return DETECTION_FACTORS["visual"][conditions_key]["large_vessel"]
                elif "medium" in object_type:
                    return DETECTION_FACTORS["visual"][conditions_key]["medium_vessel"]
                else:
                    return DETECTION_FACTORS["visual"][conditions_key]["small_vessel"]
            elif "raft" in object_type:
                return DETECTION_FACTORS["visual"][conditions_key]["life_raft"]
            elif "person" in object_type:
                if "lifejacket" in object_type:
                    return DETECTION_FACTORS["visual"][conditions_key]["person_with_lifejacket"]
                else:
                    return DETECTION_FACTORS["visual"][conditions_key]["person_without_lifejacket"]
            else:
                return DETECTION_FACTORS["visual"][conditions_key].get("debris", 0.3)
    
    elif detection_method == "radar":
        # Получаем радиолокационную заметность объекта
        search_obj = SearchObject(object_type)
        rcs = search_obj.get_radar_cross_section()
        return DETECTION_FACTORS["radar"].get(rcs, 0.1)
    
    elif detection_method == "infrared":
        # Упрощенная логика для ИК обнаружения
        if "person" in object_type:
            return DETECTION_FACTORS["infrared"]["person_in_water"]["day"]
        elif "raft" in object_type:
            return DETECTION_FACTORS["infrared"]["life_raft"]["day"]
        else:
            return DETECTION_FACTORS["infrared"]["vessel"]["day"]
    
    return 0.1  # Значение по умолчанию


def format_object_report(object_type: str, category: str = None) -> str:
    """
    Сформировать отчет об объекте поиска
    
    Args:
        object_type: Тип объекта
        category: Категория объекта
        
    Returns:
        Форматированный отчет
    """
    characteristics = get_object_characteristics(object_type, category)
    
    if not characteristics:
        return f"Объект '{object_type}' не найден в базе данных"
    
    report_lines = [
        "ХАРАКТЕРИСТИКИ ОБЪЕКТА ПОИСКА",
        "=" * 40,
        f"Тип: {characteristics.get('description', 'Неизвестно')}",
        f"Type: {characteristics.get('description_en', 'Unknown')}"
    ]
    
    # Размеры
    if "length_m" in characteristics:
        length = characteristics["length_m"]
        report_lines.append(f"Длина: {length[0]}-{length[1]} м")
    
    if "size_m" in characteristics:
        size = characteristics["size_m"]
        report_lines.append(f"Размер: {size[0]}-{size[1]} м")
    
    # Обнаружение
    if "visual_detection_nm" in characteristics:
        report_lines.append(f"Визуальное обнаружение: {characteristics['visual_detection_nm']} миль")
    
    if "radar_cross_section" in characteristics:
        report_lines.append(f"РЛС заметность: {characteristics['radar_cross_section']}")
    
    # Дрейф
    if "leeway_factor" in characteristics:
        report_lines.append(f"Коэффициент сноса ветром: {characteristics['leeway_factor']}")
    
    if "drift_factor" in characteristics:
        report_lines.append(f"Коэффициент дрейфа: {characteristics['drift_factor']}")
    
    # Выживание
    if "survival_time_hours" in characteristics:
        report_lines.append(f"Время выживания: {characteristics['survival_time_hours']} часов")
    
    if "survival_time" in characteristics:
        report_lines.append("\nВремя выживания в воде:")
        for temp, hours in sorted(characteristics["survival_time"].items()):
            report_lines.append(f"  {temp}°C: {hours} часов")
    
    # Цвета
    if "color" in characteristics:
        colors = ", ".join(characteristics["color"])
        report_lines.append(f"Типичные цвета: {colors}")
    elif "color_typical" in characteristics:
        colors = ", ".join(characteristics["color_typical"])
        report_lines.append(f"Типичные цвета: {colors}")
    
    return "\n".join(report_lines)


# Экспорт основных элементов
__all__ = [
    'SEARCH_OBJECTS',
    'VESSEL_TYPES',
    'SURVIVAL_CRAFT',
    'PERSON_IN_WATER',
    'DEBRIS_TYPES',
    'AIRCRAFT_TYPES',
    'DETECTION_FACTORS',
    'SearchObject',
    'get_object_characteristics',
    'calculate_search_area',
    'get_detection_probability',
    'format_object_report'
]


# Тестирование модуля
if __name__ == "__main__":
    print("Тестирование модуля search_object_types.py")
    print("=" * 50)
    
    # Тест объекта поиска
    obj = SearchObject("life_raft_10", "survival_craft")
    print(f"\nОбъект: Спасательный плот на 10 человек")
    print(f"Коэффициент сноса: {obj.get_leeway_factor()}")
    print(f"Дальность обнаружения: {obj.get_visual_detection_range()} миль")
    print(f"РЛС заметность: {obj.get_radar_cross_section()}")
    
    # Тест расчета дрейфа
    leeway, current = obj.calculate_drift(20, 2, 6)
    print(f"\nДрейф за 6 часов (ветер 20 уз, течение 2 уз):")
    print(f"  Снос ветром: {leeway:.1f} миль")
    print(f"  Снос течением: {current:.1f} миль")
    
    # Тест выживаемости
    person = SearchObject("with_lifejacket", "persons")
    for temp in [0, 10, 20]:
        survival = person.get_survival_time(temp)
        print(f"\nВыживание в воде {temp}°C: {survival:.1f} часов")
    
    # Тест площади поиска
    area = calculate_search_area("life_raft_10", 12, 25, 3, 2)
    print(f"\nПлощадь поиска после 12 часов: {area:.0f} кв. миль")
    
    # Тест вероятности обнаружения
    prob_visual = get_detection_probability("life_raft_10", "good", "visual")
    prob_radar = get_detection_probability("life_raft_10", "good", "radar")
    print(f"\nВероятность обнаружения плота:")
    print(f"  Визуально: {prob_visual:.0%}")
    print(f"  Радаром: {prob_radar:.0%}")
    
    # Пример отчета
    print("\n" + "=" * 50)
    print(format_object_report("merchant_large", "vessels"))
    
    print("\n" + "=" * 50)
    print("Категории объектов в базе данных:")
    for category, objects in SEARCH_OBJECTS.items():
        print(f"\n{category.upper()}:")
        for obj_type in objects.keys():
            print(f"  - {obj_type}")
