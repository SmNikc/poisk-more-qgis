# Хранение инцидентов в JSON. Улучшен:
# Try-except для ошибок чтения/записи.

import json
import os

def save_incident_to_json(data, path="incident_log.json"):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        else:
            all_data = []

        all_data.append(data)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Ошибка] Сохранение инцидента: {e}")
