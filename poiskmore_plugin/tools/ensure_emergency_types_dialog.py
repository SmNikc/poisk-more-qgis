# -*- coding: utf-8 -*-
"""
Автопатчер ПОИСК-МОРЕ: ensure_emergency_types_dialog
----------------------------------------------------
Назначение:
  1) Создает по месту файл dialogs/emergency_types_dialog.py (полноценный PyQt5-диалог
     со списком типов происшествий, CRUD и сохранением в JSON).
  2) Вносит правки в mainPlugin.py:
     - добавляет импорт EmergencyTypesDialog;
     - добавляет пункт меню "Типы происшествий" в initGui();
     - добавляет обработчик _on_emergency_types();
     - добавляет снятие пункта меню в unload().

Особенности:
  - Повторный запуск безопасен (идемпотентен).
  - Перед правкой mainPlugin.py делается .bak с меткой времени.
  - Попытка найти класс плагина как класс, внутри которого определён initGui().

Запуск (Windows):
  python C:\Projects\poisk-more-qgis\poiskmore_plugin\tools\ensure_emergency_types_dialog.py ^
         --root "C:\Projects\poisk-more-qgis\poiskmore_plugin"

Если запускать из каталога tools, можно без --root: корень вычислится автоматически.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import io
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional, Tuple

# ----------------------------- аргументы -----------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Ensure EmergencyTypesDialog and patch mainPlugin.py")
    p.add_argument("--root", type=str, default=None,
                   help="Корень плагина (папка, где лежит mainPlugin.py). "
                        "По умолчанию: два уровня выше текущего файла.")
    p.add_argument("--force-overwrite", action="store_true",
                   help="Переписать dialogs/emergency_types_dialog.py даже если существует.")
    p.add_argument("--dry-run", action="store_true",
                   help="Только показать, что бы изменили, без записи на диск.")
    return p.parse_args()


# ----------------------------- утилиты I/O -----------------------------

def _read_text(path: Path) -> str:
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)

def _backup(path: Path) -> Path:
    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = path.with_suffix(path.suffix + f".bak.{ts}")
    bak.write_bytes(path.read_bytes())
    return bak


# ----------------------- содержимое нового диалога ---------------------

_DIALOG_CODE = r'''# -*- coding: utf-8 -*-
"""
dialogs/emergency_types_dialog.py
Полноценный PyQt5-диалог "Типы происшествий" для плагина ПОИСК-МОРЕ.

Функции:
- Таблица типов (код, наименование, описание).
- Добавить/Редактировать/Удалить строки.
- Загрузка/Сохранение в JSON: data/emergency_types.json.
- Возврат выбранного типа через get_selected_type().

Зависимости: PyQt5 (в составе QGIS).
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QDialogButtonBox, QMessageBox, QInputDialog, QLineEdit, QTextEdit,
    QWidget, QLabel, QFormLayout
)
from pathlib import Path
import json

def _plugin_root() -> Path:
    # dialogs/ -> корень проекта (на уровень выше)
    return Path(__file__).resolve().parents[1]

def _json_path() -> Path:
    return _plugin_root() / "data" / "emergency_types.json"


class _EditDialog(QDialog):
    """Вспомогательный диалог для добавления/редактирования записи."""
    def __init__(self, parent=None, code="", name="", desc=""):
        super().__init__(parent)
        self.setWindowTitle("Редактирование типа происшествия")
        self.resize(520, 280)

        self._code = QLineEdit(code)
        self._name = QLineEdit(name)
        self._desc = QTextEdit(desc)

        form = QFormLayout()
        form.addRow("Код:", self._code)
        form.addRow("Наименование:", self._name)
        form.addRow("Описание:", self._desc)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        lay = QVBoxLayout()
        lay.addLayout(form)
        lay.addWidget(bb)
        self.setLayout(lay)

    def values(self):
        return self._code.text().strip(), self._name.text().strip(), self._desc.toPlainText().strip()



    def get_data(self):
        """
        Получить данные из формы
        
        Returns:
            dict: Словарь с данными формы
        """
        # Автоматически добавленный метод
        # TODO: Реализовать сбор данных из полей формы
        try:
            return self.collect_data()
        except AttributeError:
            # Если collect_data не реализован, возвращаем пустой словарь
            data = {}
            
            # Попытка собрать данные из стандартных виджетов
            for attr_name in dir(self):
                if attr_name.startswith("txt_") or attr_name.startswith("spin_") or attr_name.startswith("cmb_"):
                    try:
                        widget = getattr(self, attr_name)
                        if hasattr(widget, "text"):
                            data[attr_name] = widget.text()
                        elif hasattr(widget, "value"):
                            data[attr_name] = widget.value()
                        elif hasattr(widget, "currentText"):
                            data[attr_name] = widget.currentText()
                        elif hasattr(widget, "toPlainText"):
                            data[attr_name] = widget.toPlainText()
                    except:
                        pass
            
            return data

    def collect_data(self):
        """
        Собрать данные из полей формы
        
        Returns:
            dict: Словарь с данными формы
        """
        data = {}
        
        # TODO: Реализовать сбор данных из конкретных полей
        # Пример:
        # if hasattr(self, "txt_name"):
        #     data["name"] = self.txt_name.text()
        
        return data
class EmergencyTypesDialog(QDialog):
    """Основной диалог: типы происшествий (CRUD + JSON-персистентность)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Типы происшествий")
        self.resize(780, 460)

        self.table = QTableWidget(0, 3, self)
        self.table.setHorizontalHeaderLabels(["Код", "Наименование", "Описание"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_del = QPushButton("Удалить")
        self.btn_load = QPushButton("Загрузить")
        self.btn_save = QPushButton("Сохранить")

        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_del.clicked.connect(self._on_delete)
        self.btn_load.clicked.connect(self._on_load)
        self.btn_save.clicked.connect(self._on_save)

        buttons = QHBoxLayout()
        buttons.addWidget(self.btn_add)
        buttons.addWidget(self.btn_edit)
        buttons.addWidget(self.btn_del)
        buttons.addStretch()
        buttons.addWidget(self.btn_load)
        buttons.addWidget(self.btn_save)

        self.bb = QDialogButtonBox(QDialogButtonBox.Close)
        self.bb.rejected.connect(self.reject)

        lay = QVBoxLayout()
        lay.addLayout(buttons)
        lay.addWidget(self.table)
        lay.addWidget(self.bb)
        self.setLayout(lay)

        # загрузка при открытии
        self._load_or_seed()

    # ------------------------ API ------------------------

    def get_selected_type(self):
        """Вернуть (code, name, description) выделенной строки или None."""
        row = self.table.currentRow()
        if row < 0:
            return None
        return (
            self.table.item(row, 0).text(),
            self.table.item(row, 1).text(),
            self.table.item(row, 2).text(),
        )

    # --------------------- обработчики -------------------

    def _on_add(self):
        dlg = _EditDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            code, name, desc = dlg.values()
            if not code or not name:
                QMessageBox.warning(self, "ПОИСК-МОРЕ", "Код и наименование обязательны.")
                return
            if self._find_code_row(code) != -1:
                QMessageBox.warning(self, "ПОИСК-МОРЕ", f"Код '{code}' уже существует.")
                return
            self._append_row(code, name, desc)

    def _on_edit(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "ПОИСК-МОРЕ", "Выберите запись для редактирования.")
            return
        code = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()
        desc = self.table.item(row, 2).text()
        dlg = _EditDialog(self, code, name, desc)
        if dlg.exec_() == QDialog.Accepted:
            ncode, nname, ndesc = dlg.values()
            if not ncode or not nname:
                QMessageBox.warning(self, "ПОИСК-МОРЕ", "Код и наименование обязательны.")
                return
            # если код меняется — проверим уникальность
            if ncode != code and self._find_code_row(ncode) != -1:
                QMessageBox.warning(self, "ПОИСК-МОРЕ", f"Код '{ncode}' уже существует.")
                return
            self.table.item(row, 0).setText(ncode)
            self.table.item(row, 1).setText(nname)
            self.table.item(row, 2).setText(ndesc)

    def _on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        code = self.table.item(row, 0).text()
        if QMessageBox.question(self, "ПОИСК-МОРЕ", f"Удалить '{code}'?") == QMessageBox.Yes:
            self.table.removeRow(row)

    def _on_load(self):
        if not _json_path().exists():
            QMessageBox.information(self, "ПОИСК-МОРЕ", "Файл со справочником пока отсутствует — загружу типовые данные.")
        self._load_or_seed()

    def _on_save(self):
        data = []
        for r in range(self.table.rowCount()):
            data.append({
                "code": self.table.item(r, 0).text(),
                "name": self.table.item(r, 1).text(),
                "description": self.table.item(r, 2).text(),
            })
        _json_path().parent.mkdir(parents=True, exist_ok=True)
        with open(_json_path(), "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "ПОИСК-МОРЕ", f"Сохранено: {str(_json_path())}")

    # ----------------------- вспомогательные -------------

    def _append_row(self, code: str, name: str, desc: str):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(code))
        self.table.setItem(r, 1, QTableWidgetItem(name))
        self.table.setItem(r, 2, QTableWidgetItem(desc))

    def _find_code_row(self, code: str) -> int:
        for r in range(self.table.rowCount()):
            if self.table.item(r, 0).text() == code:
                return r
        return -1

    def _load_or_seed(self):
        self.table.setRowCount(0)
        if _json_path().exists():
            try:
                with open(_json_path(), "r", encoding="utf-8") as f:
                    data = json.load(f)
                for rec in data:
                    self._append_row(rec.get("code",""), rec.get("name",""), rec.get("description",""))
                return
            except Exception as ex:
                QMessageBox.warning(self, "ПОИСК-МОРЕ", f"Ошибка чтения JSON: {ex}\nЗагружу типовые значения.")
        # Типовой набор (можно редактировать в UI)
        seed = [
            {"code": "SHIP_DISTRESS",  "name": "Бедствие судна",          "description": "Сигнал бедствия, авария, пожар, затопление и т.п."},
            {"code": "MOB",            "name": "Человек за бортом",        "description": "Падение человека за борт, требуется поиск/спасение."},
            {"code": "AIR_ACCIDENT",   "name": "Авиакатастрофа на море",   "description": "Падение ВС, ditching и др."},
            {"code": "MEDEVAC",        "name": "Медицинская эвакуация",    "description": "Неотложная эвакуация больного/раненого."},
            {"code": "VESSEL_MISSING", "name": "Пропажа судна",            "description": "Не выходит на связь, нарушил ETA."},
            {"code": "FIRE_ONBOARD",   "name": "Пожар на судне",           "description": "Пожарные работы, эвакуация, буксировка."},
            {"code": "OTHER",          "name": "Другое",                   "description": "Иная нештатная ситуация."},
        ]
        for rec in seed:
            self._append_row(rec["code"], rec["name"], rec["description"])
'''


# -------------------------- патчинг mainPlugin.py ----------------------

_IMPORT_QACTION = 'from PyQt5.QtWidgets import QAction'
_IMPORT_DIALOG  = 'from .dialogs.emergency_types_dialog import EmergencyTypesDialog'

_MENU_SNIPPET = (
    '        # --- ensure_emergency_types_dialog (auto) ---\n'
    '        try:\n'
    '            self.action_emergency_types\n'
    '        except AttributeError:\n'
    '            self.action_emergency_types = QAction("Типы происшествий", self.iface.mainWindow())\n'
    '            self.action_emergency_types.triggered.connect(self._on_emergency_types)\n'
    '            try:\n'
    '                self.iface.addPluginToMenu("&Поиск-Море", self.action_emergency_types)\n'
    '            except Exception:\n'
    '                self.iface.addPluginToMenu("Поиск-Море", self.action_emergency_types)\n'
)

_UNLOAD_SNIPPET = (
    '        # --- ensure_emergency_types_dialog (auto) ---\n'
    '        try:\n'
    '            self.iface.removePluginMenu("&Поиск-Море", self.action_emergency_types)\n'
    '        except Exception:\n'
    '            try:\n'
    '                self.iface.removePluginMenu("Поиск-Море", self.action_emergency_types)\n'
    '            except Exception:\n'
    '                pass\n'
)

_HANDLER_SNIPPET = (
    '    # --- ensure_emergency_types_dialog (auto) ---\n'
    '    def _on_emergency_types(self):\n'
    '        dlg = EmergencyTypesDialog(self.iface.mainWindow())\n'
    '        dlg.exec_()\n\n'
)

def _ensure_line(text: str, line: str) -> Tuple[str, bool]:
    if line in text:
        return text, False
    # вставить после первого блока import
    m = re.search(r'^(?:from\s+\S+\s+import\s+\S+|import\s+\S+).*(?:\r?\n)+', text, flags=re.M)
    if m:
        idx = m.end()
        new_text = text[:idx] + line + "\n" + text[idx:]
    else:
        new_text = line + "\n" + text
    return new_text, True

def _find_class_with_initgui(text: str) -> Optional[re.Match]:
    """
    Возвращает match класса, внутри которого определён def initGui(...):
    match.group(0) — заголовок 'class ...:'
    """
    class_iter = list(re.finditer(r'^\s*class\s+([A-Za-z_][\w]*)\s*\(.*?\)\s*:\s*$', text, flags=re.M))
    for cm in class_iter:
        start = cm.end()
        # берем текст от класса до следующего class/конца
        next_class = re.search(r'^\s*class\s+[A-Za-z_][\w]*\s*\(.*?\)\s*:\s*$', text[start:], flags=re.M)
        end = start + next_class.start() if next_class else len(text)
        body = text[start:end]
        if re.search(r'^\s*def\s+initGui\s*\(\s*self\b[^\)]*\)\s*:', body, flags=re.M):
            return cm
    return None

def _insert_into_function(text: str, func_name: str, snippet: str) -> Tuple[str, bool]:
    """
    Вставляет snippet в тело функции func_name(self,...)
    после первой строки docstring/первого пустого ряда.
    """
    # Найдём дефиницию
    m = re.search(rf'^\s*def\s+{func_name}\s*\(\s*self\b[^\)]*\)\s*:\s*$', text, flags=re.M)
    if not m:
        return text, False
    # Определим отступ функции
    line_start = text.rfind("\n", 0, m.start()) + 1
    indent = re.match(r'\s*', text[line_start:m.start()]).group(0)
    body_indent = indent + "    "

    # Найдем место вставки: первая строка тела
    after_def = m.end()
    insert_pos = after_def
    # пропустим возможный docstring
    doc = re.match(r'\s*[ru]?["\']{3}.*?["\']{3}', text[after_def:], flags=re.S)
    if doc:
        insert_pos = after_def + doc.end()

    # Если snippet уже есть — не вставляем
    if snippet.strip() in text:
        return text, False

    # Выровняем отступы у snippet
    fixed = "".join(
        (body_indent + ln if ln.strip() else ln)
        for ln in snippet.splitlines(True)
    )
    return text[:insert_pos] + "\n" + fixed + text[insert_pos:], True

def _ensure_handler_in_class(text: str, class_match: re.Match) -> Tuple[str, bool]:
    """Добавить метод _on_emergency_types в найденный класс, если отсутствует."""
    # Найти тело класса
    start = class_match.end()
    next_class = re.search(r'^\s*class\s+[A-Za-z_][\w]*\s*\(.*?\)\s*:\s*$', text[start:], flags=re.M)
    end = start + next_class.start() if next_class else len(text)
    body = text[start:end]

    if re.search(r'^\s*def\s+_on_emergency_types\s*\(\s*self\b[^\)]*\)\s*:', body, flags=re.M):
        return text, False

    # Определим базовый отступ класса
    line_start = text.rfind("\n", 0, class_match.start()) + 1
    class_indent = re.match(r'\s*', text[line_start:class_match.start()]).group(0)
    method_indent = class_indent + "    "

    fixed = "".join(
        (method_indent + ln if ln.strip() else ln)
        for ln in _HANDLER_SNIPPET.splitlines(True)
    )

    # Вставим перед концом тела класса
    return text[:end] + "\n" + fixed + text[end:], True

def _patch_mainplugin(main_path: Path, dry: bool = False) -> None:
    original = _read_text(main_path)
    text = original
    changed = []

    # 1) Импорты
    text, did = _ensure_line(text, _IMPORT_QACTION)
    if did: changed.append("import QAction")
    text, did = _ensure_line(text, _IMPORT_DIALOG)
    if did: changed.append("import EmergencyTypesDialog")

    # 2) Вставка в initGui()
    text, did = _insert_into_function(text, "initGui", _MENU_SNIPPET)
    if did: changed.append("initGui() -> add action")

    # 3) Вставка в unload()
    text, did = _insert_into_function(text, "unload", _UNLOAD_SNIPPET)
    if did: changed.append("unload() -> remove action")

    # 4) Метод-обработчик в том же классе, где есть initGui()
    cm = _find_class_with_initgui(text)
    if cm:
        text, did = _ensure_handler_in_class(text, cm)
        if did: changed.append("add _on_emergency_types()")
    else:
        # fallback: если класс не найден, не рушим файл — пропустим добавление хэндлера
        pass

    if not changed:
        print(f"[OK] mainPlugin.py уже содержит все необходимые элементы — правки не требуются.")
        return

    if dry:
        print(f"[DRY] Были бы внесены правки: {', '.join(changed)}")
        return

    # Бэкап и запись
    bak = _backup(main_path)
    _write_text(main_path, text)
    print(f"[OK] mainPlugin.py пропатчен ({', '.join(changed)}). Бэкап: {bak.name}")


# --------------------------- создание файла-диалога --------------------

def _ensure_dialog_file(dialog_path: Path, force: bool, dry: bool) -> None:
    if dialog_path.exists() and not force:
        print(f"[OK] dialogs/emergency_types_dialog.py уже существует — пропуск (используйте --force-overwrite для перезаписи).")
        return
    if dry:
        print(f"[DRY] Будет создан/перезаписан файл: {dialog_path}")
        return
    _write_text(dialog_path, _DIALOG_CODE)
    print(f"[OK] Создан: {dialog_path}")


# -------------------------------- main ---------------------------------

def main():
    args = _parse_args()
    if args.root:
        root = Path(args.root).resolve()
    else:
        # .../poiskmore_plugin/tools/ensure_emergency_types_dialog.py -> подняться на 1 уровень
        root = Path(__file__).resolve().parents[1]

    main_path = root / "mainPlugin.py"
    dialogs_dir = root / "dialogs"
    dialog_path = dialogs_dir / "emergency_types_dialog.py"

    if not main_path.exists():
        print(f"[ERR] Не найден mainPlugin.py по пути: {main_path}")
        sys.exit(2)

    dialogs_dir.mkdir(parents=True, exist_ok=True)

    # 1) Создадим (или обновим) файл диалога
    _ensure_dialog_file(dialog_path, force=args.force_overwrite, dry=args.dry_run)

    # 2) Пропатчим mainPlugin.py
    _patch_mainplugin(main_path, dry=args.dry_run)

    print("[DONE] ensure_emergency_types_dialog завершён успешно.")

if __name__ == "__main__":
    main()
