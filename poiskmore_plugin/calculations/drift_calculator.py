# -*- coding: utf-8 -*-
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
