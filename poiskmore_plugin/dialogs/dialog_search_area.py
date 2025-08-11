from PyQt5.QtWidgets import QDialog, QComboBox, QPushButton, QVBoxLayout, QLabel
class DialogSearchArea(QDialog):
def __init__(self, parent=None):
super().__init__(parent)
layout = QVBoxLayout(self)
layout.addWidget(QLabel("Создать район:"))
self.mode = QComboBox()
self.mode.addItems(["Поиск от двух исходных пунктов", "Поиск вдоль исходной линии", "Далеко разнесённые исходные пункты", "Ручное построение", "Поиск от одной исходной точки"])
layout.addWidget(self.mode)
btn = QPushButton("Создать")
btn.clicked.connect(self.create)
layout.addWidget(btn)
def create(self):
self.accept()