from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class AboutDialog(QDialog):
    """Simple about dialog for the plugin."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Плагин \"Поиск-Море\""))

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
