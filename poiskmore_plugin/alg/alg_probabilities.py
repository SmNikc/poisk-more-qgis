from qgis.core import QgsRasterLayer, QgsProject
def generate_probability_map(layer_name, data):
layer = QgsRasterLayer(data, layer_name)
if layer.isValid():
QgsProject.instance().addMapLayer(layer)
return layer
return None