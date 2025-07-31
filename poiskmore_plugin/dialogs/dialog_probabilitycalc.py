python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from qgis.core import QgsTask, QgsMessageLog, Qgis, QgsPointXY, QgsGeometry, QgsFeature, QgsVectorLayer, QgsProject
from qgis.PyQt.QtCore import QVariant
import random
import math

class ProbabilityCalcForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/ProbabilityCalcForm.ui"), self)

        self.buttonGenerate.clicked.connect(self.start_async_prob)

    def start_async_prob(self):
        try:
            coords = self.lkpCoordinates.text().split(',')
            lat = float(coords[0].strip())
            lon = float(coords[1].strip())
            error_radius = self.errorRadius.value()
            weather = self.weatherCheckBox.isChecked()

            task = ProbabilityTask("Расчёт вероятности", lat, lon, error_radius, weather, self)
            QgsApplication.taskManager().addTask(task)
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", f"Неверные данные: {str(e)}")

class ProbabilityTask(QgsTask):
    def __init__(self, description, lat, lon, error_radius, weather, dialog):
        super().__init__(description, QgsTask.CanCancel)
        self.lat = lat
        self.lon = lon
        self.error_radius = error_radius
        self.weather = weather
        self.dialog = dialog
        self.exception = None
        self.layer = None

    def run(self):
        try:
            center = QgsPointXY(self.lon, self.lat)
            points = []
            for _ in range(100):  # Генерация 100 точек
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(0, self.error_radius)
                x = center.x() + dist * math.cos(angle) / 111
                y = center.y() + dist * math.sin(angle) / 111
                points.append(QgsPointXY(x, y))

            self.layer = QgsVectorLayer("Point?crs=epsg:4326", "Карта вероятностей", "memory")
            pr = self.layer.dataProvider()
            pr.addAttributes([QgsField("id", QVariant.Int)])
            self.layer.updateFields()

            for i, point in enumerate(points):
                feat = QgsFeature()
                feat.setAttributes([i])
                feat.setGeometry(QgsGeometry.fromPointXY(point))
                pr.addFeature(feat)
            self.layer.updateExtents()

            return True
        except Exception as e:
            self.exception = e
            QgsMessageLog.logMessage(f"Ошибка расчёта вероятности: {str(e)}", "Поиск-Море", Qgis.Critical)
            return False

    def finished(self, result):
        if result and self.layer:
            QgsProject.instance().addMapLayer(self.layer)
            QMessageBox.information(self.dialog, "Успех", "Карта вероятностей сгенерирована и добавлена на карту.")
        elif self.exception:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка: {str(self.exception)}")
        else:
            QMessageBox.critical(self.dialog, "Ошибка", "Расчёт не выполнен.")