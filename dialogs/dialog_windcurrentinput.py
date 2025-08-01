python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
import os
from qgis.core import QgsRasterLayer, QgsProject, QgsMessageLog, Qgis

class WindCurrentInputForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/WindCurrentInputForm.ui"), self)

        self.buttonLoad.clicked.connect(self.load_data)

    def load_data(self):
        try:
            wind_speed = self.windSpeed.text()
            wind_dir = self.windDirection.text()
            current_speed = self.currentSpeed.text()
            current_dir = self.currentDirection.text()
            map_source = self.mapSource.currentText()
            file_path = self.filePath.text()

            if map_source == "GeoTIFF":
                layer = QgsRasterLayer(file_path, "GeoTIFF Ветер/Течение", "gdal")
                if not layer.isValid():
                    QMessageBox.critical(self, "Ошибка", "Не удалось загрузить GeoTIFF.")
                    return
                QgsProject.instance().addMapLayer(layer)
            elif map_source == "WMS":
                uri = f"url={file_path}&layers=wind&format=image/png&crs=EPSG:4326"  # Пример WMS
                layer = QgsRasterLayer(uri, "WMS Ветер/Течение", "wms")
                if not layer.isValid():
                    QMessageBox.critical(self, "Ошибка", "Не удалось загрузить WMS.")
                    return
                QgsProject.instance().addMapLayer(layer)

            QgsMessageLog.logMessage(f"Данные загружены: Ветер {wind_speed}@{wind_dir}, Течение {current_speed}@{current_dir}", "Поиск-Море", Qgis.Info)
            QMessageBox.information(self, "Успех", "Данные загружены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки: {str(e)}")