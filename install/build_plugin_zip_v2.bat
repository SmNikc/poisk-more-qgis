@echo off
chcp 1251 > nul
title Генерация HTML иC:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe ZIP архива плагина

echo Генерация HTML-ленты...

set "HTMLGEN=C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe"
set "SCRIPT=C:\Projects\poisk-more-qgis\install\generate_html_from_directory.py"
set "SOURCE=C:\Projects\poisk-more-qgis"
set "TARGET=C:\Projects\poisk-more-qgis_output\Содержимое_проекта.html"

%HTMLGEN% "%SCRIPT%" "%SOURCE%" "%TARGET%"

if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: HTML не сгенерирован.
    pause
    exit /b
) else (
    echo HTML готов.
)
pause
echo Упаковка ZIP-архива...
powershell -Command "Compress-Archive -Path 'C:\Projects\poisk-more-qgis\poiskmore_plugin' -DestinationPath 'C:\Projects\poisk-more-qgis\install\poiskmore_plugin.qgis.zip' -Force"
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: Архивация не удалась.
) else (
    echo ZIP-архив успешно создан.
)