from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, QHBoxLayout, QMessageBox
from PyQt5 import uic
import os
from alg.alg_zone import create_search_area
from qgis.core import QgsProject
class SearchAreaDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        ui_path = os.path.join(os.path.dirname(__file__), 'dialog_searcharea.ui')
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            self.setup_ui()
        self.connect_buttons()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        lbl_district = QLabel("Район поиска")
        self.txt_district = QLineEdit()
        layout.addWidget(lbl_district)
        layout.addWidget(self.txt_district)
        lbl_prefix = QLabel("Префикс подрайонов")
        self.txt_prefix = QLineEdit("A")
        layout.addWidget(lbl_prefix)
        layout.addWidget(self.txt_prefix)
        lbl_sru = QLabel("Средство определения местоположения SRU")
        self.cmb_sru = QComboBox()
        self.cmb_sru.addItems(["GNSS", "Другое"])
        layout.addWidget(lbl_sru)
        layout.addWidget(self.cmb_sru)
        lbl_start_time = QLabel("Дата и время начала операции (UTC)")
        self.spin_start_date = QSpinBox(value=23)
        self.spin_start_time = QDoubleSpinBox(value=7.25)
        hbox_start = QHBoxLayout()
        hbox_start.addWidget(lbl_start_time)
        hbox_start.addWidget(self.spin_start_date)
        hbox_start.addWidget(self.spin_start_time)
        layout.addLayout(hbox_start)
        lbl_duration = QLabel("Продолжительность поиска")
        self.spin_duration = QSpinBox(value=10)
        self.spin_duration_min = QSpinBox(value=0)
        hbox_duration = QHBoxLayout()
        hbox_duration.addWidget(lbl_duration)
        hbox_duration.addWidget(self.spin_duration)
        hbox_duration.addWidget(QLabel("час"))
        hbox_duration.addWidget(self.spin_duration_min)
        hbox_duration.addWidget(QLabel("мин"))
        layout.addLayout(hbox_duration)
        self.btn_build = QPushButton("Построить")
        self.btn_cancel = QPushButton("Отмена")
        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.btn_build)
        hbox_buttons.addWidget(self.btn_cancel)
        layout.addLayout(hbox_buttons)
        self.setLayout(layout)
    def connect_buttons(self):
        self.btn_cancel.clicked.connect(self.close)
        self.btn_build.clicked.connect(self.build_area)
    def build_area(self):
        params = self.get_params()
        area_layer = create_search_area(params, mode='two_points')
        QgsProject.instance().addMapLayer(area_layer)
        QMessageBox.information(self, "Построено", "Район поиска построен и добавлен в проект QGIS.")
    def get_params(self):
        return {
            'district': self.txt_district.text(),
            'prefix': self.txt_prefix.text(),
            'sru': self.cmb_sru.currentText(),
            'start_date': self.spin_start_date.value(),
            'start_time': self.spin_start_time.value(),
            'duration_hours': self.spin_duration.value(),
            'duration_min': self.spin_duration_min.value()
        }