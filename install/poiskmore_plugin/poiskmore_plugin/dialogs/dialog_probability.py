from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic
import os
from ..alg.alg_probabilities import compute_probability_map
from qgis.core import QgsPointXY
class ProbabilityDialog(QDialog):
def init(self, parent=None):
super().init(parent)
uic.loadUi(os.path.join(os.path.dirname(file), '../forms/ProbabilityForm.ui'), self)
self.buttonGenerate.clicked.connect(self.generate_map)
def generate_map(self):
try:
lkp_lat = self.spinLkpLat.value()
lkp_lon = self.spinLkpLon.value()
radius = self.spinRadius.value()
resolution = self.spinResolution.value()
wind_speed = self.spinWindSpeed.value()
wind_dir = self.spinWindDir.value()
time = self.spinTime.value()
lkp = QgsPointXY(lkp_lon, lkp_lat)
matrix, layer = compute_probability_map(lkp, radius, resolution, wind_speed, wind_dir, time)
QMessageBox.information(self, "Успех", "Карта вероятности сгенерирована и добавлена как слой")
except ValueError as e:
QMessageBox.warning(self, "Ошибка", str(e))