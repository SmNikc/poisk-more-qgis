from PyQt5.QtCore import QTimer
from qgis.core import QgsProject
from math import cos, sin, radians
class AutoUpdater:
def __init__(self, iface, interval_ms=3600000):
self.iface = iface
self.timer = QTimer()
self.timer.timeout.connect(self.update_area)
self.timer.start(interval_ms)
def update_area(self):
layer = QgsProject.instance().mapLayersByName("Район поиска")
if layer:
layer = layer[0]
wind_speed = 5.0
wind_dir = 0.0
layer.startEditing()
for feat in layer.getFeatures():
geom = feat.geometry()
dx = wind_speed * cos(radians(wind_dir)) * 0.01
dy = wind_speed * sin(radians(wind_dir)) * 0.01
new_geom = geom.translate(dx, dy)
feat.setGeometry(new_geom)
layer.updateFeature(feat)
layer.commitChanges()
layer.triggerRepaint()