# Метод снижения пути
        lbl_method = QLabel("Метод определения местоположения")
        self.cmb_method = QComboBox()
        self.cmb_method.addItems(["GNSS", "Радар", "Визуально", "Другое"])
        layout.addWidget(lbl_method)
        layout.addWidget(self.cmb_method)
        # Расстояние DR
        lbl_dr_distance = QLabel("Расстояние DR с момента последнего определения")
        self.spin_dr_distance = QDoubleSpinBox(maximum=9999.99, value=0.0)
        self.spin_dr_distance.setSuffix(" морских миль")
        layout.addWidget(lbl_dr_distance)
        layout.addWidget(self.spin_dr_distance)
        # Описание маршрута
        lbl_route_desc = QLabel("Описание маршрута (SOA, курс следования)")
        self.txt_route_desc = QTextEdit()
        layout.addWidget(lbl_route_desc)
        layout.addWidget(self.txt_route_desc)
        # Кнопки
        self.btn_help = QPushButton("Помощь")
        self.btn_send_sitrep = QPushButton("Отправить SITREP")
        self.btn_save = QPushButton("Сохранить")
        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.btn_help)
        hbox_buttons.addWidget(self.btn_send_sitrep)
        hbox_buttons.addWidget(self.btn_save)
        layout.addLayout(hbox_buttons)
        self.setLayout(layout)
    def connect_buttons(self):
        self.btn_help.clicked.connect(self.show_help)
        self.btn_send_sitrep.clicked.connect(self.send_sitrep)
        self.btn_save.clicked.connect(self.save_object)
    def show_help(self):
        QMessageBox.information(self, "Помощь",
            "Инструкция по заполнению данных объекта поиска:\n\n"
            "1. Укажите название первичного объекта поиска\n"
            "2. Выберите тип объекта для расчета дрейфа\n"
            "3. Введите параметры объекта (длина, ширина, осадка)\n"
            "4. Укажите координатора операции\n"
            "5. Добавьте дополнительную информацию в поле 'Прочее'"
        )
    def send_sitrep(self):
        QMessageBox.information(self, "Отправлено", "SITREP по объекту поиска отправлен")
    def save_object(self):
        data = self.get_data()
        QgsProject.instance().writeEntry("PoiskMore", "search_object", str(data))
        QMessageBox.information(self, "Сохранено", "Данные объекта поиска сохранены")
        self.close()
    def get_data(self):
        return {
            'primary': self.txt_primary.text(),
            'type': self.cmb_type.currentText(),
            'drift_length': self.spin_drift_length.value(),
            'drift_width': self.spin_drift_width.value(),
            'drift_draft': self.spin_drift_draft.value(),
            'coordinator': self.txt_coordinator.text(),
            'other': self.txt_other.toPlainText(),
            'method': self.cmb_method.currentText(),
            'dr_distance': self.spin_dr_distance.value(),
            'route_desc': self.txt_route_desc.toPlainText()
        }