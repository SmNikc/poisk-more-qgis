from qgis.core import QgsGeometry
def calculate_zone_intersection(zone1, zone2):
intersection = zone1.intersection(zone2)
return intersection