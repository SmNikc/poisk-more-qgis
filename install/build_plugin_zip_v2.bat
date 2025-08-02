@echo off
chcp 65001 >nul
cd /d C:\Projects\poisk-more-qgis\install
C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe "C:\Projects\poisk-more-qgis\install\generate_html_from_directory.py" "C:\Projects\poisk-more-qgis" "C:\Projects\poisk-more-qgis_output\Содержимое_проекта.html"
pause

cd /d C:\Projects\poisk-more-qgis
powershell -Command "Compress-Archive -Path 'poiskmore_plugin' -DestinationPath 'install\poiskmore_plugin.qgis.zip' -Force"