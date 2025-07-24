@echo off
chcp 65001 >nul

echo 🔄 Создание архива poiskmore_plugin.qgis.zip...

cd /d C:\Projects\poisk-more-qgis

if exist install\poiskmore_plugin.qgis.zip (
    del /f install\poiskmore_plugin.qgis.zip
)

powershell -Command "Compress-Archive -Path 'poiskmore_plugin\*' -DestinationPath 'install\poiskmore_plugin.qgis.zip'"

echo ✅ Архив создан: install\poiskmore_plugin.qgis.zip
pause