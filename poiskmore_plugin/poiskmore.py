# poiskmore.py (основная логика плагина, перемещена из mainPlugin.py для фикса IndentationError, полное меню, 100% C#)
import os
from PyQt5.QtWidgets import QAction, QMenu, QMessageBox
from qgis.core import QgsApplication, Qgis

# Импорт формы регистрации. Используем абсолютный путь, чтобы избежать
# ошибок ModuleNotFoundError при загрузке плагина в QGIS.
from poiskmore_plugin.dialogs.dialog_registration import RegistrationDialog

class PoiskMorePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.menu = None
        self.actions = {}
        self.plugin_dir = os.path.dirname(__file__)

    def initGui(self):
        self.menu = QMenu("Поиск-Море", self.iface.mainWindow())
        # Добавляем меню непосредственно в строку меню QGIS, чтобы оно
        # отображалось как отдельный пункт верхнего уровня. Использование
        # addPluginToMenu добавляет действия только в стандартное меню
        # "Плагины", поэтому пользователь не видел пункт "Поиск-Море".
        self.iface.mainWindow().menuBar().addMenu(self.menu)

        # Подменю "Поиск"
        search_menu = QMenu("Поиск", self.menu)
        self.menu.addMenu(search_menu)
        self.add_action(search_menu, "Новый аварийный случай", self.new_emergency_case)
        self.add_action(search_menu, "Повторный поиск", self.repeat_search)
        self.add_action(search_menu, "Редактировать информацию", self.edit_info)
        self.add_action(search_menu, "Удалить текущую операцию", self.delete_operation)
        self.add_action(search_menu, "Закрыть поиск", self.close_search)
        self.add_action(search_menu, "Дела и поисковые операции", self.operations_list)
        self.add_action(search_menu, "Копировать операцию", self.copy_operation)
        self.add_action(search_menu, "Выход", QgsApplication.quit)

        # Подменю "Исходный пункт"
        datum_menu = QMenu("Исходный пункт", self.menu)
        self.menu.addMenu(datum_menu)
        self.add_action(datum_menu, "Вычислить исходные пункты", self.calculate_datum_points)
        self.add_action(datum_menu, "Исходная линия", self.datum_line)
        self.add_action(datum_menu, "Вычислить единственный исходный пункт", self.single_datum_point)

        # Подменю "Район" с "Создать район"
        area_menu = QMenu("Район", self.menu)
        self.menu.addMenu(area_menu)
        create_area_submenu = QMenu("Создать район", area_menu)
        area_menu.addMenu(create_area_submenu)
        self.add_action(create_area_submenu, "Поиск от двух исходных пунктов", self.search_two_points)
        self.add_action(create_area_submenu, "Поиск вдоль исходной линии", self.search_along_line)
        self.add_action(create_area_submenu, "Далеко разнесённые исходные пункты", self.search_distant_points)
        self.add_action(create_area_submenu, "Ручное построение", self.manual_area)
        self.add_action(create_area_submenu, "Поиск от одной исходной точки", self.search_one_point)

        # Подменю "Документы"
        docs_menu = QMenu("Документы", self.menu)
        self.menu.addMenu(docs_menu)
        self.add_action(docs_menu, "Стандартные формы", self.standard_forms)
        self.add_action(docs_menu, "План поиска", self.search_plan)
        self.add_action(docs_menu, "Планшет ГМСКЦ", self.gmskc_tablet)

        # Подменю "Сервис"
        service_menu = QMenu("Сервис", self.menu)
        self.menu.addMenu(service_menu)
        self.add_action(service_menu, "Характер аварийной ситуации", self.incident_type)

        # Подменю "Помощь"
        help_menu = QMenu("Помощь", self.menu)
        self.menu.addMenu(help_menu)
        self.add_action(help_menu, "О программе", self.about_program)
        self.add_action(help_menu, "Документация", self.documentation)

    def add_action(self, parent, text, callback):
        action = QAction(text, self.iface.mainWindow())
        action.triggered.connect(callback)
        parent.addAction(action)
        self.actions[text] = action

    def new_emergency_case(self):
        dialog = RegistrationDialog(self.iface)
        dialog.exec_()
        self.iface.messageBar().pushMessage("Новый случай создан", level=Qgis.Success)

    def repeat_search(self):
        QMessageBox.information(self.iface.mainWindow(), "Повторный поиск", "Функционал не реализован")

    def edit_info(self):
        QMessageBox.information(self.iface.mainWindow(), "Редактировать информацию", "Функционал не реализован")

    def delete_operation(self):
        QMessageBox.information(self.iface.mainWindow(), "Удалить операцию", "Функционал не реализован")

    def close_search(self):
        QMessageBox.information(self.iface.mainWindow(), "Закрыть поиск", "Функционал не реализован")

    def operations_list(self):
        QMessageBox.information(self.iface.mainWindow(), "Дела и операции", "Функционал не реализован")

    def copy_operation(self):
        QMessageBox.information(self.iface.mainWindow(), "Копировать операцию", "Функционал не реализован")

    def calculate_datum_points(self):
        QMessageBox.information(self.iface.mainWindow(), "Вычислить исходные пункты", "Функционал не реализован")

    def datum_line(self):
        QMessageBox.information(self.iface.mainWindow(), "Исходная линия", "Функционал не реализован")

    def single_datum_point(self):
        QMessageBox.information(self.iface.mainWindow(), "Единственный исходный пункт", "Функционал не реализован")

    def search_two_points(self):
        QMessageBox.information(self.iface.mainWindow(), "Поиск от двух пунктов", "Функционал не реализован")

    def search_along_line(self):
        QMessageBox.information(self.iface.mainWindow(), "Поиск вдоль линии", "Функционал не реализован")

    def search_distant_points(self):
        QMessageBox.information(self.iface.mainWindow(), "Далеко разнесённые пункты", "Функционал не реализован")

    def manual_area(self):
        QMessageBox.information(self.iface.mainWindow(), "Ручное построение", "Функционал не реализован")

    def search_one_point(self):
        QMessageBox.information(self.iface.mainWindow(), "Поиск от одной точки", "Функционал не реализован")

    def standard_forms(self):
        QMessageBox.information(self.iface.mainWindow(), "Стандартные формы", "Функционал не реализован")

    def search_plan(self):
        QMessageBox.information(self.iface.mainWindow(), "План поиска", "Функционал не реализован")

    def gmskc_tablet(self):
        QMessageBox.information(self.iface.mainWindow(), "Планшет ГМСКЦ", "Функционал не реализован")

    def incident_type(self):
        QMessageBox.information(self.iface.mainWindow(), "Характер аварийной ситуации", "Функционал не реализован")

    def about_program(self):
        QMessageBox.about(self.iface.mainWindow(), "О программе", "Поиск-Море QGIS Plugin\nВерсия 1.0")

    def documentation(self):
        QMessageBox.information(self.iface.mainWindow(), "Документация", "Функционал не реализован")

    def unload(self):
        # Удаляем меню из строки меню при выгрузке плагина
        self.iface.mainWindow().menuBar().removeAction(self.menu.menuAction())
        self.menu.deleteLater()
        self.actions.clear()