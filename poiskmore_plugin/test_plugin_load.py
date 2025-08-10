# test_plugin_load.py (тестовый скрипт загрузки плагина)
# Комментарий: Автоматический тест для проверки корректности загрузки плагина. 
# Создает мок-объекты QGIS интерфейса и тестирует инициализацию и выгрузку плагина.
from qgis.core import QgsApplication
app = QgsApplication([], False)
app.initQgis()

# Mock iface
class MockIface:
    def mainWindow(self):
        class MockWindow:
            pass
        return MockWindow()
    
    def messageBar(self):
        class MockBar:
            def pushMessage(self, *args):
                print(args)
        return MockBar()
    
    def addPluginToMenu(self, *args):
        print("Menu added")
    
    def removePluginMenu(self, *args):
        print("Menu removed")

from poiskmore_plugin import classFactory
plugin = classFactory(MockIface())
plugin.initGui()
plugin.unload()

app.exitQgis()
print("Тест загрузки пройден")