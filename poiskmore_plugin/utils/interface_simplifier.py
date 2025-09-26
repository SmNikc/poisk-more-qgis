# -*- coding: utf-8 -*-
"""
utils/interface_simplifier.py

МИНИМИЗАЦИЯ ИНТЕРФЕЙСА QGIS ДЛЯ ПЛАГИНА "ПОИСК-МОРЕ"
Скрывает лишние панели QGIS, оставляя максимум места для работы с плагином

РЕАЛИЗУЮ: Минимизация интерфейса
СООТВЕТСТВУЕТ: Восстановление функций из старого плагина v1.1.0_WEATHER_FIXED
ТОЧНЫЙ ФУНКЦИОНАЛ:
- Скрывает боковые панели QGIS (Слои, Браузер, GPS, Сообщения и т.д.)
- НЕ скрывает меню "Поиск-Море"
- Сохраняет состояние между сессиями
- Возможность включения/выключения
"""

from typing import List, Dict, Any
from qgis.PyQt.QtCore import QSettings, pyqtSignal, QObject
from qgis.PyQt.QtWidgets import QDockWidget, QMessageBox
from qgis.core import QgsMessageLog, Qgis
from qgis.gui import QgisInterface


class InterfaceSimplifier(QObject):
    """
    Упрощение интерфейса QGIS для максимизации рабочего пространства
    
    Функции:
    - Скрытие лишних панелей QGIS
    - Сохранение/восстановление состояния панелей
    - Переключение режима минимизации
    - Сохранение настроек пользователя
    """
    
    # Сигнал при изменении состояния минимизации
    minimization_changed = pyqtSignal(bool)
    
    def __init__(self, iface: QgisInterface):
        """
        Инициализация упростителя интерфейса
        
        Args:
            iface: Интерфейс QGIS
        """
        super().__init__()
        self.iface = iface
        self.settings = QSettings("PoiskMore", "InterfaceSimplifier")
        
        # Состояние
        self.is_minimized = False
        self.original_state = {}  # Сохраненное состояние панелей
        
        # Список панелей для скрытия
        self.panels_to_hide = [
            "Layers",           # Панель слоев
            "Browser",          # Браузер
            "LayerOrder",       # Порядок слоев  
            "Overview",         # Обзорная карта
            "Coordinates",      # Координаты
            "MessageLog",       # Журнал сообщений
            "GPS",             # GPS панель
            "Undo/Redo",       # Отмена/повтор
            "Digitizing",      # Инструменты оцифровки
            "Advanced Digitizing", # Продвинутая оцифровка
            "Processing",      # Обработка
            "Spatial Bookmark", # Пространственные закладки
            "Decorations"      # Оформление
        ]
        
        # Панели, которые НЕ скрываем
        self.panels_to_keep = [
            "Поиск-Море",       # Наше меню
            "Navigation"        # Основная навигация (если есть)
        ]
    
    def toggle_minimization(self) -> bool:
        """
        Переключение режима минимизации
        
        Returns:
            bool: Новое состояние (True = включена минимизация)
        """
        try:
            if self.is_minimized:
                self.restore_interface()
            else:
                self.minimize_interface()
            
            return self.is_minimized
            
        except Exception as e:
            self._log_error(f"Ошибка переключения минимизации: {str(e)}")
            return self.is_minimized
    
    def minimize_interface(self):
        """Минимизация интерфейса - скрытие лишних панелей."""
        try:
            self._log_info("Начинается минимизация интерфейса...")
            
            # Сохраняем текущее состояние панелей
            self._save_original_state()
            
            # Скрываем ненужные панели
            hidden_count = self._hide_panels()
            
            # Устанавливаем состояние
            self.is_minimized = True
            self._save_settings()
            
            # Уведомляем пользователя
            self.iface.messageBar().pushMessage(
                "ПОИСК-МОРЕ",
                f"Интерфейс минимизирован. Скрыто панелей: {hidden_count}",
                level=Qgis.Info,
                duration=3
            )
            
            # Сигнал об изменении
            self.minimization_changed.emit(True)
            
            self._log_info(f"Интерфейс минимизирован, скрыто панелей: {hidden_count}")
            
        except Exception as e:
            self._log_error(f"Ошибка минимизации интерфейса: {str(e)}")
    
    def restore_interface(self):
        """Восстановление интерфейса - показ скрытых панелей."""
        try:
            self._log_info("Начинается восстановление интерфейса...")
            
            # Восстанавливаем панели
            restored_count = self._restore_panels()
            
            # Устанавливаем состояние
            self.is_minimized = False
            self._save_settings()
            
            # Уведомляем пользователя
            self.iface.messageBar().pushMessage(
                "ПОИСК-МОРЕ", 
                f"Интерфейс восстановлен. Показано панелей: {restored_count}",
                level=Qgis.Info,
                duration=3
            )
            
            # Сигнал об изменении
            self.minimization_changed.emit(False)
            
            self._log_info(f"Интерфейс восстановлен, показано панелей: {restored_count}")
            
        except Exception as e:
            self._log_error(f"Ошибка восстановления интерфейса: {str(e)}")
    
    def _save_original_state(self):
        """Сохранение исходного состояния панелей."""
        self.original_state.clear()
        
        try:
            main_window = self.iface.mainWindow()
            dock_widgets = main_window.findChildren(QDockWidget)
            
            for dock in dock_widgets:
                widget_name = dock.objectName()
                if widget_name:
                    self.original_state[widget_name] = {
                        'visible': dock.isVisible(),
                        'floating': dock.isFloating(),
                        'area': main_window.dockWidgetArea(dock)
                    }
            
            self._log_info(f"Сохранено состояние {len(self.original_state)} панелей")
            
        except Exception as e:
            self._log_error(f"Ошибка сохранения состояния панелей: {str(e)}")
    
    def _hide_panels(self) -> int:
        """
        Скрытие панелей интерфейса
        
        Returns:
            int: Количество скрытых панелей
        """
        hidden_count = 0
        
        try:
            main_window = self.iface.mainWindow()
            dock_widgets = main_window.findChildren(QDockWidget)
            
            for dock in dock_widgets:
                widget_name = dock.objectName()
                widget_title = dock.windowTitle()
                
                # Пропускаем наши панели
                if any(keep_name in widget_title for keep_name in self.panels_to_keep):
                    continue
                
                # Скрываем если панель в списке для скрытия или соответствует паттерну
                should_hide = False
                
                for panel_pattern in self.panels_to_hide:
                    if (panel_pattern.lower() in widget_name.lower() or 
                        panel_pattern.lower() in widget_title.lower()):
                        should_hide = True
                        break
                
                # Также скрываем стандартные панели QGIS
                if (widget_name.startswith('dw') or  # dwLayers, dwBrowser и т.д.
                    'Layers' in widget_title or
                    'Browser' in widget_title or
                    'Processing' in widget_title):
                    should_hide = True
                
                if should_hide and dock.isVisible():
                    dock.hide()
                    hidden_count += 1
                    self._log_info(f"Скрыта панель: {widget_title} ({widget_name})")
            
            return hidden_count
            
        except Exception as e:
            self._log_error(f"Ошибка скрытия панелей: {str(e)}")
            return 0
    
    def _restore_panels(self) -> int:
        """
        Восстановление панелей интерфейса
        
        Returns:
            int: Количество восстановленных панелей
        """
        restored_count = 0
        
        try:
            main_window = self.iface.mainWindow()
            
            for widget_name, state in self.original_state.items():
                dock = main_window.findChild(QDockWidget, widget_name)
                
                if dock:
                    # Восстанавливаем видимость
                    if state['visible'] and not dock.isVisible():
                        dock.show()
                        restored_count += 1
                        self._log_info(f"Восстановлена панель: {dock.windowTitle()}")
                    
                    # Восстанавливаем плавающее состояние
                    if state['floating'] != dock.isFloating():
                        dock.setFloating(state['floating'])
                    
                    # Восстанавливаем область дока
                    if not state['floating'] and state['area'] != main_window.dockWidgetArea(dock):
                        main_window.addDockWidget(state['area'], dock)
            
            return restored_count
            
        except Exception as e:
            self._log_error(f"Ошибка восстановления панелей: {str(e)}")
            return 0
    
    def load_settings_on_startup(self):
        """Загрузка настроек при запуске плагина."""
        try:
            # Проверяем, была ли включена минимизация
            was_minimized = self.settings.value("minimized", False, type=bool)
            auto_minimize = self.settings.value("auto_minimize", False, type=bool)
            
            if auto_minimize or was_minimized:
                # Задержка для корректной загрузки интерфейса
                from qgis.PyQt.QtCore import QTimer
                QTimer.singleShot(1000, self.minimize_interface)
                
                self._log_info("Автоматическая минимизация интерфейса запланирована")
            
        except Exception as e:
            self._log_error(f"Ошибка загрузки настроек: {str(e)}")
    
    def _save_settings(self):
        """Сохранение настроек."""
        try:
            self.settings.setValue("minimized", self.is_minimized)
            self.settings.setValue("last_save", "2024-09-24 12:00:00")  # Текущее время
            
        except Exception as e:
            self._log_error(f"Ошибка сохранения настроек: {str(e)}")
    
    def cleanup_on_unload(self):
        """Очистка при выгрузке плагина."""
        try:
            # Если интерфейс был минимизирован, восстанавливаем его
            if self.is_minimized:
                self.restore_interface()
            
            # Сохраняем настройки
            self._save_settings()
            
            self._log_info("Упроститель интерфейса выгружен")
            
        except Exception as e:
            self._log_error(f"Ошибка выгрузки упростителя: {str(e)}")
    
    def get_status_text(self) -> str:
        """
        Получение текста статуса для меню
        
        Returns:
            str: Текст статуса
        """
        return "✓ Интерфейс минимизирован" if self.is_minimized else "○ Интерфейс обычный"
    
    def show_settings_dialog(self):
        """Показ диалога настроек минимизации."""
        try:
            from qgis.PyQt.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QLabel
            
            dialog = QDialog(self.iface.mainWindow())
            dialog.setWindowTitle("Настройки минимизации интерфейса")
            dialog.setModal(True)
            dialog.resize(300, 150)
            
            layout = QVBoxLayout(dialog)
            
            # Информация
            info_label = QLabel("Минимизация скрывает лишние панели QGIS,\nоставляя больше места для работы с плагином.")
            layout.addWidget(info_label)
            
            # Чекбокс автоминимизации
            auto_check = QCheckBox("Автоматически минимизировать при запуске")
            auto_check.setChecked(self.settings.value("auto_minimize", False, type=bool))
            layout.addWidget(auto_check)
            
            # Кнопки
            from qgis.PyQt.QtWidgets import QHBoxLayout
            buttons_layout = QHBoxLayout()
            
            ok_btn = QPushButton("OK")
            ok_btn.clicked.connect(lambda: self._save_dialog_settings(dialog, auto_check))
            buttons_layout.addWidget(ok_btn)
            
            cancel_btn = QPushButton("Отмена")
            cancel_btn.clicked.connect(dialog.reject)
            buttons_layout.addWidget(cancel_btn)
            
            layout.addLayout(buttons_layout)
            
            dialog.exec_()
            
        except Exception as e:
            self._log_error(f"Ошибка диалога настроек: {str(e)}")
    
    def _save_dialog_settings(self, dialog, auto_check):
        """Сохранение настроек из диалога."""
        try:
            self.settings.setValue("auto_minimize", auto_check.isChecked())
            dialog.accept()
            
            QMessageBox.information(
                self.iface.mainWindow(),
                "Настройки сохранены",
                "Настройки минимизации интерфейса сохранены."
            )
            
        except Exception as e:
            self._log_error(f"Ошибка сохранения настроек диалога: {str(e)}")
    
    def _log_info(self, message: str):
        """Логирование информации."""
        QgsMessageLog.logMessage(message, "Поиск-Море", Qgis.Info)
    
    def _log_error(self, message: str):
        """Логирование ошибок."""
        QgsMessageLog.logMessage(message, "Поиск-Море", Qgis.Critical)


# Глобальный экземпляр для использования в плагине
_interface_simplifier_instance = None


def get_interface_simplifier(iface: QgisInterface) -> InterfaceSimplifier:
    """
    Получение глобального экземпляра упростителя интерфейса
    
    Args:
        iface: Интерфейс QGIS
        
    Returns:
        InterfaceSimplifier: Экземпляр упростителя
    """
    global _interface_simplifier_instance
    
    if _interface_simplifier_instance is None:
        _interface_simplifier_instance = InterfaceSimplifier(iface)
    
    return _interface_simplifier_instance


def cleanup_interface_simplifier():
    """Очистка глобального экземпляра при выгрузке плагина."""
    global _interface_simplifier_instance
    
    if _interface_simplifier_instance:
        _interface_simplifier_instance.cleanup_on_unload()
        _interface_simplifier_instance = None
