# -*- coding: utf-8 -*-
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
