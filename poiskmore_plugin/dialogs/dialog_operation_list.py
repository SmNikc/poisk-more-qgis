from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QLabel
class DialogOperationList(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Дела и поисковые операции:"))
table = QTableWidget(10, 3)
table.setHorizontalHeaderLabels(["ID", "Название", "Статус"])
layout.addWidget(table)
btn = QPushButton("Закрыть")
btn.clicked.connect(self.close)
layout.addWidget(btn)