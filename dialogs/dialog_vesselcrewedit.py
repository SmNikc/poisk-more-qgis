python

Свернуть

Перенос

Исполнить

Копировать
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import os
from modules.db_interface import DBInterface

class VesselCrewEditForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "forms/VesselCrewEditForm.ui"), self)

        self.buttonSave.clicked.connect(self.save_vessel)

    def save_vessel(self):
        try:
            name = self.vesselName.text()
            imo_mmsi = self.imoMmsi.text()
            flag = self.flag.text()
            crew_count = self.crewCount.value()

            db = DBInterface()
            db.save_data("vessels", {
                "name": name,
                "imo_mmsi": imo_mmsi,
                "flag": flag,
                "crew_count": crew_count
            })
            db.close()

            QMessageBox.information(self, "Успех", "Данные судна сохранены.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {str(e)}")