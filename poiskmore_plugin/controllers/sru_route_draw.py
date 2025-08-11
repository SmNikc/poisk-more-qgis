from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsProject
def draw_sru_route(route):
layer = QgsVectorLayer("LineString?crs=epsg:4326", "SRU Route", "memory")
feat = QgsFeature()
feat.setGeometry(route)
layer.dataProvider().addFeature(feat)
QgsProject.instance().addMapLayer(layer)
return layer