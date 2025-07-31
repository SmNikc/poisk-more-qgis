python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
import requests  # Для проверки обновлений
from qgis.core import QgsMessageLog, Qgis

class UpdateControlForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/UpdateControlForm.ui"), self)

        self.labelCurrentVersion.setText("Текущая версия: 1.0.0")

        self.buttonCheckUpdate.clicked.connect(self.check_update)
        self.buttonApplyUpdate.clicked.connect(self.apply_update)

    def check_update(self):
        try:
            # Пример проверки версии (замените URL на реальный)
            response = requests.get("https://yourrepo.com/version.txt")
            latest_version = response.text.strip()
            if latest_version != "1.0.0":
                QMessageBox.information(self, "Обновление", f"Доступна версия {latest_version}.")
            else:
                QMessageBox.information(self, "Обновление", "У вас последняя версия.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка проверки: {str(e)}")

    def apply_update(self):
        try:
            # Пример обновления (скачивание ZIP, разархив)
            QMessageBox.information(self, "Обновление", "Обновление применяется (реализуйте логику скачивания).")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обновления: {str(e)}")