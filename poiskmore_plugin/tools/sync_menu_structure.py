#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автопатчер sync_menu_structure.py
Назначение:
  - Синхронизировать сборку меню с menu_structure.py без переписывания существующей логики:
    * Создать модуль расширения меню poiskmore_plugin/menu_extensions/incident_menu_patch.py
    * Мягко "обернуть" create_menu_structure(menu, actions, run_action), чтобы вызвать расширение
  - Идемпотентен: повторный запуск безопасен.
  - Делает резервную копию menu_structure.py в backup_before_update/menu_structure.py.YYYYMMDD-HHMMSS.bak

Точки модификации:
  - poiskmore_plugin/menu_structure.py   -> добавляется тонкий wrapper
  - poiskmore_plugin/menu_extensions/incident_menu_patch.py -> создаётся/обновляется
  - poiskmore_plugin/menu_extensions/__init__.py -> создаётся при отсутствии

Запуск:
  python C:\Projects\poisk-more-qgis\poiskmore_plugin\tools\sync_menu_structure.py
"""

from __future__ import annotations

import re
import sys
import shutil
from datetime import datetime
from pathlib import Path

BANNER = "[sync_menu_structure]"

def _ts() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def find_plugin_root() -> Path:
    # Скрипт лежит: <root>/poiskmore_plugin/tools/sync_menu_structure.py
    here = Path(__file__).resolve()
    tools_dir = here.parent
    plugin_root = tools_dir.parent
    # Валидация наличия menu_structure.py и mainPlugin.py
    ms = plugin_root / "menu_structure.py"
    mp = plugin_root / "mainPlugin.py"
    if not ms.exists():
        print(f"{BANNER} ERROR: не найден menu_structure.py по пути: {ms}")
        sys.exit(1)
    if not mp.exists():
        print(f"{BANNER} WARN: не найден mainPlugin.py по пути: {mp} (не критично)")
    return plugin_root

def ensure_menu_extensions(plugin_root: Path) -> Path:
    ext_dir = plugin_root / "menu_extensions"
    ext_dir.mkdir(parents=True, exist_ok=True)
    init_py = ext_dir / "__init__.py"
    if not init_py.exists():
        init_py.write_text("# -*- coding: utf-8 -*-\n# namespace for menu extensions\n", encoding="utf-8")
        print(f"{BANNER} CREATE: {init_py}")
    return ext_dir

def write_incident_menu_patch(ext_dir: Path) -> None:
    """
    Создаёт/обновляет poiskmore_plugin/menu_extensions/incident_menu_patch.py
    Добавляет пункт меню 'Регистрация происшествия' и открывает диалог.
    Использует qgis.utils.iface, чтобы НЕ трогать mainPlugin.py.
    """
    target = ext_dir / "incident_menu_patch.py"
    code = r'''# -*- coding: utf-8 -*-
"""
incident_menu_patch.py
Добавляет пункт меню "Регистрация происшествия" в корневое меню плагина.
Безопасен при повторном добавлении (идемпотентен).
По клику:
  1) пробует вызвать run_action("incident_registration") если он передан и callable;
  2) если run_action не обрабатывает, откроет диалог напрямую через qgis.utils.iface.
"""

from PyQt5.QtWidgets import QAction, QMessageBox
from qgis.utils import iface

# Импорт диалога регистрации. Диалог уже есть в проекте (dialogs/incident_registration_dialog.py).
# Если модуль отсутствует, падать не будем — покажем понятное сообщение.
try:
    from ..dialogs.incident_registration_dialog import IncidentRegistrationDialog
    _DIALOG_OK = True
except Exception as _e:
    IncidentRegistrationDialog = None  # type: ignore
    _DIALOG_OK = False
    _IMPORT_ERR = _e

ACTION_KEY = "incident_registration"
ACTION_TEXT = "Регистрация происшествия"

def apply(menu, actions: dict, run_action):
    """
    Добавляет QAction в корневое меню плагина.
    :param menu: QMenu верхнего уровня плагина
    :param actions: dict с уже созданными действиями
    :param run_action: callable(str) или None — единый роутер действий, если используется
    """
    # Если уже есть — ничего не делаем
    existing = actions.get(ACTION_KEY)
    if existing is not None:
        # на всякий случай перепривяжем слот (без дублей)
        try:
            for slot in existing.triggered.connections():
                # PyQt5 не даёт простого API удаления — пропустим
                pass
        except Exception:
            pass
        existing.triggered.connect(lambda: _trigger(run_action))
        return

    act = QAction(ACTION_TEXT, menu)
    act.setObjectName(ACTION_KEY)
    act.triggered.connect(lambda: _trigger(run_action))
    menu.addAction(act)
    actions[ACTION_KEY] = act

def _trigger(run_action):
    """Единая точка: сначала пробуем общий роутер, если есть; затем — прямой вызов диалога."""
    # 1) общий роутер (если используется архитектурой плагина)
    try:
        if callable(run_action):
            run_action(ACTION_KEY)
            return
    except Exception:
        # игнорируем и падаем на прямой вызов
        pass

    # 2) прямой вызов диалога, если импорт прошёл
    if not _DIALOG_OK or IncidentRegistrationDialog is None:
        try:
            parent = iface.mainWindow() if iface else None
        except Exception:
            parent = None
        QMessageBox.warning(parent, "Поиск-Море",
                            "Не удалось открыть диалог регистрации происшествия:\n"
                            f"{str(_IMPORT_ERR)}")
        return

    try:
        parent = iface.mainWindow() if iface else None
        dlg = IncidentRegistrationDialog(parent)
        dlg.exec_()
    except Exception as e:
        try:
            parent = iface.mainWindow() if iface else None
        except Exception:
            parent = None
        QMessageBox.warning(parent, "Поиск-Море",
                            "Ошибка при открытии диалога регистрации происшествия:\n"
                            f"{repr(e)}")
'''
    if not target.exists():
        target.write_text(code, encoding="utf-8")
        print(f"{BANNER} CREATE: {target}")
    else:
        prev = target.read_text(encoding="utf-8")
        if prev != code:
            backup = target.with_suffix(".py.bak." + _ts())
            shutil.copy2(str(target), str(backup))
            target.write_text(code, encoding="utf-8")
            print(f"{BANNER} UPDATE: {target} (backup -> {backup.name})")
        else:
            print(f"{BANNER} OK: {target} без изменений")

def patch_menu_structure(plugin_root: Path) -> None:
    menu_py = plugin_root / "menu_structure.py"
    content = menu_py.read_text(encoding="utf-8")
    marker_begin = "# --- begin: auto-patch by sync_menu_structure"
    marker_end = "# --- end: auto-patch by sync_menu_structure"

    if marker_begin in content and marker_end in content:
        print(f"{BANNER} OK: menu_structure.py уже содержит auto-patch wrapper — пропускаю")
        return

    # Проверим, что функция create_menu_structure присутствует
    has_create = re.search(r"^\s*def\s+create_menu_structure\s*\(\s*menu\s*,\s*actions\s*,\s*run_action\s*\)\s*:",
                           content, flags=re.MULTILINE) or \
                 re.search(r"^\s*def\s+create_menu_structure\s*\(", content, flags=re.MULTILINE)

    backup_dir = plugin_root / "backup_before_update"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"menu_structure.py.{_ts()}.bak"
    shutil.copy2(str(menu_py), str(backup_path))
    print(f"{BANNER} BACKUP: {backup_path}")

    wrapper = f"""
{marker_begin} ({_ts()})
# Мягкий wrapper вокруг create_menu_structure: вызывает оригинал, затем подключает расширение меню
try:
    _original_create_menu_structure  # type: ignore
except NameError:
    _original_create_menu_structure = None  # type: ignore

if _original_create_menu_structure is None:
    try:
        # Сохраняем оригинал
        _original_create_menu_structure = create_menu_structure  # type: ignore
    except Exception:
        _original_create_menu_structure = None  # type: ignore

if _original_create_menu_structure is not None:
    def create_menu_structure(menu, actions, run_action):
        # сначала оригинальная сборка меню
        _original_create_menu_structure(menu, actions, run_action)
        # затем — расширение меню "Регистрация происшествия"
        try:
            from .menu_extensions.incident_menu_patch import apply as _apply_incident_menu_patch
            _apply_incident_menu_patch(menu, actions, run_action)
        except Exception:
            # Не падаем, если вдруг модуль не загрузился — меню останется как было
            pass
else:
    # На случай, если в файле не было create_menu_structure: создаём тонкий вариант,
    # который просто подключит расширение меню.
    def create_menu_structure(menu, actions, run_action):
        try:
            from .menu_extensions.incident_menu_patch import apply as _apply_incident_menu_patch
            _apply_incident_menu_patch(menu, actions, run_action)
        except Exception:
            pass

{marker_end}
""".lstrip("\n")

    # Вставляем wrapper в конец файла
    new_content = content
    # Добавим перевод строки, если файл не оканчивается \n
    if not new_content.endswith("\n"):
        new_content += "\n"
    new_content += "\n" + wrapper

    menu_py.write_text(new_content, encoding="utf-8")
    print(f"{BANNER} PATCH: внесён auto-wrapper в {menu_py}")

def main():
    plugin_root = find_plugin_root()
    # 1) menu_extensions/*
    ext_dir = ensure_menu_extensions(plugin_root)
    write_incident_menu_patch(ext_dir)
    # 2) menu_structure.py
    patch_menu_structure(plugin_root)
    print(f"{BANNER} Done.")

if __name__ == "__main__":
    main()
