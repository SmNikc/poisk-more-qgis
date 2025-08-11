from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout
class DialogDutyOfficerTablet(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
table = QTableWidget(10, 5)
table.setHorizontalHeaderLabels(["ID", "Описание", "Координаты", "Статус", "Дата"])
layout.addWidget(table)