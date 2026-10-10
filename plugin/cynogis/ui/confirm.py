"""Boîte de confirmation humaine pour les outils de niveau 3."""
from __future__ import annotations

import json
from typing import Any

from qgis.PyQt.QtWidgets import QMessageBox, QWidget

from ..core.policy import Confirmer
from ..core.registry import ToolSpec


def make_confirmer(parent: QWidget) -> Confirmer:
    def confirm(spec: ToolSpec, params: dict[str, Any]) -> bool:
        details = json.dumps(params, ensure_ascii=False, indent=2)[:1500]
        box = QMessageBox(parent)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Cynogis : confirmation requise")
        box.setText(f"L'IA demande une action irréversible : <b>{spec.name}</b>")
        box.setInformativeText("Autoriser cette action ?")
        box.setDetailedText(details)
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.setDefaultButton(QMessageBox.StandardButton.No)
        box.exec()
        return box.clickedButton() == box.button(QMessageBox.StandardButton.Yes)

    return confirm
