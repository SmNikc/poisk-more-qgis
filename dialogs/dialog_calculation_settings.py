python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from qgis.core import QgsSettings

class CalculationSettingsForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/CalculationSettingsForm.ui"), self)

        settings = QgsSettings()
        self.driftModel.setCurrentText(settings.value("drift_model", "Стандартная"))
        self.maxIterations.setValue(int(settings.value("max_iterations", 500)))
        self.timeStep.setValue(int(settings.value("time_step", 10)))

        self.buttonSave.clicked.connect(self.save_settings)

    def save_settings(self):
        try:
            settings = QgsSettings()
            settings.setValue("drift_model", self.driftModel.currentText())
            settings.setValue("max_iterations", self.maxIterations.value())
            settings.setValue("time_step", self.timeStep.value())
            QMessageBox.information(self, "Успех", "Настройки расчётов сохранены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")