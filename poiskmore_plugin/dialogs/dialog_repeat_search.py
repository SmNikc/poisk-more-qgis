from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QLabel, QPushButton
class DialogRepeatSearch(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Повторный поиск:"))
table = QTableWidget(5, 3)
table.setHorizontalHeaderLabels(["ID", "Операция", "Дата"])
layout.addWidget(table)
btn = QPushButton("Выбрать")
btn.clicked.connect(self.select)
layout.addWidget(btn)
def select(self):
self.accept()