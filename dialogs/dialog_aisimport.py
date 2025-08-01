python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox
import os
from qgis.core import QgsVectorLayer, QgsProject, QgsMessageLog, Qgis

class AISImportForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/AISImportForm.ui"), self)

        self.buttonBrowse.clicked.connect(self.browse_file)
        self.buttonImport.clicked.connect(self.import_ais)

    def browse_file(self):
        file_path = QFileDialog.getOpenFileName(self, "Выберите файл AIS", "", "CSV/NMEA (*.csv *.nmea)")[0]
        if file_path:
            self.filePath.setText(file_path)

    def import_ais(self):
        try:
            path = self.filePath.text()
            if not path:
                QMessageBox.warning(self, "Ошибка", "Выберите файл.")
                return

            layer = QgsVectorLayer(path, "AIS данные", "ogr" if path.endswith('.csv') else "delimitedtext")
            if not layer.isValid():
                QMessageBox.critical(self, "Ошибка", "Не удалось загрузить AIS.")
                return
            QgsProject.instance().addMapLayer(layer)
            QgsMessageLog.logMessage(f"AIS импортирован: {path}", "Поиск-Море", Qgis.Info)
            QMessageBox.information(self, "Успех", "AIS данные добавлены как слой.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка импорта: {str(e)}")