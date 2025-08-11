from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QLabel
class DialogDutyTablet(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Планшет дежурного:"))
table = QTableWidget(10, 5)
table.setHorizontalHeaderLabels(["ID", "Описание", "Координаты", "Статус", "Дата"])
layout.addWidget(table)
btn = QPushButton("Обновить")
btn.clicked.connect(self.update)
layout.addWidget(btn)
def update(self):
self.accept()