from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton
from PyQt5.QtWidgets import QMessageBox

class ProbabilityDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Параметры карты вероятности")
        layout = QVBoxLayout()
        self.radius_edit = QLineEdit()
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(10)
        self.count_spin.setMaximum(10000)
        layout.addWidget(QLabel("Радиус области (градусы):"))
        layout.addWidget(self.radius_edit)
        layout.addWidget(QLabel("Количество точек:"))
        layout.addWidget(self.count_spin)
        self.ok_button = QPushButton("Сгенерировать")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def get_parameters(self):
        try:
            radius = float(self.radius_edit.text())
            if radius < 0:
                raise ValueError("Радиус не может быть отрицательным!")
            return radius, self.count_spin.value()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return 0.0, 10