from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
class RegistrationDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.name_input = QLineEdit()
layout.addWidget(self.name_input)
btn = QPushButton("Register")
btn.clicked.connect(self.register)
layout.addWidget(btn)
def register(self):
if self.name_input.text().strip():
self.accept()
else:
QMessageBox.warning(self, "Ошибка", "Имя обязательно")
def get_data(self):
return {'name': self.name_input.text()}