from qgis.core import QgsGeometry, QgsPointXY
from math import pi, cos, sin
def create_advanced_search_area(center, radius, sectors):
points = []
for i in range(sectors):
angle = i * (2 * pi / sectors)
x = center.x() + radius * cos(angle)
y = center.y() + radius * sin(angle)
points.append(QgsPointXY(x, y))
polygon = QgsGeometry.fromPolygonXY([points])
return polygon