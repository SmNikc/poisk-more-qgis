python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from qgis.core import QgsMessageLog, Qgis

class MessageImportForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/MessageImportForm.ui"), self)

        self.buttonImport.clicked.connect(self.import_message)

    def import_message(self):
        try:
            source = self.sourceSelector.currentText()
            path = self.path.text()

            QgsMessageLog.logMessage(f"Импорт сообщений из {source}: {path}", "Поиск-Море", Qgis.Info)
            QMessageBox.information(self, "Успех", "Сообщения импортированы.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка импорта: {str(e)}")