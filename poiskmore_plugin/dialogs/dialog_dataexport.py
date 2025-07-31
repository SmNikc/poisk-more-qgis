python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
import os
from modules.data_export import DataExport
from qgis.core import QgsProject

class DataExportForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/DataExportForm.ui"), self)

        self.buttonExport.clicked.connect(self.export_data)

    def export_data(self):
        try:
            export_type = self.exportType.currentText()
            target_path = self.targetPath.text() or QFileDialog.getExistingDirectory(self, "Выберите папку для экспорта")

            if not target_path:
                return

            exporter = DataExport(target_path)

            if export_type == "Полный архив (ZIP)":
                files = [layer.source() for layer in QgsProject.instance().mapLayers().values()]
                exporter.export_zip(files)
            elif export_type == "GeoJSON":
                layer = list(QgsProject.instance().mapLayers().values())[0] if QgsProject.instance().mapLayers() else None
                if layer:
                    exporter.export_geojson(layer)
            elif export_type == "PDF/Word":
                report_data = {"Тест": "Данные экспорта"}
                exporter.export_pdf(report_data)
            elif export_type == "База SQLite/PostgreSQL":
                exporter.export_db("alerts.db", os.path.join(target_path, "export.db"))

            QMessageBox.information(self, "Успех", f"Экспорт завершён в {target_path}.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")