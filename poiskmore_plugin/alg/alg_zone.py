from qgis.core import QgsGeometry, QgsFeature, QgsVectorLayer, QgsPointXY, QgsProject, QgsField, QgsFields
from qgis.PyQt.QtCore import QVariant
import math
def create_search_area(params, mode='two_points'):
    """Создание района поиска на основе параметров и режима"""
    # Создание слоя
    layer = QgsVectorLayer("Polygon?crs=epsg:4326", f"Район поиска {params.get('district', '1')}", "memory")
    pr = layer.dataProvider()
    # Добавление полей атрибутов
    fields = QgsFields()
    fields.append(QgsField("district", QVariant.String))
    fields.append(QgsField("prefix", QVariant.String))
    fields.append(QgsField("sru", QVariant.String))
    fields.append(QgsField("duration", QVariant.Int))
    pr.addAttributes(fields)
    layer.updateFields()
    if mode == 'two_points':
        # Расчет от двух исходных точек
        poly = calculate_two_point_area(params)
    elif mode == 'along_line':
        # Вдоль исходной линии
        poly = calculate_line_area(params)
    elif mode == 'distant_points':
        # Далеко разнесенные точки
        poly = calculate_distant_points_area(params)
    elif mode == 'manual_area':
        # Ручное построение
        poly = params.get('polygon')
    elif mode == 'one_point':
        # От одной исходной точки
        poly = calculate_single_point_area(params)
    else:
        # Режим по умолчанию
        points = [QgsPointXY(34.0, 33.0), QgsPointXY(35.0, 34.0), QgsPointXY(35.0, 33.0), QgsPointXY(34.0, 33.0)]
        poly = QgsGeometry.fromPolygonXY([points])
    # Создание feature с атрибутами
    feat = QgsFeature()
    feat.setGeometry(poly)
    feat.setAttributes([
        params.get('district', '1'),
        params.get('prefix', 'A'),
        params.get('sru', 'GNSS'),
        params.get('duration_hours', 10)
    ])
    pr.addFeatures([feat])
    return layer
def calculate_two_point_area(params):
    """Расчет района поиска от двух исходных пунктов"""
    # Базовые координаты (замените на реальные из params)
    lat1, lon1 = 33.0, 34.0  # Первая точка
    lat2, lon2 = 33.5, 34.5  # Вторая точка
    # Упрощенный расчет прямоугольного района
    margin = 0.1  # Запас в градусах
    min_lat = min(lat1, lat2) - margin
    max_lat = max(lat1, lat2) + margin
    min_lon = min(lon1, lon2) - margin
    max_lon = max(lon1, lon2) + margin
    points = [
        QgsPointXY(min_lon, min_lat),
        QgsPointXY(max_lon, min_lat),
        QgsPointXY(max_lon, max_lat),
        QgsPointXY(min_lon, max_lat),
        QgsPointXY(min_lon, min_lat)
    ]
    return QgsGeometry.fromPolygonXY([points])
def calculate_line_area(params):
    """Расчет района поиска вдоль исходной линии"""
    # Создание полосы вдоль линии
    start_point = QgsPointXY(34.0, 33.0)
    end_point = QgsPointXY(35.0, 34.0)
    width = 0.1  # Ширина полосы
    # Упрощенный расчет - прямоугольник вокруг линии
    points = [
        QgsPointXY(start_point.x() - width, start_point.y() - width),
        QgsPointXY(end_point.x() + width, start_point.y() - width),
        QgsPointXY(end_point.x() + width, end_point.y() + width),
        QgsPointXY(start_point.x() - width, end_point.y() + width),
        QgsPointXY(start_point.x() - width, start_point.y() - width)
    ]
    return QgsGeometry.fromPolygonXY([points])
def calculate_distant_points_area(params):
    """Расчет для далеко разнесенных исходных пунктов"""
    # Создание эллиптического района между точками
    center_lat, center_lon = 33.25, 34.25
    a, b = 0.3, 0.2  # Полуоси эллипса
    points = []
    for i in range(36):
        angle = math.radians(i * 10)
        x = center_lon + a * math.cos(angle)
        y = center_lat + b * math.sin(angle)
        points.append(QgsPointXY(x, y))
    points.append(points[0])  # Замыкание полигона
    return QgsGeometry.fromPolygonXY([points])
def calculate_single_point_area(params):
    """Расчет района поиска от одной исходной точки"""
    center_lat, center_lon = 33.0, 34.0
    radius = 0.2  # Радиус в градусах
    points = []
    for i in range(36):
        angle = math.radians(i * 10)
        x = center_lon + radius * math.cos(angle)
        y = center_lat + radius * math.sin(angle)
        points.append(QgsPointXY(x, y))
    points.append(points[0])  # Замыкание полигона
    return QgsGeometry.fromPolygonXY([points])
def add_search_layer(layer):
    """Добавление слоя района поиска в проект"""
    QgsProject.instance().addMapLayer(layer)
    # Настройка стиля слоя (прозрачная заливка, красная граница)
    symbol = layer.renderer().symbol()
    symbol.setColor(QgsProject.instance().readEntry("PoiskMore", "search_area_color", "#FF0000")[0])
    symbol.setOpacity(0.3)
    layer.triggerRepaint()