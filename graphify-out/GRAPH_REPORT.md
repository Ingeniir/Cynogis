# Graph Report - cynogis  (2026-11-24)

## Corpus Check
- 177 files · ~148,725 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 3251 nodes · 9596 edges · 135 communities (114 shown, 21 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 996 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dddfaea1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BridgeResult
- tools/webservices.py
- report.py
- common.py
- test_segment_landcover_tool.py
- test_landcover_prepare.py
- _run
- Métriques paysagères
- Documentation projet
- tools/coefficients.py
- test_persist_features.py
- test_landcover_segmentation_task.py
- prepare.py
- shapefile.py
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
- test_bridge_lifecycle.py
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
- _isopleth_geometries
- Historique des styles
- dataclasses
- HABREF
- Tests de style
- core/stakes.py
- core/zoning.py
- Schéma des paramètres
- logging
- check_surfaces.py
- test_fields.py
- Tests zonage
- test_prepare_landcover_tool.py
- PreparationControl
- Feuille de route
- test_landcover_guard.py
- ErrorCode
- test_landcover_segment.py
- ToolRegistry
- ToolError
- run_cleanup_steps
- test_landcover_delineate.py
- test_landcover_merge.py
- make
- qgis_pyqt_qtcore
- _finish_detached_job
- jobs.py
- run_qgis_integration.py
- tools/landcover.py
- test_detached_landcover_task.py
- normalize
- test_connection.py
- app.py
- BridgeResult
- Guide d'installation
- _Sampler
- Règles métier réglementaires
- normalize
- ToolResult
- pytest
- find_source_file
- Règles d'architecture
- pathlib
- Adding a tool (@tool decorator, Param, docstring)
- check_geometries
- math
- _cached_source
- merge_segments
- Commandes de dev
- Pause
- Métadonnées plugin
- Liste blanche algorithmes
- Débogage
- Fin de tâche graphify
- Venv vs Python QGIS
- Compatibilité Qt
- Fichiers locaux
- cynogis-server
- render_map
- Phase 1 : Fiabilite des calculs de surface
- test_terrain.py
- Security rules (no bypass, no overwrite, no sensitive species/cadastral data)
- Phase 3 : Tracabilite et confidentialite
- BridgeError
- install.ps1
- list_style_options
- styling.py
- core/impacts.py
- units.py
- core/project_audit.py
- Iface
- test_landcover_delineation.py
- _prepare
- test_jobs.py
- BridgeServer
- core/atlas.py
- Recorder
- correlation_matrix
- Zoning
- format_number
- run_to_project
- _rewrite
- Rule
- pyqgis.py
- FakeBridgeServer
- Provenance
- describe_groups
- Executor
- ping
- assess
- test_landcover_persist.py
- math
- RefusingTaskManager

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 241 edges
2. `ErrorCode` - 219 edges
3. `ToolResult` - 114 edges
4. `get_vector_layer()` - 103 edges
5. `feature_request()` - 73 edges
6. `geometry_kind()` - 60 edges
7. `Level` - 57 edges
8. `require_field()` - 56 edges
9. `distance_area()` - 53 edges
10. `to_json_value()` - 52 edges

## Surprising Connections (you probably didn't know these)
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `test_config_bornes_acceptees()` --uses--> `DelineationConfig`  [INFERRED]
  tests/unit/test_landcover_delineation.py → plugin/cynogis/core/landcover.py
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

## Communities (135 total, 21 thin omitted)

### Community 0 - "BridgeResult"
Cohesion: 0.21
Nodes (11): app(), install_client(), ScriptedClient, test_bridge_failure_does_not_confirm_stop(), test_cancel_waits_for_final_confirmation(), test_cleanup_error_is_not_reported_as_clean_cancellation(), test_job_completed_before_cancellation_took_effect(), test_late_cancellation_preserves_output_details() (+3 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.05
Nodes (48): Fetch, is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs() (+40 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "common.py"
Cohesion: 0.08
Nodes (20): unique_field_name(), clean_name(), unique_path(), Level, spec_of(), tool(), decorator(), ToolSpec (+12 more)

### Community 4 - "test_segment_landcover_tool.py"
Cohesion: 0.12
Nodes (34): _run(), _segmentation(), test_prevalidation_sans_tache(), test_real_chaine_complete_jusqu_a_la_couche(), test_task_annulation_des_caracteristiques(), abort_test_process(), _alias(), controlled_engine() (+26 more)

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.12
Nodes (25): _crs(), _DerivedControl, _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs() (+17 more)

### Community 6 - "_run"
Cohesion: 0.11
Nodes (22): _keep(), _kernel(), _run(), _sha(), _snapshot(), test_double_annulation_initiale_sans_lecture(), test_double_echec_nettoie_seulement_son_dossier(), test_double_noyau_refuse() (+14 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (33): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), interpret_metrics(), largest_patch_index() (+25 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "tools/coefficients.py"
Cohesion: 0.17
Nodes (9): compute_coefficients(), _geometries(), landscape_metrics(), list_coefficients(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of() (+1 more)

### Community 10 - "test_persist_features.py"
Cohesion: 0.12
Nodes (15): _altered_reread(), _failing_replace(), _input_mutation(), _keep(), _load(), _run(), _second_write(), test_double_echec_nettoie_seulement_son_dossier() (+7 more)

### Community 11 - "test_landcover_segmentation_task.py"
Cohesion: 0.10
Nodes (40): _abort(), _aoi_wkb(), _blocking(), controlled_until_cancelled(), expect_busy(), guard_free(), isolated(), make_dispatcher() (+32 more)

### Community 12 - "prepare.py"
Cohesion: 0.26
Nodes (9): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+1 more)

### Community 13 - "shapefile.py"
Cohesion: 0.11
Nodes (16): truncate_field_names(), companion_paths(), export_plan(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), test_truncate_field_names_sans_doublon() (+8 more)

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (26): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+18 more)

### Community 15 - "colors.py"
Cohesion: 0.08
Nodes (19): contrast_ratio(), darken(), lighten(), mix(), parse_color(), readable_text_color(), relative_luminance(), to_rgba_string() (+11 more)

### Community 17 - "core/referentials.py"
Cohesion: 0.11
Nodes (20): check_rules(), _covers(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), _segments(), test_cirad_974_2020_ombre_et_code_inconnu() (+12 more)

### Community 18 - "numpy"
Cohesion: 0.20
Nodes (6): elevation_sample(), _pixel_labels(), _read_window(), _sector_index(), _slope_aspect(), _surface_factors()

### Community 19 - "feature_request"
Cohesion: 0.04
Nodes (73): Pacer, get_class(), needs_priority_field(), convert_length(), add_to_memory(), area_m2(), area_method(), dissolved_areas() (+65 more)

### Community 20 - "JobManager"
Cohesion: 0.18
Nodes (4): Job, JobManager, test_jobmanager_double_finalization_error_fails_job(), test_start_refuse_sur_un_gestionnaire_detache()

### Community 21 - "test_jobs.py"
Cohesion: 0.15
Nodes (25): PreparationCancelledError, _audited(), make_obia(), _req(), test_annulation_obia_detachee_attend_le_callback_reel(), test_audit_retained_output_for_direct_tool_error(), refuse_structure(), test_audit_retained_output_requires_structured_text() (+17 more)

### Community 22 - "collections_abc"
Cohesion: 0.09
Nodes (19): distinct_colors(), interpolate_ramp(), to_hex(), validate_colors(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes() (+11 more)

### Community 23 - "json"
Cohesion: 0.19
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "test_project_audit.py"
Cohesion: 0.32
Nodes (13): layer_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique(), test_projet_sain_sans_anomalie() (+5 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.10
Nodes (11): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+3 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.30
Nodes (12): crash(), double(), make(), metier(), _req(), supprimer(), test_destroy_with_confirmation(), test_errors() (+4 more)

### Community 27 - "FakeExecutor"
Cohesion: 0.10
Nodes (11): note(), effacer(), FakeExecutor, job_invalide(), mesure_invalide(), test_cancel_all_continues_after_one_job_fails(), test_echec_de_fermeture_detache_reste_un_echec_technique(), test_job_lance_pendant_la_confirmation() (+3 more)

### Community 28 - "compute_breaks"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "test_bridge_lifecycle.py"
Cohesion: 0.09
Nodes (32): critical(), fake_remove(), fake_write(), FakeDispatcher, FakeListener, FakeSocket, make_bridge(), patched() (+24 more)

### Community 30 - "json"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "test_object_features.py"
Cohesion: 0.10
Nodes (35): _adjacency(), extract_object_features(), ObjectFeatures, _pixel_area(), assert_invariants(), assert_matches_oracle(), _FloatSubclass, _IntSubclass (+27 more)

### Community 32 - "dev_setup.py"
Cohesion: 0.13
Nodes (17): bump_version(), main(), read_metadata(), write_repository(), write_version(), check_python(), ensure_venv(), has_native_stubs() (+9 more)

### Community 33 - "re"
Cohesion: 0.06
Nodes (29): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), _columns() (+21 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.11
Nodes (16): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), _as_multipolygon(), _closer_parts(), records(), test_egalite_stable() (+8 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "ProcessingExecutor"
Cohesion: 0.08
Nodes (11): AlgCall, LandcoverPreparationTask, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, forget() (+3 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.16
Nodes (9): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), test_liste_blanche(), test_recherche_multi_termes(), test_recherche_par_categorie() (+1 more)

### Community 38 - "test_double_rmtree_en_echec"
Cohesion: 0.33
Nodes (4): _failing_write(), test_double_nettoyage_impossible_apres_annulation(), test_double_rmtree_en_echec(), blocked()

### Community 39 - "Distances"
Cohesion: 0.13
Nodes (13): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), to_float(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible() (+5 more)

### Community 41 - "Historique des styles"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "dataclasses"
Cohesion: 0.10
Nodes (26): FeatureExtractionControl, _load_features(), persist_delineation(), _snapshot(), _write_units(), _check(), _dataset(), _diagnostics() (+18 more)

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.11
Nodes (22): build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees() (+14 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.18
Nodes (12): Criterion, level_for(), level_number(), Override, parse_criteria(), parse_overrides(), parse_thresholds(), score() (+4 more)

### Community 46 - "core/zoning.py"
Cohesion: 0.18
Nodes (8): cache_matches(), cache_meta(), for_territory(), _inpn(), service_label(), Zoning, test_cache_meta_roundtrip_and_matching(), test_par_territoire()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "logging"
Cohesion: 0.24
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 49 - "check_surfaces.py"
Cohesion: 0.17
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 50 - "test_fields.py"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+10 more)

### Community 51 - "Tests zonage"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 52 - "test_prepare_landcover_tool.py"
Cohesion: 0.06
Nodes (47): foreign_pyqgis_reason(), skip_if_foreign_pyqgis(), isolated_guard(), make_task(), _obia_job(), tool(), patched(), Recorder (+39 more)

### Community 53 - "PreparationControl"
Cohesion: 0.12
Nodes (16): PreparationControl, SegmentationControl, test_callback_failure_is_not_hidden(), test_cancellation_before_callback(), test_cancellation_check_failure_is_not_hidden(), test_cancellation_requested_during_callback(), progress(), test_default_control_does_nothing() (+8 more)

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "test_landcover_guard.py"
Cohesion: 0.20
Nodes (15): expect_busy(), in_thread(), is_free(), isolated_property(), patched(), step(), test_executor_addtask_refusal_releases_guard(), test_executor_constructor_failure_releases_guard() (+7 more)

### Community 56 - "ErrorCode"
Cohesion: 0.06
Nodes (46): ToolResult, describe_summary(), ErrorCode, begin_edit(), field_type_name(), geometry_from_wkt(), get_vector_layer(), is_shapefile() (+38 more)

### Community 57 - "test_landcover_segment.py"
Cohesion: 0.09
Nodes (37): _masked_gaussian(), _positive_float(), segment_rgb(), SlicConfig, assert_contract(), forbidden_slic(), irregular_mask_with_hole(), raises() (+29 more)

### Community 58 - "ToolRegistry"
Cohesion: 0.11
Nodes (5): PermissionPolicy, ToolRegistry, Env, Env, _wkt()

### Community 59 - "ToolError"
Cohesion: 0.05
Nodes (22): ToolError, export_atlas_pdf(), _from_template(), expression_context(), prepare_expression(), export_map_image(), export_table(), _project_target() (+14 more)

### Community 60 - "run_cleanup_steps"
Cohesion: 0.14
Nodes (6): run_cleanup_steps(), test_cleanup_accepts_empty_sequence(), test_cleanup_collects_multiple_errors(), test_cleanup_continues_after_failure(), test_cleanup_does_not_swallow_process_interruptions(), test_cleanup_executes_every_step_in_order()

### Community 61 - "test_landcover_delineate.py"
Cohesion: 0.12
Nodes (19): DelineationControl, _run_features(), _band(), _delineate(), Recorder, test_caracteristiques_controle_de_type_incorrect(), test_double_echec_de_vectorisation_nettoie(), test_double_unite_morcelee_refusee() (+11 more)

### Community 62 - "test_landcover_merge.py"
Cohesion: 0.27
Nodes (10): _merge(), _tables(), test_arete_inconnue_refusee(), test_egalite_de_couleur_frontiere_la_plus_longue(), test_ilot_isole_conserve(), test_independance_de_l_ordre(), test_moyenne_ponderee_apres_fusion(), test_sans_fusion() (+2 more)

### Community 63 - "make"
Cohesion: 0.10
Nodes (18): boucle(), calcul(), erreur_avant(), lecture(), make(), sans_etape(), telechargement(), test_annulation() (+10 more)

### Community 64 - "qgis_pyqt_qtcore"
Cohesion: 0.16
Nodes (3): acquire_landcover_guard(), release(), _application()

### Community 65 - "_finish_detached_job"
Cohesion: 0.22
Nodes (9): DetachedJobOutcome, _detail_text(), _finish_detached_job(), test_outcome_annulation_tardive_conserve_le_repertoire(), test_outcome_details_de_l_erreur_principale_prioritaires(), test_outcome_n_extrait_jamais_un_chemin_du_message(), test_outcome_rejette_les_chemins_non_textuels(), test_outcome_repli_sur_le_resultat() (+1 more)

### Community 66 - "jobs.py"
Cohesion: 0.10
Nodes (5): SegmentLandcover, DelineationCancelledError, FeatureExtractionCancelledError, SegmentationCancelledError, LandcoverSegmentationTask

### Community 67 - "run_qgis_integration.py"
Cohesion: 0.17
Nodes (8): bootstrap(), build_bundle(), command(), _fail(), find_launcher(), isolated_env(), main(), probe()

### Community 68 - "tools/landcover.py"
Cohesion: 0.07
Nodes (20): _absolute_paths(), DelineateLandcover, ExtractLandcoverFeatures, DelineationConfig, _build_segmentation_step(), _checked_parent(), delineate_landcover(), _ellipsoidal_total() (+12 more)

### Community 69 - "test_detached_landcover_task.py"
Cohesion: 0.14
Nodes (25): PrepareLandcover, PreparationConfig, _crs_wkt(), expect_busy_start(), guard_free(), isolated(), make_obia_dispatcher(), obia() (+17 more)

### Community 70 - "normalize"
Cohesion: 0.18
Nodes (7): apply_mapping(), normalize(), to_ascii(), test_apply_mapping_insensible_aux_accents(), test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

### Community 71 - "test_connection.py"
Cohesion: 0.18
Nodes (11): conn_file(), _deny_unlink(), test_invalid_json_ignored_by_default(), test_invalid_json_raises_in_strict_mode(), test_missing_file_is_accepted(), test_other_instance_file_is_kept(), test_permission_error_on_delete_is_silent_by_default(), test_permission_error_on_delete_raises_in_strict_mode() (+3 more)

### Community 72 - "app.py"
Cohesion: 0.15
Nodes (9): call_tool(), _cancel_and_observe(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job() (+1 more)

### Community 73 - "BridgeResult"
Cohesion: 0.17
Nodes (10): BridgeResult, CatalogClient, FakeClient, test_catalogue_relu_seulement_si_le_pont_change(), test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat() (+2 more)

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "_Sampler"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "normalize"
Cohesion: 0.09
Nodes (19): classes_for(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match(), suggest_mapping() (+11 more)

### Community 78 - "ToolResult"
Cohesion: 0.05
Nodes (40): looks_like_mojibake(), detect_territory(), Territory, _overview_extent(), clean_number(), crs_from_text(), crs_info(), enum_name() (+32 more)

### Community 79 - "pytest"
Cohesion: 0.10
Nodes (33): LandcoverConfig, resolve_output_parent(), validate_rgb_bands(), _alias(), root(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config() (+25 more)

### Community 80 - "find_source_file"
Cohesion: 0.13
Nodes (9): find_source_file(), referentials_directory(), Source, sources_for(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent() (+1 more)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "pathlib"
Cohesion: 0.18
Nodes (4): new_token(), remove_connection_file(), write_connection_file(), remove_and_release_connection()

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "check_geometries"
Cohesion: 0.20
Nodes (4): check_geometries(), _error_kind(), geometry_report(), select_features()

### Community 85 - "math"
Cohesion: 0.10
Nodes (23): correlate(), correlation_pairs(), correlation_pvalue(), describe_categorical(), describe_full(), interpret_shape(), linear_fit(), pearson() (+15 more)

### Community 86 - "_cached_source"
Cohesion: 0.20
Nodes (6): bbox_covers(), should_replace_cache(), _bbox_wgs84(), _cached_source(), Source, test_bbox_rules()

### Community 89 - "Pause"
Cohesion: 0.28
Nodes (6): Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

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
Cohesion: 0.26
Nodes (5): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 107 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 108 - "styling.py"
Cohesion: 0.12
Nodes (18): _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _distinct_values(), _kind() (+10 more)

### Community 109 - "core/impacts.py"
Cohesion: 0.17
Nodes (9): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), test_anneaux(), test_comparaison_variantes(), test_poids_enjeu() (+1 more)

### Community 110 - "units.py"
Cohesion: 0.47
Nodes (3): convert_area(), test_conversions(), test_unknown_unit()

### Community 111 - "core/project_audit.py"
Cohesion: 0.16
Nodes (12): audit(), build_sections(), duplicate_name_findings(), _finding(), add(), project_findings(), severity_counts(), verdict() (+4 more)

### Community 113 - "test_landcover_delineation.py"
Cohesion: 0.40
Nodes (3): test_annulation_specifique(), test_config_bornes_acceptees(), test_config_refusee()

### Community 114 - "_prepare"
Cohesion: 0.15
Nodes (11): case(), _full_aoi(), islands(), _islands_mask(), _prepare(), sample(), _texture(), _chain() (+3 more)

### Community 115 - "test_jobs.py"
Cohesion: 0.10
Nodes (34): _detached(), _outcome(), _segment_step(), _segmentation_manager(), generator(), _spy_manager(), finisher(), generator() (+26 more)

### Community 116 - "BridgeServer"
Cohesion: 0.12
Nodes (6): Response, BridgeServer, Dispatcher, finish(), collecting(), render_notes()

### Community 117 - "core/atlas.py"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 118 - "Recorder"
Cohesion: 0.15
Nodes (6): Recorder, test_double_annulation_tardive_apres_99(), test_double_slic_annule_puis_echoue(), test_double_slic_demande_l_annulation(), test_real_annulation_a_99_supprime_le_temporaire(), test_real_controle_sequence_exacte()

### Community 119 - "correlation_matrix"
Cohesion: 0.19
Nodes (6): is_sensitive_field(), mask_sensitive(), sensitive_fields(), correlation_matrix(), test_mask_sensitive_hides_only_sensitive_values(), test_sensitive_fields_in_filter_columns()

### Community 120 - "Zoning"
Cohesion: 0.18
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_root_env_override()

### Community 121 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 122 - "run_to_project"
Cohesion: 0.05
Nodes (26): _allowed(), describe_algorithm(), list_algorithms(), run_algorithm(), _isopleths(), kernel_density_points(), _style(), buffer() (+18 more)

### Community 123 - "_rewrite"
Cohesion: 0.18
Nodes (18): _analysis_outside_validity(), _implicit_mask(), _read_bands(), _rewrite(), _rgb_mask_differs(), _rgb_without_photometric(), _set_pixel(), mutate() (+10 more)

### Community 126 - "pyqgis.py"
Cohesion: 0.09
Nodes (11): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+3 more)

### Community 130 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 132 - "describe_groups"
Cohesion: 0.22
Nodes (6): describe(), describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 136 - "ping"
Cohesion: 0.27
Nodes (3): ping(), build_details(), confirm()

### Community 137 - "assess"
Cohesion: 0.40
Nodes (3): assess(), zoning_state(), test_pre_diagnostic()

### Community 138 - "test_landcover_persist.py"
Cohesion: 0.10
Nodes (20): _altered_reread(), _edit_manifest(), _failing_close(), _failing_replace(), _manifest(), _other_crs(), _read_segments(), _subprocess() (+12 more)

### Community 140 - "math"
Cohesion: 0.18
Nodes (4): _validate_number(), fractal_dimension(), kurtosis(), skewness()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1051 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `common.py`, `test_segment_landcover_tool.py`, `tools/coefficients.py`, `test_landcover_segmentation_task.py`, `numpy`, `feature_request`, `JobManager`, `test_jobs.py`, `json`, `test_dispatcher.py`, `FakeExecutor`, `test_bridge_lifecycle.py`, `ProcessingExecutor`, `Schéma des paramètres`, `test_prepare_landcover_tool.py`, `test_landcover_guard.py`, `ErrorCode`, `ToolRegistry`, `make`, `qgis_pyqt_qtcore`, `_finish_detached_job`, `jobs.py`, `tools/landcover.py`, `test_detached_landcover_task.py`, `ToolResult`, `find_source_file`, `check_geometries`, `render_map`, `styling.py`, `core/project_audit.py`, `test_jobs.py`, `BridgeServer`, `correlation_matrix`, `run_to_project`, `pyqgis.py`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 116 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 116 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05450372920252438 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `tools/webservices.py`, `common.py`, `test_segment_landcover_tool.py`, `tools/coefficients.py`, `test_landcover_segmentation_task.py`, `numpy`, `feature_request`, `JobManager`, `test_jobs.py`, `json`, `test_dispatcher.py`, `FakeExecutor`, `test_bridge_lifecycle.py`, `ProcessingExecutor`, `Schéma des paramètres`, `test_prepare_landcover_tool.py`, `test_landcover_guard.py`, `ToolRegistry`, `ToolError`, `make`, `qgis_pyqt_qtcore`, `_finish_detached_job`, `jobs.py`, `tools/landcover.py`, `test_detached_landcover_task.py`, `ToolResult`, `find_source_file`, `check_geometries`, `render_map`, `styling.py`, `core/project_audit.py`, `test_jobs.py`, `BridgeServer`, `correlation_matrix`, `run_to_project`, `pyqgis.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 176 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 176 INFERRED edges - model-reasoned connections that need verification._
- **Should `report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10967741935483871 - nodes in this community are weakly interconnected._