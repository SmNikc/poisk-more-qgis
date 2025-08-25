#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт очистки проекта ПОИСК-МОРЕ от временных файлов и дубликатов
Автор: AI Assistant
Дата: 2024
Использование: python cleanup_project.py [путь_к_плагину]
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class ProjectCleaner:
    """Класс для очистки проекта от временных файлов"""
    
    def __init__(self, project_path: str = "C:\\Projects\\poisk-more-qgis\\poiskmore_plugin"):
        """
        Инициализация
        
        Args:
            project_path: Путь к проекту
        """
        self.project_path = Path(project_path)
        self.trash_dir = self.project_path / "trash" / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Паттерны файлов для удаления
        self.patterns_to_delete = [
            "*.bak.*",           # Резервные копии
            "*.pyc",             # Скомпилированные Python файлы
            "__pycache__",       # Папки кэша Python
            "*.tmp",             # Временные файлы
            "*.log",             # Логи (опционально)
            ".DS_Store",         # macOS системные файлы
            "Thumbs.db",         # Windows системные файлы
            "desktop.ini",       # Windows системные файлы
        ]
        
        # Известные дубликаты
        self.known_duplicates = [
            ("poiskmore.py", "mainPlugin.py"),  # poiskmore.py - дубликат mainPlugin.py
        ]
        
        # Статистика
        self.deleted_files: List[Path] = []
        self.moved_files: List[Path] = []
        self.errors: List[tuple] = []
        
    def find_files_to_clean(self) -> Dict[str, List[Path]]:
        """Найти все файлы для очистки"""
        files_to_clean = {
            "backup_files": [],
            "cache_files": [],
            "temp_files": [],
            "system_files": [],
            "duplicates": [],
            "empty_dirs": []
        }
        
        # Ищем файлы по паттернам
        for pattern in self.patterns_to_delete:
            for file_path in self.project_path.rglob(pattern):
                if file_path.is_file():
                    if ".bak." in str(file_path):
                        files_to_clean["backup_files"].append(file_path)
                    elif file_path.suffix in [".pyc", ".pyo"]:
                        files_to_clean["cache_files"].append(file_path)
                    elif file_path.suffix in [".tmp", ".temp"]:
                        files_to_clean["temp_files"].append(file_path)
                    elif file_path.name in [".DS_Store", "Thumbs.db", "desktop.ini"]:
                        files_to_clean["system_files"].append(file_path)
                elif file_path.is_dir() and file_path.name == "__pycache__":
                    files_to_clean["cache_files"].append(file_path)
        
        # Проверяем известные дубликаты
        for duplicate, original in self.known_duplicates:
            dup_path = self.project_path / duplicate
            orig_path = self.project_path / original
            if dup_path.exists() and orig_path.exists():
                files_to_clean["duplicates"].append(dup_path)
        
        # Находим пустые директории
        for root, dirs, files in os.walk(self.project_path, topdown=False):
            root_path = Path(root)
            # Пропускаем .git и другие служебные папки
            if ".git" in str(root_path) or "trash" in str(root_path):
                continue
            if not dirs and not files:
                files_to_clean["empty_dirs"].append(root_path)
        
        return files_to_clean
    
    def move_to_trash(self, file_path: Path) -> bool:
        """
        Переместить файл в корзину
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True если успешно перемещен
        """
        try:
            # Создаем папку для мусора если нужно
            self.trash_dir.mkdir(parents=True, exist_ok=True)
            
            # Вычисляем относительный путь
            relative_path = file_path.relative_to(self.project_path)
            trash_path = self.trash_dir / relative_path
            
            # Создаем директорию в корзине
            trash_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Перемещаем файл
            if file_path.is_dir():
                shutil.move(str(file_path), str(trash_path))
            else:
                shutil.move(str(file_path), str(trash_path))
            
            self.moved_files.append(file_path)
            return True
            
        except Exception as e:
            self.errors.append((file_path, str(e)))
            return False
    
    def delete_file(self, file_path: Path) -> bool:
        """
        Удалить файл навсегда
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            True если успешно удален
        """
        try:
            if file_path.is_dir():
                shutil.rmtree(file_path)
            else:
                file_path.unlink()
            
            self.deleted_files.append(file_path)
            return True
            
        except Exception as e:
            self.errors.append((file_path, str(e)))
            return False
    
    def clean_project(self, move_to_trash: bool = True):
        """
        Очистить проект
        
        Args:
            move_to_trash: Если True - перемещать в корзину, иначе удалять навсегда
        """
        print("=" * 60)
        print("ОЧИСТКА ПРОЕКТА ПОИСК-МОРЕ")
        print("=" * 60)
        print(f"Путь к проекту: {self.project_path}")
        print(f"Режим: {'Перемещение в корзину' if move_to_trash else 'Полное удаление'}")
        if move_to_trash:
            print(f"Корзина: {self.trash_dir}")
        print("-" * 60)
        
        # Находим файлы для очистки
        files_to_clean = self.find_files_to_clean()
        
        # Показываем статистику
        total_files = sum(len(files) for files in files_to_clean.values())
        print(f"\nНайдено файлов для очистки: {total_files}")
        print(f"  📁 Backup файлы (.bak.*): {len(files_to_clean['backup_files'])}")
        print(f"  🗑️ Кэш файлы (.pyc, __pycache__): {len(files_to_clean['cache_files'])}")
        print(f"  📄 Временные файлы (.tmp): {len(files_to_clean['temp_files'])}")
        print(f"  💻 Системные файлы: {len(files_to_clean['system_files'])}")
        print(f"  🔁 Дубликаты: {len(files_to_clean['duplicates'])}")
        print(f"  📂 Пустые папки: {len(files_to_clean['empty_dirs'])}")
        
        if total_files == 0:
            print("\n✅ Проект уже чистый!")
            return True
        
        # Показываем детали для важных файлов
        if files_to_clean['duplicates']:
            print("\n🔁 Дубликаты для удаления:")
            for dup in files_to_clean['duplicates']:
                print(f"   - {dup.name}")
        
        # Спрашиваем подтверждение
        print("\n" + "-" * 60)
        response = input(f"Продолжить очистку? (y/n): ").lower()
        if response != 'y':
            print("Отменено пользователем")
            return False
        
        # Выполняем очистку
        print("\n🧹 Выполняется очистка...")
        
        for category, files in files_to_clean.items():
            if not files:
                continue
                
            print(f"\n{category}:")
            for file_path in files:
                status = "✅" if (self.move_to_trash(file_path) if move_to_trash else self.delete_file(file_path)) else "❌"
                print(f"  {status} {file_path.name}")
        
        # Итоговая статистика
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ ОЧИСТКИ:")
        print("=" * 60)
        
        if move_to_trash:
            print(f"✅ Перемещено в корзину: {len(self.moved_files)} файлов")
        else:
            print(f"✅ Удалено: {len(self.deleted_files)} файлов")
        
        if self.errors:
            print(f"❌ Ошибки: {len(self.errors)}")
            for file_path, error in self.errors[:5]:  # Показываем первые 5 ошибок
                print(f"   - {file_path.name}: {error}")
        
        # Подсчет освобожденного места
        total_size = 0
        for file_path in (self.moved_files if move_to_trash else self.deleted_files):
            if file_path.exists():  # Для перемещенных файлов
                continue
            try:
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            except:
                pass
        
        if total_size > 0:
            size_mb = total_size / (1024 * 1024)
            print(f"\n💾 Освобождено места: {size_mb:.2f} MB")
        
        if move_to_trash:
            print(f"\n📁 Файлы сохранены в: {self.trash_dir}")
            print("   (можно удалить папку trash когда убедитесь, что все работает)")
        
        return len(self.errors) == 0
    
    def restore_from_trash(self):
        """Восстановить файлы из корзины"""
        if not self.trash_dir.exists():
            print("❌ Корзина не найдена")
            return False
        
        print(f"📂 Восстановление из: {self.trash_dir}")
        
        restored = 0
        errors = 0
        
        for trash_file in self.trash_dir.rglob("*"):
            if trash_file.is_file():
                try:
                    relative_path = trash_file.relative_to(self.trash_dir)
                    original_path = self.project_path / relative_path
                    
                    # Создаем директорию если нужно
                    original_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Перемещаем обратно
                    shutil.move(str(trash_file), str(original_path))
                    restored += 1
                    print(f"  ✅ {relative_path}")
                    
                except Exception as e:
                    errors += 1
                    print(f"  ❌ {trash_file.name}: {e}")
        
        print(f"\n✅ Восстановлено: {restored} файлов")
        if errors > 0:
            print(f"❌ Ошибок: {errors}")
        
        # Удаляем пустую корзину
        try:
            shutil.rmtree(self.trash_dir)
            print("🗑️ Корзина удалена")
        except:
            pass
        
        return errors == 0


def main():
    """Главная функция"""
    # Получаем путь к проекту
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = r"C:\Projects\poisk-more-qgis\poiskmore_plugin"
    
    # Проверяем существование
    if not os.path.exists(project_path):
        print(f"❌ Путь не существует: {project_path}")
        print("\nИспользование:")
        print(f"  python {sys.argv[0]} [путь_к_проекту]")
        return 1
    
    # Создаем очиститель
    cleaner = ProjectCleaner(project_path)
    
    print("🧹 УТИЛИТА ОЧИСТКИ ПРОЕКТА")
    print("-" * 60)
    print("Выберите режим:")
    print("  1. Переместить мусор в корзину (безопасно)")
    print("  2. Удалить навсегда (опасно!)")
    print("  3. Восстановить из корзины")
    print("  0. Выход")
    
    choice = input("\nВыбор (1/2/3/0): ").strip()
    
    if choice == "1":
        success = cleaner.clean_project(move_to_trash=True)
    elif choice == "2":
        print("\n⚠️ ВНИМАНИЕ! Файлы будут удалены НАВСЕГДА!")
        confirm = input("Вы уверены? Введите 'DELETE' для подтверждения: ")
        if confirm == "DELETE":
            success = cleaner.clean_project(move_to_trash=False)
        else:
            print("Отменено")
            return 0
    elif choice == "3":
        success = cleaner.restore_from_trash()
    else:
        print("Выход")
        return 0
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())