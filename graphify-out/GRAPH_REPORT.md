# Graph Report - cynogis  (2026-11-24)

## Corpus Check
- 168 files · ~141,676 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 3081 nodes · 9127 edges · 140 communities (119 shown, 21 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 945 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7e637e35`
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
- stats.py
- Journal d'édition
- test_dispatcher.py
- FakeExecutor
- compute_breaks
- FakeSocket
- json
- test_object_features.py
- dev_setup.py
- core/fielddata.py
- Résolution des recouvrements
- allocate
- ProcessingExecutor
- Catalogue d'algorithmes
- test_double_rmtree_en_echec
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
- tools/terrain.py
- AlgCall
- collections_abc
- run_qgis_integration.py
- core/zoning.py
- test_detached_landcover_task.py
- get_vector_layer
- test_connection.py
- app.py
- BridgeResult
- Guide d'installation
- core/impacts.py
- Règles métier réglementaires
- normalize
- render_map
- pytest
- find_source_file
- Règles d'architecture
- style.py
- Adding a tool (@tool decorator, Param, docstring)
- QgsVectorLayer
- math
- core/zoning.py
- TaskExecutor
- Commandes de dev
- test_landscape.py
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
- styling.py
- core/project_audit.py
- Iface
- core/taxref.py
- _prepare
- _segmentation_manager
- .dispatch
- segment.py
- Recorder
- require_field
- Zoning
- format_number
- to_float
- _rewrite
- PreparationConfig
- Rule
- pyqgis.py
- list_coefficients
- _status
- FakeBridgeServer
- Provenance
- RefusingTaskManager
- open_table
- connection.py
- SegmentLandcover
- parse_number
- make_confirmer
- test_real_module_import_does_not_load_slic
- units.py
- ndvi_deviation

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
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `test_diagnostics_une_seule_graine()` --uses--> `SlicConfig`  [INFERRED]
  tests/integration/test_landcover_persist.py → plugin/cynogis/landcover_processing/segment.py
- `test_diagnostics_valeurs_connues()` --uses--> `SlicConfig`  [INFERRED]
  tests/integration/test_landcover_persist.py → plugin/cynogis/landcover_processing/segment.py
- `3.4 Audit des garde-fous` --semantically_similar_to--> `Security rules (no bypass, no overwrite, no sensitive species/cadastral data)`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md

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

## Communities (140 total, 21 thin omitted)

### Community 0 - "BridgeResult"
Cohesion: 0.22
Nodes (10): install_client(), ScriptedClient, test_bridge_failure_does_not_confirm_stop(), test_cancel_waits_for_final_confirmation(), test_cleanup_error_is_not_reported_as_clean_cancellation(), test_job_completed_before_cancellation_took_effect(), test_late_cancellation_preserves_output_details(), test_timeout_preserves_cleanup_error_without_claiming_cancellation() (+2 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.06
Nodes (43): Fetch, is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs() (+35 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "common.py"
Cohesion: 0.10
Nodes (11): Level, tool(), decorator(), Param, mentions_natura2000(), Cynogis Plugin Icon (icon.svg), Green Map Location Pin, overlap_warning() (+3 more)

### Community 4 - "test_segment_landcover_tool.py"
Cohesion: 0.11
Nodes (31): abort_test_process(), _alias(), controlled_engine(), Env, environment(), final_response(), done(), guard_free() (+23 more)

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.13
Nodes (24): _crs(), _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs(), progress() (+16 more)

### Community 6 - "test_landcover_persist.py"
Cohesion: 0.06
Nodes (40): _altered_reread(), _edit_manifest(), _failing_close(), _failing_replace(), _kernel(), _manifest(), _other_crs(), _read_segments() (+32 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "_pyqgis_abi.py"
Cohesion: 0.21
Nodes (3): foreign_pyqgis_reason(), skip_if_foreign_pyqgis(), test_versions_aligned()

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
Cohesion: 0.08
Nodes (23): contrast_ratio(), darken(), distinct_colors(), interpolate_ramp(), lighten(), mix(), relative_luminance(), to_hex() (+15 more)

### Community 16 - "CynogisPlugin"
Cohesion: 0.13
Nodes (4): classFactory(), CynogisPlugin, spin(), test_real_socket_cycle_on_ephemeral_port()

### Community 17 - "core/referentials.py"
Cohesion: 0.11
Nodes (21): _covers(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), _segments(), Source, sources_for() (+13 more)

### Community 18 - "editing.py"
Cohesion: 0.13
Nodes (14): describe_summary(), is_shapefile(), add_field(), _commit_details(), _delete_field_details(), _editing_layers(), _field_limit(), get_pending_edits() (+6 more)

### Community 19 - "feature_request"
Cohesion: 0.04
Nodes (66): unique_field_name(), Pacer, convert_length(), compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer() (+58 more)

### Community 20 - "JobManager"
Cohesion: 0.11
Nodes (5): Executor, Job, JobManager, test_jobmanager_double_finalization_error_fails_job(), test_cancel_all_continues_after_one_job_fails()

### Community 21 - "test_jobs.py"
Cohesion: 0.09
Nodes (49): PreparationCancelledError, _audited(), boucle(), calcul(), effacer(), erreur_avant(), lecture(), make() (+41 more)

### Community 22 - "collections_abc"
Cohesion: 0.14
Nodes (9): all_palettes(), get_palette(), load_user_palettes(), register_palette(), validate_palette(), test_get_palette_etiree(), test_get_palette_inconnue(), test_load_user_palettes_ignore_les_erreurs() (+1 more)

### Community 23 - "json"
Cohesion: 0.32
Nodes (7): decode_request(), _protocol_error(), _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "stats.py"
Cohesion: 0.22
Nodes (9): correlate(), correlation_pvalue(), linear_fit(), pearson(), _r(), ranks(), strength(), test_pearson_and_spearman() (+1 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "FakeExecutor"
Cohesion: 0.11
Nodes (10): note(), spec_of(), FakeExecutor, job_invalide(), mesure_invalide(), test_echec_de_fermeture_detache_reste_un_echec_technique(), generator(), test_job_lance_pendant_la_confirmation() (+2 more)

### Community 28 - "compute_breaks"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "FakeSocket"
Cohesion: 0.14
Nodes (9): FakeDispatcher, FakeListener, FakeSocket, make_bridge(), request_line(), test_bridge_no_dispatch_after_stop_request(), test_bridge_socket_failure_does_not_block_others_and_is_retained(), test_bridge_stop_during_handle_line_drops_response_and_next_lines() (+1 more)

### Community 30 - "json"
Cohesion: 0.27
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "test_object_features.py"
Cohesion: 0.10
Nodes (35): _adjacency(), extract_object_features(), ObjectFeatures, _pixel_area(), assert_invariants(), assert_matches_oracle(), _FloatSubclass, _IntSubclass (+27 more)

### Community 32 - "dev_setup.py"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 33 - "core/fielddata.py"
Cohesion: 0.16
Nodes (8): column_key(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo(), test_colonnes_terrain(), test_read_csv_point_virgule_cp1252(), test_standardize_signale_les_valeurs_illisibles()

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.10
Nodes (17): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), _as_multipolygon(), _closer_parts(), records() (+9 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "ProcessingExecutor"
Cohesion: 0.11
Nodes (8): LandcoverSegmentationTask, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, forget(), _take_layers()

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.14
Nodes (10): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), list_algorithms(), test_liste_blanche(), test_recherche_multi_termes() (+2 more)

### Community 38 - "test_double_rmtree_en_echec"
Cohesion: 0.50
Nodes (3): _failing_write(), test_double_rmtree_en_echec(), blocked()

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 40 - "persist.py"
Cohesion: 0.25
Nodes (13): _check(), _dataset(), _fingerprints(), _grid(), _load_inputs(), persist_segmentation(), _read_json(), _read_raster() (+5 more)

### Community 41 - "Historique des styles"
Cohesion: 0.15
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "core/atlas.py"
Cohesion: 0.17
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.16
Nodes (16): build_categories(), normalize_geometry(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees(), test_build_categories_lignes_colorees(), test_build_categories_sans_value(), test_history_pop_vide() (+8 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.18
Nodes (12): Criterion, level_for(), level_number(), Override, parse_criteria(), parse_overrides(), parse_thresholds(), score() (+4 more)

### Community 46 - "fetch_wfs_layer"
Cohesion: 0.15
Nodes (8): service_label(), _bbox_wgs84(), _cached_source(), _local_source(), _only_fields(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "logging"
Cohesion: 0.20
Nodes (5): QgsLogHandler, setup_logging(), teardown_logging(), run(), main()

### Community 49 - "check_surfaces.py"
Cohesion: 0.17
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 50 - "ToolResult"
Cohesion: 0.04
Nodes (44): ToolResult, looks_like_mojibake(), detect_territory(), Territory, _overview_extent(), clean_number(), crs_from_text(), crs_info() (+36 more)

### Community 51 - "Tests zonage"
Cohesion: 0.18
Nodes (6): getfeature_url(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 52 - "test_prepare_landcover_tool.py"
Cohesion: 0.13
Nodes (29): abort_test_process(), Env, environment(), final_response(), done(), make_geotiff(), params(), patched() (+21 more)

### Community 53 - "PreparationControl"
Cohesion: 0.10
Nodes (17): PreparationControl, SegmentationControl, _DerivedControl, test_callback_failure_is_not_hidden(), test_cancellation_before_callback(), test_cancellation_check_failure_is_not_hidden(), test_cancellation_requested_during_callback(), progress() (+9 more)

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "test_landcover_guard.py"
Cohesion: 0.18
Nodes (16): expect_busy(), in_thread(), is_free(), isolated_property(), patched(), step(), test_executor_addtask_refusal_releases_guard(), test_executor_constructor_failure_releases_guard() (+8 more)

### Community 56 - "select_ids"
Cohesion: 0.12
Nodes (20): begin_edit(), refresh_layer(), select_ids(), calculate_field(), _change_geometries(), _check_count(), _conform(), delete_features() (+12 more)

### Community 57 - "test_landcover_segment.py"
Cohesion: 0.13
Nodes (28): segment_rgb(), assert_contract(), forbidden_slic(), irregular_mask_with_hole(), raises(), random_rgb(), rng(), slic_replaced() (+20 more)

### Community 58 - "Dispatcher"
Cohesion: 0.21
Nodes (4): Dispatcher, PermissionPolicy, ToolRegistry, ToolSpec

### Community 59 - "ToolError"
Cohesion: 0.04
Nodes (42): ErrorCode, ToolError, DetachedJobOutcome, _detail_text(), _finish_detached_job(), clean_name(), unique_path(), export_atlas_pdf() (+34 more)

### Community 60 - "run_cleanup_steps"
Cohesion: 0.14
Nodes (6): run_cleanup_steps(), test_cleanup_accepts_empty_sequence(), test_cleanup_collects_multiple_errors(), test_cleanup_continues_after_failure(), test_cleanup_does_not_swallow_process_interruptions(), test_cleanup_executes_every_step_in_order()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.25
Nodes (3): _Sampler, _segment(), _systematic()

### Community 63 - "test_landcover_task_finished.py"
Cohesion: 0.14
Nodes (16): isolated_guard(), make_task(), _obia_job(), tool(), patched(), Recorder, spin(), step() (+8 more)

### Community 64 - "tools/terrain.py"
Cohesion: 0.12
Nodes (14): get_raster_layer(), classify_slope(), _clean(), derive_terrain(), elevation_sample(), _flow_accumulation(), list_slope_classes(), _metric_raster() (+6 more)

### Community 65 - "AlgCall"
Cohesion: 0.14
Nodes (14): AlgCall, Pause, run_now(), _spy_manager(), generator(), test_apres_detachement_le_finisseur_n_est_plus_appele(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now() (+6 more)

### Community 66 - "collections_abc"
Cohesion: 0.13
Nodes (3): acquire_landcover_guard(), release(), _application()

### Community 67 - "run_qgis_integration.py"
Cohesion: 0.22
Nodes (9): bootstrap(), build_bundle(), command(), _fail(), find_launcher(), isolated_env(), main(), probe() (+1 more)

### Community 68 - "core/zoning.py"
Cohesion: 0.14
Nodes (9): assess(), cache_matches(), for_territory(), _inpn(), Zoning, zoning_state(), regulatory_prescan(), test_par_territoire() (+1 more)

### Community 69 - "test_detached_landcover_task.py"
Cohesion: 0.22
Nodes (17): _crs_wkt(), expect_busy_start(), guard_free(), isolated(), make_sample(), patched(), _req(), spin() (+9 more)

### Community 70 - "get_vector_layer"
Cohesion: 0.08
Nodes (20): _allowed(), describe_algorithm(), run_algorithm(), get_vector_layer(), kernel_density_points(), buffer(), dissolve(), extract() (+12 more)

### Community 71 - "test_connection.py"
Cohesion: 0.18
Nodes (11): conn_file(), _deny_unlink(), test_invalid_json_ignored_by_default(), test_invalid_json_raises_in_strict_mode(), test_missing_file_is_accepted(), test_other_instance_file_is_kept(), test_permission_error_on_delete_is_silent_by_default(), test_permission_error_on_delete_raises_in_strict_mode() (+3 more)

### Community 72 - "app.py"
Cohesion: 0.17
Nodes (7): call_tool(), _cancel_and_observe(), _fetch_specs(), list_tools(), _progress_token(), _to_tool(), _wait_job()

### Community 73 - "BridgeResult"
Cohesion: 0.17
Nodes (10): BridgeResult, CatalogClient, FakeClient, test_catalogue_relu_seulement_si_le_pont_change(), test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat() (+2 more)

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "core/impacts.py"
Cohesion: 0.17
Nodes (9): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), test_anneaux(), test_comparaison_variantes(), test_poids_enjeu() (+1 more)

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "normalize"
Cohesion: 0.09
Nodes (16): apply_mapping(), get_class(), LandscapeClass, merge_nomenclature(), register(), score_match(), normalize(), to_ascii() (+8 more)

### Community 78 - "render_map"
Cohesion: 0.18
Nodes (3): render_map(), _overview_map(), _project_facts()

### Community 79 - "pytest"
Cohesion: 0.09
Nodes (34): LandcoverConfig, resolve_output_parent(), _validate_number(), validate_rgb_bands(), _alias(), root(), test_config_is_immutable(), test_config_is_json_serializable() (+26 more)

### Community 80 - "find_source_file"
Cohesion: 0.15
Nodes (7): find_source_file(), referentials_directory(), list_reference_sources(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "style.py"
Cohesion: 0.12
Nodes (12): parse_color(), readable_text_color(), with_alpha(), _lookup(), _number(), validate_labels(), test_parse_color(), test_parse_color_refuse() (+4 more)

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "QgsVectorLayer"
Cohesion: 0.20
Nodes (5): field_type_name(), geometry_from_wkt(), layer_field_types(), wkt_to_layer_crs(), add_features()

### Community 85 - "math"
Cohesion: 0.12
Nodes (13): describe_full(), interpret_shape(), kurtosis(), percentile(), skewness(), _t95(), weighted_stats(), _cut() (+5 more)

### Community 86 - "core/zoning.py"
Cohesion: 0.24
Nodes (5): bbox_covers(), should_replace_cache(), status(), test_bbox_rules(), test_statut()

### Community 89 - "test_landscape.py"
Cohesion: 0.15
Nodes (10): classes_for(), suggest_mapping(), validate_codes(), check_rules(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_suggest_mapping_reconnait_les_libelles(), test_suggest_mapping_valeurs_inconnues() (+2 more)

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
Cohesion: 0.16
Nodes (5): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 107 - "build_plugin.py"
Cohesion: 0.26
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 108 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 109 - "mentions_natura2000"
Cohesion: 0.38
Nodes (4): test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 110 - "styling.py"
Cohesion: 0.12
Nodes (19): _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _distinct_values(), get_layer_style() (+11 more)

### Community 111 - "core/project_audit.py"
Cohesion: 0.15
Nodes (23): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+15 more)

### Community 113 - "core/taxref.py"
Cohesion: 0.18
Nodes (11): _columns(), match_taxa(), name_key(), read_statuses(), Statuses, Taxon, listed(), _values() (+3 more)

### Community 114 - "_prepare"
Cohesion: 0.28
Nodes (6): _full_aoi(), islands(), _islands_mask(), _prepare(), sample(), _texture()

### Community 115 - "_segmentation_manager"
Cohesion: 0.14
Nodes (16): _segment_step(), _segmentation_manager(), generator(), test_i1_reponse_finale_inconnue(), test_segment_annulation_attend_le_callback_et_reste_idempotente(), test_segment_annulation_depuis_qgis_sans_demande(), test_segment_annulation_tardive_conserve_la_sortie(), test_segment_detachee_erreur_technique_reste_un_echec() (+8 more)

### Community 116 - ".dispatch"
Cohesion: 0.19
Nodes (4): Request, finish(), collecting(), render_notes()

### Community 117 - "segment.py"
Cohesion: 0.22
Nodes (5): _diagnostics(), _positive_float(), SlicConfig, test_config_defaults_are_normalised_floats(), _DerivedSlic

### Community 118 - "Recorder"
Cohesion: 0.13
Nodes (10): SegmentationCancelledError, _keep(), Recorder, test_double_nettoyage_impossible_apres_annulation(), test_double_slic_annule_puis_echoue(), test_double_slic_demande_l_annulation(), test_real_annulation_a_99_supprime_le_temporaire(), test_real_annulation_a_chaque_checkpoint() (+2 more)

### Community 119 - "require_field"
Cohesion: 0.07
Nodes (20): is_sensitive_field(), mask_sensitive(), sensitive_fields(), require_field(), to_json_value(), check_geometries(), _error_kind(), geometry_report() (+12 more)

### Community 120 - "Zoning"
Cohesion: 0.23
Nodes (7): cache_meta(), cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_meta_roundtrip_and_matching(), test_cache_root_env_override()

### Community 121 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 122 - "to_float"
Cohesion: 0.13
Nodes (11): correlation_pairs(), describe(), describe_categorical(), describe_groups(), to_float(), test_categorical_entropy(), test_pairs_skip_missing(), test_describe_basic() (+3 more)

### Community 123 - "_rewrite"
Cohesion: 0.22
Nodes (13): _analysis_outside_validity(), _implicit_mask(), _read_bands(), _rewrite(), _rgb_mask_differs(), _rgb_without_photometric(), _set_pixel(), mutate() (+5 more)

### Community 124 - "PreparationConfig"
Cohesion: 0.29
Nodes (8): PrepareLandcover, PreparationConfig, make_obia_dispatcher(), obia(), tool(), obia_prepare_test(), test_preparation_default_limit(), test_preparation_json_serialization()

### Community 126 - "pyqgis.py"
Cohesion: 0.09
Nodes (11): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+3 more)

### Community 128 - "_status"
Cohesion: 0.26
Nodes (11): _detached(), _outcome(), finisher(), _status(), test_i1_diagnostic_avec_statut_inattendu(), test_i1_echec_jamais_declasse_ni_code_inconnu_rejete(), test_i1_erreur_technique_apres_detachement(), test_i1_interrogations_repetees_stables() (+3 more)

### Community 130 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 132 - "open_table"
Cohesion: 0.22
Nodes (4): find_file(), open_table(), _sibling(), test_open_table_zip()

### Community 133 - "connection.py"
Cohesion: 0.25
Nodes (4): new_token(), remove_connection_file(), write_connection_file(), remove_and_release_connection()

### Community 135 - "parse_number"
Cohesion: 0.43
Nodes (4): parse_count(), parse_date(), parse_number(), test_valeurs()

### Community 136 - "make_confirmer"
Cohesion: 0.33
Nodes (3): build_details(), make_confirmer(), confirm()

### Community 138 - "units.py"
Cohesion: 0.47
Nodes (3): convert_area(), test_conversions(), test_unknown_unit()

### Community 139 - "ndvi_deviation"
Cohesion: 0.50
Nodes (3): ndvi_deviation(), ndvi_range(), test_ndvi_controle()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 997 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `_status`, `tools/webservices.py`, `common.py`, `test_segment_landcover_tool.py`, `test_landcover_segmentation_task.py`, `editing.py`, `feature_request`, `JobManager`, `test_jobs.py`, `json`, `test_dispatcher.py`, `FakeExecutor`, `ProcessingExecutor`, `fetch_wfs_layer`, `Schéma des paramètres`, `ToolResult`, `test_prepare_landcover_tool.py`, `test_landcover_guard.py`, `select_ids`, `Dispatcher`, `BridgeServer`, `test_landcover_task_finished.py`, `tools/terrain.py`, `AlgCall`, `collections_abc`, `test_detached_landcover_task.py`, `get_vector_layer`, `render_map`, `find_source_file`, `QgsVectorLayer`, `test_bridge_lifecycle.py`, `styling.py`, `_segmentation_manager`, `.dispatch`, `require_field`, `pyqgis.py`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 115 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 115 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06414414414414414 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `_status`, `tools/webservices.py`, `common.py`, `test_segment_landcover_tool.py`, `test_landcover_segmentation_task.py`, `editing.py`, `feature_request`, `JobManager`, `test_jobs.py`, `json`, `test_dispatcher.py`, `FakeExecutor`, `ProcessingExecutor`, `fetch_wfs_layer`, `Schéma des paramètres`, `ToolResult`, `test_prepare_landcover_tool.py`, `test_landcover_guard.py`, `select_ids`, `Dispatcher`, `BridgeServer`, `test_landcover_task_finished.py`, `tools/terrain.py`, `AlgCall`, `collections_abc`, `test_detached_landcover_task.py`, `get_vector_layer`, `render_map`, `find_source_file`, `QgsVectorLayer`, `test_bridge_lifecycle.py`, `styling.py`, `_segmentation_manager`, `require_field`, `pyqgis.py`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 173 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 173 INFERRED edges - model-reasoned connections that need verification._
- **Should `report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10967741935483871 - nodes in this community are weakly interconnected._