python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os

class IAMSARScenarioForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/IAMSARScenarioForm.ui"), self)

        self.scenarioSelector.addItems(["MAYDAY", "PAN-PAN", "SECURITY"])
        self.buttonApply.clicked.connect(self.apply_scenario)

    def apply_scenario(self):
        try:
            scenario = self.scenarioSelector.currentText()
            description = self.scenarioDescription.toPlainText()

            # Пример применения (в реальности — вызов расчёта)
            QMessageBox.information(self, "Успех", f"Сценарий {scenario} применён: {description}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка применения: {str(e)}")