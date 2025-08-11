from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout
class DialogHelp(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Помощь:"))
layout.addWidget(QLabel("Инструкции по использованию."))
btn = QPushButton("Закрыть")
btn.clicked.connect(self.close)
layout.addWidget(btn)