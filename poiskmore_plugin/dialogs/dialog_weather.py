from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDoubleSpinBox, QLineEdit, QSpinBox, QPushButton, QHBoxLayout, QMessageBox
from PyQt5 import uic
import os
from qgis.core import QgsProject
class WeatherDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        ui_path = os.path.join(os.path.dirname(__file__), 'dialog_weather.ui')
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            self.setup_ui()
        self.connect_buttons()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        lbl_wind = QLabel("Ветер")
        self.spin_wind_speed = QDoubleSpinBox(value=1.0)
        self.spin_wind_dir = QSpinBox(value=20)
        layout.addWidget(lbl_wind)
        layout.addWidget(QLabel("Скорость (м/с):"))
        layout.addWidget(self.spin_wind_speed)
        layout.addWidget(QLabel("Направление (градусы):"))
        layout.addWidget(self.spin_wind_dir)
        lbl_waves = QLabel("Волны")
        self.spin_wave_height = QDoubleSpinBox(value=1.39)
        self.spin_wave_period = QSpinBox(value=300)
        layout.addWidget(lbl_waves)
        layout.addWidget(QLabel("Высота (м):"))
        layout.addWidget(self.spin_wave_height)
        layout.addWidget(QLabel("Период (с):"))
        layout.addWidget(self.spin_wave_period)
        self.txt_precip = QLineEdit()
        self.spin_air_temp = QDoubleSpinBox(value=0.3)
        self.spin_water_temp = QDoubleSpinBox(value=16.49)
        layout.addWidget(QLabel("Осадки:"))
        layout.addWidget(self.txt_precip)
        layout.addWidget(QLabel("Температура воздуха (°C):"))
        layout.addWidget(self.spin_air_temp)
        layout.addWidget(QLabel("Температура воды (°C):"))
        layout.addWidget(self.spin_water_temp)
        self.btn_save = QPushButton("Сохранить")
        self.btn_cancel = QPushButton("Отмена")
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_save)
        hbox.addWidget(self.btn_cancel)
        layout.addLayout(hbox)
        self.setLayout(layout)
    def connect_buttons(self):
        self.btn_cancel.clicked.connect(self.close)
        self.btn_save.clicked.connect(self.save_weather)
    def save_weather(self):
        data = self.get_data()
        QgsProject.instance().writeEntry("PoiskMore", "weather_data", str(data))
        QMessageBox.information(self, "Сохранено", "Данные погоды сохранены")
    def get_data(self):
        return {
            'wind_speed': self.spin_wind_speed.value(),
            'wind_dir': self.spin_wind_dir.value(),
            'wave_height': self.spin_wave_height.value(),
            'wave_period': self.spin_wave_period.value(),
            'precip': self.txt_precip.text(),
            'air_temp': self.spin_air_temp.value(),
            'water_temp': self.spin_water_temp.value()
        }