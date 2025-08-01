# Пересечение зон. Улучшен: Использование
# QgsSpatialIndex для оптимизации.

from qgis.core import QgsVectorLayer, QgsSpatialIndex, QgsFeature

def check_zone_intersections(layer1: QgsVectorLayer, layer2: QgsVectorLayer):
    index = QgsSpatialIndex(layer2.getFeatures())
    intersections = []

    for feat1 in layer1.getFeatures():
        candidates = index.intersects(feat1.geometry().boundingBox())
        for cand_id in candidates:
            feat2 = layer2.getFeature(cand_id)
            if feat1.geometry().intersects(feat2.geometry()):
                intersections.append((feat1.id(), feat2.id()))

    return intersections