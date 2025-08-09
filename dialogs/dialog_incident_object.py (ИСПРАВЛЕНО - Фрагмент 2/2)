# Контактная информация
        lbl_contacts = QLabel("Контактная информация:")
        self.txt_contacts = QTextEdit()
        layout.addWidget(lbl_contacts)
        layout.addWidget(self.txt_contacts)
        lbl_owners = QLabel("Владельцы:")
        self.cmb_owners = QComboBox()
        self.cmb_owners.addItems(["Выберите владельца", "Компания 1", "Компания 2"])
        layout.addWidget(lbl_owners)
        layout.addWidget(self.cmb_owners)
        lbl_operators = QLabel("Операторы:")
        self.cmb_operators = QComboBox()
        self.cmb_operators.addItems(["Выберите оператора", "Оператор 1", "Оператор 2"])
        layout.addWidget(lbl_operators)
        layout.addWidget(self.cmb_operators)
        lbl_phones = QLabel("Телефоны:")
        self.txt_phones = QLineEdit()
        layout.addWidget(lbl_phones)
        layout.addWidget(self.txt_phones)
        lbl_addresses = QLabel("Адреса:")
        self.txt_addresses = QLineEdit()
        layout.addWidget(lbl_addresses)
        layout.addWidget(self.txt_addresses)
        # Маршрутная информация
        lbl_departure = QLabel("Пункт отправления:")
        self.txt_departure = QLineEdit()
        layout.addWidget(lbl_departure)
        layout.addWidget(self.txt_departure)
        lbl_destination = QLabel("Пункт назначения:")
        self.txt_destination = QLineEdit()
        layout.addWidget(lbl_destination)
        layout.addWidget(self.txt_destination)
        lbl_etd = QLabel("ETD (время отправления):")
        self.datetime_etd = QDateTimeEdit()
        self.datetime_etd.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(lbl_etd)
        layout.addWidget(self.datetime_etd)
        lbl_eta = QLabel("ETA (время прибытия):")
        self.datetime_eta = QDateTimeEdit()
        self.datetime_eta.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(lbl_eta)
        layout.addWidget(self.datetime_eta)
        lbl_route = QLabel("Описание маршрута (SOA, курс следования):")
        self.txt_route = QTextEdit()
        layout.addWidget(lbl_route)
        layout.addWidget(self.txt_route)
        # Кнопки
        self.btn_select = QPushButton("Выбрать")
        self.btn_print = QPushButton("Печать")
        self.btn_send_sitrep = QPushButton("Отправить SITREP")
        self.btn_save = QPushButton("Сохранить")
        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.btn_select)
        hbox_buttons.addWidget(self.btn_print)
        hbox_buttons.addWidget(self.btn_send_sitrep)
        hbox_buttons.addWidget(self.btn_save)
        layout.addLayout(hbox_buttons)
        self.setLayout(layout)
    def connect_buttons(self):
        self.btn_select.clicked.connect(self.select_from_directory)
        self.btn_print.clicked.connect(self.print_form)
        self.btn_send_sitrep.clicked.connect(self.send_sitrep)
        self.btn_save.clicked.connect(self.save_object)
    def select_from_directory(self):
        QMessageBox.information(self, "Выбор", "Выбор из справочника судов выполнен")
    def print_form(self):
        c = canvas.Canvas("incident_object.pdf")
        c.drawString(100, 750, f"Характер аварии: {self.cmb_incident_type.currentText()}")
        c.drawString(100, 730, f"MMSI: {self.txt_mmsi.text()}")
        c.drawString(100, 710, f"IMO: {self.txt_imo.text()}")
        c.save()
        QMessageBox.information(self, "Печать", "Форма сохранена как PDF")
    def send_sitrep(self):
        QMessageBox.information(self, "Отправлено", "SITREP отправлен")
    def save_object(self):
        data = self.get_data()
        QgsProject.instance().writeEntry("PoiskMore", "incident_object", str(data))
        QMessageBox.information(self, "Сохранено", "Данные объекта аварии сохранены")
        self.close()
    def get_data(self):
        return {
            'incident_type': self.cmb_incident_type.currentText(),
            'length': self.spin_length.value(),
            'width': self.spin_width.value(),
            'draft': self.spin_draft.value(),
            'mmsi': self.txt_mmsi.text(),
            'imo': self.txt_imo.text(),
            'callsign': self.txt_callsign.text(),
            'color': self.txt_color.text(),
            'fuel': self.txt_fuel.text(),
            'contacts': self.txt_contacts.toPlainText(),
            'departure': self.txt_departure.text(),
            'destination': self.txt_destination.text(),
            'etd': self.datetime_etd.dateTime(),
            'eta': self.datetime_eta.dateTime(),
            'route': self.txt_route.toPlainText()
        }