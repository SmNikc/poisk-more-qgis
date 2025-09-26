# -*- coding: utf-8 -*-
"""
ui/pm_sidebar_dock.py — боковая панель «Поиск‑Море»
(исправлено: безопасная загрузка QML-стилей + корректные пути + логирование)
"""
from typing import Optional, List, Tuple
import os, json, urllib.parse, urllib.request
import traceback

from qgis.PyQt.QtCore import Qt, QSettings, QSize
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QCheckBox,
    QPushButton, QSlider, QListWidget, QListWidgetItem, QLineEdit, QGroupBox,
    QMessageBox
)
from qgis.core import (
    QgsProject, QgsRasterLayer, QgsVectorLayer, QgsFeatureRequest,
    QgsRectangle, QgsApplication, Qgis, QgsWkbTypes,
    QgsSingleSymbolRenderer, QgsMarkerSymbol, QgsLineSymbol, QgsFillSymbol
)

# Логирование в plugin.log
try:
    from ..operation_logger import setup_logger
    _PLUGIN_DIR = os.path.dirname(os.path.dirname(__file__))
    logger = setup_logger(_PLUGIN_DIR)
except Exception:
    import logging
    logger = logging.getLogger("poiskmore_plugin_fallback")
    logger.addHandler(logging.NullHandler())

# ---------- Константы ----------
ESRI_OCEAN_XYZ = "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"
OPENSEAMAP_TMS = "https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"

GROUP_BASEMAPS = "Базовые карты"
GROUP_THEMATIC = "Тематические слои"
STYLE_MAP = {
    "sarregion": "styles/region_style.qml",
    "sarrcc": "styles/sru_style.qml",
    "search": "styles/search_scheme_style.qml",
}

def _xyz_layer(url: str, name: str) -> QgsRasterLayer:
    src = f"type=xyz&url={url}"
    return QgsRasterLayer(src, name, "wms")

def _add_to_group(layer, group_name: str, index: int = 0):
    prj = QgsProject.instance()
    root = prj.layerTreeRoot()
    grp = root.findGroup(group_name)
    if grp is None:
        grp = root.addGroup(group_name)
    prj.addMapLayer(layer, False)
    grp.insertLayer(index, layer)
    return grp

def _find_layer_by_name(name: str):
    for lyr in QgsProject.instance().mapLayers().values():
        if lyr.name().strip().lower() == name.strip().lower():
            return lyr
    return None

def _vector_layers_in_group(group_name: str) -> List[QgsVectorLayer]:
    root = QgsProject.instance().layerTreeRoot()
    grp = root.findGroup(group_name)
    out = []
    if grp:
        for ch in grp.findLayers():
            lyr = ch.layer()
            if isinstance(lyr, QgsVectorLayer):
                out.append(lyr)
    return out

def _guess_style_path(plugin_dir: str, layer_name: str) -> Optional[str]:
    lname = layer_name.lower()
    for key, rel in STYLE_MAP.items():
        if key in lname:
            p = os.path.join(plugin_dir, rel)
            return p if os.path.exists(p) else None
    return None

def _apply_safe_default_symbol(layer: QgsVectorLayer):
    """Простой рендер на случай ошибок QML."""
    try:
        if layer.geometryType() == QgsWkbTypes.PolygonGeometry:
            sym = QgsFillSymbol.createSimple({
                "color": "255,192,203,120",
                "outline_color": "35,35,35,255",
                "outline_width": "0.6",
            })
        elif layer.geometryType() == QgsWkbTypes.LineGeometry:
            sym = QgsLineSymbol.createSimple({
                "line_color": "0,0,0,255",
                "line_width": "0.8",
            })
        else:
            sym = QgsMarkerSymbol.createSimple({
                "color": "255,0,0,255",
                "outline_color": "35,35,35,255",
                "size": "3"
            })
        layer.setRenderer(QgsSingleSymbolRenderer(sym))
        layer.triggerRepaint()
    except Exception:
        logger.exception("Fallback symbol failed")

def _safe_load_named_style(layer: QgsVectorLayer, style_path: str) -> bool:
    """
    Безопасная загрузка QML-стиля:
    - перехватывает любые исключения (в т.ч. «vector too long»)
    - пишет стек в plugin.log
    - включает запасной простой стиль
    """
    try:
        ok, msg = layer.loadNamedStyle(style_path)
        if not ok:
            raise RuntimeError(msg or "invalid QML")
        layer.triggerRepaint()
        return True
    except Exception as e:
        logger.error("loadNamedStyle failed for %s: %s\n%s",
                     layer.name(), e, traceback.format_exc())
        _apply_safe_default_symbol(layer)
        return False

# ---------- Восстановление связей данных ----------
class DataRelinker:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        # БЫЛО: os.path.join(plugin_dir, "data" "shapes") → "datashapes"
        # ИСПРАВЛЕНО: правильные пути с запятой
        self.search_dirs = [
            os.path.join(plugin_dir, "data", "shapes"),
            os.path.join(plugin_dir, "data"),
            plugin_dir
        ]

    def relink_by_names(self, expected: List[str]) -> List[QgsVectorLayer]:
        restored = []
        for nm in expected:
            if _find_layer_by_name(nm):
                continue
            candidate = self._find_candidate(nm)
            if candidate:
                v = QgsVectorLayer(candidate, nm, "ogr")
                if v.isValid():
                    _add_to_group(v, GROUP_THEMATIC, index=0)
                    restored.append(v)
        return restored

    def _find_candidate(self, layer_name: str) -> Optional[str]:
        base = layer_name.lower().replace(" ", "_")
        for d in self.search_dirs:
            if not os.path.isdir(d):
                continue
            for fn in os.listdir(d):
                low = fn.lower()
                # SHP / GeoJSON
                if (low.startswith(base) and low.endswith((".shp", ".geojson", ".json"))):
                    return os.path.join(d, fn)
                # GPKG: допустимо имя фичекласса ≠ имени файла
                if low.endswith(".gpkg"):
                    path = os.path.join(d, fn)
                    return f"{path}|layername={layer_name}"
        return None

# ---------- Основной UI ----------
class PmSidebarDock(QDockWidget):
    def __init__(self, iface, plugin_dir: str):
        super().__init__("Поиск‑Море — Навигация", iface.mainWindow())
        self.iface = iface
        self.plugin_dir = plugin_dir
        self.setObjectName("PmSidebarDock")

        w = QWidget(self)
        layout = QVBoxLayout(w)
        self.setWidget(w)

        # базовые карты
        gb_base = QGroupBox("Картографическая основа")
        vb = QVBoxLayout(gb_base)
        hb = QHBoxLayout()
        self.rbEsri = QRadioButton("Esri Ocean")
        self.rbOSM  = QRadioButton("OpenStreetMap")
        vb.addLayout(hb)
        hb.addWidget(self.rbEsri); hb.addWidget(self.rbOSM)
        self.cbSeamarks = QCheckBox("OpenSeaMap Seamarks (overlay)")
        vb.addWidget(self.cbSeamarks)
        hb2 = QHBoxLayout()
        hb2.addWidget(QLabel("Прозрачность seamarks"))
        self.slSeamarks = QSlider(Qt.Horizontal); self.slSeamarks.setRange(0,100); self.slSeamarks.setValue(90)
        self.btnRaise = QPushButton("Поднять overlay")
        hb2.addWidget(self.slSeamarks); hb2.addWidget(self.btnRaise)
        vb.addLayout(hb2)
        layout.addWidget(gb_base)

        # Тематика
        gb_themes = QGroupBox("Тематические слои")
        vt = QVBoxLayout(gb_themes)
        self.leFilter = QLineEdit(); self.leFilter.setPlaceholderText("Фильтр по имени слоя…")
        vt.addWidget(self.leFilter)
        self.cbAll = QCheckBox("Вкл/выкл все")
        vt.addWidget(self.cbAll)
        hb3 = QHBoxLayout()
        self.btnRepair = QPushButton("Восстановить связи")
        self.btnStyles = QPushButton("Применить стили")
        hb3.addWidget(self.btnRepair); hb3.addWidget(self.btnStyles)
        vt.addLayout(hb3)
        self.listThemes = QListWidget(); self.listThemes.setMinimumHeight(180)
        vt.addWidget(self.listThemes)
        layout.addWidget(gb_themes)

        # Привязки
        self.relinker = DataRelinker(self.plugin_dir)
        self._refresh_thematic_list()

        # Сигналы
        self.btnRepair.clicked.connect(self._repair_links)
        self.btnStyles.clicked.connect(self._apply_styles)

    # --- служебные методы ---
    def _refresh_thematic_list(self):
        self.listThemes.clear()
        themats = []
        root = QgsProject.instance().layerTreeRoot()
        grp = root.findGroup(GROUP_THEMATIC)
        if grp:
            for node in grp.findLayers():
                lyr = node.layer()
                themats.append((lyr.name(), lyr.id(), node.isVisible()))
        for nm, lyr_id, vis in themats:
            it = QListWidgetItem(nm)
            it.setData(Qt.UserRole, lyr_id)
            it.setCheckState(Qt.Checked if vis else Qt.Unchecked)
            self.listThemes.addItem(it)

    def _apply_styles(self):
        count_ok = 0
        count_err = 0
        for lyr in _vector_layers_in_group(GROUP_THEMATIC):
            sp = _guess_style_path(self.plugin_dir, lyr.name())
            if sp:
                if _safe_load_named_style(lyr, sp):
                    count_ok += 1
                else:
                    count_err += 1
        QMessageBox.information(
            self, "Поиск‑Море",
            f"Применены стили: {count_ok}. Ошибки: {count_err} (см. plugin.log)."
        )

    def _repair_links(self):
        restored = self.relinker.relink_by_names(["sarregion_m", "sarrcc_m"])
        if not restored:
            QMessageBox.information(self, "Поиск‑Море", "Не найдено подходящих источников для восстановления.")
        else:
            self._refresh_thematic_list()

# Фабричная функция
def ensure_pm_sidebar_dock(iface) -> PmSidebarDock:
    dock = None
    for d in iface.mainWindow().findChildren(QDockWidget):
        if d.objectName() == "PmSidebarDock":
            dock = d
            break
    if dock is None:
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        dock = PmSidebarDock(iface, plugin_dir)
        iface.addDockWidget(Qt.LeftDockWidgetArea, dock)
    return dock
