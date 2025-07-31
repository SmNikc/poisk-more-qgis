python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
import os
import json
from qgis.core import QgsMessageLog, Qgis

class LogbookForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/LogbookForm.ui"), self)

        self.load_logbook()

    def load_logbook(self):
        try:
            log_path = os.path.join(os.path.dirname(__file__), "../data/logbook.json")
            with open(log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            self.logTable.setRowCount(len(logs))
            for row, log in enumerate(logs):
                self.logTable.setItem(row, 0, QTableWidgetItem(log["date"]))
                self.logTable.setItem(row, 1, QTableWidgetItem(log["action"]))
        except Exception as e:
            QgsMessageLog.logMessage(f"Ошибка загрузки logbook: {str(e)}", "Поиск-Море", Qgis.Critical)