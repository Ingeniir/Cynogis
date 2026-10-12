"""Boîte de confirmation humaine pour les outils de niveau 3."""
from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from qgis.PyQt.QtWidgets import QMessageBox, QWidget

from ..core.policy import Confirmer
from ..core.registry import ToolSpec

DETAIL_PROVIDERS: dict[str, Callable[[dict], list]] = {}
VISIBLE_DETAIL_LINES = 12


def make_confirmer(parent: QWidget) -> Confirmer:
    def confirm(spec: ToolSpec, params: dict[str, Any]) -> bool:
        details = build_details(spec.name, params)
        raw = json.dumps(params, ensure_ascii=False, indent=2, default=str)[:1500]
        box = QMessageBox(parent)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Cynogis : confirmation requise")
        box.setText(f"L'IA demande une action irréversible : <b>{spec.name}</b>")
        # Les premières lignes d'impact sont visibles sans ouvrir le détail.
        summary = "\n".join(details[:VISIBLE_DETAIL_LINES])
        box.setInformativeText(f"{summary}\n\nAutoriser cette action ?" if summary
                               else "Autoriser cette action ?")
        box.setDetailedText("\n".join([*details, "", "Paramètres :", raw]) if details else raw)
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.setDefaultButton(QMessageBox.StandardButton.No)
        box.exec()
        return box.clickedButton() == box.button(QMessageBox.StandardButton.Yes)

    return confirm


def register_detail_provider(tool_name: str, provider: Callable[[dict], list]) -> None:
    """Associe à un outil une fonction qui décrit l'impact de l'appel."""
    DETAIL_PROVIDERS[tool_name] = provider


def build_details(tool_name: str, params: dict) -> list[str]:
    """Lignes de détail à afficher, jamais bloquantes en cas d'erreur."""
    provider = DETAIL_PROVIDERS.get(tool_name)
    if provider is None:
        return []
    try:
        return [str(line) for line in provider(params or {})]
    except Exception:  # le détail ne doit jamais empêcher la confirmation
        return []
