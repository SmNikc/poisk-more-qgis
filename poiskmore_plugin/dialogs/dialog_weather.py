from PyQt5.QtWidgets import QDialog, QDoubleSpinBox, QPushButton, QVBoxLayout, QMessageBox
class WeatherDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.wind_speed = QDoubleSpinBox()
self.wind_speed.setValue(10.0)
layout.addWidget(self.wind_speed)
btn = QPushButton("Save")
btn.clicked.connect(self.save)
layout.addWidget(btn)
def save(self):
if self.wind_speed.value() > 0:
self.accept()
else:
QMessageBox.warning(self, "Ошибка", "Скорость ветра >0")
def get_data(self):
return {'wind_speed': self.wind_speed.value()}