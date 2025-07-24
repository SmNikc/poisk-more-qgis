from qgis.core import QgsFeature, QgsGeometry, QgsPointXY

def create_search_scheme_layer(points, crs):
    interpolated = []
    for i in range(len(points) - 1):
        start = points[i]
        end = points[i + 1]
        steps = 10
        for s in range(steps):
            x = start.x() + (end.x() - start.x()) * s / steps
            y = start.y() + (end.y() - start.y()) * s / steps
            interpolated.append(QgsPointXY(x, y))
    interpolated.append(points[-1])
    geom = QgsGeometry.fromPolylineXY(interpolated)
    return geom
