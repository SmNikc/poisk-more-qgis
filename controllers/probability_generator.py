from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsField
from PyQt5.QtCore import QVariant
import random
import math
from qgis.core import QgsProject

def calculate_drift(lat, lon, wind_speed_ms, wind_dir_deg, time_hours, current_speed_ms=0, current_dir_deg=0):
    # Дрейф по ветру (~3% скорости, IAMSAR)
    drift_speed_wind_kmh = wind_speed_ms * 3.6 * 0.03
    drift_dist_wind_km = drift_speed_wind_kmh * time_hours
    dx_wind = drift_dist_wind_km * math.sin(math.radians(wind_dir_deg)) / (111 * math.cos(math.radians(lat)))
    dy_wind = drift_dist_wind_km * math.cos(math.radians(wind_dir_deg)) / 111

    # Дрейф по течению (полная скорость)
    drift_speed_current_kmh = current_speed_ms * 3.6
    drift_dist_current_km = drift_speed_current_kmh * time_hours
    dx_current = drift_dist_current_km * math.sin(math.radians(current_dir_deg)) / (111 * math.cos(math.radians(lat)))
    dy_current = drift_dist_current_km * math.cos(math.radians(current_dir_deg)) / 111

    new_lat = lat + dy_wind + dy_current
    new_lon = lon + dx_wind + dx_current
    return new_lat, new_lon

def generate_probability_points(center: QgsPointXY, radius, count, wind_speed_ms=6, wind_dir_deg=45, time_hours=2, current_speed_ms=0, current_dir_deg=0):
    random.seed(42)
    new_lat, new_lon = calculate_drift(center.y(), center.x(), wind_speed_ms, wind_dir_deg, time_hours, current_speed_ms, current_dir_deg)
    drifted_center = QgsPointXY(new_lon, new_lat)

    layer = QgsVectorLayer("Point?crs=EPSG:4326", "Probability Points", "memory")
    pr = layer.dataProvider()
    pr.addAttributes([QgsField("prob", QVariant.Double)])
    layer.updateFields()

    feats = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, radius)
        dx = dist * math.cos(angle)
        dy = dist * math.sin(angle)
        pt = QgsPointXY(drifted_center.x() + dx, drifted_center.y() + dy)
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(pt))
        feat.setAttributes([random.uniform(0, 1)])
        feats.append(feat)

    pr.addFeatures(feats)
    layer.updateExtents()
    QgsProject.instance().addMapLayer(layer)
    return layer
