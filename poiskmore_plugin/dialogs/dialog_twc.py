from PyQt5.QtWidgets import QDialog, QDoubleSpinBox, QPushButton, QVBoxLayout, QMessageBox
class TwcDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.twc_value = QDoubleSpinBox()
layout.addWidget(self.twc_value)
btn = QPushButton("Save")
btn.clicked.connect(self.save)
layout.addWidget(btn)
def save(self):
self.accept()
def get_data(self):
return {'twc': self.twc_value.value()}