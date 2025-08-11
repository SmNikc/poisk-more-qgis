from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout
class DialogAircraftAssignmentHistory(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
table = QTableWidget(5, 3)
table.setHorizontalHeaderLabels(["ID", "Aircraft", "Assignment"])
layout.addWidget(table)