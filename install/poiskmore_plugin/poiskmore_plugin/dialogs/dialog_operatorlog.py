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

class OperatorLogForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/OperatorLogForm.ui"), self)

        self.load_log()

    def load_log(self):
        try:
            log_path = os.path.join(os.path.dirname(__file__), "../data/operator_log.json")
            with open(log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            self.operatorLogTable.setRowCount(len(logs))
            for row, log in enumerate(logs):
                self.operatorLogTable.setItem(row, 0, QTableWidgetItem(log["date"]))
                self.operatorLogTable.setItem(row, 1, QTableWidgetItem(log["action"]))
                self.operatorLogTable.setItem(row, 2, QTableWidgetItem(log["details"]))
        except Exception as e:
            QgsMessageLog.logMessage(f"Ошибка загрузки лога: {str(e)}", "Поиск-Море", Qgis.Critical)