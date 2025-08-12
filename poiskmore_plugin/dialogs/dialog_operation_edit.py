from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QDateTimeEdit
from PyQt5.QtCore import QDateTime
class OperationEditDialog(QDialog):
def __init__(self, data, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Редактировать операцию:"))
self.edit = QLineEdit(str(data))
layout.addWidget(self.edit)
btn = QPushButton("Сохранить")
btn.clicked.connect(self.save)
layout.addWidget(btn)
def save(self):
self.accept()