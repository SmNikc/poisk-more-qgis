python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from qgis.core import QgsMessageLog, Qgis

class CoordinationForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/CoordinationForm.ui"), self)

        self.buttonSend.clicked.connect(self.send_message)

    def send_message(self):
        try:
            sru = self.sruSelector.currentText()
            status = self.sruStatus.currentText()
            message = self.messageText.toPlainText()

            # Пример отправки (в реальности — через MQ или API)
            QgsMessageLog.logMessage(f"Сообщение для SRU {sru}: {message} (Статус: {status})", "Поиск-Море", Qgis.Info)
            QMessageBox.information(self, "Успех", "Сообщение отправлено SRU.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка отправки: {str(e)}")