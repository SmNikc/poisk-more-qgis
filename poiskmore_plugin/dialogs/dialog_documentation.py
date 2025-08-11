from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QLabel
class DialogDocumentation(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Документация:"))
btn = QPushButton("Открыть")
btn.clicked.connect(self.open)
layout.addWidget(btn)
def open(self):
self.accept()