from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout
class DialogAircraftDirectory(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.aircraft_name = QLineEdit()
layout.addWidget(self.aircraft_name)
btn = QPushButton("Add")
btn.clicked.connect(self.add_aircraft)
layout.addWidget(btn)
def add_aircraft(self):
if self.aircraft_name.text().strip():
self.accept()