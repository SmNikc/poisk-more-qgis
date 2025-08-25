#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматического добавления метода get_data() во все диалоги плагина ПОИСК-МОРЕ
Автор: AI Assistant
Дата: 2024
Использование: python fix_dialogs_get_data.py [путь_к_плагину]
"""

import os
import re
import shutil
import sys
import ast
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

class DialogFixer:
    """Класс для исправления диалогов - добавление метода get_data()"""
    
    def __init__(self, plugin_path: str = "C:\\Projects\\poisk-more-qgis\\poiskmore_plugin"):
        """
        Инициализация
        
        Args:
            plugin_path: Путь к папке плагина
        """
        self.plugin_path = Path(plugin_path)
        self.dialog_patterns = [
            "dialog_*.py",
            "*_dialog.py",
            "*Dialog.py"
        ]
        self.backup_dir = self.plugin_path / "backups" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.fixed_files = []
        self.skipped_files = []
        self.error_files = []
        
    def find_dialog_files(self) -> List[Path]:
        """Найти все файлы диалогов в проекте"""
        dialog_files = []
        
        # Основная папка dialogs
        dialogs_dir = self.plugin_path / "dialogs"
        if dialogs_dir.exists():
            for pattern in self.dialog_patterns:
                dialog_files.extend(dialogs_dir.glob(pattern))
        
        # Также ищем в корне и других папках
        for pattern in self.dialog_patterns:
            dialog_files.extend(self.plugin_path.rglob(pattern))
        
        # Убираем дубликаты и файлы в backup
        dialog_files = list(set(dialog_files))
        dialog_files = [f for f in dialog_files if "backup" not in str(f).lower()]
        dialog_files = [f for f in dialog_files if ".bak." not in str(f)]
        
        return sorted(dialog_files)
    
    def check_file_has_dialog_class(self, filepath: Path) -> Optional[str]:
        """
        Проверить, есть ли в файле класс диалога
        
        Returns:
            Имя класса диалога или None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсим AST для поиска классов
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Проверяем, что класс наследуется от QDialog
                    for base in node.bases:
                        if isinstance(base, ast.Name) and 'Dialog' in base.id:
                            return node.name
                        if isinstance(base, ast.Attribute) and 'Dialog' in base.attr:
                            return node.name
            
            # Альтернативный поиск через регулярку
            class_pattern = r'class\s+(\w+)\s*\([^)]*QDialog[^)]*\)'
            matches = re.findall(class_pattern, content)
            if matches:
                return matches[0]
                
        except Exception as e:
            print(f"Ошибка при проверке {filepath}: {e}")
        
        return None
    
    def check_methods_in_class(self, filepath: Path, class_name: str) -> Tuple[bool, bool, bool]:
        """
        Проверить наличие методов в классе
        
        Returns:
            (has_get_data, has_collect_data, has_get_form_data)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Паттерны для поиска методов
            get_data_pattern = rf'def\s+get_data\s*\('
            collect_data_pattern = rf'def\s+collect_data\s*\('
            get_form_data_pattern = rf'def\s+get_form_data\s*\('
            
            has_get_data = bool(re.search(get_data_pattern, content))
            has_collect_data = bool(re.search(collect_data_pattern, content))
            has_get_form_data = bool(re.search(get_form_data_pattern, content))
            
            return has_get_data, has_collect_data, has_get_form_data
            
        except Exception as e:
            print(f"Ошибка при проверке методов в {filepath}: {e}")
            return False, False, False
    
    def add_get_data_method(self, filepath: Path, class_name: str, 
                           has_collect_data: bool, has_get_form_data: bool) -> bool:
        """
        Добавить метод get_data в класс
        
        Args:
            filepath: Путь к файлу
            class_name: Имя класса
            has_collect_data: Есть ли метод collect_data
            has_get_form_data: Есть ли метод get_form_data
            
        Returns:
            True если успешно добавлен
        """
        try:
            # Создаем резервную копию
            self.backup_file(filepath)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Находим конец класса
            class_start = -1
            class_indent = ""
            in_class = False
            last_method_line = -1
            
            for i, line in enumerate(lines):
                # Находим начало класса
                if f"class {class_name}" in line:
                    class_start = i
                    in_class = True
                    # Определяем отступ для методов класса
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        match = re.match(r'^(\s+)', next_line)
                        if match:
                            class_indent = match.group(1)
                    continue
                
                # Если мы в классе
                if in_class:
                    # Проверяем, не начался ли новый класс
                    if line.strip().startswith('class ') and i > class_start:
                        break
                    
                    # Запоминаем последнюю строку с методом
                    if line.strip().startswith('def '):
                        last_method_line = i
                    
                    # Также учитываем строки внутри методов
                    if line.strip() and not line.strip().startswith('#'):
                        if not line[0].isspace() and i > class_start + 1:
                            # Вышли из класса
                            break
                        if line.startswith(class_indent) and not line.startswith(class_indent + ' '):
                            last_method_line = i
            
            # Определяем, где вставить новый метод
            if last_method_line > 0:
                # Находим конец последнего метода
                insert_line = last_method_line + 1
                while insert_line < len(lines):
                    if (lines[insert_line].strip() and 
                        not lines[insert_line].strip().startswith('#') and
                        not lines[insert_line].startswith(class_indent + '    ')):
                        break
                    insert_line += 1
            else:
                # Вставляем после определения класса
                insert_line = class_start + 1
                while insert_line < len(lines) and lines[insert_line].strip().startswith('"""'):
                    insert_line += 1
                while insert_line < len(lines) and '"""' in lines[insert_line]:
                    insert_line += 1
                if insert_line < len(lines) and not lines[insert_line].strip():
                    insert_line += 1
            
            # Формируем метод get_data
            method_lines = []
            method_lines.append(f"\n{class_indent}def get_data(self):\n")
            method_lines.append(f'{class_indent}    """\n')
            method_lines.append(f'{class_indent}    Получить данные из формы\n')
            method_lines.append(f'{class_indent}    \n')
            method_lines.append(f'{class_indent}    Returns:\n')
            method_lines.append(f'{class_indent}        dict: Словарь с данными формы\n')
            method_lines.append(f'{class_indent}    """\n')
            
            if has_collect_data:
                method_lines.append(f'{class_indent}    return self.collect_data()\n')
            elif has_get_form_data:
                method_lines.append(f'{class_indent}    return self.get_form_data()\n')
            else:
                # Добавляем базовую реализацию collect_data
                method_lines.append(f'{class_indent}    # Автоматически добавленный метод\n')
                method_lines.append(f'{class_indent}    # TODO: Реализовать сбор данных из полей формы\n')
                method_lines.append(f'{class_indent}    try:\n')
                method_lines.append(f'{class_indent}        return self.collect_data()\n')
                method_lines.append(f'{class_indent}    except AttributeError:\n')
                method_lines.append(f'{class_indent}        # Если collect_data не реализован, возвращаем пустой словарь\n')
                method_lines.append(f'{class_indent}        data = {{}}\n')
                method_lines.append(f'{class_indent}        \n')
                method_lines.append(f'{class_indent}        # Попытка собрать данные из стандартных виджетов\n')
                method_lines.append(f'{class_indent}        for attr_name in dir(self):\n')
                method_lines.append(f'{class_indent}            if attr_name.startswith("txt_") or attr_name.startswith("spin_") or attr_name.startswith("cmb_"):\n')
                method_lines.append(f'{class_indent}                try:\n')
                method_lines.append(f'{class_indent}                    widget = getattr(self, attr_name)\n')
                method_lines.append(f'{class_indent}                    if hasattr(widget, "text"):\n')
                method_lines.append(f'{class_indent}                        data[attr_name] = widget.text()\n')
                method_lines.append(f'{class_indent}                    elif hasattr(widget, "value"):\n')
                method_lines.append(f'{class_indent}                        data[attr_name] = widget.value()\n')
                method_lines.append(f'{class_indent}                    elif hasattr(widget, "currentText"):\n')
                method_lines.append(f'{class_indent}                        data[attr_name] = widget.currentText()\n')
                method_lines.append(f'{class_indent}                    elif hasattr(widget, "toPlainText"):\n')
                method_lines.append(f'{class_indent}                        data[attr_name] = widget.toPlainText()\n')
                method_lines.append(f'{class_indent}                except:\n')
                method_lines.append(f'{class_indent}                    pass\n')
                method_lines.append(f'{class_indent}        \n')
                method_lines.append(f'{class_indent}        return data\n')
                
                # Также добавим collect_data если его нет
                method_lines.append(f"\n{class_indent}def collect_data(self):\n")
                method_lines.append(f'{class_indent}    """\n')
                method_lines.append(f'{class_indent}    Собрать данные из полей формы\n')
                method_lines.append(f'{class_indent}    \n')
                method_lines.append(f'{class_indent}    Returns:\n')
                method_lines.append(f'{class_indent}        dict: Словарь с данными формы\n')
                method_lines.append(f'{class_indent}    """\n')
                method_lines.append(f'{class_indent}    data = {{}}\n')
                method_lines.append(f'{class_indent}    \n')
                method_lines.append(f'{class_indent}    # TODO: Реализовать сбор данных из конкретных полей\n')
                method_lines.append(f'{class_indent}    # Пример:\n')
                method_lines.append(f'{class_indent}    # if hasattr(self, "txt_name"):\n')
                method_lines.append(f'{class_indent}    #     data["name"] = self.txt_name.text()\n')
                method_lines.append(f'{class_indent}    \n')
                method_lines.append(f'{class_indent}    return data\n')
            
            # Вставляем метод
            lines.insert(insert_line, ''.join(method_lines))
            
            # Записываем обратно
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при добавлении метода в {filepath}: {e}")
            return False
    
    def backup_file(self, filepath: Path):
        """Создать резервную копию файла"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        relative_path = filepath.relative_to(self.plugin_path)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(filepath, backup_path)
    
    def process_all_dialogs(self):
        """Обработать все файлы диалогов"""
        print("=" * 60)
        print("СКРИПТ ИСПРАВЛЕНИЯ ДИАЛОГОВ ПОИСК-МОРЕ")
        print("=" * 60)
        print(f"Путь к плагину: {self.plugin_path}")
        print(f"Папка резервных копий: {self.backup_dir}")
        print("-" * 60)
        
        # Находим все диалоги
        dialog_files = self.find_dialog_files()
        print(f"Найдено файлов диалогов: {len(dialog_files)}")
        
        for filepath in dialog_files:
            print(f"\nОбработка: {filepath.name}")
            
            # Проверяем наличие класса диалога
            class_name = self.check_file_has_dialog_class(filepath)
            if not class_name:
                print(f"  ⚠️ Не найден класс диалога, пропускаем")
                self.skipped_files.append(filepath)
                continue
            
            print(f"  Найден класс: {class_name}")
            
            # Проверяем наличие методов
            has_get_data, has_collect_data, has_get_form_data = self.check_methods_in_class(
                filepath, class_name
            )
            
            print(f"  Методы: get_data={has_get_data}, collect_data={has_collect_data}, get_form_data={has_get_form_data}")
            
            # Если get_data уже есть, пропускаем
            if has_get_data:
                print(f"  ✅ Метод get_data уже существует")
                self.skipped_files.append(filepath)
                continue
            
            # Добавляем метод get_data
            if self.add_get_data_method(filepath, class_name, has_collect_data, has_get_form_data):
                print(f"  ✅ Метод get_data успешно добавлен")
                self.fixed_files.append(filepath)
            else:
                print(f"  ❌ Ошибка при добавлении метода")
                self.error_files.append(filepath)
        
        # Итоговая статистика
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТЫ:")
        print("=" * 60)
        print(f"✅ Исправлено файлов: {len(self.fixed_files)}")
        if self.fixed_files:
            for f in self.fixed_files:
                print(f"   - {f.name}")
        
        print(f"\n⚠️ Пропущено файлов: {len(self.skipped_files)}")
        if self.skipped_files and len(self.skipped_files) <= 10:
            for f in self.skipped_files:
                print(f"   - {f.name}")
        
        print(f"\n❌ Файлов с ошибками: {len(self.error_files)}")
        if self.error_files:
            for f in self.error_files:
                print(f"   - {f.name}")
        
        print(f"\n📁 Резервные копии сохранены в: {self.backup_dir}")
        
        return len(self.error_files) == 0
    
    def restore_from_backup(self):
        """Восстановить файлы из резервной копии"""
        if not self.backup_dir.exists():
            print("Папка с резервными копиями не найдена")
            return False
        
        print(f"Восстановление из: {self.backup_dir}")
        
        for backup_file in self.backup_dir.rglob("*.py"):
            relative_path = backup_file.relative_to(self.backup_dir)
            original_file = self.plugin_path / relative_path
            
            print(f"Восстанавливаем: {relative_path}")
            shutil.copy2(backup_file, original_file)
        
        print("Восстановление завершено")
        return True


def main():
    """Главная функция"""
    # Получаем путь к плагину из аргументов или используем по умолчанию
    if len(sys.argv) > 1:
        plugin_path = sys.argv[1]
    else:
        plugin_path = r"C:\Projects\poisk-more-qgis\poiskmore_plugin"
    
    # Проверяем существование пути
    if not os.path.exists(plugin_path):
        print(f"❌ Путь не существует: {plugin_path}")
        print("\nИспользование:")
        print(f"  python {sys.argv[0]} [путь_к_плагину]")
        print(f"\nПример:")
        print(f"  python {sys.argv[0]} C:\\Projects\\poisk-more-qgis\\poiskmore_plugin")
        return 1
    
    # Создаем и запускаем фиксер
    fixer = DialogFixer(plugin_path)
    
    # Спрашиваем подтверждение
    print(f"Будут обработаны диалоги в: {plugin_path}")
    response = input("\nПродолжить? (y/n): ").lower()
    
    if response != 'y':
        print("Отменено пользователем")
        return 0
    
    # Обрабатываем диалоги
    success = fixer.process_all_dialogs()
    
    if not success:
        print("\n⚠️ Обнаружены ошибки при обработке")
        response = input("Восстановить из резервной копии? (y/n): ").lower()
        if response == 'y':
            fixer.restore_from_backup()
    
    print("\n✅ Готово!")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())