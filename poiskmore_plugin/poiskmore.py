from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.utils import iface

from .dialogs.sitrep_dialog import SitrepDialog
from .dialogs.region_dialog import RegionDialog
from .dialogs.exercise_dialog import ExerciseDialog
from .dialogs.err_editing_dialog import ErrEditingDialog
from .dialogs.probability_dialog import ProbabilityDialog
from .dialogs.sru_routing_dialog import SruRoutingDialog
from .dialogs.operator_log_dialog import OperatorLogDialog
from .dialogs.search_scheme_dialog import SearchSchemeDialog


class PoiskMorePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.actions = []

    def initGui(self):
        if not self.iface:
            print("Ошибка: iface не инициализирован")
            return

        self.menu = QMenu("Поиск-Море", self.iface.mainWindow().menuBar())
        self.iface.mainWindow().menuBar().addMenu(self.menu)

        self._add("SITREP", self.run_sitrep)
        self._add("Район поиска", self.run_region)
        self._add("Учение", self.run_exercise)
        self._add("Инцидент", self.run_err)
        self._add("Вероятность", self.run_probability)
        self._add("Маршрут SRU", self.run_route)
        self._add("Схема поиска", self.run_scheme)
        self._add("Лог", self.run_log)

    def _add(self, name, callback):
        action = QAction(name, self.iface.mainWindow())
        action.triggered.connect(callback)
        self.menu.addAction(action)
        self.actions.append(action)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu("Поиск-Море", action)

    def run_sitrep(self):
        SitrepDialog(self.iface).exec_()

    def run_region(self):
        RegionDialog(self.iface, self.iface.mapCanvas()).exec_()

    def run_exercise(self):
        ExerciseDialog().exec_()

    def run_err(self):
        ErrEditingDialog().exec_()

    def run_probability(self):
        ProbabilityDialog().exec_()

    def run_route(self):
        SruRoutingDialog().exec_()

    def run_scheme(self):
        SearchSchemeDialog().exec_()

    def run_log(self):
        OperatorLogDialog(self.iface).exec_()