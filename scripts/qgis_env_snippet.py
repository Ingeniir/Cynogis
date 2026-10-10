import importlib
import json
import os
import sys

import qgis
from qgis.core import Qgis, QgsApplication
from qgis.PyQt.QtCore import QT_VERSION_STR
from qgis.PyQt.QtWidgets import QApplication

pyqt = importlib.import_module("PyQt" + QT_VERSION_STR.split(".")[0])
info = {
    "qgis_version": Qgis.QGIS_VERSION,
    "qt_version": QT_VERSION_STR,
    "python_version": sys.version.split()[0],
    "python_prefix": sys.prefix,
    "qgis_python_dir": os.path.dirname(os.path.dirname(qgis.__file__)),
    "pyqt_dir": os.path.dirname(os.path.dirname(pyqt.__file__)),
    "plugins_dir": os.path.join(QgsApplication.qualifiedSettingsDirPath(), "python", "plugins"),
}
text = json.dumps(info, indent=2, ensure_ascii=False)
QApplication.clipboard().setText(text)
print(text)
print("\n→ Copié dans le presse-papiers : colle-le dans .qgis_env.json à la racine du dépôt.")
