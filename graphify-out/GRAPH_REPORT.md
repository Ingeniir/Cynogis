# Graph Report - cynogis  (2026-11-05)

## Corpus Check
- 137 files · ~101,813 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2116 nodes · 6408 edges · 109 communities (85 shown, 24 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 517 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `06556fda`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- common.py
- Shapefiles et encodage
- Serveur MCP stdio
- ToolError
- get_vector_layer
- test_fields.py
- metrics.py
- Coefficients (cœur)
- Feuille de route Cynogis
- common.py
- Données de terrain
- HABREF
- app.py
- math
- BridgeServer
- export.py
- run_to_project
- test_jobs.py
- _clipped
- core/stakes.py
- EditJournal
- test_terrain.py
- elevation_sample
- ErrorCode
- Métriques paysagères
- classify.py
- check_surfaces.py
- Territory
- Exécuteur factice
- TAXREF
- list_coefficients
- test_fields.py (2)
- Point d'entrée du plugin
- Feuille de route
- palettes.py
- find_source_file
- classify.py (2)
- get_vector_layer
- to_float
- core/project_audit.py (2)
- tasks.py
- Construction du ZIP
- protocol.py
- tasks.py
- Historique des styles
- get_vector_layer (2)
- Installation développeur
- dev_setup.py
- naming.py
- Journal d'audit
- Modèle de sécurité (à ne jamais contourner)
- Requêtes WFS
- get_vector_layer (3)
- tasks.py (2)
- FakeExecutor
- core/landscape.py
- ToolRegistry
- Dispatcher
- test_stats.py
- _closer_parts
- core/terrain.py
- build_plugin.py
- audit_project
- core/sampling.py
- classes_for
- AuditLog
- core/sampling.py (2)
- BridgeServer
- get_vector_layer (4)
- Provenance
- Règles réglementaires
- degrees_to_percent
- Adding a tool (@tool decorator, Param, docstring)
- common.py (2)
- Rapport des fonctionnalités
- contrast_ratio
- get_palette
- Phase 1 : Fiabilite des calculs de surface
- EditJournal (2)
- pathlib
- _overlay
- format_number
- Security rules (no bypass, no overwrite, no sensitive species/cadastral data)
- units.py
- core/zoning.py
- Phase 2 : Robustesse reglementaire (pre-diagnostic)
- get_vector_layer (5)
- Phase 1 : Fiabilite des calculs de surface
- tools/habref.py
- metadata.txt (Cynogis Reunion-Mayotte 0.1.0)
- Contraintes core et compat Qt
- Contrôle de code PyQGIS (2)
- Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])
- End of task: graphify update and graphify-out commit
- Python 3.14 venv vs QGIS Python 3.12
- Qt5/Qt6 compatibility via compat.py (QGIS 3.x and 4.x)
- export.py (2)
- Adding a tool (@tool decorator, Param, docstring)
- Phase 3 : Tracabilite et confidentialite
- test_naming.py
- CoefficientSpec
- _isopleth_geometries
- needs_priority_field
- Cynogis Plugin Icon (icon.svg)
- _is_empty

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
- `test_describe_empty_and_single()` --calls--> `describe()`  [INFERRED]
  tests/unit/test_stats.py → plugin/cynogis/core/stats.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `2.3 Exclure Natura 2000` --semantically_similar_to--> `Natura 2000 not applicable in overseas departments`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `2.6 Pre-diagnostic 100 % deterministe` --semantically_similar_to--> `Deterministic pre-diagnostic, never LLM-written`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `3.4 Audit des garde-fous` --semantically_similar_to--> `Security rules (no bypass, no overwrite, no sensitive species/cadastral data)`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Déploiement d'un poste (partage, plugin, serveur, client MCP)** — installation_network_share, installation_private_qgis_repo, installation_uv_tool_install, installation_cynogis_server_exe, installation_mcp_client_setup, installation_verification_ping [EXTRACTED 1.00]
- **Garde-fous de sécurité Cynogis** — raport_permission_levels, raport_human_confirmation, raport_algorithm_whitelist, raport_no_overwrite_outputs, raport_audit_log, raport_edit_journal, raport_privacy_masking, raport_restricted_network [EXTRACTED 1.00]
- **Non-negotiable regulatory business rules** — claude_territory_crs, claude_area_measurement_rule, claude_surface_3d_rule, claude_natura2000_exclusion, claude_regulatory_thresholds_config, claude_deterministic_prediagnostic [EXTRACTED 1.00]
- **Regles metier codifiees par la phase 2** — claude_natura2000_exclusion, claude_deterministic_prediagnostic, docs_roadmap_phase2_reglementaire [INFERRED 0.85]
- **Règles métier réglementaires (surfaces, 3D, Natura 2000, territoires)** — raport_surface_rules, raport_surface_3d, raport_natura2000_exclusion, raport_territories, raport_regulatory_prescan [INFERRED 0.85]
- **Fiabilite des surfaces (regles, roadmap 1.1-1.3, helpers)** — docs_roadmap_1_1_reference_tests, docs_roadmap_1_2_forbid_4326, docs_roadmap_1_3_surface_method, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.95]

## Communities (109 total, 24 thin omitted)

### Community 0 - "common.py"
Cohesion: 0.06
Nodes (47): Fetch, is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs() (+39 more)

### Community 1 - "Shapefiles et encodage"
Cohesion: 0.09
Nodes (8): Executor, Job, JobManager, Pause, run_now(), test_run_now(), algo(), steps()

### Community 2 - "Serveur MCP stdio"
Cohesion: 0.10
Nodes (19): to_float(), convert_length(), _collect(), count_observations(), count_points_in_polygon(), distance_layer(), _distance_m(), distance_matrix() (+11 more)

### Community 3 - "ToolError"
Cohesion: 0.07
Nodes (31): ToolResult, ToolError, clean_name(), unique_path(), export_atlas_pdf(), _from_template(), prepare_expression(), _output_path() (+23 more)

### Community 4 - "get_vector_layer"
Cohesion: 0.06
Nodes (51): Pacer, compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of() (+43 more)

### Community 5 - "test_fields.py"
Cohesion: 0.06
Nodes (27): companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), file_format() (+19 more)

### Community 6 - "metrics.py"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 7 - "Coefficients (cœur)"
Cohesion: 0.11
Nodes (20): _covers(), map_cirad(), map_feature(), map_ocsge(), Rule, _segments(), Source, sources_for() (+12 more)

### Community 8 - "Feuille de route Cynogis"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 9 - "common.py"
Cohesion: 0.10
Nodes (11): unique_field_name(), Level, Param, detect_territory(), crs_from_text(), make_field(), import_field_data(), save_to_project() (+3 more)

### Community 10 - "Données de terrain"
Cohesion: 0.12
Nodes (15): darken(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), test_interpolate_ramp_extremites_conservees() (+7 more)

### Community 11 - "HABREF"
Cohesion: 0.11
Nodes (24): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), _ratio() (+16 more)

### Community 12 - "app.py"
Cohesion: 0.07
Nodes (22): QgsLogHandler, setup_logging(), teardown_logging(), main(), call_tool(), _fetch_specs(), list_tools(), _progress_token() (+14 more)

### Community 13 - "math"
Cohesion: 0.09
Nodes (27): correlate(), correlation_pairs(), correlation_pvalue(), describe(), describe_categorical(), describe_full(), describe_groups(), interpret_shape() (+19 more)

### Community 14 - "BridgeServer"
Cohesion: 0.16
Nodes (3): Response, BridgeServer, test_response_encode_job_id()

### Community 15 - "export.py"
Cohesion: 0.10
Nodes (12): to_json_value(), export_table(), _project_target(), save_project(), _save_project_details(), _write_csv(), _read(), habitat_typology_join() (+4 more)

### Community 16 - "run_to_project"
Cohesion: 0.09
Nodes (16): _allowed(), describe_algorithm(), run_algorithm(), buffer(), dissolve(), extract(), fix_geometries(), _name() (+8 more)

### Community 17 - "test_jobs.py"
Cohesion: 0.11
Nodes (25): AlgCall, app(), boucle(), calcul(), effacer(), erreur_avant(), lecture(), make() (+17 more)

### Community 18 - "_clipped"
Cohesion: 0.14
Nodes (7): find_source_file(), referentials_directory(), _clipped(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 19 - "core/stakes.py"
Cohesion: 0.08
Nodes (22): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+14 more)

### Community 20 - "EditJournal"
Cohesion: 0.11
Nodes (22): build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees() (+14 more)

### Community 21 - "test_terrain.py"
Cohesion: 0.21
Nodes (8): aspect_sector(), distribution(), slope_class(), test_aspect_sector(), test_aspect_sector_plat(), test_distribution(), test_slope_class(), test_slope_class_negative()

### Community 22 - "elevation_sample"
Cohesion: 0.15
Nodes (9): _isopleths(), _style(), _clean(), elevation_sample(), _pixel_labels(), _read_window(), _sector_index(), _slope_aspect() (+1 more)

### Community 23 - "ErrorCode"
Cohesion: 0.05
Nodes (40): ErrorCode, tool(), _overview_extent(), clean_number(), crs_info(), enum_name(), extent_wgs84(), get_layer() (+32 more)

### Community 24 - "Métriques paysagères"
Cohesion: 0.10
Nodes (21): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+13 more)

### Community 25 - "classify.py"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 26 - "check_surfaces.py"
Cohesion: 0.17
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 28 - "Exécuteur factice"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 29 - "TAXREF"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 31 - "test_fields.py (2)"
Cohesion: 0.10
Nodes (20): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), truncate_field_names(), test_coerce_record_champ_inconnu_strict() (+12 more)

### Community 32 - "Point d'entrée du plugin"
Cohesion: 0.14
Nodes (11): parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo(), test_colonnes_terrain() (+3 more)

### Community 33 - "Feuille de route"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 34 - "palettes.py"
Cohesion: 0.11
Nodes (12): distinct_colors(), validate_colors(), with_alpha(), landscape_palette(), register_palette(), resolve_colors(), validate_palette(), test_distinct_colors_sans_doublon() (+4 more)

### Community 35 - "find_source_file"
Cohesion: 0.12
Nodes (15): column_key(), _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses (+7 more)

### Community 36 - "classify.py (2)"
Cohesion: 0.16
Nodes (14): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus(), test_half_plane_contient_le_milieu_cote_a() (+6 more)

### Community 37 - "get_vector_layer"
Cohesion: 0.16
Nodes (12): begin_edit(), refresh_layer(), select_ids(), calculate_field(), _check_count(), delete_features(), _delete_features_details(), delete_field() (+4 more)

### Community 38 - "to_float"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 39 - "core/project_audit.py (2)"
Cohesion: 0.16
Nodes (22): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+14 more)

### Community 40 - "tasks.py"
Cohesion: 0.10
Nodes (6): _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers()

### Community 41 - "Construction du ZIP"
Cohesion: 0.16
Nodes (8): cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, regulatory_prescan(), test_cache_meta_roundtrip_and_matching(), test_par_territoire()

### Community 42 - "protocol.py"
Cohesion: 0.22
Nodes (7): decode_request(), _protocol_error(), _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 43 - "tasks.py"
Cohesion: 0.09
Nodes (18): Box, layout_boxes(), page_size(), correspond(), Habitat, _index(), load_correspondences(), load_typology() (+10 more)

### Community 44 - "Historique des styles"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 45 - "get_vector_layer (2)"
Cohesion: 0.18
Nodes (9): _change_geometries(), _conform(), _geometries(), _measure(), move_features(), _reference_subset(), _snap(), snap_features() (+1 more)

### Community 46 - "Installation développeur"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 47 - "dev_setup.py"
Cohesion: 0.23
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 48 - "naming.py"
Cohesion: 0.19
Nodes (5): to_ascii(), is_sensitive_field(), mask_sensitive(), test_mask_sensitive_hides_only_sensitive_values(), test_sensitive()

### Community 49 - "Journal d'audit"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 50 - "Modèle de sécurité (à ne jamais contourner)"
Cohesion: 0.06
Nodes (43): Cynogis (CLAUDE.md working rules), scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Fichiers propres au poste (connection.json, tools_cache.json, audit/) (+35 more)

### Community 51 - "Requêtes WFS"
Cohesion: 0.16
Nodes (3): remove_connection_file(), classFactory(), CynogisPlugin

### Community 52 - "get_vector_layer (3)"
Cohesion: 0.18
Nodes (10): describe_summary(), _commit_details(), _delete_field_details(), _editing_layers(), get_pending_edits(), _merge_details(), request_commit(), rollback_edits() (+2 more)

### Community 53 - "tasks.py (2)"
Cohesion: 0.27
Nodes (5): service_label(), _bbox_wgs84(), _cached_source(), Source, _sources()

### Community 54 - "FakeExecutor"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 55 - "core/landscape.py"
Cohesion: 0.09
Nodes (17): apply_mapping(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+9 more)

### Community 56 - "ToolRegistry"
Cohesion: 0.13
Nodes (8): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 57 - "Dispatcher"
Cohesion: 0.18
Nodes (5): Request, Dispatcher, finish(), collecting(), render_notes()

### Community 58 - "test_stats.py"
Cohesion: 0.40
Nodes (3): test_describe_basic(), test_describe_empty_and_single(), test_to_float()

### Community 60 - "core/terrain.py"
Cohesion: 0.22
Nodes (4): altitude_band(), parse_bands(), SlopeClass, test_tranches_altitude()

### Community 61 - "build_plugin.py"
Cohesion: 0.22
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 62 - "audit_project"
Cohesion: 0.13
Nodes (7): render_map(), write_document(), write_pdf(), audit_project(), _open_project(), _overview_map(), _project_facts()

### Community 63 - "core/sampling.py"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 64 - "classes_for"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 65 - "AuditLog"
Cohesion: 0.25
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 66 - "core/sampling.py (2)"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 67 - "BridgeServer"
Cohesion: 0.24
Nodes (5): cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_root_env_override()

### Community 68 - "get_vector_layer (4)"
Cohesion: 0.22
Nodes (6): expression_context(), geometry_from_wkt(), is_shapefile(), wkt_to_layer_crs(), add_field(), _field_limit()

### Community 69 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 70 - "Règles réglementaires"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 71 - "degrees_to_percent"
Cohesion: 0.22
Nodes (7): degrees_to_percent(), percent_to_degrees(), reclass_table(), test_conversion_pente_aller_retour(), test_pente_45_degres_vaut_cent_pourcent(), test_reclass_table_degres(), test_reclass_table_pourcentage()

### Community 72 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.22
Nodes (5): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471, 2.6 Pre-diagnostic 100 % deterministe

### Community 73 - "common.py (2)"
Cohesion: 0.31
Nodes (5): mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 74 - "Rapport des fonctionnalités"
Cohesion: 0.40
Nodes (3): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, ~/.cynogis/tools_cache.json catalogue cache

### Community 75 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 76 - "get_palette"
Cohesion: 0.22
Nodes (6): all_palettes(), get_palette(), load_user_palettes(), test_get_palette_etiree(), test_get_palette_inconnue(), test_load_user_palettes_ignore_les_erreurs()

### Community 77 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 78 - "EditJournal (2)"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 80 - "_overlay"
Cohesion: 0.29
Nodes (3): is_agricultural(), _overlay(), test_is_agricultural()

### Community 81 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 82 - "Security rules (no bypass, no overwrite, no sensitive species/cadastral data)"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 83 - "units.py"
Cohesion: 0.47
Nodes (3): convert_area(), test_conversions(), test_unknown_unit()

### Community 84 - "core/zoning.py"
Cohesion: 0.24
Nodes (5): assess(), bbox_covers(), should_replace_cache(), zoning_state(), test_bbox_rules()

### Community 85 - "Phase 2 : Robustesse reglementaire (pre-diagnostic)"
Cohesion: 0.40
Nodes (4): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 86 - "get_vector_layer (5)"
Cohesion: 0.25
Nodes (4): field_type_name(), layer_field_types(), add_features(), _field_kind()

### Community 102 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

### Community 103 - "test_naming.py"
Cohesion: 0.50
Nodes (3): test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

## Knowledge Gaps
- **34 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Add-a-tool example (README)`, `Territoires Réunion EPSG:2975 / Mayotte EPSG:4471`, `Security summary (levels, whitelist, 127.0.0.1 token, audit)` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 728 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `common.py`, `Shapefiles et encodage`, `Serveur MCP stdio`, `get_vector_layer`, `common.py`, `BridgeServer`, `export.py`, `run_to_project`, `test_jobs.py`, `_clipped`, `elevation_sample`, `ErrorCode`, `Exécuteur factice`, `Feuille de route`, `get_vector_layer`, `tasks.py`, `protocol.py`, `get_vector_layer (2)`, `get_vector_layer (3)`, `tasks.py (2)`, `FakeExecutor`, `ToolRegistry`, `Dispatcher`, `audit_project`, `get_vector_layer (4)`, `get_vector_layer (5)`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 94 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Add-a-tool example (README)` to the rest of the system?**
  _34 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05600722673893405 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `common.py`, `Shapefiles et encodage`, `Serveur MCP stdio`, `ToolError`, `get_vector_layer`, `common.py`, `BridgeServer`, `export.py`, `run_to_project`, `test_jobs.py`, `_clipped`, `elevation_sample`, `Exécuteur factice`, `Feuille de route`, `get_vector_layer`, `tasks.py`, `protocol.py`, `get_vector_layer (2)`, `get_vector_layer (3)`, `FakeExecutor`, `ToolRegistry`, `Dispatcher`, `audit_project`, `get_vector_layer (4)`, `get_vector_layer (5)`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Are the 142 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 142 INFERRED edges - model-reasoned connections that need verification._
- **Should `Shapefiles et encodage` be split into smaller, more focused modules?**
  _Cohesion score 0.09365079365079365 - nodes in this community are weakly interconnected._