from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
class AswDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.asw_param = QLineEdit()
layout.addWidget(self.asw_param)
btn = QPushButton("Apply")
btn.clicked.connect(self.apply)
layout.addWidget(btn)
def apply(self):
if self.asw_param.text().strip():
self.accept()
else:
QMessageBox.warning(self, "Ошибка", "Параметр обязателен")
def get_data(self):
return {'asw': self.asw_param.text()}