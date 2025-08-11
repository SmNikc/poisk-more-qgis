from qgis.core import QgsGeometry
def create_region(points):
polygon = QgsGeometry.fromPolygonXY([points])
return polygon