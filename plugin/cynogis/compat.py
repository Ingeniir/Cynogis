"""Compatibilité Qt5 / Qt6. Tout import Qt << sensible >> passe par ici."""
from __future__ import annotations

from qgis.PyQt.QtCore import QT_VERSION_STR

Qt_MAJOR = int(QT_VERSION_STR.split('.')[0])

try:
    from qgis.PyQt.QtGui import QAction
except ImportError:
    from qgis.PyQt.QtWidgets import QAction

__all__ = ["QAction", "Qt_MAJOR"]
