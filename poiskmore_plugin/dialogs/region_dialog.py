from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QDateTimeEdit, QLineEdit
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QDoubleValidator
try:
    from ..controllers.region_create import RegionCreateController
    CREATE_FUNC = None
except ImportError:  # support old plugin builds without the controller class
    from ..controllers.region_create import create_region as CREATE_FUNC
    RegionCreateController = None
from PyQt5.QtWidgets import QMessageBox

class RegionDialog(QDialog):
    def __init__(self, iface, layer_manager):
        super().__init__()
        self.setWindowTitle("Создание района поиска")
        if RegionCreateController is not None:
            self.controller = RegionCreateController(iface, layer_manager)
        else:
            self.controller = None
            self.iface = iface
            self.layer_manager = layer_manager
        self.name_edit = QLineEdit(self)
        self.start_time = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.daylight_edit = QLineEdit(self)
        validator = QDoubleValidator(0.0, 24.0, 2, self)
        self.daylight_edit.setValidator(validator)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Название района:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel("Начало операции:"))
        layout.addWidget(self.start_time)
        layout.addWidget(QLabel("Световой день (ч):"))
        layout.addWidget(self.daylight_edit)
        self.ok_button = QPushButton("Построить", self)
        self.ok_button.clicked.connect(self.build_region)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def build_region(self):
        name = self.name_edit.text()
        start = self.start_time.dateTime()
        daylight_text = self.daylight_edit.text()
        if not name or not daylight_text:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        try:
            daylight = float(daylight_text)
            if self.controller is not None:
                self.controller.create_region(name, start, daylight)
            else:
                CREATE_FUNC(name, start, daylight)
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат для светового дня!")