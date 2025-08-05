from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox

class IncomingAlertForm(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms/IncomingAlertForm.ui", self)
        self.buttonNext.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.buttonNext2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.buttonNext3.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))
        self.buttonSave.clicked.connect(self.save_alert)

    def save_alert(self):
        # Сбор данных со всех состояний (по IAMSAR: описание инцидента, контакты, тип/метод)
        data = {
            "day": self.spinDay.value(),
            "lon": self.editLon.text(),
            "name": self.editName.text(),
            "object": self.editObject.text(),
            "callsign": self.editCallsign.text(),
            "flag": self.comboFlag.currentText(),
            "location": self.editLocation.text(),
            "lat": self.spinLat.value(),
            "lon_coord": self.spinLon.value(),
            "description": self.textDescription.toPlainText(),
            "source": self.editSource.text(),
            "event_time": self.dateEventTime.dateTime().toString("dd MMMM yyyy г. HH:mm"),
            "persons": self.spinPersons.value(),
            "coordinator": self.comboCoordinator.currentText(),
            "datetime_utc": self.dateUtc.dateTime().toString("dd MMMM yyyy г. HH:mm"),
            "channel": self.comboChannel.currentText(),
            "from2": self.editFrom2.text(),
            "to": self.editTo.text(),
            "com": self.editCom.text(),
            "additional": self.textAdditional.toPlainText(),
            "accident": self.textAccident.toPlainText(),
            "persons_on_board": self.spinPersonsOnBoard.value(),
            "hull_color": self.comboHullColor.currentText(),
            "superstructure_color": self.comboSuperstructureColor.currentText(),
            "cargo": self.textCargo.toPlainText(),
            "owner": self.editOwner.text(),
            "phone": self.editPhone.text(),
            "address": self.editAddress.text(),
            "departure": self.editDeparture.text(),
            "destination": self.editDestination.text(),
            "etd": self.dateETD.dateTime().toString("dd MMMM yyyy г. HH:mm"),
            "eta": self.dateETA.dateTime().toString("dd MMMM yyyy г. HH:mm"),
            "route": self.textRoute.toPlainText(),
            "object_type": self.comboObjectType.currentText(),
            "simulate": self.checkSimulate.isChecked(),
            "dr": self.spinDR.value(),
            "time_from": self.spinTimeFrom.value()
        }
        # Сохранение (пример: в JSON; интегрируйте с БД по CS.html)
        try:
            with open(os.path.expanduser("~/Documents/alert.json"), "w") as f:
                json.dump(data, f)
            QMessageBox.information(self, "Сохранение", "Регистрация сохранена.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))