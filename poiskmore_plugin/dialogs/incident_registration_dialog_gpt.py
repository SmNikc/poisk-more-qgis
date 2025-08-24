
# -*- coding: utf-8 -*-
"""
Incident Registration Dialog (PyQt5) + Drift integration & GeoJSON export.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QComboBox, QDateTimeEdit, QTextEdit,
    QPushButton, QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QFileDialog
)
from PyQt5.QtCore import Qt, QDateTime, pyqtSignal
import math, json
from datetime import datetime

from drift_calculator import DriftCalculator, DriftVector

class IncidentRegistrationDialog(QDialog):
    incident_registered = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация происшествия")
        self.setMinimumSize(900, 680)
        self.data = {}
        self.drift_calc = DriftCalculator()
        self._build_ui()
        self._defaults()

    # --- UI ---
    def _build_ui(self):
        root = QVBoxLayout(self)
        self.tabs = QTabWidget()

        self.tab1 = self._tab_incident_location()
        self.tab2 = self._tab_search_objects()
        self.tab3 = self._tab_additional()
        self.tab4 = self._tab_weather()
        self.tabs.addTab(self.tab1, "Объект/Местоположение")
        self.tabs.addTab(self.tab2, "Объекты поиска")
        self.tabs.addTab(self.tab3, "Доп. информация")
        self.tabs.addTab(self.tab4, "Погода")
        root.addWidget(self.tabs)

        # Buttons
        btns = QHBoxLayout()
        self.btn_calc = QPushButton("Рассчитать параметры")
        self.btn_calc.clicked.connect(self.calculate_parameters)
        self.btn_export = QPushButton("Экспорт дрейфа (GeoJSON)")
        self.btn_export.clicked.connect(self.export_geojson)
        self.btn_save = QPushButton("Сохранить")
        self.btn_save.clicked.connect(self.save_incident)
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)

        btns.addWidget(self.btn_calc)
        btns.addWidget(self.btn_export)
        btns.addStretch(1)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        root.addLayout(btns)

    def _tab_incident_location(self):
        w = QWidget(); lay = QVBoxLayout(w)

        g1 = QGroupBox("Информация о происшествии"); f1 = QFormLayout(g1)
        self.operation_name = QLineEdit()
        self.incident_type = QComboBox()
        self.incident_type.addItems(["Бедствие судна","Человек за бортом","Авиакатастрофа на море","Медицинская эвакуация","Пропажа судна","Пожар на судне","Другое"])
        self.incident_dt = QDateTimeEdit(QDateTime.currentDateTime()); self.incident_dt.setCalendarPopup(True); self.incident_dt.setDisplayFormat("dd.MM.yyyy HH:mm UTC")
        self.info_source = QComboBox(); self.info_source.addItems(["Сигнал бедствия EPIRB","Радиосообщение","Визуальное наблюдение","Сообщение от другого судна","Береговые службы","Авиация"])
        f1.addRow("Название операции:", self.operation_name)
        f1.addRow("Тип происшествия:", self.incident_type)
        f1.addRow("Дата/время происшествия:", self.incident_dt)
        f1.addRow("Источник информации:", self.info_source)
        lay.addWidget(g1)

        g2 = QGroupBox("Местоположение происшествия"); f2 = QFormLayout(g2)
        coord = QHBoxLayout()
        self.lat = QDoubleSpinBox(); self.lat.setRange(-90,90); self.lat.setDecimals(6); self.lat.setSuffix("°")
        self.lon = QDoubleSpinBox(); self.lon.setRange(-180,180); self.lon.setDecimals(6); self.lon.setSuffix("°")
        c1 = QHBoxLayout(); c1.addWidget(QLabel("Широта:")); c1.addWidget(self.lat)
        c2 = QHBoxLayout(); c2.addWidget(QLabel("Долгота:")); c2.addWidget(self.lon)
        coord.addLayout(c1); coord.addLayout(c2)
        f2.addRow(coord)
        self.position_accuracy = QComboBox(); self.position_accuracy.addItems(["Точная (GPS)","Приблизительная (±1 миля)","Район (±5 миль)","Общий район (±10 миль)","Неизвестна"])
        self.lkp_time = QDateTimeEdit(QDateTime.currentDateTime()); self.lkp_time.setCalendarPopup(True); self.lkp_time.setDisplayFormat("dd.MM.yyyy HH:mm UTC")
        f2.addRow("Точность позиции:", self.position_accuracy)
        f2.addRow("Время последней позиции:", self.lkp_time)
        lay.addWidget(g2)

        g3 = QGroupBox("Расчетные параметры"); f3 = QFormLayout(g3)
        self.asw = QLineEdit(); self.asw.setReadOnly(True)
        self.twc = QLineEdit(); self.twc.setReadOnly(True)
        self.datum = QLineEdit(); self.datum.setReadOnly(True)
        f3.addRow("ASW (мили):", self.asw)
        f3.addRow("TWC (узлы/курс):", self.twc)
        f3.addRow("Datum:", self.datum)
        lay.addWidget(g3)

        lay.addStretch(1)
        return w

    def _tab_search_objects(self):
        w = QWidget(); lay = QVBoxLayout(w)
        g = QGroupBox("Объекты для поиска"); f = QFormLayout(g)
        self.tbl = QTableWidget(5,3); self.tbl.setHorizontalHeaderLabels(["Объект","Количество","Примечание"])
        items = [("Спасательный плот","0",""),("Человек в спасжилете","0",""),("Человек без спасжилета","0",""),("Обломки","0",""),("Масляное пятно","0","")]
        for r,(obj,cnt,note) in enumerate(items):
            self.tbl.setItem(r,0,QTableWidgetItem(obj))
            self.tbl.setItem(r,1,QTableWidgetItem(cnt))
            self.tbl.setItem(r,2,QTableWidgetItem(note))
        f.addRow(self.tbl)
        lay.addWidget(g)
        lay.addStretch(1)
        return w

    def _tab_additional(self):
        w = QWidget(); lay = QVBoxLayout(w)
        g = QGroupBox("Связь / Навигация"); f = QFormLayout(g)
        self.last_contact = QDateTimeEdit(QDateTime.currentDateTime()); self.last_contact.setCalendarPopup(True); self.last_contact.setDisplayFormat("dd.MM.yyyy HH:mm UTC")
        self.freq = QLineEdit()
        self.last_course = QSpinBox(); self.last_course.setRange(0,359); self.last_course.setSuffix("°")
        self.last_speed = QDoubleSpinBox(); self.last_speed.setRange(0,50); self.last_speed.setSuffix(" узлов")
        f.addRow("Последняя связь:", self.last_contact)
        f.addRow("Рабочие частоты:", self.freq)
        f.addRow("Последний курс/скорость:", self._pair(self.last_course, self.last_speed))
        lay.addWidget(g)
        self.notes = QTextEdit(); self.notes.setPlaceholderText("Примечания...")
        lay.addWidget(self.notes)
        return w

    def _tab_weather(self):
        w = QWidget(); lay = QVBoxLayout(w)
        g1 = QGroupBox("Ветер"); f1 = QFormLayout(g1)
        self.wind_dir = QSpinBox(); self.wind_dir.setRange(0,359); self.wind_dir.setSuffix("°")
        self.wind_spd = QSpinBox(); self.wind_spd.setRange(0,100); self.wind_spd.setSuffix(" узлов")
        f1.addRow("Направление/Скорость:", self._pair(self.wind_dir, self.wind_spd))
        lay.addWidget(g1)

        g2 = QGroupBox("Течение"); f2 = QFormLayout(g2)
        self.cur_dir = QSpinBox(); self.cur_dir.setRange(0,359); self.cur_dir.setSuffix("°")
        self.cur_spd = QDoubleSpinBox(); self.cur_spd.setRange(0,10); self.cur_spd.setDecimals(1); self.cur_spd.setSuffix(" узлов")
        f2.addRow("Направление/Скорость:", self._pair(self.cur_dir, self.cur_spd))
        lay.addWidget(g2)
        return w

    def _pair(self, a, b):
        box = QHBoxLayout(); box.addWidget(a); box.addWidget(b); w = QWidget(); w.setLayout(box); return w

    def _defaults(self):
        self.operation_name.setText(f"SAR_{datetime.now().strftime('%Y%m%d_%H%M')}")
        self.wind_dir.setValue(0); self.wind_spd.setValue(10)
        self.cur_dir.setValue(90); self.cur_spd.setValue(0.5)

    # --- helpers ---
    def _elapsed_hours(self) -> float:
        inc = self.incident_dt.dateTime().toPyDateTime()
        now = datetime.utcnow()
        return max(0.0, (now - inc).total_seconds()/3600.0)

    def _primary_object_type(self) -> str:
        # Берем первый объект с count > 0, иначе 'Обломки'; маппинг 'Человек без спасжилета' -> 'Человек в воде'
        rows = self.tbl.rowCount()
        for r in range(rows):
            try:
                cnt = float(self.tbl.item(r,1).text().strip().replace(',', '.'))
            except Exception:
                cnt = 0
            name = self.tbl.item(r,0).text().strip()
            if cnt > 0:
                if name == "Человек без спасжилета":
                    return "Человек в воде"
                return name
        return "Обломки"

    def _accuracy_to_error_nm(self) -> float:
        idx = self.position_accuracy.currentIndex()
        return {0:0.1, 1:1.0, 2:5.0, 3:10.0}.get(idx, 10.0)

    # --- core actions ---
    def calculate_parameters(self):
        try:
            lat, lon = self.lat.value(), self.lon.value()
            if lat==0 and lon==0:
                raise ValueError("Укажите координаты происшествия.")
            hours = self._elapsed_hours()
            wind = {'direction': self.wind_dir.value(), 'speed': float(self.wind_spd.value())}
            current = {'direction': self.cur_dir.value(), 'speed': float(self.cur_spd.value())}
            obj = self._primary_object_type()

            # TWC/Datum через калькулятор
            drift = self.drift_calc.calculate_total_drift(wind, current, obj, hours)
            v = drift['center']['drift_vector']
            datum_center = self.drift_calc.calculate_new_position(lat, lon, v.speed*hours, v.direction)

            # Простейший ASW (плейсхолдер): зависит от видимости/моря — можно расширить позже
            base_asw = 2.0
            asw_val = base_asw

            self.asw.setText(f"{asw_val:.2f}")
            self.twc.setText(f"{v.speed:.2f} уз / {v.direction:.0f}°")
            self.datum.setText(f"{datum_center[0]:.6f}°, {datum_center[1]:.6f}°")

            # Сохраняем краткие расчёты
            self.data['calculations'] = {
                'asw_nm': asw_val,
                'twc_speed_kn': v.speed,
                'twc_direction_deg': v.direction,
                'datum_center': {'lat': datum_center[0], 'lon': datum_center[1]},
                'elapsed_hours': hours,
                'object_type': obj
            }
            QMessageBox.information(self, "OK", "Расчёт выполнен.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def export_geojson(self):
        try:
            lat, lon = self.lat.value(), self.lon.value()
            if lat==0 and lon==0:
                raise ValueError("Укажите координаты происшествия.")
            hours = self._elapsed_hours()
            wind = {'direction': self.wind_dir.value(), 'speed': float(self.wind_spd.value())}
            current = {'direction': self.cur_dir.value(), 'speed': float(self.cur_spd.value())}
            obj = self._primary_object_type()

            drift = self.drift_calc.calculate_total_drift(wind, current, obj, hours)
            datum_pts = self.drift_calc.datum_points(lat, lon, drift, hours)
            center_vec = drift['center']['drift_vector']
            line_pts = self.drift_calc.drift_line(lat, lon, center_vec, hours, num_points=12)
            search = self.drift_calc.search_area_expansion(self._accuracy_to_error_nm(), drift, hours)

            # Дополнительно построим шаблон поиска "расширяющийся квадрат" от Datum Center
            esq = self.drift_calc.expanding_square(datum_pts['center']['lat'], datum_pts['center']['lon'], track_spacing_nm=1.0, first_leg_deg=0.0, legs=7)

            # В GeoJSON положим datum, линию дрейфа, круг радиуса поиска и маршрут ESQ как LineString
            gj = self.drift_calc.to_geojson(datum_pts, line_pts, search['search_radius_nm'])
            gj['features'].append({
                "type": "Feature",
                "properties": {"name": "Expanding Square (ES)"},
                "geometry": {"type": "LineString", "coordinates": [[lon, lat] for (lat, lon) in esq]}
            })

            path, _ = QFileDialog.getSaveFileName(self, "Сохранить GeoJSON", "datum_drift.geojson", "GeoJSON (*.geojson)")
            if not path:
                return
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(gj, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Экспортирован", f"Сохранено:
{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", str(e))

    def save_incident(self):
        # простая сериализация основных полей
        self.data.update({
            'operation_name': self.operation_name.text(),
            'incident_type': self.incident_type.currentText(),
            'incident_datetime_iso': self.incident_dt.dateTime().toString(Qt.ISODate),
            'info_source': self.info_source.currentText(),
            'lat': self.lat.value(), 'lon': self.lon.value(),
            'position_accuracy': self.position_accuracy.currentText(),
            'lkp_time_iso': self.lkp_time.dateTime().toString(Qt.ISODate),
            'wind_dir': self.wind_dir.value(), 'wind_speed': self.wind_spd.value(),
            'current_dir': self.cur_dir.value(), 'current_speed': self.cur_spd.value(),
            'notes': self.notes.toPlainText()
        })
        self.incident_registered.emit(self.data)
        QMessageBox.information(self, "Сохранено", "Данные сохранены.")
        self.accept()

# For manual test run:
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    d = IncidentRegistrationDialog()
    d.show()
    sys.exit(app.exec_())
