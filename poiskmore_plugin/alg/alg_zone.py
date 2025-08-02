python from qgis.core import QgsGeometry, QgsPointXY
def create_search_zone(type, center_str): lat, lon = map(float, center_str.split(',')) center = QgsPointXY(lon, lat) if type == 'Круг': return QgsGeometry.fromPointXY(center).buffer(10, 12) # Радиус 10 км elif type == 'Квадрат':
# Логика для квадрата
return QgsGeometry.fromPolylineXY([center, QgsPointXY(lon + 0.1, lat + 0.1)]) # Заглушка return None