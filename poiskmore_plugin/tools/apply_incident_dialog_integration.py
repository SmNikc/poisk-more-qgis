# -*- coding: utf-8 -*-
"""
apply_incident_dialog_integration.py
Полный установочный скрипт:
 - пишет/обновляет файлы:
    calculations/drift_calculator.py
    calculations/drift_calculator_qgis.py
    calculations/__init__.py
    dialogs/incident_registration_dialog.py
    dialogs/__init__.py
 - переименовывает «дефисные»/двойные файлы
 - патчит mainPlugin.py (initGui/unload, QAction, импорт диалога)
Запуск: python poiskmore_plugin/tools/apply_incident_dialog_integration.py
"""

import io
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALC = ROOT / "calculations"
DLGS = ROOT / "dialogs"
TOOLS = ROOT / "tools"
MAIN = ROOT / "mainPlugin.py"

# ---------- Полные исходники, которые будут записаны ----------

DRIFT_CALCULATOR_PY = r'''# -*- coding: utf-8 -*-
"""
Модуль расчета дрейфа объектов
Реализует расчеты согласно методике IAMSAR и документации ПОИСК-МОРЕ
"""

import math
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DriftVector:
    """Вектор дрейфа"""
    direction: float  # Направление в градусах (0-360)
    speed: float      # Скорость в узлах
    
    def to_components(self) -> Tuple[float, float]:
        """Преобразовать в компоненты x, y"""
        # Преобразуем направление из навигационного (откуда) в математическое
        math_angle = math.radians(90 - self.direction)
        x = self.speed * math.cos(math_angle)
        y = self.speed * math.sin(math_angle)
        return x, y


class DriftCalculator:
    """Класс для расчета дрейфа объектов поиска"""
    
    # Коэффициенты дрейфа для различных объектов (% от скорости ветра)
    LEEWAY_RATES = {
        'Спасательный плот': {
            'min': 2.0,
            'max': 4.0,
            'divergence': 30  # Угол расхождения в градусах
        },
        'Спасательная шлюпка': {
            'min': 1.5,
            'max': 3.0,
            'divergence': 20
        },
        'Человек в воде': {
            'min': 1.0,
            'max': 2.0,
            'divergence': 15
        },
        'Человек в спасжилете': {
            'min': 2.0,
            'max': 3.0,
            'divergence': 20
        },
        'Судно малое': {
            'min': 3.0,
            'max': 5.0,
            'divergence': 25
        },
        'Судно среднее': {
            'min': 2.0,
            'max': 4.0,
            'divergence': 20
        },
        'Судно большое': {
            'min': 1.0,
            'max': 2.5,
            'divergence': 15
        },
        'Обломки': {
            'min': 3.0,
            'max': 5.0,
            'divergence': 35
        },
        'Пустая шлюпка': {
            'min': 4.0,
            'max': 7.0,
            'divergence': 30
        }
    }
    
    def __init__(self):
        """Инициализация калькулятора дрейфа"""
        pass
    
    def calculate_total_drift(self, 
                             wind: Dict[str, float],
                             current: Dict[str, float],
                             object_type: str,
                             elapsed_hours: float) -> Dict:
        """
        Рассчитать суммарный дрейф объекта
        
        Args:
            wind: Словарь с данными ветра {'direction': градусы, 'speed': узлы}
            current: Словарь с данными течения {'direction': градусы, 'speed': узлы}
            object_type: Тип объекта поиска
            elapsed_hours: Время в часах с момента аварии
            
        Returns:
            Словарь с результатами расчета дрейфа
        """
        # Получаем коэффициенты дрейфа для объекта
        leeway_data = self.LEEWAY_RATES.get(object_type, self.LEEWAY_RATES['Обломки'])
        
        # Рассчитываем компоненты дрейфа
        wind_drift = self._calculate_wind_drift(wind, leeway_data)
        current_drift = self._calculate_current_drift(current)
        
        # Суммируем векторы дрейфа
        total_drift = self._sum_drift_vectors(wind_drift, current_drift)
        
        # Рассчитываем расхождение (для левого и правого дрейфа)
        divergence_angle = leeway_data['divergence']
        left_drift = self._apply_divergence(total_drift, -divergence_angle)
        right_drift = self._apply_divergence(total_drift, divergence_angle)
        
        # Рассчитываем смещение за время
        center_displacement = self._calculate_displacement(total_drift, elapsed_hours)
        left_displacement = self._calculate_displacement(left_drift, elapsed_hours)
        right_displacement = self._calculate_displacement(right_drift, elapsed_hours)
        
        return {
            'center': {
                'drift_vector': total_drift,
                'displacement': center_displacement,
                'distance_nm': total_drift.speed * elapsed_hours
            },
            'left': {
                'drift_vector': left_drift,
                'displacement': left_displacement,
                'distance_nm': left_drift.speed * elapsed_hours
            },
            'right': {
                'drift_vector': right_drift,
                'displacement': right_displacement,
                'distance_nm': right_drift.speed * elapsed_hours
            },
            'divergence_angle': divergence_angle,
            'leeway_rate': (leeway_data['min'] + leeway_data['max']) / 2
        }
    
    def _calculate_wind_drift(self, wind: Dict, leeway_data: Dict) -> DriftVector:
        """Рассчитать дрейф от ветра"""
        leeway_rate = (leeway_data['min'] + leeway_data['max']) / 2 / 100.0
        drift_speed = wind['speed'] * leeway_rate
        drift_direction = wind['direction']  # по ветру
        return DriftVector(drift_direction, drift_speed)
    
    def _calculate_current_drift(self, current: Dict) -> DriftVector:
        """Рассчитать дрейф от течения (100%)"""
        return DriftVector(current['direction'], current['speed'])
    
    def _sum_drift_vectors(self, wind_drift: DriftVector, current_drift: DriftVector) -> DriftVector:
        """Сложить ветровой и течения"""
        wind_x, wind_y = wind_drift.to_components()
        current_x, current_y = current_drift.to_components()
        total_x = wind_x + current_x
        total_y = wind_y + current_y
        total_speed = math.sqrt(total_x**2 + total_y**2)
        if total_speed > 0:
            math_angle = math.atan2(total_y, total_x)
            nav_direction = (90 - math.degrees(math_angle)) % 360
        else:
            nav_direction = 0
        return DriftVector(nav_direction, total_speed)
    
    def _apply_divergence(self, drift: DriftVector, divergence_angle: float) -> DriftVector:
        """Применить угол расхождения"""
        new_direction = (drift.direction + divergence_angle) % 360
        return DriftVector(new_direction, drift.speed)
    
    def _calculate_displacement(self, drift: DriftVector, hours: float) -> Dict:
        """Смещение объекта за время (в милях по осям)"""
        distance = drift.speed * hours
        math_angle = math.radians(90 - drift.direction)
        dx_nm = distance * math.cos(math_angle)
        dy_nm = distance * math.sin(math_angle)
        return {
            'dx_nm': dx_nm,
            'dy_nm': dy_nm,
            'distance_nm': distance,
            'direction': drift.direction
        }
    
    def calculate_search_area_expansion(self,
                                       initial_error: float,
                                       drift_data: Dict,
                                       elapsed_hours: float) -> Dict:
        """Расширение района поиска с учётом погрешностей"""
        position_error = drift_data['center']['distance_nm'] * 0.1
        divergence_error = drift_data['center']['distance_nm'] * \
                          math.sin(math.radians(drift_data['divergence_angle']))
        total_error = math.sqrt(initial_error**2 + position_error**2 + divergence_error**2)
        search_radius = total_error * 1.5
        return {
            'initial_error': initial_error,
            'position_error': position_error,
            'divergence_error': divergence_error,
            'total_error': total_error,
            'search_radius': search_radius,
            'search_area_nm2': math.pi * search_radius**2
        }
    
    def calculate_drift_line(self,
                           start_point: Tuple[float, float],
                           drift_vector: DriftVector,
                           hours: float,
                           num_points: int = 10) -> list:
        """Линия дрейфа (список точек lat/lon во времени)"""
        points = []
        lat_start, lon_start = start_point
        for i in range(num_points + 1):
            t = (i / num_points) * hours
            displacement = self._calculate_displacement(drift_vector, t)
            dlat = displacement['dy_nm'] / 60.0
            dlon = displacement['dx_nm'] / (60.0 * math.cos(math.radians(lat_start)))
            new_lat = lat_start + dlat
            new_lon = lon_start + dlon
            points.append({
                'lat': new_lat,
                'lon': new_lon,
                'time_hours': t,
                'distance_nm': displacement['distance_nm']
            })
        return points
    
    def get_object_types(self) -> list:
        """Список типов объектов"""
        return list(self.LEEWAY_RATES.keys())
    
    def get_leeway_info(self, object_type: str) -> Optional[Dict]:
        """Информация о коэффициентах дрейфа по типу объекта"""
        return self.LEEWAY_RATES.get(object_type)
'''

DRIFT_CALCULATOR_QGIS_PY = r'''# -*- coding: utf-8 -*-
"""
Модуль расчета дрейфа объектов на море (QGIS-геометрия)
Реализует методики IAMSAR Volume II
"""

import math
from typing import Dict, List, Tuple, Optional
from qgis.core import QgsPointXY

class DriftCalculator:
    """Калькулятор дрейфа согласно методике IAMSAR"""
    DRIFT_FACTORS = {
        'person_in_water': 0.011,
        'life_raft_4_person': 0.025,
        'life_raft_6_person': 0.024,
        'life_raft_10_person': 0.023,
        'life_raft_15_person': 0.022,
        'life_raft_20_person': 0.021,
        'life_raft_25_person': 0.020,
        'boat_v_bottom': 0.035,
        'boat_flat_bottom': 0.040,
        'sport_boat': 0.045,
        'surfboard': 0.050,
        'kayak': 0.040,
        'debris': 0.030,
        'vertical_person': 0.025,
        'horizontal_person': 0.015,
    }
    DRIFT_DIVERGENCE = {'left': -30, 'right': 30, 'downwind': 0}
    def __init__(self):
        self.earth_radius_nm = 3440.065
    def calculate_drift(self, 
                       lkp: QgsPointXY,
                       wind_speed: float,
                       wind_direction: float,
                       drift_time: float,
                       drift_factor: float = 0.03,
                       current_speed: float = 0,
                       current_direction: float = 0) -> Dict:
        wind_drift_speed = wind_speed * drift_factor
        wind_drift_distance = wind_drift_speed * drift_time
        current_drift_distance = current_speed * drift_time
        wind_x = wind_drift_distance * math.sin(math.radians(wind_direction))
        wind_y = wind_drift_distance * math.cos(math.radians(wind_direction))
        current_x = current_drift_distance * math.sin(math.radians(current_direction))
        current_y = current_drift_distance * math.cos(math.radians(current_direction))
        total_x = wind_x + current_x
        total_y = wind_y + current_y
        total_distance = math.sqrt(total_x**2 + total_y**2)
        total_direction = math.degrees(math.atan2(total_x, total_y)) % 360
        new_position = self.calculate_new_position(lkp.y(), lkp.x(), total_distance, total_direction)
        return {
            'lat': new_position[0],
            'lon': new_position[1],
            'distance': total_distance,
            'direction': total_direction,
            'wind_component': wind_drift_distance,
            'current_component': current_drift_distance,
            'name': 'Datum Point',
            'time': drift_time
        }
    def calculate_datum_points(self,
                             lkp: QgsPointXY,
                             wind_speed: float,
                             wind_direction: float,
                             current_speed: float,
                             current_direction: float,
                             drift_time: float,
                             drift_factor: float = 0.03,
                             divergence_angle: float = 10) -> List[Dict]:
        datum_points = []
        main_datum = self.calculate_drift(lkp, wind_speed, wind_direction, drift_time,
                                          drift_factor, current_speed, current_direction)
        main_datum['name'] = 'Datum Center'
        datum_points.append(main_datum)
        left_direction = (wind_direction - divergence_angle) % 360
        left_datum = self.calculate_drift(lkp, wind_speed, left_direction, drift_time,
                                          drift_factor, current_speed, current_direction)
        left_datum['name'] = 'Datum Left'
        datum_points.append(left_datum)
        right_direction = (wind_direction + divergence_angle) % 360
        right_datum = self.calculate_drift(lkp, wind_speed, right_direction, drift_time,
                                           drift_factor, current_speed, current_direction)
        right_datum['name'] = 'Datum Right'
        datum_points.append(right_datum)
        max_factor = drift_factor * 1.3
        far_datum = self.calculate_drift(lkp, wind_speed, wind_direction, drift_time,
                                         max_factor, current_speed, current_direction)
        far_datum['name'] = 'Datum Max'
        datum_points.append(far_datum)
        min_factor = drift_factor * 0.7
        near_datum = self.calculate_drift(lkp, wind_speed, wind_direction, drift_time,
                                          min_factor, current_speed, current_direction)
        near_datum['name'] = 'Datum Min'
        datum_points.append(near_datum)
        return datum_points
    def calculate_new_position(self, lat: float, lon: float, 
                              distance_nm: float, bearing: float) -> Tuple[float, float]:
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        angular_distance = distance_nm / self.earth_radius_nm
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance) +
            math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
        )
        new_lon_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )
        return (math.degrees(new_lat_rad), math.degrees(new_lon_rad))
    def calculate_leeway(self, object_type: str, wind_speed: float) -> float:
        drift_factor = self.DRIFT_FACTORS.get(object_type, 0.03)
        return wind_speed * drift_factor
    def calculate_total_water_current(self, 
                                     tidal_current: Tuple[float, float],
                                     ocean_current: Tuple[float, float],
                                     wind_current: Tuple[float, float]) -> Tuple[float, float]:
        total_x = total_y = 0.0
        for speed, direction in [tidal_current, ocean_current, wind_current]:
            total_x += speed * math.sin(math.radians(direction))
            total_y += speed * math.cos(math.radians(direction))
        total_speed = math.sqrt(total_x**2 + total_y**2)
        total_direction = math.degrees(math.atan2(total_x, total_y)) % 360
        return (total_speed, total_direction)
    def calculate_search_radius(self, drift_time: float, 
                              position_error: float = 0.1,
                              drift_error: float = 0.3) -> float:
        time_factor = math.sqrt(drift_time)
        error_radius = position_error + (drift_error * time_factor)
        return error_radius * 1.1
    def calculate_expanding_square_search(self, datum: Dict, 
                                         track_spacing: float,
                                         first_leg_direction: float = 0) -> List[Tuple[float, float]]:
        waypoints = []
        current_pos = (datum['lat'], datum['lon'])
        waypoints.append(current_pos)
        legs = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]
        direction = first_leg_direction
        for leg_number, leg_length in enumerate(legs):
            distance = track_spacing * leg_length
            current_pos = self.calculate_new_position(current_pos[0], current_pos[1], distance, direction)
            waypoints.append(current_pos)
            direction = (direction + 90) % 360
        return waypoints
'''

INCIDENT_DIALOG_PY = r'''# -*- coding: utf-8 -*-
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
'''

DLG_INIT_PY = r'''# -*- coding: utf-8 -*-
from .incident_registration_dialog import IncidentRegistrationDialog
'''

CALC_INIT_PY = r'''# -*- coding: utf-8 -*-  # пакет расчётов
'''

# ---------- Утилиты ----------

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        bak = path.with_suffix(path.suffix + f".bak-{time.strftime('%Y%m%d-%H%M%S')}")
        path.replace(bak)
        print(f"[backup] {path.name} -> {bak.name}")
    path.write_text(content, encoding="utf-8")
    print(f"[write ] {path.relative_to(ROOT)}")

def ensure_pkg(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    init_py = path / "__init__.py"
    if not init_py.exists():
        init_py.write_text("# -*- coding: utf-8 -*-\n", encoding="utf-8")
        print(f"[create] {init_py.relative_to(ROOT)}")

def rename_if_exists(src_rel: str, dst_rel: str):
    src = ROOT / src_rel
    dst = ROOT / dst_rel
    if src.exists():
        if not dst.parent.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            # если уже есть правильный — просто удаляем старый
            src.unlink()
            print(f"[remove] {src_rel}")
        else:
            src.replace(dst)
            print(f"[rename] {src_rel} -> {dst_rel}")

# ---- Патч mainPlugin.py ----

HEADER_QACTION = "from qgis.PyQt.QtWidgets import QAction"
HEADER_DIALOG  = "from .dialogs.incident_registration_dialog import IncidentRegistrationDialog"

def patch_mainplugin(main_path: Path):
    if not main_path.exists():
        print(f"[skip ] mainPlugin.py не найден: {main_path}")
        return

    text = main_path.read_text(encoding="utf-8")

    changed = False
    if HEADER_QACTION not in text:
        # добавим импорт QAction рядом с другими импортами PyQt
        text = HEADER_QACTION + "\n" + text
        changed = True
        print("[patch ] +QAction import")

    if HEADER_DIALOG not in text:
        # добавим импорт диалога рядом с импортами пакетов плагина
        # ставим сразу после QAction-строки, чтобы не усложнять анализ
        idx = text.find(HEADER_QACTION)
        if idx >= 0:
            insert_at = text.find("\n", idx) + 1
            text = text[:insert_at] + HEADER_DIALOG + "\n" + text[insert_at:]
        else:
            text = HEADER_DIALOG + "\n" + text
        changed = True
        print("[patch ] +IncidentRegistrationDialog import")

    # вставка в initGui
    if "def initGui" in text and "_open_incident_registration_dialog" not in text:
        # добавим обработчик
        handler = (
            "\n    def _open_incident_registration_dialog(self):\n"
            "        try:\n"
            "            dlg = IncidentRegistrationDialog(self.iface.mainWindow())\n"
            "            dlg.exec_()\n"
            "        except Exception as e:\n"
            "            # Не валим плагин при ошибке диалога\n"
            "            print('IncidentRegistrationDialog error:', e)\n"
        )
        text = text + handler
        changed = True
        print("[patch ] +_open_incident_registration_dialog()")

    # добавим QAction в initGui
    if "def initGui" in text and "action_incident" not in text:
        def_hdr = re.search(r"def\\s+initGui\\s*\\(.*?\\):", text)
        if def_hdr:
            start = def_hdr.end()
            # определим базовый отступ тела
            body_indent = " " * 4
            # вставляем сразу после заголовка функции
            lines = (
                f"\n{body_indent}# >>> IncidentRegistrationDialog integration\n"
                f"{body_indent}self.action_incident = QAction('Регистрация происшествия', self.iface.mainWindow())\n"
                f"{body_indent}self.action_incident.triggered.connect(self._open_incident_registration_dialog)\n"
                f"{body_indent}self.iface.addPluginToMenu('&Поиск-Море', self.action_incident)\n"
                f"{body_indent}# <<< IncidentRegistrationDialog integration\n"
            )
            text = text[:start] + lines + text[start:]
            changed = True
            print("[patch ] +initGui QAction")

    # снятие в unload
    if "def unload" in text and "removePluginMenu(\"&Поиск-Море\", self.action_incident)" not in text:
        def_unload = re.search(r"def\\s+unload\\s*\\(.*?\\):", text)
        if def_unload:
            start = def_unload.end()
            body_indent = " " * 4
            lines = (
                f"\n{body_indent}# >>> IncidentRegistrationDialog integration\n"
                f"{body_indent}try:\n"
                f"{body_indent}    self.iface.removePluginMenu('&Поиск-Море', self.action_incident)\n"
                f"{body_indent}except Exception:\n"
                f"{body_indent}    pass\n"
                f"{body_indent}# <<< IncidentRegistrationDialog integration\n"
            )
            text = text[:start] + lines + text[start:]
            changed = True
            print("[patch ] +unload cleanup")

    if changed:
        bak = main_path.with_suffix(main_path.suffix + f".bak-{time.strftime('%Y%m%d-%H%M%S')}")
        main_path.replace(bak)
        main_path.write_text(text, encoding="utf-8")
        print(f"[backup] mainPlugin.py -> {bak.name}")
        print("[write ] mainPlugin.py (patched)")
    else:
        print("[ok   ] mainPlugin.py уже содержит интеграцию")


def main():
    print(f"[root ] {ROOT}")

    # Переименования «дефисных» и двойных файлов
    rename_if_exists("calculations/drift-calculator.py", "calculations/drift_calculator.py")
    rename_if_exists("calculations/search-area-calculator.py", "calculations/search_area_calculator.py")
    rename_if_exists("calculations/drift_calculator_qgis.py.py", "calculations/drift_calculator_qgis.py")

    # Пакеты
    ensure_pkg(CALC)
    ensure_pkg(DLGS)

    # __init__.py
    write_file(CALC / "__init__.py", CALC_INIT_PY)
    write_file(DLGS / "__init__.py", DLG_INIT_PY)

    # Полные модули
    write_file(CALC / "drift_calculator.py", DRIFT_CALCULATOR_PY)
    write_file(CALC / "drift_calculator_qgis.py", DRIFT_CALCULATOR_QGIS_PY)
    write_file(DLGS / "incident_registration_dialog.py", INCIDENT_DIALOG_PY)

    # Патч меню
    patch_mainplugin(MAIN)

    print("Done.")

if __name__ == "__main__":
    main()
