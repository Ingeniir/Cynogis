"""Repérage des appels sensibles dans le code soumis à execute_pyqgis. Python pur.

Indicatif : sert à alerter l'opérateur dans la fenêtre de confirmation, ce n'est pas un
bac à sable (un code obfusqué passe au travers).
"""
from __future__ import annotations

import ast

RISKY_MODULES = frozenset({"os", "sys", "subprocess", "shutil", "socket", "ctypes", "urllib",
                           "requests", "pathlib", "importlib"})
RISKY_CALLS = frozenset({"__import__", "eval", "exec", "getattr", "open", "unlink", "rmtree",
                         "rmdir", "system", "popen", "write_text", "write_bytes",
                         "removeMapLayer", "removeMapLayers", "deleteFeature", "deleteFeatures",
                         "deleteAttribute", "deleteAttributes", "commitChanges", "truncate"})


def risky_names(code: str) -> list[str]:
    """Modules importés et appels sensibles du code, triés ; [] si le code ne compile pas."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [node.module or ""]
        else:
            modules = []
        found.update(m.split(".")[0] for m in modules if m.split(".")[0] in RISKY_MODULES)
        if isinstance(node, ast.Call):
            func = node.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
            if name in RISKY_CALLS:
                found.add(name)
    return sorted(found)
