# -*- coding: utf-8 -*-
"""Инициализация QGIS-плагина 'Поиск-Море'"""

def classFactory(iface):
    """Вызывается QGIS при загрузке плагина"""
    if iface is None:
        return None
    from .poiskmore import PoiskMorePlugin
    return PoiskMorePlugin(iface)
