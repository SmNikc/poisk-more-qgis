from qgis.core import QgsPointXY, QgsGeometry, QgsFeature, QgsVectorLayer, QgsProject, QgsField, QgsFields
from qgis.PyQt.QtCore import QVariant
import math
def calculate_datum_points(iface, params=None):
    """Расчет исходных пунктов на основе данных об аварии"""
    # Создание слоя точек
    layer = QgsVectorLayer("Point?crs=epsg:4326", "Исходные пункты", "memory")
    pr = layer.dataProvider()
    # Добавление полей атрибутов
    fields = QgsFields()
    fields.append(QgsField("point_id", QVariant.String))
    fields.append(QgsField("type", QVariant.String))
    fields.append(QgsField("confidence", QVariant.Double))
    fields.append(QgsField("time_calc", QVariant.String))
    pr.addAttributes(fields)
    layer.updateFields()
    if params:
        # Расчет на основе реальных параметров
        points = calculate_real_datum_points(params)
    else:
        # Пример точек для демонстрации
        points = [
            {
                'point': QgsPointXY(34.0, 33.0),
                'id': 'LKP1',
                'type': 'Последнее известное местоположение',
                'confidence': 0.8
            },
            {
                'point': QgsPointXY(34.1, 33.1),
                'id': 'CSP1',
                'type': 'Расчетное местоположение',
                'confidence': 0.6
            }
        ]
    # Добавление точек в слой
    features = []
    for point_data in points:
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(point_data['point']))
        feat.setAttributes([
            point_data['id'],
            point_data['type'],
            point_data['confidence'],
            "2025-07-23 10:02"
        ])
        features.append(feat)
    pr.addFeatures(features)
    return layer
def calculate_real_datum_points(params):
    """Расчет исходных пунктов на основе реальных параметров аварии"""
    points = []
    # Последнее известное местоположение (LKP)
    if 'last_known_position' in params:
        lkp = params['last_known_position']
        points.append({
            'point': QgsPointXY(lkp['lon'], lkp['lat']),
            'id': 'LKP',
            'type': 'Последнее известное местоположение',
            'confidence': lkp.get('confidence', 0.9)
        })
    # Расчетное местоположение с учетом дрейфа и течения
    if 'drift_calculation' in params:
        drift = params['drift_calculation']
        # Упрощенный расчет сноса (заменить на реальные формулы)
        drift_distance = drift.get('distance', 0.1)
        drift_bearing = drift.get('bearing', 90)
        # Расчет новых координат с учетом сноса
        lat_offset = drift_distance * math.cos(math.radians(drift_bearing))
        lon_offset = drift_distance * math.sin(math.radians(drift_bearing))
        base_lat = params.get('base_lat', 33.0)
        base_lon = params.get('base_lon', 34.0)
        points.append({
            'point': QgsPointXY(base_lon + lon_offset, base_lat + lat_offset),
            'id': 'CSP',
            'type': 'Расчетное местоположение',
            'confidence': 0.7
        })
    return points
def calculate_datum_line(start_point, end_point, intervals=5):
    """Расчет исходной линии между двумя точками"""
    layer = QgsVectorLayer("LineString?crs=epsg:4326", "Исходная линия", "memory")
    pr = layer.dataProvider()
    # Создание линии
    line = QgsGeometry.fromPolylineXY([start_point, end_point])
    feat = QgsFeature()
    feat.setGeometry(line)
    pr.addFeatures([feat])
    return layer
def add_datum_layer(layer):
    """Добавление слоя исходных пунктов в проект"""
    QgsProject.instance().addMapLayer(layer)
    # Настройка стиля точек (красные круги)
    symbol = layer.renderer().symbol()
    symbol.setSize(5)
    symbol.setColor(QgsProject.instance().readEntry("PoiskMore", "datum_color", "#FF0000")[0])
    layer.triggerRepaint()
def single_datum_calculation(params):
    """Расчет единственного исходного пункта"""
    # Реализация расчета для случая, когда есть только одна достоверная точка
    confidence_threshold = params.get('confidence_threshold', 0.8)
    # Выбор наиболее достоверной точки
    best_point = None
    max_confidence = 0
    for point_data in params.get('candidate_points', []):
        if point_data['confidence'] > max_confidence and point_data['confidence'] >= confidence_threshold:
            max_confidence = point_data['confidence']
            best_point = point_data
    if best_point:
        return [best_point]
    else:
        # Если нет достаточно достоверных точек, использовать среднее
        return calculate_average_point(params.get('candidate_points', []))
def calculate_average_point(points):
    """Расчет средней точки из нескольких кандидатов"""
    if not points:
        return []
    avg_lat = sum(p['point'].y() for p in points) / len(points)
    avg_lon = sum(p['point'].x() for p in points) / len(points)
    avg_confidence = sum(p['confidence'] for p in points) / len(points)
    return [{
        'point': QgsPointXY(avg_lon, avg_lat),
        'id': 'AVG',
        'type': 'Средняя точка',
        'confidence': avg_confidence
    }]
Продолжать публикацию остальных файлов?
да, прошу опубликовать также обработав ВСЕ