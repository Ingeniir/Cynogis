# Graph Report - cynogis  (2026-10-26)

## Corpus Check
- 133 files · ~95,758 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 1978 nodes · 6001 edges · 100 communities (81 shown, 19 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 481 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2a828b65`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Web Services WFS
- Classification Breaks
- tasks.py
- Landscape Metrics
- merge_features
- Proximity & Geometry Iteration
- ErrorCode
- confirm.py
- Coefficients Computation
- common.py
- tool
- JobManager
- ToolResult
- Landscape Classification
- Feuille de route Cynogis
- Impact Quantification
- Referential Rules
- Styling Tools
- ToolError
- Terrain Classes
- Job Tests
- Edit Journal
- Unit Conversion
- Field Data Import
- Color Mixing
- Shapefile Export Plan
- Categorized Symbols
- TAXREF Taxon Status
- HTTP Fetch Step
- Color Palettes Core
- Overlap Resolution
- Layer Source Info
- Algorithm Catalog
- Field Type Coercion
- Project Audit Findings
- Distance Matrix Core
- Descriptive Stats
- _closer_parts
- Style History
- HABREF Habitat Typology
- Permission Policy
- Bridge Request Handling
- Isopleths & Density
- Coefficient & Metric Tools
- app.py
- Dev Setup Script
- Zoning Assessment
- WFS GetFeature & Zoning Tests
- Dispatcher Tests
- Plugin Build Script
- json
- Bridge TCP Server
- Atlas Layout
- Executor
- Param Schema Validation
- Plugin Entry Point
- User Palettes
- Bridge Architecture Docs
- Referentials Directory
- Zoning Cache
- PDF Report Rendering
- Sampling Geometry
- Pause
- _overlay
- Zoning Catalog
- Audit Log
- editing.py
- Sampling Allocation
- run_algorithm
- Security & Permissions Docs
- Provenance
- PyQGIS Code Check
- begin_edit
- Install Guide Docs
- apply_categorized_style
- WCAG Contrast
- tools/project_audit.py
- add_features
- Fake Executor Tests
- check_surfaces.py
- QgsLogHandler
- Layer Listing
- Territory
- Ecology Workflows Docs
- Editing & Tool Conventions Docs
- _sibling
- Geometry Validation
- Code Conventions Docs
- Deployment Docs
- Business Rules & CRS
- Coefficient Catalog
- Cynogis Plugin Icon (icon.svg)
- OCS GE Mapping
- list_style_options
- pytest
- Test App Fixture
- Server Entry Script

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 197 edges
2. `ErrorCode` - 179 edges
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
- **Cynogis safety guardrails** — claude_permission_levels, claude_algorithm_whitelist, claude_outputs_never_overwrite, raport_restricted_network, raport_audit_log, claude_edit_buffer [EXTRACTED 1.00]
- **Garde-fous Cynogis** — claude_permission_levels, claude_edit_buffer, claude_algorithm_whitelist, readme_audit_log, readme_execute_pyqgis [EXTRACTED 1.00]
- **Deploiement poste entreprise** — installation_network_share, installation_private_plugin_repo, installation_uv_tool_install, installation_shared_config, installation_referentials_dir, installation_mcp_clients [EXTRACTED 1.00]
- **Long job execution flow** — claude_job_model, raport_long_job_flow, raport_internal_tools, claude_outputs_never_overwrite [INFERRED 0.85]

## Communities (100 total, 19 thin omitted)

### Community 0 - "Web Services WFS"
Cohesion: 0.06
Nodes (42): capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list(), _local() (+34 more)

### Community 1 - "Classification Breaks"
Cohesion: 0.05
Nodes (44): clean_values(), compute_breaks(), _dedupe(), equal_interval(), format_number(), natural_breaks(), pretty_breaks(), quantile_breaks() (+36 more)

### Community 2 - "tasks.py"
Cohesion: 0.12
Nodes (8): AlgCall, Fetch, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers()

### Community 3 - "Landscape Metrics"
Cohesion: 0.07
Nodes (31): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), fractal_dimension(), largest_patch_index(), mean_patch_size() (+23 more)

### Community 4 - "merge_features"
Cohesion: 0.15
Nodes (12): _change_geometries(), _conform(), _geometries(), _measure(), merge_features(), move_features(), _record(), _reference_subset() (+4 more)

### Community 5 - "Proximity & Geometry Iteration"
Cohesion: 0.07
Nodes (28): expression_context(), feature_request(), iter_geometries(), prepare_expression(), select_ids(), to_json_value(), calculate_field(), _geometry_repr() (+20 more)

### Community 6 - "ErrorCode"
Cohesion: 0.10
Nodes (18): ErrorCode, clean_name(), unique_path(), export_atlas_pdf(), _from_template(), get_layer(), export_map_image(), export_table() (+10 more)

### Community 7 - "confirm.py"
Cohesion: 0.11
Nodes (4): build_details(), make_confirmer(), confirm(), register_detail_provider()

### Community 8 - "Coefficients Computation"
Cohesion: 0.09
Nodes (25): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+17 more)

### Community 9 - "common.py"
Cohesion: 0.10
Nodes (9): Pacer, setup_logging(), teardown_logging(), Level, Param, polygon_parts(), is_optional(), _run() (+1 more)

### Community 10 - "tool"
Cohesion: 0.06
Nodes (30): tool(), get_raster_layer(), get_vector_layer(), kernel_density_points(), delete_field(), check_geometries(), buffer(), dissolve() (+22 more)

### Community 12 - "ToolResult"
Cohesion: 0.09
Nodes (24): ToolResult, unique_field_name(), detect_territory(), _overview_extent(), clean_number(), crs_info(), enum_name(), extent_wgs84() (+16 more)

### Community 13 - "Landscape Classification"
Cohesion: 0.08
Nodes (23): apply_mapping(), classes_for(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register() (+15 more)

### Community 14 - "Feuille de route Cynogis"
Cohesion: 0.18
Nodes (10): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic), Phase 3 : Traçabilité et confidentialité, Phase 4 : Spécificités de Mayotte, Phase 5 : Modules métier différenciants (+2 more)

### Community 15 - "Impact Quantification"
Cohesion: 0.08
Nodes (22): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+14 more)

### Community 16 - "Referential Rules"
Cohesion: 0.10
Nodes (21): check_rules(), _covers(), map_cirad(), map_feature(), map_ocsge(), _segments(), Source, sources_for() (+13 more)

### Community 17 - "Styling Tools"
Cohesion: 0.15
Nodes (15): refresh_layer(), _apply(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _kind(), _numeric_values() (+7 more)

### Community 18 - "ToolError"
Cohesion: 0.09
Nodes (28): ToolError, add_to_memory(), area_m2(), crs_from_text(), distance_area(), geometry_kind(), make_field(), _save_isopleths() (+20 more)

### Community 19 - "Terrain Classes"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 20 - "Job Tests"
Cohesion: 0.13
Nodes (23): boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req(), sans_etape() (+15 more)

### Community 21 - "Edit Journal"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 22 - "Unit Conversion"
Cohesion: 0.13
Nodes (13): convert_area(), convert_length(), compute_coefficients(), group_key(), length_m(), perimeter_m(), require_field(), get_field_values() (+5 more)

### Community 23 - "Field Data Import"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 24 - "Color Mixing"
Cohesion: 0.12
Nodes (15): darken(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), test_interpolate_ramp_extremites_conservees() (+7 more)

### Community 25 - "Shapefile Export Plan"
Cohesion: 0.10
Nodes (17): truncate_field_names(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages() (+9 more)

### Community 26 - "Categorized Symbols"
Cohesion: 0.11
Nodes (22): build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees() (+14 more)

### Community 27 - "TAXREF Taxon Status"
Cohesion: 0.14
Nodes (14): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+6 more)

### Community 28 - "HTTP Fetch Step"
Cohesion: 0.16
Nodes (8): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), _local_source(), Source, _sources(), _wfs_features()

### Community 29 - "Color Palettes Core"
Cohesion: 0.11
Nodes (12): distinct_colors(), validate_colors(), with_alpha(), landscape_palette(), register_palette(), resolve_colors(), validate_palette(), test_distinct_colors_sans_doublon() (+4 more)

### Community 30 - "Overlap Resolution"
Cohesion: 0.14
Nodes (15): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus() (+7 more)

### Community 31 - "Layer Source Info"
Cohesion: 0.18
Nodes (7): file_format(), source_path(), _layer_facts(), _raster_facts(), _vector_facts(), _scan_sidecars(), _text_sample()

### Community 32 - "Algorithm Catalog"
Cohesion: 0.09
Nodes (15): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), to_ascii(), list_algorithms() (+7 more)

### Community 33 - "Field Type Coercion"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+10 more)

### Community 34 - "Project Audit Findings"
Cohesion: 0.18
Nodes (19): audit(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), _yes_no(), severities() (+11 more)

### Community 35 - "Distance Matrix Core"
Cohesion: 0.13
Nodes (13): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), to_float(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible() (+5 more)

### Community 36 - "Descriptive Stats"
Cohesion: 0.18
Nodes (7): describe(), describe_groups(), _r(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 38 - "Style History"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 39 - "HABREF Habitat Typology"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 40 - "Permission Policy"
Cohesion: 0.18
Nodes (5): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec

### Community 41 - "Bridge Request Handling"
Cohesion: 0.23
Nodes (3): Request, Dispatcher, finish()

### Community 42 - "Isopleths & Density"
Cohesion: 0.15
Nodes (6): _isopleth_geometries(), _isopleths(), _style(), _clean(), _sector_index(), _slope_aspect()

### Community 43 - "Coefficient & Metric Tools"
Cohesion: 0.20
Nodes (7): interpret_metrics(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of()

### Community 44 - "app.py"
Cohesion: 0.08
Nodes (19): main(), call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job() (+11 more)

### Community 45 - "Dev Setup Script"
Cohesion: 0.23
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 46 - "Zoning Assessment"
Cohesion: 0.16
Nodes (8): assess(), cache_matches(), for_territory(), _inpn(), Zoning, regulatory_prescan(), test_par_territoire(), test_pre_diagnostic()

### Community 47 - "WFS GetFeature & Zoning Tests"
Cohesion: 0.18
Nodes (6): getfeature_url(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 48 - "Dispatcher Tests"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 49 - "Plugin Build Script"
Cohesion: 0.23
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 50 - "json"
Cohesion: 0.15
Nodes (11): new_token(), remove_connection_file(), write_connection_file(), decode_request(), _protocol_error(), save_palette(), _line(), test_decode_invalid() (+3 more)

### Community 52 - "Atlas Layout"
Cohesion: 0.17
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 54 - "Param Schema Validation"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 56 - "User Palettes"
Cohesion: 0.22
Nodes (6): all_palettes(), get_palette(), load_user_palettes(), test_get_palette_etiree(), test_get_palette_inconnue(), test_load_user_palettes_ignore_les_erreurs()

### Community 57 - "Bridge Architecture Docs"
Cohesion: 0.22
Nodes (11): Bridge protocol v1 (JSON-lines), connection.json discovery (~/.cynogis), Cynogis (CLAUDE.md), Configuration partagee (web_services.json, palettes.json), Architecture and operation, Cynogis project report (RAPORT.md), ~/.cynogis user directory, Internal tools (list_tools, get_job_status, cancel_job) (+3 more)

### Community 58 - "Referentials Directory"
Cohesion: 0.15
Nodes (7): find_source_file(), referentials_directory(), _clipped(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 59 - "Zoning Cache"
Cohesion: 0.21
Nodes (7): cache_meta(), cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_meta_roundtrip_and_matching(), test_cache_root_env_override()

### Community 60 - "PDF Report Rendering"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 61 - "Sampling Geometry"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 62 - "Pause"
Cohesion: 0.28
Nodes (6): Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 63 - "_overlay"
Cohesion: 0.29
Nodes (3): is_agricultural(), _overlay(), test_is_agricultural()

### Community 64 - "Zoning Catalog"
Cohesion: 0.20
Nodes (6): bbox_covers(), should_replace_cache(), status(), zoning_state(), test_bbox_rules(), test_statut()

### Community 65 - "Audit Log"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 66 - "editing.py"
Cohesion: 0.14
Nodes (14): describe_summary(), is_shapefile(), add_field(), _commit_details(), _delete_features_details(), _delete_field_details(), _editing_layers(), _field_limit() (+6 more)

### Community 67 - "Sampling Allocation"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 68 - "run_algorithm"
Cohesion: 0.29
Nodes (3): _allowed(), describe_algorithm(), run_algorithm()

### Community 69 - "Security & Permissions Docs"
Cohesion: 0.29
Nodes (8): run_algorithm whitelist (ALGORITHMS), Permission levels READ/CREATE/MODIFY/DESTROY, Security rules (no bypass, no overwrite, no sensitive data), Audit log (get_audit_log), Restricted network (webservices catalogue), Security model (six guardrails), Journal d'audit ~/.cynogis/audit, execute_pyqgis (dernier recours)

### Community 70 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 71 - "PyQGIS Code Check"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 72 - "begin_edit"
Cohesion: 0.33
Nodes (4): begin_edit(), _check_count(), delete_features(), update_attributes()

### Community 73 - "Install Guide Docs"
Cohesion: 0.22
Nodes (9): Guide d'installation poste entreprise, Clients MCP (Claude Code, Claude Desktop, Codex), Depannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN...), Installation du serveur via uv tool (cynogis-server.exe), Cynogis README, Installation de developpement (dev_setup.py, qgis_env_snippet.py), RAPORT.md, SCR cibles EPSG:2975 (Reunion) / EPSG:4471 (Mayotte) (+1 more)

### Community 74 - "apply_categorized_style"
Cohesion: 0.33
Nodes (3): apply_categorized_style(), _distinct_values(), _sort_key()

### Community 75 - "WCAG Contrast"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 76 - "tools/project_audit.py"
Cohesion: 0.24
Nodes (8): build_sections(), severity_counts(), verdict(), layer_kind(), audit_project(), _open_project(), _overview_map(), _project_facts()

### Community 77 - "add_features"
Cohesion: 0.18
Nodes (5): field_type_name(), geometry_from_wkt(), layer_field_types(), wkt_to_layer_crs(), add_features()

### Community 79 - "check_surfaces.py"
Cohesion: 0.47
Nodes (3): check_site(), square(), utm_scale()

### Community 81 - "Layer Listing"
Cohesion: 0.29
Nodes (4): list_layers(), _summary(), _tree(), _visible()

### Community 83 - "Ecology Workflows Docs"
Cohesion: 0.29
Nodes (7): Ecological impact study workflow (ERC), Ecology referentials (TAXREF, BDC Statuts, HABREF, zonings), Ecology, proximity, stakes and impacts tools, Landscape diagnosis workflow, Closed landscape nomenclature, Coefficients, landscape, terrain tools, Typical AI workflows

### Community 84 - "Editing & Tool Conventions Docs"
Cohesion: 0.40
Nodes (6): Adding a tool (@tool decorator), Edit buffer and JOURNAL (request_commit only writes), Editing tools (buffer then human commit), execute_pyqgis (DESTROY, last resort), Known limits and pending validations, Tool catalog (101 + 4 internal)

### Community 88 - "Deployment Docs"
Cohesion: 0.40
Nodes (5): Partage reseau \\SERVEUR\Cynogis, Depot QGIS prive (plugins.xml), CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...), metadata.txt (Cynogis Reunion-Mayotte 0.1.0), QGIS 3.38 a 4.99, supportsQt6

### Community 89 - "Business Rules & CRS"
Cohesion: 0.83
Nodes (3): Business rules (CRS, surfaces, no Natura 2000 in DOM), EPSG:2975 La Reunion (RGR92 / UTM 40S), EPSG:4471 Mayotte (RGM04 / UTM 38S)

### Community 93 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 95 - "pytest"
Cohesion: 0.22
Nodes (5): elongation(), test_elongation(), test_detect(), test_conversions(), test_unknown_unit()

## Knowledge Gaps
- **18 isolated node(s):** `cynogis-server`, `Configuration partagee (web_services.json, palettes.json)`, `Audit log (get_audit_log)`, `Restricted network (webservices catalogue)`, `Journal d'audit ~/.cynogis/audit` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 675 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `Web Services WFS`, `tasks.py`, `merge_features`, `Proximity & Geometry Iteration`, `ErrorCode`, `confirm.py`, `common.py`, `tool`, `JobManager`, `ToolResult`, `Styling Tools`, `Job Tests`, `Unit Conversion`, `HTTP Fetch Step`, `Permission Policy`, `Bridge Request Handling`, `Coefficient & Metric Tools`, `Dispatcher Tests`, `json`, `Bridge TCP Server`, `Param Schema Validation`, `Referentials Directory`, `PDF Report Rendering`, `editing.py`, `run_algorithm`, `begin_edit`, `apply_categorized_style`, `tools/project_audit.py`, `add_features`, `Fake Executor Tests`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Are the 91 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 91 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `Configuration partagee (web_services.json, palettes.json)`, `Audit log (get_audit_log)` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Web Services WFS` be split into smaller, more focused modules?**
  _Cohesion score 0.06293965198074787 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `Web Services WFS`, `tasks.py`, `merge_features`, `Proximity & Geometry Iteration`, `confirm.py`, `common.py`, `tool`, `JobManager`, `ToolResult`, `Styling Tools`, `ToolError`, `Job Tests`, `Unit Conversion`, `HTTP Fetch Step`, `Permission Policy`, `Bridge Request Handling`, `Coefficient & Metric Tools`, `Dispatcher Tests`, `json`, `Bridge TCP Server`, `Param Schema Validation`, `Referentials Directory`, `PDF Report Rendering`, `editing.py`, `run_algorithm`, `begin_edit`, `apply_categorized_style`, `tools/project_audit.py`, `add_features`, `Fake Executor Tests`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 139 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 139 INFERRED edges - model-reasoned connections that need verification._
- **Should `Classification Breaks` be split into smaller, more focused modules?**
  _Cohesion score 0.05443371378402107 - nodes in this community are weakly interconnected._