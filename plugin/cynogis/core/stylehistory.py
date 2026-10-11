"""Historique des styles, pour pouvoir revenir en arrière.

Chaque style est conservé sous sa forme XML (QML) : le module ne connaît que
des chaînes de caractères, ce qui le rend entièrement testable.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

MAX_DEPTH = 10


@dataclass
class StyleSnapshot:
    """État d'un style à un instant donné."""

    layer_id: str
    layer_name: str
    xml: str
    description: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "layer_id": self.layer_id,
            "layer_name": self.layer_name,
            "description": self.description,
            "timestamp": self.timestamp,
            "size": len(self.xml),
        }


class StyleHistory:
    """Pile d'états par couche, de profondeur limitée."""

    def __init__(self, max_depth: int = MAX_DEPTH) -> None:
        self._stacks: dict[str, list[StyleSnapshot]] = {}
        self._order: list[str] = []
        self.max_depth = int(max_depth)

    def push(self, layer_id: str, layer_name: str, xml: str, description: str = "") -> int:
        """Empile l'état actuel avant de le remplacer."""
        if not xml:
            return self.depth(layer_id)
        stack = self._stacks.setdefault(layer_id, [])
        stack.append(StyleSnapshot(layer_id, layer_name, xml, description))
        if len(stack) > self.max_depth:
            del stack[0]
        if layer_id in self._order:
            self._order.remove(layer_id)
        self._order.append(layer_id)
        return len(stack)

    def pop(self, layer_id: str) -> StyleSnapshot | None:
        """Dépile le dernier état enregistré d'une couche."""
        stack = self._stacks.get(layer_id)
        if not stack:
            return None
        snapshot = stack.pop()
        if not stack:
            self._stacks.pop(layer_id, None)
            if layer_id in self._order:
                self._order.remove(layer_id)
        return snapshot

    def last_layer(self) -> str | None:
        """Identifiant de la dernière couche stylisée, pour un retour sans argument."""
        return self._order[-1] if self._order else None

    def depth(self, layer_id: str) -> int:
        return len(self._stacks.get(layer_id, []))

    def clear(self, layer_id: str | None = None) -> int:
        if layer_id is None:
            removed = sum(len(stack) for stack in self._stacks.values())
            self._stacks.clear()
            self._order.clear()
            return removed
        removed = len(self._stacks.pop(layer_id, []))
        if layer_id in self._order:
            self._order.remove(layer_id)
        return removed

    def summary(self) -> dict:
        return {
            "layers": [
                {
                    "layer_id": layer_id,
                    "layer_name": stack[-1].layer_name,
                    "steps": len(stack),
                    "last_change": stack[-1].description,
                }
                for layer_id, stack in self._stacks.items()
            ],
            "total_steps": sum(len(stack) for stack in self._stacks.values()),
        }


HISTORY = StyleHistory()
