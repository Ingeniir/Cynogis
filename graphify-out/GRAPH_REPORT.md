# Graph Report - cynogis  (2026-10-28)

## Corpus Check
- 136 files · ~101,200 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2102 nodes · 6384 edges · 103 communities (84 shown, 19 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 526 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `88dc890e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- common.py
- tools/terrain.py
- classify.py
- geometry_kind
- Shapefiles et encodage
- dispatcher.py
- ToolError
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
- plugin.py
- core/landscape.py
- write_table
- tools/project_audit.py
- classify.py
- EditJournal
- test_fields.py
- core/project_audit.py
- get_vector_layer
- TAXREF
- pyqgis.py
- Données de terrain
- Point d'entrée du plugin
- Résolution des chevauchements
- app.py
- AuditLog
- to_float
- geoprocessing.py
- Historique des styles
- FakeExecutor
- collections_abc
- _clipped
- ToolRegistry
- Installation développeur
- tools/landscape.py
- prescan_sections
- tasks.py
- tasks.py (2)
- find_source_file
- Requêtes WFS
- dev_setup.py
- Exécuteur factice
- core/project_audit.py
- palettes.py
- build_plugin.py
- Journal d'audit
- Fichier de connexion
- protocol.py
- audit_project
- Territory
- Construction du ZIP
- Feuille de route
- Adding a tool (@tool decorator, Param, docstring)
- erc_variant_compare
- math
- BridgeServer
- Découpe de transects
- Schéma des paramètres
- LandscapeClass
- classes_for
- core/sampling.py
- core/sampling.py
- Chemins du cache
- Protocole et découverte
- tools/habref.py
- Règles réglementaires
- prepare_expression
- contrast_ratio
- Contrôle de code PyQGIS
- export.py
- run_in_memory
- Rapport des fonctionnalités
- save_to_project
- Phase 1 : Fiabilite des calculs de surface
- Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])
- require_field
- Provenance
- metadata.txt (Cynogis Reunion-Mayotte 0.1.0)
- End of task: graphify update and graphify-out commit
- Python 3.14 venv vs QGIS Python 3.12
- Qt5/Qt6 compatibility via compat.py (QGIS 3.x and 4.x)
- export.py (2)
- core/ pure-logic modules catalogue
- Compatibilité Qt
- plugin.py
- _overlay
- re
- format_number
- Source
- units.py
- _geometry_repr
- _read

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 201 edges
2. `ErrorCode` - 183 edges
3. `tool()` - 154 edges
4. `ToolResult` - 106 edges
5. `get_vector_layer()` - 100 edges
6. `feature_request()` - 67 edges
7. `geometry_kind()` - 60 edges
8. `require_field()` - 56 edges
9. `to_json_value()` - 52 edges
10. `distance_area()` - 51 edges

## Surprising Connections (you probably didn't know these)
- `3.4 Audit des garde-fous` --semantically_similar_to--> `Security rules (no bypass, no overwrite, no sensitive species/cadastral data)`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
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

## Communities (103 total, 19 thin omitted)

### Community 0 - "common.py"
Cohesion: 0.05
Nodes (49): Fetch, is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs() (+41 more)

### Community 1 - "tools/terrain.py"
Cohesion: 0.12
Nodes (14): get_raster_layer(), classify_slope(), _clean(), derive_terrain(), elevation_sample(), _flow_accumulation(), list_slope_classes(), _metric_raster() (+6 more)

### Community 2 - "classify.py"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 3 - "geometry_kind"
Cohesion: 0.07
Nodes (33): Pacer, compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of() (+25 more)

### Community 4 - "Shapefiles et encodage"
Cohesion: 0.05
Nodes (15): AlgCall, Executor, Job, JobManager, Pause, run_now(), _FetchTask, _Handle (+7 more)

### Community 5 - "dispatcher.py"
Cohesion: 0.13
Nodes (5): render_notes(), PermissionPolicy, Level, polygon_parts(), _r4()

### Community 6 - "ToolError"
Cohesion: 0.05
Nodes (51): ToolResult, ErrorCode, ToolError, tool(), _allowed(), run_algorithm(), export_atlas_pdf(), _from_template() (+43 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 8 - "Serveur MCP stdio"
Cohesion: 0.10
Nodes (21): to_float(), convert_length(), feature_request(), iter_geometries(), _collect(), count_observations(), count_points_in_polygon(), _distance_m() (+13 more)

### Community 9 - "test_jobs.py"
Cohesion: 0.12
Nodes (24): app(), boucle(), calcul(), effacer(), lecture(), make(), _req(), sans_etape() (+16 more)

### Community 10 - "metrics.py"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 11 - "Coefficients (cœur)"
Cohesion: 0.15
Nodes (16): _covers(), map_cirad(), map_feature(), map_ocsge(), _segments(), test_cirad_974_2020_ombre_et_code_inconnu(), test_cirad_974_2020_par_code(), test_cirad_974_millesimes_meme_nomenclature() (+8 more)

### Community 12 - "Dispatcher"
Cohesion: 0.14
Nodes (4): Response, Dispatcher, finish(), collecting()

### Community 13 - "HABREF"
Cohesion: 0.09
Nodes (26): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), list_categories() (+18 more)

### Community 14 - "core/stakes.py"
Cohesion: 0.09
Nodes (22): compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number(), Override (+14 more)

### Community 15 - "Tests des jobs"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 16 - "Référentiels OCS (cœur)"
Cohesion: 0.12
Nodes (17): clean_number(), crs_info(), enum_name(), file_format(), layer_kind(), overlap_warning(), source_path(), territory_info() (+9 more)

### Community 17 - "plugin.py"
Cohesion: 0.14
Nodes (8): new_token(), remove_connection_file(), write_connection_file(), QgsLogHandler, setup_logging(), teardown_logging(), Cynogis Plugin Icon (icon.svg), Green Map Location Pin

### Community 18 - "core/landscape.py"
Cohesion: 0.13
Nodes (7): spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 19 - "write_table"
Cohesion: 0.24
Nodes (5): _output_path(), write_document(), write_pdf(), write_table(), regulatory_prescan()

### Community 20 - "tools/project_audit.py"
Cohesion: 0.14
Nodes (7): _error_kind(), geometry_report(), _layer_facts(), _raster_facts(), _vector_facts(), _scan_sidecars(), _text_sample()

### Community 21 - "classify.py"
Cohesion: 0.10
Nodes (17): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), _as_multipolygon(), _closer_parts(), records() (+9 more)

### Community 22 - "EditJournal"
Cohesion: 0.10
Nodes (24): build_categories(), describe_options(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques() (+16 more)

### Community 23 - "test_fields.py"
Cohesion: 0.05
Nodes (35): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), truncate_field_names(), companion_paths() (+27 more)

### Community 24 - "core/project_audit.py"
Cohesion: 0.16
Nodes (22): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+14 more)

### Community 25 - "get_vector_layer"
Cohesion: 0.07
Nodes (39): describe_summary(), begin_edit(), field_type_name(), geometry_from_wkt(), get_vector_layer(), is_shapefile(), layer_field_types(), refresh_layer() (+31 more)

### Community 26 - "TAXREF"
Cohesion: 0.10
Nodes (11): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+3 more)

### Community 28 - "Données de terrain"
Cohesion: 0.10
Nodes (17): darken(), distinct_colors(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), validate_colors() (+9 more)

### Community 29 - "Point d'entrée du plugin"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 30 - "Résolution des chevauchements"
Cohesion: 0.17
Nodes (6): make_field(), _isopleth_geometries(), _isopleths(), kernel_density_points(), _save_isopleths(), _style()

### Community 31 - "app.py"
Cohesion: 0.08
Nodes (19): main(), call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job() (+11 more)

### Community 32 - "AuditLog"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 33 - "to_float"
Cohesion: 0.13
Nodes (10): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), list_algorithms(), test_liste_blanche(), test_recherche_multi_termes() (+2 more)

### Community 34 - "geoprocessing.py"
Cohesion: 0.22
Nodes (9): buffer(), dissolve(), extract(), fix_geometries(), _name(), overlay(), reproject_layer(), spatial_join() (+1 more)

### Community 35 - "Historique des styles"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 36 - "FakeExecutor"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 37 - "collections_abc"
Cohesion: 0.11
Nodes (6): clean_name(), to_ascii(), Rule, test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

### Community 38 - "_clipped"
Cohesion: 0.15
Nodes (7): find_source_file(), referentials_directory(), _clipped(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 39 - "ToolRegistry"
Cohesion: 0.12
Nodes (12): apply_mapping(), ndvi_deviation(), ndvi_range(), score_match(), suggest_mapping(), test_apply_mapping_insensible_aux_accents(), test_merge_nomenclature_refuse(), test_ndvi_controle() (+4 more)

### Community 40 - "Installation développeur"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 41 - "tools/landscape.py"
Cohesion: 0.16
Nodes (5): get_class(), add_to_memory(), classify_landscape(), compute_ndvi(), extract_ravines()

### Community 42 - "prescan_sections"
Cohesion: 0.29
Nodes (5): age_days(), describe_sources(), freshness(), prescan_sections(), test_age_never_negative_and_tolerates_garbage()

### Community 43 - "tasks.py"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "tasks.py (2)"
Cohesion: 0.17
Nodes (9): _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), _local_source(), regulatory_zoning_intersect(), Source, _sources() (+1 more)

### Community 45 - "find_source_file"
Cohesion: 0.13
Nodes (14): normalize(), _columns(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+6 more)

### Community 46 - "Requêtes WFS"
Cohesion: 0.13
Nodes (3): BridgeServer, classFactory(), CynogisPlugin

### Community 47 - "dev_setup.py"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 48 - "Exécuteur factice"
Cohesion: 0.20
Nodes (9): _check(), object_schema(), Param, _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_items_enum() (+1 more)

### Community 49 - "core/project_audit.py"
Cohesion: 0.17
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 50 - "palettes.py"
Cohesion: 0.09
Nodes (17): interpolate_ramp(), all_palettes(), describe_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors() (+9 more)

### Community 51 - "build_plugin.py"
Cohesion: 0.23
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 52 - "Journal d'audit"
Cohesion: 0.12
Nodes (10): getfeature_url(), status(), test_describe_multiple_sources_and_missing(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_prescan_sections_lists_sources_with_origin(), test_read_cache_meta_rejects_bad_files() (+2 more)

### Community 53 - "Fichier de connexion"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 54 - "protocol.py"
Cohesion: 0.21
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 55 - "audit_project"
Cohesion: 0.16
Nodes (5): render_map(), audit_project(), _open_project(), _overview_map(), _project_facts()

### Community 57 - "Construction du ZIP"
Cohesion: 0.14
Nodes (11): assess(), cache_matches(), cache_meta(), for_territory(), _inpn(), service_label(), Zoning, zoning_state() (+3 more)

### Community 58 - "Feuille de route"
Cohesion: 0.30
Nodes (12): crash(), double(), make(), metier(), _req(), supprimer(), test_destroy_with_confirmation(), test_errors() (+4 more)

### Community 59 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.22
Nodes (8): Adding a tool (@tool decorator, Param, docstring), core/jobs.py::note warnings from shared helpers, Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471, Tool code conventions (no Python defaults, layer_id, ToolError enum), Shared helpers table (tools/common.py, tools/outputs.py), Add-a-tool example (README)

### Community 60 - "erc_variant_compare"
Cohesion: 0.27
Nodes (6): build_table(), _check_layers(), _distances(), erc_variant_compare(), impact_quantification(), _intersect()

### Community 61 - "math"
Cohesion: 0.08
Nodes (30): correlate(), correlation_pairs(), correlation_pvalue(), describe(), describe_categorical(), describe_full(), describe_groups(), interpret_shape() (+22 more)

### Community 62 - "BridgeServer"
Cohesion: 0.16
Nodes (8): bbox_covers(), cache_paths(), cache_root(), read_cache_meta(), should_replace_cache(), _write_cache(), test_bbox_rules(), test_cache_root_env_override()

### Community 63 - "Découpe de transects"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 64 - "Schéma des paramètres"
Cohesion: 0.17
Nodes (12): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.3 Methode plane ou ellipsoidale documentee, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD (+4 more)

### Community 65 - "LandscapeClass"
Cohesion: 0.25
Nodes (4): LandscapeClass, merge_nomenclature(), register(), test_merge_nomenclature_valide()

### Community 66 - "classes_for"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 67 - "core/sampling.py"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 68 - "core/sampling.py"
Cohesion: 0.20
Nodes (5): _cut(), _Sampler, _segment(), _systematic(), transect_sampling_plan()

### Community 69 - "Chemins du cache"
Cohesion: 0.15
Nodes (14): ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache, scripts/build_plugin.py --bump (private QGIS repo), CYNOGIS_REFERENTIALS_DIR shared referentials, Cynogis workstation installation guide, MCP client setup (Claude Code, Claude Desktop, Codex), \\SERVEUR\Cynogis network share (plugins, serveur, referentials) (+6 more)

### Community 70 - "Protocole et découverte"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 71 - "tools/habref.py"
Cohesion: 0.11
Nodes (14): unique_field_name(), find_file(), detect_territory(), _overview_extent(), extent_wgs84(), rect_to_list(), _write_csv(), import_field_data() (+6 more)

### Community 72 - "Règles réglementaires"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 73 - "prepare_expression"
Cohesion: 0.20
Nodes (4): expression_context(), prepare_expression(), export_table(), descriptive_stats()

### Community 74 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 75 - "Contrôle de code PyQGIS"
Cohesion: 0.14
Nodes (16): run_algorithm whitelist (core/algorithms.py ALGORITHMS), Edit buffer + core/edits.py JOURNAL, Ecology, proximity, stakes and impacts tools (TAXREF, HABREF, ERC), Editing tools (add_features, update_geometry, request_commit, rollback_edits), execute_pyqgis last-resort DESTROY tool + codecheck, Known limits (in-memory JOURNAL, single job, stale surface fields), Closed landscape nomenclature (5 main classes, territory-specific), Coefficients, landscape and terrain tools (+8 more)

### Community 76 - "export.py"
Cohesion: 0.12
Nodes (5): unique_path(), mentions_natura2000(), _project_target(), _save_project_details(), output_dir()

### Community 77 - "run_in_memory"
Cohesion: 0.28
Nodes (4): describe_algorithm(), is_optional(), _run(), run_in_memory()

### Community 78 - "Rapport des fonctionnalités"
Cohesion: 0.33
Nodes (5): Bridge protocol v1 (JSON-lines + token), Job response and polling (get_job_status / cancel_job), Internal tools (list_tools, get_audit_log, get_job_status, cancel_job), Long job flow (AlgCall, Fetch, Pause, JobManager, ProcessingExecutor), Simple READ call flow (token, decode, schema, policy, audit)

### Community 80 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.50
Nodes (3): Dev commands (pytest, ruff, ping_qgis, inspector, dev_setup), Testing scope: core/ unit tests, tools/ only tested in QGIS, Development installation (venv, plugin link, MCP client config)

### Community 81 - "Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])"
Cohesion: 0.67
Nodes (3): Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN]), Toolbar button naming: Serveur Cynogis vs Serveur GeoMCP, Troubleshooting table (QGIS_UNAVAILABLE, BUSY, encoding...)

### Community 83 - "Provenance"
Cohesion: 0.36
Nodes (3): Provenance, provenance_from_data(), test_provenance_roundtrip_and_kind_check()

### Community 96 - "_overlay"
Cohesion: 0.29
Nodes (3): is_agricultural(), _overlay(), test_is_agricultural()

### Community 98 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 99 - "Source"
Cohesion: 0.33
Nodes (3): Source, sources_for(), test_sources_for_territoire()

### Community 100 - "units.py"
Cohesion: 0.47
Nodes (3): convert_area(), test_conversions(), test_unknown_unit()

## Ambiguous Edges - Review These
- `Tool code conventions (no Python defaults, layer_id, ToolError enum)` → `Add-a-tool example (README)`  [AMBIGUOUS]
  README.md · relation: conceptually_related_to
- `Toolbar button naming: Serveur Cynogis vs Serveur GeoMCP` → `Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])`  [AMBIGUOUS]
  INSTALLATION.md · relation: conceptually_related_to

## Knowledge Gaps
- **36 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Phase 0 : Outillage du developpement`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)`, `Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats)` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 726 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `common.py`, `tools/terrain.py`, `geometry_kind`, `Shapefiles et encodage`, `dispatcher.py`, `Serveur MCP stdio`, `test_jobs.py`, `Dispatcher`, `core/stakes.py`, `Référentiels OCS (cœur)`, `core/landscape.py`, `write_table`, `tools/project_audit.py`, `get_vector_layer`, `pyqgis.py`, `Résolution des chevauchements`, `geoprocessing.py`, `FakeExecutor`, `_clipped`, `tools/landscape.py`, `tasks.py (2)`, `Requêtes WFS`, `Exécuteur factice`, `protocol.py`, `audit_project`, `Feuille de route`, `erc_variant_compare`, `core/sampling.py`, `tools/habref.py`, `prepare_expression`, `export.py`, `save_to_project`, `_read`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 94 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Phase 0 : Outillage du developpement` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05198358413132695 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `common.py`, `tools/terrain.py`, `geometry_kind`, `Shapefiles et encodage`, `dispatcher.py`, `Serveur MCP stdio`, `test_jobs.py`, `Dispatcher`, `core/stakes.py`, `Référentiels OCS (cœur)`, `write_table`, `tools/project_audit.py`, `get_vector_layer`, `pyqgis.py`, `Résolution des chevauchements`, `geoprocessing.py`, `FakeExecutor`, `_clipped`, `tools/landscape.py`, `tasks.py (2)`, `Requêtes WFS`, `Exécuteur factice`, `protocol.py`, `audit_project`, `Feuille de route`, `erc_variant_compare`, `core/sampling.py`, `tools/habref.py`, `prepare_expression`, `export.py`, `save_to_project`, `_read`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Tool code conventions (no Python defaults, layer_id, ToolError enum)` and `Add-a-tool example (README)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Toolbar button naming: Serveur Cynogis vs Serveur GeoMCP` and `Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._