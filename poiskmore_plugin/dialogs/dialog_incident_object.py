from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
class IncidentObjectDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.obj = QLineEdit()
layout.addWidget(self.obj)
btn = QPushButton("Save")
btn.clicked.connect(self.save)
layout.addWidget(btn)
def save(self):
if self.obj.text().strip():
self.accept()
else:
QMessageBox.warning(self, "Ошибка", "Объект обязателен")
def get_data(self):
return self.obj.text()