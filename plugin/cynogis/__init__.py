"""Cynogis : point d'entrée QGIS. Aucun import qgis ici (test unitaires sans QGIS)."""
__version__ = "0.1.0"

def classFactory(iface):
    from .plugin import CynogisPlugin

    return CynogisPlugin(iface)
