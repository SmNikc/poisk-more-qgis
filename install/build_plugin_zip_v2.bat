@echo off
chcp 65001 >nul
cd /d C:\Projects\poisk_more_output
python.exe "C:\Projects\poisk_more_output\generate_plagin(poisk_more)_html_from_directory.py" "C:\Projects\poisk_more" "C:\Projects\poisk_more_output\Содержимое_проекта(poisk_more).html"
pause

cd /d C:\Projects\poisk-more-qgis
powershell -Command "Compress-Archive -Path 'poiskmore_plugin' -DestinationPath 'install\poiskmore_plugin.qgis.zip' -Force"