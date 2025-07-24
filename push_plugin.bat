@echo off
cd /d C:\Projects\poisk-more-qgis
echo Добавление всех изменений...
git add .
set /p MSG=Введите комментарий коммита:
git commit -m "%MSG%"
echo Отправка на GitHub...
git push
pause