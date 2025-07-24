from qgis.core import QgsFeature, QgsGeometry, QgsPointXY

def build_route(start_point, end_point):
    steps = 10
    route = []
    for i in range(steps + 1):
        x = start_point.x() + (end_point.x() - start_point.x()) * i / steps
        y = start_point.y() + (end_point.y() - start_point.y()) * i / steps
        route.append(QgsPointXY(x, y))
    return QgsGeometry.fromPolylineXY(route)
