#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# Используем те же регулярки из вашего скрипта
FILE_HEADER_RE = re.compile(
    r'^\s*[-–—]{0,3}\s*FILE:\s*(.+?)\s*[-–—]{0,3}\s*$',
    re.IGNORECASE | re.MULTILINE
)

def debug_chat_format(file_path):
    """Анализирует формат кода в чате для отладки."""
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        text = f.read()
    
    lines = text.splitlines()
    
    # Найдем первый заголовок и посмотрим что после него
    for i, line in enumerate(lines):
        if FILE_HEADER_RE.match(line):
            print(f"=== ЗАГОЛОВОК НА СТРОКЕ {i+1} ===")
            print(f"Строка: {line}")
            
            # Показываем следующие 10 строк
            print(f"\n=== СЛЕДУЮЩИЕ 10 СТРОК ===")
            for j in range(i+1, min(i+11, len(lines))):
                print(f"{j+1:4d}: {repr(lines[j])}")
            
            # Ищем блоки кода разных форматов
            print(f"\n=== АНАЛИЗ КОДА ===")
            code_start = i + 1
            while code_start < len(lines):
                if FILE_HEADER_RE.match(lines[code_start]):
                    break
                    
                line_stripped = lines[code_start].strip()
                if line_stripped.startswith('```'):
                    print(f"Найден блок ``` на строке {code_start+1}: {repr(line_stripped)}")
                elif line_stripped.startswith('python'):
                    print(f"Найдено 'python' на строке {code_start+1}: {repr(line_stripped)}")
                elif 'from ' in line_stripped or 'import ' in line_stripped or 'class ' in line_stripped:
                    print(f"Найден Python код на строке {code_start+1}: {repr(line_stripped)}")
                
                code_start += 1
                if code_start > i + 20:  # Ограничиваем поиск
                    break
            
            return  # Анализируем только первый заголовок

if __name__ == '__main__':
    file_path = r"C:\Users\smeta\Downloads\POISKMORE - Grokночь на 19 авг.txt"
    debug_chat_format(file_path)