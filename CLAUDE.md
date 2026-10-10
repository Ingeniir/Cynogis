# Cynogis

Pilotage de QGIS par une IA via MCP, pour un bureau d'études (La Réunion EPSG:2975, Mayotte EPSG:4471).

## Architecture

Deux processus reliés par un pont TCP local :

```
Client MCP (Inspector, Claude) ──stdio──> server/  (cynogis_server, FastMCP, venv)
                                              │ TCP 127.0.0.1, JSON-lines + jeton
                                              ▼
                                         plugin/cynogis  (dans QGIS, thread principal Qt)
```

- `plugin/cynogis/` — plugin QGIS. `bridge/server.py` (QTcpServer) → `bridge/protocol.py` (décodage) → `core/dispatcher.py` (méthode → handler) → `tools/*.py`.
- `server/src/cynogis_server/` — serveur MCP. `app.py` déclare les `@mcp.tool()`, `client.py` ouvre une connexion TCP par appel.
- Découverte : le plugin écrit `~/.cynogis/connection.json` (`host`, `port`, `token`, `pid`) au démarrage ; le serveur le relit à chaque appel. Override : variable `CYNOGIS_CONNECTION_FILE`.

## Protocole du pont (v1)

Une ligne JSON UTF-8 par message.
- Requête : `{"v":1,"id":str,"token":str,"method":str,"params":{}}`
- Réponse OK : `{"v":1,"id","ok":true,"data","warnings":[]}`
- Réponse erreur : `{"v":1,"id","ok":false,"error":{"code","message","details"}}` — codes dans `core/errors.py::ErrorCode`.

`PROTOCOL_VERSION` et `MAX_MESSAGE_BYTES` sont dupliqués dans `plugin/cynogis/bridge/protocol.py` et `server/src/cynogis_server/client.py` : les modifier aux deux endroits.

## Ajouter un outil

1. Handler dans `plugin/cynogis/tools/<module>.py` : `def f(params: dict) -> dict | ToolResult`. Retour simple = succès ; `ToolResult(data, warnings)` pour des avertissements ; lever `ToolError(ErrorCode.X, msg)` pour une erreur métier.
2. L'enregistrer dans la fonction `register(dispatcher)` du module (appelée depuis `plugin.py`).
3. Exposer côté MCP dans `server/src/cynogis_server/app.py` : `@mcp.tool()` async qui appelle `call_qgis("<méthode>", **params)`. La docstring sert de description à l'IA.

## Contraintes

- `plugin/cynogis/__init__.py`, `core/dispatcher.py`, `core/errors.py`, `bridge/protocol.py` : **aucun import `qgis`** (testés sans QGIS).
- Chaque sous-dossier du plugin doit avoir un `__init__.py` (même vide) : sans lui, le hook d'import de QGIS ne suit pas les modules, ils survivent au déchargement et un rechargement mélange anciennes et nouvelles classes.
- Imports Qt sensibles à la version (ex. `QAction`) → passer par `compat.py`. Cible : QGIS 3.x (Qt5) et 4.x (Qt6).
- Les handlers tournent sur le thread principal de QGIS : pas d'appel bloquant long.
- Logger : `logging.getLogger("cynogis...")` uniquement (seul le logger `cynogis` est redirigé vers le journal QGIS, onglet « Cynogis »).
- Le serveur MCP communique en stdio : ne jamais `print()` sur stdout dans `cynogis_server` (logs → stderr).
- Le venv (Python 3.14) n'est pas le Python de QGIS (3.12) : le code du plugin doit rester compatible avec le Python de QGIS.

## Commandes

```bash
.venv/Scripts/python -m pytest                    # tests unitaires (sans QGIS)
.venv/Scripts/python -m ruff check plugin server scripts tests
.venv/Scripts/python scripts/ping_qgis.py         # teste le pont sans IA (QGIS + serveur Cynogis démarrés)
npx @modelcontextprotocol/inspector .venv/Scripts/python -m cynogis_server
.venv/Scripts/python scripts/dev_setup.py         # .pth vers PyQGIS + jonction du plugin dans le profil QGIS
```

`scripts/qgis_env_snippet.py` est à exécuter dans la console Python de QGIS pour générer `.qgis_env.json`.

## Débogage

- Le plugin est lié par jonction dans le profil QGIS : après une modification du plugin, **recharger le plugin dans QGIS** (Plugin Reloader ou redémarrage) — sinon le serveur MCP parle à l'ancien code.
- Le bouton « Serveur GeoMCP » de la barre d'outils démarre/arrête le pont ; sans lui, `QGIS_UNAVAILABLE`.
- `[UNKNOWN] Erreur inconnue` côté client = réponse `ok:false` sans champ `error` → bug côté plugin.
