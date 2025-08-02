python from PyQt5.QtWidgets import QDialog, QMessageBox from PyQt5 import uic import os
class IncidentDialog(QDialog): def init(self, parent=None): super().init(parent) uic.loadUi(os.path.join(os.path.dirname(file), '../forms/IncidentForm.ui'), self)
self.buttonSave.clicked.connect(self.save_incident)
def save_incident(self): type = self.comboType.currentText() lat = self.editLat.text() lon = self.editLon.text() description = self.textDescription.toPlainText()
if not all([type, lat, lon, description]): QMessageBox.warning(self, "Ошибка", "Заполните все поля") return
# Сохранение в БД или файл
# QMessageBox.information(self, "Успех", "Инцидент сохранён")