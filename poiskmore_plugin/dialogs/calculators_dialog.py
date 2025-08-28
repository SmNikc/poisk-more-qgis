from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class CalculatorsDialog(QDialog):
    """Placeholder dialog for various calculators."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Калькуляторы")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Калькуляторы находятся в разработке."))

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
