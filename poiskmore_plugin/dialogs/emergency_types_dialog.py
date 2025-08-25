# -*- coding: utf-8 -*-
"""
Диалог "Типы происшествий" для плагина Поиск-Море (QGIS).
Функциональность:
- просмотр/добавление/редактирование/удаление типов происшествий;
- валидация (уникальный код, обязательные поля);
- импорт/экспорт в JSON;
- сохранение по умолчанию в poiskmore_plugin/data/emergency_types.json.

Не требует внешней БД: хранит справочник в JSON (можно позже заменить на db/ при необходимости).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QAbstractItemView, QWidget,
    QLabel, QLineEdit, QSpinBox, QCheckBox, QFormLayout
)


# -----------------------------
# Модель данных
# -----------------------------

@dataclass
class EmergencyType:
    code: str
    name: str
    priority: int = 3
    is_medical: bool = False

    @staticmethod
    def from_dict(d: Dict) -> "EmergencyType":
        return EmergencyType(
            code=str(d.get("code", "")).strip(),
            name=str(d.get("name", "")).strip(),
            priority=int(d.get("priority", 3)),
            is_medical=bool(d.get("is_medical", False)),
        )


# -----------------------------
# Диалог редактирования записи
# -----------------------------

class _EditEmergencyTypeDialog(QDialog):
    def __init__(self, parent: QWidget = None, existing_codes: Optional[List[str]] = None, item: Optional[EmergencyType] = None):
        super().__init__(parent)
        self.setWindowTitle("Тип происшествия")
        self._existing_codes = set((existing_codes or []))
        self._original_code = item.code if item else None

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.edit_code = QLineEdit(item.code if item else "")
        self.edit_name = QLineEdit(item.name if item else "")
        self.spin_priority = QSpinBox()
        self.spin_priority.setRange(1, 9)
        self.spin_priority.setValue(item.priority if item else 3)
        self.chk_medical = QCheckBox("Медицинский")
        self.chk_medical.setChecked(item.is_medical if item else False)

        form.addRow("Код:", self.edit_code)
        form.addRow("Наименование:", self.edit_name)
        form.addRow("Приоритет (1..9):", self.spin_priority)
        form.addRow("", self.chk_medical)
        layout.addLayout(form)

        btns = QHBoxLayout()
        self.btn_ok = QPushButton("OK")
        self.btn_cancel = QPushButton("Отмена")
        btns.addStretch()
        btns.addWidget(self.btn_ok)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        self.btn_ok.clicked.connect(self._on_ok)
        self.btn_cancel.clicked.connect(self.reject)

    def _on_ok(self):
        code = self.edit_code.text().strip()
        name = self.edit_name.text().strip()
        if not code or not name:
            QMessageBox.warning(self, "Валидация", "Код и наименование обязательны.")
            return
        # проверка уникальности кода (разрешаем старый код при редактировании)
        if (code in self._existing_codes) and (code != self._original_code):
            QMessageBox.warning(self, "Валидация", f"Код '{code}' уже существует.")
            return
        self.accept()

    def result_item(self) -> EmergencyType:
        return EmergencyType(
            code=self.edit_code.text().strip(),
            name=self.edit_name.text().strip(),
            priority=self.spin_priority.value(),
            is_medical=self.chk_medical.isChecked(),
        )


# -----------------------------
# Основной диалог
# -----------------------------

class EmergencyTypesDialog(QDialog):
    """Cправочник типов происшествий с JSON-хранилищем."""

    FILE_NAME = "emergency_types.json"

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Типы происшествий")
        self.resize(720, 480)

        # Путь к JSON в data/
        self._json_path = self._default_json_path()

        self._items: List[EmergencyType] = []
        self._init_ui()
        self._load_or_seed()

    # ---- UI ----

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels(["Код", "Наименование", "Приоритет", "Мед."])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        btns = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Редактировать")
        self.btn_del = QPushButton("Удалить")
        btns.addWidget(self.btn_add)
        btns.addWidget(self.btn_edit)
        btns.addWidget(self.btn_del)
        btns.addStretch()

        self.btn_import = QPushButton("Импорт...")
        self.btn_export = QPushButton("Экспорт...")
        self.btn_save = QPushButton("Сохранить")
        self.btn_close = QPushButton("Закрыть")
        btns.addWidget(self.btn_import)
        btns.addWidget(self.btn_export)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_close)
        layout.addLayout(btns)

        self.btn_add.clicked.connect(self._on_add)
        self.btn_edit.clicked.connect(self._on_edit)
        self.btn_del.clicked.connect(self._on_delete)
        self.btn_import.clicked.connect(self._on_import)
        self.btn_export.clicked.connect(self._on_export)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_close.clicked.connect(self.close)

    # ---- Данные ----

    def _default_json_path(self) -> str:
        # .../poiskmore_plugin/dialogs/ -> .../poiskmore_plugin/data/emergency_types.json
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        data_dir = os.path.join(base, "data")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, self.FILE_NAME)

    def _seed_defaults(self) -> List[EmergencyType]:
        # Базовый набор (можете расширить при необходимости)
        return [
            EmergencyType("SHIP_DISTRESS", "Бедствие судна", priority=2, is_medical=False),
            EmergencyType("MOB", "Человек за бортом", priority=1, is_medical=False),
            EmergencyType("AIRCRAFT_AT_SEA", "Авиакатастрофа на море", priority=1, is_medical=False),
            EmergencyType("MEDEVAC", "Медицинская эвакуация", priority=1, is_medical=True),
            EmergencyType("MISSING_VESSEL", "Пропажа судна", priority=3, is_medical=False),
            EmergencyType("SHIP_FIRE", "Пожар на судне", priority=2, is_medical=False),
        ]

    def _load_or_seed(self):
        if os.path.isfile(self._json_path):
            try:
                self._items = self._load_json(self._json_path)
            except Exception as ex:
                QMessageBox.warning(self, "Загрузка", f"Не удалось загрузить JSON:\n{ex}\nБудут применены значения по умолчанию.")
                self._items = self._seed_defaults()
        else:
            self._items = self._seed_defaults()
        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(len(self._items))
        for row, it in enumerate(sorted(self._items, key=lambda x: (x.priority, x.code))):
            self._set_row(row, it)

    def _set_row(self, row: int, it: EmergencyType):
        self.table.setItem(row, 0, QTableWidgetItem(it.code))
        self.table.setItem(row, 1, QTableWidgetItem(it.name))
        self.table.setItem(row, 2, QTableWidgetItem(str(it.priority)))
        self.table.setItem(row, 3, QTableWidgetItem("Да" if it.is_medical else "Нет"))
        # выравнивание
        for col in range(4):
            item = self.table.item(row, col)
            if item:
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                if col in (2, 3):
                    item.setTextAlignment(Qt.AlignCenter)

    def _current_index(self) -> Optional[int]:
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return None
        return sel[0].row()

    def _codes_set(self) -> List[str]:
        return [it.code for it in self._items]

    # ---- Обработчики ----

    def _on_add(self):
        dlg = _EditEmergencyTypeDialog(self, existing_codes=self._codes_set(), item=None)
        if dlg.exec_() == QDialog.Accepted:
            self._items.append(dlg.result_item())
            self._refresh_table()

    def _on_edit(self):
        idx = self._current_index()
        if idx is None:
            QMessageBox.information(self, "Редактирование", "Выберите запись.")
            return
        # найдем элемент по отображаемой сортировке
        # проще — извлечь код из таблицы и найти в self._items
        code = self.table.item(idx, 0).text()
        target = next((x for x in self._items if x.code == code), None)
        if target is None:
            QMessageBox.warning(self, "Редактирование", "Не удалось найти выбранную запись.")
            return
        dlg = _EditEmergencyTypeDialog(self, existing_codes=self._codes_set(), item=target)
        if dlg.exec_() == QDialog.Accepted:
            new_item = dlg.result_item()
            # заменить по коду (сохраним порядок)
            for i, x in enumerate(self._items):
                if x.code == code:
                    self._items[i] = new_item
                    break
            self._refresh_table()

    def _on_delete(self):
        idx = self._current_index()
        if idx is None:
            QMessageBox.information(self, "Удаление", "Выберите запись.")
            return
        code = self.table.item(idx, 0).text()
        if QMessageBox.question(self, "Удаление", f"Удалить тип '{code}'?") == QMessageBox.Yes:
            self._items = [x for x in self._items if x.code != code]
            self._refresh_table()

    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Импорт типов (JSON)", "", "JSON (*.json)")
        if not path:
            return
        try:
            items = self._load_json(path)
            # проверим уникальность кодов
            codes = [it.code for it in items]
            if len(codes) != len(set(codes)):
                raise ValueError("Дубликаты кодов в импортируемом файле.")
            self._items = items
            self._refresh_table()
            QMessageBox.information(self, "Импорт", f"Импортировано записей: {len(items)}.")
        except Exception as ex:
            QMessageBox.warning(self, "Импорт", f"Ошибка импорта:\n{ex}")

    def _on_export(self):
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт типов (JSON)", "emergency_types.json", "JSON (*.json)")
        if not path:
            return
        try:
            self._save_json(path, self._items)
            QMessageBox.information(self, "Экспорт", f"Сохранено: {path}")
        except Exception as ex:
            QMessageBox.warning(self, "Экспорт", f"Ошибка экспорта:\n{ex}")

    def _on_save(self):
        try:
            self._save_json(self._json_path, self._items)
            QMessageBox.information(self, "Сохранение", f"Справочник сохранён:\n{self._json_path}")
        except Exception as ex:
            QMessageBox.warning(self, "Сохранение", f"Ошибка сохранения:\n{ex}")

    # ---- JSON I/O ----

    @staticmethod
    def _load_json(path: str) -> List[EmergencyType]:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            raise ValueError("Ожидается список объектов.")
        items = [EmergencyType.from_dict(x) for x in raw]
        # валидация на пустые поля
        for it in items:
            if not it.code or not it.name:
                raise ValueError("Пустые 'code' или 'name' в данных.")
        # уникальность кодов
        codes = [it.code for it in items]
        if len(codes) != len(set(codes)):
            raise ValueError("Коды должны быть уникальны.")
        return items

    @staticmethod
    def _save_json(path: str, items: List[EmergencyType]):
        data = [asdict(x) for x in items]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
