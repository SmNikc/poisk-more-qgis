#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_incident_dialog_and_calculations_fix.py

Назначение:
  1) Подключить диалог 'Регистрация происшествия' в меню плагина.
  2) Переименовать проблемные файлы в calculations (убрать дефисы и двойной .py),
     создать calculations/__init__.py при отсутствии.
  3) Поправить импорты по всему проекту под новые имена и относительные пути.

Запуск из корня проекта:
  python C:\Projects\poisk-more-qgis\poiskmore_plugin\tools\apply_incident_dialog_and_calculations_fix.py
"""

import re
import sys
import shutil
from datetime import datetime
from pathlib import Path

# Определяем корень плагина по расположению скрипта:
TOOLS_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = TOOLS_DIR.parent
CALC_DIR = PLUGIN_ROOT / "calculations"
DIALOGS_DIR = PLUGIN_ROOT / "dialogs"
MAIN_PLUGIN = PLUGIN_ROOT / "mainPlugin.py"

ENC = "utf-8"

def ts() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def read_text(p: Path) -> str:
    return p.read_text(encoding=ENC)

def write_text(p: Path, text: str) -> None:
    p.write_text(text, encoding=ENC)

def backup(p: Path) -> None:
    bak = p.with_suffix(p.suffix + f".bak.{ts()}")
    shutil.copy2(p, bak)
    print(f"[BACKUP] {p} -> {bak}")

def ensure_calculations_init() -> None:
    CALC_DIR.mkdir(parents=True, exist_ok=True)
    init_py = CALC_DIR / "__init__.py"
    if not init_py.exists():
        content = (
            "# -*- coding: utf-8 -*-\n"
            "\"\"\"Пакет расчётов Поиск‑Море (QGIS).\"\"\"\n"
            "from .drift_calculator import DriftCalculator as DriftCalculatorPM  # Опционально\n"
        )
        write_text(init_py, content)
        print(f"[CREATE] {init_py}")

def safe_rename(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if dst.exists():
        # Если уже переименован ранее — оставляем целевое имя
        print(f"[SKIP] target already exists: {dst.name}")
        return
    backup(src)
    src.rename(dst)
    print(f"[RENAME] {src.name} -> {dst.name}")

def rename_problem_files() -> None:
    mapping = {
        "drift-calculator.py": "drift_calculator.py",
        "drift_calculator_qgis.py.py": "drift_calculator_qgis.py",
        "search-area-calculator.py": "search_area_calculator.py",
    }
    for bad, good in mapping.items():
        safe_rename(CALC_DIR / bad, CALC_DIR / good)

def fix_imports_in_text(text: str) -> str:
    original = text

    # 1) Приводим импорты calculations к относительным
    # from calculations... -> from .calculations...
    text = re.sub(r'(^|\n)\s*from\s+calculations(\.| )', r'\1from .calculations\2', text)

    # import calculations.something -> from .calculations import something
    def repl_import(match):
        mod = match.group(1)
        mod_fixed = mod.replace('-', '_')
        return f"from .calculations import {mod_fixed}"
    text = re.sub(r'(^|\n)\s*import\s+calculations\.([A-Za-z0-9_\-]+)', repl_import, text)

    # 2) Убираем дефисы в именах модулей в любых импорт-строках
    text = re.sub(r'(\.calculations\.)drift\-calculator', r'\1drift_calculator', text)
    text = re.sub(r'(\.calculations\.)search\-area\-calculator', r'\1search_area_calculator', text)

    # 3) Исправляем упоминания двойного .py в импорт-строках (на случай артефактов)
    text = re.sub(r'(\.calculations\.drift_calculator_qgis)\.py\b', r'\1', text)

    return text if text != original else original

def iter_code_files(root: Path):
    for p in root.rglob("*.py"):
        # Не трогаем бэкапы и сам скрипт
        name = p.name
        if ".bak." in name:
            continue
        yield p

def apply_import_fixes() -> None:
    for py in iter_code_files(PLUGIN_ROOT):
        try:
            text = read_text(py)
        except Exception:
            continue
        fixed = fix_imports_in_text(text)
        if fixed != text:
            backup(py)
            write_text(py, fixed)
            print(f"[FIX IMPORTS] {py}")

def ensure_qaction_import(text: str) -> str:
    # Проверяем, есть ли импорт QAction (PyQt или qgis.PyQt)
    if re.search(r'from\s+PyQt5\.QtWidgets\s+import\s+.*\bQAction\b', text):
        return text
    if re.search(r'from\s+qgis\.PyQt\.QtWidgets\s+import\s+.*\bQAction\b', text):
        return text
    # Вставим вариант через qgis.PyQt (стабильно для QGIS)
    lines = text.splitlines()
    # Найдём последний импорт и вставим после него
    insert_at = 0
    for i, line in enumerate(lines):
        if re.match(r'^\s*(import|from)\s+', line):
            insert_at = i + 1
    lines.insert(insert_at, "from qgis.PyQt.QtWidgets import QAction")
    return "\n".join(lines)

def ensure_dialog_import(text: str) -> str:
    if re.search(r'from\s+\.\s*dialogs\.incident_registration_dialog\s+import\s+IncidentRegistrationDialog', text):
        return text
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if re.match(r'^\s*(import|from)\s+', line):
            insert_at = i + 1
    lines.insert(insert_at, "from .dialogs.incident_registration_dialog import IncidentRegistrationDialog")
    return "\n".join(lines)

def inject_into_method(text: str, method_name: str, payload_lines: list) -> str:
    """
    Вставляет payload_lines в тело метода (после первой строки def ...:).
    Если метода нет — создаёт его в классе основного плагина.
    """
    pattern = re.compile(rf'\ndef\s+{method_name}\s*\(\s*self[^\)]*\)\s*:\s*\n', re.MULTILINE)
    m = pattern.search(text)
    if not m:
        # Попробуем найти класс плагина и дописать метод в конец класса
        class_m = re.search(r'\nclass\s+([A-Za-z0-9_]+)\(.*\):\s*\n', text)
        if not class_m:
            # Если класса нет, просто добавим метод в конец файла
            add = "\n\ndef {name}(self):\n    pass\n".format(name=method_name)
            return text + add
        # Найдём конец класса (грубо — по началу следующего класса или EOF)
        start = class_m.end()
        next_class = re.search(r'\nclass\s+[A-Za-z0-9_]+\(', text[start:])
        insert_at = len(text) if not next_class else start + next_class.start()
        method_code = "\n\ndef {name}(self):\n    pass\n".format(name=method_name)
        return text[:insert_at] + method_code + text[insert_at:]

    # Метод есть — вставляем после его заголовка
    insert_pos = m.end()
    # Определяем отступ (берём отступ первой строки тела, если есть)
    body_match = re.search(r'(\n)([ \t]+)\S', text[insert_pos:])
    indent = body_match.group(2) if body_match else "    "
    payload = "".join(f"{indent}{line}\n" for line in payload_lines)
    return text[:insert_pos] + payload + text[insert_pos:]

def ensure_initGui_action(text: str) -> str:
    if "Регистрация происшествия" in text and "_open_incident_registration_dialog" in text:
        return text  # уже подключено
    payload = [
        'self.action_incident = QAction("Регистрация происшествия", self.iface.mainWindow())',
        'self.action_incident.triggered.connect(self._open_incident_registration_dialog)',
        'try:',
        '    self.iface.addPluginToMenu("&Поиск-Море", self.action_incident)',
        'except Exception:',
        '    # На случай альтернативной структуры меню: добавим к главному окну',
        '    self.iface.mainWindow().addAction(self.action_incident)',
    ]
    return inject_into_method(text, "initGui", payload)

def ensure_unload_action(text: str) -> str:
    if re.search(r'removePluginMenu\([^)]*self\.action_incident', text):
        return text
    payload = [
        'try:',
        '    self.iface.removePluginMenu("&Поиск-Море", self.action_incident)',
        'except Exception:',
        '    try:',
        '        self.iface.mainWindow().removeAction(self.action_incident)',
        '    except Exception:',
        '        pass',
    ]
    return inject_into_method(text, "unload", payload)

def ensure_open_dialog_method(text: str) -> str:
    if "_open_incident_registration_dialog" in text:
        return text
    method_code = [
        "def _open_incident_registration_dialog(self):",
        "    try:",
        "        dlg = IncidentRegistrationDialog(self.iface.mainWindow())",
        "        dlg.exec_()",
        "    except Exception as ex:",
        "        # Журналируем, но не падаем",
        "        try:",
        "            from .utils.logger import log_error",
        "            log_error(f'Incident dialog error: {ex}')",
        "        except Exception:",
        "            pass",
        ""
    ]
    # Вставим метод в конец файла
    if not text.endswith("\n"):
        text += "\n"
    return text + "\n" + "\n".join(method_code)

def patch_main_plugin() -> None:
    if not MAIN_PLUGIN.exists():
        print(f"[WARN] mainPlugin.py не найден: {MAIN_PLUGIN}")
        return
    text = read_text(MAIN_PLUGIN)
    original = text

    text = ensure_qaction_import(text)
    text = ensure_dialog_import(text)
    text = ensure_initGui_action(text)
    text = ensure_unload_action(text)
    text = ensure_open_dialog_method(text)

    if text != original:
        backup(MAIN_PLUGIN)
        write_text(MAIN_PLUGIN, text)
        print(f"[PATCH] {MAIN_PLUGIN} — меню подключено.")
    else:
        print(f"[OK] {MAIN_PLUGIN} — изменений не требуется.")

def main() -> int:
    print(f"[ROOT] {PLUGIN_ROOT}")
    ensure_calculations_init()
    rename_problem_files()
    apply_import_fixes()
    patch_main_plugin()
    print("[DONE]")
    return 0

if __name__ == "__main__":
    sys.exit(main())
