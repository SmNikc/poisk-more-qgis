from qgis.core import QgsGeometry, QgsPointXY


def calculate_sru_route(start, end):
    """Calculate a simple route between two points."""
    points = [start, end]
    route = QgsGeometry.fromPolylineXY(points)
    return route
