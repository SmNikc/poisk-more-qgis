import zipfile
from pathlib import Path
from html import escape

TEXT_EXTENSIONS = {
    '.py', '.ui', '.ts', '.js', '.html', '.json', '.xml', '.txt', '.md',
    '.ini', '.cfg', '.yml', '.yaml', '.qgs', '.qml', '.geojson', '.sql',
    '.bat', '.sh', '.docx.txt', '.csproj'
}

def is_text_file(filename: str) -> bool:
    path = Path(filename)
    suffix = path.suffix.lower()
    return (suffix in TEXT_EXTENSIONS) or (not path.suffix)

def extract_text_files(zip_path: Path, output_html_path: Path, title: str):
    entries = []
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for file_info in zipf.infolist():
            try:
                raw_name = file_info.filename.encode("cp437", errors="replace").decode("utf-8", errors="replace")
            except Exception:
                raw_name = file_info.filename

            if file_info.is_dir():
                continue
            if is_text_file(raw_name):
                try:
                    with zipf.open(file_info) as f:
                        try:
                            content = f.read().decode('utf-8')
                        except UnicodeDecodeError:
                            content = f.read().decode('cp1251', errors='replace')
                        block = (
                            f"<h2>--- FILE: {escape(raw_name)} ---</h2>\n"
                            f"<pre><code>{escape(content)}</code></pre>\n"
                        )
                        entries.append(block)
                except Exception as e:
                    print(f"⚠️ Пропущен файл: {raw_name} — ошибка: {e}")

    output_html_path.write_text(
        f"<html><body><h1>{escape(title)}</h1>\n" + "\n".join(entries) + "\n</body></html>",
        encoding="utf-8"
    )

output_dir = Path("C:/Projects/poisk-more-qgis_output")
output_dir.mkdir(parents=True, exist_ok=True)

extract_text_files(
    Path(r"C:\Users\Admin\Downloads\poiskmore_plugin_v22.zip"),
    output_dir / "poiskmore_plugin_v22.html",
    "Лента кода: poiskmore_plugin_v22.zip"
)

extract_text_files(
    Path(r"C:\Users\Admin\Downloads\poiskmore_plugin_v22.zip"),
    output_dir / "poiskmore_plugin_v22",
    "Лента кода: poiskmore_plugin_v22.zip"
)

print("✅ HTML-файлы успешно созданы.")