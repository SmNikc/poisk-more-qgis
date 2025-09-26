# -*- coding: utf-8 -*-
"""
utils/marine_maps_loader.py

ИНТЕГРАТОР МОРСКИХ КАРТ ДЛЯ ПЛАГИНА "ПОИСК-МОРЕ"
Автоматическая загрузка морских карт при старте плагина

РЕАЛИЗУЮ: Автозагрузка морских карт 
СООТВЕТСТВУЕТ: Восстановление функций из старого плагина v1.1.0_WEATHER_FIXED
ТОЧНЫЕ НАЗВАНИЯ:
- OpenSeaMap (два слоя)
- Ocean Base Map ESRI
- Позиционирование на Россию при старте
"""

import os
from typing import Optional, List
from qgis.PyQt.QtCore import QSettings
from qgis.core import (
    QgsProject, QgsRasterLayer, QgsVectorLayer, QgsLayerTreeGroup,
    QgsApplication, QgsCoordinateReferenceSystem, QgsRectangle, 
    Qgis, QgsMessageLog
)
from qgis.gui import QgisInterface


class MarineMapsLoader:
    """
    Загрузчик морских карт для плагина Поиск-Море
    
    Функции:
    - Автозагрузка OpenSeaMap и Ocean Base Map при старте
    - Создание групп слоев
    - Позиционирование на территорию России
    - Сохранение настроек пользователя
    """
    
    # Константы карт из старого плагина
    ESRI_OCEAN_XYZ = "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"
    OSM_XYZ = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    SEAMARKS_XYZ = "https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"
    
    # Названия слоев
    GROUP_BASEMAP = "Картографическая основа"
    GROUP_THEMATIC = "Тематические слои ПОИСК-МОРЕ"
    
    LAYER_ESRI = "Ocean Base Map (ESRI)"
    LAYER_OSM = "OpenStreetMap"
    LAYER_SEAMARKS = "OpenSeaMap Seamarks"
    
    # Границы России для позиционирования
    RUSSIA_EXTENT = QgsRectangle(19.0, 41.0, 180.0, 82.0)  # Приблизительные границы
    
    def __init__(self, iface: QgisInterface, plugin_dir: str):
        """
        Инициализация загрузчика морских карт
        
        Args:
            iface: Интерфейс QGIS
            plugin_dir: Путь к директории плагина
        """
        self.iface = iface
        self.plugin_dir = plugin_dir
        self.project = QgsProject.instance()
        self.settings = QSettings("PoiskMore", "MarineMaps")
        
        # Состояние загрузки
        self.maps_loaded = False
        self.sidebar_created = False
    
    def load_marine_maps_on_startup(self):
        """
        ОСНОВНАЯ ФУНКЦИЯ: Загрузка морских карт при старте плагина
        
        Выполняет:
        1. Создание групп слоев
        2. Загрузка базовых карт (Ocean Base Map ESRI, OpenStreetMap)
        3. Загрузка OpenSeaMap Seamarks
        4. Позиционирование на Россию
        5. Создание боковой панели управления
        """
        try:
            self._log_info("Начинается загрузка морских карт...")
            
            # 1. Создаем группы слоев
            self._ensure_layer_groups()
            
            # 2. Загружаем базовые карты
            self._load_base_maps()
            
            # 3. Загружаем OpenSeaMap Seamarks
            self._load_seamarks()
            
            # 4. Устанавливаем масштаб на Россию
            self._zoom_to_russia()
            
            # 5. Создаем боковую панель (если доступна)
            self._try_create_sidebar()
            
            self.maps_loaded = True
            self._log_info("Морские карты успешно загружены")
            
            # Уведомляем пользователя
            self.iface.messageBar().pushMessage(
                "ПОИСК-МОРЕ",
                "Морские карты загружены: Ocean Base Map, OpenSeaMap",
                level=Qgis.Info,
                duration=3
            )
            
        except Exception as e:
            self._log_error(f"Ошибка загрузки морских карт: {str(e)}")
            # Не блокируем запуск плагина из-за ошибок карт
    
    def _ensure_layer_groups(self):
        """Создание групп слоев если они не существуют."""
        root = self.project.layerTreeRoot()
        
        # Группа для базовых карт
        if not root.findGroup(self.GROUP_BASEMAP):
            basemap_group = root.insertGroup(0, self.GROUP_BASEMAP)
            self._log_info(f"Создана группа: {self.GROUP_BASEMAP}")
        
        # Группа для тематических слоев
        if not root.findGroup(self.GROUP_THEMATIC):
            thematic_group = root.insertGroup(1, self.GROUP_THEMATIC)
            self._log_info(f"Создана группа: {self.GROUP_THEMATIC}")
    
    def _load_base_maps(self):
        """Загрузка базовых карт."""
        root = self.project.layerTreeRoot()
        basemap_group = root.findGroup(self.GROUP_BASEMAP)
        
        # Ocean Base Map ESRI
        if not self._find_layer_by_name(self.LAYER_ESRI):
            esri_layer = self._create_xyz_layer(
                self.LAYER_ESRI, 
                self.ESRI_OCEAN_XYZ,
                "Морская карта ESRI с батиметрией"
            )
            if esri_layer and esri_layer.isValid():
                self.project.addMapLayer(esri_layer, False)
                if basemap_group:
                    basemap_group.insertLayer(0, esri_layer)
                self._log_info(f"Загружен слой: {self.LAYER_ESRI}")
            else:
                self._log_error(f"Не удалось создать слой: {self.LAYER_ESRI}")
        
        # OpenStreetMap (как альтернатива)
        if not self._find_layer_by_name(self.LAYER_OSM):
            osm_layer = self._create_xyz_layer(
                self.LAYER_OSM,
                self.OSM_XYZ,
                "Базовая карта OpenStreetMap"
            )
            if osm_layer and osm_layer.isValid():
                self.project.addMapLayer(osm_layer, False)
                if basemap_group:
                    basemap_group.insertLayer(1, osm_layer)
                # По умолчанию выключаем OSM, оставляем активным ESRI
                osm_layer.setIsVisible(False)
                self._log_info(f"Загружен слой: {self.LAYER_OSM}")
    
    def _load_seamarks(self):
        """Загрузка OpenSeaMap Seamarks (навигационные знаки)."""
        if not self._find_layer_by_name(self.LAYER_SEAMARKS):
            seamarks_layer = self._create_xyz_layer(
                self.LAYER_SEAMARKS,
                self.SEAMARKS_XYZ,
                "Навигационные знаки OpenSeaMap"
            )
            if seamarks_layer and seamarks_layer.isValid():
                self.project.addMapLayer(seamarks_layer, False)
                
                # Добавляем в группу базовых карт как overlay
                root = self.project.layerTreeRoot()
                basemap_group = root.findGroup(self.GROUP_BASEMAP)
                if basemap_group:
                    basemap_group.insertLayer(0, seamarks_layer)
                
                # Устанавливаем прозрачность по умолчанию
                seamarks_layer.setOpacity(0.8)
                self._log_info(f"Загружен слой: {self.LAYER_SEAMARKS}")
            else:
                self._log_error(f"Не удалось создать слой: {self.LAYER_SEAMARKS}")
                # Попробуем альтернативный URL OpenSeaMap
                self._try_alternative_seamarks()
    
    def _try_alternative_seamarks(self):
        """Попытка загрузки OpenSeaMap с альтернативного сервера."""
        try:
            alt_url = "https://t1.openseamap.org/seamark/{z}/{x}/{y}.png"
            alt_layer = self._create_xyz_layer(
                f"{self.LAYER_SEAMARKS} (Alt)",
                alt_url,
                "Навигационные знаки OpenSeaMap (альтернативный сервер)"
            )
            if alt_layer and alt_layer.isValid():
                self.project.addMapLayer(alt_layer, False)
                root = self.project.layerTreeRoot()
                basemap_group = root.findGroup(self.GROUP_BASEMAP)
                if basemap_group:
                    basemap_group.insertLayer(0, alt_layer)
                alt_layer.setOpacity(0.8)
                self._log_info("Загружен альтернативный OpenSeaMap")
        except Exception as e:
            self._log_error(f"Альтернативный OpenSeaMap также недоступен: {str(e)}")
    
    def _create_xyz_layer(self, name: str, url: str, description: str = "") -> Optional[QgsRasterLayer]:
        """
        Создание XYZ слоя
        
        Args:
            name: Название слоя
            url: URL шаблон
            description: Описание слоя
            
        Returns:
            QgsRasterLayer или None при ошибке
        """
        try:
            # Формируем строку подключения для XYZ
            connection_string = f"type=xyz&url={url}&zmax=19&zmin=0"
            
            layer = QgsRasterLayer(connection_string, name, "wms")
            
            if layer.isValid():
                # Устанавливаем CRS
                crs = QgsCoordinateReferenceSystem("EPSG:3857")  # Web Mercator
                layer.setCrs(crs)
                
                # Устанавливаем описание
                if description:
                    layer.setAbstract(description)
                
                return layer
            else:
                self._log_error(f"Слой {name} недействителен: {layer.error().message()}")
                return None
                
        except Exception as e:
            self._log_error(f"Ошибка создания слоя {name}: {str(e)}")
            return None
    
    def _zoom_to_russia(self):
        """Позиционирование карты на территорию России."""
        try:
            # Устанавливаем CRS карты
            canvas = self.iface.mapCanvas()
            
            # Устанавливаем экстент на Россию
            canvas.setExtent(self.RUSSIA_EXTENT)
            canvas.refresh()
            
            self._log_info("Карта позиционирована на территорию России")
            
        except Exception as e:
            self._log_error(f"Ошибка позиционирования на Россию: {str(e)}")
    
    def _try_create_sidebar(self):
        """Попытка создания боковой панели управления картами."""
        try:
            # Импортируем боковую панель если доступна
            from ..ui.pm_sidebar_dock import PoiskMoreSidebarDock, ensure_pm_sidebar_dock
            
            sidebar = ensure_pm_sidebar_dock(self.iface, self.plugin_dir)
            if sidebar:
                self.sidebar_created = True
                self._log_info("Боковая панель управления картами создана")
                
        except ImportError:
            self._log_info("Боковая панель недоступна (файл pm_sidebar_dock не найден)")
        except Exception as e:
            self._log_error(f"Ошибка создания боковой панели: {str(e)}")
    
    def _find_layer_by_name(self, name: str) -> Optional[QgsRasterLayer]:
        """Поиск слоя по имени."""
        layers = self.project.mapLayersByName(name)
        return layers[0] if layers else None
    
    def cleanup_on_unload(self):
        """Очистка ресурсов при выгрузке плагина."""
        try:
            # Сохраняем настройки
            self.settings.setValue("maps_loaded", self.maps_loaded)
            self.settings.setValue("sidebar_created", self.sidebar_created)
            
            self._log_info("Настройки морских карт сохранены")
            
        except Exception as e:
            self._log_error(f"Ошибка сохранения настроек: {str(e)}")
    
    def _log_info(self, message: str):
        """Логирование информации."""
        QgsMessageLog.logMessage(message, "Поиск-Море", Qgis.Info)
    
    def _log_error(self, message: str):
        """Логирование ошибок."""
        QgsMessageLog.logMessage(message, "Поиск-Море", Qgis.Critical)


def load_marine_maps_for_plugin(iface: QgisInterface, plugin_dir: str) -> MarineMapsLoader:
    """
    Функция-фасад для загрузки морских карт в плагине
    
    Args:
        iface: Интерфейс QGIS
        plugin_dir: Путь к директории плагина
        
    Returns:
        MarineMapsLoader: Экземпляр загрузчика карт
    """
    loader = MarineMapsLoader(iface, plugin_dir)
    loader.load_marine_maps_on_startup()
    return loader
