"""Compatibilité Qt5 / Qt6. Tout import Qt << sensible >> passe par ici."""
from __future__ import annotations

from qgis.PyQt.QtCore import QT_VERSION_STR, QEventLoop

Qt_MAJOR = int(QT_VERSION_STR.split('.')[0])

try:
    from qgis.PyQt.QtGui import QAction
except ImportError:
    from qgis.PyQt.QtWidgets import QAction

# Qt6 : drapeaux dans un sous-enum ; Qt5 : directement sur la classe.
EXCLUDE_USER_INPUT = getattr(QEventLoop, "ProcessEventsFlag", QEventLoop).ExcludeUserInputEvents

__all__ = ["EXCLUDE_USER_INPUT", "QAction", "Qt_MAJOR"]
