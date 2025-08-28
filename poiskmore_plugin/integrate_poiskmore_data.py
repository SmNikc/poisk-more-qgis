#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт интеграции данных из оригинального Поиск-Море (C#) 
в структуру разрабатываемого QGIS плагина (финальная версия)
"""

import os
import sys
import shutil
import subprocess
import json
import sqlite3  # ИСПРАВЛЕНО: добавлен импорт
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PoiskMoreDataIntegrator:
    def __init__(self, source_path=r"C:\INSTALLPOISKMORE",  # ИСПРАВЛЕНО: экранирование
                 plugin_path=r"C:\Projects\poisk-more-qgis\poiskmore_plugin"):  # ИСПРАВЛЕНО: экранирование
        self.source_path = Path(source_path)
        self.plugin_path = Path(plugin_path)
        self.log = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if not self.source_path.exists():
            logger.warning(f"Источник не найден: {self.source_path} - будут использованы существующие данные")
        if not self.plugin_path.exists():
            raise FileNotFoundError(f"Плагин не найден: {self.plugin_path}")
            
    def integrate_all(self):
        """Запуск полной интеграции данных"""
        logger.info("=" * 60)
        logger.info("Интеграция данных Поиск-Море в QGIS плагин v2.2.3")
        logger.info("=" * 60)
        
        # Создание резервной копии
        self.create_backup()
        
        # Интеграция базы данных
        self.integrate_database()
        
        # Интеграция shapefiles
        self.integrate_shapefiles()
        
        # Интеграция стилей
        self.integrate_styles()
        
        # Интеграция архивов
        self.integrate_archives()
        
        # Интеграция ресурсов
        self.integrate_resources()
        
        # Интеграция OilWater
        self.integrate_oilwater()
        
        # Создание манифеста
        self.create_data_manifest()
        
        # Сохранение лога
        self.save_integration_log()
        
        logger.info("✅ Интеграция завершена успешно!")
        
    def create_backup(self):
        """Создание резервной копии перед интеграцией"""
        backup_dir = self.plugin_path / f"backups/integration_{self.timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Копирование ключевых папок
        for dir_name in ['db', 'data', 'styles']:
            src = self.plugin_path / dir_name
            if src.exists():
                dst = backup_dir / dir_name
                shutil.copytree(src, dst, dirs_exist_ok=True)
                logger.info(f"Резервная копия создана: {dst}")
        
        self.log.append(f"Backup created: {backup_dir}")
        
    def integrate_database(self):
        """Интеграция базы данных"""
        logger.info("Интеграция базы данных...")
        db_dir = self.plugin_path / "db"
        db_dir.mkdir(exist_ok=True)
        
        # Проверяем наличие исходной БД
        source_db = self.source_path / "sardata.sqlite"
        target_db = db_dir / "incidents.db"
        
        if source_db.exists():
            # Копируем и объединяем с существующей
            temp_db = db_dir / "temp_import.db"
            shutil.copy2(source_db, temp_db)
            
            # Объединяем данные
            self.merge_databases(target_db, temp_db)
            temp_db.unlink()  # Удаляем временный файл
            
            logger.info(f"БД интегрирована: {target_db}")
            self.log.append(f"Database integrated: {source_db} -> {target_db}")
        else:
            # Если исходной БД нет, работаем с существующей
            if not target_db.exists():
                # Создаем новую БД
                conn = sqlite3.connect(target_db)
                conn.close()
                logger.info(f"Создана новая БД: {target_db}")
            else:
                logger.info(f"Используется существующая БД: {target_db}")
        
        # Парсинг дополнительных данных из XML/JSON
        self.parse_additional_data(target_db)
        
    def merge_databases(self, target_db: Path, source_db: Path):
        """Объединение двух БД с сохранением уникальных записей"""
        try:
            # Подключаемся к обеим БД
            target_conn = sqlite3.connect(target_db)
            source_conn = sqlite3.connect(source_db)
            
            target_cur = target_conn.cursor()
            source_cur = source_conn.cursor()
            
            # Получаем список таблиц из источника
            source_cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = source_cur.fetchall()
            
            for (table_name,) in tables:
                if table_name.startswith('sqlite_'):
                    continue
                    
                # Проверяем существование таблицы в целевой БД
                target_cur.execute(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table_name,))
                
                if target_cur.fetchone():
                    # Таблица существует - копируем только уникальные записи
                    source_cur.execute(f"SELECT * FROM {table_name}")
                    rows = source_cur.fetchall()
                    
                    if rows:
                        # Получаем список колонок
                        source_cur.execute(f"PRAGMA table_info({table_name})")
                        columns = [col[1] for col in source_cur.fetchall()]
                        
                        placeholders = ','.join(['?' for _ in columns])
                        insert_query = f"""
                            INSERT OR IGNORE INTO {table_name} 
                            ({','.join(columns)}) 
                            VALUES ({placeholders})
                        """
                        
                        target_cur.executemany(insert_query, rows)
                        logger.info(f"Импортировано записей в {table_name}: {len(rows)}")
                
            target_conn.commit()
            target_conn.close()
            source_conn.close()
            
        except Exception as e:
            logger.error(f"Ошибка объединения БД: {e}")
    
    def parse_additional_data(self, db_path: Path):
        """Парсинг дополнительных данных из C# файлов"""
        # Парсинг container.xml
        container_path = self.source_path / "container.xml"
        if container_path.exists():
            try:
                tree = ET.parse(container_path)
                root = tree.getroot()
                
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                
                # Создаем таблицу если её нет
                c.execute("""
                    CREATE TABLE IF NOT EXISTS container_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tag TEXT,
                        value TEXT,
                        parsed_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                for child in root:
                    c.execute("""
                        INSERT INTO container_data (tag, value)
                        VALUES (?, ?)
                    """, (child.tag, child.text))
                
                conn.commit()
                conn.close()
                logger.info("container.xml успешно импортирован")
                self.log.append("container.xml parsed")
            except Exception as e:
                logger.warning(f"Не удалось парсить container.xml: {e}")
        
    def integrate_shapefiles(self):
        """Интеграция shapefiles"""
        logger.info("Интеграция shapefiles...")
        shapes_dir = self.plugin_path / "data" / "shapes"
        shapes_dir.mkdir(parents=True, exist_ok=True)
        
        source_shapes = self.source_path / "Shapes"
        if source_shapes.exists():
            # Копируем все файлы shapes
            copied_count = 0
            for file in source_shapes.glob('*'):
                if file.is_file():
                    dst = shapes_dir / file.name
                    shutil.copy2(file, dst)
                    copied_count += 1
                    self.log.append(f"Shape copied: {file.name}")
            
            logger.info(f"Скопировано shapefiles: {copied_count} файлов")
            
            # Конвертация в GeoPackage
            self.convert_to_geopackage(shapes_dir)
        else:
            logger.info("Директория Shapes не найдена - пропускаем")
    
    def convert_to_geopackage(self, shapes_dir: Path):
        """Конвертация shapefiles в GeoPackage"""
        gpkg_file = shapes_dir / "poiskmore_shapes.gpkg"
        
        # Попытка использовать ogr2ogr
        try:
            shp_files = list(shapes_dir.glob("*.shp"))
            if shp_files:
                for i, shp in enumerate(shp_files):
                    layer_name = shp.stem
                    cmd = [
                        "ogr2ogr",
                        "-f", "GPKG",
                        "-nln", layer_name
                    ]
                    
                    # Для первого файла создаем новый GPKG, для остальных - добавляем
                    if i > 0:
                        cmd.append("-append")
                    
                    cmd.extend([str(gpkg_file), str(shp)])
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        logger.info(f"Конвертирован в GPKG: {layer_name}")
                        self.log.append(f"Converted to GPKG: {layer_name}")
                    else:
                        logger.warning(f"Ошибка конвертации {layer_name}: {result.stderr}")
                        
        except FileNotFoundError:
            logger.info("ogr2ogr не найден - используем shapefiles напрямую")
        except Exception as e:
            logger.warning(f"Ошибка при конвертации в GPKG: {e}")
    
    def integrate_styles(self):
        """Интеграция стилей слоёв"""
        logger.info("Интеграция стилей...")
        styles_dir = self.plugin_path / "styles"
        styles_dir.mkdir(exist_ok=True)
        
        # Создаем подпапки для разных форматов
        lyr_dir = styles_dir / "lyr"
        qml_dir = styles_dir / "qgis_converted"
        lyr_dir.mkdir(exist_ok=True)
        qml_dir.mkdir(exist_ok=True)
        
        # Копируем .lyr файлы
        source_styles = self.source_path / "Symbology"
        if source_styles.exists():
            copied_count = 0
            for lyr_file in source_styles.glob("*.lyr"):
                dst = lyr_dir / lyr_file.name
                shutil.copy2(lyr_file, dst)
                copied_count += 1
                self.log.append(f"Style copied: {lyr_file.name}")
                
                # Создаем placeholder QML файл
                qml_name = lyr_file.stem + ".qml"
                qml_path = qml_dir / qml_name
                self.create_placeholder_qml(qml_path, lyr_file.stem)
                
            logger.info(f"Скопировано стилей: {copied_count} файлов")
        else:
            logger.info("Директория Symbology не найдена - пропускаем")
    
    def create_placeholder_qml(self, qml_path: Path, layer_name: str):
        """Создание базового QML файла"""
        qml_content = f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.22.0">
  <renderer-v2 type="singleSymbol">
    <symbols>
      <symbol name="0" type="fill">
        <layer class="SimpleFill">
          <prop k="color" v="255,0,0,128"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_width" v="0.5"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <!-- Converted from {layer_name}.lyr -->
</qgis>"""
        
        with open(qml_path, 'w', encoding='utf-8') as f:
            f.write(qml_content)
    
    def integrate_archives(self):
        """Интеграция архивированных данных"""
        logger.info("Интеграция архивов...")
        archive_dir = self.plugin_path / "data" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Копируем архивы если есть
        source_archive = self.source_path / "Archive"
        if source_archive.exists():
            copied_count = 0
            for file in source_archive.glob("*"):
                if file.is_file():
                    dst = archive_dir / file.name
                    shutil.copy2(file, dst)
                    copied_count += 1
                    self.log.append(f"Archive copied: {file.name}")
                    
            logger.info(f"Скопировано архивов: {copied_count} файлов")
        else:
            logger.info("Директория Archive не найдена - пропускаем")
    
    def integrate_resources(self):
        """Интеграция ресурсов (иконки, изображения)"""
        logger.info("Интеграция ресурсов...")
        resources_dir = self.plugin_path / "resources"
        resources_dir.mkdir(exist_ok=True)
        
        # Копируем иконки
        source_icons = self.source_path / "Icons"
        if source_icons.exists():
            icons_dir = resources_dir / "icons"
            icons_dir.mkdir(exist_ok=True)
            
            copied_count = 0
            for file in source_icons.glob("*"):
                if file.suffix.lower() in ['.png', '.ico', '.svg', '.jpg', '.jpeg']:
                    dst = icons_dir / file.name
                    shutil.copy2(file, dst)
                    copied_count += 1
                    self.log.append(f"Icon copied: {file.name}")
                    
            logger.info(f"Скопировано иконок: {copied_count} файлов")
        else:
            logger.info("Директория Icons не найдена - пропускаем")
    
    def integrate_oilwater(self):
        """Интеграция данных OilWater"""
        logger.info("Интеграция OilWater...")
        oilwater_dir = self.plugin_path / "data" / "oilwater"
        oilwater_dir.mkdir(parents=True, exist_ok=True)
        
        source_oil = self.source_path / "OilWater"
        if source_oil.exists():
            # Парсим XML файлы с данными
            for xml_file in source_oil.glob("*.xml"):
                self.parse_oilwater_xml(xml_file, oilwater_dir)
                
            # Копируем остальные файлы
            copied_count = 0
            for file in source_oil.glob("*"):
                if file.is_file() and file.suffix != '.xml':
                    dst = oilwater_dir / file.name
                    shutil.copy2(file, dst)
                    copied_count += 1
                    self.log.append(f"OilWater file copied: {file.name}")
                    
            logger.info(f"OilWater: обработано XML и скопировано {copied_count} файлов")
        else:
            logger.info("Директория OilWater не найдена - пропускаем")
    
    def parse_oilwater_xml(self, xml_file: Path, output_dir: Path):
        """Парсинг OilWater XML файлов"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Конвертируем в JSON для удобства
            data = self.xml_to_dict(root)
            
            json_file = output_dir / f"{xml_file.stem}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.log.append(f"OilWater XML converted: {xml_file.name} -> {json_file.name}")
            
        except Exception as e:
            logger.warning(f"Ошибка парсинга {xml_file}: {e}")
    
    def xml_to_dict(self, element) -> Dict:
        """Рекурсивное преобразование XML в словарь"""
        result = {}
        
        # Атрибуты
        if element.attrib:
            result['@attributes'] = element.attrib
            
        # Текст
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
            
        # Дочерние элементы
        children = {}
        for child in element:
            child_data = self.xml_to_dict(child)
            if child.tag in children:
                if not isinstance(children[child.tag], list):
                    children[child.tag] = [children[child.tag]]
                children[child.tag].append(child_data)
            else:
                children[child.tag] = child_data
                
        if children:
            result.update(children)
            
        return result if result else element.text
    
    def create_data_manifest(self):
        """Создание манифеста интегрированных данных"""
        manifest = {
            "version": "2.2.3",
            "timestamp": self.timestamp,
            "source_path": str(self.source_path),
            "plugin_path": str(self.plugin_path),
            "integrated_components": [],
            "files_count": 0,
            "total_size_mb": 0
        }
        
        # Подсчет файлов и размера
        total_size = 0
        files_count = 0
        
        for root, dirs, files in os.walk(self.plugin_path):
            # Пропускаем директории backups
            if 'backups' in root:
                continue
                
            for file in files:
                file_path = Path(root) / file
                if file_path.exists():
                    files_count += 1
                    total_size += file_path.stat().st_size
        
        manifest["files_count"] = files_count
        manifest["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        
        # Компоненты
        components = []
        if (self.plugin_path / "db").exists():
            components.append("database")
        if (self.plugin_path / "data/shapes").exists():
            components.append("shapefiles")
        if (self.plugin_path / "styles").exists():
            components.append("styles")
        if (self.plugin_path / "data/oilwater").exists():
            components.append("oilwater")
        if (self.plugin_path / "resources/icons").exists():
            components.append("icons")
            
        manifest["integrated_components"] = components
        manifest["integration_log"] = self.log[-10:]  # Последние 10 записей лога
        
        # Сохранение манифеста
        manifest_file = self.plugin_path / "DATA_MANIFEST.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Манифест создан: {manifest_file}")
        
    def save_integration_log(self):
        """Сохранение лога интеграции"""
        log_dir = self.plugin_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"integration_{self.timestamp}.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Integration Log - {self.timestamp}\n")
            f.write("=" * 60 + "\n")
            for entry in self.log:
                f.write(f"{entry}\n")
                
        logger.info(f"Лог сохранен: {log_file}")

def main():
    """Главная функция"""
    # Парсинг аргументов командной строки
    source = r"C:\INSTALLPOISKMORE"
    plugin = r"C:\Projects\poisk-more-qgis\poiskmore_plugin"
    
    if len(sys.argv) > 1:
        source = sys.argv[1]
    if len(sys.argv) > 2:
        plugin = sys.argv[2]
        
    print("\n" + "=" * 60)
    print("🚀 ИНТЕГРАЦИЯ ДАННЫХ ПОИСК-МОРЕ")
    print("=" * 60)
    print(f"📂 Источник: {source}")
    print(f"📁 Плагин: {plugin}")
    print("-" * 60)
    
    try:
        integrator = PoiskMoreDataIntegrator(source, plugin)
        integrator.integrate_all()
        
        print("\n" + "=" * 60)
        print("✅ ИНТЕГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        
        manifest_file = Path(plugin) / "DATA_MANIFEST.json"
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
                
            print("\n📊 Интегрированные компоненты:")
            for comp in manifest.get("integrated_components", []):
                print(f"  ✓ {comp}")
                
            print(f"\n📈 Статистика:")
            print(f"  • Всего файлов: {manifest.get('files_count', 0)}")
            print(f"  • Общий размер: {manifest.get('total_size_mb', 0)} MB")
            
            print("\n📝 Последние операции:")
            for log_entry in manifest.get("integration_log", [])[-5:]:
                print(f"  • {log_entry}")
                
        print("\n💡 Следующие шаги:")
        print("  1. Проверьте структуру папок в плагине")
        print("  2. Запустите data_manager.py для проверки данных")
        print("  3. Откройте QGIS и загрузите плагин")
                
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ ОШИБКА: {e}")
        print("\n💡 Возможные решения:")
        print("  1. Проверьте пути к папкам")
        print("  2. Убедитесь что папка плагина существует")
        print("  3. Проверьте права доступа")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())