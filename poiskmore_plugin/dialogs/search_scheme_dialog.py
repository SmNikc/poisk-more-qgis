pythonfrom PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QMessageBox

class SearchSchemeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Схема поиска — Expanding Square")
        layout = QVBoxLayout()
        self.spacing_edit = QLineEdit()
        validator = QDoubleValidator(0.1, 100.0, 2, self)
        self.spacing_edit.setValidator(validator)
        self.legs_spin = QSpinBox()
        self.legs_spin.setMinimum(1)
        self.legs_spin.setMaximum(20)
        layout.addWidget(QLabel("Шаг (spacing), км:"))
        layout.addWidget(self.spacing_edit)
        layout.addWidget(QLabel("Количество отрезков:"))
        layout.addWidget(self.legs_spin)
        self.ok_button = QPushButton("Построить")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def get_parameters(self):
        spacing_text = self.spacing_edit.text()
        if not spacing_text:
            QMessageBox.warning(self, "Ошибка", "Укажите шаг!")
            return None, None
        return float(spacing_text), self.legs_spin.value()