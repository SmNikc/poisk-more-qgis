python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QGraphicsLineItem, QGraphicsScene
from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt
from qgis.core import QgsTask, QgsMessageLog, Qgis, QgsPointXY
import os
import math

class DriftCalculationForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/DriftCalculationForm.ui"), self)

        # Инициализация сцены для QGraphicsView
        self.scene = QGraphicsScene()
        self.driftGraphicsView.setScene(self.scene)

        self.buttonCalculate.clicked.connect(self.start_async_drift)

    def start_async_drift(self):
        try:
            lat = float(self.lineEditLkpLat.text())
            lon = float(self.lineEditLkpLon.text())
            wind_speed = float(self.lineEditWindSpeed.text())
            wind_dir = float(self.lineEditWindDir.text())
            current_speed = float(self.lineEditCurrentSpeed.text())
            current_dir = float(self.lineEditCurrentDir.text())
            duration = int(self.spinDuration.value())

            task = DriftCalculationTask("Расчёт дрейфа", lat, lon, wind_speed, wind_dir, current_speed, current_dir, duration, self)
            QgsApplication.taskManager().addTask(task)
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка ввода", f"Неверные данные: {str(e)}. Проверьте числа.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запуске расчёта: {str(e)}")

class DriftCalculationTask(QgsTask):
    def __init__(self, description, lat, lon, wind_speed, wind_dir, current_speed, current_dir, duration, dialog):
        super().__init__(description, QgsTask.CanCancel)
        self.lat = lat
        self.lon = lon
        self.wind_speed = wind_speed
        self.wind_dir = math.radians(wind_dir)
        self.current_speed = current_speed
        self.current_dir = math.radians(current_dir)
        self.duration = duration
        self.dialog = dialog
        self.result = None
        self.exception = None

    def run(self):
        try:
            # Расчёт дрейфа по IAMSAR том 2
            drift_speed_wind = self.wind_speed * 0.03
            drift_speed_current = self.current_speed

            dx_wind = drift_speed_wind * math.sin(self.wind_dir) * self.duration
            dy_wind = drift_speed_wind * math.cos(self.wind_dir) * self.duration
            dx_current = drift_speed_current * math.sin(self.current_dir) * self.duration
            dy_current = drift_speed_current * math.cos(self.current_dir) * self.duration

            delta_lat = (dy_wind + dy_current) / 111
            delta_lon = (dx_wind + dx_current) / (111 * math.cos(math.radians(self.lat)))

            new_lat = self.lat + delta_lat
            new_lon = self.lon + delta_lon

            self.result = (new_lat, new_lon)
            return True
        except Exception as e:
            self.exception = e
            QgsMessageLog.logMessage(f"Ошибка в задаче дрейфа: {str(e)}", "Поиск-Море", Qgis.Critical)
            return False

    def finished(self, result):
        if result and self.result:
            new_lat, new_lon = self.result
            QMessageBox.information(self.dialog, "Результат", f"Новый LKP: {new_lat:.6f}°, {new_lon:.6f}°")

            self.dialog.scene.clear()
            pen = QPen(Qt.red, 2)
            scale = 10
            line = QGraphicsLineItem(0, 0, new_lon * scale, -new_lat * scale)
            line.setPen(pen)
            self.dialog.scene.addItem(line)
            self.dialog.driftGraphicsView.fitInView(self.dialog.scene.sceneRect(), Qt.KeepAspectRatio)
        elif self.exception:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка расчёта: {str(self.exception)}")
        else:
            QMessageBox.critical(self.dialog, "Ошибка", "Расчёт не выполнен.")