from qgis.core import QgsPointXY
def calculate_sru_routing(start, end, obstacles):
route = [start, end]
for obs in obstacles:
if obs.intersects(QgsGeometry.fromPolylineXY(route)):
route.append(QgsPointXY(start.x() + 1, start.y() + 1))
return route