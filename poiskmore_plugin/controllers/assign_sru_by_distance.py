from qgis.core import QgsPointXY
def assign_sru_by_distance(sru_points, search_areas):
assignments = []
for area in search_areas:
closest_sru = min(sru_points, key=lambda p: p.distance(area.centroid()))
assignments.append((area, closest_sru))
return assignments