from PyQt5.QtWidgets import QDialog, QDoubleSpinBox, QPushButton, QVBoxLayout, QLabel
class TwcDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("TWC:"))
self.twc_value = QDoubleSpinBox(minimum=0, value=0.0)
layout.addWidget(self.twc_value)
btn = QPushButton("Сохранить")
btn.clicked.connect(self.save)
layout.addWidget(btn)
def save(self):
self.accept()