from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout
class DialogFullWorkflow(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
btn_start = QPushButton("Start Workflow")
layout.addWidget(btn_start)