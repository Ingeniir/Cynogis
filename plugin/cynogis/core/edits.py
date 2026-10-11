"""Journal des modifications en attente dans les tampons d'édition.

Ce journal est la mémoire de ce que l'IA a demandé depuis la dernière
sauvegarde. Il sert à trois choses : renseigner l'IA (get_pending_edits),
construire le texte de la fenêtre de confirmation, et tracer le tout dans
l'audit. Module pur : il ne manipule aucune couche.
"""

from __future__ import annotations

import time
from collections.abc import Iterable
from dataclasses import dataclass, field

# Garde-fous : au-delà, l'outil refuse et demande de filtrer.
MAX_FEATURES_PER_CALL = 2000
MAX_PENDING_PER_LAYER = 50_000

OPERATION_LABELS = {
    "add_features": "entités ajoutées",
    "update_attributes": "entités modifiées",
    "calculate_field": "valeurs calculées",
    "add_field": "champs ajoutés",
    "delete_field": "champs supprimés",
    "delete_features": "entités supprimées",
    "update_geometry": "géométries remplacées",
    "move_features": "entités déplacées",
    "split_feature": "entités découpées",
    "merge_features": "fusions d'entités",
    "snap_features": "géométries accrochées",
}


@dataclass
class EditEntry:
    """Une opération d'édition enregistrée dans le tampon."""

    layer_id: str
    layer_name: str
    operation: str
    count: int
    detail: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "layer_id": self.layer_id,
            "layer_name": self.layer_name,
            "operation": self.operation,
            "count": self.count,
            "detail": self.detail,
            "timestamp": self.timestamp,
        }

    def describe(self) -> str:
        label = OPERATION_LABELS.get(self.operation, self.operation)
        text = f"{self.count} {label}"
        return f"{text} ({self.detail})" if self.detail else text


class EditJournal:
    """Pile des opérations en attente, regroupées par couche."""

    def __init__(self) -> None:
        self._entries: list[EditEntry] = []

    def record(
        self, layer_id: str, layer_name: str, operation: str, count: int, detail: str = ""
    ) -> EditEntry:
        entry = EditEntry(layer_id, layer_name, operation, int(count), detail)
        self._entries.append(entry)
        return entry

    def entries(self, layer_id: str | None = None) -> list[EditEntry]:
        if layer_id is None:
            return list(self._entries)
        return [entry for entry in self._entries if entry.layer_id == layer_id]

    def layer_ids(self) -> list[str]:
        seen: list[str] = []
        for entry in self._entries:
            if entry.layer_id not in seen:
                seen.append(entry.layer_id)
        return seen

    def clear(self, layer_id: str | None = None) -> int:
        """Vide le journal (après une sauvegarde ou une annulation)."""
        before = len(self._entries)
        if layer_id is None:
            self._entries.clear()
        else:
            self._entries = [e for e in self._entries if e.layer_id != layer_id]
        return before - len(self._entries)

    def count_for(self, layer_id: str, operations: Iterable[str] | None = None) -> int:
        wanted = set(operations) if operations else None
        return sum(
            entry.count
            for entry in self._entries
            if entry.layer_id == layer_id and (wanted is None or entry.operation in wanted)
        )

    def summary(self, layer_id: str | None = None) -> dict:
        """Bilan lisible : une entrée par couche, avec le total par opération."""
        layers: dict[str, dict] = {}
        for entry in self.entries(layer_id):
            bucket = layers.setdefault(
                entry.layer_id,
                {
                    "layer_id": entry.layer_id,
                    "layer_name": entry.layer_name,
                    "operations": {},
                    "total": 0,
                    "details": [],
                },
            )
            bucket["layer_name"] = entry.layer_name
            bucket["operations"][entry.operation] = (
                bucket["operations"].get(entry.operation, 0) + entry.count
            )
            bucket["total"] += entry.count
            bucket["details"].append(entry.describe())
        return {
            "layers": list(layers.values()),
            "layer_count": len(layers),
            "total_operations": sum(bucket["total"] for bucket in layers.values()),
        }


def describe_summary(summary: dict) -> list[str]:
    """Transforme un bilan en lignes de texte pour la fenêtre de confirmation."""
    lines: list[str] = []
    for bucket in summary.get("layers", []):
        lines.append(f"• {bucket['layer_name']} :")
        for operation, count in bucket["operations"].items():
            label = OPERATION_LABELS.get(operation, operation)
            lines.append(f"    - {count} {label}")
    if not lines:
        lines.append("Aucune modification en attente.")
    return lines


def check_batch_size(count: int, limit: int = MAX_FEATURES_PER_CALL) -> None:
    """Refuse les lots trop volumineux pour un appel unique."""
    if count > limit:
        raise ValueError(
            f"{count} entités demandées en un seul appel, maximum {limit}. "
            "Filtrez la sélection ou procédez par lots."
        )


JOURNAL = EditJournal()
