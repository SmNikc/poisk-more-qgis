# Течение
        lbl_current = QLabel("Течение")
        hbox_current_dir = QHBoxLayout()
        self.spin_current_dir = QSpinBox(value=332)
        self.spin_current_speed = QDoubleSpinBox(value=1.85)
        self.datetime_current_from = QDateTimeEdit()
        self.datetime_current_from.setDateTime(QDateTime.fromString("22.07.25 21:02", "dd.MM.yy hh:mm"))
        self.datetime_current_to = QDateTimeEdit()
        self.datetime_current_to.setDateTime(QDateTime.fromString("23.07.25 10:02", "dd.MM.yy hh:mm"))
        hbox_current_dir.addWidget(QLabel("Направление (градусы):"))
        hbox_current_dir.addWidget(self.spin_current_dir)
        hbox_current_dir.addWidget(QLabel("Скорость (узлы):"))
        hbox_current_dir.addWidget(self.spin_current_speed)
        layout.addWidget(lbl_current)
        layout.addLayout(hbox_current_dir)
        layout.addWidget(QLabel("Актуально с:"))
        layout.addWidget(self.datetime_current_from)
        layout.addWidget(QLabel("Актуально по:"))
        layout.addWidget(self.datetime_current_to)
        # Таблица TWC
        self.table_twc = QTableWidget(1, 4)
        self.table_twc.setHorizontalHeaderLabels(["Скорость (узлы)", "Направление (градусы)", "Актуально с", "Актуально по"])
        self.table_twc.setItem(0, 0, QTableWidgetItem("1.85"))
        self.table_twc.setItem(0, 1, QTableWidgetItem("332"))
        self.table_twc.setItem(0, 2, QTableWidgetItem("22.07.25 21:02"))
        self.table_twc.setItem(0, 3, QTableWidgetItem("23.07.25 10:02"))
        layout.addWidget(QLabel("Расчет суммарного водного течения (TWC)"))
        layout.addWidget(self.table_twc)
        # Дополнительные поля
        self.txt_precip = QLineEdit()
        self.spin_air_temp = QDoubleSpinBox(value=0.52)
        self.spin_water_temp = QDoubleSpinBox(value=16.49)
        self.txt_source = QTextEdit("Источник погоды")
        layout.addWidget(QLabel("Осадки:"))
        layout.addWidget(self.txt_precip)
        layout.addWidget(QLabel("Температура воздуха (°C):"))
        layout.addWidget(self.spin_air_temp)
        layout.addWidget(QLabel("Температура воды (°C):"))
        layout.addWidget(self.spin_water_temp)
        layout.addWidget(QLabel("Источник погоды:"))
        layout.addWidget(self.txt_source)
        # Кнопки
        self.btn_enter_wind = QPushButton("Внести данные о ветре")
        self.btn_enter_current = QPushButton("Внести данные о течении")
        self.btn_help = QPushButton("Помощь")
        self.btn_send_sitrep = QPushButton("Отправить SITREP")
        self.btn_save = QPushButton("Сохранить")
        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.btn_enter_wind)
        hbox_buttons.addWidget(self.btn_enter_current)
        hbox_buttons.addWidget(self.btn_help)
        hbox_buttons.addWidget(self.btn_send_sitrep)
        hbox_buttons.addWidget(self.btn_save)
        layout.addLayout(hbox_buttons)
        self.setLayout(layout)
    def connect_buttons(self):
        self.btn_enter_wind.clicked.connect(self.enter_wind_data)
        self.btn_enter_current.clicked.connect(self.enter_current_data)
        self.btn_help.clicked.connect(self.show_help)
        self.btn_send_sitrep.clicked.connect(self.send_sitrep)
        self.btn_save.clicked.connect(self.save_operation)
    def enter_wind_data(self):
        row = self.table_asw.rowCount()
        self.table_asw.insertRow(row)
        self.table_asw.setItem(row, 0, QTableWidgetItem(str(self.spin_wind_speed.value())))
        self.table_asw.setItem(row, 1, QTableWidgetItem(str(self.spin_wind_dir.value())))
        self.table_asw.setItem(row, 2, QTableWidgetItem(self.datetime_wind_from.dateTime().toString("dd.MM.yyyy hh:mm")))
        self.table_asw.setItem(row, 3, QTableWidgetItem(self.datetime_wind_to.dateTime().toString("dd.MM.yyyy hh:mm")))
    def enter_current_data(self):
        row = self.table_twc.rowCount()
        self.table_twc.insertRow(row)
        self.table_twc.setItem(row, 0, QTableWidgetItem(str(self.spin_current_speed.value())))
        self.table_twc.setItem(row, 1, QTableWidgetItem(str(self.spin_current_dir.value())))
        self.table_twc.setItem(row, 2, QTableWidgetItem(self.datetime_current_from.dateTime().toString("dd.MM.yyyy hh:mm")))
        self.table_twc.setItem(row, 3, QTableWidgetItem(self.datetime_current_to.dateTime().toString("dd.MM.yyyy hh:mm")))
    def show_help(self):
        QMessageBox.information(self, "Помощь", "Инструкция по редактированию информации об операции.")
    def send_sitrep(self):
        QMessageBox.information(self, "Отправлено", "SITREP отправлен")
    def save_operation(self):
        data = self.get_data()
        QgsProject.instance().writeEntry("PoiskMore", "operation_data", str(data))
        QMessageBox.information(self, "Сохранено", "Данные операции сохранены")
        self.close()
    def get_data(self):
        return {
            'wind_speed': self.spin_wind_speed.value(),
            'wind_dir': self.spin_wind_dir.value(),
            'current_speed': self.spin_current_speed.value(),
            'current_dir': self.spin_current_dir.value(),
            'air_temp': self.spin_air_temp.value(),
            'water_temp': self.spin_water_temp.value(),
            'precip': self.txt_precip.text(),
            'source': self.txt_source.toPlainText()
        }