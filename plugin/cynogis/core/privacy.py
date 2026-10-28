"""Champs dont les valeurs ne doivent jamais être envoyée au modèle."""
from __future__ import annotations

import re
import unicodedata

# Noms et adresses (dont les champs MAJIC du cadastre), coordonnées, espèces sensibles
SENSITIVE_TOKENS = frozenset({
    "nom", "prenom", "proprietaire", "proprio", "adresse", "telephone", "tel", "mail",
    "email", "naissance", "ddenom", "dnomlp", "dprnlp", "dlign3", "dlign4", "dlign5",
    "dlign6", "sensible", "sensibilite",
})

def is_sensitive_field(name: str) -> bool:
    norm = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return any(token in SENSITIVE_TOKENS for token in re.split(r"[^a-z0-9]+", norm))