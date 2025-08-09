from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDoubleSpinBox, QSpinBox, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QDateTimeEdit
from PyQt5 import uic
import os
class AswDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        ui_path = os.path.join(os.path.dirname(__file__), 'dialog_asw.ui')
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            self.setup_ui()
        self.connect_buttons()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        lbl_speed = QLabel("Скорость (узлы)")
        self.spin_speed = QDoubleSpinBox(value=38.9)
        layout.addWidget(lbl_speed)
        layout.addWidget(self.spin_speed)
        lbl_direction = QLabel("Направление (градусы)")
        self.spin_direction = QSpinBox(value=90)
        layout.addWidget(lbl_direction)
        layout.addWidget(self.spin_direction)
        lbl_actual_from = QLabel("Актуально с")
        self.datetime_from = QDateTimeEdit()
        self.datetime_from.setDateTime(QDateTime.fromString("22.07.25 21:02", "dd.MM.yy hh:mm"))
        layout.addWidget(lbl_actual_from)
        layout.addWidget(self.datetime_from)
        lbl_actual_to = QLabel("Актуально по")
        self.datetime_to = QDateTimeEdit()
        self.datetime_to.setDateTime(QDateTime.fromString("23.07.25 10:02", "dd.MM.yy hh:mm"))
        layout.addWidget(lbl_actual_to)
        layout.addWidget(self.datetime_to)
        self.btn_cancel = QPushButton("Отмена")
        self.btn_calculate = QPushButton("Рассчитать")
        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_cancel)
        hbox.addWidget(self.btn_calculate)
        layout.addLayout(hbox)
        self.setLayout(layout)
    def connect_buttons(self):
        self.btn_cancel.clicked.connect(self.close)
        self.btn_calculate.clicked.connect(self.calculate_asw)
    def calculate_asw(self):
        speed = self.spin_speed.value()
        direction = self.spin_direction.value()
        QMessageBox.information(self, "Расчет", f"ASW рассчитан: {speed} узлов, {direction} градусов")
    def get_params(self):
        return {
            'speed': self.spin_speed.value(),
            'direction': self.spin_direction.value(),
            'from': self.datetime_from.dateTime(),
            'to': self.datetime_to.dateTime()
        }