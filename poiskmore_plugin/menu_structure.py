# -*- coding: utf-8 -*-
"""
Модуль управления структурой меню плагина ПОИСК-МОРЕ
Соответствует документации и методике проведения поисково-спасательных операций
Версия 2.0.0
"""

from qgis.PyQt.QtCore import QObject, pyqtSignal, QSettings
from qgis.PyQt.QtGui import QIcon, QAction
from qgis.PyQt.QtWidgets import QMenu, QMessageBox, QToolBar
from typing import Dict, List, Optional, Callable
import os

class MenuManager(QObject):
    """
    Менеджер структуры меню плагина
    Управляет созданием, видимостью и состоянием всех элементов меню
    """
    
    # Сигналы для взаимодействия с другими компонентами
    operation_started = pyqtSignal(dict)  # Начата новая операция
    operation_closed = pyqtSignal()       # Операция закрыта
    menu_action_triggered = pyqtSignal(str)  # Вызвано действие меню
    
    def __init__(self, iface, plugin_dir):
        """
        Инициализация менеджера меню
        
        Args:
            iface: Интерфейс QGIS
            plugin_dir: Путь к директории плагина
        """
        super().__init__()
        self.iface = iface
        self.plugin_dir = plugin_dir
        self.icons_dir = os.path.join(plugin_dir, 'icons')
        
        # Хранилище для всех меню и действий
        self.menus = {}
        self.actions = {}
        self.toolbars = {}
        
        # Состояние операции
        self.operation_active = False
        self.operation_data = None
        self.user_authorized = False
        
        # Главное меню
        self.main_menu = None
        
    def create_menu_structure(self):
        """
        Создать полную структуру меню согласно документации
        """
        # Создаем главное меню
        self.main_menu = QMenu("ПОИСК-МОРЕ", self.iface.mainWindow().menuBar())
        self.iface.mainWindow().menuBar().addMenu(self.main_menu)
        
        # Создаем все разделы меню в правильном порядке
        self._create_search_menu()      # 1. Поиск
        self._create_service_menu()     # 2. Сервис
        self._create_datum_menu()       # 3. Исходный пункт
        self._create_area_menu()        # 4. Район
        self._create_documents_menu()   # 5. Документы
        self._create_help_menu()       # 6. Помощь
        
        # Создаем панель инструментов
        self._create_toolbar()
        
        # Устанавливаем начальное состояние элементов
        self._update_menu_state()
    
    def _create_search_menu(self):
        """
        Создать меню "Поиск" - главное меню для работы с операциями
        """
        search_menu = QMenu("Поиск", self.main_menu)
        search_menu.setObjectName("search_menu")
        self.menus['search'] = search_menu
        
        # 1. Новый аварийный случай
        action_new = QAction(
            self._get_icon('new_case.png'),
            "Новый аварийный случай",
            self.iface.mainWindow()
        )
        action_new.setShortcut("Ctrl+N")
        action_new.setStatusTip("Создать новый аварийный случай и начать операцию")
        action_new.triggered.connect(self._on_new_case)
        search_menu.addAction(action_new)
        self.actions['new_case'] = action_new
        
        # 2. Повторный поиск
        action_repeat = QAction(
            self._get_icon('repeat_search.png'),
            "Повторный поиск",
            self.iface.mainWindow()
        )
        action_repeat.setStatusTip("Начать повторный поиск по существующему делу")
        action_repeat.triggered.connect(self._on_repeat_search)
        action_repeat.setEnabled(False)  # Активируется при наличии закрытых дел
        search_menu.addAction(action_repeat)
        self.actions['repeat_search'] = action_repeat
        
        # 3. Дела и поисковые операции
        action_operations = QAction(
            self._get_icon('operations_list.png'),
            "Дела и поисковые операции",
            self.iface.mainWindow()
        )
        action_operations.setShortcut("Ctrl+O")
        action_operations.setStatusTip("Просмотр и управление делами и операциями")
        action_operations.triggered.connect(self._on_operations_list)
        search_menu.addAction(action_operations)
        self.actions['operations_list'] = action_operations
        
        search_menu.addSeparator()
        
        # 4. Редактировать информацию
        action_edit = QAction(
            self._get_icon('edit_info.png'),
            "Редактировать информацию",
            self.iface.mainWindow()
        )
        action_edit.setShortcut("Ctrl+E")
        action_edit.setStatusTip("Редактировать информацию текущей операции")
        action_edit.triggered.connect(self._on_edit_info)
        action_edit.setEnabled(False)  # Активно только при открытой операции
        search_menu.addAction(action_edit)
        self.actions['edit_info'] = action_edit
        
        search_menu.addSeparator()
        
        # 5. Закрыть поиск
        action_close = QAction(
            self._get_icon('close_search.png'),
            "Закрыть поиск",
            self.iface.mainWindow()
        )
        action_close.setStatusTip("Временно приостановить текущую операцию")
        action_close.triggered.connect(self._on_close_search)
        action_close.setEnabled(False)  # Активно только при открытой операции
        search_menu.addAction(action_close)
        self.actions['close_search'] = action_close
        
        # 6. Завершить поиск
        action_finish = QAction(
            self._get_icon('finish_search.png'),
            "Завершить поиск",
            self.iface.mainWindow()
        )
        action_finish.setStatusTip("Окончательно завершить операцию и архивировать дело")
        action_finish.triggered.connect(self._on_finish_search)
        action_finish.setEnabled(False)  # Активно только при открытой операции
        search_menu.addAction(action_finish)
        self.actions['finish_search'] = action_finish
        
        self.main_menu.addMenu(search_menu)
    
    # === ОБРАБОТЧИКИ МЕНЮ "ПОИСК" ===
    
    def _on_new_case(self):
        """Обработчик создания нового аварийного случая"""
        from .dialogs.new_case_dialog import NewCaseDialog
        
        dialog = NewCaseDialog(self.iface.mainWindow())
        if dialog.exec_():
            case_data = dialog.get_case_data()
            
            # Создаем новую операцию
            self.operation_data = case_data
            self.operation_active = True
            
            # Обновляем состояние меню
            self._update_menu_state()
            
            # Излучаем сигнал о начале операции
            self.operation_started.emit(case_data)
            
            # Показываем вкладку "Операция"
            self._show_operation_tab()
            
            QMessageBox.information(
                self.iface.mainWindow(),
                "Новая операция",
                f"Создан аварийный случай №{case_data.get('case_number', 'Н/Д')}"
            )
    
    def _on_repeat_search(self):
        """Обработчик повторного поиска"""
        from .dialogs.repeat_search_dialog import RepeatSearchDialog
        
        dialog = RepeatSearchDialog(self.iface.mainWindow())
        if dialog.exec_():
            case_id = dialog.get_selected_case_id()
            
            # Загружаем архивное дело для повторного поиска
            self._load_archived_case(case_id)
            
            QMessageBox.information(
                self.iface.mainWindow(),
                "Повторный поиск",
                f"Возобновлен поиск по делу №{case_id}"
            )
    
    def _on_operations_list(self):
        """Обработчик списка операций"""
        from .dialogs.operations_list_dialog import OperationsListDialog
        
        dialog = OperationsListDialog(self.iface.mainWindow())
        if dialog.exec_():
            operation_id = dialog.get_selected_operation_id()
            if operation_id:
                self._load_operation(operation_id)
    
    def _on_edit_info(self):
        """Обработчик редактирования информации"""
        if not self.operation_active:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Предупреждение",
                "Нет активной операции для редактирования"
            )
            return
        
        from .dialogs.edit_operation_dialog import EditOperationDialog
        
        dialog = EditOperationDialog(self.operation_data, self.iface.mainWindow())
        if dialog.exec_():
            self.operation_data = dialog.get_updated_data()
            self.menu_action_triggered.emit('operation_updated')
    
    def _on_close_search(self):
        """Обработчик закрытия поиска (приостановка)"""
        if not self.operation_active:
            return
        
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            "Закрыть поиск",
            "Вы уверены, что хотите временно приостановить операцию?\n"
            "Вы сможете возобновить её позже через 'Повторный поиск'.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Сохраняем состояние операции
            self._save_operation_state('suspended')
            
            # Деактивируем операцию
            self.operation_active = False
            self.operation_closed.emit()
            
            # Обновляем меню
            self._update_menu_state()
            
            QMessageBox.information(
                self.iface.mainWindow(),
                "Поиск приостановлен",
                f"Операция №{self.operation_data.get('case_number')} приостановлена"
            )
    
    def _on_finish_search(self):
        """Обработчик завершения поиска (архивирование)"""
        if not self.operation_active:
            return
        
        from .dialogs.finish_search_dialog import FinishSearchDialog
        
        dialog = FinishSearchDialog(self.operation_data, self.iface.mainWindow())
        if dialog.exec_():
            finish_data = dialog.get_finish_data()
            
            # Архивируем операцию
            self._archive_operation(finish_data)
            
            # Деактивируем операцию
            self.operation_active = False
            self.operation_closed.emit()
            
            # Обновляем меню
            self._update_menu_state()
            
            QMessageBox.information(
                self.iface.mainWindow(),
                "Поиск завершен",
                f"Операция №{self.operation_data.get('case_number')} завершена и архивирована"
            )
    
    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
    
    def _get_icon(self, icon_name):
        """
        Получить иконку из директории icons
        
        Args:
            icon_name: Имя файла иконки
            
        Returns:
            QIcon объект или пустая иконка если файл не найден
        """
        icon_path = os.path.join(self.icons_dir, icon_name)
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()
    
    def _update_menu_state(self):
        """
        Обновить состояние элементов меню в зависимости от состояния операции
        """
        # Элементы, требующие активной операции
        operation_required = [
            'edit_info', 'close_search', 'finish_search',
            'calculate_datum', 'datum_line', 'create_area',
            'manage_sru', 'standard_forms', 'search_plan'
        ]
        
        for action_name in operation_required:
            if action_name in self.actions:
                self.actions[action_name].setEnabled(self.operation_active)
        
        # Элементы, требующие авторизации
        if 'sync_contacts' in self.actions:
            self.actions['sync_contacts'].setEnabled(self.user_authorized)
        
        # Повторный поиск доступен при наличии архивных дел
        if 'repeat_search' in self.actions:
            has_archived = self._check_archived_cases()
            self.actions['repeat_search'].setEnabled(has_archived)
    
    def _check_archived_cases(self):
        """Проверить наличие архивных дел"""
        # Здесь должна быть проверка БД на наличие архивных дел
        from .utils.db_manager import DatabaseManager
        db = DatabaseManager()
        return db.has_archived_cases()
    
    def _show_operation_tab(self):
        """Показать вкладку операции"""
        # Этот метод будет реализован при интеграции с UI
        self.menu_action_triggered.emit('show_operation_tab')

    def _create_service_menu(self):
        """
        Создать меню 'Сервис' - настройки и авторизация.
        """
        service_menu = QMenu("Сервис", self.main_menu)
        service_menu.setObjectName("service_menu")
        self.menus['service'] = service_menu
        
        # 1. Характер аварийной ситуации
        action_emergency = QAction(
            self._get_icon('emergency_type.png'),
            "Характер аварийной ситуации",
            self.iface.mainWindow()
        )
        action_emergency.setStatusTip("Настройка типов аварийных ситуаций и их характеристик")
        action_emergency.triggered.connect(self._on_emergency_types)
        service_menu.addAction(action_emergency)
        self.actions['emergency_types'] = action_emergency
        
        # 2. Авторизация
        action_auth = QAction(
            self._get_icon('authorization.png'),
            "Авторизация",
            self.iface.mainWindow()
        )
        action_auth.setShortcut("Ctrl+L")
        action_auth.setStatusTip("Авторизация пользователя в системе")
        action_auth.triggered.connect(self._on_authorization)
        service_menu.addAction(action_auth)
        self.actions['authorization'] = action_auth
        
        # 3. Синхронизировать адресную книгу
        action_sync = QAction(
            self._get_icon('sync_contacts.png'),
            "Синхронизировать адресную книгу",
            self.iface.mainWindow()
        )
        action_sync.setStatusTip("Синхронизация контактов поисково-спасательных служб")
        action_sync.triggered.connect(self._on_sync_contacts)
        action_sync.setEnabled(False)  # Активно после авторизации
        service_menu.addAction(action_sync)
        self.actions['sync_contacts'] = action_sync

        self.main_menu.addMenu(service_menu)
    
    def _create_datum_menu(self):
        """
        Создать меню "Исходный пункт" - расчет исходных точек поиска
        """
        datum_menu = QMenu("Исходный пункт", self.main_menu)
        datum_menu.setObjectName("datum_menu")
        self.menus['datum'] = datum_menu
        
        # 1. Вычислить исходные пункты
        action_calculate = QAction(
            self._get_icon('calculate_datum.png'),
            "Вычислить исходные пункты",
            self.iface.mainWindow()
        )
        action_calculate.setShortcut("Ctrl+D")
        action_calculate.setStatusTip("Расчет исходных пунктов с учетом дрейфа")
        action_calculate.triggered.connect(self._on_calculate_datum)
        action_calculate.setEnabled(False)  # Активно при наличии операции
        datum_menu.addAction(action_calculate)
        self.actions['calculate_datum'] = action_calculate
        
        # 2. Исходная линия
        action_line = QAction(
            self._get_icon('datum_line.png'),
            "Исходная линия",
            self.iface.mainWindow()
        )
        action_line.setStatusTip("Построение исходной линии между пунктами")
        action_line.triggered.connect(self._on_datum_line)
        action_line.setEnabled(False)  # Активно при наличии операции
        datum_menu.addAction(action_line)
        self.actions['datum_line'] = action_line
        
        self.main_menu.addMenu(datum_menu)
    
    def _create_area_menu(self):
        """
        Создать меню "Район" - управление районами поиска
        """
        area_menu = QMenu("Район", self.main_menu)
        area_menu.setObjectName("area_menu")
        self.menus['area'] = area_menu
        
        # 1. Подменю "Создать район"
        create_area_menu = QMenu("Создать район", area_menu)
        create_area_menu.setIcon(self._get_icon('create_area.png'))
        self.menus['create_area'] = create_area_menu
        
        # Типы районов поиска согласно методике IAMSAR
        area_types = [
            {
                'id': 'two_points',
                'name': 'Поиск от двух исходных пунктов',
                'icon': 'area_two_points.png',
                'description': 'Район между двумя рассчитанными исходными пунктами'
            },
            {
                'id': 'far_districts',
                'name': 'Поиск в далеко разнесенных районах',
                'icon': 'area_far_districts.png',
                'description': 'Несколько отдельных районов поиска'
            },
            {
                'id': 'line_between_far',
                'name': 'Поиск от линии между двумя далеко разнесенными исходными пунктами',
                'icon': 'area_line_between.png',
                'description': 'Район вдоль линии между удаленными пунктами'
            },
            {
                'id': 'two_far_districts',
                'name': 'Поиск в двух далеко разнесенных районах',
                'icon': 'area_two_far.png',
                'description': 'Два отдельных района поиска'
            },
            {
                'id': 'along_line',
                'name': 'Поиск вдоль исходной линии',
                'icon': 'area_along_line.png',
                'description': 'Район вдоль заданной линии маршрута'
            },
            {
                'id': 'manual_map',
                'name': 'Поиск в районе, определенном SMC на карте, вручную',
                'icon': 'area_manual.png',
                'description': 'Произвольный район, заданный координатором'
            }
        ]
        
        # Создаем действия для каждого типа района
        for area_type in area_types:
            action = QAction(
                self._get_icon(area_type['icon']),
                area_type['name'],
                self.iface.mainWindow()
            )
            action.setStatusTip(area_type['description'])
            action.setData(area_type['id'])  # Сохраняем тип района
            action.triggered.connect(
                lambda checked, area_id=area_type['id']: self._on_create_area(area_id)
            )
            action.setEnabled(False)  # Активируется при наличии операции
            create_area_menu.addAction(action)
            self.actions[f"area_{area_type['id']}"] = action
        
        area_menu.addMenu(create_area_menu)
        area_menu.addSeparator()
        
        # 2. Управление SRU (Search and Rescue Units)
        action_sru = QAction(
            self._get_icon('manage_sru.png'),
            "Управление SRU",
            self.iface.mainWindow()
        )
        action_sru.setStatusTip("Управление поисково-спасательными единицами")
        action_sru.triggered.connect(self._on_manage_sru)
        action_sru.setEnabled(False)  # Активно при наличии операции
        area_menu.addAction(action_sru)
        self.actions['manage_sru'] = action_sru
        
        self.main_menu.addMenu(area_menu)
    
    # === ОБРАБОТЧИКИ МЕНЮ "СЕРВИС" ===
    
    def _on_emergency_types(self):
        """Обработчик настройки типов аварийных ситуаций"""
        from .dialogs.emergency_types_dialog import EmergencyTypesDialog
        
        dialog = EmergencyTypesDialog(self.iface.mainWindow())
        dialog.exec_()
    
    def _on_authorization(self):
        """Обработчик авторизации"""
        from .dialogs.authorization_dialog import AuthorizationDialog
        
        dialog = AuthorizationDialog(self.iface.mainWindow())
        if dialog.exec_():
            user_data = dialog.get_user_data()
            if user_data:
                self.user_authorized = True
                self._update_menu_state()
                
                # Сохраняем данные пользователя
                settings = QSettings('PoiskMore', 'Authorization')
                settings.setValue('user_login', user_data['login'])
                settings.setValue('user_profile', user_data['profile'])
                
                QMessageBox.information(
                    self.iface.mainWindow(),
                    "Авторизация",
                    f"Вход выполнен: {user_data['login']} ({user_data['profile']})"
                )
    
    def _on_sync_contacts(self):
        """Обработчик синхронизации контактов"""
        if not self.user_authorized:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Требуется авторизация",
                "Для синхронизации адресной книги необходимо авторизоваться"
            )
            return
        
        from .sync.contacts_sync import ContactsSync
        
        sync = ContactsSync()
        try:
            result = sync.synchronize()
            QMessageBox.information(
                self.iface.mainWindow(),
                "Синхронизация завершена",
                f"Синхронизировано контактов: {result['synced']}\n"
                f"Новых: {result['new']}, Обновлено: {result['updated']}"
            )
        except Exception as e:
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Ошибка синхронизации",
                f"Не удалось синхронизировать контакты:\n{str(e)}"
            )
    
    # === ОБРАБОТЧИКИ МЕНЮ "ИСХОДНЫЙ ПУНКТ" ===
    
    def _on_calculate_datum(self):
        """Обработчик расчета исходных пунктов"""
        if not self.operation_active:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Нет активной операции",
                "Создайте или загрузите операцию для расчета исходных пунктов"
            )
            return
        
        from .dialogs.datum_calculation_dialog import DatumCalculationDialog
        
        dialog = DatumCalculationDialog(self.operation_data, self.iface.mainWindow())
        if dialog.exec_():
            datum_points = dialog.get_datum_points()
            
            # Сохраняем исходные пункты
            self.operation_data['datum_points'] = datum_points
            
            # Отображаем на карте
            self._display_datum_points(datum_points)
            
            QMessageBox.information(
                self.iface.mainWindow(),
                "Расчет завершен",
                f"Рассчитано исходных пунктов: {len(datum_points)}"
            )
    
    def _on_datum_line(self):
        """Обработчик создания исходной линии"""
        if not self.operation_active:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Нет активной операции",
                "Создайте или загрузите операцию для построения исходной линии"
            )
            return
        
        from .dialogs.datum_line_dialog import DatumLineDialog
        
        dialog = DatumLineDialog(self.operation_data, self.iface.mainWindow())
        if dialog.exec_():
            datum_line = dialog.get_datum_line()
            
            # Сохраняем исходную линию
            self.operation_data['datum_line'] = datum_line
            
            # Отображаем на карте
            self._display_datum_line(datum_line)
            
            QMessageBox.information(
                self.iface.mainWindow(),
                "Линия построена",
                f"Исходная линия содержит {len(datum_line)} точек"
            )
    
    # === ОБРАБОТЧИКИ МЕНЮ "РАЙОН" ===
    
    def _on_create_area(self, area_type):
        """
        Обработчик создания района поиска
        
        Args:
            area_type: Тип района поиска
        """
        if not self.operation_active:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Нет активной операции",
                "Создайте или загрузите операцию для создания района поиска"
            )
            return
        
        from .dialogs.search_area_dialog import SearchAreaDialog
        
        dialog = SearchAreaDialog(
            area_type,
            self.operation_data,
            self.iface.mainWindow()
        )
        
        if dialog.exec_():
            search_area = dialog.get_search_area()
            
            # Добавляем район в операцию
            if 'search_areas' not in self.operation_data:
                self.operation_data['search_areas'] = []
            
            self.operation_data['search_areas'].append(search_area)
            
            # Отображаем на карте
            self._display_search_area(search_area)
            
            # Обновляем статистику
            self._update_operation_statistics()
            
            QMessageBox.information(
                self.iface.mainWindow(),
                "Район создан",
                f"Создан район поиска: {search_area['name']}\n"
                f"Площадь: {search_area['area_km2']:.2f} км²"
            )
    
    def _on_manage_sru(self):
        """Обработчик управления SRU"""
        if not self.operation_active:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Нет активной операции",
                "Создайте или загрузите операцию для управления SRU"
            )
            return
        
        from .dialogs.sru_management_dialog import SRUManagementDialog
        
        dialog = SRUManagementDialog(self.operation_data, self.iface.mainWindow())
        if dialog.exec_():
            sru_data = dialog.get_sru_data()
            
            # Сохраняем данные SRU
            self.operation_data['sru_units'] = sru_data
            
            # Распределяем SRU по районам
            self._distribute_sru()
            
            QMessageBox.information(
                self.iface.mainWindow(),
                "SRU обновлены",
                f"Активных поисковых единиц: {len(sru_data)}"
            )

    def _create_documents_menu(self):
        """
        Создать меню "Документы" - формы и отчеты
        """
        docs_menu = QMenu("Документы", self.main_menu)
        docs_menu.setObjectName("documents_menu")
        self.menus['documents'] = docs_menu
        
        # 1. Стандартные формы
        action_forms = QAction(
            self._get_icon('standard_forms.png'),
            "Стандартные формы",
            self.iface.mainWindow()
        )
        action_forms.setStatusTip("Создание и заполнение стандартных форм IAMSAR")
        action_forms.triggered.connect(self._on_standard_forms)
        action_forms.setEnabled(False)  # Активно при наличии операции
        docs_menu.addAction(action_forms)
        self.actions['standard_forms'] = action_forms
        
        # 2. План поиска
        action_plan = QAction(
            self._get_icon('search_plan.png'),
            "План поиска",
            self.iface.mainWindow()
        )
        action_plan.setShortcut("Ctrl+P")
        action_plan.setStatusTip("Формирование плана поисковой операции")
        action_plan.triggered.connect(self._on_search_plan)
        action_plan.setEnabled(False)  # Активно при наличии операции
        docs_menu.addAction(action_plan)
        self.actions['search_plan'] = action_plan
        
        # 3. Планшет оперативного дежурного ГМСКЦ
        action_tablet = QAction(
            self._get_icon('duty_tablet.png'),
            "Планшет оперативного дежурного ГМСКЦ",
            self.iface.mainWindow()
        )
        action_tablet.setStatusTip("Электронный планшет дежурного МСКЦ/МСПЦ")
        action_tablet.triggered.connect(self._on_duty_tablet)
        docs_menu.addAction(action_tablet)
        self.actions['duty_tablet'] = action_tablet
        
        self.main_menu.addMenu(docs_menu)
    
    def _create_help_menu(self):
        """
        Создать меню "Помощь" - справка и документация
        """
        help_menu = QMenu("Помощь", self.main_menu)
        help_menu.setObjectName("help_menu")
        self.menus['help'] = help_menu
        
        # 1. Руководство пользователя
        action_manual = QAction(
            self._get_icon('user_manual.png'),
            "Руководство пользователя",
            self.iface.mainWindow()
        )
        action_manual.setShortcut("F1")
        action_manual.setStatusTip("Открыть руководство пользователя")
        action_manual.triggered.connect(self._on_user_manual)
        help_menu.addAction(action_manual)
        self.actions['user_manual'] = action_manual
        
        # 2. Методика IAMSAR
        action_iamsar = QAction(
            self._get_icon('iamsar.png'),
            "Методика IAMSAR",
            self.iface.mainWindow()
        )
        action_iamsar.setStatusTip("Справочник по методике IAMSAR")
        action_iamsar.triggered.connect(self._on_iamsar_guide)
        help_menu.addAction(action_iamsar)
        self.actions['iamsar_guide'] = action_iamsar
        
        # 3. Калькуляторы
        action_calc = QAction(
            self._get_icon('calculators.png'),
            "Калькуляторы",
            self.iface.mainWindow()
        )
        action_calc.setStatusTip("Вспомогательные калькуляторы для расчетов")
        action_calc.triggered.connect(self._on_calculators)
        help_menu.addAction(action_calc)
        self.actions['calculators'] = action_calc
        
        help_menu.addSeparator()
        
        # 4. О программе
        action_about = QAction(
            self._get_icon('about.png'),
            "О программе",
            self.iface.mainWindow()
        )
        action_about.setStatusTip("Информация о программе ПОИСК-МОРЕ")
        action_about.triggered.connect(self._on_about)
        help_menu.addAction(action_about)
        self.actions['about'] = action_about
        
        self.main_menu.addMenu(help_menu)
    
    def _create_toolbar(self):
        """
        Создать панель инструментов с быстрым доступом к основным функциям
        """
        toolbar = self.iface.addToolBar("ПОИСК-МОРЕ")
        toolbar.setObjectName("poisk_more_toolbar")
        self.toolbars['main'] = toolbar
        
        # Основные действия для панели инструментов
        toolbar_actions = [
            ('new_case', 'Новый случай'),
            ('operations_list', 'Список операций'),
            None,  # Разделитель
            ('calculate_datum', 'Исходные пункты'),
            ('create_area', 'Создать район'),
            ('manage_sru', 'SRU'),
            None,  # Разделитель
            ('search_plan', 'План поиска'),
            ('standard_forms', 'Формы'),
            None,  # Разделитель
            ('user_manual', 'Справка')
        ]
        
        for action_item in toolbar_actions:
            if action_item is None:
                toolbar.addSeparator()
            else:
                action_name, tooltip = action_item
                if action_name in self.actions:
                    action = self.actions[action_name]
                    action.setToolTip(tooltip)
                    toolbar.addAction(action)
                elif action_name == 'create_area':
                    # Добавляем кнопку с выпадающим меню для создания района
                    from qgis.PyQt.QtWidgets import QToolButton
                    
                    tool_button = QToolButton()
                    tool_button.setIcon(self._get_icon('create_area.png'))
                    tool_button.setToolTip('Создать район поиска')
                    tool_button.setPopupMode(QToolButton.MenuButtonPopup)
                    tool_button.setMenu(self.menus['create_area'])
                    toolbar.addWidget(tool_button)
    
    # === ОБРАБОТЧИКИ МЕНЮ "ДОКУМЕНТЫ" ===
    
    def _on_standard_forms(self):
        """Обработчик стандартных форм"""
        if not self.operation_active:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Нет активной операции",
                "Создайте или загрузите операцию для работы с формами"
            )
            return
        
        from .dialogs.standard_forms_dialog import StandardFormsDialog
        
        dialog = StandardFormsDialog(self.operation_data, self.iface.mainWindow())
        if dialog.exec_():
            form_type = dialog.get_selected_form()
            if form_type:
                self._generate_form(form_type)
    
    def _on_search_plan(self):
        """Обработчик плана поиска"""
        if not self.operation_active:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Нет активной операции",
                "Создайте или загрузите операцию для создания плана поиска"
            )
            return
        
        from .dialogs.search_plan_dialog import SearchPlanDialog
        
        dialog = SearchPlanDialog(self.operation_data, self.iface.mainWindow())
        if dialog.exec_():
            plan_data = dialog.get_plan_data()
            
            # Сохраняем план
            self.operation_data['search_plan'] = plan_data
            
            # Генерируем документ
            self._generate_search_plan_document(plan_data)
    
    def _on_duty_tablet(self):
        """Обработчик планшета дежурного"""
        from .dialogs.duty_tablet_dialog import DutyTabletDialog
        
        dialog = DutyTabletDialog(self.iface.mainWindow())
        dialog.exec_()
    
    # === ОБРАБОТЧИКИ МЕНЮ "ПОМОЩЬ" ===
    
    def _on_user_manual(self):
        """Обработчик руководства пользователя"""
        import webbrowser
        import os
        
        manual_path = os.path.join(self.plugin_dir, 'docs', 'user_manual.pdf')
        if os.path.exists(manual_path):
            webbrowser.open(manual_path)
        else:
            QMessageBox.information(
                self.iface.mainWindow(),
                "Руководство",
                "Руководство пользователя находится в разработке"
            )
    
    def _on_iamsar_guide(self):
        """Обработчик справочника IAMSAR"""
        from .dialogs.iamsar_reference_dialog import IAMSARReferenceDialog
        
        dialog = IAMSARReferenceDialog(self.iface.mainWindow())
        dialog.exec_()
    
    def _on_calculators(self):
        """Обработчик калькуляторов"""
        from .dialogs.calculators_dialog import CalculatorsDialog
        
        dialog = CalculatorsDialog(self.iface.mainWindow())
        dialog.exec_()
    
    def _on_about(self):
        """Обработчик информации о программе"""
        from .dialogs.about_dialog import AboutDialog
        
        dialog = AboutDialog(self.iface.mainWindow())
        dialog.exec_()
    
    # === МЕТОДЫ РАБОТЫ С ОПЕРАЦИЯМИ ===
    
    def _save_operation_state(self, status='active'):
        """
        Сохранить состояние текущей операции
        
        Args:
            status: Статус операции (active, suspended, completed)
        """
        if not self.operation_data:
            return
        
        from .utils.db_manager import DatabaseManager
        
        db = DatabaseManager()
        self.operation_data['status'] = status
        self.operation_data['last_modified'] = QDateTime.currentDateTime().toString()
        
        db.save_operation(self.operation_data)
    
    def _load_operation(self, operation_id):
        """
        Загрузить операцию по ID
        
        Args:
            operation_id: Идентификатор операции
        """
        from .utils.db_manager import DatabaseManager
        
        db = DatabaseManager()
        operation_data = db.load_operation(operation_id)
        
        if operation_data:
            self.operation_data = operation_data
            self.operation_active = True
            self._update_menu_state()
            self.operation_started.emit(operation_data)
    
    def _archive_operation(self, finish_data):
        """
        Архивировать завершенную операцию
        
        Args:
            finish_data: Данные о завершении операции
        """
        from .utils.db_manager import DatabaseManager
        
        db = DatabaseManager()
        self.operation_data.update(finish_data)
        self.operation_data['status'] = 'completed'
        self.operation_data['archived'] = True
        self.operation_data['archive_date'] = QDateTime.currentDateTime().toString()
        
        db.archive_operation(self.operation_data)
    
    def _load_archived_case(self, case_id):
        """
        Загрузить архивное дело для повторного поиска
        
        Args:
            case_id: Идентификатор дела
        """
        from .utils.db_manager import DatabaseManager
        
        db = DatabaseManager()
        archived_case = db.load_archived_case(case_id)
        
        if archived_case:
            # Создаем новую операцию на основе архивного дела
            self.operation_data = archived_case.copy()
            self.operation_data['status'] = 'active'
            self.operation_data['archived'] = False
            self.operation_data['reopened'] = True
            self.operation_data['reopen_date'] = QDateTime.currentDateTime().toString()
            
            self.operation_active = True
            self._update_menu_state()
            self.operation_started.emit(self.operation_data)
    
    # === МЕТОДЫ ОТОБРАЖЕНИЯ НА КАРТЕ ===
    
    def _display_datum_points(self, datum_points):
        """Отобразить исходные пункты на карте"""
        from .map.layers_manager import LayersManager
        
        layers = LayersManager(self.iface)
        layers.add_datum_points_layer(datum_points)
    
    def _display_datum_line(self, datum_line):
        """Отобразить исходную линию на карте"""
        from .map.layers_manager import LayersManager
        
        layers = LayersManager(self.iface)
        layers.add_datum_line_layer(datum_line)
    
    def _display_search_area(self, search_area):
        """Отобразить район поиска на карте"""
        from .map.layers_manager import LayersManager
        
        layers = LayersManager(self.iface)
        layers.add_search_area_layer(search_area)
    
    def _distribute_sru(self):
        """Распределить SRU по районам поиска"""
        from .calculations.sru_distribution import SRUDistribution
        
        if 'search_areas' not in self.operation_data or 'sru_units' not in self.operation_data:
            return
        
        distribution = SRUDistribution()
        assignments = distribution.distribute(
            self.operation_data['sru_units'],
            self.operation_data['search_areas']
        )
        
        self.operation_data['sru_assignments'] = assignments
        
        # Отображаем распределение на карте
        from .map.layers_manager import LayersManager
        layers = LayersManager(self.iface)
        layers.display_sru_assignments(assignments)
    
    def _update_operation_statistics(self):
        """Обновить статистику операции"""
        if not self.operation_data:
            return
        
        stats = {
            'total_area': 0,
            'covered_area': 0,
            'poc': 0,  # Probability of Containment
            'pod': 0,  # Probability of Detection
            'pos': 0   # Probability of Success
        }
        
        if 'search_areas' in self.operation_data:
            for area in self.operation_data['search_areas']:
                stats['total_area'] += area.get('area_km2', 0)
                stats['covered_area'] += area.get('covered_km2', 0)
        
        # Расчет вероятностей
        from .calculations.probability_calculator import ProbabilityCalculator
        calc = ProbabilityCalculator()
        
        if stats['total_area'] > 0:
            stats['poc'] = calc.calculate_poc(self.operation_data)
            stats['pod'] = calc.calculate_pod(self.operation_data)
            stats['pos'] = calc.calculate_pos(stats['poc'], stats['pod'])
        
        self.operation_data['statistics'] = stats
        
        # Обновляем отображение статистики
        self.menu_action_triggered.emit('update_statistics')
    
    def _generate_form(self, form_type):
        """
        Генерировать стандартную форму
        
        Args:
            form_type: Тип формы для генерации
        """
        from .reports.standard_forms import StandardFormsGenerator
        
        generator = StandardFormsGenerator()
        file_path = generator.generate_form(form_type, self.operation_data)
        
        if file_path:
            QMessageBox.information(
                self.iface.mainWindow(),
                "Форма создана",
                f"Форма сохранена: {file_path}"
            )
            
            # Открываем созданный файл
            import webbrowser
            webbrowser.open(file_path)
    
    def _generate_search_plan_document(self, plan_data):
        """
        Генерировать документ плана поиска
        
        Args:
            plan_data: Данные плана поиска
        """
        from .reports.search_plan_generator import SearchPlanGenerator
        
        generator = SearchPlanGenerator()
        file_path = generator.generate_plan(plan_data, self.operation_data)
        
        if file_path:
            QMessageBox.information(
                self.iface.mainWindow(),
                "План создан",
                f"План поиска сохранен: {file_path}"
            )
            
            # Открываем созданный файл
            import webbrowser
            webbrowser.open(file_path)
    
    def cleanup(self):
        """
        Очистка ресурсов при выгрузке плагина
        """
        # Сохраняем текущую операцию если есть
        if self.operation_active:
            self._save_operation_state()
        
        # Удаляем меню
        if self.main_menu:
            self.iface.mainWindow().menuBar().removeAction(self.main_menu.menuAction())
        
        # Удаляем панели инструментов
        for toolbar in self.toolbars.values():
            self.iface.mainWindow().removeToolBar(toolbar)
        
        # Очищаем ссылки
        self.menus.clear()
        self.actions.clear()
        self.toolbars.clear()

# --- begin: auto-patch by sync_menu_structure (20250825-203127)
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

# --- end: auto-patch by sync_menu_structure
