# Graph Report - cynogis  (2026-10-26)

## Corpus Check
- 133 files · ~93,901 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1959 nodes · 5967 edges · 101 communities (83 shown, 18 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 478 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Web Services WFS
- Classification Breaks
- Job Execution Engine
- Landscape Metrics
- Edit Buffer Tools
- Proximity & Geometry Iteration
- Tool Errors
- Plugin Infrastructure
- Coefficients Computation
- Dispatcher Core
- Tool Registry & Field Tools
- Field Naming Logic
- Territory Detection
- Landscape Classification
- Output Paths & Rasters
- Impact Quantification
- Referential Rules
- Styling Tools
- Impact Tables & Requests
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
- Pacer & Polygon Parts
- Style History
- HABREF Habitat Typology
- Permission Policy
- Bridge Request Handling
- Isopleths & Density
- Coefficient & Metric Tools
- MCP Server App
- Dev Setup Script
- Zoning Assessment
- WFS GetFeature & Zoning Tests
- Dispatcher Tests
- Plugin Build Script
- Bridge Protocol
- Bridge TCP Server
- Atlas Layout
- Output Naming
- Param Schema Validation
- Plugin Entry Point
- User Palettes
- Bridge Architecture Docs
- Referentials Directory
- Zoning Cache
- PDF Report Rendering
- Sampling Geometry
- Bridge Client
- Landscape Nomenclature Rules
- Zoning Catalog
- Audit Log
- Pending Edits & Confirmation
- Sampling Allocation
- Layer Info & Map Export
- Security & Permissions Docs
- Data Freshness
- PyQGIS Code Check
- Ping Script & Client
- Install Guide Docs
- Connection File
- WCAG Contrast
- Project Audit Core
- Field Types & Add Features
- Fake Executor Tests
- Encoding Detection
- Data Provenance
- Layer Listing
- Job Wait Tests
- Ecology Workflows Docs
- Editing & Tool Conventions Docs
- Confirmation Dialog
- Geometry Validation
- Code Conventions Docs
- Deployment Docs
- Business Rules & CRS
- Coefficient Catalog
- Coefficient Spec
- OCS GE Mapping
- Style Options Catalog
- Geometry Repr
- Territory Tests
- Test App Fixture
- Server Entry Script

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
- `telechargement()` --uses--> `Fetch`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/core/jobs.py
- `test_telechargement()` --uses--> `Fetch`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/core/jobs.py
- `calcul()` --uses--> `AlgCall`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/core/jobs.py

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Garde-fous Cynogis** — claude_permission_levels, claude_edit_buffer, claude_algorithm_whitelist, readme_audit_log, readme_execute_pyqgis [EXTRACTED 1.00]
- **Deploiement poste entreprise** — installation_network_share, installation_private_plugin_repo, installation_uv_tool_install, installation_shared_config, installation_referentials_dir, installation_mcp_clients [EXTRACTED 1.00]
- **Cynogis safety guardrails** — claude_permission_levels, claude_algorithm_whitelist, claude_outputs_never_overwrite, raport_restricted_network, raport_audit_log, claude_edit_buffer [EXTRACTED 1.00]
- **Long job execution flow** — claude_job_model, raport_long_job_flow, raport_internal_tools, claude_outputs_never_overwrite [INFERRED 0.85]

## Communities (101 total, 18 thin omitted)

### Community 0 - "Web Services WFS"
Cohesion: 0.07
Nodes (41): capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list(), _local() (+33 more)

### Community 1 - "Classification Breaks"
Cohesion: 0.05
Nodes (44): clean_values(), compute_breaks(), _dedupe(), equal_interval(), format_number(), natural_breaks(), pretty_breaks(), quantile_breaks() (+36 more)

### Community 2 - "Job Execution Engine"
Cohesion: 0.05
Nodes (15): AlgCall, Executor, Job, JobManager, Pause, run_now(), _FetchTask, _Handle (+7 more)

### Community 3 - "Landscape Metrics"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 4 - "Edit Buffer Tools"
Cohesion: 0.10
Nodes (24): begin_edit(), is_shapefile(), refresh_layer(), select_ids(), add_field(), calculate_field(), _change_geometries(), _check_count() (+16 more)

### Community 5 - "Proximity & Geometry Iteration"
Cohesion: 0.09
Nodes (18): iter_geometries(), _collect(), count_observations(), count_points_in_polygon(), distance_layer(), _distance_m(), distance_matrix(), distance_to_sensitive_features() (+10 more)

### Community 6 - "Tool Errors"
Cohesion: 0.08
Nodes (18): ErrorCode, ToolError, _allowed(), describe_algorithm(), run_algorithm(), export_atlas_pdf(), _from_template(), expression_context() (+10 more)

### Community 7 - "Plugin Infrastructure"
Cohesion: 0.08
Nodes (8): QgsLogHandler, setup_logging(), teardown_logging(), Cynogis Plugin Icon (icon.svg), Green Map Location Pin, _project_target(), _save_project_details(), register_detail_provider()

### Community 8 - "Coefficients Computation"
Cohesion: 0.10
Nodes (25): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), _ratio() (+17 more)

### Community 10 - "Tool Registry & Field Tools"
Cohesion: 0.09
Nodes (20): tool(), get_vector_layer(), _delete_field_details(), _merge_details(), check_geometries(), select_features(), buffer(), create_study_area_buffers() (+12 more)

### Community 11 - "Field Naming Logic"
Cohesion: 0.10
Nodes (15): unique_field_name(), add_to_memory(), crs_from_text(), make_field(), _save_isopleths(), _write_csv(), import_field_data(), habitat_typology_join() (+7 more)

### Community 12 - "Territory Detection"
Cohesion: 0.13
Nodes (13): detect_territory(), Territory, _overview_extent(), clean_number(), crs_info(), enum_name(), extent_wgs84(), rect_to_list() (+5 more)

### Community 13 - "Landscape Classification"
Cohesion: 0.09
Nodes (18): apply_mapping(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+10 more)

### Community 14 - "Output Paths & Rasters"
Cohesion: 0.11
Nodes (13): unique_path(), get_raster_layer(), compute_ndvi(), is_optional(), output_dir(), _output_item(), _run(), run_in_memory() (+5 more)

### Community 15 - "Impact Quantification"
Cohesion: 0.10
Nodes (21): compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number(), Override (+13 more)

### Community 16 - "Referential Rules"
Cohesion: 0.11
Nodes (21): _covers(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), _segments(), Source, sources_for() (+13 more)

### Community 17 - "Styling Tools"
Cohesion: 0.13
Nodes (18): ToolResult, _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _distinct_values() (+10 more)

### Community 18 - "Impact Tables & Requests"
Cohesion: 0.10
Nodes (17): build_table(), feature_request(), geometry_kind(), group_key(), require_field(), write_table(), get_features(), get_field_values() (+9 more)

### Community 19 - "Terrain Classes"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 20 - "Job Tests"
Cohesion: 0.13
Nodes (24): boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req(), sans_etape() (+16 more)

### Community 21 - "Edit Journal"
Cohesion: 0.10
Nodes (11): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+3 more)

### Community 22 - "Unit Conversion"
Cohesion: 0.15
Nodes (14): convert_area(), convert_length(), area_m2(), distance_area(), length_m(), perimeter_m(), habitat_area_stats(), measure() (+6 more)

### Community 23 - "Field Data Import"
Cohesion: 0.11
Nodes (13): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), _read() (+5 more)

### Community 24 - "Color Mixing"
Cohesion: 0.11
Nodes (16): darken(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), with_alpha() (+8 more)

### Community 25 - "Shapefile Export Plan"
Cohesion: 0.11
Nodes (15): truncate_field_names(), companion_paths(), export_plan(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), test_truncate_field_names_sans_doublon() (+7 more)

### Community 26 - "Categorized Symbols"
Cohesion: 0.12
Nodes (21): build_categories(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees(), test_build_categories_lignes_colorees() (+13 more)

### Community 27 - "TAXREF Taxon Status"
Cohesion: 0.11
Nodes (14): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+6 more)

### Community 28 - "HTTP Fetch Step"
Cohesion: 0.14
Nodes (10): Fetch, service_label(), _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), _local_source(), Source (+2 more)

### Community 29 - "Color Palettes Core"
Cohesion: 0.12
Nodes (10): distinct_colors(), validate_colors(), describe_palettes(), landscape_palette(), resolve_colors(), _lookup(), test_distinct_colors_sans_doublon(), test_validate_colors_message_indexe() (+2 more)

### Community 30 - "Overlap Resolution"
Cohesion: 0.14
Nodes (15): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus() (+7 more)

### Community 31 - "Layer Source Info"
Cohesion: 0.14
Nodes (11): file_format(), layer_kind(), source_path(), _layer_facts(), _open_project(), _overview_map(), _project_facts(), _raster_facts() (+3 more)

### Community 32 - "Algorithm Catalog"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 33 - "Field Type Coercion"
Cohesion: 0.12
Nodes (16): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict(), test_coerce_value() (+8 more)

### Community 34 - "Project Audit Findings"
Cohesion: 0.20
Nodes (18): audit(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons() (+10 more)

### Community 35 - "Distance Matrix Core"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 36 - "Descriptive Stats"
Cohesion: 0.14
Nodes (10): describe(), describe_groups(), _r(), to_float(), descriptive_stats(), _numeric_values(), test_describe_basic(), test_describe_empty_and_single() (+2 more)

### Community 37 - "Pacer & Polygon Parts"
Cohesion: 0.12
Nodes (7): Pacer, polygon_parts(), _as_multipolygon(), _closer_parts(), clip_reference_landcover(), _clipped(), _overlay()

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
Cohesion: 0.19
Nodes (4): Request, Response, Dispatcher, finish()

### Community 42 - "Isopleths & Density"
Cohesion: 0.13
Nodes (8): _isopleth_geometries(), _isopleths(), _style(), _clean(), elevation_sample(), _read_window(), _sector_index(), _slope_aspect()

### Community 43 - "Coefficient & Metric Tools"
Cohesion: 0.20
Nodes (8): compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), to_json_value()

### Community 44 - "MCP Server App"
Cohesion: 0.19
Nodes (6): call_tool(), _fetch_specs(), list_tools(), _progress_token(), _to_tool(), _wait_job()

### Community 45 - "Dev Setup Script"
Cohesion: 0.23
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 46 - "Zoning Assessment"
Cohesion: 0.16
Nodes (9): assess(), for_territory(), _inpn(), Zoning, zoning_state(), regulatory_prescan(), regulatory_zoning_intersect(), test_par_territoire() (+1 more)

### Community 47 - "WFS GetFeature & Zoning Tests"
Cohesion: 0.15
Nodes (8): getfeature_url(), test_describe_multiple_sources_and_missing(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_prescan_sections_lists_sources_with_origin(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 48 - "Dispatcher Tests"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 49 - "Plugin Build Script"
Cohesion: 0.22
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 50 - "Bridge Protocol"
Cohesion: 0.20
Nodes (7): decode_request(), _protocol_error(), _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 52 - "Atlas Layout"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 53 - "Output Naming"
Cohesion: 0.18
Nodes (7): sanitize_field_name(), clean_name(), to_ascii(), test_sanitize_reserve(), test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

### Community 54 - "Param Schema Validation"
Cohesion: 0.22
Nodes (8): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_items_enum(), test_object_schema()

### Community 56 - "User Palettes"
Cohesion: 0.14
Nodes (9): all_palettes(), get_palette(), load_user_palettes(), register_palette(), validate_palette(), test_get_palette_etiree(), test_get_palette_inconnue(), test_load_user_palettes_ignore_les_erreurs() (+1 more)

### Community 57 - "Bridge Architecture Docs"
Cohesion: 0.22
Nodes (11): Bridge protocol v1 (JSON-lines), connection.json discovery (~/.cynogis), Cynogis (CLAUDE.md), Configuration partagee (web_services.json, palettes.json), Architecture and operation, Cynogis project report (RAPORT.md), ~/.cynogis user directory, Internal tools (list_tools, get_job_status, cancel_job) (+3 more)

### Community 58 - "Referentials Directory"
Cohesion: 0.18
Nodes (6): find_source_file(), referentials_directory(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 59 - "Zoning Cache"
Cohesion: 0.21
Nodes (7): cache_meta(), cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_meta_roundtrip_and_matching(), test_cache_root_env_override()

### Community 60 - "PDF Report Rendering"
Cohesion: 0.17
Nodes (4): _output_path(), render_map(), write_document(), write_pdf()

### Community 61 - "Sampling Geometry"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 62 - "Bridge Client"
Cohesion: 0.26
Nodes (5): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 63 - "Landscape Nomenclature Rules"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 64 - "Zoning Catalog"
Cohesion: 0.20
Nodes (6): bbox_covers(), cache_matches(), should_replace_cache(), status(), test_bbox_rules(), test_statut()

### Community 65 - "Audit Log"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 66 - "Pending Edits & Confirmation"
Cohesion: 0.24
Nodes (7): describe_summary(), _commit_details(), _editing_layers(), get_pending_edits(), request_commit(), rollback_edits(), _targets()

### Community 67 - "Sampling Allocation"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 68 - "Layer Info & Map Export"
Cohesion: 0.18
Nodes (6): get_layer(), export_map_image(), get_layer_info(), organize_layers(), get_layer_style(), save_style_file()

### Community 69 - "Security & Permissions Docs"
Cohesion: 0.29
Nodes (8): run_algorithm whitelist (ALGORITHMS), Permission levels READ/CREATE/MODIFY/DESTROY, Security rules (no bypass, no overwrite, no sensitive data), Audit log (get_audit_log), Restricted network (webservices catalogue), Security model (six guardrails), Journal d'audit ~/.cynogis/audit, execute_pyqgis (dernier recours)

### Community 70 - "Data Freshness"
Cohesion: 0.29
Nodes (5): age_days(), describe_sources(), freshness(), prescan_sections(), test_age_never_negative_and_tolerates_garbage()

### Community 71 - "PyQGIS Code Check"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 73 - "Install Guide Docs"
Cohesion: 0.22
Nodes (9): Guide d'installation poste entreprise, Clients MCP (Claude Code, Claude Desktop, Codex), Depannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN...), Installation du serveur via uv tool (cynogis-server.exe), Cynogis README, Installation de developpement (dev_setup.py, qgis_env_snippet.py), RAPORT.md, SCR cibles EPSG:2975 (Reunion) / EPSG:4471 (Mayotte) (+1 more)

### Community 74 - "Connection File"
Cohesion: 0.31
Nodes (3): new_token(), remove_connection_file(), write_connection_file()

### Community 75 - "WCAG Contrast"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 76 - "Project Audit Core"
Cohesion: 0.36
Nodes (5): build_sections(), severity_counts(), verdict(), _yes_no(), audit_project()

### Community 77 - "Field Types & Add Features"
Cohesion: 0.22
Nodes (4): field_type_name(), layer_field_types(), add_features(), export_layer()

### Community 79 - "Encoding Detection"
Cohesion: 0.29
Nodes (5): looks_like_mojibake(), check_shapefile(), load_layer(), _mojibake_hint(), test_mojibake()

### Community 80 - "Data Provenance"
Cohesion: 0.36
Nodes (3): Provenance, provenance_from_data(), test_provenance_roundtrip_and_kind_check()

### Community 81 - "Layer Listing"
Cohesion: 0.29
Nodes (4): list_layers(), _summary(), _tree(), _visible()

### Community 82 - "Job Wait Tests"
Cohesion: 0.39
Nodes (6): BridgeResult, FakeClient, test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 83 - "Ecology Workflows Docs"
Cohesion: 0.29
Nodes (7): Ecological impact study workflow (ERC), Ecology referentials (TAXREF, BDC Statuts, HABREF, zonings), Ecology, proximity, stakes and impacts tools, Landscape diagnosis workflow, Closed landscape nomenclature, Coefficients, landscape, terrain tools, Typical AI workflows

### Community 84 - "Editing & Tool Conventions Docs"
Cohesion: 0.40
Nodes (6): Adding a tool (@tool decorator), Edit buffer and JOURNAL (request_commit only writes), Editing tools (buffer then human commit), execute_pyqgis (DESTROY, last resort), Known limits and pending validations, Tool catalog (101 + 4 internal)

### Community 85 - "Confirmation Dialog"
Cohesion: 0.33
Nodes (3): build_details(), make_confirmer(), confirm()

### Community 88 - "Deployment Docs"
Cohesion: 0.40
Nodes (5): Partage reseau \\SERVEUR\Cynogis, Depot QGIS prive (plugins.xml), CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...), metadata.txt (Cynogis Reunion-Mayotte 0.1.0), QGIS 3.38 a 4.99, supportsQt6

### Community 89 - "Business Rules & CRS"
Cohesion: 0.83
Nodes (3): Business rules (CRS, surfaces, no Natura 2000 in DOM), EPSG:2975 La Reunion (RGR92 / UTM 40S), EPSG:4471 Mayotte (RGM04 / UTM 38S)

## Knowledge Gaps
- **18 isolated node(s):** `cynogis-server`, `Clients MCP (Claude Code, Claude Desktop, Codex)`, `CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...)`, `QGIS 3.38 a 4.99, supportsQt6`, `Installation de developpement (dev_setup.py, qgis_env_snippet.py)` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 662 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `Tool Errors` to `Web Services WFS`, `Job Execution Engine`, `Edit Buffer Tools`, `Proximity & Geometry Iteration`, `Plugin Infrastructure`, `Coefficients Computation`, `Dispatcher Core`, `Tool Registry & Field Tools`, `Field Naming Logic`, `Territory Detection`, `Landscape Classification`, `Output Paths & Rasters`, `Impact Quantification`, `Styling Tools`, `Impact Tables & Requests`, `Job Tests`, `Unit Conversion`, `Field Data Import`, `HTTP Fetch Step`, `Layer Source Info`, `Descriptive Stats`, `Pacer & Polygon Parts`, `Permission Policy`, `Bridge Request Handling`, `Isopleths & Density`, `Coefficient & Metric Tools`, `Zoning Assessment`, `Dispatcher Tests`, `Bridge Protocol`, `Bridge TCP Server`, `Param Schema Validation`, `Referentials Directory`, `PDF Report Rendering`, `Pending Edits & Confirmation`, `Layer Info & Map Export`, `Field Types & Add Features`, `Fake Executor Tests`, `Encoding Detection`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 90 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 90 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `Clients MCP (Claude Code, Claude Desktop, Codex)`, `CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...)` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Web Services WFS` be split into smaller, more focused modules?**
  _Cohesion score 0.06533646322378717 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `Tool Errors` to `Web Services WFS`, `Job Execution Engine`, `Edit Buffer Tools`, `Proximity & Geometry Iteration`, `Plugin Infrastructure`, `Coefficients Computation`, `Dispatcher Core`, `Tool Registry & Field Tools`, `Field Naming Logic`, `Territory Detection`, `Landscape Classification`, `Output Paths & Rasters`, `Impact Quantification`, `Styling Tools`, `Impact Tables & Requests`, `Job Tests`, `Unit Conversion`, `Field Data Import`, `HTTP Fetch Step`, `Layer Source Info`, `Descriptive Stats`, `Pacer & Polygon Parts`, `Permission Policy`, `Bridge Request Handling`, `Isopleths & Density`, `Coefficient & Metric Tools`, `Zoning Assessment`, `Dispatcher Tests`, `Bridge Protocol`, `Bridge TCP Server`, `Param Schema Validation`, `Referentials Directory`, `PDF Report Rendering`, `Pending Edits & Confirmation`, `Layer Info & Map Export`, `Field Types & Add Features`, `Fake Executor Tests`, `Encoding Detection`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 137 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 137 INFERRED edges - model-reasoned connections that need verification._
- **Should `Classification Breaks` be split into smaller, more focused modules?**
  _Cohesion score 0.05443371378402107 - nodes in this community are weakly interconnected._