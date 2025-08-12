from PyQt5.QtWidgets import QDialog, QComboBox, QPushButton, QVBoxLayout, QLabel

class SearchAreaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Район поиска:"))
        self.mode = QComboBox()
        self.mode.addItems(["Поиск от двух точек", "Поиск вдоль линии", "Далеко разнесенные точки", "Ручное построение", "Поиск от одной точки"])
        layout.addWidget(self.mode)
        btn = QPushButton("Создать")
        btn.clicked.connect(self.create)
        layout.addWidget(btn)

    def create(self):
        self.accept()