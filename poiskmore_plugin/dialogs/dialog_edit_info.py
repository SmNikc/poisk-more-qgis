from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
class DialogEditInfo(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Редактировать информацию:"))
self.info = QLineEdit()
layout.addWidget(self.info)
btn = QPushButton("Сохранить")
btn.clicked.connect(self.save)
layout.addWidget(btn)
def save(self):
self.accept()