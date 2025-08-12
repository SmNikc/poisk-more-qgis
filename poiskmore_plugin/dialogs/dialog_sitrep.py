from PyQt5.QtWidgets import QDialog, QTextEdit, QPushButton, QVBoxLayout, QLabel, QDateTimeEdit
from PyQt5.QtCore import QDateTime


class SitrepDialog(QDialog):
    """Simple dialog for composing and sending SITREP messages."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("SITREP:"))

        # Timestamp of the report
        self.timestamp = QDateTimeEdit()
        self.timestamp.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.timestamp)

        # Report body
        self.report = QTextEdit()
        layout.addWidget(self.report)

        btn = QPushButton("Отправить")
        btn.clicked.connect(self.send)
        layout.addWidget(btn)

    def send(self):
        """Accept the dialog, signalling that the report should be sent."""
        self.accept()
