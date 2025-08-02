"""Диалог для генерации карты вероятности."""

import os
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic
from qgis.core import QgsPointXY

from ..alg.alg_probabilities import compute_probability_map


class ProbabilityDialog(QDialog):
    """Диалог генерации карты вероятности."""

    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "../forms/ProbabilityForm.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
            if hasattr(self, "buttonGenerate"):
                self.buttonGenerate.clicked.connect(self.generate_map)

    def generate_map(self):
        try:
            lkp_lat = self.spinLkpLat.value()
            lkp_lon = self.spinLkpLon.value()
            radius = self.spinRadius.value()
            resolution = self.spinResolution.value()
            wind_speed = self.spinWindSpeed.value()
            wind_dir = self.spinWindDir.value()
            current_speed = self.spinCurrentSpeed.value()
            current_dir = self.spinCurrentDir.value()
            time = self.spinTime.value()
            lkp = QgsPointXY(lkp_lon, lkp_lat)
            compute_probability_map(
                lkp,
                radius,
                resolution,
                wind_speed,
                wind_dir,
                current_speed,
                current_dir,
                time,
            )
            QMessageBox.information(self, "Успех", "Карта вероятности сгенерирована")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

