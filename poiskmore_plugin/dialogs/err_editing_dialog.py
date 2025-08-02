"""Диалог для ввода и сохранения информации об инциденте."""

import os
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic

from ..utils.db_manager import DBManager


class ErrEditingDialog(QDialog):
    """Форма добавления инцидента."""

    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(__file__), "../forms/IncidentForm.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
            if hasattr(self, "buttonSave"):
                self.buttonSave.clicked.connect(self.save_incident)

    def save_incident(self):
        incident_type = self.comboType.currentText()
        lat = self.editLat.text()
        lon = self.editLon.text()
        description = self.textDescription.toPlainText()
        if not all([incident_type, lat, lon, description]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        db = DBManager()
        db.save_incident(incident_type, float(lat), float(lon), description)
        QMessageBox.information(self, "Успех", "Инцидент сохранён")

