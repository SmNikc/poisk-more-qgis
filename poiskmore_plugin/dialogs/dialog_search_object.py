from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel


class SearchObjectDialog(QDialog):
    """Dialog for specifying the object of search."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Объект поиска:"))

        self.obj = QLineEdit()
        layout.addWidget(self.obj)

        btn = QPushButton("OK")
        btn.clicked.connect(self.ok)
        layout.addWidget(btn)

    def ok(self):
        self.accept()
