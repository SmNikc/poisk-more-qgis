import os
import zipfile

def create_zip(source_dir, zip_filename, exclude_dirs):
    """
    Создает ZIP-архив из указанной директории, включая все подпапки и файлы,
    кроме указанных в exclude_dirs директорий.
    
    :param source_dir: Путь к исходной директории.
    :param zip_filename: Полный путь к создаваемому ZIP-файлу (рекомендуется вне source_dir).
    :param exclude_dirs: Список полных путей к директориям, которые нужно исключить.
    """
    # Удаляем старый архив, если существует
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
    
    abs_zip = os.path.abspath(zip_filename)
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Нормализуем пути для сравнения
            normalized_exclude = [os.path.normpath(ed) for ed in exclude_dirs]
            # Исключаем директории из дальнейшего обхода
            dirs[:] = [d for d in dirs if os.path.normpath(os.path.join(root, d)) not in normalized_exclude]
            for file in files:
                file_path = os.path.join(root, file)
                abs_file = os.path.abspath(file_path)
                # Пропускаем сам ZIP-файл, если он внутри source_dir
                if abs_file == abs_zip:
                    continue
                # Сохраняем относительный путь в архиве
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

# Пример использования
source_dir = r"C:\Projects\poisk-more-qgis"
exclude_dirs = [r"C:\Projects\poisk-more-qgis\docker", r"C:\Projects\poisk-more-qgis\.git"]
# Рекомендуем создавать ZIP вне source_dir, чтобы избежать проблем
zip_filename = r"C:\Projects\poisk-more-qgis_output\poisk-more-qgis_archive.zip"  # Или укажите путь вне папки, напр. r"C:\Projects\poisk-more-qgis_archive.zip"

create_zip(source_dir, zip_filename, exclude_dirs)

print(f"Архив '{zip_filename}' создан успешно.")