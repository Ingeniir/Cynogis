# Graph Report - cynogis  (2026-10-26)

## Corpus Check
- 135 files · ~98,139 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2060 nodes · 6146 edges · 100 communities (83 shown, 17 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 501 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- common.py
- editing.py
- Services web OGC
- run_to_project
- Shapefiles et encodage
- styling.py
- tools/project_audit.py
- Métriques paysagères
- Serveur MCP stdio
- ToolError
- tools/proximity.py (2)
- Coefficients (cœur)
- styling.py (2)
- HABREF
- tools/proximity.py (2) (2)
- Tests des jobs
- Référentiels OCS (cœur)
- Dispatcher
- core/landscape.py
- Impacts et enjeux
- report.py (2)
- classify.py
- EditJournal
- Dérivés de terrain
- Opérations sur couleurs
- Styles (cœur)
- TAXREF
- collections_abc
- Données de terrain
- Point d'entrée du plugin
- Résolution des chevauchements
- numpy
- Liste blanche d'algorithmes
- to_float
- numpy (2)
- Historique des styles
- Fraîcheur des zonages
- fetch_wfs_layer
- tools/proximity.py (2) (3)
- ToolRegistry
- Installation développeur
- run_to_project (2)
- tools/proximity.py (2) (4)
- tasks.py
- tasks.py (2)
- find_source_file
- Requêtes WFS
- export.py
- Exécuteur factice
- core/project_audit.py
- describe
- Security model (six guardrails) (2)
- Journal d'audit
- Fichier de connexion
- core/project_audit.py (2)
- Cache des zonages
- _output_path
- Construction du ZIP
- Feuille de route
- Guide d'installation
- collections_abc (2)
- Tests du dispatcher
- BridgeServer
- Découpe de transects
- Schéma des paramètres
- Classes de paysage
- overlaps.py
- tasks.py (2) (2)
- core/sampling.py
- Chemins du cache
- Protocole et découverte
- Protocole et découverte (2)
- Règles réglementaires
- tasks.py (5)
- Cache des zonages (2)
- Contrôle de code PyQGIS
- Security model (six guardrails)
- Opérations sur couleurs (2)
- Rapport des fonctionnalités
- Phase 3 : Tracabilite et confidentialite
- Phase 1 : Fiabilite des calculs de surface
- Serveur MCP stdio (2)
- require_field
- format_number
- geometry_report
- Dérivés de terrain (2)
- styling.py (3)
- Coefficients (cœur) (2)
- Options de style
- export.py (2)
- _sibling
- tools/project_audit.py (2)
- units.py
- plugin.py
- Paquet serveur

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 190 edges
2. `ErrorCode` - 172 edges
3. `tool()` - 144 edges
4. `ToolResult` - 100 edges
5. `get_vector_layer()` - 93 edges
6. `feature_request()` - 61 edges
7. `geometry_kind()` - 54 edges
8. `require_field()` - 53 edges
9. `to_json_value()` - 49 edges
10. `distance_area()` - 45 edges

## Surprising Connections (you probably didn't know these)
- `1.3 Methode plane ou ellipsoidale documentee` --semantically_similar_to--> `Surfaces : toujours indiquer la méthode`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `note() : avertissements remontés par un helper` --references--> `area_m2()`  [EXTRACTED]
  CLAUDE.md → plugin/cynogis/tools/common.py
- `Fusion par classe avant somme (dissolved_areas + overlap_warning)` --references--> `dissolved_areas()`  [EXTRACTED]
  CLAUDE.md → plugin/cynogis/tools/common.py

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Exécution non bloquante des traitements** — claude_nonblocking_jobs, claude_job_response, claude_pacer, claude_fetch_http, claude_job_cancellation [EXTRACTED 1.00]
- **Chaîne client MCP -> serveur -> pont -> plugin** — claude_generic_mcp_server, claude_tcp_bridge, claude_bridge_protocol_v1, claude_connection_discovery, claude_tools_cache [EXTRACTED 1.00]
- **Cynogis safety guardrails** — claude_permission_levels, claude_algorithm_whitelist, raport_restricted_network, raport_audit_log, claude_edit_buffer [EXTRACTED 1.00]
- **Garde-fous Cynogis** — claude_permission_levels, claude_edit_buffer, claude_algorithm_whitelist, readme_audit_log, readme_execute_pyqgis [EXTRACTED 1.00]
- **Deploiement poste entreprise** — installation_network_share, installation_private_plugin_repo, installation_uv_tool_install, installation_shared_config, installation_referentials_dir, installation_mcp_clients [EXTRACTED 1.00]
- **Regles metier codifiees par la phase 2** — claude_natura2000_exclusion, claude_thresholds_config_rule, claude_deterministic_prediagnostic, docs_roadmap_phase2_reglementaire [INFERRED 0.85]
- **Règles de calcul des surfaces** — claude_crs_rule, claude_surface_method_rule, claude_surface_helper_rule, claude_dissolve_by_class_rule, claude_surface_3d_rule [INFERRED 0.85]
- **Long job execution flow** — raport_long_job_flow, raport_internal_tools [INFERRED 0.85]
- **Fiabilite des surfaces (regles, roadmap 1.1-1.3, helpers)** — claude_crs_rule, claude_surface_method_rule, claude_surface_helper_rule, docs_roadmap_1_1_reference_tests, docs_roadmap_1_2_forbid_4326, docs_roadmap_1_3_surface_method, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.95]

## Communities (100 total, 17 thin omitted)

### Community 0 - "common.py"
Cohesion: 0.11
Nodes (12): Level, _check(), Param, _type_ok(), add_to_memory(), geometry_kind(), make_field(), _save_isopleths() (+4 more)

### Community 1 - "editing.py"
Cohesion: 0.07
Nodes (39): begin_edit(), field_type_name(), geometry_from_wkt(), get_vector_layer(), is_shapefile(), layer_field_types(), refresh_layer(), select_ids() (+31 more)

### Community 2 - "Services web OGC"
Cohesion: 0.07
Nodes (40): Fetch, capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+32 more)

### Community 3 - "run_to_project"
Cohesion: 0.05
Nodes (29): tool(), _allowed(), describe_algorithm(), run_algorithm(), list_coefficients(), to_json_value(), kernel_density_points(), buffer() (+21 more)

### Community 4 - "Shapefiles et encodage"
Cohesion: 0.05
Nodes (35): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), truncate_field_names(), to_ascii() (+27 more)

### Community 5 - "styling.py"
Cohesion: 0.07
Nodes (31): ToolResult, expression_context(), feature_request(), prepare_expression(), require_field(), check_geometries(), get_features(), get_field_values() (+23 more)

### Community 6 - "tools/project_audit.py"
Cohesion: 0.08
Nodes (28): looks_like_mojibake(), detect_territory(), clean_number(), crs_info(), enum_name(), extent_wgs84(), file_format(), get_layer() (+20 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Serveur MCP stdio"
Cohesion: 0.08
Nodes (16): QgsLogHandler, setup_logging(), teardown_logging(), main(), call_tool(), _fetch_specs(), list_tools(), _progress_token() (+8 more)

### Community 9 - "ToolError"
Cohesion: 0.08
Nodes (20): ToolError, unique_field_name(), export_map_image(), export_table(), _output_path(), _project_target(), save_project(), _save_project_details() (+12 more)

### Community 10 - "tools/proximity.py (2)"
Cohesion: 0.10
Nodes (18): to_float(), iter_geometries(), _collect(), count_observations(), count_points_in_polygon(), _distance_m(), distance_matrix(), distance_to_sensitive_features() (+10 more)

### Community 11 - "Coefficients (cœur)"
Cohesion: 0.10
Nodes (25): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), list_categories() (+17 more)

### Community 12 - "styling.py (2)"
Cohesion: 0.10
Nodes (17): ErrorCode, clean_name(), unique_path(), export_atlas_pdf(), _from_template(), _overview_extent(), crs_from_text(), add_to_group() (+9 more)

### Community 13 - "HABREF"
Cohesion: 0.09
Nodes (18): Box, layout_boxes(), page_size(), correspond(), Habitat, _index(), load_correspondences(), load_typology() (+10 more)

### Community 14 - "tools/proximity.py (2) (2)"
Cohesion: 0.11
Nodes (15): build_table(), compute_coefficients(), landscape_metrics(), area_m2(), area_method(), distance_area(), group_key(), _distances() (+7 more)

### Community 15 - "Tests des jobs"
Cohesion: 0.12
Nodes (25): app(), boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req() (+17 more)

### Community 16 - "Référentiels OCS (cœur)"
Cohesion: 0.11
Nodes (20): _covers(), map_cirad(), map_feature(), map_ocsge(), Rule, _segments(), Source, sources_for() (+12 more)

### Community 17 - "Dispatcher"
Cohesion: 0.11
Nodes (9): Request, Response, Dispatcher, finish(), collecting(), render_notes(), PermissionPolicy, decorator() (+1 more)

### Community 18 - "core/landscape.py"
Cohesion: 0.09
Nodes (17): apply_mapping(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+9 more)

### Community 19 - "Impacts et enjeux"
Cohesion: 0.10
Nodes (20): compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number(), Override (+12 more)

### Community 20 - "report.py (2)"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 21 - "classify.py"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 22 - "EditJournal"
Cohesion: 0.10
Nodes (12): check_batch_size(), describe_summary(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations() (+4 more)

### Community 23 - "Dérivés de terrain"
Cohesion: 0.11
Nodes (16): aspect_sector(), degrees_to_percent(), distribution(), percent_to_degrees(), reclass_table(), slope_class(), SlopeClass, test_aspect_sector() (+8 more)

### Community 24 - "Opérations sur couleurs"
Cohesion: 0.11
Nodes (16): darken(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), with_alpha() (+8 more)

### Community 25 - "Styles (cœur)"
Cohesion: 0.12
Nodes (21): build_categories(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees(), test_build_categories_lignes_colorees() (+13 more)

### Community 26 - "TAXREF"
Cohesion: 0.14
Nodes (14): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+6 more)

### Community 27 - "collections_abc"
Cohesion: 0.12
Nodes (10): distinct_colors(), validate_colors(), describe_palettes(), landscape_palette(), resolve_colors(), _lookup(), test_distinct_colors_sans_doublon(), test_validate_colors_message_indexe() (+2 more)

### Community 28 - "Données de terrain"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 29 - "Point d'entrée du plugin"
Cohesion: 0.13
Nodes (5): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin

### Community 30 - "Résolution des chevauchements"
Cohesion: 0.14
Nodes (15): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus() (+7 more)

### Community 31 - "numpy"
Cohesion: 0.12
Nodes (10): _isopleth_geometries(), _isopleths(), _style(), _clean(), elevation_sample(), _pixel_labels(), _read_window(), _sector_index() (+2 more)

### Community 32 - "Liste blanche d'algorithmes"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 33 - "to_float"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 34 - "numpy (2)"
Cohesion: 0.12
Nodes (7): Commandes de développement (pytest, ruff, ping, check_surfaces), check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 35 - "Historique des styles"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 36 - "Fraîcheur des zonages"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 37 - "fetch_wfs_layer"
Cohesion: 0.15
Nodes (9): service_label(), _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), _local_source(), Source, _sources() (+1 more)

### Community 38 - "tools/proximity.py (2) (3)"
Cohesion: 0.15
Nodes (8): _geometries(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), dissolved_areas(), overlap_warning(), measure()

### Community 39 - "ToolRegistry"
Cohesion: 0.13
Nodes (5): spec_of(), ToolRegistry, build_details(), make_confirmer(), confirm()

### Community 40 - "Installation développeur"
Cohesion: 0.23
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 41 - "run_to_project (2)"
Cohesion: 0.18
Nodes (7): classify_slope(), derive_terrain(), _flow_accumulation(), list_slope_classes(), _metric_raster(), surface_3d(), zonal_statistics()

### Community 42 - "tools/proximity.py (2) (4)"
Cohesion: 0.18
Nodes (9): Pacer, convert_area(), convert_length(), perimeter_m(), habitat_area_stats(), _r4(), shape_indices(), test_conversions() (+1 more)

### Community 43 - "tasks.py"
Cohesion: 0.18
Nodes (3): _FetchTask, _Handle, ProcessingExecutor

### Community 45 - "find_source_file"
Cohesion: 0.14
Nodes (7): find_source_file(), referentials_directory(), _clipped(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 46 - "Requêtes WFS"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 47 - "export.py"
Cohesion: 0.16
Nodes (3): _input_layers(), _needs_main_thread(), _take_layers()

### Community 48 - "Exécuteur factice"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 49 - "core/project_audit.py"
Cohesion: 0.21
Nodes (10): audit(), build_sections(), duplicate_name_findings(), _finding(), add(), project_findings(), severity_counts(), verdict() (+2 more)

### Community 50 - "describe"
Cohesion: 0.18
Nodes (7): describe(), describe_groups(), _r(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 51 - "Security model (six guardrails) (2)"
Cohesion: 0.16
Nodes (14): Procédure d'ajout d'un outil (@tool), Édition dans le tampon (begin_edit, JOURNAL, request_commit), Réponse « job » (get_job_status / cancel_job, BUSY), note() : avertissements remontés par un helper, Niveaux de permission READ/CREATE/MODIFY/DESTROY, Contrat de retour (dict / ToolResult / ToolError), Audit log (get_audit_log), Code conventions (writing a tool) (+6 more)

### Community 52 - "Journal d'audit"
Cohesion: 0.25
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 53 - "Fichier de connexion"
Cohesion: 0.24
Nodes (7): decode_request(), _protocol_error(), _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 54 - "core/project_audit.py (2)"
Cohesion: 0.32
Nodes (13): layer_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique(), test_projet_sain_sans_anomalie() (+5 more)

### Community 55 - "Cache des zonages"
Cohesion: 0.19
Nodes (8): bbox_covers(), cache_matches(), cache_meta(), _inpn(), should_replace_cache(), Zoning, test_bbox_rules(), test_cache_meta_roundtrip_and_matching()

### Community 56 - "_output_path"
Cohesion: 0.13
Nodes (5): render_map(), _open_project(), _overview_map(), _project_facts(), _raster_facts()

### Community 57 - "Construction du ZIP"
Cohesion: 0.23
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 58 - "Feuille de route"
Cohesion: 0.14
Nodes (12): Feuille de route Cynogis, Jalons, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic), Phase 3 : Traçabilité et confidentialité (+4 more)

### Community 59 - "Guide d'installation"
Cohesion: 0.14
Nodes (14): Guide d'installation poste entreprise, Clients MCP (Claude Code, Claude Desktop, Codex), Partage reseau \\SERVEUR\Cynogis, Depot QGIS prive (plugins.xml), CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...), Depannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN...), Installation du serveur via uv tool (cynogis-server.exe), metadata.txt (Cynogis Reunion-Mayotte 0.1.0) (+6 more)

### Community 60 - "collections_abc (2)"
Cohesion: 0.14
Nodes (9): all_palettes(), get_palette(), load_user_palettes(), register_palette(), validate_palette(), test_get_palette_etiree(), test_get_palette_inconnue(), test_load_user_palettes_ignore_les_erreurs() (+1 more)

### Community 61 - "Tests du dispatcher"
Cohesion: 0.30
Nodes (12): crash(), double(), make(), metier(), _req(), supprimer(), test_destroy_with_confirmation(), test_errors() (+4 more)

### Community 63 - "Découpe de transects"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 64 - "Schéma des paramètres"
Cohesion: 0.24
Nodes (7): object_schema(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum(), test_object_schema()

### Community 65 - "Classes de paysage"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 66 - "overlaps.py"
Cohesion: 0.17
Nodes (5): length_m(), polygon_parts(), _as_multipolygon(), _closer_parts(), distance_layer()

### Community 68 - "core/sampling.py"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 69 - "Chemins du cache"
Cohesion: 0.24
Nodes (5): cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_root_env_override()

### Community 70 - "Protocole et découverte"
Cohesion: 0.20
Nodes (9): Protocole du pont v1 (JSON-lines + jeton), Découverte via connection.json (CYNOGIS_CONNECTION_FILE), Configuration partagee (web_services.json, palettes.json), Architecture and operation, Cynogis project report (RAPORT.md), ~/.cynogis user directory, Long job flow (AlgCall, Fetch, Pause, Pacer), Simple call flow (READ tool) (+1 more)

### Community 71 - "Protocole et découverte (2)"
Cohesion: 0.20
Nodes (6): Cynogis (pilotage QGIS par IA via MCP), Serveur MCP générique (relais list_tools / call_tool), Débogage : recharger le plugin, bouton Serveur GeoMCP, Pont TCP local (plugin QGIS <-> serveur MCP), Cache du catalogue d'outils (tools_cache.json), 1.2 Interdire les surfaces en EPSG:4326

### Community 72 - "Règles réglementaires"
Cohesion: 0.27
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 73 - "tasks.py (5)"
Cohesion: 0.27
Nodes (6): AlgCall, Pause, run_now(), test_run_now(), algo(), steps()

### Community 74 - "Cache des zonages (2)"
Cohesion: 0.20
Nodes (6): assess(), for_territory(), zoning_state(), regulatory_prescan(), test_par_territoire(), test_pre_diagnostic()

### Community 75 - "Contrôle de code PyQGIS"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 76 - "Security model (six guardrails)"
Cohesion: 0.22
Nodes (7): Liste blanche ALGORITHMS (run_algorithm), Fetch : téléchargement HTTP dans une QgsTask, Annulation du job (suppression couche / fermeture projet), Jobs non bloquants (yield from, QgsTask), Pacer (rend la main à QGIS toutes les 100 ms), Journal d'audit ~/.cynogis/audit, execute_pyqgis (dernier recours)

### Community 77 - "Opérations sur couleurs (2)"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 78 - "Rapport des fonctionnalités"
Cohesion: 0.25
Nodes (9): Ecological impact study workflow (ERC), Ecology referentials (TAXREF, BDC Statuts, HABREF, zonings), Ecology, proximity, stakes and impacts tools, Internal tools (list_tools, get_job_status, cancel_job), Landscape diagnosis workflow, Closed landscape nomenclature, Coefficients, landscape, terrain tools, Tool catalog (101 + 4 internal) (+1 more)

### Community 79 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.29
Nodes (6): Fin de tâche : graphify update, Conventions (Ruff, QgsTask, une branche par fonctionnalité), 3.2/3.3 Donnees sensibles et filtrage RGPD, 3.4 Audit des garde-fous, Phase 0 : Outillage du developpement, Phase 3 : Tracabilite et confidentialite

### Community 80 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.25
Nodes (8): 1.1 Tests de surfaces de reference (2975 / 4471), 1.3 Methode plane ou ellipsoidale documentee, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, 3.1 Encart de tracabilite automatique, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 81 - "Serveur MCP stdio (2)"
Cohesion: 0.39
Nodes (6): BridgeResult, FakeClient, test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 82 - "require_field"
Cohesion: 0.29
Nodes (3): is_agricultural(), _overlay(), test_is_agricultural()

### Community 83 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 85 - "Dérivés de terrain (2)"
Cohesion: 0.40
Nodes (3): altitude_band(), parse_bands(), test_tranches_altitude()

### Community 86 - "styling.py (3)"
Cohesion: 0.50
Nodes (3): test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

## Knowledge Gaps
- **29 isolated node(s):** `cynogis-server`, `Audit log (get_audit_log)`, `Restricted network (webservices catalogue)`, `Journal d'audit ~/.cynogis/audit`, `execute_pyqgis (dernier recours)` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 711 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `common.py`, `editing.py`, `Services web OGC`, `run_to_project`, `styling.py`, `tools/project_audit.py`, `tools/proximity.py (2)`, `styling.py (2)`, `tools/proximity.py (2) (2)`, `Tests des jobs`, `Dispatcher`, `fetch_wfs_layer`, `tools/proximity.py (2) (3)`, `tools/proximity.py (2) (4)`, `tasks.py`, `tasks.py (2)`, `find_source_file`, `export.py`, `Exécuteur factice`, `Fichier de connexion`, `_output_path`, `Tests du dispatcher`, `BridgeServer`, `Schéma des paramètres`, `overlaps.py`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 88 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 88 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `Audit log (get_audit_log)`, `Restricted network (webservices catalogue)` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10855810855810856 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `styling.py (2)` to `common.py`, `editing.py`, `Services web OGC`, `run_to_project`, `styling.py`, `tools/project_audit.py`, `ToolError`, `tools/proximity.py (2)`, `tools/proximity.py (2) (2)`, `Tests des jobs`, `Dispatcher`, `fetch_wfs_layer`, `tools/proximity.py (2) (3)`, `tools/proximity.py (2) (4)`, `tasks.py`, `tasks.py (2)`, `find_source_file`, `export.py`, `Exécuteur factice`, `Fichier de connexion`, `_output_path`, `Tests du dispatcher`, `BridgeServer`, `Schéma des paramètres`, `overlaps.py`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Are the 133 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 133 INFERRED edges - model-reasoned connections that need verification._
- **Should `editing.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07027027027027027 - nodes in this community are weakly interconnected._