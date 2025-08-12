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
    QCheckBox,
    QWidget,
)
from PyQt5.QtCore import QDateTime
from math import cos, sin, radians

class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_conn = sqlite3.connect('incidents.db')
        self.cursor = self.db_conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY, name TEXT, coords TEXT, datetime TEXT, description TEXT, object_type TEXT, aviation TEXT, additional TEXT, owner TEXT, operator TEXT, wind_speed REAL, wind_dir INTEGER, current_speed REAL, current_dir INTEGER, wave_height REAL, air_temp REAL, water_temp REAL, asw REAL, twc REAL)')
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Вкладка 1: Объект аварийного случая / Местоположение
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.addWidget(QLabel("Характер аварийной ситуации:"))
        self.incident_type = QComboBox()
        self.incident_type.addItems(["Столкновение", "Пожар", "Человек за бортом", "Другое"])
        tab1_layout.addWidget(self.incident_type)
        tab1_layout.addWidget(QLabel("Размеры (Д х Ш х Осадка):"))
        self.dimensions = QLineEdit()
        tab1_layout.addWidget(self.dimensions)
        tab1_layout.addWidget(QLabel("MMSI:"))
        self.mmsi = QLineEdit()
        tab1_layout.addWidget(self.mmsi)
        tab1_layout.addWidget(QLabel("IMO:"))
        self.imo = QLineEdit()
        tab1_layout.addWidget(self.imo)
        tab1_layout.addWidget(QLabel("Цвет корпуса:"))
        self.hull_color = QLineEdit()
        tab1_layout.addWidget(self.hull_color)
        tab1_layout.addWidget(QLabel("Цвет надстройки:"))
        self.superstructure_color = QLineEdit()
        tab1_layout.addWidget(self.superstructure_color)
        tab1_layout.addWidget(QLabel("Запас топлива на борту:"))
        self.fuel = QLineEdit()
        tab1_layout.addWidget(self.fuel)
        tab1_layout.addWidget(QLabel("№ на борту:"))
        self.board_number = QLineEdit()
        tab1_layout.addWidget(self.board_number)
        tab1_layout.addWidget(QLabel("Авиационное оборудование:"))
        self.aviation = QLineEdit()
        tab1_layout.addWidget(self.aviation)
        tab1_layout.addWidget(QLabel("Дополнительно:"))
        self.additional = QTextEdit()
        tab1_layout.addWidget(self.additional)
        tabs.addTab(tab1, "Объект / Местоположение")

        # Вкладка 2: Объекты поиска
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QLabel("Первый объект поиска:"))
        self.first_object = QLineEdit()
        tab2_layout.addWidget(self.first_object)
        tab2_layout.addWidget(QLabel("Аварийное оборудование:"))
        self.emergency_equip = QLineEdit()
        tab2_layout.addWidget(self.emergency_equip)
        tab2_layout.addWidget(QLabel("Второй объект поиска:"))
        self.second_object = QLineEdit()
        tab2_layout.addWidget(self.second_object)
        tabs.addTab(tab2, "Объекты поиска")

        # Вкладка 3: Дополнительная информация
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        tab3_layout.addWidget(QLabel("Владелец:"))
        self.owner = QLineEdit()
        tab3_layout.addWidget(self.owner)
        tab3_layout.addWidget(QLabel("Оператор:"))
        self.operator = QLineEdit()
        tab3_layout.addWidget(self.operator)
        tab3_layout.addWidget(QLabel("ФИО:"))
        self.fio = QLineEdit()
        tab3_layout.addWidget(self.fio)
        tab3_layout.addWidget(QLabel("Телефон:"))
        self.phone = QLineEdit()
        tab3_layout.addWidget(self.phone)
        tab3_layout.addWidget(QLabel("Адрес:"))
        self.address = QLineEdit()
        tab3_layout.addWidget(self.address)
        tab3_layout.addWidget(QLabel("Число лиц в опасности:"))
        self.num_people = QSpinBox(minimum=0)
        tab3_layout.addWidget(self.num_people)
        tab3_layout.addWidget(QLabel("Требуемая помощь:"))
        self.help_needed = QLineEdit()
        tab3_layout.addWidget(self.help_needed)
        tab3_layout.addWidget(QLabel("Координирующий МСКЦ:"))
        self.mskc = QLineEdit("MCKUJocal")
        tab3_layout.addWidget(self.mskc)
        tab3_layout.addWidget(QLabel("Профиль:"))
        self.profile = QLineEdit("MCKUJocal")
        tab3_layout.addWidget(self.profile)
        tabs.addTab(tab3, "Дополнительная информация")

        # Вкладка 4: Погода
        tab4 = QWidget()
        tab4_layout = QVBoxLayout(tab4)
        tab4_layout.addWidget(QLabel("Прогноз погоды:"))
        tab4_layout.addWidget(QLabel("Ветер Скорость (узлы):"))
        self.wind_speed = QDoubleSpinBox(minimum=0)
        tab4_layout.addWidget(self.wind_speed)
        tab4_layout.addWidget(QLabel("Направление (градусы):"))
        self.wind_dir = QSpinBox(minimum=0, maximum=360)
        tab4_layout.addWidget(self.wind_dir)
        tab4_layout.addWidget(QLabel("Течение Скорость (узлы):"))
        self.current_speed = QDoubleSpinBox(minimum=0)
        tab4_layout.addWidget(self.current_speed)
        tab4_layout.addWidget(QLabel("Направление (градусы):"))
        self.current_dir = QSpinBox(minimum=0, maximum=360)
        tab4_layout.addWidget(self.current_dir)
        tab4_layout.addWidget(QLabel("Высота волны (метры):"))
        self.wave_height = QDoubleSpinBox(minimum=0)
        tab4_layout.addWidget(self.wave_height)
        tab4_layout.addWidget(QLabel("Осадки:"))
        self.precipitation = QLineEdit()
        tab4_layout.addWidget(self.precipitation)
        tab4_layout.addWidget(QLabel("Температура воздуха °C:"))
        self.air_temp = QDoubleSpinBox(minimum=-50, maximum=50)
        tab4_layout.addWidget(self.air_temp)
        tab4_layout.addWidget(QLabel("Восход солнца (UTC):"))
        self.sunrise = QDateTimeEdit()
        tab4_layout.addWidget(self.sunrise)
        tab4_layout.addWidget(QLabel("Видимость (мили):"))
        self.visibility = QDoubleSpinBox(minimum=0)
        tab4_layout.addWidget(self.visibility)
        tab4_layout.addWidget(QLabel("Лёд:"))
        self.ice = QLineEdit()
        tab4_layout.addWidget(self.ice)
        tab4_layout.addWidget(QLabel("Температура воды °C:"))
        self.water_temp = QDoubleSpinBox(minimum=-10, maximum=40)
        tab4_layout.addWidget(self.water_temp)
        tab4_layout.addWidget(QLabel("Заход солнца (UTC):"))
        self.sunset = QDateTimeEdit()
        tab4_layout.addWidget(self.sunset)
        tab4_layout.addWidget(QLabel("Источник погоды:"))
        self.weather_source = QLineEdit()
        tab4_layout.addWidget(self.weather_source)
        tab4_layout.addWidget(QLabel("Фактическая погода на месте:"))
        self.actual_weather = QTextEdit()
        tab4_layout.addWidget(self.actual_weather)
        btn_calc = QPushButton("Вычислить")
        btn_calc.clicked.connect(self.calculate)
        tab4_layout.addWidget(btn_calc)
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
        data = {
            'name': self.name.text(),
            'coords': self.coords.text(),
            'datetime': self.datetime.dateTime().toString(),
            'description': self.description.toPlainText(),
            'object_type': self.object_type.currentText(),
            'aviation': self.aviation.text(),
            'additional': self.additional.toPlainText(),
            'owner': self.owner.text(),
            'operator': self.operator.text(),
            'wind_speed': self.wind_speed.value(),
            'wind_dir': self.wind_dir.value(),
            'current_speed': self.current_speed.value(),
            'current_dir': self.current_dir.value(),
            'wave_height': self.wave_height.value(),
            'air_temp': self.air_temp.value(),
            'water_temp': self.water_temp.value(),
            'asw': self.asw,
            'twc': self.twc
        }
        if not data['name'] or not data['coords']:
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return
        self.cursor.execute('INSERT INTO incidents (name, coords, datetime, description, object_type, aviation, additional, owner, operator, wind_speed, wind_dir, current_speed, current_dir, wave_height, air_temp, water_temp, asw, twc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            (data['name'], data['coords'], data['datetime'], data['description'], data['object_type'], data['aviation'], data['additional'], data['owner'], data['operator'], data['wind_speed'], data['wind_dir'], data['current_speed'], data['current_dir'], data['wave_height'], data['air_temp'], data['water_temp'], data['asw'], data['twc']))
        self.db_conn.commit()
        self.accept()

    def __del__(self):
        self.db_conn.close()