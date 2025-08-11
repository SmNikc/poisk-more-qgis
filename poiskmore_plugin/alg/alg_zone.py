from qgis.core import QgsGeometry, QgsFeature, QgsVectorLayer, QgsProject, QgsPointXY
from math import atan2, sin, cos, sqrt
def create_search_area(params, mode='two_points'):
if mode == 'two_points':
point1 = params.get('point1', QgsPointXY(30.0, 60.0))
point2 = params.get('point2', QgsPointXY(30.1, 60.1))
width = params.get('width', 0.2)
dx = point2.x() - point1.x()
dy = point2.y() - point1.y()
length = sqrt(dx**2 + dy**2)
angle = atan2(dy, dx)
half_width = width / 2
offset_x = half_width * sin(angle)
offset_y = half_width * cos(angle)
p1 = QgsPointXY(point1.x() - offset_x, point1.y() + offset_y)
p2 = QgsPointXY(point1.x() + offset_x, point1.y() - offset_y)
p3 = QgsPointXY(point2.x() + offset_x, point2.y() - offset_y)
p4 = QgsPointXY(point2.x() - offset_x, point2.y() + offset_y)
polygon = QgsGeometry.fromPolygonXY([[p1, p2, p3, p4]])
return polygon
if mode == 'along_line':
line = params.get('line', QgsGeometry.fromPolylineXY([QgsPointXY(30.0, 60.0), QgsPointXY(30.1, 60.1)]))
buffer = params.get('buffer', 0.1)
return line.buffer(buffer, 5)
if mode == 'distant_points':
p1 = params.get('p1', QgsPointXY(30.0, 60.0))
p2 = params.get('p2', QgsPointXY(31.0, 61.0))
from alg_distant_points import distant_points_calculation
return distant_points_calculation(p1, p2, params)
if mode == 'manual':
polygon = params.get('polygon', QgsGeometry.fromPolygonXY([[QgsPointXY(30.0, 60.0), QgsPointXY(30.1, 60.0), QgsPointXY(30.1, 60.1), QgsPointXY(30.0, 60.1)]]))
return polygon
if mode == 'one_point':
point = params.get('point', QgsPointXY(30.0, 60.0))
radius = params.get('radius', 0.5)
return point.buffer(radius, 20)
def add_search_layer(area_geom):
layer = QgsVectorLayer("Polygon?crs=epsg:4326", "Район поиска", "memory")
pr = layer.dataProvider()
feat = QgsFeature()
feat.setGeometry(area_geom)
pr.addFeature(feat)
QgsProject.instance().addMapLayer(layer)
return layer