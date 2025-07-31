from .dialog_sitrep import SitrepForm

class SitrepDialog(SitrepForm):
    def __init__(self, iface=None):
        super().__init__(parent=iface)

