"""Audit d'un projet QGIS : règles de contrôle et contenu du rapport.

Les faits (couches, SCR, géométries…) sont relevés par tools/project_audit.py et
arrivent ici sous forme de dictionnaires : les règles se testent sans QGIS.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence

from .classify import format_number
from .report import MAX_ROWS

SEVERITIES = ("critique", "majeur", "mineur", "info")
_RANK = {name: index for index, name in enumerate(SEVERITIES)}
INDEX_THRESHOLD = 10_000  # entités au-delà desquelles un index spatial devient utile


def _finding(severity: str, layer: str, message: str, recommendation: str = "") -> dict:
    return {"severity": severity, "layer": layer, "message": message,
            "recommendation": recommendation}


def project_findings(project: Mapping) -> list[dict]:
    """Anomalies propres au projet (enregistrement, SCR, chemins)."""
    found: list[dict] = []
    scope = "(projet)"
    if not project.get("file"):
        found.append(_finding("majeur", scope, "Projet jamais enregistré.",
                              "Enregistrer le projet (.qgz) dans le dossier de l'étude."))
    elif project.get("dirty"):
        found.append(_finding("mineur", scope, "Modifications du projet non enregistrées.",
                              "Enregistrer le projet."))
    if not project.get("crs"):
        found.append(_finding("critique", scope, "SCR du projet non défini.",
                              "Définir le SCR du projet (EPSG:2975 ou EPSG:4471)."))
    elif project.get("geographic"):
        found.append(_finding("majeur", scope, f"SCR du projet géographique ({project['crs']}) : "
                              "mesures à l'écran en degrés.",
                              "Passer le projet en SCR projeté du territoire."))
    reference = project.get("reference_crs")
    if reference and project.get("crs") and project["crs"] != reference:
        found.append(_finding("mineur", scope, f"SCR du projet {project['crs']} différent du "
                              f"SCR de référence {reference}.",
                              f"Passer le projet en {reference}."))
    if project.get("territories", 0) > 1:
        found.append(_finding("mineur", scope, "Couches réparties sur plusieurs territoires.",
                              "Vérifier que le projet ne mélange pas Réunion et Mayotte."))
    if project.get("absolute_paths"):
        found.append(_finding("mineur", scope, "Chemins des sources enregistrés en absolu : "
                              "projet non déplaçable.",
                              "Propriétés du projet > Général : chemins relatifs."))
    if not project.get("layer_count"):
        found.append(_finding("info", scope, "Projet sans couche."))
    return found


def layer_findings(layer: Mapping, project_crs: str | None = None) -> list[dict]:
    """Anomalies d'une couche à partir de ses faits relevés."""
    name = str(layer.get("name") or layer.get("id") or "?")
    found: list[dict] = []

    def add(severity: str, message: str, recommendation: str = "") -> None:
        found.append(_finding(severity, name, message, recommendation))

    if not layer.get("valid", True):
        add("critique", "Couche invalide : source introuvable ou illisible.",
            "Clic droit > Réparer la source de données, ou retirer la couche.")
        return found
    crs, reference = layer.get("crs"), layer.get("reference_crs")
    if layer.get("kind") in ("vector", "raster") and layer.get("geometry") != "none":
        if not crs:
            add("critique", "SCR non défini.", "Déclarer le SCR de la couche.")
        elif layer.get("geographic"):
            add("majeur", f"SCR géographique ({crs}) : surfaces et distances fausses.",
                f"Reprojeter en {reference or 'SCR projeté du territoire'}.")
        elif reference and crs != reference:
            add("mineur", f"SCR {crs} différent du SCR de référence {reference}.",
                f"Reprojeter en {reference}.")
        elif project_crs and crs != project_crs:
            add("info", f"SCR {crs} différent de celui du projet ({project_crs}) : "
                "reprojection à la volée.")
    if layer.get("memory"):
        add("majeur", "Couche temporaire (mémoire) : perdue à la fermeture de QGIS.",
            "L'enregistrer en GeoPackage.")
    if layer.get("modified"):
        add("majeur", "Modifications en cours non enregistrées.",
            "Enregistrer ou annuler l'édition de la couche.")
    if layer.get("source_missing"):
        add("critique", f"Fichier source absent : {layer.get('source')}.",
            "Réparer la source de données.")

    if layer.get("kind") == "vector":
        count = layer.get("feature_count")
        if count == 0:
            add("mineur", "Couche vide.", "Vérifier la source ou retirer la couche.")
        check = layer.get("geometry_check")
        if check:
            if check.get("invalid"):
                kinds = ", ".join(f"{k} ({v})" for k, v in (check.get("error_types") or {}).items())
                add("majeur", f"{check['invalid']} géométrie(s) invalide(s)"
                    + (f" : {kinds}." if kinds else "."),
                    "Corriger (fix_geometries) avant toute superposition ou mesure.")
            if check.get("null_or_empty"):
                add("mineur", f"{check['null_or_empty']} géométrie(s) nulle(s) ou vide(s).",
                    "Supprimer ou redessiner ces entités.")
        elif layer.get("geometry_skipped"):
            add("info", f"Géométries non contrôlées ({format_number(count or 0, 0)} entités, "
                "au-delà du seuil).", "Lancer check_geometries sur cette couche.")
        if (layer.get("spatial_index") is False and (count or 0) > INDEX_THRESHOLD):
            add("mineur", "Pas d'index spatial : affichage et requêtes lents.",
                "Créer un index spatial (Propriétés > Source).")
        if layer.get("shapefile"):
            for message in layer.get("sidecar_messages") or []:
                add("mineur", message)
            if layer.get("mojibake"):
                add("mineur", "Accents mal lus : encodage déclaré probablement faux.",
                    "Corriger l'encodage (set_layer_encoding).")
            add("info", "Format Shapefile : noms de champs limités à 10 caractères, 2 Go max.",
                "Préférer le GeoPackage pour les livrables.")
    elif layer.get("kind") == "raster" and layer.get("nodata") is False:
        add("mineur", "Aucune valeur NoData déclarée (bande 1) : bords comptés dans les "
            "statistiques.", "Déclarer la valeur NoData du raster.")
    return found


def duplicate_name_findings(layers: Sequence[Mapping]) -> list[dict]:
    names = Counter(str(layer.get("name")) for layer in layers)
    return [_finding("mineur", name, f"Nom porté par {count} couches : ambigu pour l'IA et "
                     "les livrables.", "Renommer les couches.")
            for name, count in names.items() if count > 1]


def audit(project: Mapping, layers: Sequence[Mapping]) -> list[dict]:
    """Toutes les anomalies, des plus graves aux moins graves."""
    findings = project_findings(project) + duplicate_name_findings(layers)
    for layer in layers:
        findings += layer_findings(layer, project.get("crs"))
    return sorted(findings, key=lambda f: _RANK[f["severity"]])


def severity_counts(findings: Sequence[Mapping]) -> dict[str, int]:
    counts = Counter(f["severity"] for f in findings)
    return {name: counts.get(name, 0) for name in SEVERITIES}


def verdict(counts: Mapping[str, int]) -> str:
    if counts.get("critique"):
        return "Projet non livrable en l'état : anomalies critiques à corriger."
    if counts.get("majeur"):
        return ("Projet utilisable, mais des anomalies majeures faussent ou fragilisent "
                "les résultats.")
    if counts.get("mineur"):
        return "Projet sain ; quelques points mineurs à reprendre."
    return "Aucune anomalie détectée."


def _yes_no(value) -> str | None:
    return None if value is None else ("oui" if value else "non")


def build_sections(project: Mapping, layers: Sequence[Mapping], findings: Sequence[Mapping],
                   map_image: str | None = None) -> list[dict]:
    """Sections au format de core/report.py (build_html / build_markdown). map_image : PNG de
    la carte d'ensemble, relatif au rapport."""
    counts = severity_counts(findings)
    sections: list[dict] = [{
        "heading": "Synthèse",
        "text": verdict(counts),
        "table": {"headers": ["Gravité", "Nombre"],
                  "rows": [[name.capitalize(), counts[name]] for name in SEVERITIES]},
    }, {
        "heading": "Projet",
        "table": {"headers": ["Élément", "Valeur"], "rows": [
            ["Fichier", project.get("file")],
            ["SCR", project.get("crs")],
            ["Territoire", project.get("territory")],
            ["Couches", project.get("layer_count")],
            ["Chemins relatifs", _yes_no(None if project.get("absolute_paths") is None
                                         else not project["absolute_paths"])],
        ]},
    }]
    if map_image:
        sections.append({"heading": "Carte d'ensemble", "image": map_image,
                         "caption": "Couches cochées du projet, cadrées sur les données."})
    priorities = list(dict.fromkeys(
        f"{f['layer']} : {f['recommendation']}" for f in findings
        if f["severity"] in ("critique", "majeur") and f["recommendation"]))
    if priorities:
        sections.append({"heading": "Actions prioritaires", "bullets": priorities})
    sections.append({
        "heading": "Inventaire des couches",
        "table": {"headers": ["Couche", "Type", "Format", "SCR", "Entités / taille",
                              "Valide"],
                  "rows": [[layer.get("name"), layer.get("geometry") or layer.get("kind"),
                            layer.get("format"), layer.get("crs"),
                            layer.get("feature_count") if layer.get("kind") == "vector"
                            else layer.get("size"), _yes_no(layer.get("valid", True))]
                           for layer in layers]},
    })
    checked = [layer for layer in layers if layer.get("geometry_check")]
    if checked:
        sections.append({
            "heading": "Contrôle des géométries",
            "table": {"headers": ["Couche", "Contrôlées", "Invalides", "Nulles ou vides",
                                  "Multi-parties"],
                      "rows": [[layer["name"], *(layer["geometry_check"].get(key, 0) for key in
                                                 ("checked", "invalid", "null_or_empty",
                                                  "multipart"))]
                               for layer in checked]},
        })
    rasters = [layer for layer in layers
               if layer.get("kind") == "raster" and layer.get("valid", True)]
    if rasters:
        sections.append({
            "heading": "Rasters",
            "table": {"headers": ["Couche", "Taille (px)", "Bandes", "Pixel", "NoData"],
                      "rows": [[layer["name"], layer.get("size"), layer.get("bands"),
                                layer.get("pixel_size"), _yes_no(layer.get("nodata"))]
                               for layer in rasters]},
        })
    sections.append({
        "heading": "Anomalies détaillées",
        "text": "" if findings else "Aucune anomalie.",
        "table": {"headers": ["Gravité", "Couche", "Constat", "Recommandation"],
                  "rows": [[f["severity"], f["layer"], f["message"], f["recommendation"] or None]
                           for f in findings[:MAX_ROWS]]} if findings else None,
    })
    return sections
