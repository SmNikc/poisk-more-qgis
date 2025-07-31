pythonfrom PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from alg_sru import simulate_sru_path, calculate_bearing
from alg_zone import generate_search_zone

class PlanSearchForm(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/PlanSearchForm.ui"), self)
        self.buttonGenerate.clicked.connect(self.generate_plan)

    def generate_plan(self):
        try:
            start_lat = self.spinStartLat.value()
            start_lon = self.spinStartLon.value()
            end_lat = self.spinEndLat.value()
            end_lon = self.spinEndLon.value()
            start = QgsPointXY(start_lon, start_lat)
            end = QgsPointXY(end_lon, end_lat)
            path_layer = simulate_sru_path(start, end)
            bearing = calculate_bearing(start_lat, start_lon, end_lat, end_lon)
            zone_layer = generate_search_zone(start, 5, 'sector')  # Пример зоны
            QMessageBox.information(self, "Успех", f"План сгенерирован, азимут: {bearing}°; слои добавлены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))