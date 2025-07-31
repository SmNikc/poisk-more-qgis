python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
import json
from modules.sitrep_mq import SitrepMQ
from qgis.core import QgsTask, QgsMessageLog, Qgis

class SitrepSendForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/SitrepSendForm.ui"), self)

        self.buttonSend.clicked.connect(self.start_async_send)

    def start_async_send(self):
        try:
            queue = self.destinationQueue.text()
            json_data = json.loads(self.sitrepJson.toPlainText())

            task = SendSitrepTask("Отправка SITREP", queue, json_data, self)
            QgsApplication.taskManager().addTask(task)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Ошибка", f"Неверный JSON: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка запуска отправки: {str(e)}")

class SendSitrepTask(QgsTask):
    def __init__(self, description, queue, json_data, dialog):
        super().__init__(description, QgsTask.CanCancel)
        self.queue = queue
        self.json_data = json_data
        self.dialog = dialog
        self.exception = None

    def run(self):
        try:
            mq = SitrepMQ()
            success = mq.send_sitrep(self.json_data)
            return success
        except Exception as e:
            self.exception = e
            QgsMessageLog.logMessage(f"Ошибка отправки SITREP: {str(e)}", "Поиск-Море", Qgis.Critical)
            return False

    def finished(self, result):
        if result:
            QMessageBox.information(self.dialog, "Успех", "SITREP отправлен через ActiveMQ.")
        elif self.exception:
            QMessageBox.critical(self.dialog, "Ошибка", f"Ошибка отправки: {str(self.exception)}")
        else:
            QMessageBox.critical(self.dialog, "Ошибка", "Отправка не выполнена.")