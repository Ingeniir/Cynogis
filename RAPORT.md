# Cynogis — rapport de projet

> Document d'orientation destiné à toute IA (ou tout développeur) qui reprend le projet.
> Il décrit **ce que fait Cynogis, comment il fonctionne, les fichiers clés, le catalogue des
> outils, les règles à respecter et les pièges connus**. Les consignes courtes de travail sont
> dans `CLAUDE.md` ; ce rapport les explique et les complète. En cas de doute, le code fait foi.
>
> État au 19/10/2026 (après la PR #23) : **101 outils exposés à l'IA** + 4 outils internes,
> 28 modules d'outils, **385 tests unitaires** au vert.

---

## 1. En une phrase

Cynogis permet à une IA (Claude, ou tout client MCP) de **piloter QGIS Desktop** pour un bureau
d'études en environnement et aménagement travaillant à **La Réunion (EPSG:2975, RGR92 / UTM 40S)**
et à **Mayotte (EPSG:4471, RGM04 / UTM 38S)** : lecture des couches, géotraitements, édition
vectorielle, analyse paysagère, écologie (habitats, taxons, enjeux, impacts, ERC), terrain,
proximité, services web, style, export et rapports — avec des garde-fous (liste blanche,
tampon d'édition, confirmation humaine, audit, sorties jamais écrasées, traitements en tâche
de fond).

---

## 2. Architecture et fonctionnement

Deux processus reliés par un pont TCP local :

```
Client MCP (Claude, MCP Inspector…)
        │ stdio (protocole MCP)
        ▼
server/src/cynogis_server/        ← serveur MCP GÉNÉRIQUE (venv Python 3.14, SDK mcp bas niveau)
  app.py    : relaie list_tools / call_tool, ne déclare AUCUN outil ; attend les jobs
  client.py : 1 connexion TCP par appel, timeout 120 s
        │ TCP 127.0.0.1, JSON-lines + jeton
        ▼
plugin/cynogis/                   ← plugin QGIS (Python 3.12 de QGIS, thread principal Qt)
  bridge/server.py   QTcpServer, vérification du jeton
  bridge/protocol.py décodage / encodage des messages (sans qgis)
  core/dispatcher.py méthode → outil : validation, permissions, audit, jobs
  tools/*.py         les outils (code PyQGIS)
  tools/tasks.py     exécuteur des étapes longues dans des QgsTask
```

**Démarrage** : le bouton « Serveur GeoMCP » de la barre d'outils lance le pont. Le plugin écrit
alors `~/.cynogis/connection.json` (`host`, `port`, `token`, `pid`). Le serveur MCP relit ce
fichier à chaque appel (remplacement possible par `CYNOGIS_CONNECTION_FILE`). Pont arrêté →
`QGIS_UNAVAILABLE`.

**Catalogue** : le serveur demande la liste des outils au plugin (`list_tools`, interne) et la
met en cache dans `~/.cynogis/tools_cache.json`, pour que le client MCP voie les outils même
QGIS fermé. Ajouter un outil ne demande **aucune modification côté serveur**.

### Flux d'un appel simple (outil `READ` rapide)

1. Le client MCP appelle par exemple `measure` avec des paramètres JSON.
2. `cynogis_server` ouvre une connexion TCP et envoie
   `{"v":1,"id","token","method":"measure","params":{…}}`.
3. `bridge/server.py` vérifie le jeton, `bridge/protocol.py` décode (taille max, version).
4. `core/dispatcher.py` : outil connu ? → `core/schema.py` valide les paramètres →
   `core/policy.py` vérifie le niveau (fenêtre de confirmation si `DESTROY`) → exécute la
   fonction de `tools/` → `core/audit.py` journalise.
5. Réponse `{"v":1,"id","ok":true,"audit_id","data","warnings":[]}` ou
   `{"ok":false,"error":{"code","message","details"}}` (codes : `core/errors.py::ErrorCode`).

### Flux d'un traitement long (job)

Un outil qui lance un algorithme Processing ou un téléchargement est un **générateur** : au lieu
d'appeler Processing, il **cède une étape** (`AlgCall`, `Fetch`, `Pause` — `core/jobs.py`).

1. Le dispatcher détecte le générateur et crée un job (`JobManager`) ; la réponse part tout de
   suite avec un `job_id` et l'avancement.
2. `tools/tasks.py::ProcessingExecutor` exécute chaque étape dans une `QgsTask` (thread de fond),
   puis reprend le générateur sur le thread principal avec le résultat. QGIS ne gèle pas.
   Repli sur le thread principal si l'algorithme est `NoThreading` ou si une couche d'entrée est
   en édition.
3. Les boucles Python longues cèdent des `Pause` via `Pacer` : la main est rendue à QGIS toutes
   les 100 ms (affichage, autres requêtes).
4. Côté serveur, `app.py::_wait_job` interroge `get_job_status` jusqu'à la réponse finale ;
   annulation MCP ou dépassement d'**1 h** (`JOB_TIMEOUT_S`) → `cancel_job`.
5. Pendant un job, seuls les outils `READ` passent (sinon `BUSY`) ; un seul job à la fois.
   Supprimer une couche ou fermer le projet annule le job (`plugin.py::_cancel_jobs`).

---

## 3. Fichiers les plus utiles

Par ordre d'importance pour comprendre ou modifier le projet :

| Fichier | Pourquoi l'ouvrir |
|---|---|
| `CLAUDE.md` | règles de travail courtes (à respecter avant tout) |
| `plugin/cynogis/plugin.py` | point d'entrée : `TOOL_MODULES`, création du registre, du dispatcher, du pont, bouton |
| `plugin/cynogis/core/registry.py` | décorateur `@tool`, `Level`, contrôle params ↔ signature |
| `plugin/cynogis/core/schema.py` | `Param` → JSON Schema et validation |
| `plugin/cynogis/core/dispatcher.py` | cœur de l'exécution : validation, permissions, audit, jobs, outils internes |
| `plugin/cynogis/core/jobs.py` | modèle des traitements longs (`AlgCall`, `Fetch`, `Pause`, `Pacer`, `run_now`) |
| `plugin/cynogis/tools/tasks.py` | exécution réelle des étapes dans des `QgsTask` |
| `plugin/cynogis/tools/outputs.py` | `run_to_project`, `run_in_memory`, `save_to_project`, `output_dir` |
| `plugin/cynogis/tools/common.py` | helpers PyQGIS partagés (couches, champs, mesures, SCR, édition) |
| `plugin/cynogis/core/errors.py` | `ErrorCode`, `ToolError` |
| `plugin/cynogis/core/algorithms.py` | liste blanche de `run_algorithm` |
| `plugin/cynogis/ui/confirm.py` | fenêtre de confirmation `DESTROY`, `register_detail_provider` |
| `plugin/cynogis/bridge/protocol.py` | format des messages, `PROTOCOL_VERSION`, `MAX_MESSAGE_BYTES` |
| `server/src/cynogis_server/app.py` | relais MCP, cache du catalogue, attente des jobs |
| `server/src/cynogis_server/client.py` | client TCP, lecture de `connection.json` |
| `scripts/ping_qgis.py` | test du pont sans IA |

### Arborescence commentée

```
plugin/cynogis/
  __init__.py          classFactory QGIS (aucun import qgis)
  plugin.py            CynogisPlugin : TOOL_MODULES, registre, dispatcher, bouton, palettes
  compat.py            imports Qt sensibles à la version (QAction…) — Qt5 / Qt6
  metadata.txt         métadonnées QGIS (qgisMinimumVersion=3.38)
  bridge/              pont TCP (connection.py, protocol.py, server.py)
  ui/confirm.py        fenêtre de confirmation DESTROY + register_detail_provider()
  core/                LOGIQUE PURE, testée sans QGIS (aucun import qgis, sauf log.py)
  tools/               OUTILS PyQGIS (un module = un domaine)
server/src/cynogis_server/   serveur MCP générique (app.py, client.py, __main__.py)
scripts/               dev_setup.py, ping_qgis.py, qgis_env_snippet.py
tests/unit/            34 fichiers pytest de core/ et bridge/protocol.py (sans QGIS)
```

### `core/` — logique métier pure (testée)

| Module | Rôle |
|---|---|
| `registry.py` | `@tool`, `Level`, `ToolSpec`, `ToolRegistry` (params ↔ signature, docstring obligatoire) |
| `schema.py` | `Param` → JSON Schema, validation des paramètres |
| `dispatcher.py` | aiguillage, `ToolResult(data, warnings, outputs)`, jobs, outils internes |
| `jobs.py` | étapes de job (`AlgCall`, `Fetch`, `Pause`), `Pacer`, `run_now`, `JobManager` |
| `policy.py` | niveau maximal autorisé, confirmation humaine pour `DESTROY` |
| `errors.py` | `ErrorCode` (enum) et `ToolError` |
| `audit.py` | journal des appels (`~/.cynogis/audit`) |
| `log.py` | redirection du logger `cynogis` vers le journal QGIS (seul module core qui importe qgis) |
| `naming.py` | `clean_name`, `unique_path` (sorties jamais écrasées), `normalize`, `to_ascii` |
| `territory.py` | Réunion / Mayotte, `detect_territory(bbox_wgs84)` → `Territory` (`.code`, `.epsg`) |
| `units.py`, `stats.py` | conversions d'unités ; statistiques descriptives, `to_float` |
| `algorithms.py` | **liste blanche** `ALGORITHMS` de `run_algorithm` + recherche sans accents |
| `codecheck.py` | repérage des appels sensibles du code soumis à `execute_pyqgis` (indicatif) |
| `resolve.py` | stratégies de résolution des chevauchements |
| `fields.py` | types de champs, noms de champs sûrs, conversion des valeurs JSON |
| `edits.py` | `JOURNAL` des modifications en attente, garde-fous de taille des lots |
| `shapefile.py` | fichiers compagnons, limite 2 Go, noms à 10 caractères, mojibake |
| `coefficients.py` | CES, COS, CBS, imperméabilisation, espaces verts, ruissellement |
| `landscape.py` | nomenclature fermée des paysages (Corine-like, classes Réunion / Mayotte) |
| `metrics.py` | indices paysagers FRAGSTATS (Shannon, Simpson, lisière, maille effective…) |
| `terrain.py` | classes de pente, reclassement, secteurs d'exposition |
| `classify.py` | seuils de classification (égaux, quantiles, Jenks, écart-type, arrondis) |
| `colors.py`, `palettes.py` | couleurs (hex, rgb(), noms FR/EN), palettes (`~/.cynogis/palettes.json`) |
| `style.py`, `stylehistory.py` | validation des symboles / étiquettes ; historique `undo_style` |
| `report.py` | notes de synthèse Markdown / HTML |
| `proximity.py` | k plus proches voisins, matrice de distances, anneau ordonné de points |
| `referentials.py` | sources OCS GE / CIRAD sur disque (`~/.cynogis/referentials/` ou `CYNOGIS_REFERENTIALS_DIR`), règles → nomenclature |
| `webservices.py` | catalogue WMS/WFS (intégré + `~/.cynogis/web_services.json`), GetCapabilities |
| `zoning.py` | zonages réglementaires et d'inventaire (Parc national, réserves, ZNIEFF, Ramsar…) |
| `fielddata.py` | relevés de terrain (GPX, CSV, KoboToolbox, QField) → schéma standard |
| `taxref.py` | rattachement des taxons à TAXREF et à la BDC Statuts (INPN) |
| `habref.py` | rattachement des habitats aux typologies locales HABREF |
| `stakes.py` | hiérarchisation des enjeux par critères pondérés |
| `impacts.py` | catégories et synthèse des impacts sur les habitats |
| `sampling.py` | répartition des unités d'échantillonnage entre strates |
| `atlas.py` | mise en page de l'atlas PDF (formats, zones en mm) |
| `project_audit.py` | règles de contrôle et contenu du rapport d'audit de projet |

---

## 4. Modèle de sécurité (à ne jamais contourner)

1. **Niveaux** (`core/registry.py::Level`) — déclarés sur chaque outil :
   - `READ` (0) : lecture seule.
   - `CREATE` (1) : produit de nouvelles données, ne touche jamais l'existant.
   - `MODIFY` (2) : modifie dans le **tampon d'édition** QGIS (ou l'affichage : style, ordre des
     couches) ; rien n'est écrit sur disque avant `request_commit` ; `rollback_edits` annule.
   - `DESTROY` (3) : **confirmation humaine** obligatoire (`ui/confirm.py`), avec un résumé
     d'impact fourni par `register_detail_provider(nom_outil, fonction)`.
2. **Pas de code arbitraire par défaut** : `run_algorithm` n'accepte que la liste blanche
   `core/algorithms.py::ALGORITHMS` ; les paramètres de sortie sont imposés par Cynogis.
   Seule exception : `execute_pyqgis` (`DESTROY`), en dernier recours — l'opérateur voit les
   étapes, la justification, le code et les appels sensibles repérés par `core/codecheck.py`
   (**indicatif, pas un bac à sable**), puis accepte ou refuse.
3. **Sorties jamais écrasées** : `<projet>/mcp_outputs/` (repli `~/.cynogis/mcp_outputs` +
   avertissement si le projet n'est pas enregistré), nom nettoyé, suffixe `_2`, `_3`…
4. **Réseau restreint** : seuls les services du catalogue (`core/webservices.py`) sont
   interrogeables, via le gestionnaire réseau de QGIS (`Fetch`, authcfg).
5. **Audit** de chaque appel (outil, paramètres tronqués, succès/erreur, fichiers créés),
   consultable par `get_audit_log`.
6. **Journal d'édition** (`core/edits.py::JOURNAL`) : ce que l'IA a modifié depuis le dernier
   enregistrement, affiché dans la confirmation de `request_commit`.

---

## 5. Catalogue des outils (101 + 4 internes)

Niveau : R = READ, C = CREATE, M = MODIFY, **D = DESTROY**. Toutes les couches sont désignées
par leur **`layer_id`** (renvoyé par `list_layers`). Toute sortie `C` va dans `mcp_outputs/`
et dans le groupe « Cynogis » du projet. Les surfaces et distances sont **ellipsoïdales** (m², m)
sauf mention contraire.

### 5.1 Système et couches

| Outil | Niv. | Fonctionnement |
|---|---|---|
| `ping` | R | vérifie que QGIS et le plugin répondent ; versions QGIS, Qt, plugin |
| `get_project_info` | R | titre, fichier, SCR, nombre de couches, territoire détecté — à appeler en premier |
| `list_layers` | R | couches dans l'ordre du panneau : layer_id, type, géométrie, SCR, format, nb d'entités, visibilité, édition |
| `get_layer_info` | R | détail d'une couche : champs, encodage, filtre (vecteur) ; bandes, nodata, pixel (raster) ; emprise, territoire |
| `get_raster_info` | R | SCR, emprise, résolution et statistiques par bande (échantillon, ou exact avec `sample_size=0`) |
| `organize_layers` | M | range des couches dans un groupe, change l'ordre et la visibilité ; ne touche pas aux données |

### 5.2 Lecture des entités et mesures

| Outil | Niv. | Fonctionnement |
|---|---|---|
| `get_features` | R | lit fid, attributs et géométrie (WKT/GeoJSON), paginé (`limit`/`offset`, `has_more`) |
| `get_field_values` | R | valeurs distinctes d'un champ avec effectifs et nombre de nulls |
| `check_geometries` | R | contrôle GEOS : nulles, vides, invalides, multi-parties ; échantillon localisé |
| `select_features` | R | surligne des entités dans QGIS (expression ou fid), zoom optionnel |
| `measure` | R | surfaces, périmètres, longueurs : total, stats (moyenne, médiane, quartiles, CV), par groupe avec parts (%) |
| `descriptive_stats` | R | stats d'un champ ou d'une expression, globales et par groupe |
| `shape_indices` | R | compacité de Gravelius, allongement, CV des surfaces, couverture et densité vs couche de référence |
| `habitat_area_stats` | C | tableau des habitats de l'aire d'étude : nb, surface (ha), parts (%), surface moyenne, périmètre |

### 5.3 Chevauchements et géotraitements

| Outil | Niv. | Fonctionnement |
|---|---|---|
| `detect_overlaps` | R | paires de polygones qui se chevauchent (même couche ou deux couches), surface commune triée |
| `resolve_overlaps` | C | copie sans chevauchement : stratégies `priority_field`, `keep_largest`, `keep_oldest`, `split_equally` ; champs de contrôle `cyn_*` |
| `fix_geometries` | C | répare les géométries invalides dans une nouvelle couche |
| `reproject_layer` | C | reprojection dans un nouveau SCR |
| `buffer` | C | zone tampon en mètres (SCR projeté requis), dissolution optionnelle |
| `create_study_area_buffers` | C | aires d'étude immédiate / rapprochée / éloignée (AEI, AER, AEE), avec surface en ha |
| `dissolve` | C | fusion globale ou par champs |
| `extract` | C | extraction par expression OU par relation spatiale |
| `spatial_join` | C | attributs des entités d'une autre couche selon un prédicat spatial, avec agrégats (`summaries`) |
| `overlay` | C | intersection, union, différence ou découpage de deux couches |
| `list_algorithms` | R | algorithmes Processing autorisés (liste blanche), recherche par mot-clé / catégorie |
| `describe_algorithm` | R | paramètres d'entrée d'un algorithme autorisé |
| `run_algorithm` | C | lance un algorithme de la liste blanche ; sorties imposées par Cynogis |

### 5.4 Édition (tampon d'édition, puis validation humaine)

| Outil | Niv. | Fonctionnement |
|---|---|---|
| `get_pending_edits` | R | modifications en attente par couche — à lire avant `request_commit` |
| `add_field` | M | ajoute un champ |
| `delete_field` | **D** | supprime un champ et ses valeurs |
| `add_features` | M | ajoute des entités (WKT + attributs, converties au type des champs) ; tout ou rien |
| `update_attributes` | M | mêmes valeurs sur un ensemble d'entités (expression ou fid, plafond `max_features`) |
| `calculate_field` | M | calcule un champ par expression QGIS (créé au besoin) |
| `delete_features` | **D** | supprime des entités (filtre obligatoire) |
| `update_geometry` | M | remplace la géométrie d'une entité, accrochage optionnel aux couches voisines |
| `move_features` | M | décale des entités de dx/dy mètres (recalage), accrochage optionnel |
| `split_feature` | M | découpe une entité par une ligne ; la 1re partie garde le fid |
| `merge_features` | **D** | fusionne des entités, attributs d'une seule conservés |
| `snap_features` | M | accroche les sommets aux couches voisines (supprime micro-trous / chevauchements) |
| `rollback_edits` | M | annule tout le tampon, retour au dernier enregistrement |
| `request_commit` | **D** | écrit sur disque après récapitulatif et accord de l'opérateur |

### 5.5 Fichiers, création et export

| Outil | Niv. | Fonctionnement |
|---|---|---|
| `check_shapefile` | R | audit d'un shapefile : compagnons, 2 Go, SCR, accents, noms tronqués |
| `load_layer` | C | ajoute un fichier vecteur ou raster au projet (rien n'est copié) |
| `create_layer` | C | couche vide (GeoPackage neuf) avec les champs demandés |
| `set_layer_encoding` | M | change l'encodage de lecture (accents) sans modifier le fichier |
| `export_layer` | C | export vers un nouveau fichier ; Shapefile : noms à 10 caractères + `.cpg` |
| `export_table` | C | table attributaire ou tableau de résultats → CSV / XLSX / ODS |
| `write_report` | C | note de synthèse Markdown / HTML (sections, listes, tableaux, nombres à la française) |
| `export_map_image` | C | PNG des couches visibles |
| `export_atlas_pdf` | C | atlas PDF, une page par entité : carte, légende, localisation, échelle, nord, pied de page |
| `save_project` | **D** | enregistre le projet QGIS (écrase le fichier existant) |
| `audit_project` | C | audit qualité complet du projet (SCR, sources, géométries, index, NoData…) en rapport PDF |
| `execute_pyqgis` | **D** | code PyQGIS libre en dernier recours, après validation du code par l'opérateur |

### 5.6 Coefficients, paysage, terrain

| Outil | Niv. | Fonctionnement |
|---|---|---|
| `list_coefficients` | R | coefficients calculables et catégories de surface avec pondérations |
| `compute_coefficients` | R | CES, CBS, imperméabilisation, espaces verts, ruissellement, COS — global ou par groupe |
| `landscape_metrics` | R | indices FRAGSTATS vectoriels, globaux ou par zone, avec interprétation |
| `list_landscape_classes` | R | nomenclature fermée des paysages (par territoire) |
| `suggest_landscape_mapping` | R | propose valeurs du champ → codes, signale les cas douteux, n'applique rien |
| `classify_landscape` | C | couche classée (`pays_code`, `pays_lib`, `pays_grp`, `pays_surf`) ; code inconnu = échec |
| `extract_ravines` | C | emprise des ravines depuis un réseau de lignes (demi-largeur + bande de protection) |
| `compute_ndvi` | C | raster NDVI (PIR − R) / (PIR + R) |
| `check_landscape` | R | NDVI moyen de chaque unité vs plage attendue de sa classe ; liste les incohérences |
| `list_slope_classes` | R | 5 classes de pente d'aménagement et secteurs d'exposition |
| `derive_terrain` | C | pente, exposition, ombrage ou accumulation de flux d'un MNT |
| `classify_slope` | C | reclassement en 5 classes, polygonisation optionnelle |
| `elevation_sample` | C | altitude, pente, exposition échantillonnées sur le MNT (points ou polygones) |
| `zonal_statistics` | C | statistiques d'un raster dans chaque polygone |
| `list_reference_sources` | R | référentiels OCS GE / CIRAD connus pour le territoire et leur présence sur disque |
| `clip_reference_landcover` | C | découpe un référentiel sur la zone et le traduit dans la nomenclature (option `overlay_sources`) |

### 5.7 Écologie, proximité, enjeux et impacts

| Outil | Niv. | Fonctionnement |
|---|---|---|
| `import_field_data` | C | relevés de terrain (GPX, CSV, Kobo, QField) → couche de points standardisée |
| `taxon_status_join` | C | enrichit les observations par TAXREF et la BDC Statuts (statut, origine, liste rouge…) |
| `habitat_typology_join` | C | rattache les habitats à HABREF (CBNM pour La Réunion, référentiel de Mayotte) |
| `count_points_in_polygon` | R | points par polygone : densité / ha, somme, richesse par catégorie |
| `count_observations` | C | synthèse des observations par habitat ou par maille (nb, richesse, protégées, invasives) |
| `invasive_species_map` | C | pression des espèces exotiques envahissantes par polygone |
| `kernel_density_points` | C | densité par noyau (.tif) avec isoplèthes 95 / 75 / 50 %, polygones optionnels |
| `transect_sampling_plan` | C | plan d'échantillonnage : points ou transects aléatoires, stratifiés ou systématiques |
| `points_to_polygon` | C | polygones depuis des points (enveloppe convexe / concave, anneau ordonné) |
| `nearest_features` | R | k plus proches voisins, distance bord à bord |
| `distance_matrix` | R | distances de chaque entité à chaque autre |
| `distance_layer` | C | lignes reliant chaque entité à ses k plus proches cibles |
| `distance_to_sensitive_features` | C | distance des entités sensibles à l'emprise, statut vs seuil de recul |
| `stake_scoring` | C | carte d'enjeux : score 0-100, niveau 1 Faible … 5 Majeur, surclassements |
| `impact_quantification` | C | surfaces d'habitat détruites (direct) et dégradées (anneaux indirects), par enjeu |
| `erc_variant_compare` | C | démarche ERC « éviter » : compare les variantes d'emprise et leurs impacts résiduels |
| `regulatory_zoning_intersect` | C | croise le projet avec les zonages réglementaires et d'inventaire |
| `fetch_wfs_layer` | C | télécharge les zonages officiels (INPN, ONF, GPU) sur une emprise ou toute l'île |

### 5.8 Services web

| Outil | Niv. | Fonctionnement |
|---|---|---|
| `web_list_services` | R | catalogue WMS / WFS (Géoplateforme IGN + services utilisateur) |
| `web_list_layers` | R | couches d'un service (GetCapabilities), filtrables |
| `web_add_layer` | C | ajoute une couche en flux (WMS image, WFS lisible par l'IA) |
| `web_download_features` | C | télécharge les entités WFS d'une emprise dans un GeoPackage figé |

### 5.9 Style

| Outil | Niv. | Fonctionnement |
|---|---|---|
| `list_style_options` | R | motifs, formes, styles de ligne, placements, palettes, méthodes acceptés |
| `get_layer_style` | R | style actuel (rendu, champ, classes, couleurs, étiquettes) |
| `apply_single_style` | M | symbole unique |
| `apply_categorized_style` | M | une couleur par valeur |
| `apply_graduated_style` | M | classes (égaux, quantiles, Jenks, écart-type, arrondis), légende à la française |
| `apply_landscape_style` | M | couleurs de référence de la nomenclature paysagère |
| `set_labels` | M | étiquettes (champ ou expression), halo par défaut |
| `undo_style` | M | jusqu'à 10 retours par couche (session QGIS) |
| `save_style_file` | C | style → fichier QML |
| `save_palette` | C | palette réutilisable dans `~/.cynogis/palettes.json` |

### 5.10 Outils internes (invisibles pour l'IA)

`list_tools` (catalogue), `get_audit_log` (journal d'audit, aussi exposé), `get_job_status` et
`cancel_job` (pilotage des jobs par le serveur MCP).

### Enchaînements typiques attendus de l'IA

- **Démarrage** : `get_project_info` → `list_layers` → `get_layer_info`.
- **Diagnostic paysager** : `list_reference_sources` → `clip_reference_landcover` (ou
  `suggest_landscape_mapping` → `classify_landscape`) → `compute_ndvi` → `check_landscape` →
  `apply_landscape_style` → `landscape_metrics` → `write_report`.
- **Étude d'impact écologique** : `create_study_area_buffers` → `import_field_data` →
  `taxon_status_join` → `habitat_typology_join` → `stake_scoring` →
  `impact_quantification` / `erc_variant_compare` → `regulatory_zoning_intersect` →
  `export_atlas_pdf`.
- **Édition** : `add_features` / `update_geometry`… → `get_pending_edits` → `request_commit`
  (confirmation) ou `rollback_edits`.
- **Pente** : `derive_terrain` → `classify_slope` → `overlay` avec les parcelles.
- **Chevauchements** : `check_geometries` → `fix_geometries` → `detect_overlaps` →
  `resolve_overlaps`.

---

## 6. Conventions de code (impératives)

### Écrire un outil

```python
@tool(level=Level.CREATE, params={
    "layer_id": Param("string", "Couche vecteur (layer_id)."),
    "distance": Param("number", "Distance en mètres."),
    "output_name": OUTPUT_NAME,             # tools/geoprocessing.py
})
def mon_outil(layer_id: str, distance: float, output_name: str | None):
    """Docstring OBLIGATOIRE : c'est la description lue par l'IA (quand l'utiliser, unités)."""
    layer = get_vector_layer(layer_id)
    result = (yield from run_to_project("native:buffer",
                                        {"INPUT": layer, "DISTANCE": distance},
                                        output_name or "tampon"))
    return result
```

- **Nom de la fonction = nom de l'outil** ; les clés de `params` correspondent **exactement**
  à la signature (sinon erreur au chargement du module).
- **Pas de valeurs par défaut Python** : défauts dans `Param(default=...)`.
- **Paramètre de couche : toujours `layer_id`** (ou `xxx_layer_id`).
- **Processing : toujours `yield from`** sur `run_to_project` / `run_in_memory` (l'outil devient
  un job). Jamais de `processing.run` direct. Sans `yield from`, on récupère un générateur au
  lieu du résultat.
- **HTTP** : céder `Fetch(url, authcfg, libellé, geojson=...)`, jamais de
  `QgsBlockingNetworkRequest` sur le thread principal.
- **Boucle longue** : `pace = Pacer("libellé", total)` puis `yield from pace(i)` en tête de boucle.
  Hors job (volume borné) : `run_now(...)`.
- **Retour** : `dict`, ou `ToolResult(data, warnings, outputs)` dès qu'il y a des avertissements
  ou des fichiers. Jamais de `"warnings"` dans un `dict`.
- **Erreurs** : `raise ToolError(ErrorCode.X, message, details)` avec un membre de l'enum. Une
  chaîne fait planter la sérialisation (`[UNKNOWN] Erreur inconnue` côté client).
- **Nouveau module** : l'ajouter à `TOOL_MODULES` **et** à l'import de `plugin.py`.
- **Outil DESTROY** : fournir un `register_detail_provider` qui décrit l'impact.

### Helpers à réutiliser (ne pas réécrire)

| Besoin | Helper |
|---|---|
| couche / champ | `get_vector_layer`, `get_raster_layer`, `get_layer`, `require_field` (insensible à la casse) |
| requête | `feature_request(layer, filter_expression, attributes, geometry)`, `prepare_expression` |
| géométries reprojetées | `iter_geometries(layer, request, crs)` |
| mesures | `distance_area(crs)` puis `area_m2`, `length_m`, `perimeter_m` (ellipsoïde du SCR, sinon du projet, sinon GRS80 ; `area_m2` répare les polygones invalides avant mesure) |
| type de géométrie | `geometry_kind(layer)` → `"point"`, `"line"`, `"polygon"`, `"none"` |
| valeurs QGIS → JSON | `to_json_value`, `group_key` |
| SCR | `crs_from_text("2975" \| "EPSG:2975")`, `extent_wgs84`, `rect_to_list`, `territory_info` |
| sortie finale | `yield from outputs.run_to_project(alg, params, nom)` (GeoPackage ou `.tif`) |
| étape intermédiaire | `yield from outputs.run_in_memory(alg, params)` → couche mémoire |
| résultat calculé en Python | couche mémoire (`add_to_memory`) puis `save_to_project(couche, nom)` — **pas** `native:savefeatures` (mal typé sous QGIS 4.2) |
| fichier non couche (CSV, QML, PNG, HTML, PDF) | `output_dir()` + `unique_path(dossier, clean_name(nom), suffixe)` |
| édition | `begin_edit`, `select_ids`, `geometry_from_wkt`, `wkt_to_layer_crs`, `make_field`, `refresh_layer` ; tracer avec `JOURNAL` |

### Contraintes techniques

- **`core/` sans import `qgis`** (sauf `core/log.py`), idem `__init__.py` et `bridge/protocol.py`.
  Toute logique testable va dans `core/`, le code PyQGIS dans `tools/`.
- **QGIS 3.38+ (Qt5) et 4.x (Qt6)** : enums scopés (`Qgis.GeometryType.Polygon`), nouvelle forme
  des enums déplacés quand elle existe (`getattr(Qgis, "VectorProviderCapability", None) or …`),
  types de champs via `QMetaType.Type`, imports Qt sensibles via `compat.py`, toujours
  `qgis.PyQt`, jamais `PyQt5`/`PyQt6`/`qgis._core`.
- **Python** : le plugin tourne sous le Python de QGIS (3.12) ; venv de dev en 3.14.
- **Logs** : `logging.getLogger("cynogis…")` uniquement. Dans `cynogis_server`, jamais de
  `print()` (stdout = canal MCP).
- **Protocole** : `PROTOCOL_VERSION` et `MAX_MESSAGE_BYTES` dupliqués dans `bridge/protocol.py`
  et `server/.../client.py`.
- **Chaque sous-dossier du plugin a un `__init__.py`**, sinon le rechargement mélange anciennes
  et nouvelles classes.
- Style : ruff, lignes de 100 caractères, messages et docstrings en français.

---

## 7. Référentiels métier et fichiers utilisateur

- **Territoires** (`core/territory.py`) : Réunion `EPSG:2975`, Mayotte `EPSG:4471`, détectés
  depuis l'emprise WGS84. En UTM, la surface planaire est sous-estimée d'environ 0,08 % à Mayotte
  et de 0 à 0,045 % à La Réunion : la mesure ellipsoïdale est la référence.
- **Nomenclature des paysages** (`core/landscape.py`) : fermée, 5 grands postes, classes communes
  ou propres à un territoire (tamarinaie, coulée de lave ; padza, mangrove).
- **Coefficients** : pondérations de référence — **pas un texte réglementaire**, le PLU prime.
- **Pentes** : 5 classes 0-5, 5-15, 15-30, 30-50, > 50 %.
- **Écologie** : TAXREF + BDC Statuts, HABREF, zonages (Parc national, réserves, ZNIEFF, APB,
  Ramsar, Conservatoire du littoral, Parc naturel marin de Mayotte).
- **Dossier `~/.cynogis/`** : `connection.json`, `tools_cache.json`, `audit/`, `palettes.json`,
  `web_services.json`, `referentials/` (OCS GE, CIRAD, TAXREF, BDC, HABREF ; ou
  `CYNOGIS_REFERENTIALS_DIR`), `mcp_outputs/` (repli).

---

## 8. Tests, qualité, commandes

```bash
.venv/Scripts/python -m pytest                    # 385 tests unitaires (sans QGIS)
.venv/Scripts/python -m ruff check plugin server scripts tests
.venv/Scripts/python scripts/ping_qgis.py         # teste le pont (QGIS + pont démarrés)
npx @modelcontextprotocol/inspector .venv/Scripts/python -m cynogis_server
.venv/Scripts/python scripts/dev_setup.py         # .pth PyQGIS + jonction du plugin dans le profil QGIS
```

`scripts/qgis_env_snippet.py` s'exécute dans la console Python de QGIS pour générer
`.qgis_env.json`.

- Les tests couvrent `core/` et `bridge/protocol.py`. **Le code de `tools/` n'est testé que dans
  QGIS** : après un refactoring, vérifier que chaque nom importé de `tools/common.py` ou
  `tools/outputs.py` existe encore (ruff ne le voit pas).
- Débogage : après modification du plugin, **le recharger dans QGIS** (Plugin Reloader ou
  redémarrage). `QGIS_UNAVAILABLE` = pont non démarré. `[UNKNOWN] Erreur inconnue` = réponse
  `ok:false` sans champ `error` → bug côté plugin.

---

## 9. État du projet et points d'attention

- **Validé** : logique `core/` (385 tests), cohérence statique des outils, traitements en tâche
  de fond (jobs, `QgsTask`, pauses, téléchargements WFS/WMS).
- **Historique récent** : outils d'audit de projet, `execute_pyqgis` avec confirmation, nouveaux
  référentiels, tâches de fond, mesure ellipsoïdale corrigée (ellipsoïde du SCR, polygones
  invalides réparés avant calcul de surface).
- **À valider dans QGIS** : édition de géométrie (split, merge, move, snap), style (catégories
  numériques, `undo_style`), export XLSX/ODS, `classify_slope` vectorisé, `extract_ravines` à
  largeur variable, `classify_landscape` avec `merge_adjacent`, atlas PDF, outils écologie
  (ERC, impacts, enjeux) sur données réelles.
- **Limites connues** :
  - `JOURNAL` (édition) et l'historique de style sont en mémoire : perdus au rechargement ;
  - un seul job à la fois ; les outils non-`READ` reçoivent `BUSY` pendant un job ;
  - les champs de surface déjà calculés (`pays_surf`…) ne sont pas recalculés après une édition
    de géométrie (les outils le signalent) ;
  - `core/codecheck.py` n'est qu'un signalement : la vraie protection d'`execute_pyqgis` est la
    relecture humaine.
- **Incohérence à corriger** : `pyproject.toml`, parenthèse non fermée dans `description`.
