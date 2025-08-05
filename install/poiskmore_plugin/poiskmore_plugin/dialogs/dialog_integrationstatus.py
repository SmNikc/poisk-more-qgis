python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
import os
from qgis.core import QgsMessageLog, Qgis

class IntegrationStatusForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/IntegrationStatusForm.ui"), self)

        self.buttonSyncNow.clicked.connect(self.sync_now)

        self.update_table()

    def update_table(self):
        integrations = [
            ("ActiveMQ", "Активен"),
            ("Email", "Активен"),
            ("FTP", "Неактивен")
        ]
        self.integrationTable.setRowCount(len(integrations))
        for row, (name, status) in enumerate(integrations):
            self.integrationTable.setItem(row, 0, QTableWidgetItem(name))
            self.integrationTable.setItem(row, 1, QTableWidgetItem(status))

    def sync_now(self):
        try:
            # Пример синхронизации
            QgsMessageLog.logMessage("Синхронизация запущена", "Поиск-Море", Qgis.Info)
            self.update_table()
            QMessageBox.information(self, "Успех", "Синхронизация завершена.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка синхронизации: {str(e)}")