import os
import re
import sys

# Путь к исходному HTML-файлу с правками
source_file = r"C:\Users\Admin\Downloads\Исправленные_файлы.html"

# Папка назначения для перезаписи файлов
target_dir = r"C:\Projects\poisk-more-qgis\poiskmore_plugin"

def extract_file_content(file_path):
    if not os.path.exists(file_path):
        print(f"Ошибка: файл {file_path} не найден. Укажите правильный путь.")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Извлечение содержимого файлов, исключая служебные строки
    files = re.findall(r"--- FILE: (.+?) ---(?:\s*```python)?\s*[\s\S]*?(?:\n\S)?([\s\S]*?)(?=\n--- FILE:|\Z)", content)
    return {file_name.strip(): re.sub(r"\s*(Свернуть|Перенос|Исполнить|Копировать)\s*", "", code.strip()) for file_name, code in files if code.strip()}

def update_files():
    file_contents = extract_file_content(source_file)
    if not file_contents:
        return
    for file_name, content in file_contents.items():
        target_path = os.path.join(target_dir, file_name)
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Файл {file_name} успешно обновлен.")
        except Exception as e:
            print(f"Ошибка при обновлении файла {file_name}: {e}")

if __name__ == "__main__":
    if not os.path.exists(target_dir):
        print(f"Папка {target_dir} не существует. Создайте ее или укажите правильный путь.")
    else:
        update_files()