# -*- coding: utf-8 -*-
"""
Модуль расчета дрейфа объектов на море
Реализует методики IAMSAR Volume II
"""

import math
from typing import Dict, List, Tuple, Optional
from qgis.core import QgsPointXY

class DriftCalculator:
    """Калькулятор дрейфа согласно методике IAMSAR"""
    
    # Константы дрейфа для различных объектов (из IAMSAR)
    DRIFT_FACTORS = {
        'person_in_water': 0.011,  # Человек в воде
        'life_raft_4_person': 0.025,  # Спасательный плот на 4 человека
        'life_raft_6_person': 0.024,  # Спасательный плот на 6 человек
        'life_raft_10_person': 0.023,  # Спасательный плот на 10 человек
        'life_raft_15_person': 0.022,  # Спасательный плот на 15 человек
        'life_raft_20_person': 0.021,  # Спасательный плот на 20 человек
        'life_raft_25_person': 0.020,  # Спасательный плот на 25 человек
        'boat_v_bottom': 0.035,  # Лодка с V-образным днищем
        'boat_flat_bottom': 0.040,  # Лодка с плоским днищем
        'sport_boat': 0.045,  # Спортивная лодка
        'surfboard': 0.050,  # Доска для серфинга
        'kayak': 0.040,  # Каяк
        'debris': 0.030,  # Обломки
        'vertical_person': 0.025,  # Человек в вертикальном положении
        'horizontal_person': 0.015,  # Человек в горизонтальном положении
    }
    
    # Поправки на направление дрейфа (градусы от направления ветра)
    DRIFT_DIVERGENCE = {
        'left': -30,  # Левое отклонение
        'right': 30,   # Правое отклонение
        'downwind': 0  # По ветру
    }
    
    def __init__(self):
        """Инициализация калькулятора"""
        self.earth_radius_nm = 3440.065  # Радиус Земли в морских милях
    
    def calculate_drift(self, 
                       lkp: QgsPointXY,
                       wind_speed: float,
                       wind_direction: float,
                       drift_time: float,
                       drift_factor: float = 0.03,
                       current_speed: float = 0,
                       current_direction: float = 0) -> Dict:
        """
        Рассчитать дрейф объекта
        
        Args:
            lkp: Последнее известное местоположение
            wind_speed: Скорость ветра (узлы)
            wind_direction: Направление ветра (градусы)
            drift_time: Время дрейфа (часы)
            drift_factor: Фактор дрейфа (обычно 0.02-0.04)
            current_speed: Скорость течения (узлы)
            current_direction: Направление течения (градусы)
            
        Returns:
            Словарь с рассчитанной точкой дрейфа
        """
        
        # Расчет ветрового дрейфа
        wind_drift_speed = wind_speed * drift_factor
        wind_drift_distance = wind_drift_speed * drift_time
        
        # Расчет течения
        current_drift_distance = current_speed * drift_time
        
        # Комбинированный дрейф (векторное сложение)
        wind_x = wind_drift_distance * math.sin(math.radians(wind_direction))
        wind_y = wind_drift_distance * math.cos(math.radians(wind_direction))
        
        current_x = current_drift_distance * math.sin(math.radians(current_direction))
        current_y = current_drift_distance * math.cos(math.radians(current_direction))
        
        total_x = wind_x + current_x
        total_y = wind_y + current_y
        
        # Общее расстояние и направление дрейфа
        total_distance = math.sqrt(total_x**2 + total_y**2)
        total_direction = math.degrees(math.atan2(total_x, total_y)) % 360
        
        # Расчет новой позиции
        new_position = self.calculate_new_position(
            lkp.y(), lkp.x(), total_distance, total_direction
        )
        
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
        """
        Рассчитать множественные исходные пункты с учетом дивергенции
        Согласно IAMSAR, рассчитываются 3-4 точки с учетом неопределенности
        
        Args:
            lkp: Последнее известное местоположение
            wind_speed: Скорость ветра (узлы)
            wind_direction: Направление ветра (градусы)
            current_speed: Скорость течения (узлы)
            current_direction: Направление течения (градусы)
            drift_time: Время дрейфа (часы)
            drift_factor: Фактор дрейфа
            divergence_angle: Угол дивергенции (градусы)
            
        Returns:
            Список исходных пунктов
        """
        datum_points = []
        
        # Основная точка дрейфа
        main_datum = self.calculate_drift(
            lkp, wind_speed, wind_direction, drift_time,
            drift_factor, current_speed, current_direction
        )
        main_datum['name'] = 'Datum Center'
        datum_points.append(main_datum)
        
        # Левая точка с учетом дивергенции
        left_direction = (wind_direction - divergence_angle) % 360
        left_datum = self.calculate_drift(
            lkp, wind_speed, left_direction, drift_time,
            drift_factor, current_speed, current_direction
        )
        left_datum['name'] = 'Datum Left'
        datum_points.append(left_datum)
        
        # Правая точка с учетом дивергенции
        right_direction = (wind_direction + divergence_angle) % 360
        right_datum = self.calculate_drift(
            lkp, wind_speed, right_direction, drift_time,
            drift_factor, current_speed, current_direction
        )
        right_datum['name'] = 'Datum Right'
        datum_points.append(right_datum)
        
        # Дальняя точка (максимальный дрейф)
        max_factor = drift_factor * 1.3  # Увеличиваем фактор на 30%
        far_datum = self.calculate_drift(
            lkp, wind_speed, wind_direction, drift_time,
            max_factor, current_speed, current_direction
        )
        far_datum['name'] = 'Datum Max'
        datum_points.append(far_datum)
        
        # Ближняя точка (минимальный дрейф)
        min_factor = drift_factor * 0.7  # Уменьшаем фактор на 30%
        near_datum = self.calculate_drift(
            lkp, wind_speed, wind_direction, drift_time,
            min_factor, current_speed, current_direction
        )
        near_datum['name'] = 'Datum Min'
        datum_points.append(near_datum)
        
        return datum_points
    
    def calculate_new_position(self, lat: float, lon: float, 
                              distance_nm: float, bearing: float) -> Tuple[float, float]:
        """
        Рассчитать новую позицию от исходной точки
        
        Args:
            lat: Широта исходной точки (градусы)
            lon: Долгота исходной точки (градусы)
            distance_nm: Расстояние (морские мили)
            bearing: Направление (градусы)
            
        Returns:
            Кортеж (новая широта, новая долгота)
        """
        # Конвертация в радианы
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        
        # Расчет по формуле большого круга
        angular_distance = distance_nm / self.earth_radius_nm
        
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance) +
            math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
        )
        
        new_lon_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )
        
        # Конвертация обратно в градусы
        new_lat = math.degrees(new_lat_rad)
        new_lon = math.degrees(new_lon_rad)
        
        return (new_lat, new_lon)
    
    def calculate_leeway(self, object_type: str, wind_speed: float) -> float:
        """
        Рассчитать снос (leeway) для объекта
        
        Args:
            object_type: Тип объекта из DRIFT_FACTORS
            wind_speed: Скорость ветра (узлы)
            
        Returns:
            Скорость сноса (узлы)
        """
        drift_factor = self.DRIFT_FACTORS.get(object_type, 0.03)
        return wind_speed * drift_factor
    
    def calculate_total_water_current(self, 
                                     tidal_current: Tuple[float, float],
                                     ocean_current: Tuple[float, float],
                                     wind_current: Tuple[float, float]) -> Tuple[float, float]:
        """
        Рассчитать суммарное течение
        
        Args:
            tidal_current: (скорость, направление) приливного течения
            ocean_current: (скорость, направление) океанического течения
            wind_current: (скорость, направление) ветрового течения
            
        Returns:
            Кортеж (суммарная скорость, суммарное направление)
        """
        # Векторное сложение течений
        total_x = 0
        total_y = 0
        
        for speed, direction in [tidal_current, ocean_current, wind_current]:
            total_x += speed * math.sin(math.radians(direction))
            total_y += speed * math.cos(math.radians(direction))
        
        total_speed = math.sqrt(total_x**2 + total_y**2)
        total_direction = math.degrees(math.atan2(total_x, total_y)) % 360
        
        return (total_speed, total_direction)
    
    def calculate_search_radius(self, drift_time: float, 
                              position_error: float = 0.1,
                              drift_error: float = 0.3) -> float:
        """
        Рассчитать радиус поиска с учетом ошибок
        
        Args:
            drift_time: Время дрейфа (часы)
            position_error: Ошибка позиции (морские мили)
            drift_error: Ошибка дрейфа (процент)
            
        Returns:
            Радиус района поиска (морские мили)
        """
        # Формула из IAMSAR
        time_factor = math.sqrt(drift_time)
        error_radius = position_error + (drift_error * time_factor)
        
        # Добавляем запас 10%
        return error_radius * 1.1
    
    def calculate_expanding_square_search(self, datum: Dict, 
                                         track_spacing: float,
                                         first_leg_direction: float = 0) -> List[Tuple[float, float]]:
        """
        Рассчитать маршрут поиска расширяющимся квадратом
        
        Args:
            datum: Исходная точка
            track_spacing: Расстояние между галсами (морские мили)
            first_leg_direction: Направление первого галса (градусы)
            
        Returns:
            Список точек маршрута
        """
        waypoints = []
        current_pos = (datum['lat'], datum['lon'])
        waypoints.append(current_pos)
        
        # Стандартный паттерн расширяющегося квадрата
        legs = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7]
        direction = first_leg_direction
        
        for leg_number, leg_length in enumerate(legs):
            distance = track_spacing * leg_length
            new_pos = self.calculate_new_position(
                current_pos[0], current_pos[1], distance, direction
            )
            waypoints.append(new_pos)
            current_pos = new_pos
            
            # Поворот на 90 градусов вправо
            direction = (direction + 90) % 360
        
        return waypoints