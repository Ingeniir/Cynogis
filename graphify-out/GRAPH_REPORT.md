# Graph Report - cynogis  (2026-11-24)

## Corpus Check
- 170 files · ~143,669 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 3128 nodes · 9248 edges · 133 communities (106 shown, 27 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 957 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `85fff08f`
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
- test_persist_features.py
- test_landcover_segmentation_task.py
- prepare.py
- test_fields.py
- Coefficients de surface
- colors.py
- CynogisPlugin
- core/referentials.py
- numpy
- feature_request
- JobManager
- test_jobs.py
- collections_abc
- json
- test_project_audit.py
- Journal d'édition
- test_dispatcher.py
- FakeExecutor
- compute_breaks
- FakeSocket
- json
- test_object_features.py
- dev_setup.py
- re
- Résolution des recouvrements
- allocate
- ProcessingExecutor
- Catalogue d'algorithmes
- test_double_rmtree_en_echec
- Distances
- persist.py
- Historique des styles
- _finish_detached_job
- HABREF
- Tests de style
- core/stakes.py
- fetch_wfs_layer
- Schéma des paramètres
- logging
- check_surfaces.py
- Territory
- Tests zonage
- test_prepare_landcover_tool.py
- PreparationControl
- Feuille de route
- test_landcover_guard.py
- ErrorCode
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
- run_algorithm
- test_connection.py
- app.py
- BridgeResult
- Guide d'installation
- contextlib
- Règles métier réglementaires
- normalize
- render_map
- pytest
- find_source_file
- Règles d'architecture
- contrast_ratio
- Adding a tool (@tool decorator, Param, docstring)
- FakeSocket
- math
- core/zoning.py
- _closer_parts
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
- RecordingJobs
- core/project_audit.py
- Iface
- Env
- _prepare
- _segmentation_manager
- Dispatcher
- test_real_uint32_grille_scr_et_masque
- Recorder
- require_field
- Zoning
- format_number
- ping
- _rewrite
- Cynogis Plugin Icon (icon.svg)
- Rule
- pyqgis.py
- test_plugin_unload_detaches_real_job_manager
- _status
- FakeBridgeServer
- Provenance
- Executor
- make_confirmer

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

## Communities (133 total, 27 thin omitted)

### Community 0 - "BridgeResult"
Cohesion: 0.21
Nodes (11): app(), install_client(), ScriptedClient, test_bridge_failure_does_not_confirm_stop(), test_cancel_waits_for_final_confirmation(), test_cleanup_error_is_not_reported_as_clean_cancellation(), test_job_completed_before_cancellation_took_effect(), test_late_cancellation_preserves_output_details() (+3 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.06
Nodes (43): Fetch, is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs() (+35 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "common.py"
Cohesion: 0.06
Nodes (38): Level, tool(), Param, looks_like_mojibake(), detect_territory(), mentions_natura2000(), _overview_extent(), clean_number() (+30 more)

### Community 4 - "test_segment_landcover_tool.py"
Cohesion: 0.13
Nodes (30): abort_test_process(), _alias(), controlled_engine(), environment(), final_response(), done(), guard_free(), params() (+22 more)

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.12
Nodes (25): _crs(), _DerivedControl, _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs() (+17 more)

### Community 6 - "test_landcover_persist.py"
Cohesion: 0.07
Nodes (36): _altered_reread(), _edit_manifest(), _failing_close(), _failing_replace(), _keep(), _kernel(), _manifest(), _run() (+28 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 10 - "test_persist_features.py"
Cohesion: 0.09
Nodes (21): _altered_reread(), _chain(), _edit_seg_manifest(), _failing_replace(), _input_mutation(), _keep(), _load(), _manifest() (+13 more)

### Community 11 - "test_landcover_segmentation_task.py"
Cohesion: 0.10
Nodes (40): _abort(), _aoi_wkb(), _blocking(), controlled_until_cancelled(), expect_busy(), guard_free(), isolated(), make_dispatcher() (+32 more)

### Community 12 - "prepare.py"
Cohesion: 0.26
Nodes (9): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+1 more)

### Community 13 - "test_fields.py"
Cohesion: 0.06
Nodes (34): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), truncate_field_names(), companion_paths() (+26 more)

### Community 14 - "Coefficients de surface"
Cohesion: 0.06
Nodes (35): Box, layout_boxes(), page_size(), CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio() (+27 more)

### Community 15 - "colors.py"
Cohesion: 0.10
Nodes (17): darken(), distinct_colors(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), validate_colors() (+9 more)

### Community 17 - "core/referentials.py"
Cohesion: 0.10
Nodes (21): _covers(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), _segments(), Source, sources_for() (+13 more)

### Community 18 - "numpy"
Cohesion: 0.10
Nodes (13): altitude_band(), parse_bands(), _isopleth_geometries(), _isopleths(), _style(), _clean(), elevation_sample(), _pixel_labels() (+5 more)

### Community 19 - "feature_request"
Cohesion: 0.04
Nodes (70): unique_field_name(), Pacer, convert_area(), convert_length(), compute_coefficients(), _geometries(), landscape_metrics(), _load_zones() (+62 more)

### Community 20 - "JobManager"
Cohesion: 0.14
Nodes (6): collecting(), Job, JobManager, test_jobmanager_double_finalization_error_fails_job(), test_cancel_all_continues_after_one_job_fails(), test_start_refuse_sur_un_gestionnaire_detache()

### Community 21 - "test_jobs.py"
Cohesion: 0.12
Nodes (41): _audited(), make(), make_obia(), _req(), test_annulation(), test_annulation_obia_detachee_attend_le_callback_reel(), test_annulation_pendant_une_pause(), test_audit_retained_output_for_direct_tool_error() (+33 more)

### Community 22 - "collections_abc"
Cohesion: 0.10
Nodes (16): interpolate_ramp(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors(), validate_palette() (+8 more)

### Community 23 - "json"
Cohesion: 0.16
Nodes (11): new_token(), remove_connection_file(), write_connection_file(), decode_request(), _protocol_error(), remove_and_release_connection(), _line(), test_decode_invalid() (+3 more)

### Community 24 - "test_project_audit.py"
Cohesion: 0.32
Nodes (13): layer_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique(), test_projet_sain_sans_anomalie() (+5 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.10
Nodes (12): check_batch_size(), describe_summary(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations() (+4 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.30
Nodes (12): crash(), double(), make(), metier(), _req(), supprimer(), test_destroy_with_confirmation(), test_errors() (+4 more)

### Community 27 - "FakeExecutor"
Cohesion: 0.07
Nodes (14): note(), boucle(), calcul(), effacer(), erreur_avant(), FakeExecutor, job_invalide(), lecture() (+6 more)

### Community 28 - "compute_breaks"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "FakeSocket"
Cohesion: 0.23
Nodes (12): FakeDispatcher, FakeListener, make_bridge(), patched(), request_line(), spin(), test_bridge_no_dispatch_after_stop_request(), test_bridge_socket_failure_does_not_block_others_and_is_retained() (+4 more)

### Community 30 - "json"
Cohesion: 0.27
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "test_object_features.py"
Cohesion: 0.10
Nodes (35): _adjacency(), extract_object_features(), ObjectFeatures, _pixel_area(), assert_invariants(), assert_matches_oracle(), _FloatSubclass, _IntSubclass (+27 more)

### Community 32 - "dev_setup.py"
Cohesion: 0.17
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 33 - "re"
Cohesion: 0.06
Nodes (28): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), _columns() (+20 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.14
Nodes (15): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus() (+7 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "ProcessingExecutor"
Cohesion: 0.08
Nodes (9): LandcoverSegmentationTask, LandcoverPreparationTask, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, forget() (+1 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.10
Nodes (14): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), to_ascii(), test_liste_blanche() (+6 more)

### Community 38 - "test_double_rmtree_en_echec"
Cohesion: 0.33
Nodes (4): _failing_write(), test_double_nettoyage_impossible_apres_annulation(), test_double_rmtree_en_echec(), blocked()

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 40 - "persist.py"
Cohesion: 0.15
Nodes (20): _check(), _dataset(), _diagnostics(), _check_tables(), _directory(), persist_object_features(), _save_table(), _schema() (+12 more)

### Community 41 - "Historique des styles"
Cohesion: 0.18
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "_finish_detached_job"
Cohesion: 0.22
Nodes (9): DetachedJobOutcome, _detail_text(), _finish_detached_job(), test_outcome_annulation_tardive_conserve_le_repertoire(), test_outcome_details_de_l_erreur_principale_prioritaires(), test_outcome_n_extrait_jamais_un_chemin_du_message(), test_outcome_rejette_les_chemins_non_textuels(), test_outcome_repli_sur_le_resultat() (+1 more)

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.11
Nodes (22): build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees() (+14 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.08
Nodes (22): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+14 more)

### Community 46 - "fetch_wfs_layer"
Cohesion: 0.17
Nodes (7): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "logging"
Cohesion: 0.33
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 49 - "check_surfaces.py"
Cohesion: 0.17
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 51 - "Tests zonage"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 52 - "test_prepare_landcover_tool.py"
Cohesion: 0.16
Nodes (28): abort_test_process(), environment(), final_response(), done(), make_geotiff(), params(), patched(), _plain() (+20 more)

### Community 53 - "PreparationControl"
Cohesion: 0.09
Nodes (20): PreparationCancelledError, PreparationControl, SegmentationCancelledError, SegmentationControl, test_double_annulation_initiale_sans_lecture(), test_real_callback_en_erreur_apres_creation(), test_callback_failure_is_not_hidden(), test_cancellation_before_callback() (+12 more)

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "test_landcover_guard.py"
Cohesion: 0.13
Nodes (16): expect_busy(), in_thread(), is_free(), isolated_property(), patched(), RefusingTaskManager, step(), test_executor_addtask_refusal_releases_guard() (+8 more)

### Community 56 - "ErrorCode"
Cohesion: 0.05
Nodes (59): ToolResult, ErrorCode, to_float(), begin_edit(), expression_context(), geometry_from_wkt(), is_shapefile(), layer_field_types() (+51 more)

### Community 57 - "test_landcover_segment.py"
Cohesion: 0.10
Nodes (33): _positive_float(), segment_rgb(), SlicConfig, assert_contract(), forbidden_slic(), irregular_mask_with_hole(), raises(), random_rgb() (+25 more)

### Community 58 - "Dispatcher"
Cohesion: 0.14
Nodes (6): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, Env

### Community 59 - "ToolError"
Cohesion: 0.04
Nodes (28): ToolError, crs_from_text(), export_table(), _project_target(), save_project(), _save_project_details(), _write_csv(), write_document() (+20 more)

### Community 60 - "run_cleanup_steps"
Cohesion: 0.12
Nodes (6): run_cleanup_steps(), test_cleanup_accepts_empty_sequence(), test_cleanup_collects_multiple_errors(), test_cleanup_continues_after_failure(), test_cleanup_does_not_swallow_process_interruptions(), test_cleanup_executes_every_step_in_order()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "test_landcover_task_finished.py"
Cohesion: 0.11
Nodes (17): isolated_guard(), make_task(), _obia_job(), tool(), patched(), Recorder, spin(), step() (+9 more)

### Community 64 - "tools/terrain.py"
Cohesion: 0.07
Nodes (22): clean_name(), unique_path(), export_atlas_pdf(), _from_template(), get_raster_layer(), kernel_density_points(), compute_ndvi(), add_to_group() (+14 more)

### Community 65 - "AlgCall"
Cohesion: 0.13
Nodes (15): AlgCall, Pause, run_now(), _spy_manager(), generator(), test_apres_detachement_le_finisseur_n_est_plus_appele(), test_echec_de_fermeture_detache_reste_un_echec_technique(), generator() (+7 more)

### Community 66 - "collections_abc"
Cohesion: 0.11
Nodes (4): SegmentLandcover, acquire_landcover_guard(), release(), _application()

### Community 67 - "run_qgis_integration.py"
Cohesion: 0.22
Nodes (9): bootstrap(), build_bundle(), command(), _fail(), find_launcher(), isolated_env(), main(), probe() (+1 more)

### Community 68 - "core/zoning.py"
Cohesion: 0.20
Nodes (7): cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, test_cache_meta_roundtrip_and_matching(), test_par_territoire()

### Community 69 - "test_detached_landcover_task.py"
Cohesion: 0.14
Nodes (25): PrepareLandcover, PreparationConfig, _crs_wkt(), expect_busy_start(), guard_free(), isolated(), make_obia_dispatcher(), obia() (+17 more)

### Community 70 - "run_algorithm"
Cohesion: 0.22
Nodes (4): _allowed(), describe_algorithm(), list_algorithms(), run_algorithm()

### Community 71 - "test_connection.py"
Cohesion: 0.18
Nodes (11): conn_file(), _deny_unlink(), test_invalid_json_ignored_by_default(), test_invalid_json_raises_in_strict_mode(), test_missing_file_is_accepted(), test_other_instance_file_is_kept(), test_permission_error_on_delete_is_silent_by_default(), test_permission_error_on_delete_raises_in_strict_mode() (+3 more)

### Community 72 - "app.py"
Cohesion: 0.17
Nodes (7): call_tool(), _cancel_and_observe(), _fetch_specs(), list_tools(), _progress_token(), _to_tool(), _wait_job()

### Community 73 - "BridgeResult"
Cohesion: 0.19
Nodes (10): BridgeResult, CatalogClient, FakeClient, test_catalogue_relu_seulement_si_le_pont_change(), test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat() (+2 more)

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "normalize"
Cohesion: 0.09
Nodes (17): apply_mapping(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+9 more)

### Community 78 - "render_map"
Cohesion: 0.14
Nodes (4): render_map(), _overview_map(), _project_facts(), _raster_facts()

### Community 79 - "pytest"
Cohesion: 0.07
Nodes (37): LandcoverConfig, resolve_output_parent(), _validate_number(), validate_rgb_bands(), test_decorator_checks(), _alias(), root(), test_config_is_immutable() (+29 more)

### Community 80 - "find_source_file"
Cohesion: 0.16
Nodes (7): find_source_file(), referentials_directory(), list_reference_sources(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 85 - "math"
Cohesion: 0.08
Nodes (31): correlate(), correlation_pairs(), correlation_pvalue(), describe(), describe_categorical(), describe_full(), describe_groups(), interpret_shape() (+23 more)

### Community 86 - "core/zoning.py"
Cohesion: 0.21
Nodes (6): assess(), bbox_covers(), should_replace_cache(), zoning_state(), test_bbox_rules(), test_pre_diagnostic()

### Community 89 - "test_landscape.py"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 99 - "test_bridge_lifecycle.py"
Cohesion: 0.23
Nodes (15): critical(), fake_remove(), fake_write(), plugin_env(), pushes(), raises(), test_plugin_no_new_bridge_while_previous_cleanup_fails(), test_plugin_normal_stop_notifies_once() (+7 more)

### Community 101 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 102 - "test_terrain.py"
Cohesion: 0.11
Nodes (16): aspect_sector(), degrees_to_percent(), distribution(), percent_to_degrees(), reclass_table(), slope_class(), SlopeClass, test_aspect_sector() (+8 more)

### Community 103 - "Security rules (no bypass, no overwrite, no sensitive species/cadastral data)"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 104 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

### Community 105 - "BridgeError"
Cohesion: 0.23
Nodes (5): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 107 - "build_plugin.py"
Cohesion: 0.27
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 108 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 109 - "mentions_natura2000"
Cohesion: 0.38
Nodes (4): test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 110 - "RecordingJobs"
Cohesion: 0.33
Nodes (3): RecordingJobs, test_plugin_project_signals_cancel_without_detaching(), test_plugin_unload_detaches_finishers_before_cancelling()

### Community 111 - "core/project_audit.py"
Cohesion: 0.19
Nodes (10): audit(), build_sections(), duplicate_name_findings(), _finding(), add(), project_findings(), severity_counts(), verdict() (+2 more)

### Community 114 - "_prepare"
Cohesion: 0.27
Nodes (7): _full_aoi(), islands(), _islands_mask(), _prepare(), sample(), _texture(), test_real_autre_preparation_meme_grille_refusee()

### Community 115 - "_segmentation_manager"
Cohesion: 0.16
Nodes (14): _segment_step(), _segmentation_manager(), generator(), test_segment_annulation_attend_le_callback_et_reste_idempotente(), test_segment_annulation_depuis_qgis_sans_demande(), test_segment_annulation_tardive_conserve_la_sortie(), test_segment_detachee_erreur_technique_reste_un_echec(), segmentation_test() (+6 more)

### Community 116 - "Dispatcher"
Cohesion: 0.13
Nodes (5): Request, Response, Dispatcher, finish(), render_notes()

### Community 117 - "test_real_uint32_grille_scr_et_masque"
Cohesion: 0.40
Nodes (5): _other_crs(), _read_segments(), test_real_trou_ilots_diagonale_pixel_isole(), test_real_uint32_grille_scr_et_masque(), _wkt()

### Community 118 - "Recorder"
Cohesion: 0.14
Nodes (6): Recorder, test_double_annulation_tardive_apres_99(), test_double_slic_annule_puis_echoue(), test_double_slic_demande_l_annulation(), test_real_annulation_a_99_supprime_le_temporaire(), test_real_controle_sequence_exacte()

### Community 119 - "require_field"
Cohesion: 0.05
Nodes (34): is_sensitive_field(), mask_sensitive(), sensitive_fields(), field_type_name(), get_vector_layer(), require_field(), to_json_value(), _delete_field_details() (+26 more)

### Community 120 - "Zoning"
Cohesion: 0.18
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_root_env_override()

### Community 121 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 123 - "_rewrite"
Cohesion: 0.23
Nodes (14): _analysis_outside_validity(), _implicit_mask(), _read_bands(), _rewrite(), _rgb_mask_differs(), _rgb_without_photometric(), _set_pixel(), mutate() (+6 more)

### Community 126 - "pyqgis.py"
Cohesion: 0.09
Nodes (11): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+3 more)

### Community 128 - "_status"
Cohesion: 0.26
Nodes (11): _detached(), _outcome(), finisher(), _status(), test_i1_diagnostic_avec_statut_inattendu(), test_i1_echec_jamais_declasse_ni_code_inconnu_rejete(), test_i1_erreur_technique_apres_detachement(), test_i1_interrogations_repetees_stables() (+3 more)

### Community 130 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 136 - "make_confirmer"
Cohesion: 0.33
Nodes (3): build_details(), make_confirmer(), confirm()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1010 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `_status`, `tools/webservices.py`, `common.py`, `test_segment_landcover_tool.py`, `test_landcover_segmentation_task.py`, `numpy`, `feature_request`, `JobManager`, `test_jobs.py`, `json`, `test_dispatcher.py`, `FakeExecutor`, `ProcessingExecutor`, `_finish_detached_job`, `fetch_wfs_layer`, `Schéma des paramètres`, `test_prepare_landcover_tool.py`, `test_landcover_guard.py`, `ErrorCode`, `Dispatcher`, `BridgeServer`, `test_landcover_task_finished.py`, `tools/terrain.py`, `collections_abc`, `test_detached_landcover_task.py`, `run_algorithm`, `render_map`, `find_source_file`, `Dispatcher`, `require_field`, `pyqgis.py`, `test_plugin_unload_detaches_real_job_manager`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Are the 115 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 115 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06414414414414414 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `_status`, `tools/webservices.py`, `common.py`, `test_segment_landcover_tool.py`, `test_landcover_segmentation_task.py`, `numpy`, `feature_request`, `JobManager`, `test_jobs.py`, `json`, `test_dispatcher.py`, `FakeExecutor`, `ProcessingExecutor`, `_finish_detached_job`, `fetch_wfs_layer`, `Schéma des paramètres`, `test_prepare_landcover_tool.py`, `test_landcover_guard.py`, `Dispatcher`, `ToolError`, `BridgeServer`, `test_landcover_task_finished.py`, `tools/terrain.py`, `collections_abc`, `test_detached_landcover_task.py`, `run_algorithm`, `render_map`, `find_source_file`, `_segmentation_manager`, `Dispatcher`, `require_field`, `pyqgis.py`, `test_plugin_unload_detaches_real_job_manager`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 173 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 173 INFERRED edges - model-reasoned connections that need verification._
- **Should `report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10967741935483871 - nodes in this community are weakly interconnected._