python from PyQt5.QtWidgets import QDialog, QMessageBox from PyQt5 import uic import os
class ExerciseDialog(QDialog): def init(self, parent=None): super().init(parent) uic.loadUi(os.path.join(os.path.dirname(file), '../forms/ExerciseForm.ui'), self)
self.buttonStart.clicked.connect(self.start_exercise)
def start_exercise(self): scenario = self.inputScenario.text() if not scenario: QMessageBox.warning(self, "Ошибка", "Сценарий обязателен") return
from .utils.multi_sru_simulator import simulate_multi_sru routes = [] # Заглушка collisions = simulate_multi_sru(routes) msg = f"Учение запущено: {scenario}\nКоллизии: {len(collisions)}" QMessageBox.information(self, "Успех", msg)