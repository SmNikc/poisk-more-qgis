from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDoubleSpinBox, QComboBox, QSpinBox, QPushButton, QHBoxLayout, QMessageBox
from PyQt5 import uic
import os
from qgis.core import QgsProject
class TwcDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        ui_path = os.path.join(os.path.dirname(__file__), 'dialog_twc.ui')
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            self.setup_ui()
        self.connect_buttons()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        lbl_type = QLabel("Тип течения")
        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["Морское течение", "1.0"])
        layout.addWidget(lbl_type)
        layout.addWidget(self.cmb_type)
        lbl_speed = QLabel("Скорость (узлы)")
        self.spin_speed = QDoubleSpinBox(value=1.0)
        layout.addWidget(lbl_speed)
        layout.addWidget(self.spin_speed)
        lbl_direction = QLabel("Направление (градусы)")
        self.spin_direction = QSpinBox(value=20)
        layout.addWidget(lbl_direction)
        layout.addWidget(self.spin_direction)
        lbl_error = QLabel("Погрешность (м/с)")
        self.spin_error = QDoubleSpinBox(value=0.3)
        layout.addWidget(lbl_error)
        layout.addWidget(self.spin_error)
        lbl_wind_factor = QLabel("Ветровой фактор")
        self.spin_wind_factor = QDoubleSpinBox(value=0.03)
        layout.addWidget(lbl_wind_factor)
        layout.addWidget(self.spin_wind_factor)
        self.btn_cancel = QPushButton("Отмена")
        self.btn_save = QPushButton("Сохранить")
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_cancel)
        hbox.addWidget(self.btn_save)
        layout.addLayout(hbox)
        self.setLayout(layout)
    def connect_buttons(self):
        self.btn_cancel.clicked.connect(self.close)
        self.btn_save.clicked.connect(self.save_twc)
    def save_twc(self):
        data = self.get_data()
        QgsProject.instance().writeEntry("PoiskMore", "twc_data", str(data))
        QMessageBox.information(self, "Сохранено", "Данные течения сохранены")
    def get_data(self):
        return {
            'type': self.cmb_type.currentText(),
            'speed': self.spin_speed.value(),
            'direction': self.spin_direction.value(),
            'error': self.spin_error.value(),
            'wind_factor': self.spin_wind_factor.value()
        }