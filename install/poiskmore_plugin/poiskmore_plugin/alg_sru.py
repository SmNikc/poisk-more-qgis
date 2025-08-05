pythonimport math
from qgis.core import QgsGeometry, QgsPointXY, QgsFeature, QgsVectorLayer, QgsProject

def calculate_bearing(lat1, lon1, lat2, lon2):
    d_lon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    x = math.sin(d_lon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(d_lon)
    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
    return bearing

def simulate_sru_path(start, end, steps=10):
    path = []
    for i in range(steps + 1):
        t = i / steps
        x = start.x() + (end.x() - start.x()) * t
        y = start.y() + (end.y() - start.y()) * t
        path.append(QgsPointXY(x, y))
    geom = QgsGeometry.fromPolylineXY(path)
    layer = QgsVectorLayer("LineString?crs=epsg:4326", "SRU Path", "memory")
    pr = layer.dataProvider()
    feat = QgsFeature()
    feat.setGeometry(geom)
    pr.addFeature(feat)
    QgsProject.instance().addMapLayer(layer)
    return layer