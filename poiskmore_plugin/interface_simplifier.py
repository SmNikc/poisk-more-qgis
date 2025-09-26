# -*- coding: utf-8 -*-
"""
Модуль упрощения интерфейса QGIS для плагина "Поиск-Море. Расчетный блок"
Скрывает все технологические элементы QGIS, оставляя только необходимое
"""

from qgis.PyQt.QtWidgets import QToolBar, QDockWidget, QMenu
from qgis.PyQt.QtCore import QSettings
from qgis.core import QgsApplication
import os

class InterfaceSimplifier:
    """
    Класс для упрощения интерфейса QGIS
    Скрывает все лишние элементы, оставляя только плагин Поиск-Море
    """
    
    def __init__(self, iface):
        self.iface = iface
        self.main_window = iface.mainWindow()
        self.hidden_elements = []
        self.settings = QSettings("PoiskMore", "SimplifiedInterface")
        
    def enable_kiosk_mode(self):
        """
        Включить упрощенный режим (киоск-режим)
        """
        # Сохраняем текущее состояние
        self._save_current_state()
        
        # === СКРЫВАЕМ ПАНЕЛИ ИНСТРУМЕНТОВ ===
        toolbars_to_keep = [
            "Поиск-Море",  # Наша панель
            "mPluginToolBar",  # Панель управления плагинами
        ]
        
        for toolbar in self.main_window.findChildren(QToolBar):
            toolbar_name = toolbar.objectName()
            toolbar_title = toolbar.windowTitle()
            
            # Пропускаем наши панели
            if any(keep in toolbar_name or keep in toolbar_title 
                   for keep in toolbars_to_keep):
                continue
                
            # Скрываем остальные
            if toolbar.isVisible():
                toolbar.setVisible(False)
                self.hidden_elements.append(('toolbar', toolbar_name))
        
        # === СКРЫВАЕМ ПАНЕЛИ (DOCKS) ===
        docks_to_keep = [
            "PmSidebarDock",  # Наша боковая панель
            "Поиск-Море",     # Любые наши панели
            "MessageLog",      # Можно оставить для отладки (опционально)
        ]
        
        for dock in self.main_window.findChildren(QDockWidget):
            dock_name = dock.objectName()
            dock_title = dock.windowTitle()
            
            # Пропускаем наши панели
            if any(keep in dock_name or keep in dock_title 
                   for keep in docks_to_keep):
                continue
                
            # Скрываем остальные
            if dock.isVisible():
                dock.setVisible(False)
                self.hidden_elements.append(('dock', dock_name))
        
        # === УПРОЩАЕМ ГЛАВНОЕ МЕНЮ ===
        menubar = self.main_window.menuBar()
        menus_to_keep = [
            "ПОИСК-МОРЕ",     # Наше меню
            "Модули",         # Для управления плагинами
            "Проект",         # Для открытия/сохранения проекта
        ]
        
        for action in menubar.actions():
            menu = action.menu()
            if menu:
                menu_title = menu.title().replace("&", "")
                if menu_title not in menus_to_keep:
                    action.setVisible(False)
                    self.hidden_elements.append(('menu', menu_title))
        
        # === СКРЫВАЕМ СТРОКУ СОСТОЯНИЯ (опционально) ===
        # self.main_window.statusBar().setVisible(False)
        
        # === ОТКЛЮЧАЕМ КОНТЕКСТНЫЕ МЕНЮ КАРТЫ ===
        canvas = self.iface.mapCanvas()
        canvas.setContextMenuPolicy(0)  # Qt.NoContextMenu
        
        # Сохраняем состояние
        self.settings.setValue("kiosk_mode_enabled", True)
        self.settings.setValue("hidden_elements", self.hidden_elements)
        
        # Уведомление
        self.iface.messageBar().pushMessage(
            "Интерфейс упрощен",
            "Технологические элементы QGIS скрыты. Для восстановления используйте меню плагина.",
            level=0,  # Info
            duration=5
        )
    
    def disable_kiosk_mode(self):
        """
        Отключить упрощенный режим, восстановить все элементы
        """
        # Восстанавливаем панели инструментов
        for toolbar in self.main_window.findChildren(QToolBar):
            toolbar.setVisible(True)
        
        # Восстанавливаем док-панели
        for dock in self.main_window.findChildren(QDockWidget):
            dock.setVisible(True)
        
        # Восстанавливаем меню
        menubar = self.main_window.menuBar()
        for action in menubar.actions():
            action.setVisible(True)
        
        # Восстанавливаем контекстное меню
        canvas = self.iface.mapCanvas()
        canvas.setContextMenuPolicy(1)  # Qt.DefaultContextMenu
        
        # Очищаем настройки
        self.settings.setValue("kiosk_mode_enabled", False)
        self.settings.remove("hidden_elements")
        
        # Уведомление
        self.iface.messageBar().pushMessage(
            "Интерфейс восстановлен",
            "Все элементы QGIS снова доступны.",
            level=0,  # Info
            duration=5
        )
    
    def toggle_kiosk_mode(self):
        """
        Переключить режим интерфейса
        """
        if self.settings.value("kiosk_mode_enabled", False, type=bool):
            self.disable_kiosk_mode()
        else:
            self.enable_kiosk_mode()
    
    def _save_current_state(self):
        """
        Сохранить текущее состояние интерфейса для восстановления
        """
        state = self.main_window.saveState()
        self.settings.setValue("interface_state", state)
    
    def _restore_saved_state(self):
        """
        Восстановить сохраненное состояние интерфейса
        """
        state = self.settings.value("interface_state")
        if state:
            self.main_window.restoreState(state)
    
    def load_base_map(self):
        """
        Загрузить базовую карту и установить вид на территорию РФ
        """
        try:
            from qgis.core import QgsRasterLayer, QgsProject, QgsRectangle
            
            # Проверяем, есть ли уже базовая карта
            has_layers = len(QgsProject.instance().mapLayers()) > 0
            
            if not has_layers:
                # Добавляем OpenStreetMap как базовую карту
                osm_url = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                osm_layer = QgsRasterLayer(osm_url, "OpenStreetMap", "wms")
                
                if osm_layer.isValid():
                    QgsProject.instance().addMapLayer(osm_layer)
            
            # Устанавливаем экстент на территорию России
            # Координаты для охвата всей территории РФ
            russia_extent = QgsRectangle(19.0, 41.0, 191.0, 82.0)
            canvas = self.iface.mapCanvas()
            canvas.setExtent(russia_extent)
            canvas.refresh()
            
            # Закрываем стартовое окно если оно есть
            self._close_welcome_page()
            
        except Exception as e:
            QgsApplication.messageLog().logMessage(
                f"Ошибка загрузки базовой карты: {e}", 
                "Poisk-More", 
                Qgis.Warning
            )
    
    def _close_welcome_page(self):
        """
        Закрыть стартовую страницу QGIS
        """
        try:
            # Ищем и закрываем виджет стартовой страницы
            from qgis.PyQt.QtWidgets import QWidget
            
            # Переключаем фокус на карту
            self.iface.mapCanvas().setFocus()
            
            # Ищем центральный виджет с новостями/проектами
            central = self.main_window.centralWidget()
            if central:
                # Если это стековый виджет, переключаем на карту
                from qgis.PyQt.QtWidgets import QStackedWidget
                if isinstance(central, QStackedWidget):
                    # Ищем индекс карты (обычно 0)
                    for i in range(central.count()):
                        widget = central.widget(i)
                        if "canvas" in str(type(widget)).lower():
                            central.setCurrentIndex(i)
                            break
                    else:
                        central.setCurrentIndex(0)
                        
        except Exception as e:
            QgsApplication.messageLog().logMessage(
                f"Ошибка закрытия стартовой страницы: {e}", 
                "Poisk-More", 
                Qgis.Warning
            )
    
    def create_minimal_interface(self):
        """
        Создать минимальный интерфейс с нуля
        Более радикальный подход - скрывает ВСЁ кроме карты и нашего плагина
        """
        # Закрываем стартовую страницу и показываем карту
        try:
            # Закрываем окно приветствия если оно открыто
            from qgis.PyQt.QtWidgets import QDialog
            for widget in self.main_window.findChildren(QDialog):
                if "welcome" in widget.objectName().lower() or "start" in widget.objectName().lower():
                    widget.close()
            
            # Переключаемся на вид карты
            self.iface.mapCanvas().setFocus()
            
            # Устанавливаем вид на территорию РФ
            # Примерные координаты для охвата территории России
            from qgis.core import QgsRectangle, QgsCoordinateReferenceSystem
            russia_extent = QgsRectangle(20.0, 41.0, 190.0, 82.0)  # долгота мин, широта мин, долгота макс, широта макс
            canvas = self.iface.mapCanvas()
            canvas.setExtent(russia_extent)
            canvas.refresh()
            
        except Exception as e:
            QgsApplication.messageLog().logMessage(f"Ошибка настройки карты: {e}", "Poisk-More", Qgis.Warning)
        
        # Скрываем ВСЕ панели инструментов КРОМЕ нашей
        toolbars_to_keep = [
            "Поиск-Море",
            "PoiskMore"
        ]
        
        for toolbar in self.main_window.findChildren(QToolBar):
            toolbar_name = toolbar.objectName()
            toolbar_title = toolbar.windowTitle()
            
            # Проверяем, нужно ли оставить панель
            keep = False
            for keeper in toolbars_to_keep:
                if keeper in toolbar_name or keeper in toolbar_title:
                    keep = True
                    break
            
            if not keep:
                toolbar.setVisible(False)
        
        # Скрываем ВСЕ док-панели КРОМЕ наших
        docks_to_keep = [
            "PmSidebarDock",
            "Поиск-Море"
        ]
        
        for dock in self.main_window.findChildren(QDockWidget):
            dock_name = dock.objectName()
            dock_title = dock.windowTitle()
            
            # Проверяем, нужно ли оставить панель
            keep = False
            for keeper in docks_to_keep:
                if keeper in dock_name or keeper in dock_title:
                    keep = True
                    break
            
            if not keep:
                dock.setVisible(False)
            else:
                dock.setVisible(True)  # Явно показываем наши панели
        
        # НЕ ОЧИЩАЕМ меню, а только скрываем лишние пункты
        menubar = self.main_window.menuBar()
        
        # Список меню для сохранения
        menus_to_keep = [
            "ПОИСК-МОРЕ",
            "Poisk-More",
            "Файл",
            "Модули",
            "Вид"
        ]
        
        # Скрываем только лишние меню, не трогая наши
        for action in menubar.actions():
            menu = action.menu()
            if menu:
                menu_title = menu.title().replace("&", "")
                
                # Проверяем, нужно ли оставить меню
                keep = False
                for keeper in menus_to_keep:
                    if keeper in menu_title or menu_title in keeper:
                        keep = True
                        break
                
                if not keep:
                    action.setVisible(False)
                else:
                    action.setVisible(True)  # Явно показываем нужные меню
        
        # Если меню "Файл" есть, упрощаем его
        for action in menubar.actions():
            menu = action.menu()
            if menu and "Файл" in menu.title():
                # Скрываем все действия
                for act in menu.actions():
                    act.setVisible(False)
                
                # Добавляем только базовые
                menu.addAction("Открыть проект...", self.iface.actionOpenProject().trigger)
                menu.addAction("Сохранить проект", self.iface.actionSaveProject().trigger)
                menu.addSeparator()
                menu.addAction("Выход", self.iface.actionExit().trigger)
                break
        
        # Если меню "Вид" есть, добавляем восстановление
        for action in menubar.actions():
            menu = action.menu()
            if menu and "Вид" in menu.title():
                menu.addSeparator()
                menu.addAction("Восстановить полный интерфейс", self.disable_kiosk_mode)
                break
        
        # Если меню "Вид" не найдено, создаем его
        view_found = False
        for action in menubar.actions():
            menu = action.menu()
            if menu and "Вид" in menu.title():
                view_found = True
                break
        
        if not view_found:
            view_menu = menubar.addMenu("Вид")
            view_menu.addAction("Восстановить полный интерфейс", self.disable_kiosk_mode)
        
        # Убеждаемся что меню ПОИСК-МОРЕ видно
        for action in menubar.actions():
            menu = action.menu()
            if menu and ("ПОИСК" in menu.title().upper() or "МОРЕ" in menu.title().upper()):
                action.setVisible(True)
                menu.setEnabled(True)
        
        # Сохраняем состояние
        self.settings.setValue("minimal_interface", True)
        
        # Уведомление
        self.iface.messageBar().pushMessage(
            "Минимальный интерфейс",
            "Активирован минимальный режим. Меню ПОИСК-МОРЕ доступно.",
            level=0,
            duration=5
        )


def add_interface_controls_to_menu(menu_manager):
    """
    Добавить управление интерфейсом в меню плагина
    
    Args:
        menu_manager: Экземпляр MenuManager плагина
    """
    from qgis.PyQt.QtWidgets import QAction
    
    # Создаем экземпляр упрощителя
    simplifier = InterfaceSimplifier(menu_manager.iface)
    
    
    # Загружаем базовую карту России при первом запуске
    simplifier.load_base_map()
    # Добавляем разделитель в меню Сервис
    if 'service' in menu_manager.menus:
        service_menu = menu_manager.menus['service']
        service_menu.addSeparator()
        
        # Добавляем подменю управления интерфейсом
        interface_menu = service_menu.addMenu("Интерфейс")
        
        # Упрощенный режим
        simple_action = QAction("Включить упрощенный режим", interface_menu)
        simple_action.triggered.connect(simplifier.enable_kiosk_mode)
        interface_menu.addAction(simple_action)
        
        # Минимальный режим
        minimal_action = QAction("Минимальный интерфейс", interface_menu)
        minimal_action.triggered.connect(simplifier.create_minimal_interface)
        interface_menu.addAction(minimal_action)
        
        # Восстановить
        restore_action = QAction("Восстановить полный интерфейс", interface_menu)
        restore_action.triggered.connect(simplifier.disable_kiosk_mode)
        interface_menu.addAction(restore_action)
        
        interface_menu.addSeparator()
        
        # Переключатель
        toggle_action = QAction("Переключить режим", interface_menu)
        toggle_action.triggered.connect(simplifier.toggle_kiosk_mode)
        interface_menu.addAction(toggle_action)
    
    # Проверяем, был ли включен упрощенный режим ранее
    if simplifier.settings.value("kiosk_mode_enabled", False, type=bool):
        simplifier.enable_kiosk_mode()
    elif simplifier.settings.value("minimal_interface", False, type=bool):
        simplifier.create_minimal_interface()
    
    return simplifier


# === АВТОЗАПУСК ПРИ СТАРТЕ ===
def auto_simplify_on_startup(iface):
    """
    Автоматически упростить интерфейс при запуске QGIS
    Добавьте вызов этой функции в initGui() плагина
    """
    settings = QSettings("PoiskMore", "SimplifiedInterface")
    
    # Если включен автозапуск упрощенного режима
    if settings.value("auto_simplify", False, type=bool):
        simplifier = InterfaceSimplifier(iface)
        simplifier.enable_kiosk_mode()
        return simplifier
    
    return None
