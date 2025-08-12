from math import sqrt, atan2, sin, cos
from qgis.core import QgsGeometry, QgsPointXY


def distant_points_calculation(point1, point2, params):
    """Calculate a search area for two distant points."""
    dx = point2.x() - point1.x()
    dy = point2.y() - point1.y()
    distance = sqrt(dx ** 2 + dy ** 2)

    if distance > params.get('threshold', 1.0):
        radius = params.get('radius', 0.5)
        area1 = point1.buffer(radius, 20)
        area2 = point2.buffer(radius, 20)
        angle = atan2(dy, dx)
        half_width = params.get('width', 0.2) / 2
        offset_x = half_width * sin(angle)
        offset_y = half_width * cos(angle)
        rp1 = QgsPointXY(point1.x() - offset_x, point1.y() + offset_y)
        rp2 = QgsPointXY(point1.x() + offset_x, point1.y() - offset_y)
        rp3 = QgsPointXY(point2.x() + offset_x, point2.y() - offset_y)
        rp4 = QgsPointXY(point2.x() - offset_x, point2.y() + offset_y)
        rect = QgsGeometry.fromPolygonXY([[rp1, rp2, rp3, rp4]])
        full_area = area1.combine(rect).combine(area2)
        return full_area
    else:
        center = QgsPointXY((point1.x() + point2.x()) / 2, (point1.y() + point2.y()) / 2)
        major = distance / 2 + params.get('radius', 0.5)
        minor = params.get('minor', 0.3)
        ellipse_points = []
        for i in range(20):
            theta = i * (2 * 3.14159 / 20)
            x = center.x() + major * cos(theta)
            y = center.y() + minor * sin(theta)
            ellipse_points.append(QgsPointXY(x, y))
        ellipse = QgsGeometry.fromPolygonXY([ellipse_points])
        return ellipse
