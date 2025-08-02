import sys
from pathlib import Path

# --- КОНФИГУРАЦИЯ ОШИБОК ДЛЯ ИСПРАВЛЕНИЯ ---
# Добавляйте сюда другие строки, которые нужно удалить или заменить.
# Формат: 'что_удалить': 'на_что_заменить' (пустая строка для полного удаления)
# Важно: включайте пробелы, чтобы замена была точной.
REPLACEMENTS = {
    ' translatable="yes"': '',
    # Пример для будущих исправлений:
    # '<some_buggy_tag>': '<a_correct_tag>',
}

def clean_ui_file(file_path: Path) -> bool:
    """
    Читает .ui файл, удаляет известные проблемные атрибуты и перезаписывает файл.
    
    Возвращает True, если файл был изменен, иначе False.
    """
    try:
        # Читаем содержимое файла с явным указанием кодировки UTF-8
        original_content = file_path.read_text(encoding='utf-8')
        modified_content = original_content

        # Применяем все исправления из словаря REPLACEMENTS
        for old, new in REPLACEMENTS.items():
            modified_content = modified_content.replace(old, new)

        # Проверяем, были ли внесены изменения
        if original_content != modified_content:
            # Перезаписываем файл только если он изменился
            file_path.write_text(modified_content, encoding='utf-8')
            return True
            
    except Exception as e:
        print(f"  ❌ Ошибка при обработке файла {file_path.name}: {e}")
    
    return False

def main(directory: str):
    """
    Основная функция для запуска сканирования и очистки.
    """
    print("🚀 Запуск скрипта очистки .ui файлов...")
    
    target_dir = Path(directory)
    if not target_dir.is_dir():
        print(f"🚫 Ошибка: Директория '{directory}' не найдена.")
        sys.exit(1)
        
    # Ищем все .ui файлы рекурсивно (включая подпапки)
    ui_files = list(target_dir.rglob('*.ui'))
    
    if not ui_files:
        print("🤷 Файлы с расширением .ui не найдены.")
        return

    print(f"🔎 Найдено {len(ui_files)} .ui файлов. Начинаю проверку...")
    
    changed_files_count = 0
    
    for file_path in ui_files:
        print(f"   - Проверяю: {file_path.relative_to(target_dir)}", end='')
        if clean_ui_file(file_path):
            print(" -> ✅ Исправлено!")
            changed_files_count += 1
        else:
            print(" -> ✔️ OK")
            
    print("\n🎉 Проверка завершена!")
    if changed_files_count > 0:
        print(f"🔧 Исправлено {changed_files_count} из {len(ui_files)} файлов.")
    else:
        print("👍 Все файлы уже в порядке, исправления не потребовались.")

if __name__ == "__main__":
    # Проверяем, передан ли путь к директории в качестве аргумента
    if len(sys.argv) < 2:
        print("⚠️ Использование: python clean_ui_files.py <путь_к_папке_с_проектом>")
        # Если путь не передан, используем текущую директорию как запасной вариант
        print("ℹ️ Путь не указан. Попытка сканирования текущей директории...")
        target_directory = "."
    else:
        target_directory = sys.argv[1]
    
    main(target_directory)