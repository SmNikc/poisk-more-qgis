from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QTableWidgetItem
class DutyTabletDialog(QDialog):
def __init__(self, parent, case_id):
super().__init__(parent)
layout = QVBoxLayout(self)
table = QTableWidget(10, 5)
table.setHorizontalHeaderLabels(["ID", "Описание", "Координаты", "Статус", "Дата"])
# Заполнение данными из case_id (пример: симуляция данных)
sample_data = [
[case_id, "Авария судна", "30.0, 60.0", "Активно", "2025-08-10"],
[case_id + 1, "Поиск человека", "31.0, 61.0", "Закрыто", "2025-08-09"]
]
for row, data_row in enumerate(sample_data):
for col, value in enumerate(data_row):
table.setItem(row, col, QTableWidgetItem(str(value)))
layout.addWidget(table)
class DutyTabletManager:
def open_tablet(self, case_id):
dialog = DutyTabletDialog(None, case_id)
dialog.exec_()