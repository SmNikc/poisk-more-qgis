pythonfrom qgis.core import QgsGeometry, QgsPointXY, QgsFeature, QgsVectorLayer, QgsProject

def generate_search_zone(lkp, error_radius, method='expanding_square', segments=12):
    center = QgsGeometry.fromPointXY(lkp)
    radius_deg = error_radius / 60
    if method == 'expanding_square':
        points = []
        for i in range(4):
            dx = radius_deg * (i + 1)
            dy = radius_deg * (i + 1)
            points.append(QgsPointXY(lkp.x() - dx, lkp.y() - dy))
            points.append(QgsPointXY(lkp.x() + dx, lkp.y() - dy))
            points.append(QgsPointXY(lkp.x() + dx, lkp.y() + dy))
            points.append(QgsPointXY(lkp.x() - dx, lkp.y() + dy))
        geom = QgsGeometry.fromPolygonXY([points])
    elif method == 'sector':
        points = []
        for angle in range(0, 360, 120):
            x = lkp.x() + radius_deg * math.cos(math.radians(angle))
            y = lkp.y() + radius_deg * math.sin(math.radians(angle))
            points.append(QgsPointXY(x, y))
        points.append(points[0])
        geom = QgsGeometry.fromPolylineXY(points)
    elif method == 'parallel_sweep':
        lines = []
        for i in range(-2, 3):
            start = QgsPointXY(lkp.x() - radius_deg, lkp.y() + i * (radius_deg / 2))
            end = QgsPointXY(lkp.x() + radius_deg, lkp.y() + i * (radius_deg / 2))
            lines.append(QgsGeometry.fromPolylineXY([start, end]))
        geom = QgsGeometry.collectGeometry(lines)
    else:
        return None
    layer = QgsVectorLayer("Polygon?crs=epsg:4326", "Search Zone", "memory")
    pr = layer.dataProvider()
    feat = QgsFeature()
    feat.setGeometry(geom.buffer(radius_deg / 2, segments))  # Дополнительный буфер по ошибке
    pr.addFeature(feat)
    QgsProject.instance().addMapLayer(layer)
    return layer