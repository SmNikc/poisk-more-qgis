from PyQt5.QtWidgets import QDialog, QVBoxLayout
from forms.embedded.embedded_map_widget import EmbeddedMapWidget


class SearchAreaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Редактор района поиска")
        self.resize(900, 600)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Вставляем карту
        self.map_widget = EmbeddedMapWidget(self)
        layout.addWidget(self.map_widget)