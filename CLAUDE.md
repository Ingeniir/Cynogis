# Cynogis

Pilotage de QGIS par une IA via MCP, pour un bureau d'études (La Réunion EPSG:2975, Mayotte EPSG:4471).

## Architecture

Deux processus reliés par un pont TCP local :

```
Client MCP (Inspector, Claude) ──stdio──> server/  (cynogis_server, SDK MCP bas niveau, venv)
                                              │ TCP 127.0.0.1, JSON-lines + jeton
                                              ▼
                                         plugin/cynogis  (dans QGIS, thread principal Qt)
```

- `plugin/cynogis/` — plugin QGIS. `bridge/server.py` (QTcpServer) → `bridge/protocol.py` (décodage) → `core/dispatcher.py` (méthode → handler) → `tools/*.py`.
- `server/src/cynogis_server/` — serveur MCP **générique** : `app.py` ne déclare aucun outil, il relaie `list_tools` (catalogue fourni par le plugin, mis en cache dans `~/.cynogis/tools_cache.json` si QGIS est absent) et `call_tool`. `client.py` ouvre une connexion TCP par appel (timeout 120 s).
- Découverte : le plugin écrit `~/.cynogis/connection.json` (`host`, `port`, `token`, `pid`) au démarrage ; le serveur le relit à chaque appel. Override : variable `CYNOGIS_CONNECTION_FILE`.

## Protocole du pont (v1)

Une ligne JSON UTF-8 par message.
- Requête : `{"v":1,"id":str,"token":str,"method":str,"params":{}}`
- Réponse OK : `{"v":1,"id","ok":true,"audit_id","data","warnings":[]}`
- Réponse erreur : `{"v":1,"id","ok":false,"audit_id","error":{"code","message","details"}}` — codes dans `core/errors.py::ErrorCode`.
- Réponse « job » (traitement Processing) : `ok:true` + `job_id` + `data` = avancement, renvoyée tout de suite. Le serveur MCP (`app.py::_wait_job`) interroge `get_job_status` jusqu'à la réponse finale (même forme qu'une réponse normale, sans `job_id`) et appelle `cancel_job` sur annulation MCP ou après 1 h. Ces deux outils sont internes (invisibles pour l'IA). Pendant un job, seuls les outils `READ` passent (sinon `BUSY`).

`PROTOCOL_VERSION` et `MAX_MESSAGE_BYTES` sont dupliqués dans `plugin/cynogis/bridge/protocol.py` et `server/src/cynogis_server/client.py` : les modifier aux deux endroits.

## Ajouter un outil

Tout se passe dans le plugin ; rien à modifier côté serveur.

1. Dans `plugin/cynogis/tools/<module>.py`, décorer une fonction avec `@tool(level=Level.X, params={"nom": Param(...)})` (`core/registry.py`, `core/schema.py`). Les noms de `params` doivent correspondre exactement à la signature ; la **docstring est obligatoire** (description pour l'IA) ; le nom de la fonction = nom de l'outil.
2. Niveaux : `READ` (lecture), `CREATE` (nouvelles données), `MODIFY` (tampon d'édition), `DESTROY` (confirmation humaine via `ui/confirm.py`).
3. Retour : `dict` = succès ; `ToolResult(data, warnings, outputs)` pour des avertissements ou des fichiers créés (audit) ; lever `ToolError(ErrorCode.X, msg, details)` pour une erreur métier. Validation des paramètres, permissions et audit sont faits par `core/dispatcher.py`.
4. Nouveau module : l'ajouter à `TOOL_MODULES` dans `plugin.py` (`register_module` échoue si le module ne contient aucun `@tool`).
5. Helpers PyQGIS partagés dans `tools/common.py` (`get_vector_layer`, `require_field`, `feature_request`, `distance_area`…).
6. Outil `DESTROY` : `register_detail_provider(nom, fn)` (`ui/confirm.py`) affiche l'impact (nb d'entités…) dans la fenêtre de confirmation.
7. Édition (`tools/editing.py`) : toujours dans le tampon (`begin_edit`), tracer chaque opération dans `core/edits.py::JOURNAL` ; seul `request_commit` (DESTROY) écrit sur disque.

## Sorties (outils de niveau CREATE)

- Toujours passer par `tools/outputs.py::run_to_project(algorithm_id, params, output_name)`, avec `yield from` (`result = (yield from run_to_project(...))`) : écrit un GeoPackage (`.tif` pour un raster) neuf dans `<projet>/mcp_outputs/` (repli `~/.cynogis/mcp_outputs` + warning si projet non enregistré), nom nettoyé par `core/naming.py`, **jamais d'écrasement** (suffixe `_2`, `_3`…), couche ajoutée au groupe « Cynogis ».
- Résultat calculé en Python (ex. `resolve_overlaps`) : remplir une couche mémoire puis `save_to_project(couche_memoire, nom)` (même résultat que `run_to_project` ; ne pas passer par `native:savefeatures`, dont la sortie « fichier » est mal typée sous QGIS 4.2).
- `run_algorithm` n'accepte que la liste blanche `ALGORITHMS` de `core/algorithms.py` (catalogue pur, testé ; ajouter un `AlgorithmSpec` = autoriser l'algorithme) ; les paramètres de sortie sont imposés par Cynogis, jamais par l'IA.

## Contraintes

- `plugin/cynogis/__init__.py`, `core/*.py` (sauf `core/log.py`), `bridge/protocol.py` : **aucun import `qgis`** (testés sans QGIS dans `tests/unit/`). La logique testable va là ; `tools/` contient le code PyQGIS.
- Chaque sous-dossier du plugin doit avoir un `__init__.py` (même vide) : sans lui, le hook d'import de QGIS ne suit pas les modules, ils survivent au déchargement et un rechargement mélange anciennes et nouvelles classes.
- Imports Qt sensibles à la version (ex. `QAction`) → passer par `compat.py`. Cible : QGIS 3.x (Qt5) et 4.x (Qt6).
- Les handlers tournent sur le thread principal de QGIS. Tout algorithme Processing passe par `run_to_project` / `run_in_memory` **avec `yield from`** : l'outil devient un générateur exécuté comme un job (`core/jobs.py`), l'algorithme tourne dans une `QgsTask` (`tools/tasks.py`) et QGIS ne gèle pas. Jamais de `processing.run` direct ; un appel sans `yield from` renvoie un générateur au lieu du résultat. Téléchargement HTTP : céder `Fetch(url, authcfg, libellé, geojson=...)` (`core/jobs.py`), exécuté dans une `QgsTask` avec le gestionnaire réseau de QGIS ; jamais de `QgsBlockingNetworkRequest` sur le thread principal. Repli automatique sur le thread principal (interface repeinte) si l'algorithme est `NoThreading` ou si une couche d'entrée est en édition. Le code Python entre deux étapes reste sur le thread principal : dans une boucle longue (parcours d'une couche entière avec opérations géométriques), créer `pace = Pacer("libellé", total)` (`core/jobs.py`) et appeler `yield from pace(i)` en tête de boucle, ce qui rend la main à QGIS toutes les 100 ms. Un helper qui cède des pauses est appelé avec `yield from` dans un outil, ou avec `run_now(...)` hors job (volume borné). Une suppression de couche ou la fermeture du projet annule le job en cours (`plugin.py::_cancel_jobs`).
- Logger : `logging.getLogger("cynogis...")` uniquement (seul le logger `cynogis` est redirigé vers le journal QGIS, onglet « Cynogis »).
- Le serveur MCP communique en stdio : ne jamais `print()` sur stdout dans `cynogis_server` (logs → stderr).
- Le venv (Python 3.14) n'est pas le Python de QGIS (3.12) : le code du plugin doit rester compatible avec le Python de QGIS.

## Commandes

```bash
.venv/Scripts/python -m pytest                    # tests unitaires (sans QGIS)
.venv/Scripts/python -m ruff check plugin server scripts tests
.venv/Scripts/python scripts/ping_qgis.py         # teste le pont sans IA (QGIS + serveur Cynogis démarrés)
"C:/Program Files/QGIS 4.2.1/bin/python-qgis.bat" scripts/check_surfaces.py  # surfaces de référence (Python de QGIS)
npx @modelcontextprotocol/inspector .venv/Scripts/python -m cynogis_server
.venv/Scripts/python scripts/dev_setup.py         # .pth vers PyQGIS + jonction du plugin dans le profil QGIS
```

`scripts/qgis_env_snippet.py` est à exécuter dans la console Python de QGIS pour générer `.qgis_env.json`.

## Débogage

- Le plugin est lié par jonction dans le profil QGIS : après une modification du plugin, **recharger le plugin dans QGIS** (Plugin Reloader ou redémarrage) — sinon le serveur MCP parle à l'ancien code.
- Le bouton « Serveur GeoMCP » de la barre d'outils démarre/arrête le pont ; sans lui, `QGIS_UNAVAILABLE`.
- `[UNKNOWN] Erreur inconnue` côté client = réponse `ok:false` sans champ `error` → bug côté plugin.

## Navigation
- Consulter graphify-out/GRAPH_REPORT.md avant d'explorer le code.

## Règles métier (non négociables)
- Systèmes de coordonnées : La Réunion = EPSG:2975 (RGR92 / UTM 40S), Mayotte = EPSG:4471 (RGM04 / UTM 38S).
  Ne jamais calculer une surface en EPSG:4326.
- Surfaces : toujours indiquer la méthode (plane ou ellipsoïdale, projetée ou 3D).
- Natura 2000 NE S'APPLIQUE PAS dans les départements d'outre-mer : ne jamais le proposer.
- Les seuils réglementaires sont dans [fichier de config] : ne jamais les écrire en dur.
- Pré-diagnostic : déterministe (intersections réelles), jamais rédigé par le LLM.

## Sécurité
- Ne jamais contourner les niveaux de permission, la confirmation humaine ni le journal d'audit.
- Les sorties ne doivent jamais écraser de fichiers existants.
- Ne jamais lire ni envoyer au modèle les données d'espèces sensibles ou les données cadastrales nominatives.

## Conventions
- Linting avec Ruff obligatoire avant chaque commit.
- Tâches longues dans des QgsTask (jamais dans le fil de l'interface).
- Une branche par fonctionnalité.

## Fin de tâche
- Après une implémentation terminée et des tests au vert, lancer `graphify update .`
  (analyse du code uniquement, sans LLM) puis inclure graphify-out/ dans le commit.
- Si README, docs/ ou CLAUDE.md ont été modifiés, me le signaler pour que je lance
  `/graphify . --update`.