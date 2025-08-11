from PyQt5.QtWidgets import QDialog, QTextEdit, QPushButton, QVBoxLayout, QLabel
class SitrepDialog(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("SITREP:"))
self.report = QTextEdit()
layout.addWidget(self.report)
btn = QPushButton("Отправить")
btn.clicked.connect(self.send)
layout.addWidget(btn)
def send(self):
self.accept()