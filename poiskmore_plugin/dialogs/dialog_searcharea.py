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
import math

class SearchAreaForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/SearchAreaForm.ui"), self)

        self.buttonCreate.clicked.connect(self.start_async_search)

    def start_async_search(self):
        try:
            area_name = self.areaName.text()
            prefix = self.prefix.text()
            search_type = self.searchType.currentText()
            start_time = self.startTime.dateTime().toString("yyyy-MM-dd hh:mm:ss")
            duration = self.duration.value()
            sru_method = self.sruMethod.currentText()

            if not area_name:
                QMessageBox.warning(self, "Ошибка", "Необходимо указать название района.")
                return

            task = SearchAreaTask("Расчёт схемы поиска", area_name, prefix, search_type, start_time, duration, sru_method, self)
            QgsApplication.taskManager().addTask(task)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запуске расчёта схемы: {str(e)}")

class SearchAreaTask(QgsTask):
    def __init__(self, description, area_name, prefix, search_type, start_time, duration, sru_method, dialog):
        super().__init__(description, QgsTask.CanCancel)
        self.area_name = area_name
        self.prefix = prefix
        self.search_type = search_type
        self.start_time = start_time
        self.duration = duration
        self.sru_method = sru_method
        self.dialog = dialog
        self.exception = None
        self.layer = None

    def run(self):
        try:
            center = QgsPointXY(30, 60)  # Пример LKP
            radius = self.duration * 10  # Пример радиуса в NM

            if self.search_type == "Expanding Square":
                geometry = self.calculate_expanding_square(center, radius)
            elif self.search_type == "Sector Search":
                geometry = self.calculate_sector_search(center, radius)
            elif self.search_type == "Parallel Sweep":
                geometry = self.calculate_parallel_sweep(center, radius)
            else:
                raise ValueError("Неизвестный тип поиска")

            self.layer = QgsVectorLayer("Polygon?crs=epsg:4326", f"{self.area_name} (Схема поиска)", "memory")
            pr = self.layer.dataProvider()
            pr.addAttributes([QgsField("id", QVariant.Int), QgsField("name", QVariant.String)])
            self.layer.updateFields()

            feat = QgsFeature()
            feat.setAttributes([1, self.area_name])
            feat.setGeometry(geometry)
            pr.addFeature(feat)
            self.layer.updateExtents()

            return True
        except Exception as e:
            self.exception = e
            QgsMessageLog.logMessage(f"Ошибка в задаче схемы поиска: {str(e)}", "Поиск-Море", Qgis.Critical)
            return False

    def calculate_expanding_square(self, center, radius):
        points = []
        step = radius / 4
        for i in range(4):
            dx = step * (i + 1)
            dy = step * (i + 1)
            points.append(QgsPointXY(center.x() - dx, center.y() - dy))
            points.append(QgsPointXY(center.x() + dx, center.y() - dy))
            points.append(QgsPointXY(center.x() + dx, center.y() + dy))
            points.append(QgsPointXY(center.x() - dx, center.y() + dy))
        return QgsGeometry.fromPolygonXY([points])

    def calculate_sector_search(self, center, radius):
        points = []
        for angle in range(0, 360, 120):
            x = center.x() + radius * math.cos(math.radians(angle))
            y = center.y() + radius * math.sin(math.radians(angle))
            points.append(QgsPointXY(x, y))
        points.append(points[0])
        return QgsGeometry.fromPolylineXY(points)

    def calculate_parallel_sweep(self, center, radius):
        lines = []
        for i in range(-2, 3):
            start = QgsPointXY(center.x() - radius, center.y() + i * (radius / 2))
            end = QgsPointXY(center.x() + radius, center.y() + i * (radius / 2))
            lines.append(QgsGeometry.fromPolylineXY([start, end]))
        return QgsGeometry.collectGeometry(lines)

    def finished(self, result):
        if result and self.layer:
            QgsProject.instance().addMapLayer(self.layer)
            QMessageBox.information(self.dialog, "Результат", f"Схема поиска '{self.area_name}' создана и добавлена на карту.")
        elif self.exception:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка при выполнении расчёта схемы: {str(self.exception)}.")
        else:
            QMessageBox.critical(self.dialog, "Ошибка", "Расчёт схемы поиска не выполнен.")