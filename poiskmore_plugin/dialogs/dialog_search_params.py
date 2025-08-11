from PyQt5.QtWidgets import QDialog, QDoubleSpinBox, QPushButton, QVBoxLayout, QMessageBox
class SearchParamsDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.radius = QDoubleSpinBox(minimum=0.1)
layout.addWidget(self.radius)
btn = QPushButton("OK")
btn.clicked.connect(self.validate)
layout.addWidget(btn)
def validate(self):
if self.radius.value() > 0:
self.accept()
else:
QMessageBox.warning(self, "Ошибка", "Радиус >0")
def get_params(self):
return {'radius': self.radius.value()}