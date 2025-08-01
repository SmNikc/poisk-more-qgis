from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from qgis.core import QgsPointXY
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp

class SruRoutingDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Маршрут SRU")
        layout = QVBoxLayout()
        self.start_edit = QLineEdit()
        validator = QRegExpValidator(QRegExp(r'^-?\d+\.?\d*,\s*-?\d+\.?\d*$'), self)
        self.start_edit.setValidator(validator)
        self.end_edit = QLineEdit()
        self.end_edit.setValidator(validator)
        layout.addWidget(QLabel("Координаты старта (x,y):"))
        layout.addWidget(self.start_edit)
        layout.addWidget(QLabel("Координаты цели (x,y):"))
        layout.addWidget(self.end_edit)
        self.ok_button = QPushButton("Построить")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def get_points(self):
        if not self.start_edit.hasAcceptableInput() or not self.end_edit.hasAcceptableInput():
            QMessageBox.warning(self, "Ошибка", "Неверный формат координат!")
            return None, None
        x1, y1 = map(float, self.start_edit.text().split(","))
        x2, y2 = map(float, self.end_edit.text().split(","))
        return QgsPointXY(x1, y1), QgsPointXY(x2, y2)