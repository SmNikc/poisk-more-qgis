from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class IAMSARReferenceDialog(QDialog):
    """Dialog displaying a placeholder for the IAMSAR methodology."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Методика IAMSAR")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Справочный материал IAMSAR пока недоступен."))

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
