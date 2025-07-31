@echo off
chcp 65001 >nul
cd /d C:\Projects\poisk-more-qgis\install
"C:\Python313\python.exe" "C:\Projects\poisk-more-qgis\install\generate_html_from_directory.py"
pause

cd /d C:\Projects\poisk-more-qgis
powershell -Command "Compress-Archive -Path 'poiskmore_plugin' -DestinationPath 'install\poiskmore_plugin.qgis.zip' -Force"