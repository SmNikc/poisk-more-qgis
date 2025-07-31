python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from qgis.core import QgsMessageLog, Qgis

class RCCCommunicationForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/RCCCommunicationForm.ui"), self)

        self.buttonSend.clicked.connect(self.send_message)

    def send_message(self):
        try:
            rcc_name = self.rccName.text()
            channel = self.rccChannel.currentText()
            message = self.messageToRcc.toPlainText()

            QgsMessageLog.logMessage(f"Сообщение RCC {rcc_name} по {channel}: {message}", "Поиск-Море", Qgis.Info)
            QMessageBox.information(self, "Успех", "Сообщение отправлено RCC.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка отправки: {str(e)}")