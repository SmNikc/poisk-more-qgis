from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QDialog
from qgis.core import QgsApplication
import os

class PoiskMorePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.actions = []

    def initGui(self):
        # 🔔 Splash‐screen перед всем остальным
        from dialogs.splash_dialog import SplashDialog
        splash = SplashDialog(self.iface.mainWindow())
        splash.exec_()

        # 🌐 Глобальная загрузка переводов (если нужна)
        # settings = QgsApplication.settings()
        # lang = settings.value("PoiskMore/language", "ru")
        # translator = QTranslator()
        # translator.load(f"poiskmore_{lang}.qm", os.path.join(os.path.dirname(__file__), "i18n"))
        # QgsApplication.installTranslator(translator)

        self.menu = "Поиск-Море"

        form_map = [
            ("Расчёт дрейфа",              "DriftCalculationForm",         "dialogs.dialog_driftcalculation"),
            ("Параметры поиска",           "SearchAreaForm",                "dialogs.dialog_searcharea"),
            ("Создание SITREP",            "SitrepForm",                    "dialogs.dialog_sitrep"),
            ("Отправка SITREP",            "SitrepSendForm",                "dialogs.dialog_sitrepsend"),
            ("Формирование отчёта",        "ReportGenerationForm",          "dialogs.dialog_reportgeneration"),
            ("Поступившая тревога",        "IncomingAlertForm",             "dialogs.dialog_incomingalert"),
            ("Координация с SRU",          "CoordinationForm",              "dialogs.dialog_coordination"),
            ("Карта и слои",               "GeoMapViewerForm",              "dialogs.dialog_geomapviewer"),
            ("Настройки",                  "SettingsForm",                  "dialogs.dialog_settings"),
            ("Журнал действий",            "OperatorLogForm",               "dialogs.dialog_operatorlog"),
            ("Отчёт в ГМСКЦ",              "GMSKCCenterReportForm",         "dialogs.dialog_gmskcreport"),
            ("Сценарий IAMSAR",            "IAMSARScenarioForm",            "dialogs.dialog_iamsarscenario"),
            ("Статус внешних модулей",     "ExternalSystemStatusForm",      "dialogs.dialog_externalsystemstatus")
        ]

        for label, class_name, module_path in form_map:
            action = QAction(label, self.iface.mainWindow())
            action.triggered.connect(self.make_form_opener(class_name, module_path))
            self.iface.addPluginToMenu(self.menu, action)
            # Специально для SearchAreaForm передаём mapCanvas
            if class_name == "SearchAreaForm":
                action.triggered.disconnect()
                action.triggered.connect(self.make_searcharea_opener(class_name, module_path))
            self.actions.append(action)

    def make_searcharea_opener(self, class_name, module_path):
        def open_searcharea():
            module = __import__(module_path, fromlist=[class_name])
            dlg_class = getattr(module, class_name)
            dlg = dlg_class()
            dlg.canvas = self.iface.mapCanvas()
            dlg.exec_()
        return open_searcharea

    def make_form_opener(self, class_name, module_path):
        def open_dialog():
            module = __import__(module_path, fromlist=[class_name])
            dlg_class = getattr(module, class_name)
            dlg = dlg_class()
            dlg.exec_()
        return open_dialog

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)