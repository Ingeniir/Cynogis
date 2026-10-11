"""Liste blanche des algorithmes Processing exposés à l'IA.

Un algorithme absent de cette table ne peut pas être exécuté, même si QGIS le
fournit. C'est la contrepartie de la décision « pas de code arbitraire » :
l'IA choisit dans un catalogue fermé, relu par un humain.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

from .naming import normalize


@dataclass(frozen=True)
class AlgorithmSpec:
    """Description d'un algorithme autorisé."""

    algorithm_id: str
    label: str
    category: str
    summary: str
    keywords: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "algorithm_id": self.algorithm_id,
            "label": self.label,
            "category": self.category,
            "summary": self.summary,
        }

CATEGORIES = (
    "geometrie",
    "projection",
    "tampon",
    "superposition",
    "selection",
    "agregation",
    "analyse",
    "conversion",
    "raster",
    "terrain",
)

ALGORITHMS: tuple[AlgorithmSpec, ...] = (
    # --- Géométrie ---------------------------------------------------------
    AlgorithmSpec("native:fixgeometries", "Corriger les géométries", "geometrie",
                  "Répare les géométries invalides (auto-intersections, anneaux mal orientés).",
                  ("valide", "reparer", "invalide")),
    AlgorithmSpec("native:multiparttosingleparts", "Multi-parties vers simples", "geometrie",
                  "Éclate chaque entité multi-partie en entités distinctes."),
    AlgorithmSpec("native:promotetomulti", "Promouvoir en multi-parties", "geometrie",
                  "Convertit les géométries simples en géométries multi-parties."),
    AlgorithmSpec("native:simplifygeometries", "Simplifier", "geometrie",
                  "Réduit le nombre de sommets selon une tolérance (Douglas-Peucker)."),
    AlgorithmSpec("native:smoothgeometry", "Lisser", "geometrie",
                  "Arrondit les angles des polygones et des lignes."),
    AlgorithmSpec("native:deleteholes", "Supprimer les trous", "geometrie",
                  "Supprime les anneaux intérieurs des polygones, sous un seuil de surface."),
    AlgorithmSpec("native:centroids", "Centroïdes", "geometrie",
                  "Crée un point au centre de gravité de chaque entité."),
    AlgorithmSpec("native:pointonsurface", "Point sur la surface", "geometrie",
                  "Crée un point garanti à l'intérieur de chaque polygone."),
    AlgorithmSpec("native:convexhull", "Enveloppe convexe", "geometrie",
                  "Calcule l'enveloppe convexe de chaque entité."),
    AlgorithmSpec("native:minimumboundinggeometry", "Géométrie englobante", "geometrie",
                  "Rectangle, cercle ou enveloppe englobant un groupe d'entités."),
    AlgorithmSpec("native:snapgeometries", "Accrocher les géométries", "geometrie",
                  "Accroche les sommets d'une couche sur une couche de référence."),
    AlgorithmSpec("native:boundary", "Limites", "geometrie",
                  "Extrait le contour des polygones ou les extrémités des lignes."),
    AlgorithmSpec("native:deleteduplicategeometries", "Supprimer les doublons", "geometrie",
                  "Supprime les entités dont la géométrie est identique à une autre.",
                  ("doublon", "duplique")),
    # --- Projection --------------------------------------------------------
    AlgorithmSpec("native:reprojectlayer", "Reprojeter", "projection",
                  "Transforme une couche vecteur vers un autre système de coordonnées.",
                  ("srs", "crs", "epsg", "utm")),
    AlgorithmSpec("native:assignprojection", "Affecter une projection", "projection",
                  "Déclare un système de coordonnées sans transformer les coordonnées."),
    # --- Tampons -----------------------------------------------------------
    AlgorithmSpec("native:buffer", "Tampon", "tampon",
                  "Crée une zone tampon à distance fixe autour des entités.",
                  ("zone", "buffer", "distance")),
    AlgorithmSpec("native:bufferbym", "Tampon variable", "tampon",
                  "Tampon dont la distance est portée par un champ ou une expression."),
    AlgorithmSpec("native:singlesidedbuffer", "Tampon unilatéral", "tampon",
                  "Tampon d'un seul côté d'une ligne."),
    AlgorithmSpec("native:offsetline", "Décaler les lignes", "tampon",
                  "Décale des lignes d'une distance donnée."),
    # --- Superposition -----------------------------------------------------
    AlgorithmSpec("native:clip", "Découper", "superposition",
                  "Découpe une couche par l'emprise d'une couche de masque.",
                  ("couper", "clip", "masque")),
    AlgorithmSpec("native:intersection", "Intersection", "superposition",
                  "Conserve les parties communes à deux couches, attributs fusionnés."),
    AlgorithmSpec("native:union", "Union", "superposition",
                  "Combine deux couches en conservant toutes les parties."),
    AlgorithmSpec("native:difference", "Différence", "superposition",
                  "Retire de la couche d'entrée les parties couvertes par la superposition."),
    AlgorithmSpec("native:symmetricaldifference", "Différence symétrique", "superposition",
                  "Conserve les parties qui n'appartiennent qu'à une seule des deux couches."),
    AlgorithmSpec("native:splitwithlines", "Découper par des lignes", "superposition",
                  "Découpe des polygones ou des lignes à l'aide d'une couche de lignes."),
    AlgorithmSpec("native:lineintersections", "Intersections de lignes", "superposition",
                  "Crée des points aux croisements de deux couches de lignes."),
    # --- Sélection / extraction -------------------------------------------
    AlgorithmSpec("native:extractbyexpression", "Extraire par expression", "selection",
                  "Crée une couche avec les entités qui vérifient une expression QGIS."),
    AlgorithmSpec("native:extractbyattribute", "Extraire par attribut", "selection",
                  "Crée une couche filtrée sur la valeur d'un champ."),
    AlgorithmSpec("native:extractbylocation", "Extraire par localisation", "selection",
                  "Extrait les entités selon leur relation spatiale avec une autre couche."),
    AlgorithmSpec("native:saveselectedfeatures", "Enregistrer la sélection", "selection",
                  "Crée une couche à partir des entités actuellement sélectionnées."),
    # --- Agrégation --------------------------------------------------------
    AlgorithmSpec("native:dissolve", "Fusionner (dissolve)", "agregation",
                  "Fusionne les entités adjacentes, éventuellement par valeurs de champs.",
                  ("regrouper", "agreger", "fusion")),
    AlgorithmSpec("native:aggregate", "Agréger", "agregation",
                  "Regroupe les entités et calcule des agrégats sur les attributs."),
    AlgorithmSpec("native:mergevectorlayers", "Fusionner des couches", "agregation",
                  "Assemble plusieurs couches de même type en une seule."),
    AlgorithmSpec("native:collect", "Rassembler les géométries", "agregation",
                  "Rassemble les géométries par valeurs de champs en multi-parties."),
    # --- Analyse -----------------------------------------------------------
    AlgorithmSpec("qgis:statisticsbycategories", "Statistiques par catégories", "analyse",
                  "Tableau de statistiques d'un champ regroupé par catégories."),
    AlgorithmSpec("native:countpointsinpolygon", "Compter les points", "analyse",
                  "Compte les points contenus dans chaque polygone."),
    AlgorithmSpec("native:joinattributestable", "Jointure attributaire", "analyse",
                  "Joint les attributs d'une table à une couche par champ commun."),
    AlgorithmSpec("native:joinattributesbylocation", "Jointure spatiale", "analyse",
                  "Joint les attributs d'une couche selon la relation spatiale."),
    AlgorithmSpec("native:nearestneighbouranalysis", "Plus proche voisin", "analyse",
                  "Indice de répartition spatiale d'une couche de points."),
    AlgorithmSpec("native:shortestline", "Lignes les plus courtes", "analyse",
                  "Trace la ligne la plus courte entre deux couches."),
    AlgorithmSpec("native:voronoipolygons", "Polygones de Voronoï", "analyse",
                  "Partage l'espace selon la proximité à des points."),
    AlgorithmSpec("native:zonalstatisticsfb", "Statistiques zonales", "analyse",
                  "Statistiques d'un raster calculées dans chaque polygone."),
    # --- Conversion --------------------------------------------------------
    AlgorithmSpec("native:polygonstolines", "Polygones vers lignes", "conversion",
                  "Convertit des polygones en lignes."),
    AlgorithmSpec("native:linestopolygons", "Lignes vers polygones", "conversion",
                  "Ferme des lignes pour créer des polygones."),
    AlgorithmSpec("native:explodelines", "Éclater les lignes", "conversion",
                  "Découpe chaque ligne en segments élémentaires."),
    AlgorithmSpec("native:fieldcalculator", "Calculatrice de champ", "conversion",
                  "Crée une copie de la couche avec un champ calculé par une expression QGIS.",
                  ("calcul", "expression", "champ")),
    AlgorithmSpec("native:addautoincrementalfield", "Ajouter un identifiant", "conversion",
                  "Ajoute un champ numérique auto-incrémenté."),
    # --- Raster / terrain --------------------------------------------------
    AlgorithmSpec("gdal:cliprasterbymasklayer", "Découper un raster", "raster",
                  "Découpe un raster selon une couche de masque vectorielle."),
    AlgorithmSpec("gdal:warpreproject", "Reprojeter un raster", "raster",
                  "Transforme un raster vers un autre système de coordonnées."),
    AlgorithmSpec("gdal:polygonize", "Raster vers vecteur", "raster",
                  "Vectorise un raster en polygones par valeur de pixel."),
    AlgorithmSpec("native:slope", "Pente", "terrain",
                  "Calcule la pente à partir d'un modèle numérique de terrain.",
                  ("mnt", "pente", "relief")),
    AlgorithmSpec("native:aspect", "Exposition", "terrain",
                  "Calcule l'orientation des versants à partir d'un MNT."),
    AlgorithmSpec("native:hillshade", "Ombrage", "terrain",
                  "Calcule un ombrage du relief à partir d'un MNT."),
    AlgorithmSpec("gdal:contour", "Courbes de niveau", "terrain",
                  "Génère des courbes de niveau à partir d'un MNT."),
)

BY_ID: dict[str, AlgorithmSpec] = {spec.algorithm_id: spec for spec in ALGORITHMS}

def is_allowed(algorithm_id: str) -> bool:
    """Vrai si l'algorithme figure dans la liste blanche."""
    return algorithm_id in BY_ID

def get_spec(algorithm_id: str) -> AlgorithmSpec | None:
    """Renvoie la fiche de l'algorithme, ou None s'il n'est pas autorisé."""
    return BY_ID.get(algorithm_id)

def search_algorithms(
        query: str | None = None, category: str | None = None
) -> list[AlgorithmSpec]:
    """Filtre la liste blanche par catégorie et/ou par mots-clés.

    La recherche ignore la casse et les accents et porte sur l'identifiant,
    le libellé, le résumé et les mots-clés.
    """
    results: list[AlgorithmSpec] = list(ALGORITHMS)
    if category:
        wanted = normalize(category)
        results = [spec for spec in results if normalize(spec.category) == wanted]
    if query:
        terms = [term for term in normalize(query).split() if term]
        results = [spec for spec in results if _matches(spec, terms)]
    return results

def _matches(spec: AlgorithmSpec, terms: Iterable[str]) -> bool:
    haystack = normalize(
        " ".join((spec.algorithm_id, spec.label, spec.summary, " ".join(spec.keywords)))
    )
    return all(term in haystack for term in terms)
