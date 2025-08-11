from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout
class DialogAbout(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("О программе: Поиск-Море v1.0"))
btn = QPushButton("Закрыть")
btn.clicked.connect(self.close)
layout.addWidget(btn)