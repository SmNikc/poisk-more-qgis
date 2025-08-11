from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
class SearchAreaDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.area_desc = QLineEdit()
layout.addWidget(self.area_desc)
btn = QPushButton("Create")
btn.clicked.connect(self.create)
layout.addWidget(btn)
def create(self):
if self.area_desc.text().strip():
self.accept()
else:
QMessageBox.warning(self, "Ошибка", "Описание обязательно")
def get_data(self):
return {'area': self.area_desc.text()}