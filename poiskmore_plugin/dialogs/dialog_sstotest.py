python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from qgis.core import QgsMessageLog, Qgis

class SSTOTestForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/SSTOTestForm.ui"), self)

        self.buttonSubmit.clicked.connect(self.submit_test)

    def submit_test(self):
        try:
            station = self.stationName.text()
            test_type = self.testType.currentText()
            test_date = self.testDate.date().toString("yyyy-MM-dd")
            result = self.testResult.toPlainText()

            QgsMessageLog.logMessage(f"Тест ССТО: {station}, {test_type}, {test_date}, Результат: {result}", "Поиск-Море", Qgis.Info)
            QMessageBox.information(self, "Успех", "Тест сохранён.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения теста: {str(e)}")