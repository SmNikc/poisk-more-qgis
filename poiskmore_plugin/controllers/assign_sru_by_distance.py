from qgis.core import (
    QgsVectorLayer,
    QgsSpatialIndex,
    QgsPointXY,
    QgsFeatureRequest,
)
from PyQt5.QtWidgets import QMessageBox


def calculate_distance(point1: QgsPointXY, point2: QgsPointXY) -> float:
    """Return Euclidean distance between two points."""
    dx = point1.x() - point2.x()
    dy = point1.y() - point2.y()
    return (dx ** 2 + dy ** 2) ** 0.5


def assign_sru_by_distance(region_layer: QgsVectorLayer, sru_layer: QgsVectorLayer) -> None:
    """Assign the closest SRU to each region feature."""
    if not region_layer or not sru_layer:
        QMessageBox.warning(None, "Ошибка", "Один из слоев пуст или не инициализирован!")
        return

    sru_index = QgsSpatialIndex(sru_layer.getFeatures())
    request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)

    for region_feat in region_layer.getFeatures():
        region_centroid = region_feat.geometry().centroid().asPoint()
        nearest_ids = sru_index.nearestNeighbor(region_centroid, 1)
        if nearest_ids:
            nearest_feat = sru_layer.getFeature(nearest_ids[0])
            region_feat.setAttribute("assigned_sru", nearest_feat.attribute("name"))
            region_layer.updateFeature(region_feat)
        else:
            QMessageBox.warning(
                None,
                "Предупреждение",
                f"Нет ближайших SRU для региона ID {region_feat.id()}",
            )

    region_layer.commitChanges()