from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout
class DialogPlanSearch(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
table = QTableWidget(5, 4)
table.setHorizontalHeaderLabels(["SRU", "Район", "Время", "Статус"])
layout.addWidget(table)