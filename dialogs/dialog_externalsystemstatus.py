python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
import os
from qgis.core import QgsMessageLog, Qgis

class ExternalSystemStatusForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/ExternalSystemStatusForm.ui"), self)

        self.buttonRefresh.clicked.connect(self.refresh_status)

        self.refresh_status()

    def refresh_status(self):
        try:
            statuses = [
                ("ActiveMQ", "Подключено" if self.check_mq() else "Ошибка"),
                ("Email", "Подключено" if self.check_email() else "Ошибка"),
                ("FTP", "Подключено" if self.check_ftp() else "Ошибка")
            ]
            self.moduleStatusTable.setRowCount(len(statuses))
            for row, (module, status) in enumerate(statuses):
                self.moduleStatusTable.setItem(row, 0, QTableWidgetItem(module))
                self.moduleStatusTable.setItem(row, 1, QTableWidgetItem(status))
        except Exception as e:
            QgsMessageLog.logMessage(f"Ошибка обновления статусов: {str(e)}", "Поиск-Море", Qgis.Critical)

    def check_mq(self):
        # Пример проверки ActiveMQ
        return True  # Замените на реальную проверку

    def check_email(self):
        # Пример проверки email
        return True

    def check_ftp(self):
        # Пример проверки FTP
        return True