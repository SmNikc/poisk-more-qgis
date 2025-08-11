"""Registration dialog for incident creation.

This dialog collects the basic information required to register a new
emergency: date and time, name, coordinates and a free form description.
"""

from PyQt5.QtCore import QDateTime, QDateTimeEdit
from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QTextEdit,
)


class RegistrationDialog(QDialog):
    """Dialog window for registering an incident."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Регистрация аварии:"))
        layout.addWidget(QLabel("Дата / Время (UTC):"))

        self.datetime = QDateTimeEdit()
        self.datetime.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.datetime)

        layout.addWidget(QLabel("Название:"))
        self.name = QLineEdit()
        layout.addWidget(self.name)

        layout.addWidget(QLabel("Координаты:"))
        self.coords = QLineEdit()
        layout.addWidget(self.coords)

        layout.addWidget(QLabel("Описание:"))
        self.description = QTextEdit()
        layout.addWidget(self.description)

        btn = QPushButton("Зарегистрировать")
        btn.clicked.connect(self.register)
        layout.addWidget(btn)

    def register(self):
        """Validate required fields and close the dialog on success."""
        if not self.name.text().strip() or not self.coords.text().strip():
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return
        self.accept()

