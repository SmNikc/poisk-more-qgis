from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QLabel
class DialogSRUAssignment(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Назначение SRU:"))
table = QTableWidget(5, 4)
table.setHorizontalHeaderLabels(["SRU", "Район", "Время", "Статус"])
layout.addWidget(table)
btn_cancel = QPushButton("Отмена")
btn_cancel.clicked.connect(self.close)
layout.addWidget(btn_cancel)
btn_save = QPushButton("Сохранить PDF")
layout.addWidget(btn_save)
btn_send = QPushButton("Отправить")
layout.addWidget(btn_send)