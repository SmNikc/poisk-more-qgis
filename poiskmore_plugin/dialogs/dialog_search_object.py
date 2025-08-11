from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
class SearchObjectDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.obj = QLineEdit()
layout.addWidget(self.obj)
btn = QPushButton("OK")
btn.clicked.connect(self.validate)
layout.addWidget(btn)
def validate(self):
if self.obj.text().strip():
self.accept()
else:
QMessageBox.warning(self, "Ошибка", "Объект обязателен")
def get_data(self):
return self.obj.text()