from PyQt5.QtWidgets import QDialog, QVBoxLayout
from forms.embedded.embedded_map_widget import EmbeddedMapWidget


class OperationEditor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Операция поиска и спасания")
        self.resize(900, 600)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.map_widget = EmbeddedMapWidget(self)
        layout.addWidget(self.map_widget)