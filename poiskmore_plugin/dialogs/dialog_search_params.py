from PyQt5.QtWidgets import QDialog, QDoubleSpinBox, QPushButton, QVBoxLayout, QLabel


class SearchParamsDialog(QDialog):
    """Dialog for specifying search parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Параметры поиска:"))

        self.radius = QDoubleSpinBox(minimum=0.1)
        layout.addWidget(self.radius)

        btn = QPushButton("OK")
        btn.clicked.connect(self.ok)
        layout.addWidget(btn)

    def ok(self):
        self.accept()
