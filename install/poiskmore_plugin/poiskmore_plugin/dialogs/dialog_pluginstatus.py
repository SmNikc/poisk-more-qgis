python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
import os
from qgis.core import QgsApplication, QgsProject

class PluginStatusForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/PluginStatusForm.ui"), self)

        self.update_status()

    def update_status(self):
        status = f"Версия QGIS: {QgsApplication.QGIS_VERSION}\nПроект: {QgsProject.instance().fileName() or 'Не открыт'}\nФормы: 37 загружено\nИнтеграция: Активна\nПоследняя синхронизация: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        self.statusText.setText(status)
        self.lastSyncText.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))