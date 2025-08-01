from PyQt5.QtGui import QIcon
import os


def load_icon(name: str) -> QIcon:
    """Load an icon from the utils icon directory."""
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    if not os.path.exists(icons_dir):
        print(f"Папка иконок не найдена: {icons_dir}")
        return QIcon()
    path = os.path.join(icons_dir, name)
    return QIcon(path) if os.path.exists(path) else QIcon()
