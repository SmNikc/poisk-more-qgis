import os
import html
from pathlib import Path
import mimetypes

def is_text_file(file_path, blocksize=512):
    """
    Определяет, является ли файл текстовым.
    Метод основан на анализе MIME-типа файла.
    """
    mime, _ = mimetypes.guess_type(file_path)
    if mime is None:
        return False
    return mime.startswith('text') or mime in ['application/xml', 'application/json']

def read_file_content(file_path):
    """
    Читает содержимое файла, если он является текстовым.
    Возвращает содержимое как строку или сообщение о невозможности чтения.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='cp1251') as f:
                return f.read()
        except UnicodeDecodeError:
            return '<em>Невозможно прочитать содержимое файла (неизвестная кодировка).</em>'
    except Exception as e:
        return f'<em>Ошибка при чтении файла: {e}</em>'

def generate_html(root_dir, output_html_path, title="Содержимое проекта"):
    """
    Генерирует HTML-файл, отображающий структуру директорий и содержимое текстовых файлов.
    """
    print(f"Начало генерации HTML файла: {output_html_path}...")

    # Убедимся, что директория для HTML-файла существует
    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)

    with open(output_html_path, 'w', encoding='utf-8') as f:
        # Запись заголовков HTML-документа
        f.write('<!DOCTYPE html>\n<html lang="ru">\n<head>\n')
        f.write('<meta charset="UTF-8">\n')
        f.write(f'<title>{html.escape(title)}</title>\n')
        f.write('<style>\n')
        f.write('body { font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; }\n')
        f.write('pre { background-color: #2d2d2d; color: #f8f8f2; padding: 10px; border-radius: 5px; overflow-x: auto; }\n')
        f.write('h1 { color: #333; border-bottom: 2px solid #ddd; padding-bottom: 10px; }\n')
        f.write('h2 { color: #555; margin-top: 40px; }\n')
        f.write('h3 { color: #666; margin-top: 20px; }\n')
        f.write('.directory { margin-left: 20px; }\n')
        f.write('</style>\n')
        f.write('</head>\n<body>\n')

        f.write(f'<h1>{html.escape(title)}</h1>\n')

        # Обход всех файлов и каталогов внутри корневой папки
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Получение относительного пути от корневой папки
            rel_dir = os.path.relpath(dirpath, root_dir)
            if rel_dir == ".":
                rel_dir = ""
            else:
                f.write(f'<h2>Каталог: {html.escape(rel_dir)}</h2>\n')
                f.write('<div class="directory">\n')

            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                rel_file_path = os.path.join(rel_dir, filename)
                if is_text_file(file_path):
                    content = read_file_content(file_path)
                    f.write(f'<h3>--- FILE: {html.escape(rel_file_path)} ---</h3>\n')
                    f.write('<pre><code>\n')
                    f.write(html.escape(content))
                    f.write('\n</code></pre>\n')
                else:
                    f.write(f'<h3>--- FILE: {html.escape(rel_file_path)} ---</h3>\n')
                    f.write('<p><em>Бинарный файл или не текстовый формат. Содержимое не отображается.</em></p>\n')
            if rel_dir != "":
                f.write('</div>\n')  # Закрытие блока каталога

        # Завершение HTML-документа
        f.write('</body>\n</html>')

    print("HTML файл успешно создан.")

def main():
    # Укажите путь к корневой папке, которую нужно обработать
    root_dir = r"C:\Projects\poisk-more-qgis\poiskmore_plugin"
    
    # Проверьте, существует ли корневая папка
    if not os.path.isdir(root_dir):
        print(f"Ошибка: Корневая папка не найдена по пути: {root_dir}")
        return
    
    # Определите путь к выходному HTML-файлу
    output_html_path = r"C:\Projects\poisk-more-qgis\install\Содержимое_проекта.html"
    
    # Генерация HTML-файла
    generate_html(root_dir, output_html_path, title="Содержимое проекта: poiskmore_plugin")

if __name__ == "__main__":
    main()