python from PyQt5.QtWidgets import QDialog, QMessageBox from PyQt5 import uic import os from .alg.alg_srudesign import calculate_sru_path
class SRUPathDialog(QDialog): def init(self, parent=None): super().init(parent) uic.loadUi(os.path.join(os.path.dirname(file), '../forms/SRUPathCalcForm.ui'), self)
self.buttonCalculate.clicked.connect(self.calculate_path)
def calculate_path(self): try: start_lat = self.spinStartLat.value() start_lon = self.spinStartLon.value() end_lat = self.spinEndLat.value() end_lon = self.spinEndLon.value() speed = self.spinSpeed.value()
# distance, time, bearing = calculate_sru_path(start_lat, start_lon, end_lat, end_lon, speed) QMessageBox.information(self, "Результат", f"Расстояние: {distance} NM\nВремя: {time} ч\nАзимут: {bearing}°") except ValueError as e: QMessageBox.warning(self, "Ошибка", str(e))
