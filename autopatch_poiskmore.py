# -*- coding: utf-8 -*-
"""
autopatch_poiskmore.py
Автоматическое внесение правок в файлы плагина «Поиск‑Море» для подключения
боковой панели (Esri Ocean / OSM + OpenSeaMap Seamarks, тематические слои, центры,
health-check, мини‑легенда).

Работает ИДЕМПОТЕНТНО: повторный запуск не дублирует вставки.
Создаёт резервную копию *.bak-autopatch-YYYYmmddHHMMSS перед сохранением.
Поддерживаемые файлы-загрузчики (любые из них, если существуют в каталоге запуска):
  - mainPlugin.py
  - poiskmore_plugin.py
  - poiskmore_plugin_main.py

Использование:
    python autopatch_poiskmore.py [путь_к_каталогу_плагина]
Если аргумент не указан — берётся текущий каталог.
"""
import sys, os, re, time, io, difflib
from pathlib import Path

DOCK_IMPORT = 'from .ui.pm_sidebar_dock import ensure_pm_sidebar_dock'
QGIS_IMPORT_NEEDLES = [
    'from qgis.core import Qgis, QgsApplication',
    'from qgis.core import QgsApplication, Qgis',
]
SETUP_SNIPPET = (
    '# === Боковая панель «Поиск‑Море»: базовые карты/overlay/тематика/центры ===\n'
    'try:\n'
    '    self._pm_sidebar = ensure_pm_sidebar_dock(self.iface, self.plugin_dir)\n'
    'except Exception as e:\n'
    '    QgsApplication.messageLog().logMessage(f"Sidebar init error: {e}", "Poisk-More", Qgis.Warning)\n'
)
UNLOAD_SNIPPET = (
    '# Снимаем боковую панель, если создана\n'
    'try:\n'
    '    if getattr(self, "_pm_sidebar", None):\n'
    '        self.iface.removeDockWidget(self._pm_sidebar)\n'
    '        self._pm_sidebar.setParent(None)\n'
    '        self._pm_sidebar = None\n'
    'except Exception:\n'
    '    pass\n'
)

TARGETS = ["mainPlugin.py", "poiskmore_plugin.py", "poiskmore_plugin_main.py"]

def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def save_backup(p: Path, text: str):
    stamp = time.strftime("%Y%m%d%H%M%S")
    bak = p.with_suffix(p.suffix + f".bak-autopatch-{stamp}")
    bak.write_text(text, encoding="utf-8")
    return bak

def ensure_imports(text: str) -> str:
    if DOCK_IMPORT in text:
        dock_ok = True
    else:
        # вставим после import MenuManager или рядом с другими импортами из .
        pattern = r'from\s+\.menu_structure\s+import\s+MenuManager.*?\n'
        m = re.search(pattern, text)
        if m:
            insert_at = m.end()
            text = text[:insert_at] + DOCK_IMPORT + '\n' + text[insert_at:]
        else:
            # fallback — после первого блока импортов
            m2 = re.search(r'(^|\n)import .*?\n', text)
            insert_at = m2.end() if m2 else 0
            text = text[:insert_at] + DOCK_IMPORT + '\n' + text[insert_at:]
    # QGIS imports
    if not any(needle in text for needle in QGIS_IMPORT_NEEDLES):
        # добавим рядом с другими импортами qgis.core
        m = re.search(r'from\s+qgis\.core\s+import\s+.*\n', text)
        if m:
            end = m.end()
            text = text[:end] + 'from qgis.core import Qgis, QgsApplication\n' + text[end:]
        else:
            text = 'from qgis.core import Qgis, QgsApplication\n' + text
    return text

def ensure_attr_in_init(text: str) -> str:
    # найдём def __init__(self, iface):
    init_re = re.compile(r'(def\s+__init__\s*\(\s*self\s*,\s*iface\s*\)\s*:\s*\n)', re.MULTILINE)
    m = init_re.search(text)
    if not m:
        return text
    body = text[m.end():]
    # определим базовый отступ по минимальному из первых непустых строк
    indents = []
    for line in body.splitlines():
        if not line.strip():
            continue
        msp = re.match(r'(\s+)', line)
        if msp:
            indents.append(len(msp.group(1)))
        if len(indents) >= 30:
            break
    base_indent = ' ' * (min(indents) if indents else 8)
    if '_pm_sidebar' not in body[:600]:
        text = text[:m.end()] + f"{base_indent}self._pm_sidebar = None\n" + body
    return text

def ensure_setup_in_initGui(text: str) -> str:
    # найдём def initGui(self):
    pat = re.compile(r'(def\s+initGui\s*\(\s*self\s*\)\s*:\s*\n)', re.MULTILINE)
    m = pat.search(text)
    if not m:
        return text
    block_start = m.end()
    # вырезаем старую вставку (если уже есть) для нормализации отступов
    body = text[block_start:]
    if 'ensure_pm_sidebar_dock' in body:
        body = re.sub(r'[ \t]*# === Боковая панель[\s\S]*?Qgis\.Warning\)\n', '', body, count=1)
    # Найдём хорошую точку для вставки: после фразы «Устанавливаем начальное состояние»,
    # иначе — перед первым return, иначе — в начале тела метода.
    insert_rel = 0
    m_hook = re.search(r'Устанавливаем начальное состояние.*\n', body)
    if m_hook:
        insert_rel = m_hook.end()
    else:
        m_ret = re.search(r'\n[ \t]+return\b', body)
        insert_rel = m_ret.start() if m_ret else 0
    # Базовый отступ = минимальный отступ среди первых 30 непустых строк тела
    indents = []
    for line in body.splitlines():
        if not line.strip():
            continue
        msp = re.match(r'(\s+)', line)
        if msp:
            indents.append(len(msp.group(1)))
        if len(indents) >= 30:
            break
    base_indent = ' ' * (min(indents) if indents else 8)
    snippet = ''.join(base_indent + line if line.strip() else line
                      for line in SETUP_SNIPPET.splitlines(True))
    body = body[:insert_rel] + snippet + body[insert_rel:]
    return text[:block_start] + body

def ensure_unload_snippet(text: str) -> str:
    pat = re.compile(r'(def\s+unload\s*\(\s*self\s*\)\s*:\s*\n)', re.MULTILINE)
    m = pat.search(text)
    if not m:
        return text
    body = text[m.end():]
    if 'removeDockWidget' in body[:1200]:
        return text
    # базовый отступ блока unload
    indents = []
    for line in body.splitlines():
        if not line.strip():
            continue
        msp = re.match(r'(\s+)', line)
        if msp:
            indents.append(len(msp.group(1)))
        if len(indents) >= 30:
            break
    base_indent = ' ' * (min(indents) if indents else 8)
    snippet = ''.join(base_indent + line if line.strip() else line
                      for line in UNLOAD_SNIPPET.splitlines(True))
    text = text[:m.end()] + snippet + body
    return text

def patch_file(p: Path) -> str:
    original = load_text(p)
    text = original
    text = ensure_imports(text)
    text = ensure_attr_in_init(text)
    text = ensure_setup_in_initGui(text)
    text = ensure_unload_snippet(text)
    if text != original:
        save_backup(p, original)
        p.write_text(text, encoding="utf-8")
    return text

def unified_diff(a_text: str, b_text: str, a_name: str, b_name: str) -> str:
    a_lines = a_text.splitlines(True)
    b_lines = b_text.splitlines(True)
    diff = difflib.unified_diff(
        a_lines, b_lines,
        fromfile=a_name, tofile=b_name,
        fromfiledate="", tofiledate="",
        n=3
    )
    return ''.join(diff)

def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    print(f"[autopatch] Каталог: {root}")
    targets = [root / t for t in TARGETS if (root / t).exists()]
    if not targets:
        print("[autopatch] Не найдено ни одного целевого файла.")
        sys.exit(1)
    for p in targets:
        print(f"[autopatch] Патчим {p.name} …")
        before = load_text(p)
        after  = patch_file(p)
        if before == after:
            print("  — изменений не требуется (уже применено или неподходящий шаблон).")
        else:
            print("  — OK, изменения внесены.")
            print("  --- unified diff (для контроля) ---")
            print(unified_diff(before, after, p.name, p.name))
    print("[autopatch] Готово.")
    
if __name__ == "__main__":
    main()
