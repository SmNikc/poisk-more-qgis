from qgis.core import QgsGeometry, QgsFeature, QgsVectorLayer, QgsPointXY, QgsProject, QgsField, QgsFields
from qgis.PyQt.QtCore import QVariant
import math
def distant_points_calculation(iface, params):
    """Расчет районов поиска для далеко разнесенных исходных пунктов"""
    layer = QgsVectorLayer("Polygon?crs=epsg:4326", "Далеко разнесенные районы", "memory")
    pr = layer.dataProvider()
    # Добавление полей атрибутов
    fields = QgsFields()
    fields.append(QgsField("area_id", QVariant.String))
    fields.append(QgsField("area_type", QVariant.String))
    fields.append(QgsField("probability", QVariant.Double))
    fields.append(QgsField("priority", QVariant.Int))
    pr.addAttributes(fields)
    layer.updateFields()
    # Получение исходных точек
    point1 = params.get('point1', QgsPointXY(34.0, 33.0))
    point2 = params.get('point2', QgsPointXY(35.5, 34.5))
    # Расчет расстояния между точками
    distance = calculate_distance(point1, point2)
    if distance > params.get('distance_threshold', 50):  # Если расстояние больше 50 морских миль
        # Создание двух отдельных районов
        areas = create_separate_areas(point1, point2, params)
    else:
        # Создание связующего района
        areas = create_connecting_area(point1, point2, params)
    # Добавление районов в слой
    features = []
    for i, area_data in enumerate(areas):
        feat = QgsFeature()
        feat.setGeometry(area_data['geometry'])
        feat.setAttributes([
            f"DA{i+1}",
            area_data['type'],
            area_data['probability'],
            area_data['priority']
        ])
        features.append(feat)
    pr.addFeatures(features)
    return layer
def calculate_distance(point1, point2):
    """Расчет расстояния между двумя точками в морских милях"""
    # Упрощенный расчет расстояния (заменить на точную формулу)
    lat_diff = abs(point1.y() - point2.y())
    lon_diff = abs(point1.x() - point2.x())
    distance_deg = math.sqrt(lat_diff**2 + lon_diff**2)
    return distance_deg * 60  # Перевод в морские мили (приблизительно)
def create_separate_areas(point1, point2, params):
    """Создание двух отдельных районов поиска"""
    areas = []
    # Радиус поиска для каждого района
    search_radius = params.get('search_radius', 0.2)
    # Район 1
    area1 = create_circular_area(point1, search_radius)
    areas.append({
        'geometry': area1,
        'type': 'Первичный район',
        'probability': 0.6,
        'priority': 1
    })
    # Район 2
    area2 = create_circular_area(point2, search_radius)
    areas.append({
        'geometry': area2,
        'type': 'Вторичный район',
        'probability': 0.4,
        'priority': 2
    })
    return areas
def create_connecting_area(point1, point2, params):
    """Создание связующего района между точками"""
    areas = []
    # Создание эллиптического района, охватывающего обе точки
    center_lat = (point1.y() + point2.y()) / 2
    center_lon = (point1.x() + point2.x()) / 2
    # Расчет размеров эллипса
    lat_diff = abs(point1.y() - point2.y())
    lon_diff = abs(point1.x() - point2.x())
    a = max(lat_diff, lon_diff) / 2 + params.get('margin', 0.1)  # Большая полуось
    b = min(lat_diff, lon_diff) / 2 + params.get('margin', 0.1)  # Малая полуось
    if a < 0.05:  # Минимальный размер
        a = 0.05
    if b < 0.05:
        b = 0.05
    # Создание эллиптического полигона
    ellipse = create_elliptical_area(QgsPointXY(center_lon, center_lat), a, b)
    areas.append({
        'geometry': ellipse,
        'type': 'Связующий район',
        'probability': 0.8,
        'priority': 1
    })
    return areas
def create_circular_area(center, radius):
    """Создание кругового района поиска"""
    points = []
    for i in range(36):
        angle = math.radians(i * 10)
        x = center.x() + radius * math.cos(angle)
        y = center.y() + radius * math.sin(angle)
        points.append(QgsPointXY(x, y))
    points.append(points[0])  # Замыкание полигона
    return QgsGeometry.fromPolygonXY([points])
def create_elliptical_area(center, a, b, rotation=0):
    """Создание эллиптического района поиска"""
    points = []
    for i in range(36):
        angle = math.radians(i * 10)
        # Координаты на эллипсе
        x_ellipse = a * math.cos(angle)
        y_ellipse = b * math.sin(angle)
        # Поворот эллипса
        cos_rot = math.cos(rotation)
        sin_rot = math.sin(rotation)
        x_rotated = x_ellipse * cos_rot - y_ellipse * sin_rot
        y_rotated = x_ellipse * sin_rot + y_ellipse * cos_rot
        # Смещение к центру
        x = center.x() + x_rotated
        y = center.y() + y_rotated
        points.append(QgsPointXY(x, y))
    points.append(points[0])  # Замыкание полигона
    return QgsGeometry.fromPolygonXY([points])
def calculate_probability_distribution(point1, point2, time_elapsed):
    """Расчет распределения вероятности между районами"""
    # Упрощенная модель: вероятность зависит от времени и расстояния
    base_prob1 = 0.6
    base_prob2 = 0.4
    # Коррекция на время (чем больше времени, тем больше неопределенность)
    time_factor = min(1.0, time_elapsed / 24.0)  # Нормализация на 24 часа
    prob1 = base_prob1 * (1 - time_factor * 0.2)
    prob2 = base_prob2 * (1 - time_factor * 0.2)
    # Нормализация
    total = prob1 + prob2
    return prob1 / total, prob2 / total
def optimize_search_pattern(areas, available_resources):
    """Оптимизация схемы поиска для нескольких районов"""
    # Сортировка районов по приоритету и вероятности
    sorted_areas = sorted(areas, key=lambda x: (x['priority'], -x['probability']))
    search_plan = []
    for i, area in enumerate(sorted_areas):
        search_plan.append({
            'area_id': f"DA{i+1}",
            'search_order': i + 1,
            'recommended_pattern': get_search_pattern(area),
            'estimated_time': calculate_search_time(area, available_resources)
        })
    return search_plan
def get_search_pattern(area):
    """Определение оптимальной схемы поиска для района"""
    area_size = area['geometry'].area()
    if area_size < 0.01:  # Малый район
        return "Расширяющиеся квадраты"
    elif area_size < 0.05:  # Средний район
        return "Параллельные галсы"
    else:  # Большой район
        return "Секторный поиск"
def calculate_search_time(area, resources):
    """Расчет времени поиска для района"""
    area_size = area['geometry'].area()
    search_speed = resources.get('search_speed', 10)  # узлов
    coverage_factor = resources.get('coverage_factor', 0.8)
    # Упрощенный расчет времени
    estimated_hours = (area_size * 3600) / (search_speed * coverage_factor)
    return max(1, int(estimated_hours))