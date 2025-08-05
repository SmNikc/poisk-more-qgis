"""Диалог запуска учений."""

import os
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic


class ExerciseDialog(QDialog):
    """Простой диалог для запуска учения."""

    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "../forms/ExerciseForm.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
            if hasattr(self, "buttonStart"):
                self.buttonStart.clicked.connect(self.start_exercise)

    def start_exercise(self):
        scenario = self.inputScenario.text()
        if not scenario:
            QMessageBox.warning(self, "Ошибка", "Сценарий обязателен")
            return

        from ..utils.multi_sru_simulator import simulate_multi_sru

        routes = []  # заглушка для маршрутов
        collisions = simulate_multi_sru(routes)
        msg = f"Учение запущено: {scenario}\nКоллизии: {len(collisions)}"
        QMessageBox.information(self, "Успех", msg)

