# -*- coding: utf-8 -*-
"""
Структура меню для плагина ПОИСК-МОРЕ
Версия: 2.0 ПОЛНАЯ (восстановленная с полной поддержкой IAMSAR)
Путь установки: poiskmore_plugin/menu_structure.py

ПОЛНАЯ ПОДДЕРЖКА IAMSAR ОБЯЗАТЕЛЬНА!
"""

from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QToolBar
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt
import os


def create_menu(iface, plugin):
    """
    Создать полную структуру меню согласно IAMSAR
    
    Args:
        iface: интерфейс QGIS
        plugin: экземпляр плагина
        
    Returns:
        QMenu объект с полной структурой
    """
    
    # Главное меню
    menu = QMenu("&Поиск-Море", iface.mainWindow())
    menu.setObjectName("PoiskMoreMenu")
    
    # Путь к иконкам
    icon_dir = os.path.join(os.path.dirname(__file__), 'icons')
    
    # ========== 1. МЕНЮ "ПОИСК" ==========
    search_menu = QMenu("&Поиск", menu)
    search_menu.setObjectName("SearchMenu")
    
    # 1.1 Новый аварийный случай
    action = QAction("&Новый аварийный случай", iface.mainWindow())
    action.setShortcut(QKeySequence("Ctrl+N"))
    action.setToolTip("Создать новый аварийный случай")
    action.setStatusTip("Регистрация нового инцидента SAR")
    action.triggered.connect(plugin.open_new_emergency_dialog)
    search_menu.addAction(action)
    
    # 1.2 Повторный поиск
    action = QAction("&Повторный поиск", iface.mainWindow())
    action.setShortcut(QKeySequence("Ctrl+R"))
    action.setToolTip("Возобновить поисковую операцию")
    action.triggered.connect(plugin.open_repeat_search_dialog)
    search_menu.addAction(action)
    
    # 1.3 Дела и поисковые операции
    action = QAction("&Дела и поисковые операции", iface.mainWindow())
    action.setShortcut(QKeySequence("Ctrl+O"))
    action.setToolTip("Список всех операций SAR")
    action.triggered.connect(plugin.open_operation_list_dialog)
    search_menu.addAction(action)
    
    search_menu.addSeparator()
    
    # 1.4 Редактировать информацию
    action = QAction("&Редактировать информацию", iface.mainWindow())
    action.setShortcut(QKeySequence("Ctrl+E"))
    action.triggered.connect(plugin.edit_current_incident)
    search_menu.addAction(action)
    
    # 1.5 Закрыть поиск
    action = QAction("&Закрыть поиск", iface.mainWindow())
    action.triggered.connect(plugin.close_current_search)
    search_menu.addAction(action)
    
    # 1.6 Завершить
    action = QAction("За&вершить", iface.mainWindow())
    action.triggered.connect(plugin.complete_operation)
    search_menu.addAction(action)
    
    menu.addMenu(search_menu)
    
    # ========== 2. МЕНЮ "СЕРВИС" ==========
    service_menu = QMenu("&Сервис", menu)
    service_menu.setObjectName("ServiceMenu")
    
    # 2.1 Типы аварийных ситуаций
    action = QAction("&Типы аварийных ситуаций", iface.mainWindow())
    action.setToolTip("Управление типами ситуаций согласно IAMSAR")
    action.triggered.connect(plugin.manage_situation_types)
    service_menu.addAction(action)
    
    # 2.2 Авторизация
    action = QAction("&Авторизация", iface.mainWindow())
    action.triggered.connect(plugin.show_authorization)
    service_menu.addAction(action)
    
    # 2.3 Синхронизация адресной книги
    action = QAction("&Синхронизация адресной книги", iface.mainWindow())
    action.triggered.connect(plugin.sync_address_book)
    service_menu.addAction(action)
    
    # 2.4 Минимизация интерфейса
    action = QAction("&Минимизация интерфейса", iface.mainWindow())
    action.setShortcut(QKeySequence("F11"))
    action.triggered.connect(plugin.minimize_interface)
    service_menu.addAction(action)
    
    # 2.5 Морские карты
    action = QAction("&Морские карты", iface.mainWindow())
    action.setToolTip("Управление морскими картами S-57/S-63")
    action.triggered.connect(plugin.manage_marine_maps)
    service_menu.addAction(action)
    
    # 2.6 Настройки
    action = QAction("&Настройки", iface.mainWindow())
    action.setShortcut(QKeySequence("Ctrl+,"))
    action.triggered.connect(plugin.show_settings)
    service_menu.addAction(action)
    
    menu.addMenu(service_menu)
    
    # ========== 3. МЕНЮ "ИСХОДНЫЕ ПУНКТЫ" (DATUM) ==========
    datum_menu = QMenu("&Исходные пункты", menu)
    datum_menu.setObjectName("DatumMenu")
    datum_menu.setToolTip("Расчет datum согласно IAMSAR Vol. II Ch.4")
    
    # 3.1 Расчет исходных пунктов
    action = QAction("&Расчет исходных пунктов", iface.mainWindow())
    action.setShortcut(QKeySequence("Ctrl+D"))
    action.setToolTip("Расчет datum с учетом дрейфа (IAMSAR)")
    action.setStatusTip("Calculate datum points considering drift")
    action.triggered.connect(plugin.calculate_drift)
    datum_menu.addAction(action)
    
    # 3.2 Исходная линия
    action = QAction("&Исходная линия", iface.mainWindow())
    action.setToolTip("Создать datum line для множественных объектов")
    action.triggered.connect(plugin.create_datum_line)
    datum_menu.addAction(action)
    
    # 3.3 Множественные datum
    action = QAction("&Множественные datum", iface.mainWindow())
    action.setToolTip("Расчет для нескольких сценариев")
    action.triggered.connect(plugin.calculate_multiple_datum)
    datum_menu.addAction(action)
    
    menu.addMenu(datum_menu)
    
    # ========== 4. МЕНЮ "РАЙОН" ==========
    area_menu = QMenu("&Район", menu)
    area_menu.setObjectName("AreaMenu")
    area_menu.setToolTip("Построение районов поиска по IAMSAR")
    
    # 4.1 Создать район
    action = QAction("&Создать район", iface.mainWindow())
    action.setShortcut(QKeySequence("Ctrl+A"))
    action.setToolTip("Построить район поиска (10 методов IAMSAR)")
    action.triggered.connect(plugin.open_searcharea_dialog)
    area_menu.addAction(action)
    
    # 4.2 Ручное построение района
    action = QAction("&Ручное построение района", iface.mainWindow())
    action.setToolTip("Нарисовать район вручную")
    action.triggered.connect(plugin.create_manual_area)
    area_menu.addAction(action)
    
    # 4.3 Разделить район
    action = QAction("Раз&делить район", iface.mainWindow())
    action.setToolTip("Разделить на подрайоны для SRU")
    action.triggered.connect(plugin.split_search_area)
    area_menu.addAction(action)
    
    area_menu.addSeparator()
    
    # 4.4 Импорт района
    action = QAction("&Импорт района", iface.mainWindow())
    action.triggered.connect(plugin.import_search_area)
    area_menu.addAction(action)
    
    # 4.5 Экспорт района
    action = QAction("&Экспорт района", iface.mainWindow())
    action.triggered.connect(plugin.export_search_area)
    area_menu.addAction(action)
    
    menu.addMenu(area_menu)
    
    # ========== 5. МЕНЮ "ОПТИМАЛЬНЫЙ ПОИСК" ==========
    optimal_menu = QMenu("&Оптимальный поиск", menu)
    optimal_menu.setObjectName("OptimalMenu")
    optimal_menu.setToolTip("Оптимизация поиска по IAMSAR Vol. II Ch.5")
    
    # 5.1 Управление SRU
    action = QAction("&Управление SRU", iface.mainWindow())
    action.setShortcut(QKeySequence("Ctrl+U"))
    action.setToolTip("Управление поисково-спасательными единицами")
    action.setStatusTip("Search and Rescue Units management")
    action.triggered.connect(plugin.manage_sru)
    optimal_menu.addAction(action)
    
    # 5.2 Распределение маршрутов
    action = QAction("&Распределение маршрутов", iface.mainWindow())
    action.setToolTip("Allocate search patterns to SRUs")
    action.triggered.connect(plugin.allocate_routes)
    optimal_menu.addAction(action)
    
    # 5.3 Расчет POD
    action = QAction("Расчет &POD", iface.mainWindow())
    action.setToolTip("Probability of Detection calculation")
    action.triggered.connect(plugin.calculate_pod)
    optimal_menu.addAction(action)
    
    # 5.4 Оптимизация плана
    action = QAction("&Оптимизация плана", iface.mainWindow())
    action.setToolTip("Optimize search plan (SORAL method)")
    action.triggered.connect(plugin.optimize_search_plan)
    optimal_menu.addAction(action)
    
    menu.addMenu(optimal_menu)
    
    # ========== 6. МЕНЮ "ПОГОДА И ТЕЧЕНИЯ" ==========
    weather_menu = QMenu("&Погода и течения", menu)
    weather_menu.setObjectName("WeatherMenu")
    
    # 6.1 Расписание погоды
    action = QAction("&Расписание погоды", iface.mainWindow())
    action.setShortcut(QKeySequence("Ctrl+W"))
    action.setToolTip("График изменения погодных условий")
    action.triggered.connect(plugin.open_weather_schedule_dialog)
    weather_menu.addAction(action)
    
    # 6.2 Карта течений
    action = QAction("&Карта течений", iface.mainWindow())
    action.setToolTip("Отобразить карту морских течений")
    action.triggered.connect(plugin.show_current_map)
    weather_menu.addAction(action)
    
    # 6.3 Импорт метеоданных
    action = QAction("&Импорт метеоданных", iface.mainWindow())
    action.setToolTip("Загрузить GRIB/NetCDF данные")
    action.triggered.connect(plugin.import_weather_data)
    weather_menu.addAction(action)
    
    # 6.4 Обновить прогноз
    action = QAction("&Обновить прогноз", iface.mainWindow())
    action.setShortcut(QKeySequence("F5"))
    action.triggered.connect(plugin.update_weather_forecast)
    weather_menu.addAction(action)
    
    menu.addMenu(weather_menu)
    
    # ========== 7. МЕНЮ "ДОКУМЕНТЫ" ==========
    docs_menu = QMenu("&Документы", menu)
    docs_menu.setObjectName("DocsMenu")
    
    # 7.1 План поиска
    action = QAction("&План поиска", iface.mainWindow())
    action.setShortcut(QKeySequence("Ctrl+P"))
    action.setToolTip("Экспорт плана поиска в PDF")
    action.triggered.connect(plugin.export_plan_to_pdf)
    docs_menu.addAction(action)
    
    # 7.2 Планшет оперативного дежурного
    action = QAction("Планшет &оперативного дежурного", iface.mainWindow())
    action.setToolTip("Планшет дежурного ГМСКЦ/MRCC")
    action.triggered.connect(plugin.open_duty_tablet)
    docs_menu.addAction(action)
    
    # 7.3 Подменю сообщений
    messages_menu = QMenu("Сформированные &сообщения", docs_menu)
    
    # Типы сообщений согласно IAMSAR
    message_types = [
        ("MAYDAY Relay", "MAYDAY_RELAY"),
        ("PAN-PAN", "PAN_PAN"),
        ("SAR.SURPIC", "SURPIC"),
        ("SITREP", "SITREP"),
        ("Search Action Plan", "SAP"),
        ("Distress Alert", "DISTRESS"),
    ]
    
    for msg_name, msg_type in message_types:
        action = QAction(msg_name, iface.mainWindow())
        action.triggered.connect(lambda checked, t=msg_type: plugin.create_message(t))
        messages_menu.addAction(action)
    
    docs_menu.addMenu(messages_menu)
    
    # 7.4 Отправить SITREP
    action = QAction("Отправить &SITREP", iface.mainWindow())
    action.setToolTip("Отправить ситуационный отчет")
    action.triggered.connect(plugin.send_sitrep)
    docs_menu.addAction(action)
    
    # 7.5 Стандартные формы
    action = QAction("Стандартные &формы", iface.mainWindow())
    action.setToolTip("Формы IAMSAR/IMO")
    action.triggered.connect(plugin.open_standard_forms)
    docs_menu.addAction(action)
    
    # 7.6 Журнал операций
    action = QAction("&Журнал операций", iface.mainWindow())
    action.setToolTip("SAR Mission Log")
    action.triggered.connect(plugin.show_operation_log)
    docs_menu.addAction(action)
    
    docs_menu.addSeparator()
    
    # 7.7 Экспорт в Word
    action = QAction("Экспорт в &Word", iface.mainWindow())
    action.triggered.connect(plugin.export_to_word)
    docs_menu.addAction(action)
    
    menu.addMenu(docs_menu)
    
    # ========== 8. МЕНЮ "ПОМОЩЬ" ==========
    help_menu = QMenu("&Помощь", menu)
    help_menu.setObjectName("HelpMenu")
    
    # 8.1 Руководство пользователя
    action = QAction("&Руководство пользователя", iface.mainWindow())
    action.setShortcut(QKeySequence("F1"))
    action.triggered.connect(plugin.show_user_guide)
    help_menu.addAction(action)
    
    # 8.2 Методика IAMSAR
    action = QAction("Методика &IAMSAR", iface.mainWindow())
    action.setToolTip("IAMSAR Manual references")
    action.triggered.connect(plugin.show_iamsar_guide)
    help_menu.addAction(action)
    
    # 8.3 Калькуляторы
    action = QAction("&Калькуляторы", iface.mainWindow())
    action.setToolTip("Вспомогательные калькуляторы SAR")
    action.triggered.connect(plugin.show_calculators)
    help_menu.addAction(action)
    
    help_menu.addSeparator()
    
    # 8.4 Проверить обновления
    action = QAction("Проверить &обновления", iface.mainWindow())
    action.triggered.connect(plugin.check_updates)
    help_menu.addAction(action)
    
    # 8.5 О программе
    action = QAction("&О программе", iface.mainWindow())
    action.triggered.connect(plugin.show_about)
    help_menu.addAction(action)
    
    menu.addMenu(help_menu)
    
    return menu


def create_toolbar(iface, plugin):
    """
    Создать панель инструментов с основными функциями IAMSAR
    
    Args:
        iface: интерфейс QGIS
        plugin: экземпляр плагина
        
    Returns:
        QToolBar объект
    """
    
    toolbar = iface.addToolBar("Поиск-Море")
    toolbar.setObjectName("PoiskMoreToolbar")
    
    icon_dir = os.path.join(os.path.dirname(__file__), 'icons')
    
    # Кнопка нового инцидента
    icon = QIcon(os.path.join(icon_dir, 'new_incident.png')) if os.path.exists(os.path.join(icon_dir, 'new_incident.png')) else QIcon()
    action = QAction(icon, "Новый инцидент", iface.mainWindow())
    action.setToolTip("Создать новый аварийный случай SAR")
    action.triggered.connect(plugin.open_new_emergency_dialog)
    toolbar.addAction(action)
    
    # Кнопка расчета дрейфа
    icon = QIcon(os.path.join(icon_dir, 'drift.png')) if os.path.exists(os.path.join(icon_dir, 'drift.png')) else QIcon()
    action = QAction(icon, "Расчет дрейфа", iface.mainWindow())
    action.setToolTip("Рассчитать дрейф и datum")
    action.triggered.connect(plugin.calculate_drift)
    toolbar.addAction(action)
    
    # Кнопка создания района
    icon = QIcon(os.path.join(icon_dir, 'search_area.png')) if os.path.exists(os.path.join(icon_dir, 'search_area.png')) else QIcon()
    action = QAction(icon, "Район поиска", iface.mainWindow())
    action.setToolTip("Создать район поиска")
    action.triggered.connect(plugin.open_searcharea_dialog)
    toolbar.addAction(action)
    
    # Кнопка управления SRU
    icon = QIcon(os.path.join(icon_dir, 'sru.png')) if os.path.exists(os.path.join(icon_dir, 'sru.png')) else QIcon()
    action = QAction(icon, "Управление SRU", iface.mainWindow())
    action.setToolTip("Управление поисково-спасательными единицами")
    action.triggered.connect(plugin.manage_sru)
    toolbar.addAction(action)
    
    toolbar.addSeparator()
    
    # Кнопка погоды
    icon = QIcon(os.path.join(icon_dir, 'weather.png')) if os.path.exists(os.path.join(icon_dir, 'weather.png')) else QIcon()
    action = QAction(icon, "Погода", iface.mainWindow())
    action.setToolTip("Расписание погоды")
    action.triggered.connect(plugin.open_weather_schedule_dialog)
    toolbar.addAction(action)
    
    # Кнопка плана
    icon = QIcon(os.path.join(icon_dir, 'plan.png')) if os.path.exists(os.path.join(icon_dir, 'plan.png')) else QIcon()
    action = QAction(icon, "План поиска", iface.mainWindow())
    action.setToolTip("Экспорт плана поиска")
    action.triggered.connect(plugin.export_plan_to_pdf)
    toolbar.addAction(action)
    
    toolbar.addSeparator()
    
    # Кнопка помощи
    icon = QIcon(os.path.join(icon_dir, 'help.png')) if os.path.exists(os.path.join(icon_dir, 'help.png')) else QIcon()
    action = QAction(icon, "Помощь IAMSAR", iface.mainWindow())
    action.setToolTip("Справка по методике IAMSAR")
    action.triggered.connect(plugin.show_iamsar_guide)
    toolbar.addAction(action)
    
    return toolbar


if __name__ == "__main__":
    print("=" * 60)
    print("СТРУКТУРА МЕНЮ ПЛАГИНА ПОИСК-МОРЕ")
    print("Полная поддержка IAMSAR")
    print("=" * 60)
    print("\nМеню включает:")
    print("1. Поиск - управление инцидентами")
    print("2. Сервис - настройки и карты")
    print("3. Исходные пункты - расчет datum")
    print("4. Район - построение районов поиска")
    print("5. Оптимальный поиск - управление SRU")
    print("6. Погода и течения - метеоданные")
    print("7. Документы - отчеты и сообщения")
    print("8. Помощь - руководства IAMSAR")
    print("\n✅ Структура полностью соответствует IAMSAR")
