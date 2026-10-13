# Cynogis

Pilotage de **QGIS Desktop** par une IA via le **Model Context Protocol (MCP)**, conçu pour un
bureau d'études environnement travaillant à **La Réunion** (EPSG:2975, RGR92 / UTM 40S) et à
**Mayotte** (EPSG:4471, RGM04 / UTM 38S).

L'utilisateur décrit sa demande en langage naturel ; l'assistant IA (Claude ou tout client MCP)
enchaîne les outils Cynogis directement dans QGIS — avec des garde-fous : niveaux de permission,
tampon d'édition, confirmation humaine, sorties jamais écrasées et journal d'audit.

## Fonctionnalités

Une centaine d'outils, regroupés par domaine :

| Domaine | Exemples |
|---|---|
| Projet et couches | inventaire, métadonnées, SCR, infos raster, audit de projet, organisation des couches |
| Géotraitements | reprojection, correction de géométries, tampon, fusion, extraction, superposition, jointure spatiale |
| Édition vectorielle | champs, attributs, déplacement, découpage, fusion et accrochage de géométries |
| Qualité des données | contrôle des géométries, chevauchements, diagnostic des shapefiles et de l'encodage |
| Paysage | nomenclature fermée Réunion / Mayotte, classification, indices FRAGSTATS, ravines |
| Terrain | pente, exposition, accumulation de flux, classes de pente, échantillonnage du MNT |
| Biodiversité | TAXREF, HABREF, statuts de protection, carte d'enjeux pondérés, densité de points |
| Études d'impact | croisement avec les zonages réglementaires, surfaces d'habitats impactés, comparaison de variantes |
| Relevés de terrain | plans d'échantillonnage, import GPX / CSV / KoboToolbox / QField |
| Services web | catalogue WMS / WFS (IGN, DEAL, INPN), téléchargement d'entités |
| Statistiques | descriptives, zonales, coefficients d'urbanisme (CES, COS, CBS, ruissellement) |
| Cartographie et livrables | styles, étiquettes, export d'image, atlas PDF, tables, notes de synthèse |

La liste exacte est fournie au client MCP par le plugin lui-même (`list_tools`).

## Sécurité

Chaque outil déclare un niveau :

| Niveau | Effet |
|---|---|
| `READ` | lecture seule |
| `CREATE` | produit de nouvelles données, ne touche jamais l'existant |
| `MODIFY` | modifie dans le **tampon d'édition** QGIS, rien n'est écrit sur disque, tout est annulable |
| `DESTROY` | **confirmation humaine** dans QGIS, avec un résumé de l'impact |

- Écriture sur disque uniquement via `request_commit` (`DESTROY`), après affichage du journal des modifications.
- `run_algorithm` n'accepte qu'une liste blanche d'algorithmes Processing ; les sorties sont imposées par Cynogis.
- Sorties en GeoPackage dans `<projet>/mcp_outputs/`, jamais écrasées (suffixes `_2`, `_3`…), ajoutées au groupe « Cynogis ».
- `execute_pyqgis` (dernier recours) : l'IA décrit chaque étape, l'utilisateur voit le code et accepte ou refuse.
- Pont TCP limité à `127.0.0.1`, protégé par un jeton régénéré à chaque démarrage. Aucune donnée ne quitte le poste.
- Chaque appel est journalisé (`~/.cynogis/audit`).

## Architecture

```
Client MCP (Claude, MCP Inspector) ──stdio──> server/   cynogis_server (venv Python)
                                                  │ TCP 127.0.0.1, JSON-lines + jeton
                                                  ▼
                                             plugin/cynogis   (dans QGIS, thread principal Qt)
                                               bridge/ → core/dispatcher.py → tools/*.py
```

- **`server/`** — serveur MCP générique : il ne déclare aucun outil, il relaie `list_tools` et
  `call_tool` vers le plugin et met le catalogue en cache (`~/.cynogis/tools_cache.json`).
- **`plugin/cynogis/`** — plugin QGIS : pont TCP, dispatcher (validation, permissions, audit) et outils PyQGIS.
  `core/` contient la logique pure, testée sans QGIS ; `tools/` contient le code PyQGIS.
- **Découverte** : au démarrage du pont, le plugin écrit `~/.cynogis/connection.json`
  (`host`, `port`, `token`, `pid`). Override : variable `CYNOGIS_CONNECTION_FILE`.

## Prérequis

- QGIS **3.38 à 4.x** (Qt5 ou Qt6)
- Python ≥ 3.10 pour le serveur MCP
- Un client MCP (Claude Desktop, Claude Code, MCP Inspector…)

## Installation

### 1. Serveur MCP

```bash
git clone https://github.com/Ingeniir/Cynogis.git
cd Cynogis
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"     # Linux / macOS : .venv/bin/python
```

### 2. Plugin QGIS

Copier (ou lier) `plugin/cynogis` dans le dossier des plugins du profil QGIS :

- Windows : `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\cynogis`
- Linux : `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/cynogis`

Pour le développement, `scripts/dev_setup.py` crée la jonction et l'autocomplétion PyQGIS (voir plus bas).

Activer **Cynogis Réunion-Mayotte** dans *Extensions → Installer/Gérer les extensions*, puis cliquer
sur le bouton **« Serveur GeoMCP »** de la barre d'outils pour démarrer le pont.

### 3. Client MCP

Exemple pour Claude Desktop (`claude_desktop_config.json`) :

```json
{
  "mcpServers": {
    "cynogis": {
      "command": "C:/chemin/vers/Cynogis/.venv/Scripts/python.exe",
      "args": ["-m", "cynogis_server"]
    }
  }
}
```

Pour Claude Code : `claude mcp add cynogis -- C:/chemin/vers/Cynogis/.venv/Scripts/python.exe -m cynogis_server`

Vérifier le pont sans IA (QGIS ouvert, pont démarré) :

```bash
.venv/Scripts/python scripts/ping_qgis.py
```

## Utilisation

Exemples de demandes :

- « Liste les couches du projet et signale celles qui ne sont pas en EPSG:2975. »
- « Croise l'emprise du projet avec les zonages réglementaires et calcule les surfaces d'habitats impactés, direct et indirect à 50 m. »
- « Classe la pente du MNT en 5 classes et superpose-la aux parcelles. »
- « Corrige les géométries de la couche Parcelles, puis résous les chevauchements en gardant le plus grand polygone. »

Les modifications restent dans le tampon d'édition jusqu'à validation dans QGIS.

## Développement

```bash
.venv/Scripts/python -m pytest                              # tests unitaires (sans QGIS)
.venv/Scripts/python -m ruff check plugin server scripts tests
npx @modelcontextprotocol/inspector .venv/Scripts/python -m cynogis_server
```

Mise en place du poste :

1. Dans la console Python de QGIS, exécuter `scripts/qgis_env_snippet.py` → génère `.qgis_env.json`.
2. `.venv/Scripts/python scripts/dev_setup.py` → `.pth` vers PyQGIS et jonction du plugin dans le profil QGIS.
3. Après chaque modification du plugin, **le recharger dans QGIS** (Plugin Reloader ou redémarrage).

### Ajouter un outil

Tout se passe dans le plugin, rien à modifier côté serveur :

```python
@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "distance": Param("number", "Distance en mètres."),
    "output_name": OUTPUT_NAME,
})
def mon_outil(layer_id: str, distance: float, output_name: str | None) -> ToolResult:
    """Description lue par l'IA : quand l'utiliser, unités, limites."""
    layer = get_vector_layer(layer_id)
    return run_to_project("native:buffer", {"INPUT": layer, "DISTANCE": distance}, output_name)
```

- Nom de la fonction = nom de l'outil ; les clés de `params` doivent correspondre à la signature ; docstring obligatoire.
- Nouveau module : l'ajouter à `TOOL_MODULES` dans `plugin.py`.
- `core/` ne doit jamais importer `qgis` : c'est ce qui le rend testable.

Conventions détaillées : [`CLAUDE.md`](CLAUDE.md) et [`RAPORT.md`](RAPORT.md).

## Dépannage

| Symptôme | Cause |
|---|---|
| `QGIS_UNAVAILABLE` | QGIS fermé ou pont non démarré (bouton « Serveur GeoMCP ») |
| Le comportement ne suit pas le code | plugin non rechargé dans QGIS |
| `[UNKNOWN] Erreur inconnue` | réponse d'erreur mal formée côté plugin : voir le journal QGIS, onglet « Cynogis » |
| Appel abandonné après 120 s | traitement trop long sur le thread principal de QGIS |

## Auteur

Cédric Hoareau — [Ingeniir](https://github.com/Ingeniir)
