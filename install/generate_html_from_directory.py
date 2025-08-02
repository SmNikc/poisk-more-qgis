import os
import html

root_dir = r"C:\Projects\poisk-more-qgis"
output_html = r"C:\Projects\poisk-more-qgis_output\Содержимое_проекта.html"

special_text = {'.gitignore', '.flake8', 'Dockerfile', 'LICENSE', 'README.md', 'requirements.txt'}

exclude_dirs = {'docker', '.git', '.idea', '.vscode', '__pycache__'}

def is_binary_file(path):
    # Простая проверка: если не удаётся открыть как текст, значит бинарный
    try:
        with open(path, 'r', encoding='utf-8') as f:
            f.read()
        return False
    except Exception:
        return True

def should_include_yml(path):
    rel_path = path.replace("\\", "/")
    return rel_path.startswith(".github/workflows/") and rel_path.lower().endswith(('.yml', '.yaml'))

def should_exclude(rel_path):
    # Пропуск системных/мусорных директорий и desktop.ini
    parts = rel_path.replace("\\", "/").split("/")
    if any(p in exclude_dirs for p in parts):
        return True
    if os.path.basename(rel_path).lower() == "desktop.ini":
        return True
    return False

def scan_and_generate(root_dir, output_html):
    with open(output_html, "w", encoding="utf-8") as f:
        f.write('<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8"><title>Содержимое проекта</title></head><body>\n')
        f.write('<h1>Содержимое проекта</h1>\n')
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Фильтрация папок на лету
            rel_dir = os.path.relpath(dirpath, root_dir)
            if rel_dir == ".":
                rel_dir = ""
            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            for filename in filenames:
                rel_file_path = os.path.join(rel_dir, filename).replace("\\", "/") if rel_dir else filename
                # Пропуск мусорных файлов/папок
                if should_exclude(rel_file_path):
                    continue
                base_name = os.path.basename(rel_file_path)
                # Спец-файлы и .github/workflows/*.yml — всегда текстовые!
                if base_name in special_text or should_include_yml(rel_file_path):
                    try:
                        with open(os.path.join(dirpath, filename), 'r', encoding='utf-8') as file:
                            content = file.read()
                    except Exception:
                        content = ''
                    f.write(f'<h3>{html.escape(rel_file_path)}</h3><pre>{html.escape(content)}</pre>\n')
                    continue
                # Все обычные текстовые файлы (пытаемся открыть как текст)
                abs_path = os.path.join(dirpath, filename)
                if not is_binary_file(abs_path):
                    try:
                        with open(abs_path, 'r', encoding='utf-8') as file:
                            content = file.read()
                        f.write(f'<h3>{html.escape(rel_file_path)}</h3><pre>{html.escape(content)}</pre>\n')
                    except Exception:
                        f.write(f'<h3>{html.escape(rel_file_path)}</h3><em>Бинарный файл.</em>\n')
                else:
                    f.write(f'<h3>{html.escape(rel_file_path)}</h3><em>Бинарный файл.</em>\n')
        f.write('</body></html>\n')

scan_and_generate(root_dir, output_html)
