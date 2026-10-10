"""Redirige le logger 'cynogis' vers le panneau Journal de QGIS (onglet Cynogis)."""
from __future__ import annotations

import logging

from qgis.core import Qgis, QgsMessageLog

TAG = "Cynogis"
_LEVELS = (
    (logging.ERROR, Qgis.MessageLevel.Critical),
    (logging.WARNING, Qgis.MessageLevel.Warning),
    (logging.NOTSET, Qgis.MessageLevel.Info),
)

class QgsLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            level = next(q for lvl, q in _LEVELS if lvl <= record.levelno)
            QgsMessageLog.logMessage(self.format(record), TAG, level)
        except Exception:
            self.handleError(record)

def setup_logging(level: int = logging.INFO) -> logging.Handler:
    logger = logging.getLogger("cynogis")
    handler = QgsLogHandler()
    handler.setFormatter(logging.Formatter("%(name)s : %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return handler

def teardown_logging(handler: logging.Handler) -> None:
    logging.getLogger("cynogis").removeHandler(handler)
