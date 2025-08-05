python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
import shutil
from qgis.core import QgsMessageLog, Qgis

class CleanupUtilityForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/CleanupUtilityForm.ui"), self)

        self.buttonRunCleanup.clicked.connect(self.run_cleanup)

    def run_cleanup(self):
        try:
            if self.clearLogs.isChecked():
                log_path = os.path.join(os.path.dirname(__file__), "../data/logs")
                if os.path.exists(log_path):
                    shutil.rmtree(log_path)
                    QgsMessageLog.logMessage("Логи очищены", "Поиск-Море", Qgis.Info)

            if self.clearTemp.isChecked():
                temp_path = os.path.join(os.path.dirname(__file__), "../temp")
                if os.path.exists(temp_path):
                    shutil.rmtree(temp_path)
                    QgsMessageLog.logMessage("Временные файлы очищены", "Поиск-Море", Qgis.Info)

            if self.clearDatabase.isChecked():
                db_path = os.path.join(os.path.dirname(__file__), "../data/alerts.db")
                if os.path.exists(db_path):
                    os.remove(db_path)
                    QgsMessageLog.logMessage("База данных сброшена", "Поиск-Море", Qgis.Info)

            QMessageBox.information(self, "Успех", "Очистка завершена.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка очистки: {str(e)}")