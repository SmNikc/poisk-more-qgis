#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль для работы с интегрированными данными Поиск-Море
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Union  # ИСПРАВЛЕНО: добавлены типы

# Импорты QGIS делаем опциональными для тестирования вне QGIS
try:
    from PyQt5.QtCore import QSettings
    from qgis.core import (
        QgsProject, QgsVectorLayer, QgsRasterLayer,
        QgsDataSourceUri, QgsLayerTreeGroup,
        QgsMessageLog, Qgis, QgsStyle
    )
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False
    print("QGIS не доступен, работаем в ограниченном режиме")

import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataManager:
    """Менеджер для работы с данными плагина Поиск-Море"""
    
    def __init__(self, plugin_root: Union[str, Path]):  # ИСПРАВЛЕНО: Union вместо |
        """
        Инициализация менеджера данных
        
        Args:
            plugin_root: Путь к корневой папке плагина
        """
        self.root = Path(plugin_root)
        self.db_path = self.root / "db" / "incidents.db"
        self.data_shapes = self.root / "data" / "shapes"
        self.data_export = self.root / "data" / "export"
        self.styles_qml = self.root / "styles" / "qgis_converted"
        self.styles_lyr = self.root / "styles" / "lyr"
        self.manifest = self._load_manifest()
        self.conn = None
        
    def __enter__(self):
        """Контекстный менеджер для автоматического закрытия БД"""
        self.connect_incidents()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрытие соединения при выходе из контекста"""
        if self.conn:
            self.conn.close()

    def _load_manifest(self) -> Optional[Dict]:
        """Загрузка манифеста данных"""
        manifest_file = self.root / "DATA_MANIFEST.json"
        if manifest_file.exists():
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Ошибка загрузки манифеста: {e}")
        return None

    def connect_incidents(self) -> sqlite3.Connection:
        """Подключение к БД инцидентов"""
        if not self.db_path.exists():
            # Создаем БД если её нет
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._create_database()
            
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        return self.conn
    
    def _create_database(self):
        """Создание новой БД с базовой структурой"""
        logger.info(f"Создание новой БД: {self.db_path}")
        
        conn = sqlite3.connect(str(self.db_path))
        c = conn.cursor()
        
        # Создаем основную таблицу incidents
        c.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                coords_lat REAL,
                coords_lon REAL,
                datetime TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Создаем индексы
        c.execute("CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_incidents_datetime ON incidents(datetime)")
        
        conn.commit()
        conn.close()

    def load_default_layers(self) -> Dict[str, Optional[object]]:
        """Загрузка слоёв по умолчанию в QGIS проект"""
        loaded = {}
        
        if not QGIS_AVAILABLE:
            logger.warning("QGIS недоступен, пропускаем загрузку слоёв")
            return loaded
            
        gpkg_shapes = self.data_shapes / "poiskmore_shapes.gpkg"
        gpkg_export = self.data_export / "poiskmore_export.gpkg"

        # Загрузка из GeoPackage если есть
        if gpkg_shapes.exists():
            loaded["sarregion"] = self.load_layer_gpkg(gpkg_shapes, "sarregion", "SubRegions")
            loaded["sarrcc"] = self.load_layer_gpkg(gpkg_shapes, "sarrcc", "SarUnits")
            loaded["incidents"] = self.load_layer_gpkg(gpkg_shapes, "incidents", "Incidents")
        else:
            # Загрузка из shapefiles
            loaded["sarregion"] = self.load_layer_shp(
                self.data_shapes / "sarregion_m.shp", 
                "SAR Regions", 
                "SubRegions"
            )
            loaded["sarrcc"] = self.load_layer_shp(
                self.data_shapes / "sarrcc_m.shp",
                "MRCC/MRSC",
                "SarUnits"
            )

        # Загрузка инцидентов из БД
        if self.db_path.exists():
            loaded["incidents_db"] = self.load_layer_from_db()
            
        return loaded

    def load_layer_gpkg(self, gpkg: Path, layer_name: str, 
                       qml_hint: Optional[str] = None) -> Optional[object]:
        """
        Загрузка слоя из GeoPackage
        
        Args:
            gpkg: Путь к GeoPackage файлу
            layer_name: Имя слоя в GeoPackage
            qml_hint: Подсказка для поиска QML стиля
            
        Returns:
            QgsVectorLayer или None
        """
        if not QGIS_AVAILABLE:
            return None
            
        try:
            uri = QgsDataSourceUri()
            uri.setDatabase(str(gpkg))
            uri.setDataSource('', layer_name, 'geom')
            
            layer = QgsVectorLayer(uri.uri(), layer_name, "ogr")
            
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                
                # Применяем стиль если есть
                if qml_hint:
                    qml_file = self.styles_qml / f"{qml_hint}.qml"
                    if qml_file.exists():
                        layer.loadNamedStyle(str(qml_file))
                        
                logger.info(f"Слой загружен: {layer_name}")
                return layer
            else:
                logger.error(f"Невалидный слой: {layer_name}")
                
        except Exception as e:
            logger.error(f"Ошибка загрузки слоя {layer_name}: {e}")
            
        return None
    
    def load_layer_shp(self, shp_path: Path, display_name: str,
                      qml_hint: Optional[str] = None) -> Optional[object]:
        """
        Загрузка слоя из shapefile
        
        Args:
            shp_path: Путь к shapefile
            display_name: Отображаемое имя слоя
            qml_hint: Подсказка для поиска QML стиля
            
        Returns:
            QgsVectorLayer или None
        """
        if not QGIS_AVAILABLE:
            return None
            
        if not shp_path.exists():
            logger.warning(f"Shapefile не найден: {shp_path}")
            return None
            
        try:
            layer = QgsVectorLayer(str(shp_path), display_name, "ogr")
            
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                
                # Применяем стиль если есть
                if qml_hint:
                    qml_file = self.styles_qml / f"{qml_hint}.qml"
                    if qml_file.exists():
                        layer.loadNamedStyle(str(qml_file))
                        
                logger.info(f"Слой загружен: {display_name}")
                return layer
            else:
                logger.error(f"Невалидный слой: {display_name}")
                
        except Exception as e:
            logger.error(f"Ошибка загрузки слоя {display_name}: {e}")
            
        return None
    
    def load_layer_from_db(self) -> Optional[object]:
        """Загрузка слоя инцидентов из БД"""
        if not QGIS_AVAILABLE:
            return None
            
        try:
            uri = QgsDataSourceUri()
            uri.setDatabase(str(self.db_path))
            uri.setDataSource('', 'incidents', 'geometry')
            
            layer = QgsVectorLayer(uri.uri(), "Incidents (DB)", "spatialite")
            
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)
                logger.info("Слой инцидентов загружен из БД")
                return layer
            else:
                # Попробуем без геометрии
                uri.setGeometryColumn('')
                layer = QgsVectorLayer(uri.uri(), "Incidents (DB)", "spatialite")
                
                if layer.isValid():
                    QgsProject.instance().addMapLayer(layer)
                    logger.info("Слой инцидентов загружен из БД (без геометрии)")
                    return layer
                    
        except Exception as e:
            logger.error(f"Ошибка загрузки слоя из БД: {e}")
            
        return None
    
    def get_incidents(self, status: Optional[str] = None,
                     limit: int = 100) -> List[Dict]:
        """
        Получение списка инцидентов из БД
        
        Args:
            status: Фильтр по статусу (active, suspended, closed, archived)
            limit: Максимальное количество записей
            
        Returns:
            Список словарей с данными инцидентов
        """
        if not self.conn:
            self.connect_incidents()
            
        query = "SELECT * FROM incidents"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
            
        query += f" ORDER BY datetime DESC LIMIT {limit}"
        
        try:
            c = self.conn.cursor()
            c.execute(query, params)
            
            # Преобразуем в список словарей
            columns = [description[0] for description in c.description]
            incidents = []
            
            for row in c.fetchall():
                incident = dict(zip(columns, row))
                incidents.append(incident)
                
            return incidents
            
        except Exception as e:
            logger.error(f"Ошибка получения инцидентов: {e}")
            return []
    
    def add_incident(self, data: Dict) -> bool:
        """
        Добавление нового инцидента в БД
        
        Args:
            data: Словарь с данными инцидента
            
        Returns:
            True если успешно, False при ошибке
        """
        if not self.conn:
            self.connect_incidents()
            
        required_fields = ['case_number', 'name']
        
        # Проверка обязательных полей
        for field in required_fields:
            if field not in data:
                logger.error(f"Отсутствует обязательное поле: {field}")
                return False
                
        try:
            # Формируем запрос
            fields = list(data.keys())
            placeholders = ','.join(['?' for _ in fields])
            fields_str = ','.join(fields)
            
            query = f"INSERT INTO incidents ({fields_str}) VALUES ({placeholders})"
            values = [data[field] for field in fields]
            
            c = self.conn.cursor()
            c.execute(query, values)
            self.conn.commit()
            
            logger.info(f"Добавлен инцидент: {data.get('case_number')}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка добавления инцидента: {e}")
            self.conn.rollback()
            return False
    
    def update_incident(self, case_number: str, data: Dict) -> bool:
        """
        Обновление данных инцидента
        
        Args:
            case_number: Номер дела
            data: Словарь с обновляемыми полями
            
        Returns:
            True если успешно, False при ошибке
        """
        if not self.conn:
            self.connect_incidents()
            
        try:
            # Формируем запрос
            set_clause = ','.join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            values.append(case_number)
            
            query = f"UPDATE incidents SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE case_number = ?"
            
            c = self.conn.cursor()
            c.execute(query, values)
            self.conn.commit()
            
            if c.rowcount > 0:
                logger.info(f"Обновлен инцидент: {case_number}")
                return True
            else:
                logger.warning(f"Инцидент не найден: {case_number}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка обновления инцидента: {e}")
            self.conn.rollback()
            return False
    
    def get_statistics(self) -> Dict:
        """
        Получение статистики по инцидентам
        
        Returns:
            Словарь со статистикой
        """
        if not self.conn:
            self.connect_incidents()
            
        stats = {
            'total': 0,
            'active': 0,
            'suspended': 0,
            'closed': 0,
            'archived': 0
        }
        
        try:
            c = self.conn.cursor()
            
            # Общее количество
            c.execute("SELECT COUNT(*) FROM incidents")
            stats['total'] = c.fetchone()[0]
            
            # По статусам
            c.execute("""
                SELECT status, COUNT(*) 
                FROM incidents 
                GROUP BY status
            """)
            
            for row in c.fetchall():
                status, count = row
                if status in stats:
                    stats[status] = count
                    
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            
        return stats
    
    def close(self):
        """Закрытие соединения с БД"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Соединение с БД закрыто")

def test_data_manager():
    """Тестирование функций DataManager"""
    print("Тестирование DataManager...")
    
    # Создаем временную директорию для тестов
    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        manager = DataManager(tmp_dir)
        
        # Тест подключения к БД
        conn = manager.connect_incidents()
        assert conn is not None, "Ошибка подключения к БД"
        
        # Тест добавления инцидента
        test_incident = {
            'case_number': 'TEST-001',
            'name': 'Тестовый инцидент',
            'coords_lat': 55.7558,
            'coords_lon': 37.6173,
            'description': 'Тестовое описание'
        }
        
        success = manager.add_incident(test_incident)
        assert success, "Ошибка добавления инцидента"
        
        # Тест получения инцидентов
        incidents = manager.get_incidents()
        assert len(incidents) > 0, "Инциденты не найдены"
        assert incidents[0]['case_number'] == 'TEST-001'
        
        # Тест обновления
        success = manager.update_incident('TEST-001', {'status': 'closed'})
        assert success, "Ошибка обновления инцидента"
        
        # Тест статистики
        stats = manager.get_statistics()
        assert stats['total'] == 1
        assert stats['closed'] == 1
        
        manager.close()
        
    print("✅ Все тесты пройдены!")

if __name__ == "__main__":
    # Запуск тестов при прямом вызове
    test_data_manager()