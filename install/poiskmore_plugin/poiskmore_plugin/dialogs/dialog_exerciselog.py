python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QInputDialog, QMessageBox
import os
import json
from qgis.core import QgsMessageLog, Qgis

class ExerciseLogForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/ExerciseLogForm.ui"), self)

        self.buttonAddExercise.clicked.connect(self.add_exercise)
        self.buttonDeleteExercise.clicked.connect(self.delete_exercise)

        self.load_log()

    def load_log(self):
        try:
            log_path = os.path.join(os.path.dirname(__file__), "../data/exercise_log.json")
            with open(log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            self.exerciseTable.setRowCount(len(logs))
            for row, log in enumerate(logs):
                self.exerciseTable.setItem(row, 0, QTableWidgetItem(log["date"]))
                self.exerciseTable.setItem(row, 1, QTableWidgetItem(log["name"]))
                self.exerciseTable.setItem(row, 2, QTableWidgetItem(log["region"]))
                self.exerciseTable.setItem(row, 3, QTableWidgetItem(log["result"]))
        except Exception as e:
            QgsMessageLog.logMessage(f"Ошибка загрузки журнала учений: {str(e)}", "Поиск-Море", Qgis.Critical)

    def add_exercise(self):
        name, ok = QInputDialog.getText(self, "Добавление учения", "Название учения:")
        if ok:
            # Добавление (пример)
            row = self.exerciseTable.rowCount()
            self.exerciseTable.insertRow(row)
            self.exerciseTable.setItem(row, 0, QTableWidgetItem(datetime.datetime.now().strftime("%Y-%m-%d")))
            self.exerciseTable.setItem(row, 1, QTableWidgetItem(name))
            self.exerciseTable.setItem(row, 2, QTableWidgetItem("Район"))
            self.exerciseTable.setItem(row, 3, QTableWidgetItem("Результат"))

    def delete_exercise(self):
        selected = self.exerciseTable.selectedRows()
        if selected:
            self.exerciseTable.removeRow(selected[0])