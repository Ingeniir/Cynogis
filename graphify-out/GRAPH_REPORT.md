# Graph Report - cynogis  (2026-10-26)

## Corpus Check
- 135 files · ~96,832 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2049 nodes · 6049 edges · 93 communities (77 shown, 16 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 468 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- tools/proximity.py (2)
- tool
- dispatcher.py
- Services web OGC
- styling.py (2)
- editing.py
- report.py (2)
- Serveur MCP stdio
- Métriques paysagères
- Coefficients (cœur)
- Opérations sur couleurs
- HABREF
- Typage des champs
- Référentiels OCS (cœur)
- Tests des jobs
- Dispatcher
- tools/impacts.py
- Styles (cœur)
- EditJournal
- core/landscape.py
- Dérivés de terrain
- Point d'entrée du plugin
- TAXREF
- collections_abc
- ToolRegistry
- Shapefiles et encodage
- Données de terrain
- tools/project_audit.py
- Liste blanche d'algorithmes
- Résolution des chevauchements
- Historique des styles
- describe
- styling.py
- to_float
- tools/impacts.py (2)
- Security model (six guardrails)
- tools/project_audit.py (2)
- find_source_file
- Impacts et enjeux
- tasks.py
- tasks.py (2)
- Fichier de connexion
- Installation développeur
- Schéma des paramètres
- tasks.py (3)
- Exécuteur factice
- Tests du dispatcher
- Construction du ZIP
- Journal d'audit
- Feuille de route
- Guide d'installation
- Cache des zonages
- Requêtes WFS
- Protocole et découverte (2)
- measures.py
- Découpe de transects
- Protocole et découverte
- Fraîcheur des zonages
- Classes de paysage
- tasks.py (4)
- units.py
- core/sampling.py
- Chemins du cache
- ToolError
- Security model (six guardrails) (2)
- Zonages WFS (outils)
- tasks.py (5)
- core/zoning.py
- Contrôle de code PyQGIS
- Règles réglementaires
- Phase 1 : Fiabilite des calculs de surface
- Rapport des fonctionnalités
- Fraîcheur des zonages (2)
- common.py
- Pacer
- Options de style
- feature_request
- geometry_report
- export_layer
- Pacer (2)
- core/zoning.py (2)
- editing.py (2)
- feature_request (2)
- tools/project_audit.py (3)
- Zonages WFS (outils) (2)
- Compatibilité Qt
- Résolution des chevauchements (2)
- dispatcher.py (2)
- Paquet serveur

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 170 edges
2. `ErrorCode` - 152 edges
3. `tool()` - 139 edges
4. `get_vector_layer()` - 94 edges
5. `ToolResult` - 92 edges
6. `feature_request()` - 63 edges
7. `geometry_kind()` - 57 edges
8. `require_field()` - 51 edges
9. `to_json_value()` - 49 edges
10. `distance_area()` - 46 edges

## Surprising Connections (you probably didn't know these)
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `note() : avertissements remontés par les helpers` --references--> `note()`  [EXTRACTED]
  CLAUDE.md → plugin/cynogis/core/jobs.py
- `1.2 Interdire les surfaces en EPSG:4326` --semantically_similar_to--> `SCR : EPSG:2975 (Réunion), EPSG:4471 (Mayotte), jamais de surface en 4326`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `1.3 Methode plane ou ellipsoidale documentee` --semantically_similar_to--> `Toujours indiquer la méthode de calcul de surface`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Exécution non bloquante dans QGIS** — claude_nonblocking_jobs, claude_job_response, claude_fetch_http, claude_pacer, claude_job_cancellation [EXTRACTED 1.00]
- **Cynogis safety guardrails** — claude_permission_levels, claude_algorithm_whitelist, raport_restricted_network, raport_audit_log, claude_edit_buffer [EXTRACTED 1.00]
- **Garde-fous Cynogis** — claude_permission_levels, claude_edit_buffer, claude_algorithm_whitelist, readme_audit_log, readme_execute_pyqgis [EXTRACTED 1.00]
- **Deploiement poste entreprise** — installation_network_share, installation_private_plugin_repo, installation_uv_tool_install, installation_shared_config, installation_referentials_dir, installation_mcp_clients [EXTRACTED 1.00]
- **Regles metier codifiees par la phase 2** — claude_natura2000_exclusion, claude_thresholds_config_rule, claude_deterministic_prediagnostic, docs_roadmap_phase2_reglementaire [INFERRED 0.85]
- **Garde-fous de sécurité** — claude_security_rules, claude_permission_levels, claude_edit_buffer, claude_outputs_no_overwrite, claude_algorithm_whitelist [INFERRED 0.85]
- **Règles de calcul des surfaces** — claude_crs_rule, claude_surface_method_rule, claude_surface_helper_rule, claude_dissolve_by_class_rule, claude_note_warnings [INFERRED 0.85]
- **Long job execution flow** — raport_long_job_flow, raport_internal_tools [INFERRED 0.85]
- **Fiabilite des surfaces (regles, roadmap 1.1-1.3, helpers)** — claude_crs_rule, claude_surface_method_rule, claude_surface_helper_rule, docs_roadmap_1_1_reference_tests, docs_roadmap_1_2_forbid_4326, docs_roadmap_1_3_surface_method, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.95]

## Communities (93 total, 16 thin omitted)

### Community 0 - "tools/proximity.py (2)"
Cohesion: 0.04
Nodes (57): Pacer, convert_length(), compute_coefficients(), _geometries(), landscape_metrics(), list_coefficients(), _load_zones(), _polygon_layer() (+49 more)

### Community 1 - "tool"
Cohesion: 0.04
Nodes (46): ToolError, tool(), _allowed(), describe_algorithm(), run_algorithm(), get_raster_layer(), _isopleths(), kernel_density_points() (+38 more)

### Community 2 - "dispatcher.py"
Cohesion: 0.09
Nodes (21): ToolResult, Level, Param, detect_territory(), clean_number(), crs_info(), enum_name(), extent_wgs84() (+13 more)

### Community 3 - "Services web OGC"
Cohesion: 0.07
Nodes (41): Fetch, capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+33 more)

### Community 4 - "styling.py (2)"
Cohesion: 0.06
Nodes (42): clean_values(), compute_breaks(), _dedupe(), equal_interval(), format_number(), natural_breaks(), pretty_breaks(), quantile_breaks() (+34 more)

### Community 5 - "editing.py"
Cohesion: 0.08
Nodes (36): ErrorCode, unique_field_name(), begin_edit(), geometry_from_wkt(), get_vector_layer(), is_shapefile(), select_ids(), wkt_to_layer_crs() (+28 more)

### Community 6 - "report.py (2)"
Cohesion: 0.07
Nodes (42): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+34 more)

### Community 7 - "Serveur MCP stdio"
Cohesion: 0.07
Nodes (22): QgsLogHandler, setup_logging(), teardown_logging(), main(), call_tool(), _fetch_specs(), list_tools(), _progress_token() (+14 more)

### Community 8 - "Métriques paysagères"
Cohesion: 0.07
Nodes (32): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), fractal_dimension(), interpret_metrics(), largest_patch_index() (+24 more)

### Community 9 - "Coefficients (cœur)"
Cohesion: 0.09
Nodes (26): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+18 more)

### Community 10 - "Opérations sur couleurs"
Cohesion: 0.09
Nodes (21): contrast_ratio(), darken(), distinct_colors(), interpolate_ramp(), lighten(), mix(), parse_color(), relative_luminance() (+13 more)

### Community 11 - "HABREF"
Cohesion: 0.08
Nodes (19): Box, layout_boxes(), page_size(), correspond(), Habitat, _index(), load_correspondences(), load_typology() (+11 more)

### Community 12 - "Typage des champs"
Cohesion: 0.09
Nodes (21): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), truncate_field_names(), to_ascii() (+13 more)

### Community 13 - "Référentiels OCS (cœur)"
Cohesion: 0.10
Nodes (20): _covers(), map_cirad(), map_feature(), map_ocsge(), Rule, _segments(), Source, sources_for() (+12 more)

### Community 14 - "Tests des jobs"
Cohesion: 0.12
Nodes (25): app(), boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req() (+17 more)

### Community 15 - "Dispatcher"
Cohesion: 0.11
Nodes (6): Response, BridgeServer, Dispatcher, finish(), collecting(), render_notes()

### Community 16 - "tools/impacts.py"
Cohesion: 0.09
Nodes (15): add_to_memory(), make_field(), _isopleth_geometries(), _save_isopleths(), export_table(), _write_csv(), write_table(), import_field_data() (+7 more)

### Community 17 - "Styles (cœur)"
Cohesion: 0.10
Nodes (24): readable_text_color(), build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_readable_text_color() (+16 more)

### Community 18 - "EditJournal"
Cohesion: 0.09
Nodes (14): check_batch_size(), describe_summary(), EditEntry, EditJournal, _commit_details(), rollback_edits(), journal(), test_check_batch_size() (+6 more)

### Community 19 - "core/landscape.py"
Cohesion: 0.09
Nodes (17): apply_mapping(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+9 more)

### Community 20 - "Dérivés de terrain"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 21 - "Point d'entrée du plugin"
Cohesion: 0.10
Nodes (5): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin

### Community 22 - "TAXREF"
Cohesion: 0.12
Nodes (15): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+7 more)

### Community 23 - "collections_abc"
Cohesion: 0.09
Nodes (16): validate_colors(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors(), validate_palette() (+8 more)

### Community 24 - "ToolRegistry"
Cohesion: 0.13
Nodes (8): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 25 - "Shapefiles et encodage"
Cohesion: 0.12
Nodes (14): companion_paths(), export_plan(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), test_export_plan_renommage(), test_export_plan_type_non_supporte() (+6 more)

### Community 26 - "Données de terrain"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 27 - "tools/project_audit.py"
Cohesion: 0.15
Nodes (11): file_format(), layer_kind(), source_path(), audit_project(), _layer_facts(), _open_project(), _overview_map(), _project_facts() (+3 more)

### Community 28 - "Liste blanche d'algorithmes"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 29 - "Résolution des chevauchements"
Cohesion: 0.16
Nodes (14): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus(), test_half_plane_contient_le_milieu_cote_a() (+6 more)

### Community 30 - "Historique des styles"
Cohesion: 0.15
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 31 - "describe"
Cohesion: 0.15
Nodes (8): describe(), describe_groups(), _r(), to_float(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 32 - "styling.py"
Cohesion: 0.13
Nodes (11): clean_name(), unique_path(), export_atlas_pdf(), _overview_extent(), _output_path(), output_dir(), export_layer(), save_style_file() (+3 more)

### Community 33 - "to_float"
Cohesion: 0.13
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 34 - "tools/impacts.py (2)"
Cohesion: 0.13
Nodes (10): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), _zones(), test_anneaux(), test_comparaison_variantes() (+2 more)

### Community 35 - "Security model (six guardrails)"
Cohesion: 0.15
Nodes (15): Liste blanche ALGORITHMS (run_algorithm), Édition dans le tampon (begin_edit, JOURNAL, request_commit), Sorties via run_to_project / save_to_project, jamais d'écrasement, Niveaux de permission READ / CREATE / MODIFY / DESTROY, 3.2/3.3 Donnees sensibles et filtrage RGPD, 3.4 Audit des garde-fous, Phase 3 : Tracabilite et confidentialite, Audit log (get_audit_log) (+7 more)

### Community 36 - "tools/project_audit.py (2)"
Cohesion: 0.18
Nodes (8): looks_like_mojibake(), crs_from_text(), check_shapefile(), load_layer(), _mojibake_hint(), _scan_sidecars(), set_layer_encoding(), _text_sample()

### Community 37 - "find_source_file"
Cohesion: 0.14
Nodes (8): find_source_file(), referentials_directory(), _clipped(), list_reference_sources(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 38 - "Impacts et enjeux"
Cohesion: 0.18
Nodes (12): Criterion, level_for(), level_number(), Override, parse_criteria(), parse_overrides(), parse_thresholds(), score() (+4 more)

### Community 39 - "tasks.py"
Cohesion: 0.18
Nodes (3): _FetchTask, _Handle, ProcessingExecutor

### Community 41 - "Fichier de connexion"
Cohesion: 0.21
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 42 - "Installation développeur"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 43 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 44 - "tasks.py (3)"
Cohesion: 0.17
Nodes (3): _input_layers(), _needs_main_thread(), _take_layers()

### Community 45 - "Exécuteur factice"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 46 - "Tests du dispatcher"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 47 - "Construction du ZIP"
Cohesion: 0.22
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 48 - "Journal d'audit"
Cohesion: 0.25
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 49 - "Feuille de route"
Cohesion: 0.14
Nodes (12): Feuille de route Cynogis, Jalons, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic), Phase 3 : Traçabilité et confidentialité (+4 more)

### Community 50 - "Guide d'installation"
Cohesion: 0.14
Nodes (14): Guide d'installation poste entreprise, Clients MCP (Claude Code, Claude Desktop, Codex), Partage reseau \\SERVEUR\Cynogis, Depot QGIS prive (plugins.xml), CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...), Depannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN...), Installation du serveur via uv tool (cynogis-server.exe), metadata.txt (Cynogis Reunion-Mayotte 0.1.0) (+6 more)

### Community 51 - "Cache des zonages"
Cohesion: 0.16
Nodes (8): cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, regulatory_prescan(), test_cache_meta_roundtrip_and_matching(), test_par_territoire()

### Community 52 - "Requêtes WFS"
Cohesion: 0.18
Nodes (6): getfeature_url(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 53 - "Protocole et découverte (2)"
Cohesion: 0.15
Nodes (11): Protocole du pont v1, Fetch (téléchargement HTTP dans une QgsTask), Fin de tâche : graphify update + GRAPH_REPORT.md, Annulation du job (suppression de couche / fermeture du projet), Réponse « job » (get_job_status / cancel_job), Jobs non bloquants (yield from, QgsTask), Pacer (rend la main à QGIS toutes les 100 ms), Débogage : recharger le plugin, bouton Serveur GeoMCP (+3 more)

### Community 54 - "measures.py"
Cohesion: 0.19
Nodes (6): Commandes de développement (pytest, ruff, ping_qgis, check_surfaces), check_dissolved(), check_geographic_rejected(), check_site(), square(), utm_scale()

### Community 55 - "Découpe de transects"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 56 - "Protocole et découverte"
Cohesion: 0.17
Nodes (10): Découverte via ~/.cynogis/connection.json, Serveur MCP générique (relais list_tools / call_tool), Cache du catalogue d'outils (~/.cynogis/tools_cache.json), Configuration partagee (web_services.json, palettes.json), Architecture and operation, Cynogis project report (RAPORT.md), ~/.cynogis user directory, Long job flow (AlgCall, Fetch, Pause, Pacer) (+2 more)

### Community 57 - "Fraîcheur des zonages"
Cohesion: 0.23
Nodes (7): age_days(), describe_sources(), freshness(), prescan_sections(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing(), test_prescan_sections_lists_sources_with_origin()

### Community 58 - "Classes de paysage"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 60 - "units.py"
Cohesion: 0.22
Nodes (6): elongation(), convert_area(), test_elongation(), test_detect(), test_conversions(), test_unknown_unit()

### Community 61 - "core/sampling.py"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 62 - "Chemins du cache"
Cohesion: 0.24
Nodes (5): cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_root_env_override()

### Community 63 - "ToolError"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 64 - "Security model (six guardrails) (2)"
Cohesion: 0.24
Nodes (6): Procédure d'ajout d'un outil (@tool), note() : avertissements remontés par les helpers, Contrat de retour (dict / ToolResult / ToolError), 1.2 Interdire les surfaces en EPSG:4326, Code conventions (writing a tool), Shared helpers to reuse (tools/common.py, outputs.py)

### Community 65 - "Zonages WFS (outils)"
Cohesion: 0.27
Nodes (5): service_label(), _bbox_wgs84(), _cached_source(), Source, _sources()

### Community 66 - "tasks.py (5)"
Cohesion: 0.27
Nodes (6): AlgCall, Pause, run_now(), test_run_now(), algo(), steps()

### Community 67 - "core/zoning.py"
Cohesion: 0.24
Nodes (5): bbox_covers(), should_replace_cache(), status(), test_bbox_rules(), test_statut()

### Community 68 - "Contrôle de code PyQGIS"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 69 - "Règles réglementaires"
Cohesion: 0.28
Nodes (6): Cynogis (pilotage de QGIS par une IA via MCP), 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 70 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.22
Nodes (8): 1.1 Tests de surfaces de reference (2975 / 4471), 1.3 Methode plane ou ellipsoidale documentee, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, 3.1 Encart de tracabilite automatique, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 71 - "Rapport des fonctionnalités"
Cohesion: 0.25
Nodes (9): Ecological impact study workflow (ERC), Ecology referentials (TAXREF, BDC Statuts, HABREF, zonings), Ecology, proximity, stakes and impacts tools, Internal tools (list_tools, get_job_status, cancel_job), Landscape diagnosis workflow, Closed landscape nomenclature, Coefficients, landscape, terrain tools, Tool catalog (101 + 4 internal) (+1 more)

### Community 72 - "Fraîcheur des zonages (2)"
Cohesion: 0.36
Nodes (3): Provenance, provenance_from_data(), test_provenance_roundtrip_and_kind_check()

### Community 73 - "common.py"
Cohesion: 0.29
Nodes (4): list_layers(), _summary(), _tree(), _visible()

### Community 74 - "Pacer"
Cohesion: 0.29
Nodes (3): is_agricultural(), _overlay(), test_is_agricultural()

### Community 75 - "Options de style"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 76 - "feature_request"
Cohesion: 0.33
Nodes (3): expression_context(), prepare_expression(), _local_source()

### Community 78 - "export_layer"
Cohesion: 0.47
Nodes (3): add_to_group(), add_to_project(), _output_item()

### Community 80 - "core/zoning.py (2)"
Cohesion: 0.40
Nodes (3): assess(), zoning_state(), test_pre_diagnostic()

## Knowledge Gaps
- **30 isolated node(s):** `cynogis-server`, `Green Map Location Pin`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)`, `Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats)`, `1.5 Gestion des doubles comptes` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 704 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `tool` to `tools/proximity.py (2)`, `dispatcher.py`, `Services web OGC`, `styling.py (2)`, `editing.py`, `HABREF`, `Tests des jobs`, `Dispatcher`, `tools/impacts.py`, `collections_abc`, `ToolRegistry`, `tools/project_audit.py`, `styling.py`, `tools/project_audit.py (2)`, `find_source_file`, `tasks.py`, `tasks.py (2)`, `Fichier de connexion`, `Schéma des paramètres`, `tasks.py (3)`, `Exécuteur factice`, `Tests du dispatcher`, `ToolError`, `Zonages WFS (outils)`, `feature_request`, `export_layer`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Are the 83 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 83 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `Green Map Location Pin`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)` to the rest of the system?**
  _30 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/proximity.py (2)` be split into smaller, more focused modules?**
  _Cohesion score 0.041970802919708027 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `editing.py` to `tools/proximity.py (2)`, `tool`, `dispatcher.py`, `Services web OGC`, `styling.py (2)`, `HABREF`, `Tests des jobs`, `Dispatcher`, `tools/impacts.py`, `collections_abc`, `ToolRegistry`, `tools/project_audit.py`, `styling.py`, `tools/project_audit.py (2)`, `find_source_file`, `tasks.py`, `tasks.py (2)`, `Fichier de connexion`, `Schéma des paramètres`, `tasks.py (3)`, `Exécuteur factice`, `Tests du dispatcher`, `ToolError`, `feature_request`, `export_layer`, `Zonages WFS (outils) (2)`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 116 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 116 INFERRED edges - model-reasoned connections that need verification._
- **Should `tool` be split into smaller, more focused modules?**
  _Cohesion score 0.03813646670789528 - nodes in this community are weakly interconnected._