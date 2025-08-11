from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
from PyQt5.QtCore import QDateTime, QDateTimeEdit
class DialogNewEmergency(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Новый аварийный случай:"))
layout.addWidget(QLabel("Дата / Время (UTC):"))
self.datetime = QDateTimeEdit()
self.datetime.setDateTime(QDateTime.currentDateTime())
layout.addWidget(self.datetime)
layout.addWidget(QLabel("Название:"))
self.name = QLineEdit()
layout.addWidget(self.name)
layout.addWidget(QLabel("Координаты:"))
self.coords = QLineEdit()
layout.addWidget(self.coords)
btn = QPushButton("Зарегистрировать")
btn.clicked.connect(self.register)
layout.addWidget(btn)
def register(self):
self.accept()