from qgis.core import QgsRasterLayer, QgsProject
def draw_heatmap(data):
layer = QgsRasterLayer(data, "Heatmap")
if layer.isValid():
QgsProject.instance().addMapLayer(layer)
return layer
return None