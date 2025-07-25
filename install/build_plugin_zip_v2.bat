@echo off
cd /d C:\Projects\poisk-more-qgis
powershell -Command "Compress-Archive -Path 'poiskmore_plugin' -DestinationPath 'install\poiskmore_plugin.qgis.zip' -Force"