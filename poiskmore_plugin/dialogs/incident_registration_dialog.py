# -*- coding: utf-8 -*-
"""
dialogs/incident_registration_dialog.py
Диалог "Регистрация происшествия" (загрузка существующего .ui)
 - подхватывает имена полей из .ui: lineEdit_asw, lineEdit_twc, lineEdit_datum,
   doubleSpinBox_latitude, doubleSpinBox_longitude и т.п.
 - вычисляет TWC/Datum через calculations.drift_calculator.DriftCalculator
"""

import os
import math
from datetime import datetime, timezone

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QPushButton
from PyQt5.QtCore import QDateTime

from ..calculations.drift_calculator import DriftCalculator, DriftVector

UI_FILE = os.path.join(os.path.dirname(__file__), 'incident_registration_dialog.ui')


def _get(widget_owner, *names):
    """Найти первый доступный виджет по одному из objectName."""
    for n in names:
        w = getattr(widget_owner, n, None)
        if w is not None:
            return w
    return None


def _spin_value(w, default=0.0):
    try:
        return float(w.value())
    except Exception:
        return float(default)


class IncidentRegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_FILE, self)

        # Кандидаты имен для виджетов — подхватываем то, что есть в .ui
        self.le_asw   = _get(self, 'lineEdit_asw', 'asw_calculated')
        self.le_twc   = _get(self, 'lineEdit_twc', 'twc_calculated')
        self.le_datum = _get(self, 'lineEdit_datum', 'datum_calculated')

        self.sb_lat = _get(self, 'doubleSpinBox_latitude', 'spinBox_lat', 'latitude')
        self.sb_lon = _get(self, 'doubleSpinBox_longitude', 'spinBox_lon', 'longitude')

        self.dt_incident = _get(self, 'dateTimeEdit_incident', 'incident_datetime')
        self.dt_lkp      = _get(self, 'dateTimeEdit_last_contact', 'last_known_position_time')

        self.sb_wind_dir   = _get(self, 'spinBox_wind_dir', 'wind_direction', 'spinBox_wind_direction')
        self.sb_wind_speed = _get(self, 'doubleSpinBox_wind_speed', 'wind_speed')
        self.sb_cur_dir    = _get(self, 'spinBox_current_dir', 'current_direction')
        self.sb_cur_speed  = _get(self, 'doubleSpinBox_current_speed', 'current_speed')

        self.sb_elapsed_hours = _get(self, 'doubleSpinBox_elapsed_hours', 'spinBox_drift_time', 'doubleSpinBox_time')

        # Кнопки (ищем разные варианты имен)
        self.btn_calc   = _get(self, 'pushButton_calculate', 'btn_calculate')
        self.btn_save   = _get(self, 'pushButton_save', 'btn_save')
        self.btn_cancel = _get(self, 'pushButton_cancel', 'btn_cancel')

        if isinstance(self.btn_calc, QPushButton):
            self.btn_calc.clicked.connect(self.on_calculate)
        if isinstance(self.btn_save, QPushButton):
            self.btn_save.clicked.connect(self.accept)
        if isinstance(self.btn_cancel, QPushButton):
            self.btn_cancel.clicked.connect(self.reject)

        # Установка разумных значений по умолчанию (если поля пустые)
        if self.dt_incident and isinstance(self.dt_incident, QDateTime):
            self.dt_incident.setDateTime(QDateTime.currentDateTime())
        if self.dt_lkp and isinstance(self.dt_lkp, QDateTime):
            self.dt_lkp.setDateTime(QDateTime.currentDateTime())

        self._drift = DriftCalculator()

    # ---------- расчёт ----------
    def on_calculate(self):
        try:
            lat = _spin_value(self.sb_lat, 0.0)
            lon = _spin_value(self.sb_lon, 0.0)

            wind_dir   = _spin_value(self.sb_wind_dir,   0.0)
            wind_speed = _spin_value(self.sb_wind_speed, 0.0)
            cur_dir    = _spin_value(self.sb_cur_dir,    0.0)
            cur_speed  = _spin_value(self.sb_cur_speed,  0.0)

            # Если отдельного «времени дрейфа» нет, оцениваем его по разнице дат
            hours = _spin_value(self.sb_elapsed_hours, 0.0)
            if hours <= 0.0 and self.dt_incident:
                dt = self.dt_incident.dateTime().toPyDateTime().replace(tzinfo=None)
                now = datetime.utcnow()
                hours = max(0.0, (now - dt).total_seconds() / 3600.0)
            if hours <= 0.0:
                hours = 1.0  # безопасный минимум

            # Тип объекта поиска (если есть). Если нет — «Обломки»
            obj_type = 'Обломки'
            cb = getattr(self, 'comboBox_object_type', None)
            if cb is not None and hasattr(cb, 'currentText'):
                t = cb.currentText().strip()
                if t:
                    obj_type = t

            drift_data = self._drift.calculate_total_drift(
                wind={'direction': wind_dir, 'speed': wind_speed},
                current={'direction': cur_dir, 'speed': cur_speed},
                object_type=obj_type,
                elapsed_hours=hours
            )
            dv = drift_data['center']['drift_vector']

            # Пересчёт Datum из начальных координат
            if self.le_datum or self.le_twc:
                # смещение в градусы (~1 NM = 1/60 градуса)
                distance_nm = dv.speed * hours
                math_angle = math.radians(90 - dv.direction)
                dx_nm = distance_nm * math.cos(math_angle)
                dy_nm = distance_nm * math.sin(math_angle)

                dlat = dy_nm / 60.0
                dlon = dx_nm / (60.0 * max(1e-6, math.cos(math.radians(lat))))
                new_lat = lat + dlat
                new_lon = lon + dlon

                if self.le_twc:
                    self.le_twc.setText(f"{dv.speed:.2f} kn @ {dv.direction:.0f}°")
                if self.le_datum:
                    self.le_datum.setText(f"{new_lat:.6f}, {new_lon:.6f}")

            # ASW тут не считаем — поле оставляем для отдельного алгоритма (у вас он есть отдельно)
            # но значение очищаем/обновляем чтобы было видно, что расчёт прошёл
            if self.le_asw and not self.le_asw.text():
                self.le_asw.setText("—")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка расчёта", str(e))
