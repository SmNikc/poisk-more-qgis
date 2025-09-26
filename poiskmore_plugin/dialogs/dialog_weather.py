# -*- coding: utf-8 -*-
"""
dialog_weather.py — контроллер вкладки «Погода».
Интегрирует новую форму с расписанием ветра и течений.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox, QMessageBox
from PyQt5.QtCore import pyqtSignal

from .weather_schedule_dialog import WeatherScheduleDialog


class DialogWeather(QDialog):
    """Простой диалог-обертка для вызова формы погоды с расписанием"""
    
    weather_data_updated = pyqtSignal(dict)
    
    def __init__(self, incident_id=None, parent=None):
        super().__init__(parent)
        self.incident_id = incident_id
        self.weather_data = {}
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Погода")
        self.setMinimumSize(400, 200)
        
        layout = QVBoxLayout()
        
        # Информационная группа
        info_group = QGroupBox("Метеоусловия")
        info_layout = QVBoxLayout()
        
        self.asw_label = QLabel("Средний ветер (ASW): не рассчитан")
        info_layout.addWidget(self.asw_label)
        
        self.twc_label = QLabel("Суммарное течение (TWC): не рассчитано")
        info_layout.addWidget(self.twc_label)
        
        self.status_label = QLabel("Статус: данные не введены")
        info_layout.addWidget(self.status_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.btn_edit_schedule = QPushButton("📋 Внести расписание ветра и течений")
        self.btn_edit_schedule.clicked.connect(self.open_weather_schedule)
        button_layout.addWidget(self.btn_edit_schedule)
        
        self.btn_import = QPushButton("📥 Импорт из Гидрометео")
        self.btn_import.clicked.connect(self.import_hydro)
        button_layout.addWidget(self.btn_import)
        
        layout.addLayout(button_layout)
        
        # Кнопки диалога
        dialog_buttons = QHBoxLayout()
        
        self.btn_ok = QPushButton("OK")
        self.btn_ok.clicked.connect(self.accept)
        dialog_buttons.addWidget(self.btn_ok)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        dialog_buttons.addWidget(self.btn_cancel)
        
        layout.addLayout(dialog_buttons)
        
        self.setLayout(layout)
    
    def open_weather_schedule(self):
        """Открыть полную форму с расписанием ветра и течений"""
        dlg = WeatherScheduleDialog(self.incident_id, self)
        dlg.weather_updated.connect(self.on_weather_updated)
        
        if dlg.exec_():
            QMessageBox.information(self, "Успешно", 
                                  "Данные расписания сохранены")
    
    def on_weather_updated(self, data):
        """Обработка обновления данных погоды"""
        self.weather_data = data
        
        # Обновляем метки
        if 'asw' in data:
            self.asw_label.setText(f"Средний ветер (ASW): {data['asw']['speed']} @ {data['asw']['direction']}")
        
        if 'twc' in data:
            self.twc_label.setText(f"Суммарное течение (TWC): {data['twc']['speed']} @ {data['twc']['direction']}")
        
        self.status_label.setText("Статус: данные введены ✓")
        
        # Передаем сигнал дальше
        self.weather_data_updated.emit(data)
    
    def import_hydro(self):
        """Импорт из модуля Гидрометео"""
        QMessageBox.information(self, "Импорт", 
                              "Функция импорта из модуля Гидрометео\n"
                              "будет реализована в следующей версии.")
    
    def get_weather_data(self):
        """Получить введенные данные погоды"""
        return self.weather_data
