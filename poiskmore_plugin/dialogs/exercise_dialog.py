from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QDateEdit, QPushButton
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMessageBox

class ExerciseDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учение / Тренировка")
        layout = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.date_edit = QDateEdit(QDate.currentDate())
        self.region_edit = QLineEdit()
        self.units_edit = QTextEdit()
        self.scenario_edit = QTextEdit()

        layout.addWidget(QLabel("Название учения:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Дата проведения:"))
        layout.addWidget(self.date_edit)
        layout.addWidget(QLabel("Район проведения:"))
        layout.addWidget(self.region_edit)
        layout.addWidget(QLabel("Задействованные силы и средства (SRU):"))
        layout.addWidget(self.units_edit)
        layout.addWidget(QLabel("Сценарий:"))
        layout.addWidget(self.scenario_edit)
        self.ok_button = QPushButton("Сохранить")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def accept(self):
        if not self.name_edit.text() or not self.region_edit.text():
            QMessageBox.warning(self, "Ошибка", "Заполните название и район!")
            return
        super().accept()