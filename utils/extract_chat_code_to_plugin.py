#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
extract_chat_code_to_plugin.py — извлекает код из чата для QGIS плагина
Версия 2.0 - с дедупликацией и улучшенным парсингом
"""

import argparse
import datetime
import os
import re
import shutil
import sys
import zipfile

# Регулярка для поиска заголовков файлов
FILE_HEADER_RE = re.compile(
    r'^\s*[-–—]{0,3}\s*FILE:\s*(.+?)\s*[-–—]{0,3}\s*$',
    re.IGNORECASE
)

def normalize_relpath(rel: str) -> str:
    """Нормализация пути файла."""
    rel = rel.strip().strip('"').strip("'")
    rel = re.sub(r'\s*(?:[-–—]{2,}.*|\)+)$', '', rel)
    rel = rel.replace('\\', '/').lstrip('./')
    return rel

def is_valid_path(path: str) -> tuple[bool, str]:
    """Проверяет корректность пути."""
    if not path or path.strip() == '':
        return False, "пустой путь"
   
    invalid_chars = '<>"|?*'
    for char in invalid_chars:
        if char in path:
            return False, f"содержит недопустимый символ '{char}'"
   
    if re.search(r'[|\\]FILE:', path) or r'\s*' in path or '.+?' in path:
        return False, "содержит остатки регулярного выражения"
   
    return True, ""

def parse_stream(text, verbose=False):
    """
    Парсит текст чата, извлекает файлы по заголовкам FILE.
    Поддерживает формат: pythonкод (без разделения на строки)
    Включает дедупликацию файлов.
    """
    files = []
    invalid_files = []
    lines = text.splitlines()
   
    i = 0
    while i < len(lines):
        line = lines[i]
       
        # Ищем заголовок файла
        match = FILE_HEADER_RE.match(line)
        if match:
            relpath = normalize_relpath(match.group(1))
           
            # Проверяем корректность пути
            is_valid, reason = is_valid_path(relpath)
            if not is_valid:
                invalid_files.append({
                    'line': i + 1,
                    'original_line': line.strip(),
                    'parsed_path': relpath,
                    'reason': reason
                })
                if verbose:
                    print(f"Некорректный путь на строке {i + 1}: {relpath} ({reason})")
                i += 1
                continue
           
            if verbose:
                print(f"Найден заголовок: {relpath} на строке {i + 1}")
           
            # Ищем код после заголовка
            content_lines = []
            i += 1
            
            # Ищем код до следующего заголовка FILE
            while i < len(lines):
                current_line = lines[i]
                
                # Проверяем, не начинается ли новый файл
                if FILE_HEADER_RE.match(current_line):
                    break
                
                stripped = current_line.strip()
                
                # Пропускаем комментарии отчетов и описания
                if (stripped.startswith('# Описание изменений:') or 
                    stripped.startswith('# Отчет:') or
                    stripped.startswith('Подтвердите:') or
                    stripped.startswith('"Да"') or
                    'Запросов в этом часе:' in stripped):
                    i += 1
                    continue
                
                # Ищем строку, начинающуюся с python + код
                if stripped.startswith('python') and len(stripped) > 6:
                    # Извлекаем код после слова python
                    code_part = stripped[6:]  # Убираем "python"
                    if code_part.strip():
                        content_lines.append(code_part)
                        if verbose:
                            print(f"  Найден код в строке {i + 1}: {code_part[:50]}...")
                
                # Обычные строки кода (не начинающиеся с python, не комментарии)
                elif (stripped and 
                      not stripped.startswith('#') and 
                      'python' not in stripped.lower() and
                      not stripped.startswith('Подтвердите') and
                      'FILE:' not in stripped):
                    content_lines.append(current_line)
                    if verbose and not content_lines:  # Первая строка кода
                        print(f"  Найдена строка кода: {stripped[:50]}...")
                
                i += 1
           
            if content_lines:
                # Убираем пустые строки в начале и конце
                while content_lines and not content_lines[0].strip():
                    content_lines.pop(0)
                while content_lines and not content_lines[-1].strip():
                    content_lines.pop()
                
                if content_lines:
                    content = '\n'.join(content_lines)
                    files.append((relpath, content))
                    if verbose:
                        print(f"✅ Сохранен {relpath}: {len(content)} символов, {len(content_lines)} строк")
                else:
                    if verbose:
                        print(f"❌ Код для {relpath} пустой после очистки")
            else:
                if verbose:
                    print(f"❌ Нет кода после {relpath}")
                    # Показываем следующие строки для отладки
                    debug_start = max(0, i - 5)
                    debug_end = min(len(lines), i + 5)
                    print(f"  Контекст (строки {debug_start}-{debug_end}):")
                    for j in range(debug_start, debug_end):
                        marker = " >>> " if j == i else "     "
                        print(f"  {marker}{j + 1}: {repr(lines[j])}")
        else:
            i += 1
   
    # ДЕДУПЛИКАЦИЯ: Удаляем дубликаты (оставляем последний вариант)
    unique_files = {}
    for rel, content in files:
        if rel in unique_files:
            if verbose:
                print(f"🔄 Обновлен дубликат: {rel}")
        unique_files[rel] = content

    files = list(unique_files.items())
    
    if verbose:
        print(f"\n📊 После дедупликации: {len(files)} уникальных файлов")
   
    return files, invalid_files

def ensure_under_root(root: str, rel: str) -> str:
    """Проверяет безопасность пути."""
    root_abs = os.path.abspath(root)
    dest = os.path.abspath(os.path.join(root, rel))
    if not dest.startswith(root_abs):
        raise ValueError(f'Unsafe path traversal: {rel}')
    return dest

def write_files(files, root, eol='\n', encoding='utf-8', dry_run=False, backup=False, verbose=True):
    """Записывает файлы на диск."""
    count = 0
    failed_files = []
   
    for rel, content in files:
        try:
            dest = ensure_under_root(root, rel)
            dir_path = os.path.dirname(dest)
           
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
           
            # Нормализуем окончания строк
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            if eol == '\r\n':
                content = content.replace('\n', '\r\n')
           
            if dry_run:
                if verbose:
                    print(f'[DRY-RUN] Would write {dest} ({len(content)} bytes)')
                count += 1
                continue
           
            if backup and os.path.exists(dest):
                ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                backup_path = dest + f'.bak.{ts}'
                shutil.copy2(dest, backup_path)
                if verbose:
                    print(f'[BACKUP] {backup_path}')
           
            # metadata.txt всегда в utf-8
            enc = 'utf-8' if os.path.basename(dest).lower() == 'metadata.txt' else encoding
           
            with open(dest, 'w', encoding=enc, newline='') as fh:
                fh.write(content)
           
            count += 1
            if verbose:
                print(f'[WROTE] {dest}')
               
        except (ValueError, OSError) as e:
            failed_files.append({'path': rel, 'error': str(e)})
            if verbose:
                print(f'[ERROR] {rel}: {e}')
   
    return count, failed_files

def ensure_package_markers(root, verbose=True):
    """Создает __init__.py в нужных папках."""
    python_dirs = ['alg', 'forms', 'utils', 'services', 'dialogs', 'models', 'controllers', 'events', 'db', 'esb']
    
    for subdir in python_dirs:
        subdir_path = os.path.join(root, subdir)
        if os.path.exists(subdir_path):
            init_path = os.path.join(subdir_path, '__init__.py')
            if not os.path.exists(init_path):
                try:
                    with open(init_path, 'w', encoding='utf-8') as fh:
                        fh.write('# Package marker\n')
                    if verbose:
                        print(f'[CREATED] {init_path}')
                except OSError as e:
                    if verbose:
                        print(f'[ERROR] {init_path}: {e}')

def make_zip(root, zip_out, topname=None, verbose=True):
    """Собирает ZIP плагина."""
    if not topname:
        topname = os.path.basename(os.path.normpath(root))
   
    try:
        # Создаем директорию для ZIP если не существует
        zip_dir = os.path.dirname(zip_out)
        if zip_dir and not os.path.exists(zip_dir):
            os.makedirs(zip_dir, exist_ok=True)
            
        with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED) as zf:
            base = os.path.abspath(root)
            file_count = 0
            
            for dirpath, dirnames, filenames in os.walk(root):
                for filename in filenames:
                    # Пропускаем backup файлы и служебные
                    if (filename.endswith('.bak') or 
                        filename.startswith('.') or
                        filename.endswith('.pyc')):
                        continue
                        
                    filepath = os.path.join(dirpath, filename)
                    arcname = os.path.join(topname, os.path.relpath(filepath, base)).replace('\\', '/')
                    zf.write(filepath, arcname)
                    file_count += 1
                    
                    if verbose:
                        print(f'[ZIP] Добавлено: {arcname}')
       
        if verbose:
            print(f'[ZIP] ✅ Готово: {zip_out} ({file_count} файлов)')
            
    except Exception as e:
        print(f'[ERROR] ZIP: {e}')

def main():
    ap = argparse.ArgumentParser(
        description='Извлечение кода из чата в QGIS плагин',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python extract_chat_code_to_plugin.py -i chat.txt -r /path/to/plugin --backup
  python extract_chat_code_to_plugin.py -i chat.txt -r /path/to/plugin --zip-out plugin.zip
        """
    )
    
    ap.add_argument('--input', '-i', default='-',
                    help='Файл чата или "-" для stdin')
    ap.add_argument('--root', '-r', required=True,
                    help='Корень проекта')
    ap.add_argument('--encoding', default='utf-8',
                    help='Кодировка записи (по умолчанию: utf-8)')
    ap.add_argument('--eol', choices=['lf', 'crlf'], default='lf',
                    help='Окончания строк (по умолчанию: lf)')
    ap.add_argument('--dry-run', action='store_true',
                    help='Только показать, что будет сделано')
    ap.add_argument('--backup', action='store_true',
                    help='Создавать бэкапы существующих файлов (.bak)')
    ap.add_argument('--quiet', action='store_true',
                    help='Тихий режим (минимум вывода)')
    ap.add_argument('--verbose', action='store_true',
                    help='Детальный вывод')
    ap.add_argument('--zip-out',
                    help='Путь к выходному ZIP архиву')
    ap.add_argument('--zip-topname',
                    help='Имя корневой папки в ZIP (по умолчанию: имя root)')
   
    args = ap.parse_args()
    verbose = args.verbose and not args.quiet
   
    # Чтение входного файла
    if args.input == '-':
        text = sys.stdin.read()
    else:
        if not os.path.exists(args.input):
            print(f'❌ Файл не найден: {args.input}', file=sys.stderr)
            sys.exit(2)
        try:
            with open(args.input, 'r', encoding='utf-8-sig') as fh:
                text = fh.read()
        except Exception as e:
            print(f'❌ Ошибка чтения файла {args.input}: {e}', file=sys.stderr)
            sys.exit(2)
    
    if verbose:
        print(f"📖 Обрабатываем {len(text)} символов из {args.input}")
    
    # Парсинг файлов из чата
    files, invalid_files = parse_stream(text, verbose=verbose)
   
    # Отчет о найденных файлах
    if not args.quiet:
        print(f'\n=== Найдено корректных файлов: {len(files)} ===')
        for rel, content in files:
            size_kb = len(content) / 1024
            print(f' ✅ {rel} ({size_kb:.1f} KB)')
   
    if invalid_files and not args.quiet:
        print(f'\n=== Некорректные файлы: {len(invalid_files)} ===')
        for invalid in invalid_files:
            print(f' ❌ Строка {invalid["line"]}: {invalid["reason"]}')
            print(f'    {invalid["original_line"]}')
    
    if not files:
        print('❌ Файлы с корректным кодом не найдены', file=sys.stderr)
        if not args.quiet:
            print('💡 Проверьте формат заголовков: --- FILE: path/to/file.py ---')
        sys.exit(3)
    
    # Запись файлов
    eol_char = '\n' if args.eol == 'lf' else '\r\n'
    n, failed_files = write_files(
        files, args.root, 
        eol=eol_char, 
        encoding=args.encoding,
        dry_run=args.dry_run, 
        backup=args.backup, 
        verbose=verbose
    )
    
    if failed_files and not args.quiet:
        print(f'\n=== Ошибки записи: {len(failed_files)} ===')
        for failed in failed_files:
            print(f' ❌ {failed["path"]}: {failed["error"]}')
    
    # Создание __init__.py файлов
    if not args.dry_run:
        if verbose:
            print(f'\n📦 Создание маркеров пакетов...')
        ensure_package_markers(args.root, verbose=verbose)
    
    # Создание ZIP архива
    if args.zip_out and not args.dry_run:
        if verbose:
            print(f'\n🗜️ Создание ZIP архива...')
        make_zip(args.root, args.zip_out, topname=args.zip_topname, verbose=verbose)
    
    # Итоговый отчет
    success_icon = "✅" if n == len(files) else "⚠️"
    print(f'\n{success_icon} === ИТОГО: {n} из {len(files)} файлов обработано ===')
    
    if args.zip_out and not args.dry_run and os.path.exists(args.zip_out):
        zip_size = os.path.getsize(args.zip_out) / 1024
        print(f'📦 ZIP архив: {args.zip_out} ({zip_size:.1f} KB)')

if __name__ == '__main__':
    main()