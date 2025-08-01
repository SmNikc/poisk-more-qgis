python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from qgis.core import QgsTask, QgsMessageLog, Qgis, QgsVectorFileWriter, QgsFeature, QgsGeometry, QgsField
from qgis.PyQt.QtCore import QVariant
import datetime

class ReportGenerationForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/ReportGenerationForm.ui"), self)

        self.buttonExportPDF.clicked.connect(self.start_async_pdf)
        self.buttonExportGeoJSON.clicked.connect(self.start_async_geojson)

    def start_async_pdf(self):
        try:
            operation_name = self.operationName.text()
            start_time = self.startTime.dateTime().toString("yyyy-MM-dd hh:mm:ss")
            end_time = self.endTime.dateTime().toString("yyyy-MM-dd hh:mm:ss")
            sru_summary = self.sruSummary.toPlainText()
            search_results = self.searchResults.toPlainText()
            conclusion = self.conclusion.toPlainText()

            task = ReportPDFTask("Генерация PDF", operation_name, start_time, end_time, sru_summary, search_results, conclusion, self)
            QgsApplication.taskManager().addTask(task)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запуске PDF: {str(e)}")

    def start_async_geojson(self):
        try:
            task = ReportGeoJSONTask("Генерация GeoJSON", self)
            QgsApplication.taskManager().addTask(task)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запуске GeoJSON: {str(e)}")

class ReportPDFTask(QgsTask):
    def __init__(self, description, operation_name, start_time, end_time, sru_summary, search_results, conclusion, dialog):
        super().__init__(description, QgsTask.CanCancel)
        self.operation_name = operation_name
        self.start_time = start_time
        self.end_time = end_time
        self.sru_summary = sru_summary
        self.search_results = search_results
        self.conclusion = conclusion
        self.dialog = dialog
        self.exception = None
        self.pdf_path = None

    def run(self):
        try:
            pdf_path = QFileDialog.getSaveFileName(self.dialog, "Сохранить PDF", "", "PDF (*.pdf)")[0]
            if not pdf_path:
                return False
            c = canvas.Canvas(pdf_path, pagesize=letter)
            y = 750
            c.drawString(100, y, f"Операция: {self.operation_name}")
            y -= 20
            c.drawString(100, y, f"Начало: {self.start_time}")
            y -= 20
            c.drawString(100, y, f"Окончание: {self.end_time}")
            y -= 20
            c.drawString(100, y, f"SRU: {self.sru_summary}")
            y -= 20
            c.drawString(100, y, f"Результаты: {self.search_results}")
            y -= 20
            c.drawString(100, y, f"Выводы: {self.conclusion}")
            c.save()
            self.pdf_path = pdf_path
            return True
        except Exception as e:
            self.exception = e
            QgsMessageLog.logMessage(f"Ошибка PDF: {str(e)}", "Поиск-Море", Qgis.Critical)
            return False

    def finished(self, result):
        if result and self.pdf_path:
            QMessageBox.information(self.dialog, "Успех", f"PDF создан: {self.pdf_path}")
        elif self.exception:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка PDF: {str(self.exception)}")
        else:
            QMessageBox.critical(self.dialog, "Ошибка", "Генерация PDF отменена.")

class ReportGeoJSONTask(QgsTask):
    def __init__(self, description, dialog):
        super().__init__(description, QgsTask.CanCancel)
        self.dialog = dialog
        self.exception = None
        self.geojson_path = None

    def run(self):
        try:
            geojson_path = QFileDialog.getSaveFileName(self.dialog, "Сохранить GeoJSON", "", "GeoJSON (*.geojson)")[0]
            if not geojson_path:
                return False
            layer = QgsVectorLayer("Polygon?crs=epsg:4326", "Экспорт зон", "memory")
            pr = layer.dataProvider()
            pr.addAttributes([QgsField("id", QVariant.Int)])
            layer.updateFields()

            feat = QgsFeature()
            feat.setAttributes([1])
            geom = QgsGeometry.fromWkt("POLYGON ((30 60, 31 61, 32 60, 30 60))")  # Пример геометрии
            feat.setGeometry(geom)
            pr.addFeature(feat)
            layer.updateExtents()

            QgsVectorFileWriter.writeAsVectorFormat(layer, geojson_path, "utf-8", layer.crs(), "GeoJSON")
            self.geojson_path = geojson_path
            return True
        except Exception as e:
            self.exception = e
            QgsMessageLog.logMessage(f"Ошибка GeoJSON: {str(e)}", "Поиск-Море", Qgis.Critical)
            return False

    def finished(self, result):
        if result and self.geojson_path:
            layer = QgsVectorLayer(self.geojson_path, "Экспортированные зоны", "ogr")
            QgsProject.instance().addMapLayer(layer)
            QMessageBox.information(self.dialog, "Успех", f"GeoJSON создан и добавлен: {self.geojson_path}")
        elif self.exception:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка GeoJSON: {str(self.exception)}")
        else:
            QMessageBox.critical(self.dialog, "Ошибка", "Экспорт GeoJSON отменён.")