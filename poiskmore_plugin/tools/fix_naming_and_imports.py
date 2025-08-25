import os, re, shutil

ROOT = r"C:\Projects\poisk-more-qgis\poiskmore_plugin"

RENAMES = {
    os.path.join(ROOT, "calculations", "drift-calculator.py"):
        os.path.join(ROOT, "calculations", "drift_calculator.py"),
    os.path.join(ROOT, "calculations", "search-area-calculator.py"):
        os.path.join(ROOT, "calculations", "search_area_calculator.py"),
    os.path.join(ROOT, "calculations", "drift_calculator_qgis.py.py"):
        os.path.join(ROOT, "calculations", "drift_calculator_qgis.py"),
}

for src, dst in RENAMES.items():
    if os.path.exists(src):
        print(f"REN: {src} -> {dst}")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)

# фикса импортов вида "from ..calculations.drift_calculator import ..." внутри пакета
for dirpath, _, files in os.walk(ROOT):
    for f in files:
        if f.endswith(".py"):
            p = os.path.join(dirpath, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as r:
                text = r.read()
            new_text = re.sub(
                r"\bfrom\s+drift_calculator\s+import\b",
                "from ..calculations.drift_calculator import",
                text
            )
            if new_text != text:
                print(f"FIX import in: {p}")
                with open(p, "w", encoding="utf-8") as w:
                    w.write(new_text)

# гарантируем __init__.py в calculations
calc_pkg = os.path.join(ROOT, "calculations", "__init__.py")
if not os.path.exists(calc_pkg):
    with open(calc_pkg, "w", encoding="utf-8") as w:
        w.write("# package marker\n")
    print("ADD:", calc_pkg)

print("Done.")
