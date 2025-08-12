from PyQt5.QtWidgets import QDialog, QDoubleSpinBox, QSpinBox, QPushButton, QVBoxLayout, QMessageBox, QLabel
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QDateTimeEdit  # Импорт QDateTimeEdit из QtWidgets

class WeatherDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Погода:"))
        layout.addWidget(QLabel("Скорость ветра (узлы):"))
        self.wind_speed = QDoubleSpinBox(minimum=0, value=10.0)
        layout.addWidget(self.wind_speed)
        layout.addWidget(QLabel("Направление ветра (градусы):"))
        self.wind_dir = QSpinBox(minimum=0, maximum=360, value=0)
        layout.addWidget(self.wind_dir)
        layout.addWidget(QLabel("Скорость течения (узлы):"))
        self.current_speed = QDoubleSpinBox(minimum=0, value=2.0)
        layout.addWidget(self.current_speed)
        layout.addWidget(QLabel("Направление течения (градусы):"))
        self.current_dir = QSpinBox(minimum=0, maximum=360, value=90)
        layout.addWidget(self.current_dir)
        layout.addWidget(QLabel("Время (часы):"))
        self.time_hours = QDoubleSpinBox(minimum=0, value=3.0)
        layout.addWidget(self.time_hours)
        btn = QPushButton("Сохранить")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)

    def save(self):
        self.accept()