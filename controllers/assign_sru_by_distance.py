Назначение SRU. Полный код, улучшен:
использование QgsSpatialIndex для
скорости.
from qgis.core import QgsVectorLayer, QgsFeatureIterator, QgsSpatialIndex, 
QgsPointXY, QgsFeature
from PyQt5.QtWidgets import QMessageBox
def assign_sru_by_distance(region_layer: QgsVectorLayer, sru_layer: QgsVectorLayer):
sru_index = QgsSpatialIndex(sru_layer.getFeatures())
for region_feat in region_layer.getFeatures():
region_centroid = region_feat.geometry().centroid()
nearest_ids = sru_index.nearestNeighbor(region_centroid, 1)
if nearest_ids:
nearest_feat = sru_layer.getFeature(nearest_ids[0])
region_feat.setAttribute("assigned_sru", nearest_feat.attribute("name"))
region_layer.updateFeature(region_feat)
else:
QMessageBox.warning(None, "Предупреждение", "Нет ближайших SRU для региона 
ID " + str(region_feat.id()))
region_layer.commitChanges()
