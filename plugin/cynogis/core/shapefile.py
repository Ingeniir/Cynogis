"""Contraintes propres au format Shapefile.

Le bureau d'études échange beaucoup de .shp : mieux vaut annoncer les limites
du format avant l'export que découvrir des champs tronqués chez le client.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .fields import FIELD_TYPES, truncate_field_names

REQUIRED_SIDECARS = (".shp", ".shx", ".dbf")
RECOMMENDED_SIDECARS = (".prj", ".cpg")
OTHER_SIDECARS = (".sbn", ".sbx", ".qix", ".qmd", ".qpj", ".shp.xml", ".atx", ".fix")

MAX_SIZE_BYTES = 2 * 1024 ** 3        # limite dure du format (.shp et .dbf)
WARN_SIZE_BYTES = 1500 * 1024 ** 2    # on alerte avant d'y arriver
MAX_FIELD_NAME = 10
MAX_TEXT_LENGTH = 254
COMMON_ENCODINGS = ("UTF-8", "ISO-8859-1", "windows-1252", "ISO-8859-15")

# Caractères typiques d'un fichier lu avec le mauvais encodage.
MOJIBAKE = ("Ã©", "Ã¨", "Ã ", "Ã§", "Ã´",  # noqa: RUF001 - é è à ç ô
            "Ã®", "Ãª", "ï¿½", "�")  # î ê, U+FFFD


@dataclass(frozen=True)
class SidecarReport:
    """État des fichiers qui accompagnent un .shp."""

    present: tuple[str, ...]
    missing_required: tuple[str, ...]
    missing_recommended: tuple[str, ...]

    @property
    def is_complete(self) -> bool:
        return not self.missing_required

    def to_dict(self) -> dict:
        return {
            "present": list(self.present),
            "missing_required": list(self.missing_required),
            "missing_recommended": list(self.missing_recommended),
            "is_complete": self.is_complete,
        }


def sidecar_report(extensions) -> SidecarReport:
    """Compare les extensions trouvées à côté du .shp avec celles attendues."""
    found = {str(ext).lower() for ext in extensions}
    present = tuple(sorted(found))
    missing_required = tuple(ext for ext in REQUIRED_SIDECARS if ext not in found)
    missing_recommended = tuple(ext for ext in RECOMMENDED_SIDECARS if ext not in found)
    return SidecarReport(present, missing_required, missing_recommended)


def sidecar_messages(report: SidecarReport) -> list[str]:
    """Phrases d'explication destinées à l'utilisateur et à l'IA."""
    messages: list[str] = []
    if report.missing_required:
        messages.append(
            "Fichiers obligatoires manquants : "
            f"{', '.join(report.missing_required)}. Le shapefile est inutilisable "
            "sans eux ; redemandez la livraison complète."
        )
    if ".prj" in report.missing_recommended:
        messages.append(
            "Pas de fichier .prj : le système de coordonnées est inconnu. "
            "Il devra être déclaré à la main (EPSG:2975 à La Réunion, "
            "EPSG:4471 à Mayotte)."
        )
    if ".cpg" in report.missing_recommended:
        messages.append(
            "Pas de fichier .cpg : l'encodage des textes est supposé. "
            "Vérifiez les accents dans la table attributaire."
        )
    return messages


def looks_like_mojibake(values) -> bool:
    """Détecte un encodage probablement mal interprété dans des textes."""
    return any(
        isinstance(value, str) and any(marker in value for marker in MOJIBAKE)
        for value in values
    )


def size_messages(path_sizes: dict) -> list[str]:
    """Alerte sur la limite des 2 Go du format."""
    messages: list[str] = []
    for extension, size in path_sizes.items():
        if size >= MAX_SIZE_BYTES:
            messages.append(
                f"Le fichier {extension} dépasse 2 Go : limite absolue du format "
                "Shapefile, les données sont probablement tronquées. Passez au GeoPackage."
            )
        elif size >= WARN_SIZE_BYTES:
            mo = size // (1024 * 1024)
            messages.append(
                f"Le fichier {extension} pèse {mo} Mo, proche de la limite de 2 Go "
                "du format Shapefile. Le GeoPackage est recommandé."
            )
    return messages


def export_plan(field_names, field_types) -> dict:
    """Prépare un export Shapefile : renommages et pertes annoncés à l'avance.

    `field_types` associe chaque nom de champ à un type Cynogis ; les types
    non représentables en .dbf (booléen, date-heure) sont signalés.
    """
    mapping = truncate_field_names(list(field_names), MAX_FIELD_NAME)
    renamed = {
        original: short for original, short in mapping.items() if original != short
    }
    warnings: list[str] = []
    if renamed:
        details = ", ".join(f"{old} → {new}" for old, new in list(renamed.items())[:10])
        suite = "…" if len(renamed) > 10 else ""
        warnings.append(
            f"{len(renamed)} nom(s) de champ raccourci(s) à 10 caractères : {details}{suite}"
        )
    for name, type_name in (field_types or {}).items():
        spec = FIELD_TYPES.get(type_name)
        if spec and not spec.shapefile_ok:
            warnings.append(
                f"Le champ « {name} » ({spec.label}) n'existe pas en Shapefile : "
                "il sera converti en texte ou en entier."
            )
    warnings.append(
        "Rappel Shapefile : textes limités à 254 caractères, pas de valeurs "
        "nulles distinctes de zéro, un seul type de géométrie par fichier."
    )
    return {"field_mapping": mapping, "renamed": renamed, "warnings": warnings}


def companion_paths(shp_path: str) -> list[str]:
    """Tous les chemins possibles accompagnant un .shp (existants ou non)."""
    stem, _ = os.path.splitext(shp_path)
    extensions = REQUIRED_SIDECARS + RECOMMENDED_SIDECARS + OTHER_SIDECARS
    return [stem + extension for extension in extensions]
