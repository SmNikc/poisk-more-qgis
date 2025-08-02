python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from qgis.core import QgsMessageLog, Qgis

class ExerciseNoticeForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/ExerciseNoticeForm.ui"), self)

        self.buttonSend.clicked.connect(self.send_notice)

    def send_notice(self):
        try:
            name = self.exerciseName.text()
            start_time = self.startTime.dateTime().toString("yyyy-MM-dd hh:mm:ss")
            region = self.region.text()
            notes = self.notes.toPlainText()

            QgsMessageLog.logMessage(f"Уведомление об учении: {name}, {start_time}, {region}, {notes}", "Поиск-Море", Qgis.Info)
            QMessageBox.information(self, "Успех", "Уведомление отправлено.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка отправки: {str(e)}")