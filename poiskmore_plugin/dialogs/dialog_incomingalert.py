python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from modules.imap_reader import IMAPReader
from modules.db_interface import DBInterface
from qgis.core import QgsTask, QgsMessageLog, Qgis

class IncomingAlertForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/IncomingAlertForm.ui"), self)

        self.buttonAcknowledge.clicked.connect(self.save_manual_alert)
        self.buttonFetchEmail.clicked.connect(self.start_async_email_fetch)

    def save_manual_alert(self):
        try:
            alert_type = self.alertType.currentText()
            lat = float(self.lineEditLat.text())
            lon = float(self.lineEditLon.text())
            time_received = self.timeReceived.dateTime().toString("yyyy-MM-dd hh:mm:ss")
            source = self.source.text()
            description = self.description.toPlainText()

            db = DBInterface()
            db.save_data("alerts", {
                "alert_type": alert_type,
                "latitude": lat,
                "longitude": lon,
                "time_received": time_received,
                "source": source,
                "description": description
            })
            db.close()

            QMessageBox.information(self, "Успех", "Тревога сохранена.")
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", f"Неверные данные: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")

    def start_async_email_fetch(self):
        try:
            email_server = self.emailServer.text()
            email_user = self.emailUser.text()
            email_password = self.emailPassword.text()

            task = EmailFetchTask("Получение тревог по email", email_server, email_user, email_password, self)
            QgsApplication.taskManager().addTask(task)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка запуска email: {str(e)}")