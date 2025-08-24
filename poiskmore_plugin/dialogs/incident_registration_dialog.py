#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Файл: incident_registration_dialog.py
Назначение: Полноценный диалог регистрации происшествия (SAR) c 4 вкладками.
Загружает интерфейс из incident_registration_dialog.ui, выполняет расчёты ASW/TWC/Datum,
валидацию и отдаёт результат через сигнал incident_registered.
Совместимо с PyQt5.
"""

import math
from datetime import datetime
from pathlib import Path

from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMessageBox, QTableWidgetItem
)


class IncidentRegistrationDialog(QDialog):
    """
    Диалог регистрации происшествия на море, соответствующий методике IAMSAR.
    Интерфейс загружается из incident_registration_dialog.ui (находится рядом с .py).
    """
    incident_registered = pyqtSignal(dict)

    def __init__(self, parent=None, ui_path: Path = None):
        super().__init__(parent)

        # Путь к UI по умолчанию — рядом с этим .py
        self._ui_path = ui_path or Path(__file__).with_name('incident_registration_dialog.ui')
        if not self._ui_path.exists():
            raise FileNotFoundError(f'UI-файл не найден: {self._ui_path}')

        # Загружаем UI и создаём атрибуты по objectName
        uic.loadUi(str(self._ui_path), self)

        # Подготовка комбобоксов и значений по умолчанию
        self._populate_enums()
        self._set_defaults()

        # Инициализация таблицы объектов поиска (если пуста)
        self._init_search_objects_table()

        # Сигналы
        self.pushButton_calculate.clicked.connect(self.calculate_parameters)
        self.pushButton_save.clicked.connect(self.save_incident)
        self.pushButton_cancel.clicked.connect(self.reject)

        # Хранилище собранных данных
        self.incident_data = {}

    # --------------------------- UI helpers ---------------------------

    def _populate_enums(self):
        """Заполнение справочных списков в комбобоксах (если они ещё пусты)."""
        # Шкала Бофорта
        if self.comboBox_beaufort.count() == 0:
            self.comboBox_beaufort.addItems([
                "0 - Штиль (0-1 узел)",
                "1 - Тихий (1-3 узла)",
                "2 - Легкий (4-6 узлов)",
                "3 - Слабый (7-10 узлов)",
                "4 - Умеренный (11-16 узлов)",
                "5 - Свежий (17-21 узел)",
                "6 - Сильный (22-27 узлов)",
                "7 - Крепкий (28-33 узла)",
                "8 - Очень крепкий (34-40 узлов)",
                "9 - Шторм (41-47 узлов)",
                "10 - Сильный шторм (48-55 узлов)",
                "11 - Жестокий шторм (56-63 узла)",
                "12 - Ураган (>64 узлов)",
            ])

        # Шкала Дугласа
        if self.comboBox_douglas.count() == 0:
            self.comboBox_douglas.addItems([
                "0 - Зеркально гладкое",
                "1 - Рябь (0-0.1 м)",
                "2 - Слабое волнение (0.1-0.5 м)",
                "3 - Легкое волнение (0.5-1.25 м)",
                "4 - Умеренное волнение (1.25-2.5 м)",
                "5 - Неспокойное море (2.5-4 м)",
                "6 - Крупное волнение (4-6 м)",
                "7 - Очень крупное (6-9 м)",
                "8 - Огромное (9-14 м)",
                "9 - Исключительное (>14 м)",
            ])

        # Видимость
        if self.comboBox_visibility.count() == 0:
            self.comboBox_visibility.addItems([
                "Отличная (>10 миль)",
                "Очень хорошая (5-10 миль)",
                "Хорошая (2-5 миль)",
                "Умеренная (1-2 мили)",
                "Плохая (0.5-1 миля)",
                "Очень плохая (200-500 м)",
                "Туман (<200 м)",
            ])

        # Осадки
        if self.comboBox_precipitation.count() == 0:
            self.comboBox_precipitation.addItems([
                "Нет",
                "Морось",
                "Небольшой дождь",
                "Дождь",
                "Сильный дождь",
                "Небольшой снег",
                "Снег",
                "Сильный снег",
                "Град",
            ])

        # Облачность (октасы)
        if self.comboBox_cloud_cover.count() == 0:
            self.comboBox_cloud_cover.addItems([
                "0/8 - Ясно",
                "1/8 - Почти ясно",
                "2/8 - Небольшая облачность",
                "3/8 - Переменная облачность",
                "4/8 - Облачно с прояснениями",
                "5/8 - Облачно",
                "6/8 - Значительная облачность",
                "7/8 - Почти сплошная",
                "8/8 - Сплошная облачность",
            ])

        # Тип судна
        if self.comboBox_vessel_type.count() == 0:
            self.comboBox_vessel_type.addItems([
                "Грузовое судно",
                "Танкер",
                "Пассажирское судно",
                "Рыболовное судно",
                "Яхта/катер",
                "Военный корабль",
                "Подводная лодка",
                "Воздушное судно",
                "Другое",
            ])

        # Тип происшествия
        if self.comboBox_incident_type.count() == 0:
            self.comboBox_incident_type.addItems([
                "Бедствие судна",
                "Человек за бортом",
                "Авиакатастрофа на море",
                "Медицинская эвакуация",
                "Пропажа судна",
                "Пожар на судне",
                "Другое",
            ])

        # Источник информации
        if self.comboBox_info_source.count() == 0:
            self.comboBox_info_source.addItems([
                "Сигнал бедствия EPIRB",
                "Радиосообщение",
                "Визуальное наблюдение",
                "Сообщение от другого судна",
                "Береговые службы",
                "Авиация",
            ])

        # Точность позиции
        if self.comboBox_position_accuracy.count() == 0:
            self.comboBox_position_accuracy.addItems([
                "Точная (GPS)",
                "Приблизительная (±1 миля)",
                "Район (±5 миль)",
                "Общий район (±10 миль)",
                "Неизвестна",
            ])

        # Состояние людей
        if self.comboBox_people_condition.count() == 0:
            self.comboBox_people_condition.addItems([
                "Хорошее",
                "Удовлетворительное",
                "Требуется медпомощь",
                "Критическое",
                "Неизвестно",
            ])

    def _set_defaults(self):
        """Установка типовых значений по умолчанию."""
        now = datetime.now().strftime('%Y%m%d_%H%M')
        if not self.lineEdit_operation_name.text():
            self.lineEdit_operation_name.setText(f"SAR_{now}")

        # Погодные параметры
        self.spinBox_wind_dir.setValue(0)
        self.spinBox_wind_speed.setValue(10)
        self.comboBox_beaufort.setCurrentIndex(min(3, self.comboBox_beaufort.count()-1))

        self.comboBox_douglas.setCurrentIndex(min(2, self.comboBox_douglas.count()-1))
        self.doubleSpinBox_wave_height.setValue(0.8)

        self.spinBox_current_dir.setValue(90)
        self.doubleSpinBox_current_speed.setValue(0.5)

        self.comboBox_visibility.setCurrentIndex(min(2, self.comboBox_visibility.count()-1))
        self.comboBox_precipitation.setCurrentIndex(0)
        self.comboBox_cloud_cover.setCurrentIndex(5)

        self.spinBox_air_temp.setValue(15)
        self.spinBox_water_temp.setValue(12)

        self.spinBox_swell_dir.setValue(0)
        self.doubleSpinBox_swell_height.setValue(0.0)

        # Координаты как 0 по умолчанию — пользователь должен ввести реальные
        # Даты в виджетах уже стоят "сейчас" из .ui

    def _init_search_objects_table(self):
        """Заполнение таблицы объектов поиска стандартными значениями, если она пуста."""
        tbl = self.tableWidget_search_objects
        if tbl.rowCount() == 0:
            items = [
                ("Спасательный плот", "0", ""),
                ("Человек в спасжилете", "0", ""),
                ("Человек без спасжилета", "0", ""),
                ("Обломки", "0", ""),
                ("Масляное пятно", "0", ""),
            ]
            tbl.setRowCount(len(items))
            for r, (obj, qty, note) in enumerate(items):
                tbl.setItem(r, 0, QTableWidgetItem(obj))
                tbl.setItem(r, 1, QTableWidgetItem(qty))
                tbl.setItem(r, 2, QTableWidgetItem(note))

    # --------------------------- Calculations ---------------------------

    def calculate_parameters(self):
        """Расчёт ASW, TWC и Datum (упрощённые формулы для оперативной оценки)."""
        try:
            # Исходная позиция
            lat = self.doubleSpinBox_latitude.value()
            lon = self.doubleSpinBox_longitude.value()

            # Время, прошедшее с момента происшествия (часы)
            incident_dt = self.dateTimeEdit_incident.dateTime().toPyDateTime()
            now_dt = datetime.now()
            elapsed_hours = max(0.0, (now_dt - incident_dt).total_seconds() / 3600.0)

            # Ветер
            wind_speed = self.spinBox_wind_speed.value()          # уз
            wind_dir = self.spinBox_wind_dir.value()              # градусы, откуда дует/куда течёт — принята к направлению дрейфа

            # Течение
            cur_speed = self.doubleSpinBox_current_speed.value()  # уз
            cur_dir = self.spinBox_current_dir.value()            # градусы

            # Ветровой дрейф ~3% от скорости ветра
            wind_drift_speed = wind_speed * 0.03

            # Разложение по осям (направления в судовождении: 0° = север, 90° = восток)
            def to_xy(speed, course_deg):
                x = speed * math.sin(math.radians(course_deg))
                y = speed * math.cos(math.radians(course_deg))
                return x, y

            wdx, wdy = to_xy(wind_drift_speed, wind_dir)
            cdx, cdy = to_xy(cur_speed, cur_dir)

            twc_x = wdx + cdx
            twc_y = wdy + cdy

            twc_speed = math.hypot(twc_x, twc_y)              # узлы
            twc_dir = math.degrees(math.atan2(twc_x, twc_y))  # курс, 0..360
            if twc_dir < 0:
                twc_dir += 360.0

            # ASW — базовая доступная ширина поиска (условно 2 мили для крупного объекта)
            base_asw = 2.0
            visibility_factor = {
                0: 1.0,  # Отличная
                1: 0.9,
                2: 0.75,
                3: 0.5,
                4: 0.3,
                5: 0.15,
                6: 0.05,  # Туман
            }.get(self.comboBox_visibility.currentIndex(), 0.5)

            sea_state_factor = 1.0 - (min(self.comboBox_douglas.currentIndex(), 7) * 0.1)
            sea_state_factor = max(0.1, sea_state_factor)
            asw = base_asw * visibility_factor * sea_state_factor  # мили

            # Смещение Datum: узлы * часы = мили; переводим в градусы
            drift_nm = twc_speed * elapsed_hours  # морские мили
            # 1 морская миля ≈ 1/60 градуса широты
            dlat = (drift_nm * math.cos(math.radians(twc_dir))) / 60.0
            # для долготы учитываем широту
            dlon = 0.0
            cos_lat = math.cos(math.radians(lat)) or 1e-6
            dlon = (drift_nm * math.sin(math.radians(twc_dir))) / (60.0 * cos_lat)

            datum_lat = lat + dlat
            datum_lon = lon + dlon

            # Вывод на форму
            self.lineEdit_asw.setText(f"{asw:.2f}")
            self.lineEdit_twc.setText(f"{twc_speed:.2f} уз / {twc_dir:.0f}°")
            self.lineEdit_datum.setText(f"{datum_lat:.6f}°, {datum_lon:.6f}°")

            # Сохраняем в структуру
            self.incident_data['calculations'] = {
                'asw_miles': asw,
                'twc_speed_kn': twc_speed,
                'twc_course_deg': twc_dir,
                'datum_lat': datum_lat,
                'datum_lon': datum_lon,
                'elapsed_hours': elapsed_hours,
            }

            QMessageBox.information(
                self, "Расчёт выполнен",
                (f"ASW: {asw:.2f} миль\n"
                 f"TWC: {twc_speed:.2f} уз, курс {twc_dir:.0f}°\n"
                 f"Datum: {datum_lat:.6f}°, {datum_lon:.6f}°\n"
                 f"Прошло времени: {elapsed_hours:.1f} ч")
            )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка расчёта", f"Не удалось выполнить расчёт:\n{e}")

    # --------------------------- Validation & Save ---------------------------

    def _validate(self):
        """Проверка корректности заполнения полей. Возвращает список ошибок."""
        errors = []

        if not self.lineEdit_operation_name.text().strip():
            errors.append("Не указано название операции.")

        lat = self.doubleSpinBox_latitude.value()
        lon = self.doubleSpinBox_longitude.value()
        if abs(lat) < 1e-9 and abs(lon) < 1e-9:
            errors.append("Не заданы координаты происшествия.")

        # Количество людей (общее) — хотя бы одно значение > 0
        people_total = (
            self.spinBox_on_board.value() +
            self.spinBox_in_water.value() +
            self.spinBox_in_rafts.value()
        )
        if people_total == 0:
            errors.append("Не указано количество людей для спасения.")

        # Время происшествия не должно быть в будущем
        incident_dt = self.dateTimeEdit_incident.dateTime().toPyDateTime()
        if incident_dt > datetime.now():
            errors.append("Время происшествия не может быть в будущем.")

        return errors

    def save_incident(self):
        """Сбор данных, валидация и эмит сигнала incident_registered."""
        errors = self._validate()
        if errors:
            QMessageBox.warning(self, "Ошибки заполнения", "\n".join(errors))
            return

        def iso(dt_edit):
            return dt_edit.dateTime().toString(Qt.ISODate)

        # Вкладка 1
        data = {
            'operation_name': self.lineEdit_operation_name.text().strip(),
            'incident_type': self.comboBox_incident_type.currentText(),
            'incident_datetime': iso(self.dateTimeEdit_incident),
            'info_source': self.comboBox_info_source.currentText(),
            'latitude': self.doubleSpinBox_latitude.value(),
            'longitude': self.doubleSpinBox_longitude.value(),
            'position_accuracy': self.comboBox_position_accuracy.currentText(),
            'last_known_position_time': iso(self.dateTimeEdit_last_position),
        }

        # Вкладка 2
        data.update({
            'vessel_name': self.lineEdit_vessel_name.text(),
            'vessel_callsign': self.lineEdit_callsign.text(),
            'vessel_type': self.comboBox_vessel_type.currentText(),
            'vessel_length_m': self.spinBox_vessel_length.value(),
            'vessel_width_m': self.spinBox_vessel_width.value(),
            'vessel_color': self.lineEdit_vessel_color.text(),
            'people_on_board': self.spinBox_on_board.value(),
            'people_in_water': self.spinBox_in_water.value(),
            'people_in_rafts': self.spinBox_in_rafts.value(),
            'survival_equipment': self.textEdit_survival.toPlainText(),
            'people_condition': self.comboBox_people_condition.currentText(),
        })

        # Таблица объектов
        objects = []
        for r in range(self.tableWidget_search_objects.rowCount()):
            obj = self.tableWidget_search_objects.item(r, 0)
            qty = self.tableWidget_search_objects.item(r, 1)
            note = self.tableWidget_search_objects.item(r, 2)
            objects.append({
                'object': obj.text() if obj else "",
                'count': qty.text() if qty else "",
                'note': note.text() if note else "",
            })
        data['search_objects'] = objects

        # Вкладка 3
        data.update({
            'last_contact_time': iso(self.dateTimeEdit_last_contact),
            'working_frequencies': self.lineEdit_frequencies.text(),
            'emergency_beacons': self.lineEdit_emergency_beacons.text(),
            'last_course_deg': self.spinBox_course.value(),
            'last_speed_kn': self.doubleSpinBox_speed.value(),
            'destination': self.lineEdit_destination.text(),
            'eta': iso(self.dateTimeEdit_eta),
            'vessels_in_area': self.textEdit_vessels_in_area.toPlainText(),
            'aircraft_available': self.textEdit_aircraft_available.toPlainText(),
            'shore_facilities': self.textEdit_shore_facilities.toPlainText(),
            'additional_notes': self.textEdit_additional_notes.toPlainText(),
        })

        # Вкладка 4
        data.update({
            'wind_direction_deg': self.spinBox_wind_dir.value(),
            'wind_speed_kn': self.spinBox_wind_speed.value(),
            'beaufort_scale_index': self.comboBox_beaufort.currentIndex(),
            'douglas_scale_index': self.comboBox_douglas.currentIndex(),
            'wave_height_m': self.doubleSpinBox_wave_height.value(),
            'swell_direction_deg': self.spinBox_swell_dir.value(),
            'swell_height_m': self.doubleSpinBox_swell_height.value(),
            'current_direction_deg': self.spinBox_current_dir.value(),
            'current_speed_kn': self.doubleSpinBox_current_speed.value(),
            'visibility': self.comboBox_visibility.currentText(),
            'precipitation': self.comboBox_precipitation.currentText(),
            'cloud_cover': self.comboBox_cloud_cover.currentText(),
            'air_temp_c': self.spinBox_air_temp.value(),
            'water_temp_c': self.spinBox_water_temp.value(),
        })

        # Присоединяем расчёты, если уже были
        if hasattr(self, 'incident_data') and 'calculations' in self.incident_data:
            data['calculations'] = self.incident_data['calculations']

        # Эмит сигнала и уведомление
        self.incident_registered.emit(data)
        QMessageBox.information(self, "Сохранено",
                                f"Данные операции «{data['operation_name']}» сохранены.")
        self.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    dlg = IncidentRegistrationDialog()

    def _debug_print(payload: dict):
        print("=== INCIDENT DATA ===")
        for k, v in payload.items():
            if isinstance(v, dict):
                print(f"{k}:")
                for kk, vv in v.items():
                    print(f"  {kk}: {vv}")
            else:
                print(f"{k}: {v}")

    dlg.incident_registered.connect(_debug_print)
    dlg.show()
    sys.exit(app.exec_())
