"""Nomenclature des paysages de La Réunion et de Mayotte.

La nomenclature est volontairement fermée : l'IA ne peut pas inventer un type
de paysage, elle rattache les valeurs du terrain à des codes existants. La
structure suit la logique de Corine Land Cover (grand poste puis détail) afin
que les restitutions restent comparables aux référentiels nationaux.

Les couleurs sont des suggestions de départ : la décision « le style est libre »
reste valable, l'IA peut proposer autre chose.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field

from .naming import normalize

TERRITORIES = ("reunion", "mayotte", "commun")
# Mots trop génériques pour rattacher une valeur à une classe à eux seuls.
STOP_WORDS = frozenset({"a", "au", "aux", "d", "de", "des", "du", "en", "et", "l", "la", "le",
                        "les", "sur", "zone", "zones", "type", "autre", "autres"})


@dataclass(frozen=True)
class LandscapeClass:
    """Un type de paysage de la nomenclature."""

    code: str
    label: str
    group: str
    territory: str = "commun"
    keywords: tuple[str, ...] = field(default_factory=tuple)
    color: str = "#cccccc"
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "label": self.label,
            "group": self.group,
            "territory": self.territory,
            "suggested_color": self.color,
            "note": self.note,
        }


GROUPS = {
    "1": "Territoires artificialisés",
    "2": "Territoires agricoles",
    "3": "Forêts et milieux semi-naturels",
    "4": "Zones humides",
    "5": "Surfaces en eau",
}

CLASSES: tuple[LandscapeClass, ...] = (
    # --- 1. Territoires artificialisés ------------------------------------
    LandscapeClass("1.1.1", "Tissu urbain dense", "1", "commun",
                   ("urbain", "ville", "centre", "bourg", "agglomeration"), "#d7191c"),
    LandscapeClass("1.1.2", "Habitat diffus", "1", "commun",
                   ("diffus", "pavillonnaire", "mitage", "habitat isole"), "#f08080",
                   "Mitage caractéristique des mi-pentes réunionnaises."),
    LandscapeClass("1.2.1", "Zone d'activité et commerciale", "1", "commun",
                   ("activite", "industriel", "commercial", "zone artisanale"), "#cc4ccc"),
    LandscapeClass("1.2.2", "Réseau routier", "1", "commun",
                   ("route", "voirie", "chemin", "piste", "rn", "nationale"), "#4d4d4d"),
    LandscapeClass("1.2.4", "Aéroport et port", "1", "commun",
                   ("aeroport", "port", "piste aeroport", "quai"), "#8c8c8c"),
    LandscapeClass("1.3.1", "Carrière et extraction", "1", "commun",
                   ("carriere", "extraction", "gravier", "andain"), "#a6761d"),
    LandscapeClass("1.4.1", "Espace vert urbain", "1", "commun",
                   ("parc", "jardin", "square", "espace vert"), "#a6d96a"),
    LandscapeClass("1.4.2", "Équipement sportif et de loisirs", "1", "commun",
                   ("stade", "sport", "loisir", "camping", "terrain de foot"), "#c2e699"),
    # --- 2. Territoires agricoles -----------------------------------------
    LandscapeClass("2.1.1", "Canne à sucre", "2", "reunion",
                   ("canne", "canne a sucre", "sucriere"), "#ffd92f",
                   "Culture dominante des bas de La Réunion."),
    LandscapeClass("2.1.2", "Culture maraîchère", "2", "commun",
                   ("maraichage", "maraicher", "legume", "jardin creole"), "#fee08b"),
    LandscapeClass("2.1.3", "Culture vivrière", "2", "mayotte",
                   ("vivrier", "manioc", "banane", "jardin mahorais"), "#fdd49e",
                   "Souvent en cultures associées sous couvert arboré à Mayotte."),
    LandscapeClass("2.2.1", "Verger et arboriculture", "2", "commun",
                   ("verger", "arboriculture", "letchi", "mangue", "agrume"), "#d9a441"),
    LandscapeClass("2.2.3", "Plantation pérenne", "2", "mayotte",
                   ("ylang", "vanille", "girofle", "cocoteraie", "plantation"), "#bf9000"),
    LandscapeClass("2.3.1", "Prairie et pâturage", "2", "commun",
                   ("prairie", "pature", "paturage", "elevage", "herbage"), "#b8e186"),
    LandscapeClass("2.4.1", "Mosaïque agricole", "2", "commun",
                   ("mosaique", "agricole mixte", "polyculture"), "#e6d8a0"),
    # --- 3. Forêts et milieux semi-naturels -------------------------------
    LandscapeClass("3.1.1", "Forêt humide de montagne", "3", "reunion",
                   ("foret humide", "bois de couleurs des hauts", "foret primaire"), "#1a9641",
                   "Forêt de bois de couleurs des Hauts, cœur du Parc national."),
    LandscapeClass("3.1.2", "Forêt semi-sèche", "3", "reunion",
                   ("semi seche", "foret seche", "savane boisee"), "#78c679",
                   "Milieu très relictuel, enjeu de conservation majeur."),
    LandscapeClass("3.1.3", "Tamarinaie", "3", "reunion",
                   ("tamarin", "tamarinaie", "tamarin des hauts"), "#41ab5d"),
    LandscapeClass("3.1.4", "Forêt naturelle", "3", "mayotte",
                   ("foret naturelle", "foret mahoraise", "relique forestiere"), "#238b45"),
    LandscapeClass("3.1.5", "Plantation forestière", "3", "commun",
                   ("cryptomeria", "plantation forestiere", "reboisement", "cryptomeria japonica"),
                   "#006837"),
    LandscapeClass("3.2.1", "Savane", "3", "commun",
                   ("savane", "herbacee seche", "zone seche"), "#dfc27d"),
    LandscapeClass("3.2.2", "Fourré et brande", "3", "reunion",
                   ("brande", "fourre", "avoune", "ericacee", "branle"), "#9bbb59"),
    LandscapeClass("3.2.3", "Végétation arbustive", "3", "commun",
                   ("arbustif", "broussaille", "fourre secondaire", "friche"), "#8fbc8f"),
    LandscapeClass("3.2.4", "Espèces exotiques envahissantes", "3", "commun",
                   ("envahissant", "exotique", "goyavier", "vigne marronne", "acacia"),
                   "#b15928", "À distinguer du couvert naturel dans les diagnostics."),
    LandscapeClass("3.3.1", "Roche nue et éboulis", "3", "commun",
                   ("roche", "rocher", "eboulis", "falaise", "rempart"), "#bdbdbd"),
    LandscapeClass("3.3.2", "Coulée de lave", "3", "reunion",
                   ("lave", "coulee", "enclos", "volcan", "scorie"), "#636363",
                   "Coulées du Piton de la Fournaise, végétation pionnière."),
    LandscapeClass("3.3.3", "Padza", "3", "mayotte",
                   ("padza", "sol erode", "laterite", "badland"), "#d95f0e",
                   "Sol latéritique dénudé, marqueur d'érosion propre à Mayotte."),
    LandscapeClass("3.3.4", "Sol nu", "3", "commun",
                   ("sol nu", "terre nue", "denude", "remblai"), "#cfa16b"),
    LandscapeClass("3.3.5", "Plage et cordon littoral", "3", "commun",
                   ("plage", "sable", "cordon", "dune", "galet"), "#ffe6b3"),
    # --- 4. Zones humides --------------------------------------------------
    LandscapeClass("4.1.1", "Zone humide intérieure", "4", "commun",
                   ("zone humide", "marais", "tourbiere", "etang"), "#80cdc1"),
    LandscapeClass("4.2.1", "Mangrove", "4", "mayotte",
                   ("mangrove", "paletuvier", "vasiere"), "#01665e",
                   "Milieu protégé, interface terre-lagon à Mayotte."),
    LandscapeClass("4.2.2", "Herbier et platier", "4", "mayotte",
                   ("herbier", "platier", "estran"), "#35978f"),
    # --- 5. Surfaces en eau -------------------------------------------------
    LandscapeClass("5.1.1", "Ravine et lit de rivière", "5", "commun",
                   ("ravine", "riviere", "bras", "lit", "thalweg", "cours d eau"), "#4393c3",
                   "Élément structurant majeur du paysage réunionnais et mahorais."),
    LandscapeClass("5.1.2", "Plan d'eau", "5", "commun",
                   ("bassin", "retenue", "lac", "plan d eau", "reservoir"), "#2166ac"),
    LandscapeClass("5.2.1", "Lagon et récif", "5", "mayotte",
                   ("lagon", "recif", "corail", "barriere"), "#92c5de"),
    LandscapeClass("5.2.2", "Mer", "5", "commun",
                   ("mer", "ocean", "marin"), "#1f4e79"),
)

BY_CODE: dict[str, LandscapeClass] = {item.code: item for item in CLASSES}


def classes_for(territory: str | None = None) -> list[LandscapeClass]:
    """Classes applicables à un territoire (les classes communes incluses)."""
    if not territory:
        return list(CLASSES)
    wanted = normalize(territory)
    if wanted not in TERRITORIES:
        raise ValueError(f"Territoire inconnu : {territory} (attendu : reunion, mayotte).")
    return [item for item in CLASSES if item.territory in ("commun", wanted)]


def get_class(code: str) -> LandscapeClass | None:
    """Fiche d'une classe par son code, None si le code est inconnu."""
    return BY_CODE.get(str(code).strip())


def validate_codes(codes: Iterable[str], territory: str | None = None) -> list[str]:
    """Renvoie les codes qui n'appartiennent pas à la nomenclature.

    Garde-fou central : aucun code inventé ne doit entrer dans une couche.
    """
    allowed = {item.code for item in classes_for(territory)}
    return [str(code) for code in codes if str(code) not in allowed]


def score_match(value: str, item: LandscapeClass) -> float:
    """Score de ressemblance entre une valeur de terrain et une classe.

    Le score est volontairement simple et explicable : correspondance exacte,
    puis mot-clé entier, puis inclusion partielle. Aucun apprentissage, aucun
    résultat imprévisible.
    """
    text = normalize(value)
    if not text:
        return 0.0
    if text == item.code:
        return 1.0
    label = normalize(item.label)
    if text == label:
        return 1.0
    words = set(text.split()) - STOP_WORDS
    padded = f" {text} "
    best = 0.0
    for keyword in (label, *(normalize(k) for k in item.keywords)):
        if not keyword:
            continue
        if text == keyword:
            best = max(best, 0.95)
        elif f" {keyword} " in padded or f" {text} " in f" {keyword} ":  # mots entiers
            best = max(best, 0.8)
        else:  # mots en commun : toujours sous 0.8, donc à vérifier par un humain
            common = words & set(keyword.split())
            if common:
                best = max(best, min(0.5 + 0.1 * len(common), 0.75))
    return best


def suggest_mapping(
    values: Sequence[str],
    territory: str | None = None,
    threshold: float = 0.5,
) -> dict:
    """Propose une correspondance entre les valeurs d'un champ et la nomenclature.

    Rien n'est appliqué : la proposition est soumise à l'IA puis à l'humain.
    Les valeurs non reconnues sont listées pour être tranchées explicitement.
    """
    candidates = classes_for(territory)
    mapping: dict[str, dict] = {}
    unmatched: list[str] = []
    for raw in values:
        value = "" if raw is None else str(raw)
        scored = [(score_match(value, item), item) for item in candidates]
        scored.sort(key=lambda pair: (-pair[0], pair[1].code))
        best_score, best_item = scored[0] if scored else (0.0, None)
        if best_item is None or best_score < threshold:
            unmatched.append(value)
            continue
        mapping[value] = {
            "code": best_item.code,
            "label": best_item.label,
            "confidence": round(best_score, 2),
            "alternatives": [
                {"code": item.code, "label": item.label, "confidence": round(score, 2)}
                for score, item in scored[1:4]
                if score >= threshold * 0.8
            ],
        }
    return {
        "mapping": mapping,
        "unmatched": unmatched,
        "matched_count": len(mapping),
        "review_required": [
            value for value, entry in mapping.items() if entry["confidence"] < 0.8
        ],
    }


def apply_mapping(value, mapping: Mapping[str, str], default: str | None = None) -> str | None:
    """Traduit une valeur de terrain en code de nomenclature.

    La correspondance est cherchée telle quelle, puis sous forme normalisée :
    « Forêt humide » et « foret humide » désignent la même chose.
    """
    if value is None:
        return default
    text = str(value)
    if text in mapping:
        return mapping[text]
    normalized = {normalize(key): code for key, code in mapping.items()}
    return normalized.get(normalize(text), default)


def merge_nomenclature(custom: Sequence[Mapping]) -> list[LandscapeClass]:
    """Intègre des classes propres au bureau d'études, après validation.

    Chaque entrée doit fournir code, label et group ; les codes existants sont
    refusés pour éviter qu'une redéfinition passe inaperçue.
    """
    added: list[LandscapeClass] = []
    for entry in custom or []:
        code = str(entry.get("code") or "").strip()
        label = str(entry.get("label") or "").strip()
        group = str(entry.get("group") or "").strip()
        if not code or not label:
            raise ValueError("Chaque classe doit comporter un code et un libellé.")
        if code in BY_CODE:
            raise ValueError(f"Le code {code} existe déjà dans la nomenclature.")
        if group not in GROUPS:
            raise ValueError(f"Groupe inconnu : {group} (attendu : {', '.join(GROUPS)}).")
        territory = normalize(entry.get("territory") or "commun")
        if territory not in TERRITORIES:
            raise ValueError(f"Territoire inconnu : {territory}")
        added.append(
            LandscapeClass(
                code=code,
                label=label,
                group=group,
                territory=territory,
                keywords=tuple(str(k) for k in entry.get("keywords") or ()),
                color=str(entry.get("color") or "#cccccc"),
                note=str(entry.get("note") or ""),
            )
        )
    return added


def register(classes: Sequence[LandscapeClass]) -> int:
    """Ajoute des classes validées à la nomenclature de la session."""
    global CLASSES
    CLASSES = CLASSES + tuple(classes)
    for item in classes:
        BY_CODE[item.code] = item
    return len(classes)
