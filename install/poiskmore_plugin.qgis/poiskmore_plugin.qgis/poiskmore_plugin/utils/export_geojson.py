Экспорт слоя в GeoJSON. Исправлено:
Использован QgsVectorFileWriter вместо
exportNamedStyle.
from qgis.core import QgsVectorLayer, QgsVectorFileWriter
import os
def export_layer_to_geojson(layer: QgsVectorLayer, filename="export.geojson"):
filepath = os.path.join(os.path.expanduser("~"), "Documents", filename)
options = QgsVectorFileWriter.SaveVectorOptions()
options.driverName = "GeoJSON"
error = QgsVectorFileWriter.writeAsVectorFormat(layer, filepath, options)
return error == QgsVectorFileWriter.NoError
