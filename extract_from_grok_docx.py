import os
import re
from docx import Document

def extract_code_blocks(docx_path):
    doc = Document(docx_path)
    lines = []
    for para in doc.paragraphs:
        lines.append(para.text)
    text = '\n'.join(lines)
    file_blocks = re.findall(
        r'--- FILE: (.*?) ---\s*([\s\S]*?)(?=(?:--- FILE: |$))',
        text
    )
    return file_blocks

def is_code_line(line):
    # Примитивный фильтр для кода (можно доработать под ваш стиль)
    if not line.strip():
        return True
    if line.strip().startswith("#"):
        return True
    if re.match(r'^\s*(def |class |import |from |return |for |while |if |elif |else|try:|except |with |@)', line):
        return True
    if re.match(r'^[\s\w\[\]\(\)\{\},.:=\'\"#%<>/\*-]+$', line) and not re.search(r'[а-яА-Я]', line):
        return True
    return False

def auto_comment_non_code(content, ext):
    # Только для кода — .py, .js, .ts, .java и т.п.
    if ext not in ('.py', '.js', '.ts', '.java'):
        return content
    lines = []
    for line in content.strip().split('\n'):
        if is_code_line(line):
            lines.append(line)
        else:
            lines.append('# ' + line)
    return '\n'.join(lines)

def save_code_blocks(blocks, root_dir):
    for file_path, content in blocks:
        file_path = file_path.strip().replace('\\', '/')
        ext = os.path.splitext(file_path)[1].lower()
        # Пропуск бинарных файлов
        if ext in ('.png', '.jpg', '.ico', '.exe', '.dll') or 'бинарный файл' in content.lower():
            print(f"⚠️ Пропускаю бинарный файл: {file_path}")
            continue
        abs_path = os.path.join(root_dir, file_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        # Автокомментирование только для кода
        content2 = auto_comment_non_code(content, ext)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content2.strip() + '\n')
        print(f"✅ Сохранён: {abs_path}")

if __name__ == "__main__":
    # Настройте эти переменные под себя:
    docx_path = r"C:\Users\Admin\Downloads\GROK_FULL_3.docx"
    plugin_dir = r"C:\Projects\poisk-more-qgis\poiskmore_plugin"
    blocks = extract_code_blocks(docx_path)
    print(f"Найдено файлов: {len(blocks)}")
    save_code_blocks(blocks, plugin_dir)
    print("✅ Все файлы успешно сохранены с авто-комментированием не-кода в .py/.js/.ts.")

