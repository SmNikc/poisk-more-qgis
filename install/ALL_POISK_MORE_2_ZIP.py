import os
import zipfile

src = r"C:\Projects\poisk-more-qgis"
dst = r"C:\Projects\poisk-more-qgis_output\poisk-more-qgis.zip"
excludes = {".git", "docker"}

os.makedirs(os.path.dirname(dst), exist_ok=True)

with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(src):
        # Исключаем папки .git и docker на любом уровне
        dirs[:] = [d for d in dirs if d not in excludes]
        
        for file in files:
            fullpath = os.path.join(root, file)
            arcname = os.path.relpath(fullpath, src)
            zipf.write(fullpath, arcname)
            print(f"Добавлен: {arcname}")

print(f"✅ Архив создан: {dst}")