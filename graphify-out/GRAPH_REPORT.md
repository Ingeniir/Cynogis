# Graph Report - cynogis  (2026-10-27)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 2059 nodes · 6081 edges · 96 communities (80 shown, 16 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 473 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1e9204e1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- common.py
- editing.py
- Services web OGC
- measures.py
- Shapefiles et encodage
- common.py
- tool
- Métriques paysagères
- Serveur MCP stdio
- test_jobs.py
- metrics.py
- Coefficients (cœur)
- Dispatcher
- HABREF
- core/stakes.py
- Tests des jobs
- Référentiels OCS (cœur)
- Dispatcher
- core/landscape.py
- Impacts et enjeux
- report.py (2)
- classify.py
- EditJournal
- Dérivés de terrain
- tools/atlas.py
- Styles (cœur)
- TAXREF
- editing.py
- Données de terrain
- Point d'entrée du plugin
- Résolution des chevauchements
- numpy
- Liste blanche d'algorithmes
- to_float
- numpy (2)
- Historique des styles
- calculate_field
- fetch_wfs_layer
- tools/proximity.py (2) (3)
- ToolRegistry
- Installation développeur
- collections_abc
- Provenance
- tasks.py
- tasks.py (2)
- find_source_file
- Requêtes WFS
- dev_setup.py
- Exécuteur factice
- core/project_audit.py
- describe
- build_plugin.py
- Journal d'audit
- Fichier de connexion
- protocol.py
- landscape_metrics
- territory.py
- Construction du ZIP
- Feuille de route
- Guide d'installation
- core/zoning.py
- Tests du dispatcher
- BridgeServer
- Découpe de transects
- Schéma des paramètres
- core/landscape.py
- classes_for
- core/sampling.py
- core/sampling.py
- Chemins du cache
- Protocole et découverte
- open_table
- Règles réglementaires
- tasks.py (5)
- contrast_ratio
- Contrôle de code PyQGIS
- list_style_options
- Rapport des fonctionnalités
- Phase 3 : Tracabilite et confidentialite
- Phase 1 : Fiabilite des calculs de surface
- Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])
- require_field
- format_number
- metadata.txt (Cynogis Reunion-Mayotte 0.1.0)
- End of task: graphify update and graphify-out commit
- Python 3.14 venv vs QGIS Python 3.12
- Qt5/Qt6 compatibility via compat.py (QGIS 3.x and 4.x)
- export.py (2)
- core/ pure-logic modules catalogue
- Compatibilité Qt
- plugin.py

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 182 edges
2. `ErrorCode` - 164 edges
3. `tool()` - 141 edges
4. `get_vector_layer()` - 95 edges
5. `ToolResult` - 94 edges
6. `feature_request()` - 62 edges
7. `geometry_kind()` - 58 edges
8. `require_field()` - 53 edges
9. `distance_area()` - 49 edges
10. `to_json_value()` - 47 edges

## Surprising Connections (you probably didn't know these)
- `3.4 Audit des garde-fous` --semantically_similar_to--> `Security rules (no bypass, no overwrite, no sensitive species/cadastral data)`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `test_describe_empty_and_single()` --calls--> `describe()`  [INFERRED]
  tests/unit/test_stats.py → plugin/cynogis/core/stats.py
- `2.3 Exclure Natura 2000` --semantically_similar_to--> `Natura 2000 not applicable in overseas departments`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `2.6 Pre-diagnostic 100 % deterministe` --semantically_similar_to--> `Deterministic pre-diagnostic, never LLM-written`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Non-negotiable regulatory business rules** — claude_territory_crs, claude_area_measurement_rule, claude_surface_3d_rule, claude_natura2000_exclusion, claude_regulatory_thresholds_config, claude_deterministic_prediagnostic [EXTRACTED 1.00]
- **Regles metier codifiees par la phase 2** — claude_natura2000_exclusion, claude_deterministic_prediagnostic, docs_roadmap_phase2_reglementaire [INFERRED 0.85]
- **Long-running job execution model** — claude_job_response, claude_qgstask_background_jobs, raport_long_job_flow, raport_internal_tools [INFERRED 0.85]
- **Cynogis safety guardrails** — claude_permission_levels, claude_algorithm_whitelist, claude_edit_buffer_journal, claude_run_to_project, raport_execute_pyqgis, raport_restricted_network [INFERRED 0.85]
- **Fiabilite des surfaces (regles, roadmap 1.1-1.3, helpers)** — docs_roadmap_1_1_reference_tests, docs_roadmap_1_2_forbid_4326, docs_roadmap_1_3_surface_method, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.95]

## Communities (96 total, 16 thin omitted)

### Community 0 - "common.py"
Cohesion: 0.07
Nodes (42): is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+34 more)

### Community 1 - "editing.py"
Cohesion: 0.06
Nodes (33): ErrorCode, ToolError, _allowed(), run_algorithm(), get_raster_layer(), import_field_data(), _read(), buffer() (+25 more)

### Community 2 - "Services web OGC"
Cohesion: 0.06
Nodes (41): clean_values(), compute_breaks(), _dedupe(), equal_interval(), format_number(), natural_breaks(), pretty_breaks(), quantile_breaks() (+33 more)

### Community 3 - "measures.py"
Cohesion: 0.08
Nodes (30): Pacer, convert_area(), convert_length(), compute_coefficients(), area_m2(), area_method(), dissolved_areas(), distance_area() (+22 more)

### Community 4 - "Shapefiles et encodage"
Cohesion: 0.05
Nodes (15): AlgCall, Executor, Fetch, Job, JobManager, Pause, _FetchTask, _Handle (+7 more)

### Community 5 - "common.py"
Cohesion: 0.14
Nodes (8): Level, Param, describe_algorithm(), add_to_memory(), geometry_kind(), to_json_value(), is_optional(), get_layer_style()

### Community 6 - "tool"
Cohesion: 0.07
Nodes (30): ToolResult, tool(), decorator(), list_coefficients(), feature_request(), get_vector_layer(), overlap_warning(), require_field() (+22 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.07
Nodes (42): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+34 more)

### Community 8 - "Serveur MCP stdio"
Cohesion: 0.07
Nodes (24): unique_field_name(), fractal_dimension(), describe(), describe_groups(), _r(), to_float(), _collect(), count_observations() (+16 more)

### Community 9 - "test_jobs.py"
Cohesion: 0.08
Nodes (29): note(), app(), boucle(), calcul(), effacer(), erreur_avant(), FakeExecutor, job_invalide() (+21 more)

### Community 10 - "metrics.py"
Cohesion: 0.07
Nodes (30): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), largest_patch_index(), mean_patch_size(), patch_density() (+22 more)

### Community 11 - "Coefficients (cœur)"
Cohesion: 0.07
Nodes (27): _covers(), find_source_file(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), referentials_directory(), _segments() (+19 more)

### Community 12 - "Dispatcher"
Cohesion: 0.09
Nodes (7): Response, BridgeServer, Dispatcher, finish(), collecting(), render_notes(), test_response_encode_job_id()

### Community 13 - "HABREF"
Cohesion: 0.10
Nodes (25): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), list_categories() (+17 more)

### Community 14 - "core/stakes.py"
Cohesion: 0.08
Nodes (22): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+14 more)

### Community 15 - "Tests des jobs"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 16 - "Référentiels OCS (cœur)"
Cohesion: 0.11
Nodes (17): clean_number(), crs_info(), enum_name(), extent_wgs84(), rect_to_list(), territory_info(), _geometry_repr(), get_layer_info() (+9 more)

### Community 17 - "Dispatcher"
Cohesion: 0.11
Nodes (11): QgsLogHandler, setup_logging(), teardown_logging(), call_tool(), _fetch_specs(), list_tools(), _progress_token(), run() (+3 more)

### Community 18 - "core/landscape.py"
Cohesion: 0.11
Nodes (7): PermissionPolicy, spec_of(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 19 - "Impacts et enjeux"
Cohesion: 0.11
Nodes (11): export_map_image(), export_table(), _output_path(), _project_target(), render_map(), save_project(), _save_project_details(), _write_csv() (+3 more)

### Community 20 - "report.py (2)"
Cohesion: 0.11
Nodes (13): run_now(), file_format(), layer_kind(), source_path(), _error_kind(), geometry_report(), audit_project(), _layer_facts() (+5 more)

### Community 21 - "classify.py"
Cohesion: 0.10
Nodes (17): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), _as_multipolygon(), _closer_parts(), records() (+9 more)

### Community 22 - "EditJournal"
Cohesion: 0.11
Nodes (22): build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees() (+14 more)

### Community 23 - "Dérivés de terrain"
Cohesion: 0.11
Nodes (16): truncate_field_names(), companion_paths(), export_plan(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), test_truncate_field_names_sans_doublon() (+8 more)

### Community 24 - "tools/atlas.py"
Cohesion: 0.11
Nodes (15): clean_name(), unique_path(), _build(), export_atlas_pdf(), _from_template(), _label(), _north_arrow(), _overview_extent() (+7 more)

### Community 25 - "Styles (cœur)"
Cohesion: 0.14
Nodes (15): select_ids(), _change_geometries(), _check_count(), _conform(), delete_features(), _delete_features_details(), _geometries(), _measure() (+7 more)

### Community 26 - "TAXREF"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 27 - "editing.py"
Cohesion: 0.12
Nodes (15): describe_summary(), is_shapefile(), add_field(), _commit_details(), _delete_field_details(), _editing_layers(), _field_limit(), get_pending_edits() (+7 more)

### Community 28 - "Données de terrain"
Cohesion: 0.12
Nodes (15): darken(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), test_interpolate_ramp_extremites_conservees() (+7 more)

### Community 29 - "Point d'entrée du plugin"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 30 - "Résolution des chevauchements"
Cohesion: 0.12
Nodes (9): expression_context(), prepare_expression(), _isopleth_geometries(), _isopleths(), kernel_density_points(), _save_isopleths(), _style(), _run() (+1 more)

### Community 31 - "numpy"
Cohesion: 0.13
Nodes (12): main(), BridgeError, BridgeResult, QgisBridgeClient, FakeClient, test_client_reponse_illisible(), scenario(), handle() (+4 more)

### Community 32 - "Liste blanche d'algorithmes"
Cohesion: 0.16
Nodes (8): new_token(), remove_connection_file(), write_connection_file(), AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 33 - "to_float"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 34 - "numpy (2)"
Cohesion: 0.13
Nodes (16): coerce_record(), coerce_value(), _parse_date(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict(), test_coerce_value(), test_coerce_value_date_invalide() (+8 more)

### Community 35 - "Historique des styles"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 36 - "calculate_field"
Cohesion: 0.13
Nodes (10): begin_edit(), field_type_name(), geometry_from_wkt(), layer_field_types(), refresh_layer(), wkt_to_layer_crs(), add_features(), calculate_field() (+2 more)

### Community 37 - "fetch_wfs_layer"
Cohesion: 0.13
Nodes (4): FieldType, resolve_type(), to_ascii(), Rule

### Community 38 - "tools/proximity.py (2) (3)"
Cohesion: 0.15
Nodes (9): looks_like_mojibake(), detect_territory(), crs_from_text(), check_shapefile(), load_layer(), _mojibake_hint(), _scan_sidecars(), set_layer_encoding() (+1 more)

### Community 39 - "ToolRegistry"
Cohesion: 0.13
Nodes (11): get_class(), LandscapeClass, merge_nomenclature(), score_match(), suggest_mapping(), test_merge_nomenclature_refuse(), test_merge_nomenclature_valide(), test_score_match_exact_et_mot_cle() (+3 more)

### Community 40 - "Installation développeur"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 41 - "collections_abc"
Cohesion: 0.13
Nodes (9): distinct_colors(), validate_colors(), with_alpha(), landscape_palette(), resolve_colors(), test_distinct_colors_sans_doublon(), test_validate_colors_message_indexe(), test_resolve_colors_priorite_aux_couleurs() (+1 more)

### Community 42 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 43 - "tasks.py"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "tasks.py (2)"
Cohesion: 0.16
Nodes (8): service_label(), _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 45 - "find_source_file"
Cohesion: 0.18
Nodes (11): _columns(), match_taxa(), name_key(), read_statuses(), Statuses, Taxon, listed(), _values() (+3 more)

### Community 47 - "dev_setup.py"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 48 - "Exécuteur factice"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 49 - "core/project_audit.py"
Cohesion: 0.16
Nodes (6): check_dissolved(), check_geographic_rejected(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 50 - "describe"
Cohesion: 0.12
Nodes (10): all_palettes(), get_palette(), load_user_palettes(), register_palette(), validate_palette(), save_palette(), test_get_palette_etiree(), test_get_palette_inconnue() (+2 more)

### Community 51 - "build_plugin.py"
Cohesion: 0.22
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 52 - "Journal d'audit"
Cohesion: 0.16
Nodes (6): getfeature_url(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 53 - "Fichier de connexion"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 54 - "protocol.py"
Cohesion: 0.21
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 55 - "landscape_metrics"
Cohesion: 0.20
Nodes (7): interpret_metrics(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of()

### Community 56 - "territory.py"
Cohesion: 0.19
Nodes (6): mentions_natura2000(), Territory, test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 57 - "Construction du ZIP"
Cohesion: 0.16
Nodes (8): assess(), cache_matches(), for_territory(), _inpn(), Zoning, regulatory_prescan(), test_par_territoire(), test_pre_diagnostic()

### Community 58 - "Feuille de route"
Cohesion: 0.30
Nodes (12): crash(), double(), make(), metier(), _req(), supprimer(), test_destroy_with_confirmation(), test_errors() (+4 more)

### Community 59 - "Guide d'installation"
Cohesion: 0.18
Nodes (12): Adding a tool (@tool decorator, Param, docstring), run_algorithm whitelist (core/algorithms.py ALGORITHMS), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Permission levels READ / CREATE / MODIFY / DESTROY, Tool code conventions (no Python defaults, layer_id, ToolError enum), Editing tools (add_features, update_geometry, request_commit, rollback_edits), execute_pyqgis last-resort DESTROY tool + codecheck (+4 more)

### Community 60 - "core/zoning.py"
Cohesion: 0.18
Nodes (6): bbox_covers(), should_replace_cache(), status(), zoning_state(), test_bbox_rules(), test_statut()

### Community 61 - "Tests du dispatcher"
Cohesion: 0.18
Nodes (8): elongation(), test_elongation(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float(), test_conversions(), test_unknown_unit()

### Community 62 - "BridgeServer"
Cohesion: 0.21
Nodes (7): cache_meta(), cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_meta_roundtrip_and_matching(), test_cache_root_env_override()

### Community 63 - "Découpe de transects"
Cohesion: 0.18
Nodes (6): Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471, 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 64 - "Schéma des paramètres"
Cohesion: 0.17
Nodes (12): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.3 Methode plane ou ellipsoidale documentee, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD (+4 more)

### Community 65 - "core/landscape.py"
Cohesion: 0.20
Nodes (6): apply_mapping(), ndvi_deviation(), ndvi_range(), register(), test_apply_mapping_insensible_aux_accents(), test_ndvi_controle()

### Community 66 - "classes_for"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 67 - "core/sampling.py"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 68 - "core/sampling.py"
Cohesion: 0.25
Nodes (3): _Sampler, _segment(), _systematic()

### Community 69 - "Chemins du cache"
Cohesion: 0.22
Nodes (10): Cynogis (CLAUDE.md working rules), scripts/build_plugin.py --bump (private QGIS repo), Cynogis workstation installation guide, MCP client setup (Claude Code, Claude Desktop, Codex), \\SERVEUR\Cynogis network share (plugins, serveur, referentials), Private QGIS plugin repository (plugins.xml), cynogis-server.exe installed via uv tool install, Cynogis project report (RAPORT.md) (+2 more)

### Community 70 - "Protocole et découverte"
Cohesion: 0.31
Nodes (5): Box, layout_boxes(), page_size(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 71 - "open_table"
Cohesion: 0.22
Nodes (4): find_file(), open_table(), _sibling(), test_open_table_zip()

### Community 72 - "Règles réglementaires"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 73 - "tasks.py (5)"
Cohesion: 0.25
Nodes (6): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, ~/.cynogis/tools_cache.json catalogue cache, CYNOGIS_REFERENTIALS_DIR shared referentials, ~/.cynogis/ user directory contents, Simple READ call flow (token, decode, schema, policy, audit)

### Community 74 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 75 - "Contrôle de code PyQGIS"
Cohesion: 0.22
Nodes (9): Ecology, proximity, stakes and impacts tools (TAXREF, HABREF, ERC), Closed landscape nomenclature (5 main classes, territory-specific), Coefficients, landscape and terrain tools, Restricted network: only catalogue web services via Fetch, Style tools (categorized, graduated, undo_style, palettes), Tool catalogue (101 + 4 internal tools), Typical AI tool chains (landscape diagnosis, ecological impact study, editing, slope, overlaps), Web services tools (WMS/WFS) (+1 more)

### Community 77 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 78 - "Rapport des fonctionnalités"
Cohesion: 0.40
Nodes (5): Job response and polling (get_job_status / cancel_job), run_to_project / save_to_project output pipeline, Internal tools (list_tools, get_audit_log, get_job_status, cancel_job), Long job flow (AlgCall, Fetch, Pause, JobManager, ProcessingExecutor), Shared helpers table (tools/common.py, tools/outputs.py)

### Community 79 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.47
Nodes (3): add_to_group(), add_to_project(), _output_item()

### Community 80 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.50
Nodes (3): Dev commands (pytest, ruff, ping_qgis, inspector, dev_setup), Testing scope: core/ unit tests, tools/ only tested in QGIS, Development installation (venv, plugin link, MCP client config)

### Community 81 - "Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])"
Cohesion: 0.67
Nodes (3): Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN]), Toolbar button naming: Serveur Cynogis vs Serveur GeoMCP, Troubleshooting table (QGIS_UNAVAILABLE, BUSY, encoding...)

## Ambiguous Edges - Review These
- `Tool code conventions (no Python defaults, layer_id, ToolError enum)` → `Add-a-tool example (README)`  [AMBIGUOUS]
  README.md · relation: conceptually_related_to
- `Toolbar button naming: Serveur Cynogis vs Serveur GeoMCP` → `Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])`  [AMBIGUOUS]
  INSTALLATION.md · relation: conceptually_related_to

## Knowledge Gaps
- **36 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)`, `Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats)`, `Phase 0 : Outillage du developpement` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 716 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `editing.py` to `Services web OGC`, `measures.py`, `Shapefiles et encodage`, `common.py`, `tool`, `Serveur MCP stdio`, `test_jobs.py`, `Coefficients (cœur)`, `Dispatcher`, `Référentiels OCS (cœur)`, `core/landscape.py`, `report.py (2)`, `tools/atlas.py`, `Styles (cœur)`, `editing.py`, `Résolution des chevauchements`, `calculate_field`, `tools/proximity.py (2) (3)`, `tasks.py (2)`, `Exécuteur factice`, `core/project_audit.py`, `describe`, `protocol.py`, `landscape_metrics`, `Feuille de route`, `Phase 3 : Tracabilite et confidentialite`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Are the 87 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 87 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06516105146242132 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `editing.py` to `Services web OGC`, `measures.py`, `Shapefiles et encodage`, `common.py`, `tool`, `Serveur MCP stdio`, `test_jobs.py`, `Coefficients (cœur)`, `Dispatcher`, `Référentiels OCS (cœur)`, `core/landscape.py`, `report.py (2)`, `tools/atlas.py`, `Styles (cœur)`, `editing.py`, `Résolution des chevauchements`, `calculate_field`, `tools/proximity.py (2) (3)`, `tasks.py (2)`, `Exécuteur factice`, `core/project_audit.py`, `describe`, `protocol.py`, `landscape_metrics`, `Feuille de route`, `Phase 3 : Tracabilite et confidentialite`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Tool code conventions (no Python defaults, layer_id, ToolError enum)` and `Add-a-tool example (README)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Toolbar button naming: Serveur Cynogis vs Serveur GeoMCP` and `Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._