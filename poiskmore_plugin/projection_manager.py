#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль автоматической настройки проекций для плагина ПОИСК-МОРЕ
Добавить в папку плагина как projection_manager.py
"""

from qgis.core import (
    QgsProject, 
    QgsCoordinateReferenceSystem,
    QgsVectorLayer,
    QgsCoordinateTransform,
    QgsFeature
)
from qgis.PyQt.QtCore import QSettings
import os

class ProjectionManager:
    """Менеджер проекций для автоматической настройки"""
    
    # Стандартная проекция для морских карт
    DEFAULT_CRS = 'EPSG:4326'  # WGS 84
    
    # Custom Mercator для Балтийского региона
    BALTIC_MERCATOR_PROJ4 = '+proj=merc +lon_0=20 +lat_ts=60 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
    
    # Словарь известных слоев и их проекций
    LAYER_PROJECTIONS = {
        'sarrcc_m': 'EPSG:4326',
        'sarregion_m': 'EPSG:4326',
        'ThingPoints': 'custom_mercator',
        'SarUnits': 'custom_mercator',
        'Export_Output': 'EPSG:4326'
    }
    
    def __init__(self):
        """Инициализация менеджера проекций"""
        self.project = QgsProject.instance()
        self.custom_crs = None
        
    def setup_project_crs(self):
        """Настройка проекции проекта"""
        try:
            # Установить проекцию проекта
            project_crs = QgsCoordinateReferenceSystem(self.DEFAULT_CRS)
            self.project.setCrs(project_crs)
            
            # Включить преобразование "на лету"
            settings = QSettings()
            settings.setValue('/Projections/otfTransformAutoEnable', True)
            settings.setValue('/Projections/otfTransformEnabled', True)
            
            print(f"[ProjectionManager] Проекция проекта установлена: {self.DEFAULT_CRS}")
            return True
            
        except Exception as e:
            print(f"[ProjectionManager] Ошибка настройки проекции проекта: {e}")
            return False
    
    def create_custom_mercator(self):
        """Создание custom Mercator проекции для Балтийского региона"""
        try:
            self.custom_crs = QgsCoordinateReferenceSystem()
            self.custom_crs.createFromProj(self.BALTIC_MERCATOR_PROJ4)
            
            if self.custom_crs.isValid():
                print("[ProjectionManager] Custom Mercator проекция создана")
                return True
            else:
                print("[ProjectionManager] Ошибка создания Custom Mercator")
                return False
                
        except Exception as e:
            print(f"[ProjectionManager] Ошибка создания custom проекции: {e}")
            return False
    
    def fix_layer_projection(self, layer_name):
        """
        Исправление проекции для конкретного слоя
        
        Args:
            layer_name: имя слоя
        """
        try:
            # Найти слой
            layers = self.project.mapLayersByName(layer_name)
            if not layers:
                return False
                
            layer = layers[0]
            
            # Определить нужную проекцию
            if layer_name in self.LAYER_PROJECTIONS:
                projection_type = self.LAYER_PROJECTIONS[layer_name]
                
                if projection_type == 'custom_mercator':
                    # Создать custom проекцию если еще не создана
                    if not self.custom_crs:
                        self.create_custom_mercator()
                    
                    if self.custom_crs and self.custom_crs.isValid():
                        layer.setCrs(self.custom_crs)
                        print(f"[ProjectionManager] {layer_name}: установлена Custom Mercator")
                else:
                    # Стандартная проекция EPSG
                    crs = QgsCoordinateReferenceSystem(projection_type)
                    layer.setCrs(crs)
                    print(f"[ProjectionManager] {layer_name}: установлена {projection_type}")
            else:
                # Неизвестный слой - устанавливаем по умолчанию
                crs = QgsCoordinateReferenceSystem(self.DEFAULT_CRS)
                layer.setCrs(crs)
                print(f"[ProjectionManager] {layer_name}: установлена проекция по умолчанию")
                
            return True
            
        except Exception as e:
            print(f"[ProjectionManager] Ошибка настройки слоя {layer_name}: {e}")
            return False
    
    def fix_all_layers(self):
        """Исправить проекции для всех слоев в проекте"""
        fixed_count = 0
        
        for layer in self.project.mapLayers().values():
            if isinstance(layer, QgsVectorLayer):
                if self.fix_layer_projection(layer.name()):
                    fixed_count += 1
        
        print(f"[ProjectionManager] Исправлено слоев: {fixed_count}")
        return fixed_count > 0
    
    def setup_layer_symbology(self, layer_name, fill_opacity=0):
        """
        Настройка символики слоя (убрать заливку, оставить границы)
        
        Args:
            layer_name: имя слоя
            fill_opacity: прозрачность заливки (0 = без заливки)
        """
        try:
            layers = self.project.mapLayersByName(layer_name)
            if not layers:
                return False
                
            layer = layers[0]
            
            # Получить рендерер
            renderer = layer.renderer()
            if renderer:
                symbol = renderer.symbol()
                if symbol:
                    # Установить прозрачность заливки
                    symbol.setOpacity(fill_opacity)
                    
                    # Или полностью убрать заливку для полигонов
                    if layer.geometryType() == 2:  # Polygon
                        for i in range(symbol.symbolLayerCount()):
                            symbol_layer = symbol.symbolLayer(i)
                            if symbol_layer:
                                # Убрать заливку
                                symbol_layer.setFillColor(QColor(0, 0, 0, 0))
                                # Или установить стиль без заливки
                                symbol_layer.setBrushStyle(Qt.NoBrush)
                    
                    layer.triggerRepaint()
                    print(f"[ProjectionManager] {layer_name}: символика настроена")
                    return True
                    
        except Exception as e:
            print(f"[ProjectionManager] Ошибка настройки символики {layer_name}: {e}")
            
        return False
    
    def auto_setup(self):
        """
        Автоматическая полная настройка проекций и символики
        Вызывать при загрузке плагина
        """
        print("[ProjectionManager] Начинаю автоматическую настройку...")
        
        # 1. Настроить проекцию проекта
        self.setup_project_crs()
        
        # 2. Создать custom проекцию
        self.create_custom_mercator()
        
        # 3. Исправить все слои
        self.fix_all_layers()
        
        # 4. Настроить символику для известных слоев
        for layer_name in ['sarrcc_m', 'sarregion_m']:
            self.setup_layer_symbology(layer_name, fill_opacity=0)
        
        # 5. Обновить карту
        try:
            from qgis.utils import iface
            iface.mapCanvas().refresh()
        except:
            pass
        
        print("[ProjectionManager] Автоматическая настройка завершена")


# Функция для быстрого запуска (можно вызвать из плагина)
def auto_fix_projections():
    """Быстрая функция для исправления всех проекций"""
    manager = ProjectionManager()
    manager.auto_setup()
    return True
