from qgis.core import QgsGeometry, QgsPointXY

def is_point_inside_zone(point: QgsPointXY, zone_geom: QgsGeometry):
    if not point or not zone_geom:
        return False
    point_geom = QgsGeometry.fromPointXY(point)
    return zone_geom.contains(point_geom)