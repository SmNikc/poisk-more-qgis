from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel
class IncidentObjectDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Объект инцидента:"))
self.obj = QLineEdit()
layout.addWidget(self.obj)
btn = QPushButton("Сохранить")
btn.clicked.connect(self.save)
layout.addWidget(btn)
def save(self):
self.accept()