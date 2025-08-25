from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout

class DutyTabletDialog(QDialog):
    """Dialog window for duty officer tablet"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Планшет дежурного")
        layout = QVBoxLayout(self)

        table = QTableWidget(10, 5, self)
        table.setHorizontalHeaderLabels([
            "ID", "Описание", "Координаты", "Статус", "Дата"
        ])
        layout.addWidget(table)

