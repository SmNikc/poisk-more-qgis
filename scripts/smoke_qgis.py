import os, sys
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
os.environ.setdefault("DISPLAY", ":99")

try:
    from qgis.core import QgsApplication
    print("QGIS import OK")
except Exception as e:
    print("QGIS import FAILED:", e)
    sys.exit(1)

print("Environment ready.")
