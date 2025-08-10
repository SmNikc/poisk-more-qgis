# test_plugin_load.py (тестовый скрипт загрузки плагина)
# Комментарий: Автоматический тест для проверки корректности загрузки плагина. 
# Создает мок-объекты QGIS интерфейса и тестирует инициализацию и выгрузку плагина.
from qgis.core import QgsApplication
app = QgsApplication([], False)
app.initQgis()

# Mock iface
class MockIface:
    def mainWindow(self):
        class MockMenuBar:
            def addMenu(self, menu):
                print("Menu added", menu.title())
                return menu

            def removeAction(self, *args):
                print("Menu removed")

        class MockWindow:
            def menuBar(self):
                return MockMenuBar()

        return MockWindow()

    def messageBar(self):
        class MockBar:
            def pushMessage(self, *args):
                print(args)
        return MockBar()

from poiskmore_plugin import classFactory
plugin = classFactory(MockIface())
plugin.initGui()
plugin.unload()

app.exitQgis()
print("Тест загрузки пройден")
