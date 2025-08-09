import math
from qgis.core import QgsPointXY, QgsGeometry
from PyQt5.QtCore import QDateTime
def calculate_drift(start_point, wind_data, current_data, time_hours):
    """Расчет дрейфа объекта под воздействием ветра и течения"""
    # Ветровой снос (упрощенная формула)
    wind_factor = 0.033  # Стандартный коэффициент для объектов в воде
    wind_drift_distance = wind_data['speed'] * wind_factor * time_hours
    wind_drift_x = wind_drift_distance * math.sin(math.radians(wind_data['direction']))
    wind_drift_y = wind_drift_distance * math.cos(math.radians(wind_data['direction']))
    # Снос течением
    current_drift_distance = current_data['speed'] * time_hours
    current_drift_x = current_drift_distance * math.sin(math.radians(current_data['direction']))
    current_drift_y = current_drift_distance * math.cos(math.radians(current_data['direction']))
    # Общий снос (сумма векторов)
    total_drift_x = wind_drift_x + current_drift_x
    total_drift_y = wind_drift_y + current_drift_y
    # Перевод в градусы координат (упрощенно)
    lat_offset = total_drift_y / 60.0  # 1 градус = 60 морских миль
    lon_offset = total_drift_x / (60.0 * math.cos(math.radians(start_point.y())))
    # Новое положение
    new_point = QgsPointXY(
        start_point.x() + lon_offset,
        start_point.y() + lat_offset
    )
    return {
        'end_point': new_point,
        'total_distance': math.sqrt(total_drift_x**2 + total_drift_y**2),
        'total_bearing': math.degrees(math.atan2(total_drift_x, total_drift_y)),
        'wind_component': math.sqrt(wind_drift_x**2 + wind_drift_y**2),
        'current_component': math.sqrt(current_drift_x**2 + current_drift_y**2)
    }
def calculate_probability_area(center_point, error_radius, confidence_level=0.95):
    """Расчет области вероятного нахождения объекта"""
    # Коэффициенты для различных уровней достоверности
    confidence_factors = {
        0.50: 0.674,  # 50% - 1 сигма
        0.68: 1.000,  # 68% - 1 сигма
        0.95: 1.960,  # 95% - 2 сигмы
        0.99: 2.576   # 99% - 3 сигмы
    }
    factor = confidence_factors.get(confidence_level, 1.960)
    search_radius = error_radius * factor
    # Создание кругового района вероятности
    points = []
    for i in range(36):
        angle = math.radians(i * 10)
        lat_offset = search_radius * math.cos(angle) / 60.0
        lon_offset = search_radius * math.sin(angle) / (60.0 * math.cos(math.radians(center_point.y())))
        point = QgsPointXY(
            center_point.x() + lon_offset,
            center_point.y() + lat_offset
        )
        points.append(point)
    points.append(points[0])  # Замыкание
    return {
        'geometry': QgsGeometry.fromPolygonXY([points]),
        'radius_nm': search_radius,
        'confidence': confidence_level,
        'area_nm2': math.pi * search_radius**2
    }
def calculate_leeway(object_type, wind_speed, wind_direction):
    """Расчет дрейфа от ветра для различных типов объектов"""
    # Коэффициенты дрейфа для разных объектов (в процентах от скорости ветра)
    leeway_factors = {
        'person_in_water': {'factor': 1.2, 'angle_offset': 15},
        'life_raft_4_person': {'factor': 6.0, 'angle_offset': 10},
        'life_raft_6_person': {'factor': 5.5, 'angle_offset': 12},
        'life_raft_10_person': {'factor': 5.0, 'angle_offset': 15},
        'boat_capsized': {'factor': 2.8, 'angle_offset': 20},
        'debris_light': {'factor': 4.0, 'angle_offset': 25},
        'debris_heavy': {'factor': 1.5, 'angle_offset': 30}
    }
    object_data = leeway_factors.get(object_type, {'factor': 3.0, 'angle_offset': 15})
    # Расчет скорости дрейфа
    leeway_speed = wind_speed * object_data['factor'] / 100.0
    # Направление дрейфа (под углом к ветру)
    leeway_direction = wind_direction + object_data['angle_offset']
    if leeway_direction >= 360:
        leeway_direction -= 360
    return {
        'speed': leeway_speed,
        'direction': leeway_direction,
        'factor_percent': object_data['factor']
    }
def calculate_search_area_coverage(search_pattern, area_geometry, track_spacing, detection_range):
    """Расчет покрытия района поиска заданной схемой"""
    area_size = area_geometry.area()  # В квадратных градусах
    if search_pattern == 'parallel_track':
        # Параллельные галсы
        bbox = area_geometry.boundingBox()
        width = bbox.width()
        height = bbox.height()
        # Количество галсов
        num_tracks = int(height / track_spacing) + 1
        # Эффективная ширина поиска на галс
        effective_width = min(track_spacing, detection_range * 2)
        # Покрытая площадь
        covered_area = num_tracks * width * effective_width
    elif search_pattern == 'expanding_square':
        # Расширяющиеся квадраты
        # Упрощенный расчет - полное покрытие в пределах дальности обнаружения
        search_radius = detection_range / 60.0  # Перевод в градусы
        covered_area = math.pi * search_radius**2
    elif search_pattern == 'sector_search':
        # Секторный поиск
        # Покрытие зависит от количества секторов и дальности
        num_sectors = 8  # Стандартно 8 секторов
        sector_angle = 360 / num_sectors
        search_radius = detection_range / 60.0
        covered_area = math.pi * search_radius**2
    else:
        # По умолчанию
        covered_area = area_size * 0.8  # 80% покрытие
    coverage_percentage = min(100, (covered_area / area_size) * 100)
    return {
        'coverage_percent': coverage_percentage,
        'covered_area': covered_area,
        'total_area': area_size,
        'recommended_time': calculate_search_time(covered_area, 10)  # 10 узлов средняя скорость
    }
def calculate_search_time(area_size, search_speed):
    """Расчет времени поиска"""
    # Упрощенный расчет времени поиска
    area_nm2 = area_size * 3600  # Перевод в морские мили квадратные
    # Эффективная скорость поиска (учитывает маневры, повороты)
    effective_speed = search_speed * 0.7
    # Время = площадь / (скорость * эффективная ширина обзора)
    effective_sweep_width = 2.0  # морских миль
    time_hours = area_nm2 / (effective_speed * effective_sweep_width)
    return max(1, int(time_hours))
def calculate_optimal_track_spacing(detection_range, probability_of_detection):
    """Расчет оптимального расстояния между галсами"""
    # Корректировка дальности обнаружения на вероятность
    if probability_of_detection >= 0.9:
        effective_range = detection_range * 0.9
    elif probability_of_detection >= 0.7:
        effective_range = detection_range * 0.7
    elif probability_of_detection >= 0.5:
        effective_range = detection_range * 0.5
    else:
        effective_range = detection_range * 0.3
    # Оптимальное расстояние между галсами
    optimal_spacing = effective_range * 1.5
    return {
        'spacing_nm': optimal_spacing,
        'detection_range_nm': detection_range,
        'effective_range_nm': effective_range,
        'pod': probability_of_detection
    }
def calculate_cumulative_probability(searches):
    """Расчет кумулятивной вероятности обнаружения при множественных поисках"""
    cumulative_prob = 0.0
    for search in searches:
        individual_prob = search.get('probability', 0.0)
        # Формула: P_cum = P_prev + P_current * (1 - P_prev)
        cumulative_prob = cumulative_prob + individual_prob * (1 - cumulative_prob)
    return min(1.0, cumulative_prob)
def great_circle_distance(point1, point2):
    """Расчет расстояния по большому кругу между двумя точками"""
    # Перевод в радианы
    lat1 = math.radians(point1.y())
    lon1 = math.radians(point1.x())
    lat2 = math.radians(point2.y())
    lon2 = math.radians(point2.x())
    # Формула гаверсинуса
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    # Радиус Земли в морских милях
    earth_radius_nm = 3440.07
    distance = earth_radius_nm * c
    return distance
def calculate_bearing(point1, point2):
    """Расчет пеленга между двумя точками"""
    lat1 = math.radians(point1.y())
    lat2 = math.radians(point2.y())
    dlon = math.radians(point2.x() - point1.x())
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.degrees(math.atan2(y, x))
    # Нормализация к 0-360
    bearing = (bearing + 360) % 360
    return bearing