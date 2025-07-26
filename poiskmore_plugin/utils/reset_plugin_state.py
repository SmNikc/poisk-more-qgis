pythonimport os

def reset_plugin_state(files=None):
    if files is None:
        files = ["operator_log.txt", "log_summary.txt", "incident_log.json"]
    removed = []
    for f in files:
        try:
            if os.path.exists(f):
                os.remove(f)
                removed.append(f)
        except OSError as e:
            print(f"Ошибка удаления {f}: {e}")
    return removed