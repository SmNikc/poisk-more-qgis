from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout
class DialogCaseArchive(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
table = QTableWidget(10, 2)
table.setHorizontalHeaderLabels(["Case ID", "Date"])
layout.addWidget(table)