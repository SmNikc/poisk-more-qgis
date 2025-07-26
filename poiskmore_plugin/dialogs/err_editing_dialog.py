from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QDateTimeEdit
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QMessageBox

class ErrEditingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактирование происшествия")
        layout = QVBoxLayout()

        self.id_edit = QLineEdit()
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.location_edit = QLineEdit()
        self.description_edit = QTextEdit()

        layout.addWidget(QLabel("ID происшествия:"))
        layout.addWidget(self.id_edit)
        layout.addWidget(QLabel("Дата и время:"))
        layout.addWidget(self.datetime_edit)
        layout.addWidget(QLabel("Координаты (lat/lon):"))
        layout.addWidget(self.location_edit)
        layout.addWidget(QLabel("Описание:"))
        layout.addWidget(self.description_edit)

        self.save_button = QPushButton("Сохранить изменения")
        self.save_button.clicked.connect(self.accept)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def accept(self):
        if not self.id_edit.text() or not self.location_edit.text():
            QMessageBox.warning(self, "Ошибка", "Заполните ID и координаты!")
            return
        super().accept()