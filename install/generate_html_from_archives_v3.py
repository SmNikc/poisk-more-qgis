import os
import zipfile
import html

# Разрешённые расширения (нижний регистр)
EXTENSIONS = {
    '.py', '.ui', '.ts', '.js', '.html', '.json', '.xml', '.txt',
    '.md', '.ini', '.cfg', '.yml', '.yaml', '.qgs', '.qml',
    '.geojson', '.sql', '.bat', '.sh', '.docx.txt'
}

def process_archive(archive_path, output_html_path, title):
    blocks = []
    with zipfile.ZipFile(archive_path, 'r') as zf:
        for info in zf.infolist():
            # пропускаем каталоги
            if info.is_dir():
                continue

            # нормализуем расширение в нижний регистр
            _, ext = os.path.splitext(info.filename)
            if ext.lower() not in EXTENSIONS:
                continue

            # пытаемся прочитать файл как UTF-8, подставляя � при ошибках
            raw = zf.read(info.filename)
            try:
                content = raw.decode('utf-8')
            except UnicodeDecodeError:
                content = raw.decode('utf-8', errors='replace')

            # экранируем для вывода в HTML
            safe_name    = html.escape(info.filename)
            safe_content = html.escape(content)

            block = (
                f'<h2>--- FILE: {safe_name} ---</h2>\n'
                f'<pre><code>{safe_content}</code></pre>\n'
            )
            blocks.append(block)

    # запись результирующего HTML
    with open(output_html_path, 'w', encoding='utf-8') as out:
        out.write(f'<html><body><h1>Лента кода: {html.escape(title)}</h1>\n')
        out.write('\n'.join(blocks))
        out.write('\n</body></html>')

if __name__ == '__main__':
    # пример вызова:
    # C:\Python313\python.exe generate_html_from_archives_v3.py CS.zip CS.html
    import sys
    arc, out = sys.argv[1], sys.argv[2]
    title = os.path.splitext(os.path.basename(arc))[0]
    process_archive(arc, out, title)