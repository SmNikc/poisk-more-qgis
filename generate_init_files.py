import os

PROJECT_ROOT = r"C:\Projects\poisk-more-qgis"  # ← укажите при необходимости

def ensure_init_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        # Пропускаем скрытые и системные папки
        if any(part.startswith('.') for part in dirpath.split(os.sep)):
            continue

        init_path = os.path.join(dirpath, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w", encoding="utf-8") as f:
                f.write("# __init__.py сгенерирован автоматически\n")
            print(f"✅ Добавлен: {init_path}")
        else:
            print(f"✔️ Уже есть: {init_path}")

if __name__ == "__main__":
    ensure_init_files(PROJECT_ROOT)