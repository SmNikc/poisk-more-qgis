from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QLabel, QTabWidget, QTextEdit, QComboBox, QDoubleSpinBox, QSpinBox
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QDateTimeEdit

class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Вкладка 1: Основная информация
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        tab1_layout.addWidget(QLabel("Дата / Время (UTC):"))
        self.datetime = QDateTimeEdit()
        self.datetime.setDateTime(QDateTime.currentDateTime())
        tab1_layout.addWidget(self.datetime)
        tab1_layout.addWidget(QLabel("Название:"))
        self.name = QLineEdit()
        tab1_layout.addWidget(self.name)
        tab1_layout.addWidget(QLabel("Координаты:"))
        self.coords = QLineEdit()
        tab1_layout.addWidget(self.coords)
        tab1_layout.addWidget(QLabel("Описание:"))
        self.description = QTextEdit()
        tab1_layout.addWidget(self.description)
        tabs.addTab(tab1, "Основная информация")

        # Вкладка 2: Объект аварийного случая / Местоположение
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        tab2_layout.addWidget(QLabel("Тип объекта:"))
        self.object_type = QComboBox()
        self.object_type.addItems(["Судно", "Самолет", "Человек за бортом"])
        tab2_layout.addWidget(self.object_type)
        tab2_layout.addWidget(QLabel("Авиационное оборудование:"))
        self.aviation = QLineEdit()
        tab2_layout.addWidget(self.aviation)
        tab2_layout.addWidget(QLabel("Дополнительно:"))
        self.additional = QTextEdit()
        tab2_layout.addWidget(self.additional)
        tabs.addTab(tab2, "Объект / Местоположение")

        # Вкладка 3: Погода
        tab3 = QWidget()
        tab3_layout = QVBoxLayout(tab3)
        tab3_layout.addWidget(QLabel("Скорость ветра (узлы):"))
        self.wind_speed = QDoubleSpinBox(minimum=0, value=10.0)
        tab3_layout.addWidget(self.wind_speed)
        tab3_layout.addWidget(QLabel("Направление ветра (градусы):"))
        self.wind_dir = QSpinBox(minimum=0, maximum=360, value=0)
        tab3_layout.addWidget(self.wind_dir)
        tab3_layout.addWidget(QLabel("Температура воздуха °C:"))
        self.air_temp = QDoubleSpinBox(minimum=-50, maximum=50, value=0.52)
        tab3_layout.addWidget(self.air_temp)
        tabs.addTab(tab3, "Погода")

        # Вкладка 4: Расчет
        tab4 = QWidget()
        tab4_layout = QVBoxLayout(tab4)
        tab4_layout.addWidget(QLabel("Число лиц в опасности:"))
        self.num_people = QSpinBox(minimum=0, value=0)
        tab4_layout.addWidget(self.num_people)
        tab4_layout.addWidget(QLabel("Требуемая помощь:"))
        self.help_needed = QLineEdit()
        tab4_layout.addWidget(self.help_needed)
        tabs.addTab(tab4, "Расчет")

        btn = QPushButton("Зарегистрировать")
        btn.clicked.connect(self.register)
        layout.addWidget(btn)

    def register(self):
        if not self.name.text().strip() or not self.coords.text().strip():
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return
        self.accept()