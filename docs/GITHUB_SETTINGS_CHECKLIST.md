# GitHub: General → Actions → Data controls → Environments (пошагово)

## 1) General
- Description, Topics → заполнить
- Merge button → оставить **Squash merge** (по желанию)
- Rules / Branch protection (Rulesets):
  - Для `main`: запрет прямых push, обязательные PR‑review, required checks (CI).

## 2) Actions → General
- Actions permissions → Allow all actions (или ограничить Verified)
- Workflow permissions → **Read and write**

## 3) Actions → Data controls
- Artifacts & Logs retention → 30–90 дней (рекомендация: 30d)

## 4) Environments
Создайте `dev`, `ci`, `prod`. В Variables задайте:
```
QT_QPA_PLATFORM=offscreen
DISPLAY=:99
QGIS_PREFIX_PATH=/usr
PYTHONPATH=/usr/share/qgis/python
QGIS_PROVIDER_FILE=/usr/lib/qgis/plugins
```
Для `prod`: включите Protection (required reviewers, branches = `main`/tags `v*`).

## 5) Автоматизация правил (опционально)
Если установлен GitHub CLI:
```bash
bash scripts/apply_ruleset.sh owner=SmNikc repo=poisk-more-qgis token=YOUR_GH_TOKEN
```
Скрипт применит пример ruleset из `scripts/ruleset_main.json`.