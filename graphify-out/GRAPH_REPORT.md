# Graph Report - cynogis  (2026-10-26)

## Corpus Check
- 131 files · ~89,145 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 1933 nodes · 5931 edges · 88 communities (76 shown, 12 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 475 edges (avg confidence: 0.93)
- Token cost: 149,161 input · 0 output

## Community Hubs (Navigation)
- Web Services WFS
- Job Execution Engine
- Tool Errors & Output Save
- Project & Shapefile Audit
- Tool Modules Registry Core
- Landscape Metrics
- Reference Landcover Sources
- Proximity & Observation Tools
- Styling Tools
- Plugin Infrastructure
- Outputs & Export
- Measures & Overlaps
- Landscape Classification
- Coefficients Computation
- Color Utilities
- Layer Info & Common
- Vector Feature Tools
- Stakes & Impact Scoring
- Naming & Algorithm Catalog
- Job Tests
- Report Builder
- Classification Breaks
- TAXREF Taxon Status
- Dispatcher & Bridge Server
- Edit Journal
- Field Type Coercion
- Overlap Resolution
- Slope & Terrain Classes
- Elevation & Isopleths
- Field Data Import
- Distance Matrix Core
- Edit Buffer Tools
- Style History
- Coefficient & Metric Tools
- Data Provenance
- HABREF Habitat Typology
- Plugin Lifecycle
- Symbol Validation
- Attribute Editing
- Geometry Editing
- Bridge Protocol
- Tool Registry & Policy
- MCP Server App
- Referential Rules & Palettes
- WFS Fetch & Cache
- Descriptive Stats
- Atlas & Table Export
- Install & Deployment Docs
- Param Schema Validation
- Zoning Tests
- Dev Setup Script
- Raster Terrain Tools
- Project Audit Core
- Dispatcher Tests
- Atlas Layout
- Project Audit Tests
- Plugin Build Script
- Label Validation
- Bridge Client
- Palette Ramps
- Zoning Assessment
- Feature Add & WKT
- Audit Log
- Sampling Allocation
- Zoning Territory Catalog
- Zoning Cache
- Map Rendering
- User Palettes
- PyQGIS Code Check
- Server Entry & Ping
- Security & Protocol Concepts
- Sampling Plans
- Fake Executor Tests
- Geometry Sampler
- Job Wait Tests
- Architecture Concepts
- Style Options Catalog
- Run Algorithm Tool
- Confirmation Dialog
- French Number Format
- Coefficient Spec
- Territory Model
- Territory Tests
- Test App Fixture
- Server Package

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 195 edges
2. `ErrorCode` - 177 edges
3. `tool()` - 148 edges
4. `ToolResult` - 101 edges
5. `get_vector_layer()` - 96 edges
6. `feature_request()` - 63 edges
7. `geometry_kind()` - 57 edges
8. `require_field()` - 53 edges
9. `to_json_value()` - 49 edges
10. `save_to_project()` - 46 edges

## Surprising Connections (you probably didn't know these)
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `test_response_encode_has_audit_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_protocol.py → plugin/cynogis/bridge/protocol.py
- `make()` --uses--> `AuditLog`  [INFERRED]
  tests/unit/test_dispatcher.py → plugin/cynogis/core/audit.py
- `make()` --uses--> `AuditLog`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/core/audit.py

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Garde-fous Cynogis** — claude_permission_levels, claude_edit_buffer, claude_algorithm_whitelist, claude_run_to_project, readme_audit_log, readme_execute_pyqgis [EXTRACTED 1.00]
- **Deploiement poste entreprise** — installation_network_share, installation_private_plugin_repo, installation_uv_tool_install, installation_shared_config, installation_referentials_dir, installation_mcp_clients [EXTRACTED 1.00]

## Communities (88 total, 12 thin omitted)

### Community 0 - "Web Services WFS"
Cohesion: 0.07
Nodes (40): Fetch, capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+32 more)

### Community 1 - "Job Execution Engine"
Cohesion: 0.05
Nodes (15): AlgCall, Executor, Job, JobManager, Pause, run_now(), _FetchTask, _Handle (+7 more)

### Community 2 - "Tool Errors & Output Save"
Cohesion: 0.08
Nodes (30): ErrorCode, ToolError, _from_template(), add_to_memory(), geometry_kind(), make_field(), _save_isopleths(), _write_csv() (+22 more)

### Community 3 - "Project & Shapefile Audit"
Cohesion: 0.06
Nodes (28): write_connection_file(), truncate_field_names(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport (+20 more)

### Community 4 - "Tool Modules Registry Core"
Cohesion: 0.12
Nodes (9): unique_field_name(), Level, Param, detect_territory(), _overview_extent(), extent_wgs84(), rect_to_list(), reproject_layer() (+1 more)

### Community 5 - "Landscape Metrics"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 6 - "Reference Landcover Sources"
Cohesion: 0.06
Nodes (29): _covers(), find_source_file(), is_agricultural(), map_feature(), map_ocsge(), referentials_directory(), _segments(), Source (+21 more)

### Community 7 - "Proximity & Observation Tools"
Cohesion: 0.10
Nodes (21): feature_request(), iter_geometries(), to_json_value(), check_landscape(), _collect(), count_observations(), count_points_in_polygon(), _distance_m() (+13 more)

### Community 8 - "Styling Tools"
Cohesion: 0.09
Nodes (26): ToolResult, get_class(), tool(), delete_field(), save_project(), suggest_landscape_mapping(), set_layer_encoding(), _apply() (+18 more)

### Community 9 - "Plugin Infrastructure"
Cohesion: 0.07
Nodes (6): QgsLogHandler, setup_logging(), teardown_logging(), Cynogis Plugin Icon (icon.svg), Green Map Location Pin, register_detail_provider()

### Community 10 - "Outputs & Export"
Cohesion: 0.09
Nodes (20): clean_name(), unique_path(), export_map_image(), _output_path(), _project_target(), _save_project_details(), write_document(), write_pdf() (+12 more)

### Community 11 - "Measures & Overlaps"
Cohesion: 0.10
Nodes (20): Pacer, needs_priority_field(), convert_area(), convert_length(), area_m2(), distance_area(), group_key(), length_m() (+12 more)

### Community 12 - "Landscape Classification"
Cohesion: 0.08
Nodes (22): apply_mapping(), classes_for(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+14 more)

### Community 13 - "Coefficients Computation"
Cohesion: 0.10
Nodes (25): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), list_categories() (+17 more)

### Community 14 - "Color Utilities"
Cohesion: 0.09
Nodes (20): contrast_ratio(), darken(), distinct_colors(), lighten(), mix(), parse_color(), relative_luminance(), to_hex() (+12 more)

### Community 15 - "Layer Info & Common"
Cohesion: 0.13
Nodes (18): clean_number(), crs_info(), enum_name(), file_format(), get_layer(), layer_kind(), source_path(), territory_info() (+10 more)

### Community 16 - "Vector Feature Tools"
Cohesion: 0.09
Nodes (16): get_vector_layer(), check_geometries(), _error_kind(), geometry_report(), _geometry_repr(), get_features(), get_field_values(), select_features() (+8 more)

### Community 17 - "Stakes & Impact Scoring"
Cohesion: 0.09
Nodes (21): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+13 more)

### Community 18 - "Naming & Algorithm Catalog"
Cohesion: 0.09
Nodes (15): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), to_ascii(), list_algorithms() (+7 more)

### Community 19 - "Job Tests"
Cohesion: 0.13
Nodes (24): boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req(), sans_etape() (+16 more)

### Community 20 - "Report Builder"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 21 - "Classification Breaks"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 22 - "TAXREF Taxon Status"
Cohesion: 0.11
Nodes (15): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+7 more)

### Community 23 - "Dispatcher & Bridge Server"
Cohesion: 0.15
Nodes (4): Response, BridgeServer, Dispatcher, finish()

### Community 24 - "Edit Journal"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 25 - "Field Type Coercion"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+10 more)

### Community 26 - "Overlap Resolution"
Cohesion: 0.12
Nodes (15): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), _closer_parts(), records(), test_egalite_stable(), test_half_plane_centres_confondus() (+7 more)

### Community 27 - "Slope & Terrain Classes"
Cohesion: 0.10
Nodes (16): aspect_sector(), degrees_to_percent(), distribution(), percent_to_degrees(), reclass_table(), slope_class(), SlopeClass, test_aspect_sector() (+8 more)

### Community 28 - "Elevation & Isopleths"
Cohesion: 0.10
Nodes (11): altitude_band(), parse_bands(), _isopleth_geometries(), _isopleths(), _style(), _clean(), elevation_sample(), _read_window() (+3 more)

### Community 29 - "Field Data Import"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 30 - "Distance Matrix Core"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 31 - "Edit Buffer Tools"
Cohesion: 0.15
Nodes (13): describe_summary(), is_shapefile(), add_field(), _commit_details(), _delete_field_details(), _editing_layers(), _field_limit(), get_pending_edits() (+5 more)

### Community 32 - "Style History"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 33 - "Coefficient & Metric Tools"
Cohesion: 0.18
Nodes (9): compute_coefficients(), _geometries(), landscape_metrics(), list_coefficients(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of() (+1 more)

### Community 34 - "Data Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 35 - "HABREF Habitat Typology"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 37 - "Symbol Validation"
Cohesion: 0.16
Nodes (16): build_categories(), normalize_geometry(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees(), test_build_categories_lignes_colorees(), test_build_categories_sans_value(), test_history_pop_vide() (+8 more)

### Community 38 - "Attribute Editing"
Cohesion: 0.18
Nodes (11): begin_edit(), refresh_layer(), select_ids(), calculate_field(), _check_count(), delete_features(), _delete_features_details(), merge_features() (+3 more)

### Community 39 - "Geometry Editing"
Cohesion: 0.18
Nodes (9): _change_geometries(), _conform(), _geometries(), _measure(), move_features(), _reference_subset(), _snap(), snap_features() (+1 more)

### Community 40 - "Bridge Protocol"
Cohesion: 0.18
Nodes (10): new_token(), remove_connection_file(), decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid() (+2 more)

### Community 41 - "Tool Registry & Policy"
Cohesion: 0.19
Nodes (5): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec

### Community 42 - "MCP Server App"
Cohesion: 0.19
Nodes (6): call_tool(), _fetch_specs(), list_tools(), _progress_token(), _to_tool(), _wait_job()

### Community 43 - "Referential Rules & Palettes"
Cohesion: 0.12
Nodes (5): landscape_palette(), check_rules(), map_cirad(), Rule, test_tables_coherentes_avec_la_nomenclature()

### Community 44 - "WFS Fetch & Cache"
Cohesion: 0.16
Nodes (8): service_label(), _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 45 - "Descriptive Stats"
Cohesion: 0.17
Nodes (8): describe(), describe_groups(), _r(), to_float(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 46 - "Atlas & Table Export"
Cohesion: 0.12
Nodes (7): export_atlas_pdf(), expression_context(), prepare_expression(), kernel_density_points(), export_table(), descriptive_stats(), _local_source()

### Community 47 - "Install & Deployment Docs"
Cohesion: 0.13
Nodes (16): Cynogis (CLAUDE.md), Rechargement du plugin apres modification, compat.py (Qt5/Qt6, QGIS 3.x et 4.x), Guide d'installation poste entreprise, Clients MCP (Claude Code, Claude Desktop, Codex), Partage reseau \\SERVEUR\Cynogis, Depot QGIS prive (plugins.xml), CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...) (+8 more)

### Community 48 - "Param Schema Validation"
Cohesion: 0.18
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 49 - "Zoning Tests"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 50 - "Dev Setup Script"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 51 - "Raster Terrain Tools"
Cohesion: 0.17
Nodes (7): get_raster_layer(), compute_ndvi(), classify_slope(), derive_terrain(), _flow_accumulation(), list_slope_classes(), _metric_raster()

### Community 52 - "Project Audit Core"
Cohesion: 0.21
Nodes (10): audit(), build_sections(), duplicate_name_findings(), _finding(), add(), project_findings(), severity_counts(), verdict() (+2 more)

### Community 53 - "Dispatcher Tests"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 54 - "Atlas Layout"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 55 - "Project Audit Tests"
Cohesion: 0.32
Nodes (13): layer_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique(), test_projet_sain_sans_anomalie() (+5 more)

### Community 56 - "Plugin Build Script"
Cohesion: 0.23
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 57 - "Label Validation"
Cohesion: 0.18
Nodes (8): readable_text_color(), _lookup(), _number(), validate_labels(), test_readable_text_color(), test_validate_labels_halo_deduit(), test_validate_labels_placement_inconnu(), test_validate_labels_sans_source()

### Community 58 - "Bridge Client"
Cohesion: 0.26
Nodes (5): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 59 - "Palette Ramps"
Cohesion: 0.18
Nodes (9): interpolate_ramp(), get_palette(), resolve_colors(), test_interpolate_ramp_extremites_conservees(), test_interpolate_ramp_longueurs(), test_get_palette_etiree(), test_get_palette_inconnue(), test_resolve_colors_priorite_aux_couleurs() (+1 more)

### Community 60 - "Zoning Assessment"
Cohesion: 0.21
Nodes (6): assess(), bbox_covers(), should_replace_cache(), zoning_state(), test_bbox_rules(), test_pre_diagnostic()

### Community 61 - "Feature Add & WKT"
Cohesion: 0.20
Nodes (5): field_type_name(), geometry_from_wkt(), layer_field_types(), wkt_to_layer_crs(), add_features()

### Community 62 - "Audit Log"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 63 - "Sampling Allocation"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 64 - "Zoning Territory Catalog"
Cohesion: 0.20
Nodes (7): cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, test_cache_meta_roundtrip_and_matching(), test_par_territoire()

### Community 65 - "Zoning Cache"
Cohesion: 0.24
Nodes (5): cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_root_env_override()

### Community 66 - "Map Rendering"
Cohesion: 0.18
Nodes (3): render_map(), _open_project(), _overview_map()

### Community 67 - "User Palettes"
Cohesion: 0.20
Nodes (6): all_palettes(), load_user_palettes(), register_palette(), validate_palette(), test_load_user_palettes_ignore_les_erreurs(), test_validate_palette_trop_courte()

### Community 68 - "PyQGIS Code Check"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 70 - "Security & Protocol Concepts"
Cohesion: 0.28
Nodes (3): Depannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN...), Journal d'audit ~/.cynogis/audit, execute_pyqgis (dernier recours)

### Community 71 - "Sampling Plans"
Cohesion: 0.31
Nodes (3): _cut(), _systematic(), transect_sampling_plan()

### Community 74 - "Job Wait Tests"
Cohesion: 0.39
Nodes (6): BridgeResult, FakeClient, test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 75 - "Architecture Concepts"
Cohesion: 0.29
Nodes (3): Decouverte via ~/.cynogis/connection.json, Decorateur @tool (registry/schema), Configuration partagee (web_services.json, palettes.json)

### Community 76 - "Style Options Catalog"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 77 - "Run Algorithm Tool"
Cohesion: 0.29
Nodes (3): _allowed(), describe_algorithm(), run_algorithm()

### Community 78 - "Confirmation Dialog"
Cohesion: 0.33
Nodes (3): build_details(), make_confirmer(), confirm()

### Community 79 - "French Number Format"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

## Knowledge Gaps
- **10 isolated node(s):** `cynogis-server`, `CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...)`, `Configuration partagee (web_services.json, palettes.json)`, `Clients MCP (Claude Code, Claude Desktop, Codex)`, `SCR cibles EPSG:2975 (Reunion) / EPSG:4471 (Mayotte)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 654 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `Tool Errors & Output Save` to `Web Services WFS`, `Job Execution Engine`, `Project & Shapefile Audit`, `Tool Modules Registry Core`, `Reference Landcover Sources`, `Proximity & Observation Tools`, `Styling Tools`, `Plugin Infrastructure`, `Outputs & Export`, `Measures & Overlaps`, `Layer Info & Common`, `Vector Feature Tools`, `Job Tests`, `Dispatcher & Bridge Server`, `Elevation & Isopleths`, `Edit Buffer Tools`, `Coefficient & Metric Tools`, `Attribute Editing`, `Geometry Editing`, `Bridge Protocol`, `Tool Registry & Policy`, `WFS Fetch & Cache`, `Atlas & Table Export`, `Param Schema Validation`, `Raster Terrain Tools`, `Dispatcher Tests`, `Feature Add & WKT`, `Map Rendering`, `Sampling Plans`, `Fake Executor Tests`, `Run Algorithm Tool`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Are the 90 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 90 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...)`, `Configuration partagee (web_services.json, palettes.json)` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Web Services WFS` be split into smaller, more focused modules?**
  _Cohesion score 0.06790890269151138 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `Tool Errors & Output Save` to `Web Services WFS`, `Job Execution Engine`, `Project & Shapefile Audit`, `Tool Modules Registry Core`, `Reference Landcover Sources`, `Proximity & Observation Tools`, `Styling Tools`, `Plugin Infrastructure`, `Outputs & Export`, `Measures & Overlaps`, `Layer Info & Common`, `Vector Feature Tools`, `Job Tests`, `Dispatcher & Bridge Server`, `Elevation & Isopleths`, `Edit Buffer Tools`, `Coefficient & Metric Tools`, `Attribute Editing`, `Geometry Editing`, `Bridge Protocol`, `Tool Registry & Policy`, `WFS Fetch & Cache`, `Atlas & Table Export`, `Param Schema Validation`, `Raster Terrain Tools`, `Dispatcher Tests`, `Feature Add & WKT`, `Map Rendering`, `Sampling Plans`, `Fake Executor Tests`, `Run Algorithm Tool`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 137 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 137 INFERRED edges - model-reasoned connections that need verification._
- **Should `Job Execution Engine` be split into smaller, more focused modules?**
  _Cohesion score 0.05325140809011777 - nodes in this community are weakly interconnected._