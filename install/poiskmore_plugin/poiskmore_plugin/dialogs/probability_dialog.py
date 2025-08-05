from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic
import os
from ..alg.alg_probabilities import compute_probability_map
from qgis.core import QgsPointXY


class ProbabilityDialog(QDialog):
    """Диалог расчёта карты вероятности."""

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(
            os.path.join(os.path.dirname(__file__), "../forms/ProbabilityForm.ui"),
            self,
        )
        self.buttonGenerate.clicked.connect(self.generate_map)

    def generate_map(self):
        """Формирует карту вероятности и отображает результат пользователю."""
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
            QMessageBox.information(
                self, "Успех", "Карта вероятности сгенерирована"
            )
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
