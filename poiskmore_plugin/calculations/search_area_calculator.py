# -*- coding: utf-8 -*-
"""
Модуль расчета районов поиска
Реализует методы расчета согласно разделу 3 документации
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass 
class SearchArea:
    """Район поиска"""
    id: str
    name: str
    type: str  # Тип района (two_points, along_line, distant_areas, manual)
    bounds: List[Tuple[float, float]]  # Границы района [(lat, lon), ...]
    center: Tuple[float, float]  # Центр района
    area_nm2: float  # Площадь в квадратных морских милях
    sub_areas: List[Dict]  # Подрайоны для распределения SRU
    priority: int  # Приоритет поиска (1 - высший)


class SearchAreaCalculator:
    """Класс для расчета районов поиска"""
    
    # Стандартные параметры поиска
    DEFAULT_SEARCH_PARAMS = {
        'track_spacing': 0.5,  # Расстояние между галсами в милях
        'search_speed': 10,     # Скорость поиска в узлах
        'visibility': 3,        # Видимость в милях
        'coverage_factor': 1.0  # Коэффициент покрытия
    }
    
    def __init__(self):
        """Инициализация калькулятора"""
        self.search_areas = []
    
    def calculate_from_two_points(self,
                                 datum_left: Dict,
                                 datum_right: Dict,
                                 search_duration: float,
                                 params: Optional[Dict] = None) -> SearchArea:
        """
        Расчет района поиска от двух исходных пунктов
        Соответствует разделу 3.1 документации
        
        Args:
            datum_left: Левый исходный пункт с данными дрейфа
            datum_right: Правый исходный пункт с данными дрейфа
            search_duration: Продолжительность поиска в часах
            params: Параметры поиска
            
        Returns:
            Район поиска
        """
        params = params or self.DEFAULT_SEARCH_PARAMS
        
        # Получаем координаты исходных пунктов
        left_pos = (datum_left['lat'], datum_left['lon'])
        right_pos = (datum_right['lat'], datum_right['lon'])
        
        # Рассчитываем смещение за время поиска
        drift_distance = datum_left.get('drift_speed', 1.0) * search_duration
        
        # Строим прямоугольный район поиска
        # Ширина = расстояние между исходными пунктами + погрешности
        width_nm = self._calculate_distance(left_pos, right_pos) + drift_distance
        
        # Длина = дистанция дрейфа за время поиска
        length_nm = drift_distance * 2
        
        # Центр района
        center_lat = (left_pos[0] + right_pos[0]) / 2
        center_lon = (left_pos[1] + right_pos[1]) / 2
        
        # Направление дрейфа
        drift_direction = datum_left.get('drift_direction', 0)
        
        # Строим границы района
        bounds = self._create_rectangle_bounds(
            (center_lat, center_lon),
            width_nm,
            length_nm,
            drift_direction
        )
        
        # Площадь района
        area_nm2 = width_nm * length_nm
        
        # Создаем подрайоны для распределения SRU
        sub_areas = self._divide_into_sub_areas(bounds, params['track_spacing'])
        
        search_area = SearchArea(
            id=f"area_two_points_{len(self.search_areas)+1}",
            name="Поиск от двух исходных пунктов",
            type="two_points",
            bounds=bounds,
            center=(center_lat, center_lon),
            area_nm2=area_nm2,
            sub_areas=sub_areas,
            priority=1
        )
        
        self.search_areas.append(search_area)
        return search_area
    
    def calculate_along_line(self,
                           datum_line: List[Tuple[float, float]],
                           search_width: float,
                           params: Optional[Dict] = None) -> SearchArea:
        """
        Расчет района поиска вдоль исходной линии
        Соответствует разделу 3.5 документации
        
        Args:
            datum_line: Список точек исходной линии [(lat, lon), ...]
            search_width: Ширина полосы поиска в милях
            params: Параметры поиска
            
        Returns:
            Район поиска вдоль линии
        """
        params = params or self.DEFAULT_SEARCH_PARAMS
        
        # Рассчитываем длину линии
        total_length = 0
        for i in range(len(datum_line) - 1):
            total_length += self._calculate_distance(datum_line[i], datum_line[i+1])
        
        # Создаем буферную зону вокруг линии
        bounds = self._create_buffer_around_line(datum_line, search_width / 2)
        
        # Центр района - середина линии
        mid_index = len(datum_line) // 2
        center = datum_line[mid_index]
        
        # Площадь района
        area_nm2 = total_length * search_width
        
        # Создаем подрайоны вдоль линии
        sub_areas = self._divide_line_into_segments(datum_line, search_width, params['track_spacing'])
        
        search_area = SearchArea(
            id=f"area_along_line_{len(self.search_areas)+1}",
            name="Поиск вдоль исходной линии",
            type="along_line",
            bounds=bounds,
            center=center,
            area_nm2=area_nm2,
            sub_areas=sub_areas,
            priority=1
        )
        
        self.search_areas.append(search_area)
        return search_area
    
    def calculate_distant_areas(self,
                               datum_points: List[Dict],
                               max_distance: float,
                               search_duration: float,
                               params: Optional[Dict] = None) -> List[SearchArea]:
        """
        Расчет далеко разнесенных районов поиска
        Соответствует разделам 3.2 и 3.4 документации
        
        Args:
            datum_points: Список исходных пунктов
            max_distance: Максимальное расстояние между районами
            search_duration: Продолжительность поиска
            params: Параметры поиска
            
        Returns:
            Список районов поиска
        """
        params = params or self.DEFAULT_SEARCH_PARAMS
        areas = []
        
        # Группируем исходные пункты по расстоянию
        groups = self._group_points_by_distance(datum_points, max_distance)
        
        for i, group in enumerate(groups):
            # Для каждой группы создаем отдельный район
            if len(group) == 1:
                # Одиночный пункт - круговой район
                area = self._create_circular_area(
                    group[0],
                    search_duration,
                    params
                )
            else:
                # Несколько пунктов - полигональный район
                area = self._create_polygon_area(
                    group,
                    search_duration,
                    params
                )
            
            area.id = f"area_distant_{len(self.search_areas)+1}_{i+1}"
            area.name = f"Далеко разнесенный район {i+1}"
            area.priority = i + 1
            
            areas.append(area)
            self.search_areas.append(area)
        
        return areas
    
    def calculate_from_single_point(self,
                                   datum_point: Dict,
                                   search_radius: float,
                                   params: Optional[Dict] = None) -> SearchArea:
        """
        Расчет района поиска от одного исходного пункта
        
        Args:
            datum_point: Исходный пункт
            search_radius: Радиус поиска в милях
            params: Параметры поиска
            
        Returns:
            Район поиска
        """
        params = params or self.DEFAULT_SEARCH_PARAMS
        
        center = (datum_point['lat'], datum_point['lon'])
        
        # Создаем круговой район
        num_points = 36  # Точек для аппроксимации круга
        bounds = []
        for i in range(num_points):
            angle = (i * 360 / num_points)
            lat, lon = self._calculate_point_at_distance_and_bearing(
                center, search_radius, angle
            )
            bounds.append((lat, lon))
        
        # Площадь круга
        area_nm2 = math.pi * search_radius ** 2
        
        # Создаем концентрические подрайоны
        sub_areas = self._create_concentric_sub_areas(center, search_radius, params['track_spacing'])
        
        search_area = SearchArea(
            id=f"area_single_point_{len(self.search_areas)+1}",
            name="Поиск от одного исходного пункта",
            type="single_point",
            bounds=bounds,
            center=center,
            area_nm2=area_nm2,
            sub_areas=sub_areas,
            priority=1
        )
        
        self.search_areas.append(search_area)
        return search_area
    
    def calculate_manual_area(self,
                             user_bounds: List[Tuple[float, float]],
                             params: Optional[Dict] = None) -> SearchArea:
        """
        Создание района поиска вручную
        Соответствует разделу 3.6 документации
        
        Args:
            user_bounds: Границы района, заданные пользователем
            params: Параметры поиска
            
        Returns:
            Район поиска
        """
        params = params or self.DEFAULT_SEARCH_PARAMS
        
        # Вычисляем центр
        center = self._calculate_polygon_center(user_bounds)
        
        # Вычисляем площадь
        area_nm2 = self._calculate_polygon_area(user_bounds)
        
        # Создаем подрайоны
        sub_areas = self._divide_polygon_into_sub_areas(user_bounds, params['track_spacing'])
        
        search_area = SearchArea(
            id=f"area_manual_{len(self.search_areas)+1}",
            name="Район, определенный вручную",
            type="manual",
            bounds=user_bounds,
            center=center,
            area_nm2=area_nm2,
            sub_areas=sub_areas,
            priority=1
        )
        
        self.search_areas.append(search_area)
        return search_area
    
    def optimize_search_pattern(self,
                              search_area: SearchArea,
                              sru_units: List[Dict]) -> Dict:
        """
        Оптимизация схемы поиска для района
        
        Args:
            search_area: Район поиска
            sru_units: Список поисковых единиц (SRU)
            
        Returns:
            Оптимизированная схема поиска
        """
        total_sru_capacity = sum(sru['search_speed'] * sru['endurance'] 
                                for sru in sru_units)
        
        # Время для покрытия района
        coverage_time = search_area.area_nm2 / total_sru_capacity
        
        # Распределяем SRU по подрайонам
        assignments = []
        sub_area_index = 0
        
        for sru in sru_units:
            if sub_area_index < len(search_area.sub_areas):
                assignments.append({
                    'sru_id': sru['id'],
                    'sru_name': sru['name'],
                    'sub_area': search_area.sub_areas[sub_area_index],
                    'pattern': self._determine_search_pattern(
                        search_area.sub_areas[sub_area_index],
                        sru
                    )
                })
                sub_area_index += 1
        
        return {
            'area_id': search_area.id,
            'total_time_hours': coverage_time,
            'assignments': assignments,
            'coverage_probability': self._calculate_pod(search_area, sru_units)
        }
    
    def _calculate_distance(self, point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
        """
        Рассчитать расстояние между двумя точками в морских милях
        
        Args:
            point1: Первая точка (lat, lon)
            point2: Вторая точка (lat, lon)
            
        Returns:
            Расстояние в морских милях
        """
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        # Формула гаверсинуса
        R = 3440.065  # Радиус Земли в морских милях
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2)**2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def _calculate_point_at_distance_and_bearing(self,
                                                start_point: Tuple[float, float],
                                                distance_nm: float,
                                                bearing_deg: float) -> Tuple[float, float]:
        """
        Рассчитать точку на заданном расстоянии и азимуте
        
        Args:
            start_point: Начальная точка (lat, lon)
            distance_nm: Расстояние в морских милях
            bearing_deg: Азимут в градусах
            
        Returns:
            Новая точка (lat, lon)
        """
        lat1, lon1 = start_point
        R = 3440.065  # Радиус Земли в морских милях
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        bearing_rad = math.radians(bearing_deg)
        
        lat2_rad = math.asin(
            math.sin(lat1_rad) * math.cos(distance_nm/R) +
            math.cos(lat1_rad) * math.sin(distance_nm/R) * math.cos(bearing_rad)
        )
        
        lon2_rad = lon1_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(distance_nm/R) * math.cos(lat1_rad),
            math.cos(distance_nm/R) - math.sin(lat1_rad) * math.sin(lat2_rad)
        )
        
        lat2 = math.degrees(lat2_rad)
        lon2 = math.degrees(lon2_rad)
        
        return (lat2, lon2)
    
    def _create_rectangle_bounds(self,
                                center: Tuple[float, float],
                                width_nm: float,
                                length_nm: float,
                                orientation_deg: float) -> List[Tuple[float, float]]:
        """
        Создать границы прямоугольного района
        
        Args:
            center: Центр района
            width_nm: Ширина в милях
            length_nm: Длина в милях
            orientation_deg: Ориентация в градусах
            
        Returns:
            Список точек границ
        """
        half_width = width_nm / 2
        half_length = length_nm / 2
        
        # Углы прямоугольника относительно центра
        corners = [
            (-half_length, -half_width),
            (half_length, -half_width),
            (half_length, half_width),
            (-half_length, half_width)
        ]
        
        bounds = []
        for dx, dy in corners:
            # Расстояние и направление от центра
            distance = math.sqrt(dx**2 + dy**2)
            angle = math.degrees(math.atan2(dy, dx)) + orientation_deg
            
            lat, lon = self._calculate_point_at_distance_and_bearing(
                center, distance, angle
            )
            bounds.append((lat, lon))
        
        return bounds
    
    def _divide_into_sub_areas(self,
                              bounds: List[Tuple[float, float]],
                              track_spacing: float) -> List[Dict]:
        """
        Разделить район на подрайоны для SRU
        
        Args:
            bounds: Границы района
            track_spacing: Расстояние между галсами
            
        Returns:
            Список подрайонов
        """
        # Упрощенное деление на сетку
        # В реальности нужен более сложный алгоритм
        sub_areas = []
        
        # Определяем bbox
        lats = [p[0] for p in bounds]
        lons = [p[1] for p in bounds]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        # Размер подрайона (примерно)
        sub_size = track_spacing * 10  # 10 галсов на подрайон
        
        lat_steps = int((max_lat - min_lat) * 60 / sub_size) + 1
        lon_steps = int((max_lon - min_lon) * 60 / sub_size) + 1
        
        for i in range(lat_steps):
            for j in range(lon_steps):
                sub_lat_min = min_lat + (i * sub_size / 60)
                sub_lat_max = min_lat + ((i + 1) * sub_size / 60)
                sub_lon_min = min_lon + (j * sub_size / 60)
                sub_lon_max = min_lon + ((j + 1) * sub_size / 60)
                
                sub_areas.append({
                    'id': f"sub_{i}_{j}",
                    'bounds': [
                        (sub_lat_min, sub_lon_min),
                        (sub_lat_max, sub_lon_min),
                        (sub_lat_max, sub_lon_max),
                        (sub_lat_min, sub_lon_max)
                    ],
                    'center': ((sub_lat_min + sub_lat_max) / 2,
                              (sub_lon_min + sub_lon_max) / 2),
                    'area_nm2': sub_size ** 2
                })
        
        return sub_areas
    
    def _calculate_polygon_area(self, points: List[Tuple[float, float]]) -> float:
        """
        Рассчитать площадь полигона в квадратных морских милях
        
        Args:
            points: Список точек полигона
            
        Returns:
            Площадь в квадратных морских милях
        """
        # Используем формулу площади для сферического полигона
        # Упрощенная версия - проекция на плоскость
        if len(points) < 3:
            return 0
        
        # Центр полигона
        center = self._calculate_polygon_center(points)
        
        # Переводим в локальную проекцию относительно центра
        local_points = []
        for lat, lon in points:
            dx = (lon - center[1]) * 60 * math.cos(math.radians(center[0]))
            dy = (lat - center[0]) * 60
            local_points.append((dx, dy))
        
        # Формула площади полигона (формула шнурования)
        area = 0
        n = len(local_points)
        for i in range(n):
            j = (i + 1) % n
            area += local_points[i][0] * local_points[j][1]
            area -= local_points[j][0] * local_points[i][1]
        
        return abs(area) / 2
    
    def _calculate_polygon_center(self, points: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Рассчитать центр полигона
        
        Args:
            points: Список точек полигона
            
        Returns:
            Центр (lat, lon)
        """
        if not points:
            return (0, 0)
        
        lat_sum = sum(p[0] for p in points)
        lon_sum = sum(p[1] for p in points)
        
        return (lat_sum / len(points), lon_sum / len(points))
    
    def _determine_search_pattern(self, sub_area: Dict, sru: Dict) -> Dict:
        """
        Определить схему поиска для подрайона
        
        Args:
            sub_area: Подрайон
            sru: Поисковая единица
            
        Returns:
            Схема поиска
        """
        # Параллельные галсы - наиболее эффективная схема
        pattern = {
            'type': 'parallel',
            'track_spacing': self.DEFAULT_SEARCH_PARAMS['track_spacing'],
            'direction': 0,  # Будет оптимизировано
            'legs': []
        }
        
        # Рассчитываем галсы
        bounds = sub_area['bounds']
        width = self._calculate_distance(bounds[0], bounds[1])
        length = self._calculate_distance(bounds[1], bounds[2])
        
        # Направление галсов - вдоль длинной стороны
        if length > width:
            pattern['direction'] = 0
            num_tracks = int(width / pattern['track_spacing'])
        else:
            pattern['direction'] = 90
            num_tracks = int(length / pattern['track_spacing'])
        
        # Создаем галсы
        for i in range(num_tracks):
            pattern['legs'].append({
                'number': i + 1,
                'start': None,  # Будет рассчитано
                'end': None,    # Будет рассчитано
                'distance': length if length > width else width
            })
        
        return pattern
    
    def _calculate_pod(self, search_area: SearchArea, sru_units: List[Dict]) -> float:
        """
        Рассчитать вероятность обнаружения (POD)
        
        Args:
            search_area: Район поиска
            sru_units: Список SRU
            
        Returns:
            Вероятность обнаружения (0-1)
        """
        # Упрощенная формула POD
        # POD = 1 - exp(-W*V*t/A)
        # W - ширина полосы обзора
        # V - скорость поиска
        # t - время поиска
        # A - площадь района
        
        total_coverage = 0
        for sru in sru_units:
            sweep_width = sru.get('sweep_width', 2.0)  # мили
            speed = sru.get('search_speed', 10)  # узлы
            time = sru.get('endurance', 4)  # часы
            
            coverage = sweep_width * speed * time
            total_coverage += coverage
        
        coverage_factor = total_coverage / search_area.area_nm2
        
        # Вероятность обнаружения
        pod = 1 - math.exp(-coverage_factor)
        
        return min(pod, 0.99)  # Максимум 99%
    
    def _create_buffer_around_line(self,
                                  line: List[Tuple[float, float]],
                                  buffer_distance: float) -> List[Tuple[float, float]]:
        """
        Создать буферную зону вокруг линии
        
        Args:
            line: Линия
            buffer_distance: Расстояние буфера в милях
            
        Returns:
            Границы буферной зоны
        """
        # Создаем точки с обеих сторон линии
        left_side = []
        right_side = []
        
        for i in range(len(line) - 1):
            # Направление сегмента
            lat1, lon1 = line[i]
            lat2, lon2 = line[i + 1]
            
            # Азимут сегмента
            bearing = math.degrees(math.atan2(lon2 - lon1, lat2 - lat1))
            
            # Перпендикулярные направления
            left_bearing = (bearing - 90) % 360
            right_bearing = (bearing + 90) % 360
            
            # Точки слева
            left_point = self._calculate_point_at_distance_and_bearing(
                line[i], buffer_distance, left_bearing
            )
            left_side.append(left_point)
            
            # Точки справа
            right_point = self._calculate_point_at_distance_and_bearing(
                line[i], buffer_distance, right_bearing
            )
            right_side.append(right_point)
        
        # Добавляем последнюю точку
        bearing = math.degrees(math.atan2(
            line[-1][1] - line[-2][1],
            line[-1][0] - line[-2][0]
        ))
        
        left_side.append(self._calculate_point_at_distance_and_bearing(
            line[-1], buffer_distance, (bearing - 90) % 360
        ))
        
        right_side.append(self._calculate_point_at_distance_and_bearing(
            line[-1], buffer_distance, (bearing + 90) % 360
        ))
        
        # Объединяем в полигон
        return left_side + right_side[::-1]
    
    def _group_points_by_distance(self,
                                 points: List[Dict],
                                 max_distance: float) -> List[List[Dict]]:
        """
        Группировать точки по расстоянию
        
        Args:
            points: Список точек
            max_distance: Максимальное расстояние для группировки
            
        Returns:
            Список групп точек
        """
        if not points:
            return []
        
        groups = []
        used = set()
        
        for i, point in enumerate(points):
            if i in used:
                continue
            
            group = [point]
            used.add(i)
            
            for j, other_point in enumerate(points):
                if j in used:
                    continue
                
                # Проверяем расстояние до всех точек в группе
                in_group = True
                for group_point in group:
                    dist = self._calculate_distance(
                        (group_point['lat'], group_point['lon']),
                        (other_point['lat'], other_point['lon'])
                    )
                    if dist > max_distance:
                        in_group = False
                        break
                
                if in_group:
                    group.append(other_point)
                    used.add(j)
            
            groups.append(group)
        
        return groups
    
    def _create_circular_area(self,
                            datum_point: Dict,
                            search_duration: float,
                            params: Dict) -> SearchArea:
        """Создать круговой район поиска"""
        return self.calculate_from_single_point(
            datum_point,
            datum_point.get('drift_speed', 1.0) * search_duration * 1.5,
            params
        )
    
    def _create_polygon_area(self,
                           datum_points: List[Dict],
                           search_duration: float,
                           params: Dict) -> SearchArea:
        """Создать полигональный район поиска"""
        # Находим выпуклую оболочку точек
        points = [(p['lat'], p['lon']) for p in datum_points]
        
        # Расширяем на величину дрейфа
        expansion = max(p.get('drift_speed', 1.0) for p in datum_points) * search_duration
        
        # Центр
        center = self._calculate_polygon_center(points)
        
        # Расширенные границы
        expanded_bounds = []
        for lat, lon in points:
            # Направление от центра
            bearing = math.degrees(math.atan2(lon - center[1], lat - center[0]))
            # Новая точка
            new_point = self._calculate_point_at_distance_and_bearing(
                (lat, lon), expansion, bearing
            )
            expanded_bounds.append(new_point)
        
        area_nm2 = self._calculate_polygon_area(expanded_bounds)
        sub_areas = self._divide_polygon_into_sub_areas(expanded_bounds, params['track_spacing'])
        
        return SearchArea(
            id="temp",
            name="temp",
            type="polygon",
            bounds=expanded_bounds,
            center=center,
            area_nm2=area_nm2,
            sub_areas=sub_areas,
            priority=1
        )
    
    def _divide_line_into_segments(self,
                                  line: List[Tuple[float, float]],
                                  width: float,
                                  spacing: float) -> List[Dict]:
        """Разделить линию на сегменты для поиска"""
        segments = []
        segment_length = spacing * 10  # 10 галсов на сегмент
        
        total_length = 0
        for i in range(len(line) - 1):
            total_length += self._calculate_distance(line[i], line[i+1])
        
        num_segments = int(total_length / segment_length) + 1
        
        for i in range(num_segments):
            start_dist = i * segment_length
            end_dist = min((i + 1) * segment_length, total_length)
            
            segments.append({
                'id': f"segment_{i}",
                'start_distance': start_dist,
                'end_distance': end_dist,
                'width': width,
                'area_nm2': (end_dist - start_dist) * width
            })
        
        return segments
    
    def _create_concentric_sub_areas(self,
                                    center: Tuple[float, float],
                                    radius: float,
                                    spacing: float) -> List[Dict]:
        """Создать концентрические подрайоны"""
        sub_areas = []
        num_rings = int(radius / (spacing * 5)) + 1
        
        for i in range(num_rings):
            inner_radius = i * spacing * 5
            outer_radius = min((i + 1) * spacing * 5, radius)
            
            sub_areas.append({
                'id': f"ring_{i}",
                'type': 'ring',
                'inner_radius': inner_radius,
                'outer_radius': outer_radius,
                'center': center,
                'area_nm2': math.pi * (outer_radius**2 - inner_radius**2)
            })
        
        return sub_areas
    
    def _divide_polygon_into_sub_areas(self,
                                      bounds: List[Tuple[float, float]],
                                      spacing: float) -> List[Dict]:
        """Разделить полигон на подрайоны"""
        # Используем упрощенный метод деления на сетку
        return self._divide_into_sub_areas(bounds, spacing)