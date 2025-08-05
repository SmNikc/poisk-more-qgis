"""QGIS plugin entry point.

This module defines the :class:`PoiskMorePlugin` class used by QGIS to
initialise the plugin and expose the actions available in the "Поиск-Море"
menu. The previous version of this file lost all indentation which caused a
runtime ``IndentationError`` when the plugin was loaded.  The class and its
methods are now correctly indented so the plugin can be instantiated by QGIS.
"""

from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.utils import iface

# Dialog modules are imported lazily inside the slot methods so that the plugin
# can be loaded even if optional components are missing.


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

        # Only the SITREP dialog is implemented at the moment.
        self._add("SITREP", self.run_sitrep)

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
        from .dialogs.dialog_sitrep import SitrepDialog

        SitrepDialog(self.iface.mainWindow()).exec_()

