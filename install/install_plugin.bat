:: install_plugin.bat
:: Устанавливает плагин локально в QGIS (Windows)

@echo off
set PLUGIN_NAME=poiskmore_plugin
set QGIS_PROFILE=%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins

echo Удаление предыдущей версии...
rmdir /S /Q "%QGIS_PROFILE%\%PLUGIN_NAME%"

echo Копирование новой версии...
xcopy /E /I /Y "C:\Projects\poisk-more-qgis" "%QGIS_PROFILE%\%PLUGIN_NAME%"

echo Готово. Запустите QGIS и активируйте плагин "Поиск-Море".
pause
