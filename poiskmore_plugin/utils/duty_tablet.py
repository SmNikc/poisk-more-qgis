from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QTableWidgetItem
class DutyTabletDialog(QDialog):
def __init__(self, parent, case_id):
super().__init__(parent)
layout = QVBoxLayout(self)
table = QTableWidget(10, 5)
table.setHorizontalHeaderLabels(["ID", "Описание", "Координаты", "Статус", "Дата"])
data = [
[case_id, "Аварийный случай", "30.0, 60.0", "Открыт", "2025-08-10"],
[case_id + 1, "Повторный поиск", "31.0, 61.0", "Закрыт", "2025-08-11"]
]
for row, row_data in enumerate(data):
for col, item in enumerate(row_data):
table.setItem(row, col, QTableWidgetItem(str(item)))
layout.addWidget(table)
self.setLayout(layout)
class DutyTabletManager:
def open_tablet(self, case_id):
dialog = DutyTabletDialog(None, case_id)
dialog.exec_()