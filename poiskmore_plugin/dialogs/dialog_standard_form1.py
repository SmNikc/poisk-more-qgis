pythonfrom PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QDateTime, QDateTimeEdit

class StandardForm1Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Стандартная форма 1"))
        table = QTableWidget(10, 5)
        table.setHorizontalHeaderLabels(["Дата", "Название", "Позиция", "Описание", "Действия"])
        layout.addWidget(table)
        btn_print = QPushButton("Печать")
        btn_print.clicked.connect(self.print_form)
        layout.addWidget(btn_print)
        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save_form)
        layout.addWidget(btn_save)

    def print_form(self):
        # Реализация печати
        pass

    def save_form(self):
        # Реализация сохранения
        pass