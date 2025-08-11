from qgis.core import QgsGeometry, QgsPointXY
def calculate_sru_route(start, end):
points = [start, end]
route = QgsGeometry.fromPolylineXY(points)
return route