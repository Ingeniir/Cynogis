"""Construction des notes de synthèse livrées avec les données.

Le rapport est produit à partir de données structurées fournies par l'IA, pas
d'un texte libre reformaté : les tableaux restent cohérents avec les chiffres
calculés par les outils.
"""

from __future__ import annotations

import datetime as _datetime
import html
from collections.abc import Mapping, Sequence

from .classify import format_number

MAX_SECTIONS = 50
MAX_ROWS = 2000


def _escape_cell(value, decimals: int = 2) -> str:
    """Rend une valeur présentable dans un tableau."""
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "oui" if value else "non"
    if isinstance(value, (int, float)):
        return format_number(value, 0 if isinstance(value, int) else decimals)
    return str(value).replace("|", "/").replace("\n", " ")


def normalize_table(table: Mapping) -> dict:
    """Valide un tableau et uniformise ses lignes.

    Accepte soit des lignes sous forme de dictionnaires, soit des listes avec
    un en-tête explicite.
    """
    rows = list(table.get("rows") or [])
    if len(rows) > MAX_ROWS:
        raise ValueError(f"Tableau trop volumineux : {len(rows)} lignes, maximum {MAX_ROWS}.")
    headers = list(table.get("headers") or [])
    if rows and isinstance(rows[0], Mapping):
        if not headers:
            headers = list(rows[0].keys())
        values = [[row.get(column) for column in headers] for row in rows]
    else:
        values = [list(row) for row in rows]
        width = max((len(row) for row in values), default=0)
        if not headers:
            headers = [f"Colonne {index + 1}" for index in range(width)]
        values = [row + [None] * (width - len(row)) for row in values]
    return {"headers": [str(header) for header in headers], "rows": values}


def normalize_sections(sections: Sequence[Mapping]) -> list[dict]:
    """Valide les sections du rapport."""
    if len(sections or []) > MAX_SECTIONS:
        raise ValueError(f"Rapport trop long : maximum {MAX_SECTIONS} sections.")
    normalized: list[dict] = []
    for index, section in enumerate(sections or []):
        if not isinstance(section, Mapping):
            raise ValueError(f"Section {index + 1} : objet attendu.")
        entry: dict = {
            "heading": str(section.get("heading") or f"Section {index + 1}"),
            "text": str(section.get("text") or "").strip(),
            "bullets": [str(item) for item in (section.get("bullets") or [])],
        }
        if section.get("table"):
            entry["table"] = normalize_table(section["table"])
        normalized.append(entry)
    return normalized


def build_markdown(
    title: str,
    sections: Sequence[Mapping],
    metadata: Mapping | None = None,
    decimals: int = 2,
) -> str:
    """Compose le rapport au format Markdown."""
    parts = [f"# {title}", ""]
    stamp = _datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")
    parts.append(f"*Note produite le {stamp} avec Cynogis.*")
    parts.append("")
    if metadata:
        for key, value in metadata.items():
            parts.append(f"- **{key}** : {_escape_cell(value, decimals)}")
        parts.append("")
    for section in normalize_sections(sections):
        parts.append(f"## {section['heading']}")
        parts.append("")
        if section["text"]:
            parts.extend([section["text"], ""])
        for bullet in section["bullets"]:
            parts.append(f"- {bullet}")
        if section["bullets"]:
            parts.append("")
        table = section.get("table")
        if table and table["headers"]:
            parts.append("| " + " | ".join(table["headers"]) + " |")
            parts.append("|" + "|".join([" --- "] * len(table["headers"])) + "|")
            for row in table["rows"]:
                parts.append(
                    "| " + " | ".join(_escape_cell(cell, decimals) for cell in row) + " |"
                )
            parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def build_html(
    title: str,
    sections: Sequence[Mapping],
    metadata: Mapping | None = None,
    decimals: int = 2,
) -> str:
    """Compose le même rapport au format HTML, imprimable tel quel."""
    escape = html.escape
    stamp = _datetime.datetime.now().strftime("%d/%m/%Y à %H:%M")
    style = (
        "body{font-family:Calibri,Arial,sans-serif;margin:2.5cm;color:#222;}"
        "h1{border-bottom:2px solid #1a9641;padding-bottom:6px;}"
        "h2{color:#1a6b2f;margin-top:1.6em;}"
        "table{border-collapse:collapse;margin:1em 0;width:100%;}"
        "th,td{border:1px solid #bbb;padding:5px 8px;text-align:left;font-size:0.95em;}"
        "th{background:#eef5ee;}"
        "tr:nth-child(even) td{background:#fafafa;}"
        ".meta{color:#666;font-size:0.9em;}"
    )
    parts = [
        "<!DOCTYPE html>",
        '<html lang="fr"><head><meta charset="utf-8">',
        f"<title>{escape(title)}</title><style>{style}</style></head><body>",
        f"<h1>{escape(title)}</h1>",
        f'<p class="meta">Note produite le {stamp} avec Cynogis.</p>',
    ]
    if metadata:
        parts.append("<ul>")
        for key, value in metadata.items():
            parts.append(
                f"<li><strong>{escape(str(key))}</strong> : "
                f"{escape(_escape_cell(value, decimals))}</li>"
            )
        parts.append("</ul>")
    for section in normalize_sections(sections):
        parts.append(f"<h2>{escape(section['heading'])}</h2>")
        if section["text"]:
            parts.append(f"<p>{escape(section['text'])}</p>")
        if section["bullets"]:
            parts.append("<ul>")
            parts.extend(f"<li>{escape(bullet)}</li>" for bullet in section["bullets"])
            parts.append("</ul>")
        table = section.get("table")
        if table and table["headers"]:
            parts.append("<table><thead><tr>")
            parts.extend(f"<th>{escape(header)}</th>" for header in table["headers"])
            parts.append("</tr></thead><tbody>")
            for row in table["rows"]:
                parts.append("<tr>")
                parts.extend(
                    f"<td>{escape(_escape_cell(cell, decimals))}</td>" for cell in row
                )
                parts.append("</tr>")
            parts.append("</tbody></table>")
    parts.append("</body></html>")
    return "\n".join(parts)


def table_to_rows(records: Sequence[Mapping], columns: Sequence[str] | None = None) -> dict:
    """Transforme une liste de dictionnaires en tableau prêt à écrire."""
    items = list(records or [])
    if not items:
        return {"headers": list(columns or []), "rows": []}
    headers = list(columns) if columns else list(items[0].keys())
    return {
        "headers": headers,
        "rows": [[record.get(column) for column in headers] for record in items],
    }
