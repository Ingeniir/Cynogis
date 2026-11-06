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
BLOCKING_CALLS = frozenset({"run", "runAndLoadResults", "execAlgorithmDialog",
                            "sleep", "QgsBlockingNetworkRequest", "urlopen", "get", "post"})
BLOCKING_OWNERS = frozenset({"processing", "time", "requests", "urllib"})

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

def blocking_calls(code: str) -> list[str]:
    """Appels qui bloquent le thread principal : à interdire dans execute_pyqgis."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            owner = node.func.value
            if isinstance(owner, ast.Name) and owner.id in BLOCKING_OWNERS \
                    and node.func.attr in BLOCKING_CALLS:
                found.add(f"{owner.id}.{node.func.attr}")
    return sorted(found)
