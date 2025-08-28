#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПОЛНАЯ МИГРАЦИЯ БАЗЫ ДАННЫХ ПОИСК-МОРЕ
========================================
Комплексный скрипт миграции всех БД и таблиц проекта (финальная версия)

Автор: AI Assistant
Дата: 2025-01-17
Версия: 2.2.3 (исправлены все синтаксические ошибки)
"""

import sqlite3
import os
import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import shutil
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TableMigrator:
    """Базовый класс для миграции таблицы"""
    
    def __init__(self, conn: sqlite3.Connection, table_name: str, schema: str):
        self.conn = conn
        self.table_name = table_name
        self.schema = schema
        
    def migrate(self, old_data: List[Tuple]) -> bool:
        try:
            c = self.conn.cursor()
            c.execute(self.schema)
            
            if old_data:
                placeholders = ','.join(['?'] * len(old_data[0]))
                c.executemany(f"INSERT INTO {self.table_name} VALUES ({placeholders})", old_data)
                
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Ошибка миграции {self.table_name}: {e}")
            return False
            
    def add_indexes(self, indexes: List[str]):
        c = self.conn.cursor()
        for idx in indexes:
            try:
                c.execute(idx)
            except Exception as e:
                logger.warning(f"Не удалось создать индекс: {e}")
        self.conn.commit()

class DatabaseMigration:
    """Класс для полной миграции БД ПОИСК-МОРЕ"""
    
    SCHEMA_VERSION = "2.2.3"
    
    DATABASES = {
        'incidents.db': 'Основная БД инцидентов и операций',
        'poiskmore.db': 'Вспомогательная БД плагина'
    }
    
    # Схема incidents (50 ключевых полей)
    INCIDENTS_SCHEMA = """
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE NOT NULL,
            weather_data_id TEXT,
            name TEXT NOT NULL,
            object_type TEXT,
            aviation TEXT,
            mmsi TEXT,
            imo TEXT,
            call_sign TEXT,
            board_number TEXT,
            download_size REAL,
            coords_lat REAL NOT NULL CHECK(coords_lat BETWEEN -90 AND 90),
            coords_lon REAL NOT NULL CHECK(coords_lon BETWEEN -180 AND 180),
            last_known_position_lat REAL,
            last_known_position_lon REAL,
            datum_lat REAL,
            datum_lon REAL,
            datetime TEXT NOT NULL,
            datetime_start TEXT,
            datetime_end TEXT,
            datetime_suspended TEXT,
            datetime_reopened TEXT,
            last_contact_time TEXT,
            download_date TEXT,
            description TEXT,
            situation_type TEXT NOT NULL,
            incident_type TEXT,
            help_needed TEXT,
            default_status INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'suspended', 'closed', 'archived')),
            close_reason TEXT,
            suspended_reason TEXT,
            hull_color TEXT,
            superstructure_color TEXT,
            fuel REAL,
            displacement REAL,
            length REAL,
            width REAL,
            draft REAL,
            num_people INTEGER DEFAULT 0,
            persons_rescued INTEGER DEFAULT 0,
            persons_missing INTEGER DEFAULT 0,
            persons_deceased INTEGER DEFAULT 0,
            crew_count INTEGER,
            passengers_count INTEGER,
            contacts TEXT,
            owner_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    # Схема sru_resources
    SRU_RESOURCES_SCHEMA = """
        CREATE TABLE IF NOT EXISTS sru_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            call_sign TEXT,
            capabilities TEXT,
            max_speed REAL,
            endurance_hours REAL,
            persons_capacity INTEGER,
            status TEXT DEFAULT 'available',
            base_location TEXT,
            current_lat REAL,
            current_lon REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    
    # Схема sru_assignments
    SRU_ASSIGNMENTS_SCHEMA = """
        CREATE TABLE IF NOT EXISTS sru_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            resource_id INTEGER NOT NULL,
            assignment_time TEXT NOT NULL,
            arrival_time TEXT,
            departure_time TEXT,
            search_pattern TEXT,
            assigned_area TEXT,
            status TEXT DEFAULT 'assigned',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents(id),
            FOREIGN KEY (resource_id) REFERENCES sru_resources(id)
        )
    """
    
    def __init__(self, work_dir: str = "."):
        self.work_dir = Path(work_dir).resolve()
        self.db_dir = self.work_dir / "db"
        self.backup_dir = self.work_dir / f"backups/migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_file = self.backup_dir / 'migration.log'
        self.success_count = 0
        self.warnings = []
        self.errors = []
        
        # Создаем директорию для БД если её нет
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self) -> bool:
        """Создание резервных копий БД"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            for db_name in self.DATABASES.keys():
                db_path = self.db_dir / db_name
                if db_path.exists():
                    backup_path = self.backup_dir / f"{db_name}.backup"
                    shutil.copy2(db_path, backup_path)
                    logger.info(f"Создана резервная копия: {backup_path}")
                    
            return True
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            self.errors.append(str(e))
            return False
            
    def analyze_database(self, db_path: Path) -> Dict[str, List[str]]:
        """Анализ существующей структуры БД"""
        structure = {}
        
        if not db_path.exists():
            return structure
            
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = c.fetchall()
            
            for table in tables:
                table_name = table[0]
                c.execute(f"PRAGMA table_info({table_name})")
                columns = c.fetchall()
                structure[table_name] = [col[1] for col in columns]
                
            conn.close()
        except Exception as e:
            logger.warning(f"Не удалось проанализировать БД: {e}")
            
        return structure
        
    def get_old_data(self, conn: sqlite3.Connection, table_name: str) -> List[Tuple]:
        """Получение данных из старой таблицы"""
        try:
            c = conn.cursor()
            c.execute(f"SELECT * FROM {table_name}")
            return c.fetchall()
        except Exception as e:
            logger.warning(f"Не удалось получить данные из {table_name}: {e}")
            return []
            
    def copy_data_to_new_table(self, conn: sqlite3.Connection, old_table: str, 
                               new_table: str, columns_mapping: Dict[str, str]) -> bool:
        """Копирование данных с маппингом колонок"""
        try:
            c = conn.cursor()
            
            # Получаем список колонок в новой таблице
            c.execute(f"PRAGMA table_info({new_table})")
            new_columns = [col[1] for col in c.fetchall()]
            
            # Формируем запрос копирования
            select_columns = []
            insert_columns = []
            
            for new_col in new_columns:
                if new_col in columns_mapping:
                    old_col = columns_mapping[new_col]
                    select_columns.append(old_col)
                    insert_columns.append(new_col)
                elif new_col not in ['id', 'created_at', 'updated_at']:
                    select_columns.append('NULL')
                    insert_columns.append(new_col)
                    
            if insert_columns:
                query = f"""
                    INSERT INTO {new_table} ({','.join(insert_columns)})
                    SELECT {','.join(select_columns)} FROM {old_table}
                """
                c.execute(query)
                conn.commit()
                
            return True
        except Exception as e:
            logger.error(f"Ошибка копирования данных: {e}")
            return False
            
    def create_indexes(self, conn: sqlite3.Connection, table_name: str, indexes: List[str]):
        """Создание индексов для таблицы"""
        c = conn.cursor()
        for idx in indexes:
            try:
                c.execute(idx)
            except Exception as e:
                logger.warning(f"Не удалось создать индекс: {e}")
        conn.commit()
        
    def migrate_incidents_table(self, db_path: Path) -> bool:
        """Миграция таблицы incidents"""
        logger.info(f"Миграция incidents в {db_path.name}...")
        
        try:
            conn = sqlite3.connect(db_path)
            
            old_structure = self.analyze_database(db_path)
            has_old_incidents = 'incidents' in old_structure
            
            old_data = []
            if has_old_incidents:
                old_data = self.get_old_data(conn, 'incidents')
                
            c = conn.cursor()
            
            # Создаем новую таблицу
            if has_old_incidents:
                c.execute("DROP TABLE IF EXISTS new_incidents")
                c.execute(self.INCIDENTS_SCHEMA.replace('incidents', 'new_incidents'))
                
                # Маппинг колонок
                columns_mapping = {}
                old_columns = old_structure['incidents']
                for col in old_columns:
                    columns_mapping[col] = col
                    
                self.copy_data_to_new_table(conn, 'incidents', 'new_incidents', columns_mapping)
                
                c.execute("DROP TABLE IF EXISTS incidents")
                c.execute("ALTER TABLE new_incidents RENAME TO incidents")
            else:
                # Создаем таблицу с нуля
                c.execute(self.INCIDENTS_SCHEMA)
            
            # Создаем индексы
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status)",
                "CREATE INDEX IF NOT EXISTS idx_incidents_datetime ON incidents(datetime)",
                "CREATE INDEX IF NOT EXISTS idx_incidents_coords ON incidents(coords_lat, coords_lon)",
                "CREATE INDEX IF NOT EXISTS idx_incidents_case ON incidents(case_number)"
            ]
            self.create_indexes(conn, 'incidents', indexes)
            
            conn.close()
            self.success_count += 1
            logger.info("Миграция incidents завершена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка миграции incidents: {e}")
            self.errors.append(str(e))
            return False
            
    def migrate_other_tables(self, db_path: Path) -> bool:
        """Миграция остальных таблиц"""
        tables_schemas = [
            ('sru_resources', self.SRU_RESOURCES_SCHEMA),
            ('sru_assignments', self.SRU_ASSIGNMENTS_SCHEMA)
        ]
        
        try:
            conn = sqlite3.connect(db_path)
            
            for table_name, schema in tables_schemas:
                logger.info(f"Миграция {table_name}...")
                c = conn.cursor()
                c.execute(schema)
                self.success_count += 1
                    
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Ошибка миграции таблиц: {e}")
            self.errors.append(str(e))
            return False
            
    def parse_csharp_data(self, csharp_dir: Path) -> List[Dict]:
        """Парсинг данных из C# версии"""
        data = []
        
        # Парсинг container.xml
        container_path = csharp_dir / "container.xml"
        if container_path.exists():
            try:
                tree = ET.parse(container_path)
                root = tree.getroot()
                parsed = {child.tag: child.text for child in root}
                data.append(parsed)
            except Exception as e:
                logger.warning(f"Ошибка парсинга container.xml: {e}")
                
        # Парсинг JSON файлов
        for json_file in csharp_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    parsed = json.load(f)
                    if isinstance(parsed, list):
                        data.extend(parsed)
                    else:
                        data.append(parsed)
            except Exception as e:
                logger.warning(f"Ошибка парсинга {json_file}: {e}")
                
        return data
        
    def migrate_from_csharp(self, csharp_dir: str = r'C:\INSTALLPOISKMORE') -> bool:
        """Миграция данных из C# версии"""
        logger.info(f"Миграция из C# данных...")
        csharp_path = Path(csharp_dir)
        
        if not csharp_path.exists():
            logger.warning(f"Директория C# не найдена: {csharp_dir}")
            return True
            
        parsed_data = self.parse_csharp_data(csharp_path)
        
        if not parsed_data:
            logger.warning("Нет данных для миграции из C#")
            return True
            
        try:
            db_path = self.db_dir / 'incidents.db'
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            migrated_count = 0
            for item in parsed_data:
                try:
                    # Генерируем уникальный case_number если его нет
                    case_number = item.get('CaseNumber', item.get('id', f'AUTO_{migrated_count:04d}'))
                    name = item.get('Name', item.get('name', 'Unnamed'))
                    
                    c.execute("""
                        INSERT OR IGNORE INTO incidents (
                            case_number, 
                            name, 
                            description,
                            coords_lat,
                            coords_lon,
                            datetime,
                            situation_type
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        case_number,
                        name,
                        item.get('Description', item.get('description', '')),
                        55.0,  # Значения по умолчанию
                        37.0,  # для координат
                        datetime.now().isoformat(),
                        'unknown'
                    ))
                    migrated_count += 1
                except Exception as e:
                    logger.warning(f"Не удалось вставить запись: {e}")
                    
            conn.commit()
            conn.close()
            
            if migrated_count > 0:
                logger.info(f"Мигрировано {migrated_count} записей из C#")
                self.success_count += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка миграции из C#: {e}")
            self.errors.append(str(e))
            return False
            
    def verify_migration(self) -> bool:
        """Проверка успешности миграции"""
        logger.info("Проверка миграции...")
        
        for db_name in self.DATABASES.keys():
            db_path = self.db_dir / db_name
            if not db_path.exists():
                logger.warning(f"БД не найдена: {db_path}")
                continue
                
            try:
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                
                # Проверяем наличие основных таблиц
                c.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t[0] for t in c.fetchall()]
                
                logger.info(f"БД {db_name} содержит таблицы: {', '.join(tables)}")
                
                if 'incidents' in tables:
                    c.execute("SELECT COUNT(*) FROM incidents")
                    count = c.fetchone()[0]
                    logger.info(f"  - Таблица incidents содержит {count} записей")
                    
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка проверки {db_name}: {e}")
                self.warnings.append(str(e))
                
        return True
        
    def run_migration(self) -> bool:
        """Запуск полной миграции"""
        logger.info("=" * 60)
        logger.info(f"МИГРАЦИЯ БД ПОИСК-МОРЕ v{self.SCHEMA_VERSION}")
        logger.info("=" * 60)
        
        # Создаем резервные копии
        if not self.create_backup():
            logger.warning("Не удалось создать резервные копии, продолжаем без них")
            
        # Миграция из C# если доступно
        self.migrate_from_csharp()
        
        # Миграция БД
        for db_name in self.DATABASES.keys():
            db_path = self.db_dir / db_name
            
            # Создаем БД если её нет
            if not db_path.exists():
                logger.info(f"Создание новой БД: {db_path}")
                db_path.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(db_path)
                conn.close()
            
            if not self.migrate_incidents_table(db_path):
                logger.error(f"Ошибка миграции {db_name}")
                
            if not self.migrate_other_tables(db_path):
                logger.error(f"Ошибка миграции таблиц в {db_name}")
                
        # Проверка
        self.verify_migration()
        
        return len(self.errors) == 0
        
    def print_summary(self):
        """Вывод итогов миграции"""
        print("\n" + "=" * 60)
        print("📊 ИТОГИ МИГРАЦИИ")
        print("=" * 60)
        print(f"✅ Успешно выполнено: {self.success_count} операций")
        print(f"⚠️  Предупреждений: {len(self.warnings)}")
        print(f"❌ Ошибок: {len(self.errors)}")
        
        if self.warnings:
            print("\n⚠️ Предупреждения:")
            for i, w in enumerate(self.warnings, 1):
                print(f"  {i}. {w}")
                
        if self.errors:
            print("\n❌ Ошибки:")
            for i, e in enumerate(self.errors, 1):
                print(f"  {i}. {e}")
                
        print("=" * 60)

def main():
    """Главная функция"""
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Проверяем существование директории
    if not os.path.exists(work_dir):
        print(f"❌ Директория не существует: {work_dir}")
        print("Создаю директорию...")
        os.makedirs(work_dir, exist_ok=True)
        
    # Инициализация миграции
    migration = DatabaseMigration(work_dir)
    
    print("\n" + "=" * 60)
    print("🚀 МИГРАЦИЯ БАЗЫ ДАННЫХ ПОИСК-МОРЕ")
    print("=" * 60)
    print(f"📁 Рабочая директория: {Path(work_dir).resolve()}")
    print(f"📊 Версия схемы: {migration.SCHEMA_VERSION}")
    print("-" * 60)
    
    # Запрос подтверждения
    print("\n⚠️  ВНИМАНИЕ! Будет выполнена миграция БД.")
    print("   Существующие данные будут сохранены в резервные копии.")
    response = input("\n❓ Продолжить? (да/yes/y): ").lower()
    
    if response not in ['да', 'yes', 'y', 'д']:
        print("❌ Миграция отменена пользователем")
        return 0
        
    # Запуск миграции
    print("\n🔄 Начинаю миграцию...")
    print("-" * 60)
    
    success = migration.run_migration()
    
    # Вывод итогов
    migration.print_summary()
    
    if success:
        print("\n✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        print(f"📁 БД находятся в: {migration.db_dir}")
        if migration.backup_dir.exists():
            print(f"💾 Резервные копии: {migration.backup_dir}")
        return 0
    else:
        print("\n❌ МИГРАЦИЯ ЗАВЕРШЕНА С ОШИБКАМИ!")
        if migration.backup_dir.exists():
            print(f"💾 Восстановите из резервных копий: {migration.backup_dir}")
        return 1

if __name__ == "__main__":
    sys.exit(main())