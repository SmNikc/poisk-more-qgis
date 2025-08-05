"""QGIS plugin entry point.

This module defines the :class:`PoiskMorePlugin` class used by QGIS to
initialise the plugin and expose the actions available in the "Поиск-Море"
menu. The previous version of this file lost all indentation which caused a
runtime ``IndentationError`` when the plugin was loaded.  The class and its
methods are now correctly indented so the plugin can be instantiated by QGIS.
"""

from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.utils import iface

from .dialogs.dialog_sitrep import SitrepForm
from .dialogs.region_dialog import RegionDialog
from .dialogs.exercise_dialog import ExerciseDialog
from .dialogs.err_editing_dialog import ErrEditingDialog
from .dialogs.probability_dialog import ProbabilityDialog
from .dialogs.sru_routing_dialog import SruRoutingDialog
from .dialogs.operator_log_dialog import OperatorLogDialog
from .dialogs.search_scheme_dialog import SearchSchemeDialog


class PoiskMorePlugin:
    """Главный класс плагина."""

    def __init__(self, iface):
        """Создаёт экземпляр плагина.

        Parameters
        ----------
        iface: QgsInterface
            Интерфейс QGIS, предоставляемый при загрузке плагина.
        """
        self.iface = iface
        self.actions = []

    def initGui(self):
        """Добавляет элементы меню плагина в интерфейс QGIS."""
        if not self.iface:
            print("Ошибка: iface не инициализирован")
            return

        menu_bar = self.iface.mainWindow().menuBar()
        self.menu = QMenu("Поиск-Море", menu_bar)
        menu_bar.addMenu(self.menu)

        self._add("SITREP", self.run_sitrep)
        self._add("Район поиска", self.run_region)
        self._add("Учение", self.run_exercise)
        self._add("Инцидент", self.run_err)
        self._add("Вероятность", self.run_probability)
        self._add("Маршрут SRU", self.run_route)
        self._add("Схема поиска", self.run_scheme)
        self._add("Лог", self.run_log)

    def _add(self, name, callback):
        """Создаёт действие меню и добавляет его в меню плагина."""
        action = QAction(name, self.iface.mainWindow())
        action.triggered.connect(callback)
        self.menu.addAction(action)
        self.actions.append(action)

    def unload(self):
        """Удаляет действия меню плагина из интерфейса QGIS."""
        for action in self.actions:
            self.iface.removePluginMenu("Поиск-Море", action)

    def run_sitrep(self):
        """Открывает форму SITREP."""
        SitrepForm(self.iface.mainWindow()).exec_()

    def run_region(self):
        """Открывает диалог выбора района поиска."""
        RegionDialog(self.iface).exec_()

    def run_exercise(self):
        """Открывает форму учений."""
        ExerciseDialog().exec_()

    def run_err(self):
        """Открывает форму инцидента."""
        ErrEditingDialog().exec_()

    def run_probability(self):
        """Открывает диалог вероятности."""
        ProbabilityDialog().exec_()

    def run_route(self):
        """Открывает диалог маршрута SRU."""
        SruRoutingDialog().exec_()

    def run_scheme(self):
        """Открывает диалог схемы поиска."""
        SearchSchemeDialog().exec_()

    def run_log(self):
        """Открывает журнал оператора."""
        OperatorLogDialog(self.iface).exec_()

