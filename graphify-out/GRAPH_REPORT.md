# Graph Report - cynogis  (2026-11-24)

## Corpus Check
- 166 files · ~137,913 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 3032 nodes · 8996 edges · 138 communities (110 shown, 28 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 944 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4d52c50d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BridgeResult
- tools/webservices.py
- report.py
- common.py
- test_segment_landcover_tool.py
- test_landcover_prepare.py
- test_landcover_persist.py
- Métriques paysagères
- Documentation projet
- _pyqgis_abi.py
- shapefile.py
- test_landcover_segmentation_task.py
- prepare.py
- test_fields.py
- Coefficients de surface
- colors.py
- CynogisPlugin
- core/referentials.py
- editing.py
- feature_request
- JobManager
- test_jobs.py
- collections_abc
- json
- math
- Journal d'édition
- test_dispatcher.py
- FakeExecutor
- compute_breaks
- FakeSocket
- json
- Env
- dev_setup.py
- re
- Résolution des recouvrements
- allocate
- tasks.py
- Catalogue d'algorithmes
- _run
- Distances
- persist.py
- Historique des styles
- core/atlas.py
- HABREF
- Tests de style
- core/stakes.py
- fetch_wfs_layer
- Schéma des paramètres
- logging
- check_surfaces.py
- ToolResult
- Tests zonage
- test_prepare_landcover_tool.py
- PreparationControl
- Feuille de route
- test_landcover_guard.py
- select_ids
- test_landcover_segment.py
- Dispatcher
- ToolError
- run_cleanup_steps
- BridgeServer
- Plan d'échantillonnage
- test_landcover_task_finished.py
- elevation_sample
- Pause
- move_features
- run_qgis_integration.py
- core/zoning.py
- test_detached_landcover_task.py
- run_algorithm
- test_connection.py
- app.py
- CatalogClient
- Guide d'installation
- core/impacts.py
- Règles métier réglementaires
- core/landscape.py
- render_map
- pytest
- find_source_file
- Règles d'architecture
- normalize
- Adding a tool (@tool decorator, Param, docstring)
- QgsVectorLayer
- test_stats_full.py
- bbox_covers
- TaskExecutor
- Commandes de dev
- import_field_data
- Métadonnées plugin
- Liste blanche algorithmes
- Débogage
- Fin de tâche graphify
- Venv vs Python QGIS
- Compatibilité Qt
- Fichiers locaux
- cynogis-server
- test_bridge_lifecycle.py
- Phase 1 : Fiabilite des calculs de surface
- test_terrain.py
- Security rules (no bypass, no overwrite, no sensitive species/cadastral data)
- Phase 3 : Tracabilite et confidentialite
- BridgeError
- install.ps1
- build_plugin.py
- list_style_options
- mentions_natura2000
- ErrorCode
- core/project_audit.py
- Iface
- _finish_detached_job
- _prepare
- to_json_value
- check_geometries
- segment.py
- Recorder
- profile_table
- Zoning
- format_number
- Any
- _surface_factors
- controlled_engine
- Rule
- pyqgis.py
- list_coefficients
- test_stats.py
- FakeBridgeServer
- Provenance
- RefusingTaskManager
- SlicSpy
- client.py
- _alias
- Territory
- _tree
- test_real_module_import_does_not_load_slic

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 238 edges
2. `ErrorCode` - 216 edges
3. `ToolResult` - 112 edges
4. `get_vector_layer()` - 103 edges
5. `feature_request()` - 73 edges
6. `geometry_kind()` - 60 edges
7. `Level` - 57 edges
8. `require_field()` - 56 edges
9. `to_json_value()` - 52 edges
10. `distance_area()` - 51 edges

## Surprising Connections (you probably didn't know these)
- `test_segmentation_control_sans_callback()` --uses--> `SegmentationControl`  [INFERRED]
  tests/unit/test_landcover_execution.py → plugin/cynogis/core/landcover_execution.py
- `test_segmentation_progression_flottante()` --uses--> `SegmentationControl`  [INFERRED]
  tests/unit/test_landcover_execution.py → plugin/cynogis/core/landcover_execution.py
- `test_describe_empty_and_single()` --calls--> `describe()`  [INFERRED]
  tests/unit/test_stats.py → plugin/cynogis/core/stats.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `test_diagnostics_une_seule_graine()` --uses--> `SlicConfig`  [INFERRED]
  tests/integration/test_landcover_persist.py → plugin/cynogis/landcover_processing/segment.py

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Déploiement d'un poste (partage, plugin, serveur, client MCP)** — installation_network_share, installation_private_qgis_repo, installation_uv_tool_install, installation_cynogis_server_exe, installation_mcp_client_setup, installation_verification_ping [EXTRACTED 1.00]
- **Chaîne d'exécution d'un appel MCP** — raport_serveur_mcp_generique, raport_pont_tcp_jsonlines, raport_flux_appel_simple, raport_flux_traitement_long_job, raport_outils_internes [EXTRACTED 1.00]
- **Garde-fous de sécurité Cynogis** — raport_niveaux_permission, raport_confirmation_humaine_destroy, raport_liste_blanche_algorithmes, raport_sorties_jamais_ecrasees, raport_journal_audit, raport_journal_edition, raport_confidentialite_champs_sensibles [EXTRACTED 1.00]
- **Non-negotiable regulatory business rules** — claude_territory_crs, claude_area_measurement_rule, claude_surface_3d_rule, claude_natura2000_exclusion, claude_regulatory_thresholds_config, claude_deterministic_prediagnostic [EXTRACTED 1.00]
- **Regles metier codifiees par la phase 2** — claude_natura2000_exclusion, claude_deterministic_prediagnostic, docs_roadmap_phase2_reglementaire [INFERRED 0.85]
- **Règles métier sur les surfaces et le pré-diagnostic** — raport_surfaces_ellipsoidales, raport_fusion_avant_somme, raport_surface_3d, raport_regulatory_prescan, raport_territoires_reunion_mayotte, raport_natura_2000_exclu [INFERRED 0.85]
- **Fiabilite des surfaces (regles, roadmap 1.1-1.3, helpers)** — docs_roadmap_1_1_reference_tests, docs_roadmap_1_2_forbid_4326, docs_roadmap_1_3_surface_method, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.95]

## Communities (138 total, 28 thin omitted)

### Community 0 - "BridgeResult"
Cohesion: 0.14
Nodes (19): BridgeError, BridgeResult, FakeClient, test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat(), install_client() (+11 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.10
Nodes (28): capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list(), _local() (+20 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "common.py"
Cohesion: 0.13
Nodes (8): unique_field_name(), Level, tool(), decorator(), Param, detect_territory(), Cynogis Plugin Icon (icon.svg), Green Map Location Pin

### Community 4 - "test_segment_landcover_tool.py"
Cohesion: 0.20
Nodes (25): abort_test_process(), environment(), final_response(), done(), guard_free(), params(), patched(), _plain() (+17 more)

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.13
Nodes (24): _crs(), _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs(), progress() (+16 more)

### Community 6 - "test_landcover_persist.py"
Cohesion: 0.08
Nodes (33): _altered_reread(), _analysis_outside_validity(), _edit_manifest(), _failing_close(), _failing_replace(), _implicit_mask(), _manifest(), _other_crs() (+25 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 10 - "shapefile.py"
Cohesion: 0.11
Nodes (16): truncate_field_names(), companion_paths(), export_plan(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), test_truncate_field_names_sans_doublon() (+8 more)

### Community 11 - "test_landcover_segmentation_task.py"
Cohesion: 0.10
Nodes (40): _abort(), _aoi_wkb(), _blocking(), controlled_until_cancelled(), expect_busy(), guard_free(), isolated(), make_dispatcher() (+32 more)

### Community 12 - "prepare.py"
Cohesion: 0.16
Nodes (12): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+4 more)

### Community 13 - "test_fields.py"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+10 more)

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (25): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+17 more)

### Community 15 - "colors.py"
Cohesion: 0.09
Nodes (21): contrast_ratio(), darken(), distinct_colors(), interpolate_ramp(), lighten(), mix(), parse_color(), relative_luminance() (+13 more)

### Community 17 - "core/referentials.py"
Cohesion: 0.11
Nodes (20): check_rules(), _covers(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), _segments(), test_cirad_974_2020_ombre_et_code_inconnu() (+12 more)

### Community 18 - "editing.py"
Cohesion: 0.15
Nodes (13): describe_summary(), is_shapefile(), add_field(), _commit_details(), _delete_field_details(), _editing_layers(), _field_limit(), get_pending_edits() (+5 more)

### Community 19 - "feature_request"
Cohesion: 0.04
Nodes (62): Pacer, get_class(), convert_area(), convert_length(), add_to_memory(), area_m2(), area_method(), dissolved_areas() (+54 more)

### Community 20 - "JobManager"
Cohesion: 0.09
Nodes (6): collecting(), Executor, Job, JobManager, render_notes(), test_cancel_all_continues_after_one_job_fails()

### Community 21 - "test_jobs.py"
Cohesion: 0.06
Nodes (74): PreparationCancelledError, _audited(), boucle(), calcul(), _detached(), effacer(), erreur_avant(), lecture() (+66 more)

### Community 22 - "collections_abc"
Cohesion: 0.10
Nodes (15): validate_colors(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors(), validate_palette() (+7 more)

### Community 23 - "json"
Cohesion: 0.16
Nodes (11): new_token(), remove_connection_file(), write_connection_file(), decode_request(), _protocol_error(), remove_and_release_connection(), _line(), test_decode_invalid() (+3 more)

### Community 24 - "math"
Cohesion: 0.17
Nodes (14): correlate(), correlation_pvalue(), describe(), describe_full(), interpret_shape(), kurtosis(), linear_fit(), pearson() (+6 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "FakeExecutor"
Cohesion: 0.10
Nodes (15): AlgCall, note(), FakeExecutor, job_invalide(), mesure_invalide(), _spy_manager(), generator(), test_apres_detachement_le_finisseur_n_est_plus_appele() (+7 more)

### Community 28 - "compute_breaks"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "FakeSocket"
Cohesion: 0.14
Nodes (9): FakeDispatcher, FakeListener, FakeSocket, make_bridge(), request_line(), test_bridge_no_dispatch_after_stop_request(), test_bridge_socket_failure_does_not_block_others_and_is_retained(), test_bridge_stop_during_handle_line_drops_response_and_next_lines() (+1 more)

### Community 30 - "json"
Cohesion: 0.27
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 32 - "dev_setup.py"
Cohesion: 0.19
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 33 - "re"
Cohesion: 0.06
Nodes (28): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), _columns() (+20 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.10
Nodes (17): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), _as_multipolygon(), _closer_parts(), records() (+9 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "tasks.py"
Cohesion: 0.06
Nodes (14): Fetch, SegmentLandcover, acquire_landcover_guard(), release(), _application(), LandcoverSegmentationTask, LandcoverPreparationTask, _FetchTask (+6 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.14
Nodes (10): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), list_algorithms(), test_liste_blanche(), test_recherche_multi_termes() (+2 more)

### Community 38 - "_run"
Cohesion: 0.10
Nodes (23): _failing_write(), _keep(), _kernel(), _run(), _sha(), _snapshot(), test_double_echec_nettoie_seulement_son_dossier(), test_double_nettoyage_impossible_apres_annulation() (+15 more)

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 40 - "persist.py"
Cohesion: 0.23
Nodes (14): _check(), _dataset(), _diagnostics(), _fingerprints(), _grid(), _load_inputs(), persist_segmentation(), _read_json() (+6 more)

### Community 41 - "Historique des styles"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "core/atlas.py"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.10
Nodes (24): readable_text_color(), build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_readable_text_color() (+16 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.18
Nodes (12): Criterion, level_for(), level_number(), Override, parse_criteria(), parse_overrides(), parse_thresholds(), score() (+4 more)

### Community 46 - "fetch_wfs_layer"
Cohesion: 0.22
Nodes (6): service_label(), _bbox_wgs84(), _cached_source(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "logging"
Cohesion: 0.33
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 49 - "check_surfaces.py"
Cohesion: 0.21
Nodes (5): check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 50 - "ToolResult"
Cohesion: 0.04
Nodes (46): ToolResult, looks_like_mojibake(), _overview_extent(), clean_number(), crs_info(), enum_name(), extent_wgs84(), file_format() (+38 more)

### Community 51 - "Tests zonage"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 52 - "test_prepare_landcover_tool.py"
Cohesion: 0.18
Nodes (27): abort_test_process(), environment(), final_response(), done(), params(), patched(), _plain(), request() (+19 more)

### Community 53 - "PreparationControl"
Cohesion: 0.11
Nodes (17): PreparationControl, _DerivedControl, test_callback_failure_is_not_hidden(), test_cancellation_before_callback(), test_cancellation_check_failure_is_not_hidden(), test_cancellation_requested_during_callback(), progress(), test_default_control_does_nothing() (+9 more)

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "test_landcover_guard.py"
Cohesion: 0.19
Nodes (16): expect_busy(), in_thread(), is_free(), isolated_property(), patched(), step(), test_executor_addtask_refusal_releases_guard(), test_executor_constructor_failure_releases_guard() (+8 more)

### Community 56 - "select_ids"
Cohesion: 0.17
Nodes (12): begin_edit(), refresh_layer(), select_ids(), calculate_field(), _check_count(), delete_features(), _delete_features_details(), delete_field() (+4 more)

### Community 57 - "test_landcover_segment.py"
Cohesion: 0.15
Nodes (27): segment_rgb(), assert_contract(), forbidden_slic(), irregular_mask_with_hole(), raises(), random_rgb(), rng(), slic_replaced() (+19 more)

### Community 58 - "Dispatcher"
Cohesion: 0.07
Nodes (16): Request, Response, Dispatcher, finish(), PermissionPolicy, spec_of(), ToolRegistry, ToolSpec (+8 more)

### Community 59 - "ToolError"
Cohesion: 0.06
Nodes (29): ToolError, WebService, wfs_params(), wms_params(), _project_target(), save_project(), _save_project_details(), _write_csv() (+21 more)

### Community 60 - "run_cleanup_steps"
Cohesion: 0.11
Nodes (6): run_cleanup_steps(), test_cleanup_accepts_empty_sequence(), test_cleanup_collects_multiple_errors(), test_cleanup_continues_after_failure(), test_cleanup_does_not_swallow_process_interruptions(), test_cleanup_executes_every_step_in_order()

### Community 61 - "BridgeServer"
Cohesion: 0.18
Nodes (3): BridgeServer, spin(), test_real_socket_cycle_on_ephemeral_port()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "test_landcover_task_finished.py"
Cohesion: 0.13
Nodes (17): isolated_guard(), make_task(), _obia_job(), tool(), patched(), Recorder, spin(), step() (+9 more)

### Community 64 - "elevation_sample"
Cohesion: 0.22
Nodes (5): _clean(), elevation_sample(), _metric_raster(), _read_window(), _sector_index()

### Community 65 - "Pause"
Cohesion: 0.28
Nodes (6): Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 66 - "move_features"
Cohesion: 0.18
Nodes (9): _change_geometries(), _conform(), _geometries(), _measure(), move_features(), _reference_subset(), _snap(), snap_features() (+1 more)

### Community 67 - "run_qgis_integration.py"
Cohesion: 0.22
Nodes (8): bootstrap(), build_bundle(), command(), _fail(), find_launcher(), isolated_env(), main(), probe()

### Community 68 - "core/zoning.py"
Cohesion: 0.13
Nodes (12): is_natura2000_layer(), assess(), cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, zoning_state() (+4 more)

### Community 69 - "test_detached_landcover_task.py"
Cohesion: 0.14
Nodes (23): PrepareLandcover, PreparationConfig, _crs_wkt(), expect_busy_start(), guard_free(), isolated(), make_obia_dispatcher(), obia() (+15 more)

### Community 70 - "run_algorithm"
Cohesion: 0.16
Nodes (6): _allowed(), describe_algorithm(), run_algorithm(), is_optional(), _run(), run_in_memory()

### Community 71 - "test_connection.py"
Cohesion: 0.18
Nodes (11): conn_file(), _deny_unlink(), test_invalid_json_ignored_by_default(), test_invalid_json_raises_in_strict_mode(), test_missing_file_is_accepted(), test_other_instance_file_is_kept(), test_permission_error_on_delete_is_silent_by_default(), test_permission_error_on_delete_raises_in_strict_mode() (+3 more)

### Community 72 - "app.py"
Cohesion: 0.17
Nodes (7): call_tool(), _cancel_and_observe(), _fetch_specs(), list_tools(), _progress_token(), _to_tool(), _wait_job()

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "core/impacts.py"
Cohesion: 0.17
Nodes (9): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), test_anneaux(), test_comparaison_variantes(), test_poids_enjeu() (+1 more)

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "core/landscape.py"
Cohesion: 0.08
Nodes (20): classes_for(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match(), suggest_mapping() (+12 more)

### Community 78 - "render_map"
Cohesion: 0.18
Nodes (3): render_map(), _overview_map(), _project_facts()

### Community 79 - "pytest"
Cohesion: 0.07
Nodes (37): LandcoverConfig, resolve_output_parent(), _validate_number(), validate_rgb_bands(), _alias(), root(), test_config_is_immutable(), test_config_is_json_serializable() (+29 more)

### Community 80 - "find_source_file"
Cohesion: 0.12
Nodes (10): find_source_file(), referentials_directory(), Source, sources_for(), list_reference_sources(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file() (+2 more)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "normalize"
Cohesion: 0.18
Nodes (7): apply_mapping(), normalize(), to_ascii(), test_apply_mapping_insensible_aux_accents(), test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "QgsVectorLayer"
Cohesion: 0.18
Nodes (6): field_type_name(), geometry_from_wkt(), layer_field_types(), wkt_to_layer_crs(), add_features(), _field_kind()

### Community 85 - "test_stats_full.py"
Cohesion: 0.17
Nodes (8): ranks(), weighted_stats(), test_describe_full_shape(), test_empty(), test_outlier_detected(), test_ranks_ties(), test_sensitive(), test_weighted_median()

### Community 86 - "bbox_covers"
Cohesion: 0.50
Nodes (3): bbox_covers(), should_replace_cache(), test_bbox_rules()

### Community 89 - "import_field_data"
Cohesion: 0.18
Nodes (4): crs_from_text(), import_field_data(), _read(), create_layer()

### Community 99 - "test_bridge_lifecycle.py"
Cohesion: 0.16
Nodes (21): critical(), fake_remove(), fake_write(), patched(), plugin_env(), pushes(), raises(), RecordingJobs (+13 more)

### Community 101 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 102 - "test_terrain.py"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 103 - "Security rules (no bypass, no overwrite, no sensitive species/cadastral data)"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 104 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

### Community 105 - "BridgeError"
Cohesion: 0.29
Nodes (4): main(), QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 107 - "build_plugin.py"
Cohesion: 0.24
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 108 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 109 - "mentions_natura2000"
Cohesion: 0.31
Nodes (5): mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 110 - "ErrorCode"
Cohesion: 0.04
Nodes (52): ErrorCode, clean_name(), unique_path(), export_atlas_pdf(), _from_template(), expression_context(), get_layer(), get_vector_layer() (+44 more)

### Community 111 - "core/project_audit.py"
Cohesion: 0.15
Nodes (23): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+15 more)

### Community 113 - "_finish_detached_job"
Cohesion: 0.24
Nodes (8): DetachedJobOutcome, _detail_text(), _finish_detached_job(), test_outcome_annulation_tardive_conserve_le_repertoire(), test_outcome_details_de_l_erreur_principale_prioritaires(), test_outcome_rejette_les_chemins_non_textuels(), test_outcome_repli_sur_le_resultat(), test_outcome_runtime_error_causee_par_tool_error()

### Community 114 - "_prepare"
Cohesion: 0.28
Nodes (6): _full_aoi(), islands(), _islands_mask(), _prepare(), sample(), _texture()

### Community 115 - "to_json_value"
Cohesion: 0.09
Nodes (15): compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), overlap_warning() (+7 more)

### Community 116 - "check_geometries"
Cohesion: 0.29
Nodes (3): check_geometries(), _error_kind(), geometry_report()

### Community 117 - "segment.py"
Cohesion: 0.22
Nodes (4): _positive_float(), SlicConfig, test_config_defaults_are_normalised_floats(), _DerivedSlic

### Community 118 - "Recorder"
Cohesion: 0.10
Nodes (11): SegmentationCancelledError, SegmentationControl, Recorder, test_double_annulation_initiale_sans_lecture(), test_double_annulation_tardive_apres_99(), test_double_slic_annule_puis_echoue(), test_double_slic_demande_l_annulation(), test_real_annulation_a_99_supprime_le_temporaire() (+3 more)

### Community 119 - "profile_table"
Cohesion: 0.12
Nodes (11): is_sensitive_field(), mask_sensitive(), sensitive_fields(), correlation_pairs(), to_float(), correlation_matrix(), _is_empty(), profile_table() (+3 more)

### Community 120 - "Zoning"
Cohesion: 0.18
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_root_env_override()

### Community 121 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 122 - "Any"
Cohesion: 0.33
Nodes (3): describe_categorical(), describe_groups(), test_categorical_entropy()

### Community 123 - "_surface_factors"
Cohesion: 0.33
Nodes (3): _pixel_labels(), _slope_aspect(), _surface_factors()

### Community 124 - "controlled_engine"
Cohesion: 0.33
Nodes (3): controlled_engine(), quick_engine(), engine()

### Community 126 - "pyqgis.py"
Cohesion: 0.08
Nodes (12): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+4 more)

### Community 128 - "test_stats.py"
Cohesion: 0.33
Nodes (4): test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 130 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 986 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `common.py`, `test_segment_landcover_tool.py`, `test_landcover_segmentation_task.py`, `editing.py`, `feature_request`, `JobManager`, `test_jobs.py`, `json`, `test_dispatcher.py`, `FakeExecutor`, `tasks.py`, `fetch_wfs_layer`, `Schéma des paramètres`, `ToolResult`, `test_prepare_landcover_tool.py`, `test_landcover_guard.py`, `select_ids`, `Dispatcher`, `run_cleanup_steps`, `BridgeServer`, `test_landcover_task_finished.py`, `elevation_sample`, `move_features`, `test_detached_landcover_task.py`, `run_algorithm`, `render_map`, `find_source_file`, `QgsVectorLayer`, `import_field_data`, `test_bridge_lifecycle.py`, `ErrorCode`, `_finish_detached_job`, `to_json_value`, `check_geometries`, `profile_table`, `pyqgis.py`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Are the 115 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 115 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `BridgeResult` be split into smaller, more focused modules?**
  _Cohesion score 0.14039408866995073 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `common.py`, `test_segment_landcover_tool.py`, `test_landcover_segmentation_task.py`, `editing.py`, `feature_request`, `JobManager`, `test_jobs.py`, `json`, `test_dispatcher.py`, `FakeExecutor`, `tasks.py`, `Schéma des paramètres`, `ToolResult`, `test_prepare_landcover_tool.py`, `test_landcover_guard.py`, `select_ids`, `Dispatcher`, `ToolError`, `run_cleanup_steps`, `BridgeServer`, `test_landcover_task_finished.py`, `elevation_sample`, `move_features`, `test_detached_landcover_task.py`, `run_algorithm`, `render_map`, `find_source_file`, `QgsVectorLayer`, `import_field_data`, `test_bridge_lifecycle.py`, `_finish_detached_job`, `to_json_value`, `check_geometries`, `profile_table`, `pyqgis.py`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 173 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 173 INFERRED edges - model-reasoned connections that need verification._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09856035437430787 - nodes in this community are weakly interconnected._