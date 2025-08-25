# -*- coding: utf-8 -*-
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
