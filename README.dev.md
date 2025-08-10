# Поиск‑Море — Dev окружение (QGIS + ActiveMQ)

Этот комплект запускает локальную среду разработки, идентичную CI и Codex.

## Состав
- `docker-compose.dev.yml` — поднимает два сервиса: `qgis` и `activemq` (сборка из `./docker/qgis` и `./docker/activemq`).
- `scripts/smoke_qgis.py` — быстрый тест импортов QGIS (headless).
- Этот файл — краткая инструкция.

## Требования
- Docker Desktop 4.x+ (Windows) / Docker Engine 24.x+
- В каталоге проекта должны существовать:  
  - `C:\Projects\poisk-more-qgis\docker\qgis\Dockerfile` (образ QGIS c Python)  
  - `C:\Projects\poisk-more-qgis\docker\activemq\Dockerfile` (образ ActiveMQ)  

## Запуск
Откройте PowerShell или CMD:

```bat
cd C:\Projects\poisk-more-qgis
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml up -d
```

Проверка QGIS внутри контейнера:
```bat
docker exec -it pmq_qgis bash
python3 /workspace/scripts/smoke_qgis.py
```

Остановка окружения:
```bat
docker compose -f docker-compose.dev.yml down -v
```

## Примечания
- Сервис `qgis` стартует командой `sleep infinity` — это удобно для интерактивной отладки.
- Переменные среды (`QT_QPA_PLATFORM`, `DISPLAY`, пути QGIS) уже заданы для headless‑режима.
- ActiveMQ доступен на `http://localhost:8161` (логин/пароль по умолчанию в вашем образе).

## Пути
- Файл compose: `C:\Projects\poisk-more-qgis\docker-compose.dev.yml`
- Скрипт теста: `C:\Projects\poisk-more-qgis\scripts\smoke_qgis.py`
