python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
import os
from modules.backup import BackupManager
from qgis.core import QgsSettings

class BackupSettingsForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/BackupSettingsForm.ui"), self)

        settings = QgsSettings()
        self.backupPath.setText(settings.value("backup_path", os.path.expanduser("~/Backup")))
        self.backupInterval.setValue(int(settings.value("backup_interval", 60)))

        self.buttonSave.clicked.connect(self.save_settings)

    def save_settings(self):
        try:
            path = self.backupPath.text()
            interval = self.backupInterval.value()

            settings = QgsSettings()
            settings.setValue("backup_path", path)
            settings.setValue("backup_interval", interval)

            backup = BackupManager(path)
            backup.backup_project(os.path.dirname(__file__))

            QMessageBox.information(self, "Успех", "Настройки сохранены и backup выполнен.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {str(e)}")