def classFactory(iface):
if iface is None:
raise ValueError("iface не инициализирован")
from .poiskmore import PoiskMorePlugin
return PoiskMorePlugin(iface)