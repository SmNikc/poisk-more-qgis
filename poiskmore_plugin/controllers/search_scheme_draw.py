from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsProject
def draw_search_scheme(scheme):
layer = QgsVectorLayer("LineString?crs=epsg:4326", "Search Scheme", "memory")
feat = QgsFeature()
feat.setGeometry(QgsGeometry.fromPolylineXY(scheme))
layer.dataProvider().addFeature(feat)
QgsProject.instance().addMapLayer(layer)
return layer