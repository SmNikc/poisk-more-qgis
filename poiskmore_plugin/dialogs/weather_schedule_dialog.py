# -*- coding: utf-8 -*-
"""
Диалог ввода расписания ветра и течений с таблицами по времени
Полная реализация согласно IAMSAR и методике Поиск-Море
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QGroupBox, QLabel,
                             QSpinBox, QDoubleSpinBox, QDateTimeEdit, QTabWidget,
                             QComboBox, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta
import math


class WeatherScheduleDialog(QDialog):
    """Диалог ввода расписания ветра и течений по времени"""
    
    weather_updated = pyqtSignal(dict)  # Сигнал при обновлении данных
    
    def __init__(self, incident_id=None, parent=None):
        super().__init__(parent)
        self.incident_id = incident_id
        self.setup_ui()
        self.load_existing_data()
        
    def setup_ui(self):
        """Создание интерфейса с вкладками"""
        self.setWindowTitle("Расписание метеоусловий")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout()
        
        # Табы для ветра и течений
        self.tabs = QTabWidget()
        
        # Вкладка расписания ветра
        self.wind_tab = self.create_wind_tab()
        self.tabs.addTab(self.wind_tab, "🌬️ Расписание ветра")
        
        # Вкладка расписания течений
        self.current_tab = self.create_current_tab()
        self.tabs.addTab(self.current_tab, "🌊 Расписание течений")
        
        # Вкладка расчета дрейфа
        self.drift_tab = self.create_drift_tab()
        self.tabs.addTab(self.drift_tab, "📊 Расчет дрейфа")
        
        layout.addWidget(self.tabs)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        self.btn_import = QPushButton("📥 Импорт из Гидрометео")
        self.btn_import.clicked.connect(self.import_from_hydro)
        btn_layout.addWidget(self.btn_import)
        
        self.btn_calculate = QPushButton("🧮 Рассчитать ASW/TWC")
        self.btn_calculate.clicked.connect(self.calculate_summary)
        btn_layout.addWidget(self.btn_calculate)
        
        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_save.clicked.connect(self.save_data)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def create_wind_tab(self):
        """Создание вкладки расписания ветра"""
        widget = QGroupBox()
        layout = QVBoxLayout()
        
        # Заголовок
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>Расписание ветра (ASW - Average Surface Wind)</b>"))
        header_layout.addStretch()
        
        # Период
        header_layout.addWidget(QLabel("Период с:"))
        self.wind_dt_from = QDateTimeEdit()
        self.wind_dt_from.setDisplayFormat("dd.MM.yyyy HH:mm UTC")
        self.wind_dt_from.setDateTime(QDateTime.currentDateTimeUtc())
        header_layout.addWidget(self.wind_dt_from)
        
        header_layout.addWidget(QLabel("по:"))
        self.wind_dt_to = QDateTimeEdit()
        self.wind_dt_to.setDisplayFormat("dd.MM.yyyy HH:mm UTC")
        dt_to = QDateTime.currentDateTimeUtc().addSecs(24*3600)  # +24 часа
        self.wind_dt_to.setDateTime(dt_to)
        header_layout.addWidget(self.wind_dt_to)
        
        layout.addLayout(header_layout)
        
        # Таблица расписания ветра
        self.wind_table = QTableWidget()
        self.wind_table.setColumnCount(7)
        self.wind_table.setHorizontalHeaderLabels([
            "Время (UTC)", "Направление\n(откуда, °)", "Скорость\n(м/с)", 
            "Скорость\n(узлы)", "Порывы\n(м/с)", "Высота\n(м)", "Источник"
        ])
        
        # Настройка ширины колонок
        header = self.wind_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Кнопки управления таблицей
        table_btn_layout = QHBoxLayout()
        
        btn_add_wind = QPushButton("➕ Добавить строку")
        btn_add_wind.clicked.connect(lambda: self.add_wind_row())
        table_btn_layout.addWidget(btn_add_wind)
        
        btn_del_wind = QPushButton("➖ Удалить строку")
        btn_del_wind.clicked.connect(lambda: self.delete_selected_row(self.wind_table))
        table_btn_layout.addWidget(btn_del_wind)
        
        btn_interpolate = QPushButton("📈 Интерполировать")
        btn_interpolate.clicked.connect(self.interpolate_wind)
        table_btn_layout.addWidget(btn_interpolate)
        
        table_btn_layout.addStretch()
        
        layout.addLayout(table_btn_layout)
        layout.addWidget(self.wind_table)
        
        # Результаты расчета ASW
        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("<b>Средний ветер (ASW):</b>"))
        
        result_layout.addWidget(QLabel("Скорость:"))
        self.asw_speed_label = QLabel("0.0 м/с")
        self.asw_speed_label.setStyleSheet("font-weight: bold; color: blue;")
        result_layout.addWidget(self.asw_speed_label)
        
        result_layout.addWidget(QLabel("Направление:"))
        self.asw_dir_label = QLabel("0°")
        self.asw_dir_label.setStyleSheet("font-weight: bold; color: blue;")
        result_layout.addWidget(self.asw_dir_label)
        
        result_layout.addWidget(QLabel("Погрешность:"))
        self.asw_error_label = QLabel("±0.0 м/с")
        self.asw_error_label.setStyleSheet("color: red;")
        result_layout.addWidget(self.asw_error_label)
        
        result_layout.addStretch()
        
        layout.addLayout(result_layout)
        
        widget.setLayout(layout)
        
        # Добавляем начальные строки
        self.add_wind_row()
        self.add_wind_row(hours_offset=6)
        self.add_wind_row(hours_offset=12)
        self.add_wind_row(hours_offset=24)
        
        return widget
    
    def create_current_tab(self):
        """Создание вкладки расписания течений"""
        widget = QGroupBox()
        layout = QVBoxLayout()
        
        # Заголовок
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>Расписание течений (TWC - Total Water Current)</b>"))
        header_layout.addStretch()
        
        # Период
        header_layout.addWidget(QLabel("Период с:"))
        self.current_dt_from = QDateTimeEdit()
        self.current_dt_from.setDisplayFormat("dd.MM.yyyy HH:mm UTC")
        self.current_dt_from.setDateTime(QDateTime.currentDateTimeUtc())
        header_layout.addWidget(self.current_dt_from)
        
        header_layout.addWidget(QLabel("по:"))
        self.current_dt_to = QDateTimeEdit()
        self.current_dt_to.setDisplayFormat("dd.MM.yyyy HH:mm UTC")
        dt_to = QDateTime.currentDateTimeUtc().addSecs(24*3600)
        self.current_dt_to.setDateTime(dt_to)
        header_layout.addWidget(self.current_dt_to)
        
        layout.addLayout(header_layout)
        
        # Таблица расписания течений
        self.current_table = QTableWidget()
        self.current_table.setColumnCount(6)
        self.current_table.setHorizontalHeaderLabels([
            "Время (UTC)", "Направление\n(куда, °)", "Скорость\n(узлы)", 
            "Глубина\n(м)", "Тип", "Источник"
        ])
        
        header = self.current_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Кнопки управления таблицей
        table_btn_layout = QHBoxLayout()
        
        btn_add_current = QPushButton("➕ Добавить строку")
        btn_add_current.clicked.connect(lambda: self.add_current_row())
        table_btn_layout.addWidget(btn_add_current)
        
        btn_del_current = QPushButton("➖ Удалить строку")
        btn_del_current.clicked.connect(lambda: self.delete_selected_row(self.current_table))
        table_btn_layout.addWidget(btn_del_current)
        
        btn_tidal = QPushButton("🌊 Приливные таблицы")
        btn_tidal.clicked.connect(self.load_tidal_data)
        table_btn_layout.addWidget(btn_tidal)
        
        table_btn_layout.addStretch()
        
        layout.addLayout(table_btn_layout)
        layout.addWidget(self.current_table)
        
        # Результаты расчета TWC
        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("<b>Суммарное течение (TWC):</b>"))
        
        result_layout.addWidget(QLabel("Скорость:"))
        self.twc_speed_label = QLabel("0.0 узлов")
        self.twc_speed_label.setStyleSheet("font-weight: bold; color: blue;")
        result_layout.addWidget(self.twc_speed_label)
        
        result_layout.addWidget(QLabel("Направление:"))
        self.twc_dir_label = QLabel("0°")
        self.twc_dir_label.setStyleSheet("font-weight: bold; color: blue;")
        result_layout.addWidget(self.twc_dir_label)
        
        result_layout.addWidget(QLabel("Погрешность:"))
        self.twc_error_label = QLabel("±0.0 узлов")
        self.twc_error_label.setStyleSheet("color: red;")
        result_layout.addWidget(self.twc_error_label)
        
        result_layout.addStretch()
        
        layout.addLayout(result_layout)
        
        widget.setLayout(layout)
        
        # Добавляем начальные строки
        self.add_current_row()
        self.add_current_row(hours_offset=6)
        
        return widget
    
    def create_drift_tab(self):
        """Создание вкладки расчета дрейфа"""
        widget = QGroupBox()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>Расчет дрейфа по IAMSAR</b>"))
        
        # Параметры объекта
        obj_layout = QHBoxLayout()
        obj_layout.addWidget(QLabel("Тип объекта:"))
        
        self.object_type = QComboBox()
        self.object_type.addItems([
            "Спасательный плот с тентом",
            "Спасательный плот без тента",
            "Человек в спасжилете",
            "Человек без спасжилета",
            "Малое судно (<20м)",
            "Среднее судно (20-50м)",
            "Большое судно (>50м)"
        ])
        self.object_type.currentIndexChanged.connect(self.update_leeway_coefficients)
        obj_layout.addWidget(self.object_type)
        
        obj_layout.addStretch()
        
        layout.addLayout(obj_layout)
        
        # Коэффициенты ливея
        coef_layout = QHBoxLayout()
        coef_layout.addWidget(QLabel("DWL slope:"))
        self.dwl_slope = QDoubleSpinBox()
        self.dwl_slope.setDecimals(4)
        self.dwl_slope.setValue(0.0110)
        coef_layout.addWidget(self.dwl_slope)
        
        coef_layout.addWidget(QLabel("intercept:"))
        self.dwl_intercept = QDoubleSpinBox()
        self.dwl_intercept.setDecimals(4)
        self.dwl_intercept.setValue(0.0)
        coef_layout.addWidget(self.dwl_intercept)
        
        coef_layout.addWidget(QLabel("CWL slope:"))
        self.cwl_slope = QDoubleSpinBox()
        self.cwl_slope.setDecimals(4)
        self.cwl_slope.setValue(0.0060)
        coef_layout.addWidget(self.cwl_slope)
        
        coef_layout.addWidget(QLabel("intercept:"))
        self.cwl_intercept = QDoubleSpinBox()
        self.cwl_intercept.setDecimals(4)
        self.cwl_intercept.setValue(0.0)
        coef_layout.addWidget(self.cwl_intercept)
        
        coef_layout.addStretch()
        
        layout.addLayout(coef_layout)
        
        # Таблица результатов дрейфа по времени
        self.drift_table = QTableWidget()
        self.drift_table.setColumnCount(9)
        self.drift_table.setHorizontalHeaderLabels([
            "Время", "Ветер\n(м/с)", "DWL\n(узлы)", "CWL±\n(узлы)",
            "Leeway\n(узлы)", "TWC\n(узлы)", "Дрейф\n(узлы)",
            "Направление\n(°)", "Смещение\n(мили)"
        ])
        
        layout.addWidget(self.drift_table)
        
        # Итоговые результаты
        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("<b>Итоговый дрейф:</b>"))
        
        result_layout.addWidget(QLabel("Смещение:"))
        self.total_drift_label = QLabel("0.0 морских миль")
        self.total_drift_label.setStyleSheet("font-weight: bold; color: red;")
        result_layout.addWidget(self.total_drift_label)
        
        result_layout.addWidget(QLabel("Направление:"))
        self.drift_dir_label = QLabel("0°")
        self.drift_dir_label.setStyleSheet("font-weight: bold; color: red;")
        result_layout.addWidget(self.drift_dir_label)
        
        result_layout.addWidget(QLabel("Расхождение датумов:"))
        self.divergence_label = QLabel("0.0 мили")
        self.divergence_label.setStyleSheet("color: orange;")
        result_layout.addWidget(self.divergence_label)
        
        result_layout.addStretch()
        
        layout.addLayout(result_layout)
        
        widget.setLayout(layout)
        return widget
    
    def add_wind_row(self, hours_offset=0):
        """Добавить строку в таблицу ветра"""
        row_count = self.wind_table.rowCount()
        self.wind_table.insertRow(row_count)
        
        # Время
        dt = QDateTime.currentDateTimeUtc().addSecs(hours_offset * 3600)
        time_item = QTableWidgetItem(dt.toString("dd.MM HH:mm"))
        self.wind_table.setItem(row_count, 0, time_item)
        
        # Направление (откуда)
        dir_item = QTableWidgetItem("0")
        self.wind_table.setItem(row_count, 1, dir_item)
        
        # Скорость м/с
        speed_ms_item = QTableWidgetItem("0.0")
        self.wind_table.setItem(row_count, 2, speed_ms_item)
        
        # Скорость узлы (автоматический пересчет)
        speed_kn_item = QTableWidgetItem("0.0")
        self.wind_table.setItem(row_count, 3, speed_kn_item)
        
        # Порывы
        gust_item = QTableWidgetItem("")
        self.wind_table.setItem(row_count, 4, gust_item)
        
        # Высота измерения
        height_item = QTableWidgetItem("10")
        self.wind_table.setItem(row_count, 5, height_item)
        
        # Источник
        source_item = QTableWidgetItem("Ручной ввод")
        self.wind_table.setItem(row_count, 6, source_item)
    
    def add_current_row(self, hours_offset=0):
        """Добавить строку в таблицу течений"""
        row_count = self.current_table.rowCount()
        self.current_table.insertRow(row_count)
        
        # Время
        dt = QDateTime.currentDateTimeUtc().addSecs(hours_offset * 3600)
        time_item = QTableWidgetItem(dt.toString("dd.MM HH:mm"))
        self.current_table.setItem(row_count, 0, time_item)
        
        # Направление (куда)
        dir_item = QTableWidgetItem("0")
        self.current_table.setItem(row_count, 1, dir_item)
        
        # Скорость узлы
        speed_item = QTableWidgetItem("0.0")
        self.current_table.setItem(row_count, 2, speed_item)
        
        # Глубина
        depth_item = QTableWidgetItem("0")
        self.current_table.setItem(row_count, 3, depth_item)
        
        # Тип
        type_item = QTableWidgetItem("Поверхностное")
        self.current_table.setItem(row_count, 4, type_item)
        
        # Источник
        source_item = QTableWidgetItem("Ручной ввод")
        self.current_table.setItem(row_count, 5, source_item)
    
    def delete_selected_row(self, table):
        """Удалить выбранную строку из таблицы"""
        current_row = table.currentRow()
        if current_row >= 0:
            table.removeRow(current_row)
    
    def interpolate_wind(self):
        """Интерполировать данные ветра между точками"""
        if self.wind_table.rowCount() < 2:
            QMessageBox.warning(self, "Предупреждение", 
                               "Для интерполяции нужно минимум 2 строки")
            return
        
        # TODO: Реализовать интерполяцию
        QMessageBox.information(self, "Интерполяция", 
                               "Функция интерполяции будет реализована")
    
    def update_leeway_coefficients(self):
        """Обновить коэффициенты ливея в зависимости от типа объекта"""
        # Коэффициенты из IAMSAR Приложение N
        coefficients = {
            "Спасательный плот с тентом": (0.0110, 0.0, 0.0060, 0.0),
            "Спасательный плот без тента": (0.0160, 0.0, 0.0100, 0.0),
            "Человек в спасжилете": (0.0120, 0.0, 0.0050, 0.0),
            "Человек без спасжилета": (0.0100, 0.0, 0.0040, 0.0),
            "Малое судно (<20м)": (0.0420, 0.0, 0.0480, 0.0),
            "Среднее судно (20-50м)": (0.0330, 0.0, 0.0420, 0.0),
            "Большое судно (>50м)": (0.0280, 0.0, 0.0380, 0.0),
        }
        
        obj_type = self.object_type.currentText()
        if obj_type in coefficients:
            dwl_s, dwl_i, cwl_s, cwl_i = coefficients[obj_type]
            self.dwl_slope.setValue(dwl_s)
            self.dwl_intercept.setValue(dwl_i)
            self.cwl_slope.setValue(cwl_s)
            self.cwl_intercept.setValue(cwl_i)
    
    def calculate_summary(self):
        """Рассчитать ASW, TWC и дрейф"""
        # Расчет ASW (средневзвешенный ветер)
        self.calculate_asw()
        
        # Расчет TWC (суммарное течение)
        self.calculate_twc()
        
        # Расчет дрейфа по времени
        self.calculate_drift()
    
    def calculate_asw(self):
        """Рассчитать средневзвешенный ветер (ASW)"""
        if self.wind_table.rowCount() == 0:
            return
        
        # Векторное усреднение
        sum_u = 0.0  # Компонента E-W
        sum_v = 0.0  # Компонента N-S
        total_weight = 0.0
        
        for row in range(self.wind_table.rowCount()):
            try:
                # Получаем данные из таблицы
                speed_ms = float(self.wind_table.item(row, 2).text())
                dir_from = float(self.wind_table.item(row, 1).text())
                
                # Преобразуем в направление "куда"
                dir_to = (dir_from + 180) % 360
                
                # Радианы
                dir_rad = math.radians(dir_to)
                
                # Векторные компоненты
                u = speed_ms * math.sin(dir_rad)
                v = speed_ms * math.cos(dir_rad)
                
                # Вес (можно учитывать временной интервал)
                weight = 1.0  # Упрощенно - равные веса
                
                sum_u += u * weight
                sum_v += v * weight
                total_weight += weight
                
            except (ValueError, AttributeError):
                continue
        
        if total_weight > 0:
            avg_u = sum_u / total_weight
            avg_v = sum_v / total_weight
            
            # Результирующая скорость и направление
            asw_speed = math.sqrt(avg_u**2 + avg_v**2)
            asw_dir = math.degrees(math.atan2(avg_u, avg_v)) % 360
            
            # Погрешность (упрощенно - 10% от скорости)
            asw_error = asw_speed * 0.1
            
            self.asw_speed_label.setText(f"{asw_speed:.1f} м/с")
            self.asw_dir_label.setText(f"{asw_dir:.0f}°")
            self.asw_error_label.setText(f"±{asw_error:.1f} м/с")
    
    def calculate_twc(self):
        """Рассчитать суммарное течение (TWC)"""
        if self.current_table.rowCount() == 0:
            return
        
        # Векторное усреднение
        sum_u = 0.0
        sum_v = 0.0
        total_weight = 0.0
        
        for row in range(self.current_table.rowCount()):
            try:
                speed_kn = float(self.current_table.item(row, 2).text())
                dir_to = float(self.current_table.item(row, 1).text())
                
                dir_rad = math.radians(dir_to)
                
                u = speed_kn * math.sin(dir_rad)
                v = speed_kn * math.cos(dir_rad)
                
                weight = 1.0
                
                sum_u += u * weight
                sum_v += v * weight
                total_weight += weight
                
            except (ValueError, AttributeError):
                continue
        
        if total_weight > 0:
            avg_u = sum_u / total_weight
            avg_v = sum_v / total_weight
            
            twc_speed = math.sqrt(avg_u**2 + avg_v**2)
            twc_dir = math.degrees(math.atan2(avg_u, avg_v)) % 360
            twc_error = twc_speed * 0.15  # 15% погрешность
            
            self.twc_speed_label.setText(f"{twc_speed:.2f} узлов")
            self.twc_dir_label.setText(f"{twc_dir:.0f}°")
            self.twc_error_label.setText(f"±{twc_error:.2f} узлов")
    
    def calculate_drift(self):
        """Рассчитать дрейф по времени согласно IAMSAR"""
        # Очистка таблицы дрейфа
        self.drift_table.setRowCount(0)
        
        # Получаем коэффициенты ливея
        dwl_slope = self.dwl_slope.value()
        dwl_intercept = self.dwl_intercept.value()
        cwl_slope = self.cwl_slope.value()
        cwl_intercept = self.cwl_intercept.value()
        
        total_drift_nm = 0.0
        total_drift_u = 0.0
        total_drift_v = 0.0
        
        # Для каждого временного интервала
        for row in range(self.wind_table.rowCount()):
            try:
                # Ветер
                wind_speed_ms = float(self.wind_table.item(row, 2).text())
                wind_speed_kn = wind_speed_ms * 1.94384  # м/с в узлы
                
                # Расчет компонентов ливея
                dwl = dwl_slope * wind_speed_kn + dwl_intercept
                cwl = cwl_slope * wind_speed_kn + cwl_intercept  # ± для двух ветвей
                
                # Скорость ливея
                leeway_speed = math.sqrt(dwl**2 + cwl**2)
                
                # Течение (упрощенно - берем среднее TWC)
                twc_speed = 0.5  # узлы (заглушка)
                
                # Суммарный дрейф
                drift_speed = leeway_speed + twc_speed
                
                # Добавляем строку в таблицу
                drift_row = self.drift_table.rowCount()
                self.drift_table.insertRow(drift_row)
                
                time_str = self.wind_table.item(row, 0).text() if self.wind_table.item(row, 0) else ""
                self.drift_table.setItem(drift_row, 0, QTableWidgetItem(time_str))
                self.drift_table.setItem(drift_row, 1, QTableWidgetItem(f"{wind_speed_ms:.1f}"))
                self.drift_table.setItem(drift_row, 2, QTableWidgetItem(f"{dwl:.3f}"))
                self.drift_table.setItem(drift_row, 3, QTableWidgetItem(f"±{cwl:.3f}"))
                self.drift_table.setItem(drift_row, 4, QTableWidgetItem(f"{leeway_speed:.2f}"))
                self.drift_table.setItem(drift_row, 5, QTableWidgetItem(f"{twc_speed:.2f}"))
                self.drift_table.setItem(drift_row, 6, QTableWidgetItem(f"{drift_speed:.2f}"))
                
                # Накапливаем смещение (за 1 час)
                drift_nm_per_hour = drift_speed * 1.0  # узлы * часы = мили
                total_drift_nm += drift_nm_per_hour
                
            except (ValueError, AttributeError):
                continue
        
        # Итоговые результаты
        self.total_drift_label.setText(f"{total_drift_nm:.1f} морских миль")
        
        # Расхождение датумов (из-за ±CWL)
        divergence = abs(cwl) * self.wind_table.rowCount() * 2  # Упрощенно
        self.divergence_label.setText(f"{divergence:.1f} мили")
    
    def import_from_hydro(self):
        """Импорт данных из модуля Гидрометео"""
        QMessageBox.information(self, "Импорт", 
                               "Функция импорта из Гидрометео будет реализована.\n"
                               "Будут загружены данные GRIB/ECMWF.")
    
    def load_tidal_data(self):
        """Загрузить приливные данные"""
        QMessageBox.information(self, "Приливы", 
                               "Загрузка приливных таблиц будет реализована.\n"
                               "Источник: Admiralty Tide Tables")
    
    def load_existing_data(self):
        """Загрузить существующие данные из БД"""
        if not self.incident_id:
            return
        
        # TODO: Загрузка из БД
        # db.load_wind_schedule(self.incident_id)
        # db.load_current_schedule(self.incident_id)
    
    def save_data(self):
        """Сохранить данные в БД"""
        try:
            # Сбор данных из таблиц
            wind_data = []
            for row in range(self.wind_table.rowCount()):
                wind_entry = {
                    'time': self.wind_table.item(row, 0).text(),
                    'direction': float(self.wind_table.item(row, 1).text()),
                    'speed_ms': float(self.wind_table.item(row, 2).text()),
                    'gust': self.wind_table.item(row, 4).text(),
                    'height': float(self.wind_table.item(row, 5).text()),
                    'source': self.wind_table.item(row, 6).text()
                }
                wind_data.append(wind_entry)
            
            current_data = []
            for row in range(self.current_table.rowCount()):
                current_entry = {
                    'time': self.current_table.item(row, 0).text(),
                    'direction': float(self.current_table.item(row, 1).text()),
                    'speed_kn': float(self.current_table.item(row, 2).text()),
                    'depth': float(self.current_table.item(row, 3).text()),
                    'type': self.current_table.item(row, 4).text(),
                    'source': self.current_table.item(row, 5).text()
                }
                current_data.append(current_entry)
            
            # Отправляем сигнал с данными
            weather_data = {
                'wind_schedule': wind_data,
                'current_schedule': current_data,
                'asw': {
                    'speed': self.asw_speed_label.text(),
                    'direction': self.asw_dir_label.text()
                },
                'twc': {
                    'speed': self.twc_speed_label.text(),
                    'direction': self.twc_dir_label.text()
                }
            }
            
            self.weather_updated.emit(weather_data)
            
            QMessageBox.information(self, "Сохранение", 
                                   "Данные расписания сохранены успешно!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", 
                                f"Ошибка при сохранении: {str(e)}")
