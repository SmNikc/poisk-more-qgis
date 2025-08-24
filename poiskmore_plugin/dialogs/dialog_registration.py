# -*- coding: utf-8 -*-
"""
Диалог регистрации аварийного случая для плагина ПОИСК-МОРЕ
Полная версия с исправлениями критических ошибок
"""

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

class RegistrationDialog(QDialog):
    """Диалог регистрации нового аварийного случая"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация аварийного случая")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # Инициализация БД
        self.init_database()
        
        # Создание интерфейса
        self.setup_ui()
        
        # Инициализация значений по умолчанию
        self.asw = 0
        self.twc = 0
        
    def init_database(self):
        """Инициализация подключения к БД"""
        try:
            self.db_conn = sqlite3.connect('incidents.db')
            self.cursor = self.db_conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY,
                    case_number TEXT,
                    name TEXT,
                    coords_lat REAL,
                    coords_lon REAL,
                    datetime TEXT,
                    description TEXT,
                    situation_type TEXT,
                    object_type TEXT,
                    aviation TEXT,
                    hull_color TEXT,
                    superstructure_color TEXT,
                    fuel REAL,
                    board_number TEXT,
                    contacts TEXT,
                    owner_name TEXT,
                    operator_name TEXT,
                    fio TEXT,
                    phone TEXT,
                    address TEXT,
                    num_people INTEGER,
                    help_needed TEXT,
                    mskc TEXT,
                    profile TEXT,
                    wind_speed REAL,
                    wind_dir INTEGER,
                    current_speed REAL,
                    current_dir INTEGER,
                    wave_height REAL,
                    precipitation TEXT,
                    air_temp REAL,
                    visibility REAL,
                    ice TEXT,
                    water_temp REAL,
                    sunrise TEXT,
                    sunset TEXT,
                    weather_source TEXT,
                    actual_weather TEXT,
                    asw REAL,
                    twc REAL,
                    status TEXT DEFAULT 'active'
                )
            ''')
            self.db_conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось создать БД: {str(e)}")
            self.db_conn = None
            self.cursor = None
    
    def setup_ui(self):
        """Создание интерфейса"""
        layout = QVBoxLayout(self)
        
        # Основная информация
        info_group = QGroupBox("Основная информация")
        info_layout = QFormLayout()
        
        self.txt_case_number = QLineEdit()
        self.txt_case_number.setPlaceholderText("Автоматически")
        info_layout.addRow("Номер дела:", self.txt_case_number)
        
        self.dt_incident = QDateTimeEdit(QDateTime.currentDateTime())
        info_layout.addRow("Дата/время:", self.dt_incident)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Вкладки
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Вкладка 1: Объект АС / Местоположение
        tab1 = self.create_tab1()
        tabs.addTab(tab1, "Объект / Местоположение")
        
        # Вкладка 2: Объекты поиска
        tab2 = self.create_tab2()
        tabs.addTab(tab2, "Объекты поиска")
        
        # Вкладка 3: Дополнительная информация
        tab3 = self.create_tab3()
        tabs.addTab(tab3, "Дополнительная информация")
        
        # Вкладка 4: Погода
        tab4 = self.create_tab4()
        tabs.addTab(tab4, "Погода")
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        btn_register = QPushButton("Зарегистрировать")
        btn_register.clicked.connect(self.register)
        btn_layout.addWidget(btn_register)
        
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
    
    def create_tab1(self):
        """Вкладка 1: Объект АС / Местоположение"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Координаты
        coord_layout = QHBoxLayout()
        self.spin_lat_deg = QSpinBox(minimum=-90, maximum=90)
        self.spin_lat_min = QDoubleSpinBox(minimum=0, maximum=59.999)
        self.cmb_lat_dir = QComboBox()
        self.cmb_lat_dir.addItems(["N", "S"])
        coord_layout.addWidget(QLabel("Град:"))
        coord_layout.addWidget(self.spin_lat_deg)
        coord_layout.addWidget(QLabel("Мин:"))
        coord_layout.addWidget(self.spin_lat_min)
        coord_layout.addWidget(self.cmb_lat_dir)
        layout.addRow("Широта:", coord_layout)
        
        coord_lon_layout = QHBoxLayout()
        self.spin_lon_deg = QSpinBox(minimum=-180, maximum=180)
        self.spin_lon_min = QDoubleSpinBox(minimum=0, maximum=59.999)
        self.cmb_lon_dir = QComboBox()
        self.cmb_lon_dir.addItems(["E", "W"])
        coord_lon_layout.addWidget(QLabel("Град:"))
        coord_lon_layout.addWidget(self.spin_lon_deg)
        coord_lon_layout.addWidget(QLabel("Мин:"))
        coord_lon_layout.addWidget(self.spin_lon_min)
        coord_lon_layout.addWidget(self.cmb_lon_dir)
        layout.addRow("Долгота:", coord_lon_layout)
        
        # Характер ситуации
        self.cmb_incident_type = QComboBox()
        self.cmb_incident_type.addItems([
            "Столкновение",
            "Пожар",
            "Человек за бортом",
            "Посадка на мель",
            "Потеря управления",
            "Затопление",
            "Другое"
        ])
        layout.addRow("Характер аварийной ситуации:", self.cmb_incident_type)
        
        # Объект
        self.txt_object_name = QLineEdit()
        layout.addRow("Название объекта:", self.txt_object_name)
        
        self.cmb_object_type = QComboBox()
        self.cmb_object_type.addItems([
            "Морское судно",
            "Воздушное судно",
            "Спасательный плот",
            "Человек в воде",
            "Другое"
        ])
        layout.addRow("Тип объекта:", self.cmb_object_type)
        
        self.txt_dimensions = QLineEdit()
        self.txt_dimensions.setPlaceholderText("Д х Ш х Осадка")
        layout.addRow("Размеры (м):", self.txt_dimensions)
        
        self.txt_mmsi = QLineEdit()
        layout.addRow("MMSI:", self.txt_mmsi)
        
        self.txt_imo = QLineEdit()
        layout.addRow("IMO:", self.txt_imo)
        
        self.txt_hull_color = QLineEdit()
        layout.addRow("Цвет корпуса:", self.txt_hull_color)
        
        self.txt_superstructure_color = QLineEdit()
        layout.addRow("Цвет надстройки:", self.txt_superstructure_color)
        
        self.txt_fuel = QLineEdit()
        layout.addRow("Запас топлива:", self.txt_fuel)
        
        self.txt_board_number = QLineEdit()
        layout.addRow("№ на борту:", self.txt_board_number)
        
        return tab
    
    def create_tab2(self):
        """Вкладка 2: Объекты поиска"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.txt_first_object = QLineEdit()
        self.txt_first_object.setPlaceholderText("Например: Спасательный плот на 10 человек")
        layout.addRow("Первый объект поиска:", self.txt_first_object)
        
        self.cmb_emergency_equip = QComboBox()
        self.cmb_emergency_equip.addItems([
            "EPIRB",
            "SART",
            "Спасательный плот",
            "Спасательная шлюпка",
            "Спасательный жилет",
            "Пиротехника",
            "Другое"
        ])
        layout.addRow("Аварийное оборудование:", self.cmb_emergency_equip)
        
        self.txt_second_object = QLineEdit()
        self.txt_second_object.setPlaceholderText("Дополнительные объекты")
        layout.addRow("Второй объект поиска:", self.txt_second_object)
        
        self.txt_search_notes = QTextEdit()
        self.txt_search_notes.setMaximumHeight(100)
        layout.addRow("Примечания:", self.txt_search_notes)
        
        return tab
    
    def create_tab3(self):
        """Вкладка 3: Дополнительная информация"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.spin_num_people = QSpinBox(minimum=0, maximum=9999)
        layout.addRow("Число лиц в опасности:", self.spin_num_people)
        
        self.txt_help_needed = QLineEdit()
        self.txt_help_needed.setPlaceholderText("Медицинская помощь, эвакуация и т.д.")
        layout.addRow("Требуемая помощь:", self.txt_help_needed)
        
        self.txt_owner = QLineEdit()
        layout.addRow("Владелец:", self.txt_owner)
        
        self.txt_operator = QLineEdit()
        layout.addRow("Оператор:", self.txt_operator)
        
        self.txt_contacts = QLineEdit()
        layout.addRow("Контакты экипажа:", self.txt_contacts)
        
        self.txt_fio = QLineEdit()
        layout.addRow("ФИО заявителя:", self.txt_fio)
        
        self.txt_phone = QLineEdit()
        layout.addRow("Телефон:", self.txt_phone)
        
        self.txt_address = QLineEdit()
        layout.addRow("Адрес:", self.txt_address)
        
        self.txt_mskc = QLineEdit("МСКЦ Астрахань")
        layout.addRow("Координирующий МСКЦ:", self.txt_mskc)
        
        self.txt_profile = QLineEdit("Местный")
        layout.addRow("Профиль:", self.txt_profile)
        
        self.txt_additional = QTextEdit()
        self.txt_additional.setMaximumHeight(100)
        layout.addRow("Дополнительно:", self.txt_additional)
        
        return tab
    
    def create_tab4(self):
        """Вкладка 4: Погода"""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Ветер
        wind_layout = QHBoxLayout()
        self.wind_speed = QDoubleSpinBox(minimum=0, maximum=100)
        self.wind_dir = QSpinBox(minimum=0, maximum=360)
        wind_layout.addWidget(QLabel("Скорость (узлы):"))
        wind_layout.addWidget(self.wind_speed)
        wind_layout.addWidget(QLabel("Направление (°):"))
        wind_layout.addWidget(self.wind_dir)
        layout.addRow("Ветер:", wind_layout)
        
        # Течение
        current_layout = QHBoxLayout()
        self.current_speed = QDoubleSpinBox(minimum=0, maximum=10)
        self.current_dir = QSpinBox(minimum=0, maximum=360)
        current_layout.addWidget(QLabel("Скорость (узлы):"))
        current_layout.addWidget(self.current_speed)
        current_layout.addWidget(QLabel("Направление (°):"))
        current_layout.addWidget(self.current_dir)
        layout.addRow("Течение:", current_layout)
        
        self.wave_height = QDoubleSpinBox(minimum=0, maximum=20)
        layout.addRow("Высота волны (м):", self.wave_height)
        
        self.precipitation = QLineEdit()
        self.precipitation.setPlaceholderText("Нет / Дождь / Снег / Туман")
        layout.addRow("Осадки:", self.precipitation)
        
        self.air_temp = QDoubleSpinBox(minimum=-50, maximum=50)
        layout.addRow("Температура воздуха °C:", self.air_temp)
        
        self.visibility = QDoubleSpinBox(minimum=0, maximum=50)
        layout.addRow("Видимость (мили):", self.visibility)
        
        self.ice = QLineEdit()
        self.ice.setPlaceholderText("Нет / Блинчатый / Сплоченный")
        layout.addRow("Лёд:", self.ice)
        
        self.water_temp = QDoubleSpinBox(minimum=-10, maximum=40)
        layout.addRow("Температура воды °C:", self.water_temp)
        
        self.sunrise = QDateTimeEdit()
        layout.addRow("Восход солнца (UTC):", self.sunrise)
        
        self.sunset = QDateTimeEdit()
        layout.addRow("Заход солнца (UTC):", self.sunset)
        
        self.weather_source = QLineEdit()
        self.weather_source.setPlaceholderText("Meteo.ru / Gismeteo / Местные данные")
        layout.addRow("Источник погоды:", self.weather_source)
        
        self.actual_weather = QTextEdit()
        self.actual_weather.setMaximumHeight(60)
        layout.addRow("Фактическая погода:", self.actual_weather)
        
        # Кнопка расчета
        btn_calc = QPushButton("Вычислить ASW/TWC")
        btn_calc.clicked.connect(self.calculate)
        layout.addRow("", btn_calc)
        
        # Результаты расчета
        self.lbl_asw = QLabel("ASW: не рассчитано")
        self.lbl_twc = QLabel("TWC: не рассчитано")
        layout.addRow("Результаты:", self.lbl_asw)
        layout.addRow("", self.lbl_twc)
        
        return tab
    
    def calculate(self):
        """Расчет ASW и TWC"""
        try:
            # Расчёт ASW (Average Surface Wind - средний ветер)
            wind_speed = self.wind_speed.value()
            wind_dir = self.wind_dir.value()
            self.asw = wind_speed * cos(radians(wind_dir))
            
            # Расчёт TWC (Total Water Current - суммарное течение)
            current_speed = self.current_speed.value()
            current_dir = self.current_dir.value()
            self.twc = current_speed * sin(radians(current_dir))
            
            # Обновление отображения
            self.lbl_asw.setText(f"ASW: {self.asw:.2f} узлов")
            self.lbl_twc.setText(f"TWC: {self.twc:.2f} узлов")
            
            QMessageBox.information(
                self,
                "Расчёт выполнен",
                f"ASW: {self.asw:.2f} узлов\nTWC: {self.twc:.2f} узлов"
            )
        except Exception as e:
            QMessageBox.warning(self, "Ошибка расчета", str(e))
    
    def collect_data(self):
        """Сбор данных из формы"""
        # Преобразование координат в десятичные градусы
        lat = self.spin_lat_deg.value() + self.spin_lat_min.value() / 60
        if self.cmb_lat_dir.currentText() == "S":
            lat = -lat
        
        lon = self.spin_lon_deg.value() + self.spin_lon_min.value() / 60
        if self.cmb_lon_dir.currentText() == "W":
            lon = -lon
        
        # Генерация номера дела если не указан
        case_number = self.txt_case_number.text()
        if not case_number:
            case_number = f"AC-{QDateTime.currentDateTime().toString('yyyyMMdd-HHmmss')}"
        
        data = {
            'case_number': case_number,
            'name': self.txt_object_name.text(),
            'coords_lat': lat,
            'coords_lon': lon,
            'coords': f"{lat:.4f}, {lon:.4f}",
            'datetime': self.dt_incident.dateTime().toString('yyyy-MM-dd HH:mm:ss'),
            'description': self.txt_additional.toPlainText(),
            'situation_type': self.cmb_incident_type.currentText(),
            'object_type': self.cmb_object_type.currentText(),
            'aviation': '',  # Не используется в новой версии
            'hull_color': self.txt_hull_color.text(),
            'superstructure_color': self.txt_superstructure_color.text(),
            'fuel': self.txt_fuel.text(),
            'board_number': self.txt_board_number.text(),
            'contacts': self.txt_contacts.text(),
            'owner': self.txt_owner.text(),
            'operator': self.txt_operator.text(),
            'fio': self.txt_fio.text(),
            'phone': self.txt_phone.text(),
            'address': self.txt_address.text(),
            'num_people': self.spin_num_people.value(),
            'help_needed': self.txt_help_needed.text(),
            'mskc': self.txt_mskc.text(),
            'profile': self.txt_profile.text(),
            'first_object': self.txt_first_object.text(),
            'emergency_equip': self.cmb_emergency_equip.currentText(),
            'second_object': self.txt_second_object.text(),
            'search_notes': self.txt_search_notes.toPlainText(),
            'wind_speed': self.wind_speed.value(),
            'wind_dir': self.wind_dir.value(),
            'current_speed': self.current_speed.value(),
            'current_dir': self.current_dir.value(),
            'wave_height': self.wave_height.value(),
            'precipitation': self.precipitation.text(),
            'air_temp': self.air_temp.value(),
            'visibility': self.visibility.value(),
            'ice': self.ice.text(),
            'water_temp': self.water_temp.value(),
            'sunrise': self.sunrise.dateTime().toString('HH:mm'),
            'sunset': self.sunset.dateTime().toString('HH:mm'),
            'weather_source': self.weather_source.text(),
            'actual_weather': self.actual_weather.toPlainText(),
            'asw': self.asw,
            'twc': self.twc,
            'status': 'active',
            'additional': self.txt_additional.toPlainText()
        }
        
        return data
    
    def validate_data(self, data):
        """Валидация данных"""
        errors = []
        
        # Проверка обязательных полей
        if not data['name']:
            errors.append("Не указано название объекта")
        
        if not data['situation_type']:
            errors.append("Не указан характер аварийной ситуации")
        
        if data['coords_lat'] == 0 and data['coords_lon'] == 0:
            errors.append("Не указаны координаты")
        
        # Проверка диапазонов
        if not (-90 <= data['coords_lat'] <= 90):
            errors.append("Широта должна быть от -90 до 90")
        
        if not (-180 <= data['coords_lon'] <= 180):
            errors.append("Долгота должна быть от -180 до 180")
        
        if errors:
            QMessageBox.warning(
                self,
                "Ошибки валидации",
                "Обнаружены следующие ошибки:\n\n" + "\n".join(errors)
            )
            return False
        
        return True
    
    def get_data(self):
        """Получить данные формы (для совместимости с mainPlugin.py)"""
        return self.collect_data()
    
    def register(self):
        """Регистрация аварийного случая"""
        data = self.collect_data()
        
        if not self.validate_data(data):
            return
        
        if not self.cursor:
            QMessageBox.critical(self, "Ошибка", "База данных недоступна")
            return
        
        try:
            # Сохранение в БД
            self.cursor.execute('''
                INSERT INTO incidents (
                    case_number, name, coords_lat, coords_lon, datetime,
                    description, situation_type, object_type, hull_color,
                    superstructure_color, fuel, board_number, contacts,
                    owner_name, operator_name, fio, phone, address,
                    num_people, help_needed, mskc, profile,
                    wind_speed, wind_dir, current_speed, current_dir,
                    wave_height, precipitation, air_temp, visibility,
                    ice, water_temp, sunrise, sunset, weather_source,
                    actual_weather, asw, twc, status
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?
                )
            ''', (
                data['case_number'], data['name'], data['coords_lat'],
                data['coords_lon'], data['datetime'], data['description'],
                data['situation_type'], data['object_type'], data['hull_color'],
                data['superstructure_color'], data['fuel'], data['board_number'],
                data['contacts'], data['owner'], data['operator'], data['fio'],
                data['phone'], data['address'], data['num_people'],
                data['help_needed'], data['mskc'], data['profile'],
                data['wind_speed'], data['wind_dir'], data['current_speed'],
                data['current_dir'], data['wave_height'], data['precipitation'],
                data['air_temp'], data['visibility'], data['ice'],
                data['water_temp'], data['sunrise'], data['sunset'],
                data['weather_source'], data['actual_weather'],
                data['asw'], data['twc'], data['status']
            ))
            
            self.db_conn.commit()
            
            QMessageBox.information(
                self,
                "Успех",
                f"Аварийный случай {data['case_number']} зарегистрирован"
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка сохранения",
                f"Не удалось сохранить данные:\n{str(e)}"
            )
    
    def __del__(self):
        """Деструктор - закрытие БД"""
        if hasattr(self, 'db_conn') and self.db_conn:
            self.db_conn.close()