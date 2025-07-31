# dialogs/dialog_registration.py
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic
import os

class RegistrationForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), '../forms/RegistrationForm.ui'), self)

        self.buttonNext.clicked.connect(self.next_state)
        self.buttonPrev.clicked.connect(self.prev_state)
        self.buttonFinish.clicked.connect(self.finish_registration)

        self.update_buttons()

    def next_state(self):
        current = self.stackedWidget.currentIndex()
        if current < self.stackedWidget.count() - 1:
            self.stackedWidget.setCurrentIndex(current + 1)
        self.update_buttons()

    def prev_state(self):
        current = self.stackedWidget.currentIndex()
        if current > 0:
            self.stackedWidget.setCurrentIndex(current - 1)
        self.update_buttons()

    def update_buttons(self):
        idx = self.stackedWidget.currentIndex()
        count = self.stackedWidget.count()
        self.buttonPrev.setEnabled(idx > 0)
        self.buttonNext.setEnabled(idx < count - 1)
        self.buttonFinish.setEnabled(idx == count - 1)

        if idx == count - 1:
            summary = self.collect_summary()
            self.plainConfirm.setPlainText(summary)

    def collect_summary(self):
        summary = f"Тип происшествия: {self.comboIncidentType.currentText()}\n"
        summary += f"Дата/Время: {self.dateTimeIncident.dateTime().toString('dd.MM.yyyy HH:mm')}\n"
        summary += f"Место: {self.editLocation.text()}\n"
        summary += f"Координаты: {self.editCoordinates.text()}\n"
        summary += f"Название судна: {self.editVesselName.text()}\n"
        summary += f"IMO: {self.editIMONumber.text()}\n"
        summary += f"Позывной: {self.editCallSign.text()}\n"
        summary += f"Экипаж: {self.spinPersonsOnBoard.value()}\n"
        summary += f"Ситуация:\n{self.textSituationDescription.toPlainText()}\n"
        return summary

    def finish_registration(self):
        summary = self.collect_summary()
        QMessageBox.information(self, "Регистрация происшествия", f"Происшествие зарегистрировано:\n\n{summary}")
        self.accept()