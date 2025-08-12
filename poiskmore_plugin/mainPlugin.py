import os

from qgis.PyQt.QtWidgets import QAction, QMenu, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QSpinBox, QDoubleSpinBox, QLineEdit, QPushButton, QFileDialog, QMessageBox, QInputDialog
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import QUrl
from qgis.core import Qgis, QgsApplication, QgsProject, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer
from qgis.gui import QgsMapToolEmitPoint

# Используем абсолютные импорты, чтобы QGIS корректно находил модули
# диалогов даже при нестандартной загрузке плагина.
from poiskmore_plugin.dialogs.dialog_registration import RegistrationDialog
from poiskmore_plugin.dialogs.dialog_weather import WeatherDialog
from poiskmore_plugin.dialogs.dialog_searcharea import SearchAreaDialog
from poiskmore_plugin.dialogs.dialog_sitrep import SitrepDialog
from poiskmore_plugin.dialogs.dialog_asw import AswDialog
from poiskmore_plugin.dialogs.dialog_twc import TwcDialog
from poiskmore_plugin.dialogs.dialog_operation_edit import OperationEditDialog
from poiskmore_plugin.dialogs.dialog_incident_object import IncidentObjectDialog
from poiskmore_plugin.dialogs.dialog_search_params import SearchParamsDialog
from poiskmore_plugin.dialogs.dialog_search_object import SearchObjectDialog

from .alg.alg_datum import calculate_datum_points, add_datum_layer
from .alg.alg_zone import create_search_area, add_search_layer
from .alg.alg_distant_points import distant_points_calculation
from .alg.alg_manual_area import manual_area, ManualAreaTool

class PoiskMorePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.menu = None
        self._menu_bar = None
        self.actions = {}
        self.plugin_dir = os.path.dirname(__file__)
        self.current_operation = None
        self.operations = []
        self._map_tool = None

    def initGui(self):
        self.menu = QMenu("Поиск-Море", self.iface.mainWindow())
        self._menu_bar = self.iface.mainWindow().menuBar()
        self._menu_bar.addMenu(self.menu)

        search_menu = QMenu("Поиск", self.menu)
        self.menu.addMenu(search_menu)
        self.add_action(search_menu, "Новый аварийный случай", self.new_emergency_case)
        self.add_action(search_menu, "Повторный поиск", self.repeat_search)
        self.add_action(search_menu, "Редактировать информацию", self.edit_info)
        self.add_action(search_menu, "Удалить текущую операцию", self.delete_operation)
        self.add_action(search_menu, "Закрыть поиск", self.close_search)
        self.add_action(search_menu, "Дела и поисковые операции", self.operations_list)
        self.add_action(search_menu, "Копировать операцию", self.copy_operation)
        self.add_action(search_menu, "Выход", lambda: QgsApplication.quit())

        datum_menu = QMenu("Исходный пункт", self.menu)
        self.menu.addMenu(datum_menu)
        self.add_action(datum_menu, "Вычислить исходные пункты", self.calculate_datum_points)
        self.add_action(datum_menu, "Исходная линия", self.datum_line)
        self.add_action(datum_menu, "Вычислить единственный исходный пункт", self.single_datum_point)

        area_menu = QMenu("Район", self.menu)
        self.menu.addMenu(area_menu)
        create_area_submenu = QMenu("Создать район", area_menu)
        area_menu.addMenu(create_area_submenu)
        self.add_action(create_area_submenu, "Поиск от двух исходных пунктов", self.search_two_points)
        self.add_action(create_area_submenu, "Поиск вдоль исходной линии", self.search_along_line)
        self.add_action(create_area_submenu, "Далеко разнесённые исходные пункты", self.search_distant_points)
        self.add_action(create_area_submenu, "Ручное построение", self.manual_area)
        self.add_action(create_area_submenu, "Поиск от одной исходной точки", self.search_one_point)

        docs_menu = QMenu("Документы", self.menu)
        self.menu.addMenu(docs_menu)
        self.add_action(docs_menu, "Стандартные формы", self.standard_forms)
        self.add_action(docs_menu, "План поиска", self.search_plan)
        self.add_action(docs_menu, "Планшет ГМСКЦ", self.gmskc_tablet)

        service_menu = QMenu("Сервис", self.menu)
        self.menu.addMenu(service_menu)
        self.add_action(service_menu, "Характер аварийной ситуации", self.incident_type)

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
        dialog = RegistrationDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.current_operation = dialog.get_data()
            self.operations.append(self.current_operation)
            self.iface.messageBar().pushMessage("Новый аварийный случай создан", Qgis.Success)

    def repeat_search(self):
        if not self.operations:
            QMessageBox.warning(self.iface.mainWindow(), "Ошибка", "Нет предыдущих операций")
            return
        dialog = QDialog()
        layout = QVBoxLayout()
        table = QTableWidget(len(self.operations), 1)
        for i, op in enumerate(self.operations):
            table.setItem(i, 0, QTableWidgetItem(str(op)))
        layout.addWidget(table)
        dialog.setLayout(layout)
        if dialog.exec_() == QDialog.Accepted:
            selected = table.currentRow()
            self.current_operation = self.operations[selected].copy()
            self.iface.messageBar().pushMessage("Операция повторена", Qgis.Success)

    def edit_info(self):
        if not self.current_operation:
            QMessageBox.warning(self.iface.mainWindow(), "Ошибка", "Нет текущей операции")
            return
        dialog = OperationEditDialog(self.current_operation)
        if dialog.exec_() == QDialog.Accepted:
            self.current_operation = dialog.get_data()
            self.iface.messageBar().pushMessage("Информация обновлена", Qgis.Success)

    def delete_operation(self):
        if not self.current_operation:
            QMessageBox.warning(self.iface.mainWindow(), "Ошибка", "Нет текущей операции")
            return
        reply = QMessageBox.question(self.iface.mainWindow(), "Подтверждение", "Удалить операцию?")
        if reply == QMessageBox.Yes:
            self.operations.remove(self.current_operation)
            self.current_operation = None
            self.iface.messageBar().pushMessage("Операция удалена", Qgis.Info)

    def close_search(self):
        if not self.current_operation:
            QMessageBox.warning(self.iface.mainWindow(), "Ошибка", "Нет текущей операции")
            return
        reply = QMessageBox.question(self.iface.mainWindow(), "Подтверждение", "Закрыть поиск?")
        if reply == QMessageBox.Yes:
            self.current_operation['status'] = 'closed'
            self.iface.messageBar().pushMessage("Поиск закрыт", Qgis.Success)

    def operations_list(self):
        dialog = QDialog()
        layout = QVBoxLayout()
        table = QTableWidget(len(self.operations), 1)
        for i, op in enumerate(self.operations):
            table.setItem(i, 0, QTableWidgetItem(str(op)))
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()

    def copy_operation(self):
        if not self.current_operation:
            QMessageBox.warning(self.iface.mainWindow(), "Ошибка", "Нет текущей операции")
            return
        new_op = self.current_operation.copy()
        new_op['id'] = len(self.operations) + 1
        self.operations.append(new_op)
        self.iface.messageBar().pushMessage("Операция скопирована", Qgis.Success)

    def calculate_datum_points(self):
        dialog = QDialog()
        layout = QVBoxLayout()
        lkp_input = QLineEdit("30.0,60.0")
        wind_speed = QDoubleSpinBox(); wind_speed.setValue(10.0)
        wind_dir = QSpinBox(); wind_dir.setValue(0)
        current_speed = QDoubleSpinBox(); current_speed.setValue(2.0)
        current_dir = QSpinBox(); current_dir.setValue(90)
        time_hours = QDoubleSpinBox(); time_hours.setValue(3.0)
        layout.addWidget(QLabel("LKP (lon,lat):"))
        layout.addWidget(lkp_input)
        layout.addWidget(QLabel("Wind speed:"))
        layout.addWidget(wind_speed)
        layout.addWidget(QLabel("Wind dir:"))
        layout.addWidget(wind_dir)
        layout.addWidget(QLabel("Current speed:"))
        layout.addWidget(current_speed)
        layout.addWidget(QLabel("Current dir:"))
        layout.addWidget(current_dir)
        layout.addWidget(QLabel("Time (hours):"))
        layout.addWidget(time_hours)
        btn = QPushButton("Calculate")
        btn.clicked.connect(lambda: self.do_calculate_datum_points(dialog, lkp_input.text(), wind_speed.value(), wind_dir.value(), current_speed.value(), current_dir.value(), time_hours.value()))
        layout.addWidget(btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def do_calculate_datum_points(self, dialog, lkp_str, wind_speed, wind_dir, current_speed, current_dir, time_hours):
        try:
            lon, lat = map(lambda s: float(s.strip()), lkp_str.split(','))
            lkp = QgsPointXY(lon, lat)
            params = {'lkp': lkp, 'wind_speed': wind_speed, 'wind_dir': wind_dir, 'current_speed': current_speed, 'current_dir': current_dir, 'time_hours': time_hours}
            result = calculate_datum_points(self.iface, params)
            if result:
                add_datum_layer(result)
                dialog.accept()
        except Exception as e:
            QMessageBox.warning(dialog, "Ошибка", f"Неверные данные: {str(e)}")

    def datum_line(self):
        self.datum_points = []
        self._map_tool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self._map_tool.canvasClicked.connect(self.add_datum_point)
        self.iface.mapCanvas().setMapTool(self._map_tool)
        self.iface.messageBar().pushMessage("Выберите две точки для линии", Qgis.Info)

    def add_datum_point(self, point):
        self.datum_points.append(point)
        if len(self.datum_points) == 2:
            line = QgsGeometry.fromPolylineXY(self.datum_points)
            layer = QgsVectorLayer("LineString?crs=epsg:4326", "Исходная линия", "memory")
            feat = QgsFeature()
            feat.setGeometry(line)
            layer.dataProvider().addFeature(feat)
            layer.updateExtents()
            QgsProject.instance().addMapLayer(layer)
            self.iface.mapCanvas().unsetMapTool(self._map_tool)
            self._map_tool = None
            self.iface.messageBar().pushMessage("Исходная линия создана", Qgis.Success)

    def single_datum_point(self):
        point = QgsPointXY(30.0, 60.0)
        layer = QgsVectorLayer("Point?crs=epsg:4326", "Единственный datum", "memory")
        feat = QgsFeature()
        feat.setGeometry(QgsGeometry.fromPointXY(point))
        layer.dataProvider().addFeature(feat)
        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)
        self.iface.messageBar().pushMessage("Единственный datum добавлен", Qgis.Success)

    def search_two_points(self):
        dialog = SearchParamsDialog()
        if dialog.exec_() == QDialog.Accepted:
            params = dialog.get_params()
            area = create_search_area(params, mode='two_points')
            self.add_search_result_layer(area)
            self.iface.messageBar().pushMessage("Район создан", Qgis.Success)

    def search_along_line(self):
        self.line_points = []
        self._map_tool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self._map_tool.canvasClicked.connect(self.add_line_point)
        self.iface.mapCanvas().setMapTool(self._map_tool)
        self.iface.messageBar().pushMessage("Выберите точки линии", Qgis.Info)

    def add_line_point(self, point):
        self.line_points.append(point)
        if len(self.line_points) == 2:
            line = QgsGeometry.fromPolylineXY(self.line_points)
            area = line.buffer(0.1, 5)
            self.add_search_result_layer(area)
            self.iface.mapCanvas().unsetMapTool(self._map_tool)
            self._map_tool = None
            self.iface.messageBar().pushMessage("Район вдоль линии создан", Qgis.Success)

    def search_distant_points(self):
        p1 = QgsPointXY(30.0, 60.0)
        p2 = QgsPointXY(31.0, 61.0)
        params = {'threshold': 50, 'radius': 0.5, 'width': 0.2}
        areas = distant_points_calculation(p1, p2, params)
        for area in areas:
            self.add_search_result_layer(area)
        self.iface.messageBar().pushMessage("Районы для distant points созданы", Qgis.Success)

    def manual_area(self):
        manual_area(self.iface)

    def search_one_point(self):
        point = QgsPointXY(30.0, 60.0)
        geom = QgsGeometry.fromPointXY(point).buffer(0.5, 20)
        self.add_search_result_layer(geom)
        self.iface.messageBar().pushMessage("Район от одной точки создан", Qgis.Success)

    def add_search_result_layer(self, geom):
        layer = QgsVectorLayer("Polygon?crs=epsg:4326", "Район поиска", "memory")
        feat = QgsFeature()
        feat.setGeometry(geom)
        layer.dataProvider().addFeature(feat)
        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)

    def standard_forms(self):
        forms = ["Form1", "Form2"]
        form, ok = QInputDialog.getItem(self.iface.mainWindow(), "Стандартные формы", "Выберите форму", forms, 0, False)
        if ok:
            QMessageBox.information(self.iface.mainWindow(), "Форма", f"Форма {form} открыта")

    def search_plan(self):
        dialog = QDialog()
        layout = QVBoxLayout()
        table = QTableWidget(5, 4)
        table.setHorizontalHeaderLabels(["SRU", "Район", "Время", "Статус"])
        layout.addWidget(table)
        dialog.setLayout(layout)
        if dialog.exec_() == QDialog.Accepted:
            # Generate plan
            self.iface.messageBar().pushMessage("План поиска сгенерирован", Qgis.Success)

    def gmskc_tablet(self):
        path, _ = QFileDialog.getOpenFileName(self.iface.mainWindow(), "Открыть планшет", "", "Word (*.docx)")
        if path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def incident_type(self):
        dialog = IncidentObjectDialog()
        dialog.exec_()

    def about_program(self):
        QMessageBox.about(self.iface.mainWindow(), "О программе", "Поиск-Море v1.0")

    def documentation(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.join(self.plugin_dir, 'docs/manual.pdf')))

    def unload(self):
        if self._menu_bar and self.menu:
            self._menu_bar.removeAction(self.menu.menuAction())
        if self.menu:
            self.menu.deleteLater()
        self.menu = None
        self._menu_bar = None
        self.actions.clear()