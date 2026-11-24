"""Garde-fou : ne pas charger PyQGIS compilé pour un autre Python que l'interpréteur courant.

Le venv de développement peut voir le dossier python de QGIS (cynogis_dev.pth). Importer
qgis.core y charge des DLL compilées pour le Python de QGIS : plantage natif
(0xc0000139 sous Windows) que pytest ne présente que comme un module ignoré.

Ici, rien n'est chargé : le paquet qgis est localisé sans exécuter son __init__, puis la
version de Python attendue est lue dans l'extension _core (dépendance python3XX.dll sous
Windows, étiquette cpython-3XX ailleurs). Aucune version n'est figée : la comparaison se
fait avec l'installation QGIS présente. Version illisible : pas de conclusion, on laisse
pytest.importorskip décider comme avant.
"""
from __future__ import annotations

import functools
import importlib.util
import re
import sys
from pathlib import Path

_DLL = re.compile(rb"python3(\d+)\.dll", re.IGNORECASE)
_TAG = re.compile(r"cpython-3(\d+)")


@functools.lru_cache(maxsize=1)
def foreign_pyqgis_reason() -> str | None:
    """Motif d'incompatibilité, ou None si compatible ou indéterminé."""
    try:
        spec = importlib.util.find_spec("qgis")  # n'exécute pas qgis/__init__.py
    except (ImportError, ValueError):
        return None
    if spec is None or not spec.submodule_search_locations:
        return None
    current = sys.version_info[1]
    for location in spec.submodule_search_locations:
        for core in sorted(Path(location).glob("_core*")):
            if core.suffix == ".pyd":
                try:
                    minors = {int(m) for m in _DLL.findall(core.read_bytes())}
                except OSError:
                    continue
            else:
                minors = {int(m) for m in _TAG.findall(core.name)}
            if minors and current not in minors:
                expected = ", ".join(f"3.{m}" for m in sorted(minors))
                return (f"PyQGIS de {core.parent} compilé pour Python {expected}, "
                        f"interpréteur {sys.version.split()[0]} : lancer "
                        "scripts/run_qgis_integration.py (Python de QGIS)")
    return None


def skip_if_foreign_pyqgis(pytest_module) -> None:
    """Ignore le module de test, avec le motif, avant toute importation de qgis.core."""
    reason = foreign_pyqgis_reason()
    if reason is not None:
        pytest_module.skip(reason, allow_module_level=True)
