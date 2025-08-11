from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout
class DialogSearchAreaAdvanced(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
self.adv_param = QLineEdit()
layout.addWidget(self.adv_param)
btn = QPushButton("Apply Advanced")
btn.clicked.connect(self.apply)
layout.addWidget(btn)
def apply(self):
self.accept()