import sqlite3
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QTabWidget, QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox, QSpinBox, QDateTimeEdit, QCheckBox, QWidget
from PyQt5.QtCore import QDateTime
from math import cos, sin, radians

class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_conn = sqlite3.connect('incidents.db')
        self.cursor = self.db_conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS incidents (id INTEGER PRIMARY KEY, name TEXT, coords TEXT, datetime TEXT, description TEXT, object_type TEXT, aviation TEXT, additional TEXT, owner TEXT, operator TEXT, wind_speed REAL, wind_dir INTEGER, current_speed REAL, current_dir INTEGER, wave_height REAL, air_temp REAL, water_temp REAL, asw REAL, twc REAL)')
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'dialog_registration.ui'), self)
        self.btn_save_pdf.clicked.connect(self.save_pdf)
        self.btn_send.clicked.connect(self.send_sitrep)
        self.btn_cancel.clicked.connect(self.close)

    def save_pdf(self):
        data = self.collect_data()
        if not self.validate_data(data):
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return
        # Реализация сохранения в PDF (используем reportlab или аналог)
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        filepath = "incident_report.pdf"
        c = canvas.Canvas(filepath, pagesize=letter)
        c.drawString(100, 750, str(data))
        c.save()
        QMessageBox.information(self, "Успех", "PDF сохранён")

    def send_sitrep(self):
        data = self.collect_data()
        if not self.validate_data(data):
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля")
            return
        # Реализация отправки SITREP (email или API)
        QMessageBox.information(self, "Успех", "SITREP отправлен")

    def collect_data(self):
        data = {
            'name': self.txt_name.text(),
            # Соберите все поля с вкладок аналогично
            'wind_speed': self.wind_speed.value(),  # Пример с вкладки Погода
            # ... (добавьте все поля)
        }
        # Расчёт ASW (средний ветер)
        wind_speed = data.get('wind_speed', 0)
        wind_dir = data.get('wind_dir', 0)
        data['asw'] = wind_speed * cos(radians(wind_dir))  # Пример расчёта
        # Расчёт TWC (суммарное течение)
        current_speed = data.get('current_speed', 0)
        current_dir = data.get('current_dir', 0)
        data['twc'] = current_speed * sin(radians(current_dir))  # Пример расчёта
        return data

    def validate_data(self, data):
        required = ['name', 'coords']  # Добавьте все обязательные
        return all(data.get(field) for field in required)

    def accept(self):
        data = self.collect_data()
        if not self.validate_data(data):
            return
        self.cursor.execute('INSERT INTO incidents (name, coords, datetime, description, object_type, aviation, additional, owner, operator, wind_speed, wind_dir, current_speed, current_dir, wave_height, air_temp, water_temp, asw, twc) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                            (data['name'], data['coords'], data['datetime'], data['description'], data['object_type'], data['aviation'], data['additional'], data['owner'], data['operator'], data['wind_speed'], data['wind_dir'], data['current_speed'], data['current_dir'], data['wave_height'], data['air_temp'], data['water_temp'], data['asw'], data['twc']))
        self.db_conn.commit()
        super().accept()

    def __del__(self):
        self.db_conn.close()