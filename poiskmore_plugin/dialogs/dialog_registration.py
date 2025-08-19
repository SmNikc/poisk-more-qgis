import sqlite3
from PyQt5.QtWidgets import (
    QDialog,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QTabWidget,
    QTextEdit,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
    QDateTimeEdit,
    QHBoxLayout,
    QGroupBox,
    QFormLayout,
    QWidget,
)
from PyQt5.QtCore import QDateTime
from math import cos, sin, radians
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_conn = sqlite3.connect('incidents.db')
        self.cursor = self.db_conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY, name TEXT, coords_lat_deg INTEGER, coords_lat_min REAL, coords_lat_dir TEXT, coords_lon_deg INTEGER, coords_lon_min REAL, coords_lon_dir TEXT, datetime TEXT, description TEXT, situation_type TEXT, object_type TEXT, aviation TEXT, hull_color TEXT, superstructure_color TEXT, fuel REAL, board_number TEXT, contacts TEXT, owner_name TEXT, operator_name TEXT, fio TEXT, phone TEXT, address TEXT, num_people INTEGER, help_needed TEXT, mskc TEXT, profile TEXT, wind_speed REAL, wind_dir INTEGER, current_speed REAL, current_dir INTEGER, wave_height REAL, precipitation TEXT, air_temp REAL, visibility REAL, ice TEXT, water_temp REAL, sunrise TEXT, sunset TEXT, weather_source TEXT, actual_weather TEXT, asw REAL, twc REAL)')
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Вкладка 1: Объект АС / Местоположение (по скриншоту №1)
        tab1 = QWidget()
        tab1_layout = QFormLayout(tab1)
        self.cmb_incident_type = QComboBox()
        self.cmb_incident_type.addItems(["Столкновение", "Пожар", "Человек за бортом", "Другое"])
        tab1_layout.addRow("Характер аварийной ситуации:", self.cmb_incident_type)
        self.txt_dimensions = QLineEdit()
        tab1_layout.addRow("Размеры (Д х Ш х Осадка):", self.txt_dimensions)
        self.txt_mmsi = QLineEdit()
        tab1_layout.addRow("MMSI:", self.txt_mmsi)
        self.txt_imo = QLineEdit()
        tab1_layout.addRow("IMO:", self.txt_imo)
        self.txt_hull_color = QLineEdit()
        tab1_layout.addRow("Цвет корпуса:", self.txt_hull_color)
        self.txt_superstructure_color = QLineEdit()
        tab1_layout.addRow("Цвет надстройки:", self.txt_superstructure_color)
        self.txt_fuel = QLineEdit()
        tab1_layout.addRow("Запас топлива на борту:", self.txt_fuel)
        self.txt_board_number = QLineEdit()
        tab1_layout.addRow("№ на борту:", self.txt_board_number)
        self.cmb_aviation = QComboBox()
        self.cmb_aviation.addItems(["Авиационное оборудование", "Другое"])
        tab1_layout.addRow("Авиационное оборудование:", self.cmb_aviation)
        self.txt_contacts = QLineEdit()
        tab1_layout.addRow("Контакты экипажа:", self.txt_contacts)
        self.txt_owner = QLineEdit()
        tab1_layout.addRow("Владельцы:", self.txt_owner)
        self.txt_operator = QLineEdit()
        tab1_layout.addRow("Оператор:", self.txt_operator)
        self.txt_fio = QLineEdit()
        tab1_layout.addRow("ФИО:", self.txt_fio)
        self.txt_phone = QLineEdit()
        tab1_layout.addRow("Телефон:", self.txt_phone)
        self.txt_address = QLineEdit()
        tab1_layout.addRow("Адрес:", self.txt_address)
        self.txt_additional = QTextEdit()
        tab1_layout.addRow("Дополнительно:", self.txt_additional)
        tabs.addTab(tab1, "Объект / Местоположение")

        # Вкладка 2: Объекты поиска (по скриншоту №2)
        tab2 = QWidget()
        tab2_layout = QFormLayout(tab2)
        self.txt_first_object = QLineEdit()
        tab2_layout.addRow("Первый объект поиска:", self.txt_first_object)
        self.cmb_emergency_equip = QComboBox()
        self.cmb_emergency_equip.addItems(["Аварийное оборудование", "Другое"])
        tab2_layout.addRow("Аварийное оборудование:", self.cmb_emergency_equip)
        self.txt_second_object = QLineEdit()
        tab2_layout.addRow("Второй объект поиска:", self.txt_second_object)
        tabs.addTab(tab2, "Объекты поиска")

        # Вкладка 3: Дополнительная информация (по скриншоту №3)
        tab3 = QWidget()
        tab3_layout = QFormLayout(tab3)
        self.spin_num_people = QSpinBox(minimum=0)
        tab3_layout.addRow("Число лиц в опасности:", self.spin_num_people)
        self.txt_help_needed = QLineEdit()
        tab3_layout.addRow("Требуемая помощь:", self.txt_help_needed)
        self.txt_mskc = QLineEdit("MCKUJocal")
        tab3_layout.addRow("Координирующий МСКЦ:", self.txt_mskc)
        self.txt_profile = QLineEdit("MCKUJocal")
        tab3_layout.addRow("Профиль:", self.txt_profile)
        tabs.addTab(tab3, "Дополнительная информация")

        # Вкладка 4: Погода (по скриншоту №4)
        tab4 = QWidget()
        tab4_layout = QFormLayout(tab4)
        self.wind_speed = QDoubleSpinBox(minimum=0)
        tab4_layout.addRow("Ветер Скорость (узлы):", self.wind_speed)
        self.wind_dir = QSpinBox(minimum=0, maximum=360)
        tab4_layout.addRow("Направление (градусы):", self.wind_dir)
        self.current_speed = QDoubleSpinBox(minimum=0)
        tab4_layout.addRow("Течение Скорость (узлы):", self.current_speed)
        self.current_dir = QSpinBox(minimum=0, maximum=360)
        tab4_layout.addRow("Направление (градусы):", self.current_dir)
        self.wave_height = QDoubleSpinBox(minimum=0)
        tab4_layout.addRow("Высота волны (метры):", self.wave_height)
        self.precipitation = QLineEdit()
        tab4_layout.addRow("Осадки:", self.precipitation)
        self.air_temp = QDoubleSpinBox(minimum=-50, maximum=50)
        tab4_layout.addRow("Температура воздуха °C:", self.air_temp)
        self.visibility = QDoubleSpinBox(minimum=0)
        tab4_layout.addRow("Видимость (мили):", self.visibility)
        self.ice = QLineEdit()
        tab4_layout.addRow("Лёд:", self.ice)
        self.water_temp = QDoubleSpinBox(minimum=-10, maximum=40)
        tab4_layout.addRow("Температура воды °C:", self.water_temp)
        self.sunrise = QDateTimeEdit()
        tab4_layout.addRow("Восход солнца (UTC):", self.sunrise)
        self.sunset = QDateTimeEdit()
        tab4_layout.addRow("Заход солнца (UTC):", self.sunset)
        self.weather_source = QLineEdit()
        tab4_layout.addRow("Источник погоды:", self.weather_source)
        self.actual_weather = QTextEdit()
        tab4_layout.addRow("Фактическая погода на месте:", self.actual_weather)
        btn_calc = QPushButton("Вычислить")
        btn_calc.clicked.connect(self.calculate)
        tab4_layout.addRow(btn_calc)
        tabs.addTab(tab4, "Погода")

        btn = QPushButton("Зарегистрировать")
        btn.clicked.connect(self.register)
        layout.addWidget(btn)

    def calculate(self):
        # Расчёт ASW (средний ветер)
        wind_speed = self.wind_speed.value()
        wind_dir = self.wind_dir.value()
        self.asw = wind_speed * cos(radians(wind_dir))  # Пример расчёта
        # Расчёт TWC (суммарное течение)
        current_speed = self.current_speed.value()
        current_dir = self.current_dir.value()
        self.twc = current_speed * sin(radians(current_dir))  # Пример расчёта
        QMessageBox.information(self, "Расчёт", f"ASW: {self.asw}\nTWC: {self.twc}")

    def register(self):
        data = self.collect_data()
        if not self.validate_data(data):
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return
        self.cursor.execute('INSERT INTO incidents (name, coords, datetime, description, object_type, aviation, additional, owner, operator, wind_speed, wind_dir, current_speed, current_dir, wave_height, air_temp, water_temp, asw, twc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            (data['name'], data['coords'], data['datetime'], data['description'], data['object_type'], data['aviation'], data['additional'], data['owner'], data['operator'], data['wind_speed'], data['wind_dir'], data['current_speed'], data['current_dir'], data['wave_height'], data['air_temp'], data['water_temp'], data['asw'], data['twc']))
        self.db_conn.commit()
        self.accept()

    def __del__(self):
        self.db_conn.close()
