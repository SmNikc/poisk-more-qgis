python

Свернуть

Перенос

Исполнить

Копировать
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QTranslator, QSettings
import os
import importlib
from dialogs.splash_dialog import SplashDialog
from qgis.core import QgsRasterLayer, QgsProject

class PoiskMorePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.actions = []

        # Показ заставки при старте
        splash = SplashDialog(self.iface.mainWindow())
        splash.exec_()

        # Загрузка перевода
        settings = QSettings()
        language = settings.value("language", "Русский")
        translator = QTranslator()
        lang_code = "ru" if language == "Русский" else "en"
        translator_path = os.path.join(os.path.dirname(__file__), f"i18n/poiskmore_{lang_code}.qm")
        translator.load(translator_path)
        QgsApplication.installTranslator(translator)

    def initGui(self):
        self.menu = "Поиск-Море"

        # Полный список 37 форм
        form_map = [
            ("Расчёт дрейфа", "DriftCalculationForm", "dialogs.dialog_driftcalculation"),
            ("Ввод ветра и течения", "WindCurrentInputForm", "dialogs.dialog_windcurrentinput"),
            ("Параметры района поиска", "SearchAreaForm", "dialogs.dialog_searcharea"),
            ("Формирование отчета", "ReportGenerationForm", "dialogs.dialog_reportgeneration"),
            ("Настройки системы", "SettingsForm", "dialogs.dialog_settings"),
            ("Координация с SRU", "CoordinationForm", "dialogs.dialog_coordination"),
            ("Управление SRU", "SRUManagementForm", "dialogs.dialog_srumanagement"),
            ("Создание SITREP", "SitrepForm", "dialogs.dialog_sitrep"),
            ("План действий", "ActionPlanForm", "dialogs.dialog_actionplan"),
            ("Журнал действий", "LogbookForm", "dialogs.dialog_logbook"),
            ("Настройки расчётов", "CalculationSettingsForm", "dialogs.dialog_calculation_settings"),
            ("Судно и экипаж", "VesselCrewEditForm", "dialogs.dialog_vesselcrewedit"),
            ("Карта и геоданные", "GeoMapViewerForm", "dialogs.dialog_geomapviewer"),
            ("Печать/экспорт", "PrintFormsDialog", "dialogs.dialog_printforms"),
            ("Тест ССТО", "SSTOTestForm", "dialogs.dialog_sstotest"),
            ("Уведомление об учении", "ExerciseNoticeForm", "dialogs.dialog_exercisenotice"),
            ("Начальная вероятность", "ProbabilityCalcForm", "dialogs.dialog_probabilitycalc"),
            ("Импорт AIS", "AISImportForm", "dialogs.dialog_aisimport"),
            ("База данных", "DatabaseConnectionForm", "dialogs.dialog_databaseconnection"),
            ("Журнал действий оператора", "OperatorLogForm", "dialogs.dialog_operatorlog"),
            ("Отчёт в ГМСКЦ", "GMSKCCenterReportForm", "dialogs.dialog_gmskcreport"),
            ("Сценарий IAMSAR", "IAMSARScenarioForm", "dialogs.dialog_iamsarscenario"),
            ("Поступившая тревога", "IncomingAlertForm", "dialogs.dialog_incomingalert"),
            ("Внешние модули", "ExternalSystemStatusForm", "dialogs.dialog_externalsystemstatus"),
            ("Отправка SITREP", "SitrepSendForm", "dialogs.dialog_sitrepsend"),
            ("Резервное копирование", "BackupSettingsForm", "dialogs.dialog_backupsettings"),
            ("Обновления", "UpdateControlForm", "dialogs.dialog_updatecontrol"),
            ("Системный журнал", "SystemLogForm", "dialogs.dialog_systemlog"),
            ("Статус плагина", "PluginStatusForm", "dialogs.dialog_pluginstatus"),
            ("Экспорт проекта", "DataExportForm", "dialogs.dialog_dataexport"),
            ("Очистка данных", "CleanupUtilityForm", "dialogs.dialog_cleanuputility"),
            ("Интеграции", "IntegrationStatusForm", "dialogs.dialog_integrationstatus"),
            ("Компоненты", "ComponentListForm", "dialogs.dialog_componentlist"),
            ("Журнал учений", "ExerciseLogForm", "dialogs.dialog_exerciselog"),
            ("Связь с RCC", "RCCCommunicationForm", "dialogs.dialog_rcccommunication"),
            ("Импорт сообщений", "MessageImportForm", "dialogs.dialog_messageimport"),
            ("Просмотр тревог", "AlertViewerForm", "dialogs.dialog_alertviewer")
        ]

        for label, class_name, module_path in form_map:
            action = QAction(QIcon(), label, self.iface.mainWindow())
            action.triggered.connect(self.make_form_opener(class_name, module_path))
            self.iface.addPluginToMenu(self.menu, action)
            self.actions.append(action)

        # Пункт для OpenSeaMap
        openstreetmap_action = QAction(QIcon(), "Открыть OpenSeaMap", self.iface.mainWindow())
        openstreetmap_action.triggered.connect(self.load_openseamap)
        self.iface.addPluginToMenu(self.menu, openstreetmap_action)
        self.actions.append(openseamap_action)

        # Пункты для экспорта, backup, статус
        export_action = QAction(QIcon(), "Экспорт проекта", self.iface.mainWindow())
        export_action.triggered.connect(self.export_project)
        self.iface.addPluginToMenu(self.menu, export_action)
        self.actions.append(export_action)

        backup_action = QAction(QIcon(), "Резервное копирование", self.iface.mainWindow())
        backup_action.triggered.connect(self.backup_project)
        self.iface.addPluginToMenu(self.menu, backup_action)
        self.actions.append(backup_action)

        status_action = QAction(QIcon(), "Статус плагина", self.iface.mainWindow())
        status_action.triggered.connect(self.show_plugin_status)
        self.iface.addPluginToMenu(self.menu, status_action)
        self.actions.append(status_action)

    def make_form_opener(self, class_name, module_path):
        def open_dialog():
            try:
                module = importlib.import_module(module_path)
                dialog_class = getattr(module, class_name)
                dlg = dialog_class()
                dlg.exec_()
            except Exception as e:
                QgsMessageLog.logMessage(f"Ошибка загрузки формы {class_name}: {str(e)}", "Поиск-Море", Qgis.Critical)
        return open_dialog

    def load_openseamap(self):
        try:
            url = "type=xyz&url=https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"
            layer = QgsRasterLayer(url, "OpenSeaMap", "wms")
            if not layer.isValid():
                QgsMessageLog.logMessage("Ошибка загрузки OpenSeaMap", "Поиск-Море", Qgis.Critical)
                return
            QgsProject.instance().addMapLayer(layer)
            QgsMessageLog.logMessage("OpenSeaMap загружен как слой", "Поиск-Море", Qgis.Info)
        except Exception as e:
            QgsMessageLog.logMessage(f"Ошибка: {str(e)}", "Поиск-Море", Qgis.Critical)

    def export_project(self):
        from modules.data_export import DataExport
        exporter = DataExport(os.path.expanduser("~/Desktop/export"))
        # Пример данных
        report_data = {"Операция": "Тест", "Результат": "Успех"}
        exporter.export_pdf(report_data)
        layer = QgsProject.instance().mapLayers().values()[0] if QgsProject.instance().mapLayers() else None
        if layer:
            exporter.export_geojson(layer)
        exporter.export_db("alerts.db", os.path.expanduser("~/Desktop/export/alerts_backup.db"))
        files = ["report.pdf", "zones.geojson"]
        exporter.export_zip(files)

    def backup_project(self):
        from modules.backup import BackupManager
        backup = BackupManager(os.path.expanduser("~/Desktop/backup"))
        backup.backup_project(os.path.dirname(__file__))

    def show_plugin_status(self):
        from dialogs.dialog_pluginstatus import PluginStatusForm
        dlg = PluginStatusForm()
        dlg.exec_()

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu("Поиск-Море", action)