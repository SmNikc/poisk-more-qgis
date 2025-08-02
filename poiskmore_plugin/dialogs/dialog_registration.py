# python """Форма регистрации происшествий."""
from PyQt5.QtWidgets import QDialog, QMessageBox from PyQt5 import uic import os
from ..utils.db_manager import DBManager
class RegistrationForm(QDialog): def init(self, parent=None): super().init(parent) ui_path = os.path.join(os.path.dirname(file), "../forms/RegistrationForm.ui") uic.loadUi(ui_path, self) self.db = DBManager()
self.buttonNext.clicked.connect(self.next_state) self.buttonPrev.clicked.connect(self.prev_state) self.buttonFinish.clicked.connect(self.finish_registration)
self.update_buttons()
def next_state(self): index = self.stackedWidget.currentIndex() if index < self.stackedWidget.count() - 1: self.stackedWidget.setCurrentIndex(index + 1) self.update_buttons()
def prev_state(self): index = self.stackedWidget.currentIndex() if index > 0: self.stackedWidget.setCurrentIndex(index - 1) self.update_buttons()
def update_buttons(self): index = self.stackedWidget.currentIndex() self.buttonPrev.setEnabled(index > 0) self.buttonNext.setEnabled(index < self.stackedWidget.count() - 1) self.buttonFinish.setEnabled(index == self.stackedWidget.count() - 1) if index == self.stackedWidget.count() - 1: self.plainConfirm.setPlainText(self.collect_summary())
def collect_summary(self) -> str: return ( f"Тип: {self.comboIncidentType.currentText()}\n" f"Дата: {self.dateTimeIncident.dateTime().toString()}\n" f"Место: {self.editLocation.text()}\n" f"Судно: {self.editVesselName.text()}\n" f"IMO: {self.editIMONumber.text()}\n" f"Описание: {self.textDescription.toPlainText()}" )
def finish_registration(self): incident_type = self.comboIncidentType.currentText() lat = self.editLat.text() lon = self.editLon.text() description = self.textDescription.toPlainText()
# errors = self.validate_data(incident_type, lat, lon, description) if errors: QMessageBox.warning(self, "Ошибка", "\n".join(errors)) return
# self.db.save_incident(incident_type, float(lat), float(lon), description) QMessageBox.information(self, "Успех", "Происшествие зарегистрировано") self.accept()
def validate_data(self, incident_type, lat, lon, description): errors = [] if not incident_type: errors.append("Выберите тип происшествия") try: float(lat) float(lon) except ValueError: errors.append("Неверные координаты") if not description: errors.append("Введите описание") return errors