from math import cos, sin, radians
from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsFeature,
    QgsFields,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
)


def calculate_datum_points(iface, params):
    """Calculate datum points based on wind and current data."""
    lkp = params.get('lkp', QgsPointXY(30.0, 60.0))
    wind_speed = params.get('wind_speed', 10.0)
    wind_dir = params.get('wind_dir', 0.0)
    current_speed = params.get('current_speed', 2.0)
    current_dir = params.get('current_dir', 90.0)
    time_hours = params.get('time_hours', 3.0)

    leeway_factor = 0.04
    wind_drift_x = wind_speed * cos(radians(wind_dir)) * time_hours * leeway_factor
    wind_drift_y = wind_speed * sin(radians(wind_dir)) * time_hours * leeway_factor
    current_drift_x = current_speed * cos(radians(current_dir)) * time_hours
    current_drift_y = current_speed * sin(radians(current_dir)) * time_hours
    total_drift_x = wind_drift_x + current_drift_x
    total_drift_y = wind_drift_y + current_drift_y
    error_radius = time_hours * 0.1

    datum_min = QgsPointXY(
        lkp.x() + total_drift_x - error_radius,
        lkp.y() + total_drift_y - error_radius,
    )
    datum_max = QgsPointXY(
        lkp.x() + total_drift_x + error_radius,
        lkp.y() + total_drift_y + error_radius,
    )
    datum = QgsPointXY(lkp.x() + total_drift_x, lkp.y() + total_drift_y)
    return [datum_min, datum_max, datum]


def add_datum_layer(points):
    """Add the datum points as a memory layer to the project."""
    layer = QgsVectorLayer("Point?crs=epsg:4326", "Исходные пункты", "memory")
    pr = layer.dataProvider()
    fields = QgsFields()
    fields.append(QgsField("Name", QVariant.String))
    pr.addAttributes(fields)
    layer.updateFields()

    for i, point in enumerate(points):
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(point))
        feat.setAttributes([f"Datum {i+1}"])
        pr.addFeature(feat)

    QgsProject.instance().addMapLayer(layer)
    return layer
