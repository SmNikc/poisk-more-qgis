# -*- coding: utf-8 -*-
import os
import html
import mimetypes
import shutil
import sys

TEXT_EXTENSIONS = {
    '.py', '.ui', '.ts', '.js', '.html', '.json', '.xml', '.txt', '.md',
    '.ini', '.cfg', '.yml', '.yaml', '.qgs', '.qml', '.geojson', '.sql',
    '.bat', '.sh', '.docx.txt', '.csproj', '.qrc'
}

def is_text_file(file_path):
    if file_path.lower().endswith('.zip'):
        return False
    mime, _ = mimetypes.guess_type(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    return mime and mime.startswith('text') or ext in TEXT_EXTENSIONS

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='cp1251') as f:
                return f.read()
        except UnicodeDecodeError:
            return '<em>Невозможно прочитать файл (неизвестная кодировка).</em>'
    except Exception as e:
        return f'<em>Ошибка: {e}</em>'

def generate_html(root_dir, output_html_path, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = ['docker']

    # Простой и безопасный способ создания резервной копии
    bak_path = output_html_path.replace(".html", "_BAK.html")
    if os.path.exists(output_html_path):
        if os.path.exists(bak_path):
            os.remove(bak_path)
        shutil.move(output_html_path, bak_path)

    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
    output_dir = os.path.abspath(os.path.dirname(output_html_path))

    with open(output_html_path, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html><html lang="ru"><head>')
        f.write('<meta charset="UTF-8"><title>Содержимое проекта</title></head><body>')
        f.write('<h1>Содержимое проекта</h1>')

        for dirpath, dirnames, filenames in os.walk(root_dir):
            abs_dirpath = os.path.abspath(dirpath)
            if abs_dirpath.startswith(output_dir):
                dirnames.clear()
                continue

            dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
            rel_dir = os.path.relpath(dirpath, root_dir)

            if rel_dir != ".":
                f.write(f'<h2>{html.escape(rel_dir)}</h2>')

            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                rel_file_path = os.path.join(rel_dir, filename)
                if is_text_file(file_path):
                    content = read_file_content(file_path)
                    f.write(f'<h3>{html.escape(rel_file_path)}</h3><pre>{html.escape(content)}</pre>')
                else:
                    f.write(f'<h3>{html.escape(rel_file_path)}</h3><em>Бинарный файл.</em>')

        f.write('</body></html>')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Использование: python script.py <исходная_папка> <выходной_html>")
        sys.exit(1)

    generate_html(sys.argv[1], sys.argv[2])