from qgis.core import QgsRasterLayer, QgsProject


def generate_probability_map(layer_name, data):
    """Generate a probability raster layer and add it to the project."""
    layer = QgsRasterLayer(data, layer_name)
    if layer.isValid():
        QgsProject.instance().addMapLayer(layer)
        return layer
    return None
