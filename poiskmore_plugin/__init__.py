# -*- coding: utf-8 -*-
"""
QGIS Plugin - Поиск-Море
"""

def classFactory(iface):
    """
    Load PoiskMorePlugin class from file poiskmore_plugin.
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .poiskmore_plugin import PoiskMorePlugin
    return PoiskMorePlugin(iface)
