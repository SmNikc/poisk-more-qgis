# CODEX: пошаговая настройка окружения для `poisk-more-qgis`

## 1) Создайте Environment
- Name: **poisk-more-dev**
- Container image: **Preinstalled packages → universal**
- Agent internet access: **On**

## 2) Environment variables
Добавьте следующие переменные (Environment → Variables):
```
QT_QPA_PLATFORM=offscreen
DISPLAY=:99
QGIS_PREFIX_PATH=/usr
PYTHONPATH=/usr/share/qgis/python
QGIS_PROVIDER_FILE=/usr/lib/qgis/plugins
ACTIVEMQ_HOST=localhost
ACTIVEMQ_PORT=61616
```
> При необходимости добавьте Secrets (например, GH_TOKEN).

## 3) Setup Script
Скопируйте **полностью** содержимое файла:
`C:\Projects\poisk-more-qgis\codex\setup_qgis_activemq.sh`

## 4) Smoke‑тесты после старта окружения
Откройте терминал в CODEX и выполните:
```bash
python3 scripts/smoke_qgis.py
bash scripts/codex_verify.sh
```
Ожидаемый вывод: `QGIS import OK` и `ActiveMQ is up`.

## 5) Полезные команды
```bash
# Просмотр логов Xvfb / ActiveMQ
tail -n 100 /tmp/xvfb.log
tail -n 100 /tmp/activemq.log

# Проверка qgis_process
qgis_process --help || true
```

## 6) Если установка QGIS упала на ключе
Запустите патч‑скрипт:
```bash
bash scripts/patch_qgis_key.sh
```
Он переключит ключ на `qgis-archive-keyring.gpg` и обновит apt‑источники.