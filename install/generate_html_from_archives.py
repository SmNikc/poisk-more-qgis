# FILE: C:\Projects\poisk-more-qgis\install\generate_html_from_archives.py
import zipfile
from pathlib import Path
from html import escape

# Поддерживаемые расширения (регистронезависимо)
TEXT_EXTENSIONS = {
    '.py', '.cs', '.csproj', '.ts', '.js', '.html', '.json', '.xml',
    '.txt', '.md', '.ini', '.cfg', '.yml', '.yaml', '.qgs', '.qml',
    '.geojson', '.sql', '.bat', '.sh', '.docx.txt'
}

# Пути к архивам (абсолютные пути на вашей машине)
CS_ZIP      = Path(r"C:\Users\Admin\Downloads\poiskmore_plugin_v22.zip")
CSPROJ_ZIP  = Path(r"C:\Users\Admin\Downloads\poiskmore_plugin_v22.zip")
OUTPUT_DIR  = Path(r"C:\Projects\poisk-more-qgis_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def is_text_file(filename: str) -> bool:
    """
    Проверяет по расширению (без учёта регистра) или без расширения.
    """
    ext = Path(filename).suffix.lower()
    return (ext in TEXT_EXTENSIONS) or (not ext)


def extract_and_write(zip_path: Path, out_html: Path, title: str):
    blocks = []
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = info.filename
            if not is_text_file(name):
                continue
            raw = zf.read(name)
            try:
                text = raw.decode('utf-8')
            except Exception:
                text = raw.decode('cp1251', errors='replace')
            safe_name    = escape(name)
            safe_text    = escape(text)
            blocks.append(
                f'<h2>--- FILE: {safe_name} ---</h2>\n'
                f'<pre><code>{safe_text}</code></pre>\n'
            )
    html_content = '<html><body><h1>Лента: ' + escape(title) + '</h1>\n' + ''.join(blocks) + '</body></html>'
    out_html.write_text(html_content, encoding='utf-8')


if __name__ == '__main__':
    extract_and_write(CS_ZIP,     OUTPUT_DIR / 'poiskmore_plugin_v22.html',     'poiskmore_plugin_v22.zip')
    extract_and_write(CSPROJ_ZIP, OUTPUT_DIR / 'poiskmore_plugin_v22.html', 'poiskmore_plugin_v22.zip')
    print('✅ HTML-ленты успешно созданы в', OUTPUT_DIR)