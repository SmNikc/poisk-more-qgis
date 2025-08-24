#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль: #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль: sea_conditions.py
Описание: Справочник состояний моря, шкала Дугласа, корреляция с Бофортом
Автор: Claude AI
Дата создания: 2025-08-24
Версия: 1.0.0

Содержит международные стандарты оценки состояния моря для SAR операций
"""

from typing import Dict, List, Tuple, Optional


# Шкала Дугласа для состояния моря (Douglas Sea Scale)
# Международный стандарт WMO (World Meteorological Organization)
SEA_CONDITIONS = {
    0: {
        "state": "Calm (glassy)",
        "state_ru": "Зеркально гладкое",
        "wave_height_m": (0, 0),
        "wave_height_ft": (0, 0),
        "description": "Море абсолютно спокойное, поверхность как зеркало",
        "visibility_factor": 1.0,
        "drift_factor": 0.02,
        "search_difficulty": "Отличные условия",
        "beaufort_correlation": [0]
    },
    1: {
        "state": "Calm (rippled)",
        "state_ru": "Рябь",
        "wave_height_m": (0, 0.1),
        "wave_height_ft": (0, 0.33),
        "description": "Легкая рябь на поверхности, без гребней",
        "visibility_factor": 0.95,
        "drift_factor": 0.025,
        "search_difficulty": "Отличные условия",
        "beaufort_correlation": [1, 2]
    },
    2: {
        "state": "Smooth",
        "state_ru": "Слабое волнение",
        "wave_height_m": (0.1, 0.5),
        "wave_height_ft": (0.33, 1.64),
        "description": "Небольшие волны, гребни не опрокидываются",
        "visibility_factor": 0.9,
        "drift_factor": 0.03,
        "search_difficulty": "Хорошие условия",
        "beaufort_correlation": [2, 3]
    },
    3: {
        "state": "Slight",
        "state_ru": "Легкое волнение",
        "wave_height_m": (0.5, 1.25),
        "wave_height_ft": (1.64, 4.1),
        "description": "Небольшие волны с редкими барашками",
        "visibility_factor": 0.85,
        "drift_factor": 0.035,
        "search_difficulty": "Хорошие условия",
        "beaufort_correlation": [3, 4]
    },
    4: {
        "state": "Moderate",
        "state_ru": "Умеренное волнение",
        "wave_height_m": (1.25, 2.5),
        "wave_height_ft": (4.1, 8.2),
        "description": "Умеренные волны, много барашков",
        "visibility_factor": 0.75,
        "drift_factor": 0.04,
        "search_difficulty": "Удовлетворительные условия",
        "beaufort_correlation": [4, 5]
    },
    5: {
        "state": "Rough",
        "state_ru": "Неспокойное море",
        "wave_height_m": (2.5, 4.0),
        "wave_height_ft": (8.2, 13.1),
        "description": "Крупные волны с пенистыми гребнями, брызги",
        "visibility_factor": 0.6,
        "drift_factor": 0.05,
        "search_difficulty": "Сложные условия",
        "beaufort_correlation": [5, 6]
    },
    6: {
        "state": "Very rough",
        "state_ru": "Крупное волнение",
        "wave_height_m": (4.0, 6.0),
        "wave_height_ft": (13.1, 19.7),
        "description": "Море штормит, гребни срываются ветром",
        "visibility_factor": 0.45,
        "drift_factor": 0.06,
        "search_difficulty": "Очень сложные условия",
        "beaufort_correlation": [6, 7]
    },
    7: {
        "state": "High",
        "state_ru": "Очень крупное волнение",
        "wave_height_m": (6.0, 9.0),
        "wave_height_ft": (19.7, 29.5),
        "description": "Высокие волны, пена ложится полосами по ветру",
        "visibility_factor": 0.3,
        "drift_factor": 0.08,
        "search_difficulty": "Крайне сложные условия",
        "beaufort_correlation": [7, 8]
    },
    8: {
        "state": "Very high",
        "state_ru": "Огромное волнение",
        "wave_height_m": (9.0, 14.0),
        "wave_height_ft": (29.5, 45.9),
        "description": "Очень высокие волны, море покрыто пеной",
        "visibility_factor": 0.15,
        "drift_factor": 0.1,
        "search_difficulty": "Практически невозможно",
        "beaufort_correlation": [8, 9, 10]
    },
    9: {
        "state": "Phenomenal",
        "state_ru": "Исключительное волнение",
        "wave_height_m": (14.0, 99.0),  # 99 означает "и выше"
        "wave_height_ft": (45.9, 999),
        "description": "Исключительно высокие волны, воздух наполнен пеной и брызгами",
        "visibility_factor": 0.05,
        "drift_factor": 0.15,
        "search_difficulty": "Невозможно",
        "beaufort_correlation": [11, 12]
    }
}

# Дополнительные параметры для зыби (Swell)
SWELL_CONDITIONS = {
    "low": {
        "height_m": (0, 2),
        "description": "Низкая зыбь",
        "period_sec": (0, 7),
        "impact": "Минимальное влияние на поиск"
    },
    "moderate": {
        "height_m": (2, 4),
        "description": "Умеренная зыбь",
        "period_sec": (7, 11),
        "impact": "Умеренное влияние, возможна качка"
    },
    "heavy": {
        "height_m": (4, 99),
        "description": "Сильная зыбь",
        "period_sec": (11, 99),
        "impact": "Значительное влияние, сильная качка"
    }
}

# Корреляция шкалы Бофорта и Дугласа
BEAUFORT_TO_DOUGLAS = {
    0: [0],           # Штиль
    1: [1],           # Тихий
    2: [1, 2],        # Легкий
    3: [2, 3],        # Слабый
    4: [3, 4],        # Умеренный
    5: [4, 5],        # Свежий
    6: [5, 6],        # Сильный
    7: [6, 7],        # Крепкий
    8: [7],           # Очень крепкий
    9: [8],           # Шторм
    10: [8],          # Сильный шторм
    11: [9],          # Жестокий шторм
    12: [9]           # Ураган
}

# Влияние состояния моря на различные типы объектов поиска
SEA_STATE_IMPACT = {
    "life_raft": {
        # Спасательный плот
        0: {"visibility": 1.0, "drift": 1.0, "survival": 1.0},
        1: {"visibility": 0.95, "drift": 1.05, "survival": 1.0},
        2: {"visibility": 0.9, "drift": 1.1, "survival": 1.0},
        3: {"visibility": 0.85, "drift": 1.15, "survival": 0.95},
        4: {"visibility": 0.75, "drift": 1.2, "survival": 0.9},
        5: {"visibility": 0.6, "drift": 1.3, "survival": 0.85},
        6: {"visibility": 0.45, "drift": 1.4, "survival": 0.75},
        7: {"visibility": 0.3, "drift": 1.5, "survival": 0.6},
        8: {"visibility": 0.15, "drift": 1.7, "survival": 0.4},
        9: {"visibility": 0.05, "drift": 2.0, "survival": 0.2}
    },
    "person_in_water": {
        # Человек в воде
        0: {"visibility": 1.0, "drift": 1.0, "survival": 1.0},
        1: {"visibility": 0.9, "drift": 1.05, "survival": 0.95},
        2: {"visibility": 0.8, "drift": 1.1, "survival": 0.9},
        3: {"visibility": 0.65, "drift": 1.15, "survival": 0.8},
        4: {"visibility": 0.5, "drift": 1.2, "survival": 0.65},
        5: {"visibility": 0.35, "drift": 1.3, "survival": 0.5},
        6: {"visibility": 0.2, "drift": 1.4, "survival": 0.3},
        7: {"visibility": 0.1, "drift": 1.5, "survival": 0.15},
        8: {"visibility": 0.05, "drift": 1.7, "survival": 0.05},
        9: {"visibility": 0.01, "drift": 2.0, "survival": 0.01}
    },
    "vessel": {
        # Судно
        0: {"visibility": 1.0, "drift": 1.0, "survival": 1.0},
        1: {"visibility": 1.0, "drift": 1.0, "survival": 1.0},
        2: {"visibility": 1.0, "drift": 1.02, "survival": 1.0},
        3: {"visibility": 0.95, "drift": 1.05, "survival": 1.0},
        4: {"visibility": 0.9, "drift": 1.08, "survival": 0.95},
        5: {"visibility": 0.85, "drift": 1.1, "survival": 0.9},
        6: {"visibility": 0.75, "drift": 1.15, "survival": 0.85},
        7: {"visibility": 0.6, "drift": 1.2, "survival": 0.75},
        8: {"visibility": 0.4, "drift": 1.3, "survival": 0.6},
        9: {"visibility": 0.2, "drift": 1.5, "survival": 0.4}
    }
}


def get_sea_state_description(douglas_scale: int) -> Dict:
    """
    Получить полное описание состояния моря по шкале Дугласа
    
    Args:
        douglas_scale: Балл по шкале Дугласа (0-9)
        
    Returns:
        Словарь с параметрами состояния моря
    """
    if douglas_scale not in SEA_CONDITIONS:
        return SEA_CONDITIONS[0]  # По умолчанию - штиль
    
    return SEA_CONDITIONS[douglas_scale]


def get_beaufort_from_douglas(douglas_scale: int) -> List[int]:
    """
    Получить соответствующие баллы по шкале Бофорта
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        
    Returns:
        Список возможных баллов по Бофорту
    """
    if douglas_scale not in SEA_CONDITIONS:
        return [0]
    
    return SEA_CONDITIONS[douglas_scale]["beaufort_correlation"]


def get_douglas_from_beaufort(beaufort_scale: int) -> List[int]:
    """
    Получить соответствующие баллы по шкале Дугласа
    
    Args:
        beaufort_scale: Балл по шкале Бофорта
        
    Returns:
        Список возможных баллов по Дугласу
    """
    if beaufort_scale not in BEAUFORT_TO_DOUGLAS:
        return [0]
    
    return BEAUFORT_TO_DOUGLAS[beaufort_scale]


def calculate_search_width_correction(douglas_scale: int, 
                                      base_width: float) -> float:
    """
    Рассчитать корректировку ширины поиска в зависимости от состояния моря
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        base_width: Базовая ширина поиска (мили)
        
    Returns:
        Скорректированная ширина поиска
    """
    if douglas_scale not in SEA_CONDITIONS:
        return base_width
    
    visibility_factor = SEA_CONDITIONS[douglas_scale]["visibility_factor"]
    return base_width * visibility_factor


def calculate_drift_correction(douglas_scale: int,
                               object_type: str,
                               base_drift: float) -> float:
    """
    Рассчитать корректировку дрейфа объекта
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        object_type: Тип объекта поиска
        base_drift: Базовый дрейф (узлы)
        
    Returns:
        Скорректированный дрейф
    """
    if object_type not in SEA_STATE_IMPACT:
        return base_drift
    
    if douglas_scale not in SEA_STATE_IMPACT[object_type]:
        return base_drift
    
    drift_factor = SEA_STATE_IMPACT[object_type][douglas_scale]["drift"]
    return base_drift * drift_factor


def get_swell_category(height_m: float) -> str:
    """
    Определить категорию зыби по высоте
    
    Args:
        height_m: Высота зыби в метрах
        
    Returns:
        Категория зыби
    """
    if height_m <= 2:
        return "low"
    elif height_m <= 4:
        return "moderate"
    else:
        return "heavy"


def estimate_survival_probability(douglas_scale: int,
                                  object_type: str,
                                  hours_in_water: float,
                                  water_temp_c: float) -> float:
    """
    Оценить вероятность выживания
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        object_type: Тип объекта (person_in_water, life_raft, vessel)
        hours_in_water: Время в воде (часы)
        water_temp_c: Температура воды (°C)
        
    Returns:
        Вероятность выживания (0-1)
    """
    # Базовая выживаемость от состояния моря
    if object_type not in SEA_STATE_IMPACT:
        base_survival = 1.0
    elif douglas_scale not in SEA_STATE_IMPACT[object_type]:
        base_survival = 1.0
    else:
        base_survival = SEA_STATE_IMPACT[object_type][douglas_scale]["survival"]
    
    # Корректировка на температуру воды (для человека)
    if object_type == "person_in_water":
        if water_temp_c < 0:
            temp_factor = 0.1  # Очень холодная вода
        elif water_temp_c < 10:
            temp_factor = 0.3  # Холодная вода
        elif water_temp_c < 15:
            temp_factor = 0.5  # Прохладная вода
        elif water_temp_c < 20:
            temp_factor = 0.7  # Умеренная температура
        else:
            temp_factor = 0.9  # Теплая вода
    else:
        temp_factor = 1.0
    
    # Корректировка на время
    time_factor = max(0, 1 - (hours_in_water / 24))  # Снижение на 1/24 каждый час
    
    # Итоговая вероятность
    survival_probability = base_survival * temp_factor * time_factor
    
    return max(0, min(1, survival_probability))


def get_wave_period_estimate(douglas_scale: int) -> Tuple[float, float]:
    """
    Оценить период волн по состоянию моря
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        
    Returns:
        Кортеж (минимальный период, максимальный период) в секундах
    """
    # Эмпирическая формула: период ≈ 3 * sqrt(длина волны)
    wave_periods = {
        0: (0, 0),
        1: (1, 3),
        2: (3, 5),
        3: (4, 6),
        4: (5, 8),
        5: (6, 10),
        6: (8, 12),
        7: (10, 14),
        8: (12, 16),
        9: (14, 20)
    }
    
    return wave_periods.get(douglas_scale, (0, 0))


def format_sea_state_report(douglas_scale: int,
                            wind_speed_knots: float,
                            swell_height_m: float = 0,
                            swell_direction: int = 0) -> str:
    """
    Сформировать текстовый отчет о состоянии моря
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        wind_speed_knots: Скорость ветра в узлах
        swell_height_m: Высота зыби в метрах
        swell_direction: Направление зыби в градусах
        
    Returns:
        Форматированный отчет
    """
    sea_state = get_sea_state_description(douglas_scale)
    swell_cat = get_swell_category(swell_height_m)
    swell_desc = SWELL_CONDITIONS[swell_cat]["description"]
    
    report = f"""
СОСТОЯНИЕ МОРЯ
==============
Шкала Дугласа: {douglas_scale} - {sea_state['state_ru']}
Высота волн: {sea_state['wave_height_m'][0]:.1f}-{sea_state['wave_height_m'][1]:.1f} м
Описание: {sea_state['description']}
Условия поиска: {sea_state['search_difficulty']}

ЗЫБЬ
====
Категория: {swell_desc}
Высота: {swell_height_m:.1f} м
Направление: {swell_direction}°

ВЛИЯНИЕ НА ОПЕРАЦИЮ
==================
Фактор видимости: {sea_state['visibility_factor']:.0%}
Фактор дрейфа: {sea_state['drift_factor']:.0%}
Скорость ветра: {wind_speed_knots:.1f} узлов
Соответствует Бофорту: {sea_state['beaufort_correlation']}
"""
    
    return report


# Экспорт основных функций
__all__ = [
    'SEA_CONDITIONS',
    'SWELL_CONDITIONS',
    'BEAUFORT_TO_DOUGLAS',
    'SEA_STATE_IMPACT',
    'get_sea_state_description',
    'get_beaufort_from_douglas',
    'get_douglas_from_beaufort',
    'calculate_search_width_correction',
    'calculate_drift_correction',
    'get_swell_category',
    'estimate_survival_probability',
    'get_wave_period_estimate',
    'format_sea_state_report'
]


# Тестирование модуля
if __name__ == "__main__":
    print("Тестирование модуля sea_conditions.py")
    print("=" * 50)
    
    # Тест шкалы Дугласа
    for scale in range(10):
        desc = get_sea_state_description(scale)
        print(f"\nДуглас {scale}: {desc['state_ru']}")
        print(f"  Высота волн: {desc['wave_height_m'][0]}-{desc['wave_height_m'][1]} м")
        print(f"  Видимость: {desc['visibility_factor']:.0%}")
        
    # Тест корреляции с Бофортом
    print("\n" + "=" * 50)
    print("Корреляция Бофорт -> Дуглас:")
    for beaufort in range(13):
        douglas = get_douglas_from_beaufort(beaufort)
        print(f"  Бофорт {beaufort} -> Дуглас {douglas}")
    
    # Тест выживаемости
    print("\n" + "=" * 50)
    print("Вероятность выживания (человек в воде, 10°C):")
    for hours in [1, 3, 6, 12, 24]:
        prob = estimate_survival_probability(4, "person_in_water", hours, 10)
        print(f"  {hours} часов: {prob:.0%}")
    
    # Пример отчета
    print("\n" + "=" * 50)
    print("Пример отчета:")
    print(format_sea_state_report(4, 15, 2.5, 270))
Описание: Справочник состояний моря, шкала Дугласа, корреляция с Бофортом
Автор: Claude AI
Дата создания: 2025-08-24
Версия: 1.0.0

Содержит международные стандарты оценки состояния моря для SAR операций
"""

from typing import Dict, List, Tuple, Optional


# Шкала Дугласа для состояния моря (Douglas Sea Scale)
# Международный стандарт WMO (World Meteorological Organization)
SEA_CONDITIONS = {
    0: {
        "state": "Calm (glassy)",
        "state_ru": "Зеркально гладкое",
        "wave_height_m": (0, 0),
        "wave_height_ft": (0, 0),
        "description": "Море абсолютно спокойное, поверхность как зеркало",
        "visibility_factor": 1.0,
        "drift_factor": 0.02,
        "search_difficulty": "Отличные условия",
        "beaufort_correlation": [0]
    },
    1: {
        "state": "Calm (rippled)",
        "state_ru": "Рябь",
        "wave_height_m": (0, 0.1),
        "wave_height_ft": (0, 0.33),
        "description": "Легкая рябь на поверхности, без гребней",
        "visibility_factor": 0.95,
        "drift_factor": 0.025,
        "search_difficulty": "Отличные условия",
        "beaufort_correlation": [1, 2]
    },
    2: {
        "state": "Smooth",
        "state_ru": "Слабое волнение",
        "wave_height_m": (0.1, 0.5),
        "wave_height_ft": (0.33, 1.64),
        "description": "Небольшие волны, гребни не опрокидываются",
        "visibility_factor": 0.9,
        "drift_factor": 0.03,
        "search_difficulty": "Хорошие условия",
        "beaufort_correlation": [2, 3]
    },
    3: {
        "state": "Slight",
        "state_ru": "Легкое волнение",
        "wave_height_m": (0.5, 1.25),
        "wave_height_ft": (1.64, 4.1),
        "description": "Небольшие волны с редкими барашками",
        "visibility_factor": 0.85,
        "drift_factor": 0.035,
        "search_difficulty": "Хорошие условия",
        "beaufort_correlation": [3, 4]
    },
    4: {
        "state": "Moderate",
        "state_ru": "Умеренное волнение",
        "wave_height_m": (1.25, 2.5),
        "wave_height_ft": (4.1, 8.2),
        "description": "Умеренные волны, много барашков",
        "visibility_factor": 0.75,
        "drift_factor": 0.04,
        "search_difficulty": "Удовлетворительные условия",
        "beaufort_correlation": [4, 5]
    },
    5: {
        "state": "Rough",
        "state_ru": "Неспокойное море",
        "wave_height_m": (2.5, 4.0),
        "wave_height_ft": (8.2, 13.1),
        "description": "Крупные волны с пенистыми гребнями, брызги",
        "visibility_factor": 0.6,
        "drift_factor": 0.05,
        "search_difficulty": "Сложные условия",
        "beaufort_correlation": [5, 6]
    },
    6: {
        "state": "Very rough",
        "state_ru": "Крупное волнение",
        "wave_height_m": (4.0, 6.0),
        "wave_height_ft": (13.1, 19.7),
        "description": "Море штормит, гребни срываются ветром",
        "visibility_factor": 0.45,
        "drift_factor": 0.06,
        "search_difficulty": "Очень сложные условия",
        "beaufort_correlation": [6, 7]
    },
    7: {
        "state": "High",
        "state_ru": "Очень крупное волнение",
        "wave_height_m": (6.0, 9.0),
        "wave_height_ft": (19.7, 29.5),
        "description": "Высокие волны, пена ложится полосами по ветру",
        "visibility_factor": 0.3,
        "drift_factor": 0.08,
        "search_difficulty": "Крайне сложные условия",
        "beaufort_correlation": [7, 8]
    },
    8: {
        "state": "Very high",
        "state_ru": "Огромное волнение",
        "wave_height_m": (9.0, 14.0),
        "wave_height_ft": (29.5, 45.9),
        "description": "Очень высокие волны, море покрыто пеной",
        "visibility_factor": 0.15,
        "drift_factor": 0.1,
        "search_difficulty": "Практически невозможно",
        "beaufort_correlation": [8, 9, 10]
    },
    9: {
        "state": "Phenomenal",
        "state_ru": "Исключительное волнение",
        "wave_height_m": (14.0, 99.0),  # 99 означает "и выше"
        "wave_height_ft": (45.9, 999),
        "description": "Исключительно высокие волны, воздух наполнен пеной и брызгами",
        "visibility_factor": 0.05,
        "drift_factor": 0.15,
        "search_difficulty": "Невозможно",
        "beaufort_correlation": [11, 12]
    }
}

# Дополнительные параметры для зыби (Swell)
SWELL_CONDITIONS = {
    "low": {
        "height_m": (0, 2),
        "description": "Низкая зыбь",
        "period_sec": (0, 7),
        "impact": "Минимальное влияние на поиск"
    },
    "moderate": {
        "height_m": (2, 4),
        "description": "Умеренная зыбь",
        "period_sec": (7, 11),
        "impact": "Умеренное влияние, возможна качка"
    },
    "heavy": {
        "height_m": (4, 99),
        "description": "Сильная зыбь",
        "period_sec": (11, 99),
        "impact": "Значительное влияние, сильная качка"
    }
}

# Корреляция шкалы Бофорта и Дугласа
BEAUFORT_TO_DOUGLAS = {
    0: [0],           # Штиль
    1: [1],           # Тихий
    2: [1, 2],        # Легкий
    3: [2, 3],        # Слабый
    4: [3, 4],        # Умеренный
    5: [4, 5],        # Свежий
    6: [5, 6],        # Сильный
    7: [6, 7],        # Крепкий
    8: [7],           # Очень крепкий
    9: [8],           # Шторм
    10: [8],          # Сильный шторм
    11: [9],          # Жестокий шторм
    12: [9]           # Ураган
}

# Влияние состояния моря на различные типы объектов поиска
SEA_STATE_IMPACT = {
    "life_raft": {
        # Спасательный плот
        0: {"visibility": 1.0, "drift": 1.0, "survival": 1.0},
        1: {"visibility": 0.95, "drift": 1.05, "survival": 1.0},
        2: {"visibility": 0.9, "drift": 1.1, "survival": 1.0},
        3: {"visibility": 0.85, "drift": 1.15, "survival": 0.95},
        4: {"visibility": 0.75, "drift": 1.2, "survival": 0.9},
        5: {"visibility": 0.6, "drift": 1.3, "survival": 0.85},
        6: {"visibility": 0.45, "drift": 1.4, "survival": 0.75},
        7: {"visibility": 0.3, "drift": 1.5, "survival": 0.6},
        8: {"visibility": 0.15, "drift": 1.7, "survival": 0.4},
        9: {"visibility": 0.05, "drift": 2.0, "survival": 0.2}
    },
    "person_in_water": {
        # Человек в воде
        0: {"visibility": 1.0, "drift": 1.0, "survival": 1.0},
        1: {"visibility": 0.9, "drift": 1.05, "survival": 0.95},
        2: {"visibility": 0.8, "drift": 1.1, "survival": 0.9},
        3: {"visibility": 0.65, "drift": 1.15, "survival": 0.8},
        4: {"visibility": 0.5, "drift": 1.2, "survival": 0.65},
        5: {"visibility": 0.35, "drift": 1.3, "survival": 0.5},
        6: {"visibility": 0.2, "drift": 1.4, "survival": 0.3},
        7: {"visibility": 0.1, "drift": 1.5, "survival": 0.15},
        8: {"visibility": 0.05, "drift": 1.7, "survival": 0.05},
        9: {"visibility": 0.01, "drift": 2.0, "survival": 0.01}
    },
    "vessel": {
        # Судно
        0: {"visibility": 1.0, "drift": 1.0, "survival": 1.0},
        1: {"visibility": 1.0, "drift": 1.0, "survival": 1.0},
        2: {"visibility": 1.0, "drift": 1.02, "survival": 1.0},
        3: {"visibility": 0.95, "drift": 1.05, "survival": 1.0},
        4: {"visibility": 0.9, "drift": 1.08, "survival": 0.95},
        5: {"visibility": 0.85, "drift": 1.1, "survival": 0.9},
        6: {"visibility": 0.75, "drift": 1.15, "survival": 0.85},
        7: {"visibility": 0.6, "drift": 1.2, "survival": 0.75},
        8: {"visibility": 0.4, "drift": 1.3, "survival": 0.6},
        9: {"visibility": 0.2, "drift": 1.5, "survival": 0.4}
    }
}


def get_sea_state_description(douglas_scale: int) -> Dict:
    """
    Получить полное описание состояния моря по шкале Дугласа
    
    Args:
        douglas_scale: Балл по шкале Дугласа (0-9)
        
    Returns:
        Словарь с параметрами состояния моря
    """
    if douglas_scale not in SEA_CONDITIONS:
        return SEA_CONDITIONS[0]  # По умолчанию - штиль
    
    return SEA_CONDITIONS[douglas_scale]


def get_beaufort_from_douglas(douglas_scale: int) -> List[int]:
    """
    Получить соответствующие баллы по шкале Бофорта
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        
    Returns:
        Список возможных баллов по Бофорту
    """
    if douglas_scale not in SEA_CONDITIONS:
        return [0]
    
    return SEA_CONDITIONS[douglas_scale]["beaufort_correlation"]


def get_douglas_from_beaufort(beaufort_scale: int) -> List[int]:
    """
    Получить соответствующие баллы по шкале Дугласа
    
    Args:
        beaufort_scale: Балл по шкале Бофорта
        
    Returns:
        Список возможных баллов по Дугласу
    """
    if beaufort_scale not in BEAUFORT_TO_DOUGLAS:
        return [0]
    
    return BEAUFORT_TO_DOUGLAS[beaufort_scale]


def calculate_search_width_correction(douglas_scale: int, 
                                      base_width: float) -> float:
    """
    Рассчитать корректировку ширины поиска в зависимости от состояния моря
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        base_width: Базовая ширина поиска (мили)
        
    Returns:
        Скорректированная ширина поиска
    """
    if douglas_scale not in SEA_CONDITIONS:
        return base_width
    
    visibility_factor = SEA_CONDITIONS[douglas_scale]["visibility_factor"]
    return base_width * visibility_factor


def calculate_drift_correction(douglas_scale: int,
                               object_type: str,
                               base_drift: float) -> float:
    """
    Рассчитать корректировку дрейфа объекта
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        object_type: Тип объекта поиска
        base_drift: Базовый дрейф (узлы)
        
    Returns:
        Скорректированный дрейф
    """
    if object_type not in SEA_STATE_IMPACT:
        return base_drift
    
    if douglas_scale not in SEA_STATE_IMPACT[object_type]:
        return base_drift
    
    drift_factor = SEA_STATE_IMPACT[object_type][douglas_scale]["drift"]
    return base_drift * drift_factor


def get_swell_category(height_m: float) -> str:
    """
    Определить категорию зыби по высоте
    
    Args:
        height_m: Высота зыби в метрах
        
    Returns:
        Категория зыби
    """
    if height_m <= 2:
        return "low"
    elif height_m <= 4:
        return "moderate"
    else:
        return "heavy"


def estimate_survival_probability(douglas_scale: int,
                                  object_type: str,
                                  hours_in_water: float,
                                  water_temp_c: float) -> float:
    """
    Оценить вероятность выживания
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        object_type: Тип объекта (person_in_water, life_raft, vessel)
        hours_in_water: Время в воде (часы)
        water_temp_c: Температура воды (°C)
        
    Returns:
        Вероятность выживания (0-1)
    """
    # Базовая выживаемость от состояния моря
    if object_type not in SEA_STATE_IMPACT:
        base_survival = 1.0
    elif douglas_scale not in SEA_STATE_IMPACT[object_type]:
        base_survival = 1.0
    else:
        base_survival = SEA_STATE_IMPACT[object_type][douglas_scale]["survival"]
    
    # Корректировка на температуру воды (для человека)
    if object_type == "person_in_water":
        if water_temp_c < 0:
            temp_factor = 0.1  # Очень холодная вода
        elif water_temp_c < 10:
            temp_factor = 0.3  # Холодная вода
        elif water_temp_c < 15:
            temp_factor = 0.5  # Прохладная вода
        elif water_temp_c < 20:
            temp_factor = 0.7  # Умеренная температура
        else:
            temp_factor = 0.9  # Теплая вода
    else:
        temp_factor = 1.0
    
    # Корректировка на время
    time_factor = max(0, 1 - (hours_in_water / 24))  # Снижение на 1/24 каждый час
    
    # Итоговая вероятность
    survival_probability = base_survival * temp_factor * time_factor
    
    return max(0, min(1, survival_probability))


def get_wave_period_estimate(douglas_scale: int) -> Tuple[float, float]:
    """
    Оценить период волн по состоянию моря
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        
    Returns:
        Кортеж (минимальный период, максимальный период) в секундах
    """
    # Эмпирическая формула: период ≈ 3 * sqrt(длина волны)
    wave_periods = {
        0: (0, 0),
        1: (1, 3),
        2: (3, 5),
        3: (4, 6),
        4: (5, 8),
        5: (6, 10),
        6: (8, 12),
        7: (10, 14),
        8: (12, 16),
        9: (14, 20)
    }
    
    return wave_periods.get(douglas_scale, (0, 0))


def format_sea_state_report(douglas_scale: int,
                            wind_speed_knots: float,
                            swell_height_m: float = 0,
                            swell_direction: int = 0) -> str:
    """
    Сформировать текстовый отчет о состоянии моря
    
    Args:
        douglas_scale: Балл по шкале Дугласа
        wind_speed_knots: Скорость ветра в узлах
        swell_height_m: Высота зыби в метрах
        swell_direction: Направление зыби в градусах
        
    Returns:
        Форматированный отчет
    """
    sea_state = get_sea_state_description(douglas_scale)
    swell_cat = get_swell_category(swell_height_m)
    swell_desc = SWELL_CONDITIONS[swell_cat]["description"]
    
    report = f"""
СОСТОЯНИЕ МОРЯ
==============
Шкала Дугласа: {douglas_scale} - {sea_state['state_ru']}
Высота волн: {sea_state['wave_height_m'][0]:.1f}-{sea_state['wave_height_m'][1]:.1f} м
Описание: {sea_state['description']}
Условия поиска: {sea_state['search_difficulty']}

ЗЫБЬ
====
Категория: {swell_desc}
Высота: {swell_height_m:.1f} м
Направление: {swell_direction}°

ВЛИЯНИЕ НА ОПЕРАЦИЮ
==================
Фактор видимости: {sea_state['visibility_factor']:.0%}
Фактор дрейфа: {sea_state['drift_factor']:.0%}
Скорость ветра: {wind_speed_knots:.1f} узлов
Соответствует Бофорту: {sea_state['beaufort_correlation']}
"""
    
    return report


# Экспорт основных функций
__all__ = [
    'SEA_CONDITIONS',
    'SWELL_CONDITIONS',
    'BEAUFORT_TO_DOUGLAS',
    'SEA_STATE_IMPACT',
    'get_sea_state_description',
    'get_beaufort_from_douglas',
    'get_douglas_from_beaufort',
    'calculate_search_width_correction',
    'calculate_drift_correction',
    'get_swell_category',
    'estimate_survival_probability',
    'get_wave_period_estimate',
    'format_sea_state_report'
]


# Тестирование модуля
if __name__ == "__main__":
    print("Тестирование модуля sea_conditions.py")
    print("=" * 50)
    
    # Тест шкалы Дугласа
    for scale in range(10):
        desc = get_sea_state_description(scale)
        print(f"\nДуглас {scale}: {desc['state_ru']}")
        print(f"  Высота волн: {desc['wave_height_m'][0]}-{desc['wave_height_m'][1]} м")
        print(f"  Видимость: {desc['visibility_factor']:.0%}")
        
    # Тест корреляции с Бофортом
    print("\n" + "=" * 50)
    print("Корреляция Бофорт -> Дуглас:")
    for beaufort in range(13):
        douglas = get_douglas_from_beaufort(beaufort)
        print(f"  Бофорт {beaufort} -> Дуглас {douglas}")
    
    # Тест выживаемости
    print("\n" + "=" * 50)
    print("Вероятность выживания (человек в воде, 10°C):")
    for hours in [1, 3, 6, 12, 24]:
        prob = estimate_survival_probability(4, "person_in_water", hours, 10)
        print(f"  {hours} часов: {prob:.0%}")
    
    # Пример отчета
    print("\n" + "=" * 50)
    print("Пример отчета:")
    print(format_sea_state_report(4, 15, 2.5, 270))