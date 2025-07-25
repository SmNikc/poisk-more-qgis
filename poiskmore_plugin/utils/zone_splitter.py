# Разделение зоны линией. Улучшен:
# Обработка tuple из splitGeometry,
# проверка типов.
from qgis.core import QgsFeature, QgsGeometry
def split_zone_by_line(zone_feat: QgsFeature, split_geom: QgsGeometry):
# if not isinstance(zone_feat, QgsFeature) or not isinstance(split_geom, QgsGeometry):
# return []
# zone_geom = zone_feat.geometry()
# if not zone_geom.intersects(split_geom):
# return [zone_geom]
# split_result = zone_geom.splitGeometry(split_geom.asPolyline(), False)
# if isinstance(split_result, tuple):
# new_geoms, topology_test = split_result
# return new_geoms
# return []