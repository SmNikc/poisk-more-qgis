# -*- coding: utf-8 -*-
"""
Главный файл плагина ПОИСК-МОРЕ для QGIS
Использует MenuManager для управления структурой меню
"""

import os
from .dialogs.emergency_types_dialog import EmergencyTypesDialog
from PyQt5.QtWidgets import QAction
from qgis.PyQt.QtWidgets import QAction, QMenu, QDialog, QMessageBox
from .dialogs.incident_registration_dialog import IncidentRegistrationDialog
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.core import Qgis, QgsApplication, QgsProject

# Импорт менеджера меню - УЖЕ ЕСТЬ В ПАПКЕ!
from .menu_structure import MenuManager

# Импорт существующих диалогов
try:
    from .dialogs.dialog_registration import RegistrationDialog
    from .dialogs.dialog_weather import WeatherDialog
    from .dialogs.dialog_searcharea import SearchAreaDialog
    from .dialogs.dialog_sitrep import SitrepDialog
    from .dialogs.dialog_operation_edit import OperationEditDialog
    from .dialogs.dialog_incident_object import IncidentObjectDialog
    from .dialogs.dialog_search_params import SearchParamsDialog
except ImportError as e:
    print(f"Внимание: не все диалоги доступны: {e}")

# Импорт алгоритмов
try:
    from .alg.alg_datum import calculate_datum_points, add_datum_layer
    from .alg.alg_zone import create_search_area, add_search_layer
    from .alg.alg_distant_points import distant_points_calculation
    from .alg.alg_manual_area import manual_area, ManualAreaTool
except ImportError as e:
    print(f"Внимание: не все алгоритмы доступны: {e}")

class PoiskMorePlugin:
    """
    Главный класс плагина ПОИСК-МОРЕ
    Интегрирует MenuManager с существующей логикой
    """
    
    def __init__(self, iface):
        """
        Конструктор плагина
        
        Args:
            iface: Интерфейс QGIS
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        
        # Менеджер меню - будет создан в initGui
        self.menu_manager = None
        
        # Данные операций (сохраняем совместимость)
        self.current_operation = None
        self.operations = []
        self._map_tool = None
        
        # Инициализация переводчика для локализации
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PoiskMore_{}.qm'.format(locale)
        )
        
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)
    
    def initGui(self):
        """
        Инициализация GUI плагина
        Использует MenuManager для создания структуры меню
        """
        # --- ensure_emergency_types_dialog (auto) ---
        try:
            self.action_emergency_types
        except AttributeError:
            self.action_emergency_types = QAction("Типы происшествий", self.iface.mainWindow())
            self.action_emergency_types.triggered.connect(self._on_emergency_types)
            try:
                self.iface.addPluginToMenu("&Поиск-Море", self.action_emergency_types)
            except Exception:
                self.iface.addPluginToMenu("Поиск-Море", self.action_emergency_types)

        # Создаем менеджер меню с полной структурой
        self.menu_manager = MenuManager(self.iface, self.plugin_dir)
        self.menu_manager.create_menu_structure()
        
        # Подключаем сигналы менеджера меню
        self.menu_manager.operation_started.connect(self.on_operation_started)
        self.menu_manager.operation_closed.connect(self.on_operation_closed)
        self.menu_manager.menu_action_triggered.connect(self.on_menu_action)
        
        # Переопределяем обработчики для интеграции с существующей логикой
        self._override_menu_handlers()
        
        # Устанавливаем начальное состояние
        self._update_menu_state()
        
        # Показываем сообщение о загрузке
        self.iface.messageBar().pushMessage(
            "ПОИСК-МОРЕ",
            "Плагин загружен и готов к работе",
            level=Qgis.Info,
            duration=3
        )
    
    def _override_menu_handlers(self):
        """
        Переопределяем обработчики меню для использования существующей логики
        """
        # Подключаем существующие обработчики к действиям меню
        actions = self.menu_manager.actions
        
        # Меню "Поиск"
        if 'new_case' in actions:
            actions['new_case'].triggered.disconnect()  # Отключаем стандартный
            actions['new_case'].triggered.connect(self.new_emergency_case)
        
        if 'operations_list' in actions:
            actions['operations_list'].triggered.disconnect()
            actions['operations_list'].triggered.connect(self.operations_list)
        
        if 'edit_info' in actions:
            actions['edit_info'].triggered.disconnect()
            actions['edit_info'].triggered.connect(self.edit_info)
        
        if 'close_search' in actions:
            actions['close_search'].triggered.disconnect()
            actions['close_search'].triggered.connect(self.close_search)
        
        # Меню "Исходный пункт"
        if 'calculate_datum' in actions:
            actions['calculate_datum'].triggered.disconnect()
            actions['calculate_datum'].triggered.connect(self.calculate_datum_points)
        
        if 'datum_line' in actions:
            actions['datum_line'].triggered.disconnect()
            actions['datum_line'].triggered.connect(self.datum_line)
        
        # Меню "Район"
        if 'area_two_points' in actions:
            actions['area_two_points'].triggered.disconnect()
            actions['area_two_points'].triggered.connect(self.search_two_points)
        
        if 'area_along_line' in actions:
            actions['area_along_line'].triggered.disconnect()
            actions['area_along_line'].triggered.connect(self.search_along_line)
        
        if 'area_manual_map' in actions:
            actions['area_manual_map'].triggered.disconnect()
            actions['area_manual_map'].triggered.connect(self.manual_area)
    
    def _update_menu_state(self):
        """
        Обновить состояние меню в зависимости от наличия операции
        """
        if self.menu_manager:
            # Обновляем состояние меню через менеджер
            self.menu_manager.operation_active = bool(self.current_operation)
            self.menu_manager._update_menu_state()
    
    # === ОБРАБОТЧИКИ СИГНАЛОВ МЕНЕДЖЕРА ===
    
    def on_operation_started(self, operation_data):
        """
        Обработчик начала новой операции от менеджера меню
        """
        self.current_operation = operation_data
        self.operations.append(operation_data)
        self._update_menu_state()
        
        # Показываем сообщение
        self.iface.messageBar().pushMessage(
            "Операция начата",
            f"Аварийный случай №{operation_data.get('case_number', 'N/A')}",
            level=Qgis.Success,
            duration=5
        )
    
    def on_operation_closed(self):
        """
        Обработчик закрытия операции от менеджера меню
        """
        if self.current_operation:
            self.current_operation['status'] = 'closed'
            self.current_operation = None
            self._update_menu_state()
            
            self.iface.messageBar().pushMessage(
                "Операция закрыта",
                "Текущая операция закрыта",
                level=Qgis.Info,
                duration=5
            )
    
    def on_menu_action(self, action_name):
        """
        Обработчик действий меню от менеджера
        """
        # Здесь можно обрабатывать дополнительные действия
        pass

    # === СУЩЕСТВУЮЩИЕ ОБРАБОТЧИКИ (СОХРАНЯЕМ СОВМЕСТИМОСТЬ) ===

    def _on_emergency_types(self):
        """Открыть диалог настройки типов аварийных ситуаций"""
        dialog = EmergencyTypesDialog(self.iface.mainWindow())
        dialog.exec_()

    def new_emergency_case(self):
        """Создать новый аварийный случай"""
        try:
            dialog = RegistrationDialog()
            if dialog.exec_() == QDialog.Accepted:
                self.current_operation = dialog.get_data()
                self.operations.append(self.current_operation)
                
                # Обновляем менеджер меню
                self.menu_manager.operation_data = self.current_operation
                self.menu_manager.operation_active = True
                self.menu_manager._update_menu_state()
                
                self.iface.messageBar().pushMessage(
                    "Успех",
                    "Новый аварийный случай создан",
                    level=Qgis.Success,
                    duration=5
                )
        except Exception as e:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Ошибка",
                f"Не удалось создать операцию: {str(e)}"
            )
    
    def operations_list(self):
        """Показать список операций"""
        if not self.operations:
            QMessageBox.information(
                self.iface.mainWindow(),
                "Список операций",
                "Нет сохраненных операций"
            )
            return
        
        # TODO: Использовать существующий диалог operations_list_dialog
        info = f"Всего операций: {len(self.operations)}\n"
        for i, op in enumerate(self.operations[:5], 1):
            info += f"{i}. {op.get('case_number', 'N/A')}\n"
        
        QMessageBox.information(
            self.iface.mainWindow(),
            "Дела и поисковые операции",
            info
        )
    
    def edit_info(self):
        """Редактировать информацию об операции"""
        if not self.current_operation:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Предупреждение",
                "Нет активной операции для редактирования"
            )
            return
        
        try:
            dialog = OperationEditDialog(self.current_operation)
            if dialog.exec_() == QDialog.Accepted:
                self.current_operation = dialog.get_data()
                self.iface.messageBar().pushMessage(
                    "Успех",
                    "Информация обновлена",
                    level=Qgis.Success,
                    duration=5
                )
        except:
            QMessageBox.information(
                self.iface.mainWindow(),
                "Редактирование",
                "Функция редактирования будет доступна в следующей версии"
            )
    
    def close_search(self):
        """Закрыть текущий поиск"""
        if not self.current_operation:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Предупреждение",
                "Нет активной операции"
            )
            return
        
        reply = QMessageBox.question(
            self.iface.mainWindow(),
            "Закрыть поиск",
            "Вы уверены, что хотите закрыть текущий поиск?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_operation['status'] = 'closed'
            self.current_operation = None
            self._update_menu_state()
            
            self.iface.messageBar().pushMessage(
                "Поиск закрыт",
                "Текущая операция закрыта",
                level=Qgis.Info,
                duration=5
            )
    
    def calculate_datum_points(self):
        """Вычислить исходные пункты"""
        if not self.current_operation:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Предупреждение",
                "Создайте операцию для расчета исходных пунктов"
            )
            return
        
        try:
            # Используем существующий алгоритм
            from .alg.alg_datum import calculate_datum_points
            # TODO: Открыть диалог для ввода параметров
            QMessageBox.information(
                self.iface.mainWindow(),
                "Расчет исходных пунктов",
                "Функция расчета будет доступна после настройки параметров"
            )
        except Exception as e:
            QMessageBox.warning(
                self.iface.mainWindow(),
                "Ошибка",
                f"Ошибка при расчете: {str(e)}"
            )
    
    def datum_line(self):
        """Построить исходную линию"""
        QMessageBox.information(
            self.iface.mainWindow(),
            "Исходная линия",
            "Выберите две точки на карте для построения линии"
        )
        # TODO: Активировать инструмент выбора точек
    
    def search_two_points(self):
        """Поиск от двух исходных пунктов"""
        QMessageBox.information(
            self.iface.mainWindow(),
            "Создание района",
            "Поиск от двух исходных пунктов"
        )
    
    def search_along_line(self):
        """Поиск вдоль исходной линии"""
        QMessageBox.information(
            self.iface.mainWindow(),
            "Создание района",
            "Поиск вдоль исходной линии"
        )
    
    def manual_area(self):
        """Ручное создание района поиска"""
        try:
            from .alg.alg_manual_area import manual_area
            manual_area(self.iface)
        except:
            QMessageBox.information(
                self.iface.mainWindow(),
                "Ручное построение",
                "Нарисуйте район поиска на карте"
            )
    
    def unload(self):
        """
        Выгрузка плагина
        Очистка ресурсов при отключении
        """
        # --- ensure_emergency_types_dialog (auto) ---
        try:
            self.iface.removePluginMenu("&Поиск-Море", self.action_emergency_types)
        except Exception:
            try:
                self.iface.removePluginMenu("Поиск-Море", self.action_emergency_types)
            except Exception:
                pass

        # Сохраняем текущую операцию если есть
        if self.current_operation:
            reply = QMessageBox.question(
                self.iface.mainWindow(),
                "Выгрузка плагина",
                "Есть активная операция. Сохранить перед выгрузкой?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes and self.menu_manager:
                self.menu_manager._save_operation_state()
        
        # Очищаем меню через менеджер
        if self.menu_manager:
            self.menu_manager.cleanup()
        
        # Очищаем инструменты карты
        if self._map_tool:
            self.iface.mapCanvas().unsetMapTool(self._map_tool)
            self._map_tool = None
        
        # Показываем сообщение
        self.iface.messageBar().pushMessage(
            "ПОИСК-МОРЕ",
            "Плагин выгружен",
            level=Qgis.Info,
            duration=3
        )
    def _open_incident_registration_dialog(self):
        try:
            dlg = IncidentRegistrationDialog(self.iface.mainWindow())
            dlg.exec_()
        except Exception as e:
            # Не валим плагин при ошибке диалога
            print('IncidentRegistrationDialog error:', e)




