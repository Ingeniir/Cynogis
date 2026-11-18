# Graph Report - cynogis  (2026-11-18)

## Corpus Check
- 161 files · ~128,144 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2833 nodes · 8300 edges · 140 communities (113 shown, 27 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 846 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eea8aba9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BridgeResult
- tools/webservices.py
- report.py
- ToolResult
- geometry_report
- test_landcover_prepare.py
- test_landcover_persist.py
- Métriques paysagères
- Documentation projet
- habitat_typology_join
- shapefile.py
- test_project_audit.py
- prepare.py
- numpy
- Coefficients de surface
- colors.py
- CynogisPlugin
- core/referentials.py
- run_to_project
- feature_request
- JobManager
- Tests des jobs
- collections_abc
- json
- math
- Journal d'édition
- test_dispatcher.py
- FakeExecutor
- compute_breaks
- fields.py
- audit.py
- ToolRegistry
- dev_setup.py
- Données terrain CSV
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
- describe
- contrast_ratio
- common.py
- Tests zonage
- test_prepare_landcover_tool.py
- PreparationControl
- Feuille de route
- test_landcover_guard.py
- ToolResult
- test_landcover_segment.py
- Dispatcher
- ToolError
- run_cleanup_steps
- Cache des zonages
- Plan d'échantillonnage
- test_landcover_task_finished.py
- numpy
- Pause
- Provenance
- test_job_lance_pendant_la_confirmation
- regulatory_prescan
- test_detached_landcover_task.py
- test_stats_full.py
- test_connection.py
- app.py
- CatalogClient
- Guide d'installation
- FakeSocket
- Règles métier réglementaires
- core/landscape.py
- render_map
- pytest
- find_source_file
- Règles d'architecture
- re
- Adding a tool (@tool decorator, Param, docstring)
- pyqgis.py
- Iface
- core/zoning.py
- LandcoverPreparationTask
- Commandes de dev
- Cynogis Plugin Icon (icon.svg)
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
- export.py
- core/impacts.py
- ToolResult
- core/project_audit.py
- _status
- _finish_detached_job
- ._start_bridge
- check_surfaces.py
- collections_abc
- describe_algorithm
- Recorder
- profile_table
- Zoning
- FakeBridgeServer
- test_double_rmtree_en_echec
- inspect_landcover_inputs
- PreparationConfig
- Rule
- risky_names
- _geometry_repr
- classes_for
- client.py
- correlate
- _clipped
- Executor
- landcover_guard.py
- Env
- format_number
- units.py
- RecordingJobs
- test_double_annulation_initiale_sans_lecture
- _is_empty

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 226 edges
2. `ErrorCode` - 203 edges
3. `ToolResult` - 109 edges
4. `get_vector_layer()` - 103 edges
5. `feature_request()` - 73 edges
6. `geometry_kind()` - 60 edges
7. `require_field()` - 56 edges
8. `to_json_value()` - 52 edges
9. `distance_area()` - 51 edges
10. `Level` - 50 edges

## Surprising Connections (you probably didn't know these)
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `test_describe_empty_and_single()` --calls--> `describe()`  [INFERRED]
  tests/unit/test_stats.py → plugin/cynogis/core/stats.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `test_diagnostics_une_seule_graine()` --uses--> `SlicConfig`  [INFERRED]
  tests/integration/test_landcover_persist.py → plugin/cynogis/landcover_processing/segment.py
- `test_diagnostics_valeurs_connues()` --uses--> `SlicConfig`  [INFERRED]
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

## Communities (140 total, 27 thin omitted)

### Community 0 - "BridgeResult"
Cohesion: 0.17
Nodes (16): BridgeResult, app(), test_wait_job_annule_dans_qgis(), scenario(), install_client(), ScriptedClient, test_bridge_failure_does_not_confirm_stop(), test_cancel_waits_for_final_confirmation() (+8 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.05
Nodes (50): is_natura2000_layer(), mentions_natura2000(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs() (+42 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "ToolResult"
Cohesion: 0.18
Nodes (5): Level, tool(), decorator(), Param, to_json_value()

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.12
Nodes (25): _crs(), _DerivedControl, _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs() (+17 more)

### Community 6 - "test_landcover_persist.py"
Cohesion: 0.07
Nodes (34): _altered_reread(), _analysis_outside_validity(), _edit_manifest(), _failing_close(), _failing_replace(), _full_aoi(), _implicit_mask(), islands() (+26 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (33): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), interpret_metrics(), largest_patch_index() (+25 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "habitat_typology_join"
Cohesion: 0.20
Nodes (4): find_file(), open_table(), habitat_typology_join(), _sibling()

### Community 10 - "shapefile.py"
Cohesion: 0.10
Nodes (17): truncate_field_names(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages() (+9 more)

### Community 11 - "test_project_audit.py"
Cohesion: 0.32
Nodes (13): layer_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique(), test_projet_sain_sans_anomalie() (+5 more)

### Community 12 - "prepare.py"
Cohesion: 0.23
Nodes (9): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+1 more)

### Community 13 - "numpy"
Cohesion: 0.13
Nodes (6): _diagnostics(), _isopleth_geometries(), _isopleths(), _style(), check_surface_3d(), synthetic_dem()

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (26): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+18 more)

### Community 15 - "colors.py"
Cohesion: 0.10
Nodes (18): darken(), distinct_colors(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string() (+10 more)

### Community 17 - "core/referentials.py"
Cohesion: 0.11
Nodes (21): _covers(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), _segments(), Source, sources_for() (+13 more)

### Community 18 - "run_to_project"
Cohesion: 0.10
Nodes (14): kernel_density_points(), buffer(), dissolve(), extract(), fix_geometries(), _name(), overlay(), reproject_layer() (+6 more)

### Community 19 - "feature_request"
Cohesion: 0.05
Nodes (56): build_table(), Pacer, convert_length(), add_to_memory(), area_m2(), area_method(), distance_area(), feature_request() (+48 more)

### Community 20 - "JobManager"
Cohesion: 0.16
Nodes (5): collecting(), Job, JobManager, test_jobmanager_double_finalization_error_fails_job(), test_start_refuse_sur_un_gestionnaire_detache()

### Community 21 - "Tests des jobs"
Cohesion: 0.15
Nodes (33): PreparationCancelledError, make(), make_obia(), _req(), test_annulation(), test_annulation_obia_detachee_attend_le_callback_reel(), test_annulation_pendant_une_pause(), test_boucle_avec_pauses() (+25 more)

### Community 22 - "collections_abc"
Cohesion: 0.09
Nodes (16): validate_colors(), all_palettes(), describe_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors() (+8 more)

### Community 23 - "json"
Cohesion: 0.32
Nodes (7): decode_request(), _protocol_error(), _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "math"
Cohesion: 0.15
Nodes (11): fractal_dimension(), correlation_pvalue(), describe(), describe_full(), interpret_shape(), kurtosis(), percentile(), _r() (+3 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.09
Nodes (11): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+3 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "FakeExecutor"
Cohesion: 0.17
Nodes (4): FakeExecutor, test_cancel_all_continues_after_one_job_fails(), test_echec_de_fermeture_detache_reste_un_echec_technique(), generator()

### Community 28 - "compute_breaks"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "fields.py"
Cohesion: 0.11
Nodes (17): coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict(), test_coerce_value() (+9 more)

### Community 30 - "audit.py"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.13
Nodes (7): PermissionPolicy, spec_of(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 32 - "dev_setup.py"
Cohesion: 0.17
Nodes (12): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+4 more)

### Community 33 - "Données terrain CSV"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.10
Nodes (17): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), _as_multipolygon(), _closer_parts(), records() (+9 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "tasks.py"
Cohesion: 0.10
Nodes (10): AlgCall, Fetch, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, forget() (+2 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.12
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 38 - "_run"
Cohesion: 0.10
Nodes (24): _keep(), _kernel(), _run(), _sha(), _snapshot(), test_double_echec_nettoie_seulement_son_dossier(), test_double_mutation_avant_publication(), mutating() (+16 more)

### Community 39 - "Distances"
Cohesion: 0.13
Nodes (13): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), to_float(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible() (+5 more)

### Community 40 - "persist.py"
Cohesion: 0.23
Nodes (13): _check(), _dataset(), _fingerprints(), _grid(), _load_inputs(), persist_segmentation(), _read_json(), _read_raster() (+5 more)

### Community 41 - "Historique des styles"
Cohesion: 0.18
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "core/atlas.py"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.10
Nodes (24): build_categories(), describe_options(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques() (+16 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.18
Nodes (12): Criterion, level_for(), level_number(), Override, parse_criteria(), parse_overrides(), parse_thresholds(), score() (+4 more)

### Community 46 - "fetch_wfs_layer"
Cohesion: 0.16
Nodes (8): service_label(), _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.22
Nodes (8): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_items_enum(), test_object_schema()

### Community 48 - "describe"
Cohesion: 0.17
Nodes (7): describe_categorical(), describe_groups(), test_categorical_entropy(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 49 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 50 - "common.py"
Cohesion: 0.08
Nodes (28): detect_territory(), _overview_extent(), clean_number(), crs_info(), enum_name(), extent_wgs84(), file_format(), get_layer() (+20 more)

### Community 51 - "Tests zonage"
Cohesion: 0.18
Nodes (6): getfeature_url(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 52 - "test_prepare_landcover_tool.py"
Cohesion: 0.19
Nodes (20): abort_test_process(), environment(), final_response(), done(), make_geotiff(), params(), patched(), _plain() (+12 more)

### Community 53 - "PreparationControl"
Cohesion: 0.12
Nodes (17): PreparationControl, SegmentationCancelledError, SegmentationControl, test_callback_failure_is_not_hidden(), test_cancellation_before_callback(), test_cancellation_check_failure_is_not_hidden(), test_cancellation_requested_during_callback(), progress() (+9 more)

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "test_landcover_guard.py"
Cohesion: 0.13
Nodes (15): expect_busy(), in_thread(), is_free(), isolated_property(), patched(), RefusingTaskManager, test_executor_addtask_refusal_releases_guard(), test_executor_constructor_failure_releases_guard() (+7 more)

### Community 56 - "ToolResult"
Cohesion: 0.07
Nodes (40): describe_summary(), coerce_record(), unique_field_name(), begin_edit(), geometry_from_wkt(), get_vector_layer(), is_shapefile(), layer_field_types() (+32 more)

### Community 57 - "test_landcover_segment.py"
Cohesion: 0.10
Nodes (32): _positive_float(), segment_rgb(), SlicConfig, assert_contract(), forbidden_slic(), irregular_mask_with_hole(), raises(), random_rgb() (+24 more)

### Community 58 - "Dispatcher"
Cohesion: 0.12
Nodes (6): Request, Response, BridgeServer, Dispatcher, finish(), render_notes()

### Community 59 - "ToolError"
Cohesion: 0.05
Nodes (34): ErrorCode, ToolError, _allowed(), run_algorithm(), export_atlas_pdf(), _from_template(), crs_from_text(), expression_context() (+26 more)

### Community 60 - "run_cleanup_steps"
Cohesion: 0.12
Nodes (6): run_cleanup_steps(), test_cleanup_accepts_empty_sequence(), test_cleanup_collects_multiple_errors(), test_cleanup_continues_after_failure(), test_cleanup_does_not_swallow_process_interruptions(), test_cleanup_executes_every_step_in_order()

### Community 61 - "Cache des zonages"
Cohesion: 0.40
Nodes (3): cache_paths(), cache_root(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "test_landcover_task_finished.py"
Cohesion: 0.15
Nodes (16): isolated_guard(), make_task(), _obia_job(), tool(), patched(), Recorder, spin(), step() (+8 more)

### Community 64 - "numpy"
Cohesion: 0.12
Nodes (13): classify_slope(), _clean(), derive_terrain(), elevation_sample(), _flow_accumulation(), list_slope_classes(), _metric_raster(), _pixel_labels() (+5 more)

### Community 65 - "Pause"
Cohesion: 0.28
Nodes (6): Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 66 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 67 - "test_job_lance_pendant_la_confirmation"
Cohesion: 0.10
Nodes (13): note(), boucle(), calcul(), effacer(), erreur_avant(), job_invalide(), lecture(), mesure_invalide() (+5 more)

### Community 68 - "regulatory_prescan"
Cohesion: 0.18
Nodes (6): assess(), for_territory(), zoning_state(), regulatory_prescan(), test_par_territoire(), test_pre_diagnostic()

### Community 69 - "test_detached_landcover_task.py"
Cohesion: 0.22
Nodes (17): _crs_wkt(), expect_busy_start(), guard_free(), isolated(), make_sample(), patched(), _req(), spin() (+9 more)

### Community 70 - "test_stats_full.py"
Cohesion: 0.15
Nodes (9): ranks(), weighted_stats(), test_describe_full_shape(), test_empty(), test_outlier_detected(), test_pairs_skip_missing(), test_ranks_ties(), test_sensitive() (+1 more)

### Community 71 - "test_connection.py"
Cohesion: 0.18
Nodes (11): conn_file(), _deny_unlink(), test_invalid_json_ignored_by_default(), test_invalid_json_raises_in_strict_mode(), test_missing_file_is_accepted(), test_other_instance_file_is_kept(), test_permission_error_on_delete_is_silent_by_default(), test_permission_error_on_delete_raises_in_strict_mode() (+3 more)

### Community 72 - "app.py"
Cohesion: 0.17
Nodes (7): call_tool(), _cancel_and_observe(), _fetch_specs(), list_tools(), _progress_token(), _to_tool(), _wait_job()

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "FakeSocket"
Cohesion: 0.14
Nodes (9): FakeDispatcher, FakeListener, FakeSocket, make_bridge(), request_line(), test_bridge_no_dispatch_after_stop_request(), test_bridge_socket_failure_does_not_block_others_and_is_retained(), test_bridge_stop_during_handle_line_drops_response_and_next_lines() (+1 more)

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "core/landscape.py"
Cohesion: 0.10
Nodes (16): apply_mapping(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match(), suggest_mapping() (+8 more)

### Community 78 - "render_map"
Cohesion: 0.13
Nodes (5): render_map(), write_document(), write_pdf(), _overview_map(), _project_facts()

### Community 79 - "pytest"
Cohesion: 0.12
Nodes (23): LandcoverConfig, _validate_number(), validate_rgb_bands(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config(), test_equal_area_thresholds_are_allowed(), test_extremely_large_number_is_rejected() (+15 more)

### Community 80 - "find_source_file"
Cohesion: 0.15
Nodes (7): find_source_file(), referentials_directory(), list_reference_sources(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "re"
Cohesion: 0.18
Nodes (12): _columns(), match_taxa(), name_key(), read_statuses(), Statuses, Taxon, listed(), _values() (+4 more)

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "pyqgis.py"
Cohesion: 0.15
Nodes (5): _as_generator(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm()

### Community 86 - "core/zoning.py"
Cohesion: 0.20
Nodes (6): bbox_covers(), _inpn(), should_replace_cache(), status(), test_bbox_rules(), test_statut()

### Community 99 - "test_bridge_lifecycle.py"
Cohesion: 0.19
Nodes (20): critical(), fake_remove(), fake_write(), patched(), plugin_env(), pushes(), raises(), test_bridge_stopped_instance_cannot_restart() (+12 more)

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
Cohesion: 0.18
Nodes (7): BridgeError, QgisBridgeClient, FakeClient, test_client_reponse_illisible(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 107 - "build_plugin.py"
Cohesion: 0.24
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 108 - "export.py"
Cohesion: 0.07
Nodes (13): clean_name(), to_ascii(), unique_path(), Territory, _output_path(), _project_target(), _save_project_details(), output_dir() (+5 more)

### Community 109 - "core/impacts.py"
Cohesion: 0.19
Nodes (8): compare_variants(), direct_label(), ring_labels(), stake_weight(), test_anneaux(), test_comparaison_variantes(), test_poids_enjeu(), test_tableau()

### Community 110 - "ToolResult"
Cohesion: 0.08
Nodes (26): ToolResult, get_class(), require_field(), get_features(), check_landscape(), suggest_landscape_mapping(), _apply(), apply_categorized_style() (+18 more)

### Community 111 - "core/project_audit.py"
Cohesion: 0.19
Nodes (10): audit(), build_sections(), duplicate_name_findings(), _finding(), add(), project_findings(), severity_counts(), verdict() (+2 more)

### Community 112 - "_status"
Cohesion: 0.22
Nodes (12): _detached(), _outcome(), finisher(), _status(), test_i1_diagnostic_avec_statut_inattendu(), test_i1_echec_jamais_declasse_ni_code_inconnu_rejete(), test_i1_erreur_technique_apres_detachement(), test_i1_interrogations_repetees_stables() (+4 more)

### Community 113 - "_finish_detached_job"
Cohesion: 0.18
Nodes (11): DetachedJobOutcome, _detail_text(), _finish_detached_job(), _spy_manager(), generator(), test_apres_detachement_le_finisseur_n_est_plus_appele(), test_outcome_annulation_tardive_conserve_le_repertoire(), test_outcome_n_extrait_jamais_un_chemin_du_message() (+3 more)

### Community 114 - "._start_bridge"
Cohesion: 0.17
Nodes (6): new_token(), remove_connection_file(), write_connection_file(), remove_and_release_connection(), spin(), test_real_socket_cycle_on_ephemeral_port()

### Community 115 - "check_surfaces.py"
Cohesion: 0.11
Nodes (12): compute_coefficients(), _geometries(), landscape_metrics(), list_coefficients(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of() (+4 more)

### Community 116 - "collections_abc"
Cohesion: 0.10
Nodes (4): QgsLogHandler, setup_logging(), teardown_logging(), register_detail_provider()

### Community 118 - "Recorder"
Cohesion: 0.14
Nodes (6): Recorder, test_double_annulation_tardive_apres_99(), test_double_slic_annule_puis_echoue(), test_double_slic_demande_l_annulation(), test_real_annulation_a_99_supprime_le_temporaire(), test_real_controle_sequence_exacte()

### Community 119 - "profile_table"
Cohesion: 0.09
Nodes (12): is_sensitive_field(), mask_sensitive(), sensitive_fields(), field_type_name(), check_geometries(), get_field_values(), select_features(), correlation_matrix() (+4 more)

### Community 120 - "Zoning"
Cohesion: 0.18
Nodes (7): cache_matches(), cache_meta(), read_cache_meta(), Zoning, _only_fields(), _write_cache(), test_cache_meta_roundtrip_and_matching()

### Community 122 - "test_double_rmtree_en_echec"
Cohesion: 0.33
Nodes (4): _failing_write(), test_double_nettoyage_impossible_apres_annulation(), test_double_rmtree_en_echec(), blocked()

### Community 123 - "inspect_landcover_inputs"
Cohesion: 0.21
Nodes (5): _build_preparation_step(), inspect_landcover_inputs(), prepare_landcover_inputs(), _read_aoi_geometry(), _reject()

### Community 124 - "PreparationConfig"
Cohesion: 0.27
Nodes (9): PrepareLandcover, PreparationConfig, make_obia_dispatcher(), obia(), tool(), step(), obia_prepare_test(), test_preparation_default_limit() (+1 more)

### Community 126 - "risky_names"
Cohesion: 0.24
Nodes (6): blocking_calls(), risky_names(), _details(), test_appels_bloquants(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 128 - "classes_for"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 129 - "client.py"
Cohesion: 0.24
Nodes (3): main(), run(), main()

### Community 130 - "correlate"
Cohesion: 0.31
Nodes (6): correlate(), correlation_pairs(), linear_fit(), pearson(), strength(), test_pearson_and_spearman()

### Community 133 - "landcover_guard.py"
Cohesion: 0.38
Nodes (3): acquire_landcover_guard(), release(), _application()

### Community 135 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 136 - "units.py"
Cohesion: 0.47
Nodes (3): convert_area(), test_conversions(), test_unknown_unit()

### Community 138 - "test_double_annulation_initiale_sans_lecture"
Cohesion: 0.50
Nodes (3): test_double_annulation_initiale_sans_lecture(), test_real_une_seule_graine_sans_slic(), forbidden()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 933 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `ToolResult`, `landcover_guard.py`, `habitat_typology_join`, `run_to_project`, `feature_request`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `FakeExecutor`, `ToolRegistry`, `tasks.py`, `fetch_wfs_layer`, `Schéma des paramètres`, `common.py`, `test_landcover_guard.py`, `ToolResult`, `Dispatcher`, `test_landcover_task_finished.py`, `numpy`, `test_job_lance_pendant_la_confirmation`, `test_detached_landcover_task.py`, `render_map`, `find_source_file`, `pyqgis.py`, `test_bridge_lifecycle.py`, `export.py`, `ToolResult`, `_status`, `_finish_detached_job`, `check_surfaces.py`, `collections_abc`, `profile_table`, `inspect_landcover_inputs`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Are the 109 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 109 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.051201671891327065 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `tools/webservices.py`, `ToolResult`, `landcover_guard.py`, `habitat_typology_join`, `run_to_project`, `feature_request`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `FakeExecutor`, `ToolRegistry`, `tasks.py`, `fetch_wfs_layer`, `Schéma des paramètres`, `common.py`, `test_landcover_guard.py`, `ToolResult`, `Dispatcher`, `test_landcover_task_finished.py`, `numpy`, `test_job_lance_pendant_la_confirmation`, `test_detached_landcover_task.py`, `render_map`, `find_source_file`, `pyqgis.py`, `test_bridge_lifecycle.py`, `export.py`, `ToolResult`, `_status`, `_finish_detached_job`, `check_surfaces.py`, `collections_abc`, `profile_table`, `inspect_landcover_inputs`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 160 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 160 INFERRED edges - model-reasoned connections that need verification._
- **Should `report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10967741935483871 - nodes in this community are weakly interconnected._