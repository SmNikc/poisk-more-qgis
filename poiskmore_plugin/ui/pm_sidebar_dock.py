# -*- coding: utf-8 -*-
"""
ui/pm_sidebar_dock.py — боковая панель «Поиск‑Море»
Функциональность:
  • Базовые карты: Esri World Ocean Base / OpenStreetMap
  • Overlay OpenSeaMap Seamarks (видимость, непрозрачность, поднять/опустить)
  • Тематические слои: чекбоксы, «вкл/выкл все», фильтр‑поиск, авто‑восстановление связей (SHP→GPKG/WMS),
    авто‑применение QML‑стилей (styles/sar_regions.qml, styles/sarrcc.qml)
  • МСКЦ/МСПЦ: список из векторного слоя или data/centers.json, zoom‑to
  • Health‑check картографических сервисов (XYZ/WMS/WFS)
  • Мини‑легенда для активных WMS‑слоёв (GetLegendGraphic)
Сохранение пользовательских настроек через QSettings("PoiskMore","PluginSidebar").
"""
from typing import Optional, List, Tuple
import os, json, urllib.parse, urllib.request

from qgis.PyQt.QtCore import Qt, QSettings, QSize
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QCheckBox,
    QPushButton, QSlider, QListWidget, QListWidgetItem, QLineEdit, QGroupBox,
    QMessageBox
)
from qgis.core import (
    QgsProject, QgsRasterLayer, QgsVectorLayer, QgsFeatureRequest,
    QgsRectangle, QgsApplication, Qgis
)

# ---------- Константы ----------
ESRI_OCEAN_XYZ = "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"
OSM_XYZ        = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
SEAMARKS_XYZ   = "https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png"

GROUP_BASEMAP  = "Картографическая основа"
GROUP_THEMATIC = "Тематические слои"
GROUP_CENTERS  = "Районы МСКЦ/МСПЦ"

LAYER_ESRI     = "Esri World Ocean Base"
LAYER_OSM      = "OpenStreetMap"
LAYER_SEAMARKS = "OpenSeaMap Seamarks"

STYLE_MAP = {
    "sarregion": "styles/sar_regions.qml",
    "sarrcc":    "styles/sarrcc.qml"
}

# ---------- Вспомогательные ----------
def _layer_tree_node(layer):
    root = QgsProject.instance().layerTreeRoot()
    return root.findLayer(layer.id()) if layer else None

def _xyz_layer(name: str, url: str, zmin=0, zmax=19) -> QgsRasterLayer:
    # Для XYZ в QGIS провайдер указывается как "wms" с type=xyz в строке источника
    src = f"type=xyz&url={url}&zmin={zmin}&zmax={zmax}"
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

# ---------- Восстановление связей данных ----------
class DataRelinker:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
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

# ---------- Менеджер базовых карт ----------
class BasemapManager:
    def __init__(self, settings: QSettings):
        self.stg = settings
        self._ensure_layers()

    def _ensure_layers(self):
        esri = _find_layer_by_name(LAYER_ESRI)
        if not esri:
            # При необходимости укажите API‑key в url (Esri Basemap Styles API) — здесь используем общедоступный raster endpoint
            esri = _xyz_layer(LAYER_ESRI, ESRI_OCEAN_XYZ)
            _add_to_group(esri, GROUP_BASEMAP, index=1)
        osm = _find_layer_by_name(LAYER_OSM)
        if not osm:
            osm = _xyz_layer(LAYER_OSM, OSM_XYZ)
            _add_to_group(osm, GROUP_BASEMAP, index=0)
        sm = _find_layer_by_name(LAYER_SEAMARKS)
        if not sm:
            sm = _xyz_layer(LAYER_SEAMARKS, SEAMARKS_XYZ)
            sm.setOpacity(0.9)
            _add_to_group(sm, GROUP_BASEMAP, index=2)

        want = self.stg.value("base", LAYER_ESRI, type=str)
        self.set_base(want)
        self.set_seamarks_visible(self.stg.value("seamarks_vis", True, type=bool))
        self.set_seamarks_opacity(float(self.stg.value("seamarks_op", 0.9)))

    def _set_layer_visible(self, layer, visible: bool):
        node = _layer_tree_node(layer)
        if node:
            node.setItemVisibilityChecked(visible)

    def set_base(self, name: str):
        e = _find_layer_by_name(LAYER_ESRI)
        o = _find_layer_by_name(LAYER_OSM)
        self._set_layer_visible(e, name == LAYER_ESRI)
        self._set_layer_visible(o, name == LAYER_OSM)
        self.stg.setValue("base", name)

    def set_seamarks_visible(self, vis: bool):
        sm = _find_layer_by_name(LAYER_SEAMARKS)
        self._set_layer_visible(sm, vis)
        self.stg.setValue("seamarks_vis", vis)

    def set_seamarks_opacity(self, alpha: float):
        sm = _find_layer_by_name(LAYER_SEAMARKS)
        if sm: sm.setOpacity(max(0.0, min(1.0, alpha)))
        self.stg.setValue("seamarks_op", alpha)

    def raise_seamarks(self):
        # Поднимаем overlay поверх базовых
        root = QgsProject.instance().layerTreeRoot()
        grp = root.findGroup(GROUP_BASEMAP)
        if not grp: return
        for node in grp.findLayers():
            if node.layer().name() == LAYER_SEAMARKS:
                layer = node.layer()
                # QgsLayerTreeGroup.moveLayer() был удалён в QGIS 3.40.
                # Удаляем слой из группы и вставляем его в начало, чтобы
                # сохранить прежнее поведение "поднять overlay".
                grp.removeLayer(layer)
                grp.insertLayer(0, layer)
                break

# ---------- Основной Dock ----------
class PoiskMoreSidebarDock(QDockWidget):
    def __init__(self, iface, plugin_dir: str, parent=None):
        super().__init__("Поиск‑Море · Навигация", parent)
        self.iface = iface
        self.plugin_dir = plugin_dir
        self.stg = QSettings("PoiskMore", "PluginSidebar")
        self.basemap = BasemapManager(self.stg)
        self.relinker = DataRelinker(plugin_dir)

        self.setObjectName("PoiskMoreSidebarDock")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setMinimumWidth(360)

        self._build_ui()
        self._bind_signals()
        self._ensure_groups()
        self._try_restore_thematic()
        self._load_centers()
        self._refresh_legend()

    # --- UI ---
    def _build_ui(self):
        root = QWidget(self)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(8,8,8,8)
        layout.setSpacing(8)

        # БАЗОВЫЕ КАРТЫ
        gb_base = QGroupBox("Картографическая основа")
        vb = QVBoxLayout(gb_base)
        hb = QHBoxLayout()
        self.rbEsri = QRadioButton("Esri Ocean")
        self.rbOSM  = QRadioButton("OpenStreetMap")
        self.rbEsri.setChecked(self.stg.value("base", LAYER_ESRI, type=str) == LAYER_ESRI)
        self.rbOSM.setChecked(not self.rbEsri.isChecked())
        hb.addWidget(self.rbEsri); hb.addWidget(self.rbOSM)
        vb.addLayout(hb)
        self.cbSeamarks = QCheckBox("OpenSeaMap Seamarks (overlay)")
        self.cbSeamarks.setChecked(self.stg.value("seamarks_vis", True, type=bool))
        vb.addWidget(self.cbSeamarks)
        hb2 = QHBoxLayout()
        hb2.addWidget(QLabel("Прозрачность seamarks"))
        self.slSeamarks = QSlider(Qt.Horizontal); self.slSeamarks.setRange(0,100)
        self.slSeamarks.setValue(int(float(self.stg.value("seamarks_op", 0.9))*100))
        self.btnRaise = QPushButton("Поднять overlay")
        hb2.addWidget(self.slSeamarks); hb2.addWidget(self.btnRaise)
        vb.addLayout(hb2)
        layout.addWidget(gb_base)

        # ТЕМАТИКА
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

        # ЦЕНТРЫ
        gb_centers = QGroupBox("МСКЦ / МСПЦ")
        vc = QVBoxLayout(gb_centers)
        self.listCenters = QListWidget(); self.listCenters.setMinimumHeight(150)
        self.btnZoom = QPushButton("Приблизить к центру")
        vc.addWidget(self.listCenters); vc.addWidget(self.btnZoom)
        layout.addWidget(gb_centers)

        # СЕРВИСЫ и ЛЕГЕНДА
        gb_svc = QGroupBox("Сервисы и легенда")
        vs = QVBoxLayout(gb_svc)
        self.btnHealth = QPushButton("Проверка сервисов (XYZ/WMS/WFS)")
        vs.addWidget(self.btnHealth)
        self.listLegend = QListWidget(); self.listLegend.setIconSize(QSize(64,24))
        self.listLegend.setMinimumHeight(120)
        vs.addWidget(QLabel("Легенда активных WMS‑слоёв:"))
        vs.addWidget(self.listLegend)
        layout.addWidget(gb_svc)

        layout.addStretch(1)
        self.setWidget(root)

        # Первичное заполнение «Тематические слои»
        self._refresh_thematic_list()

    # --- Сигналы ---
    def _bind_signals(self):
        self.rbEsri.toggled.connect(lambda on: on and self.basemap.set_base(LAYER_ESRI))
        self.rbOSM.toggled.connect(lambda on: on and self.basemap.set_base(LAYER_OSM))
        self.cbSeamarks.toggled.connect(self.basemap.set_seamarks_visible)
        self.slSeamarks.valueChanged.connect(lambda v: self.basemap.set_seamarks_opacity(v/100.0))
        self.btnRaise.clicked.connect(self.basemap.raise_seamarks)

        self.cbAll.toggled.connect(self._toggle_all_thematic)
        self.leFilter.textChanged.connect(self._apply_filter)
        self.listThemes.itemChanged.connect(self._theme_item_changed)
        self.btnRepair.clicked.connect(self._repair_links)
        self.btnStyles.clicked.connect(self._apply_styles)

        zoom_handler = getattr(self, "_zoom_to_center", None)
        if zoom_handler:
            self.btnZoom.clicked.connect(zoom_handler)
        else:
            def _missing_zoom_handler():
                QMessageBox.warning(
                    self,
                    "Поиск‑Море",
                    "Эта сборка плагина не поддерживает приближение к центрам."
                )

            self._missing_zoom_handler = _missing_zoom_handler
            self.btnZoom.clicked.connect(self._missing_zoom_handler)
            QgsApplication.messageLog().logMessage(
                "Zoom-to-center handler is missing; falling back to stub.",
                "Poisk-More",
                Qgis.Warning
            )
        self.btnHealth.clicked.connect(self._check_services)

    # --- Инициализация групп ---
    def _ensure_groups(self):
        root = QgsProject.instance().layerTreeRoot()
        if not root.findGroup(GROUP_BASEMAP):  root.addGroup(GROUP_BASEMAP)
        if not root.findGroup(GROUP_THEMATIC): root.addGroup(GROUP_THEMATIC)
        if not root.findGroup(GROUP_CENTERS):  root.addGroup(GROUP_CENTERS)

    # --- Тематика ---
    def _try_restore_thematic(self):
        # Если в тематике пусто — попытаемся вернуть SAR‑слои
        if not _vector_layers_in_group(GROUP_THEMATIC):
            restored = self.relinker.relink_by_names(["sarregion_m", "sarrcc_m"])
            if restored:
                QgsApplication.messageLog().logMessage(
                    f"Восстановлены тематические слои: {', '.join([l.name() for l in restored])}",
                    "Poisk-More", 0
                )
        self._refresh_thematic_list()

    def _refresh_thematic_list(self):
        self.listThemes.blockSignals(True)
        self.listThemes.clear()
        root = QgsProject.instance().layerTreeRoot()
        grp = root.findGroup(GROUP_THEMATIC)
        if grp:
            for node in grp.findLayers():
                lyr = node.layer()
                item = QListWidgetItem(lyr.name())
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if node.itemVisibilityChecked() else Qt.Unchecked)
                item.setData(Qt.UserRole, node.layer().id())
                self.listThemes.addItem(item)
        self.listThemes.blockSignals(False)

    def _apply_filter(self, text: str):
        text = (text or "").lower()
        for i in range(self.listThemes.count()):
            it = self.listThemes.item(i)
            it.setHidden(text not in it.text().lower())

    def _toggle_all_thematic(self, on: bool):
        root = QgsProject.instance().layerTreeRoot()
        grp = root.findGroup(GROUP_THEMATIC)
        if not grp: return
        for node in grp.children():
            try:
                node.setItemVisibilityChecked(on)
            except Exception:
                pass
        self._refresh_thematic_list()

    def _theme_item_changed(self, item: QListWidgetItem):
        lyr_id = item.data(Qt.UserRole)
        root = QgsProject.instance().layerTreeRoot()
        grp = root.findGroup(GROUP_THEMATIC)
        if not grp: return
        for node in grp.findLayers():
            if node.layerId() == lyr_id:
                node.setItemVisibilityChecked(item.checkState() == Qt.Checked)
                break

    def _apply_styles(self):
        count = 0
        for lyr in _vector_layers_in_group(GROUP_THEMATIC):
            sp = _guess_style_path(self.plugin_dir, lyr.name())
            if sp:
                ok, err = lyr.loadNamedStyle(sp)
                if ok:
                    lyr.triggerRepaint(); count += 1
        QMessageBox.information(self, "Поиск‑Море", f"Применены стили: {count}")

    def _repair_links(self):
        restored = self.relinker.relink_by_names(["sarregion_m", "sarrcc_m"])
        if not restored:
            QMessageBox.information(self, "Поиск‑Море", "Не найдено подходящих источников для восстановления.")
        else:
            self._refresh_thematic_list()

    # --- Центры ---
    def _load_centers(self):
        self.listCenters.clear()
        # 1) ищем подходящий векторный слой
        lyr = None
        for L in QgsProject.instance().mapLayers().values():
            if isinstance(L, QgsVectorLayer):
                nm = L.name().lower()
                if any(k in nm for k in ("mskc","mspc","mrcc","центр")):
                    fields = [f.name().lower() for f in L.fields()]
                    if any(x in fields for x in ("name","title","naim","center","center_name")):
                        lyr = L; break
        if lyr:
            name_field = None
            for prefer in ("name","title","naim","center_name"):
                if prefer in [f.name().lower() for f in lyr.fields()]:
                    name_field = prefer; break
            if name_field:
                for f in lyr.getFeatures(QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry)):
                    nm = f[name_field]
                    if not nm: continue
                    it = QListWidgetItem(str(nm))
                    it.setData(Qt.UserRole, ("layer", (lyr.id(), f.id())))
                    self.listCenters.addItem(it)
        # 2) fallback: centers.json
        if self.listCenters.count() == 0:
            fp = os.path.join(self.plugin_dir, "data", "centers.json")
            if os.path.exists(fp):
                try:
                    data = json.load(open(fp,"r",encoding="utf-8"))
                    for c in data:
                        nm = c.get("name") or c.get("title")
                        bbox = c.get("bbox")
                        if not nm: continue
                        it = QListWidgetItem(str(nm))
                        it.setData(Qt.UserRole, ("json", bbox))
                        self.listCenters.addItem(it)
                except Exception as e:
                    QgsApplication.messageLog().logMessage(f"centers.json error: {e}", "Poisk-More", 2)

    def _zoom_to_center(self):
        it = self.listCenters.currentItem()
        if not it:
            QMessageBox.information(self, "Поиск‑Море", "Выберите центр.")
            return
        mode, payload = it.data(Qt.UserRole)
        if mode == "json" and payload:
            xmin,ymin,xmax,ymax = payload
            rect = QgsRectangle(xmin,ymin,xmax,ymax)
            self.iface.mapCanvas().setExtent(rect); self.iface.mapCanvas().refresh(); return
        if mode == "layer":
            lyr_id, fid = payload
            lyr = QgsProject.instance().mapLayer(lyr_id)
            if isinstance(lyr, QgsVectorLayer):
                for f in lyr.getFeatures(QgsFeatureRequest(fid)):
                    g = f.geometry()
                    if g and not g.isEmpty():
                        self.iface.mapCanvas().setExtent(g.boundingBox())
                        self.iface.mapCanvas().refresh(); return
        QMessageBox.warning(self, "Поиск‑Море", "Не удалось приблизить к выбранному центру.")

    # --- Health‑check сервисов и мини‑легенда ---
    def _check_services(self):
        msgs = []
        # XYZ endpoints
        for name, url in [(LAYER_ESRI, ESRI_OCEAN_XYZ), ("OSM", OSM_XYZ), ("Seamarks", SEAMARKS_XYZ)]:
            test = url.replace("{z}","3").replace("{x}","4").replace("{y}","2")
            ok = self._probe_url(test)
            msgs.append(f"[XYZ] {name}: {'OK' if ok else 'FAIL'}")
        # WMS/WFS в проекте
        for lyr in QgsProject.instance().mapLayers().values():
            if isinstance(lyr, QgsRasterLayer) and lyr.providerType().lower()=="wms":
                ok = self._probe_wms_layer(lyr)
                msgs.append(f"[WMS] {lyr.name()}: {'OK' if ok else 'FAIL'}")
        QMessageBox.information(self, "Проверка сервисов", "\n".join(msgs))
        self._refresh_legend()

    def _probe_url(self, url: str) -> bool:
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"PoiskMore/1.0"})
            with urllib.request.urlopen(req, timeout=6) as r:
                return (200 <= r.status < 400)
        except Exception:
            return False

    def _parse_wms_source(self, src: str) -> Tuple[Optional[str], Optional[str]]:
        # Пример src: "url=https://host/geoserver/wms&layers=poisk:sarregion_m&format=image/png&crs=EPSG:3857"
        parts = {}
        for token in src.split("&"):
            if "=" in token:
                k,v = token.split("=",1)
                parts[k]=v
        base = parts.get("url"); layers = parts.get("layers")
        return base, layers

    def _probe_wms_layer(self, lyr: QgsRasterLayer) -> bool:
        base, layers = self._parse_wms_source(lyr.source())
        if not base or not layers: return False
        params = {"SERVICE":"WMS","REQUEST":"GetCapabilities","VERSION":"1.3.0"}
        url = f"{base}?{urllib.parse.urlencode(params)}"
        return self._probe_url(url)

    def _legend_url(self, base: str, layer_name: str) -> str:
        params = {"SERVICE":"WMS","REQUEST":"GetLegendGraphic","FORMAT":"image/png","LAYER":layer_name}
        return f"{base}?{urllib.parse.urlencode(params)}"

    def _refresh_legend(self):
        self.listLegend.clear()
        for lyr in QgsProject.instance().mapLayers().values():
            if isinstance(lyr, QgsRasterLayer) and lyr.providerType().lower()=="wms":
                # Показываем только видимые
                node = _layer_tree_node(lyr)
                if not node or not node.itemVisibilityChecked():
                    continue
                base, layers = self._parse_wms_source(lyr.source())
                if not base or not layers: continue
                for ln in layers.split(","):
                    url = self._legend_url(base, ln)
                    icon = self._fetch_legend_icon(url)
                    it = QListWidgetItem(QIcon(icon) if icon else QIcon(), f"{lyr.name()} • {ln}")
                    self.listLegend.addItem(it)

    def _fetch_legend_icon(self, url: str) -> Optional[QPixmap]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"PoiskMore/1.0"})
            data = urllib.request.urlopen(req, timeout=6).read()
            pix = QPixmap(); pix.loadFromData(data, "PNG")
            return pix
        except Exception:
            return None

# ---------- Фабрика ----------
def ensure_pm_sidebar_dock(iface, plugin_dir: str) -> PoiskMoreSidebarDock:
    dock = PoiskMoreSidebarDock(iface, plugin_dir, parent=iface.mainWindow())
    iface.addDockWidget(Qt.LeftDockWidgetArea, dock)
    dock.show()
    return dock
