python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os

class ActionPlanForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/ActionPlanForm.ui"), self)

        self.buttonSave.clicked.connect(self.save_plan)

    def save_plan(self):
        try:
            plan_text = self.actionPlanText.toPlainText()
            if not plan_text:
                QMessageBox.warning(self, "Ошибка", "План не может быть пустым.")
                return

            save_path = QFileDialog.getSaveFileName(self, "Сохранить план", "", "Text (*.txt)")[0]
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(plan_text)
                QMessageBox.information(self, "Успех", f"План сохранён: {save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")