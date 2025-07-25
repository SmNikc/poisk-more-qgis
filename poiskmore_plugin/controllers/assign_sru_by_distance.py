from qgis.core import (
    QgsVectorLayer, QgsFeatureIterator, QgsSpatialIndex,
    QgsPointXY, QgsFeature, QgsFeatureRequest
# )
from PyQt5.QtWidgets import QMessageBox

def assign_sru_by_distance(region_layer: QgsVectorLayer, sru_layer: QgsVectorLayer):
    if not region_layer or not sru_layer:
        QMessageBox.warning(None, "Ошибка", "Один из слоев пуст или не инициализирован!")
        return

    sru_index = QgsSpatialIndex(sru_layer.getFeatures())
    request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)

    for region_feat in region_layer.getFeatures():
        region_centroid = region_feat.geometry().centroid()
        nearest_ids = sru_index.nearestNeighbor(region_centroid, 1)

        if nearest_ids:
            nearest_feat = sru_layer.getFeature(nearest_ids[0])
            region_feat.setAttribute("assigned_sru", nearest_feat.attribute("name"))
            region_layer.updateFeature(region_feat)
        else:
            QMessageBox.warning(
                None,
                "Предупреждение",
                f"Нет ближайших SRU для региона ID {region_feat.id()}"
            )

    region_layer.commitChanges()