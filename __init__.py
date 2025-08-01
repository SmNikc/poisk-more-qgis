# -*- coding: utf-8 -*-
"""Инициализация QGIS-плагина 'Поиск-Море'."""


def classFactory(iface):
    """Создаёт экземпляр плагина."""
    if iface is None:
        return None
    from .poiskmore import PoiskMorePlugin
    return PoiskMorePlugin(iface)
