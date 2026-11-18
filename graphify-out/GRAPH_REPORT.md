# Graph Report - cynogis  (2026-11-18)

## Corpus Check
- 163 files · ~131,603 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2919 nodes · 8600 edges · 136 communities (110 shown, 26 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 904 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `efaa00b2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BridgeResult
- tools/webservices.py
- report.py
- common.py
- geometry_report
- test_landcover_prepare.py
- _rewrite
- Métriques paysagères
- Documentation projet
- habitat_typology_join
- shapefile.py
- test_landcover_segmentation_task.py
- prepare.py
- numpy
- Coefficients de surface
- colors.py
- CynogisPlugin
- core/referentials.py
- _segmentation_manager
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
- check_surfaces.py
- common.py
- Tests zonage
- test_prepare_landcover_tool.py
- PreparationControl
- Feuille de route
- test_landcover_guard.py
- ToolResult
- test_landcover_segment.py
- Dispatcher
- ErrorCode
- plugin.py
- erc_variant_compare
- Plan d'échantillonnage
- test_landcover_task_finished.py
- ToolError
- Pause
- Provenance
- test_jobs.py
- Zoning
- test_detached_landcover_task.py
- privacy.py
- test_connection.py
- app.py
- BridgeResult
- Guide d'installation
- SegmentLandcover
- Règles métier réglementaires
- core/landscape.py
- render_map
- pytest
- find_source_file
- Règles d'architecture
- re
- Adding a tool (@tool decorator, Param, docstring)
- pyqgis.py
- regulatory_zoning_intersect
- core/zoning.py
- LandcoverPreparationTask
- Commandes de dev
- _prepare
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
- core/impacts.py
- ToolResult
- core/project_audit.py
- _status
- _finish_detached_job
- _closer_parts
- geometry_kind
- dispatcher.py
- segment.py
- Recorder
- to_json_value
- Zoning
- _spy_manager
- test_double_rmtree_en_echec
- inspect_landcover_inputs
- PrepareLandcover
- Rule
- risky_names
- list_coefficients
- RefusingTaskManager
- SlicSpy
- age_days
- _overlay
- ping
- landcover_guard.py
- _altered_reread
- test_real_module_import_does_not_load_slic

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 227 edges
2. `ErrorCode` - 207 edges
3. `ToolResult` - 111 edges
4. `get_vector_layer()` - 103 edges
5. `feature_request()` - 73 edges
6. `geometry_kind()` - 60 edges
7. `require_field()` - 56 edges
8. `Level` - 52 edges
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

## Communities (136 total, 26 thin omitted)

### Community 0 - "BridgeResult"
Cohesion: 0.21
Nodes (11): app(), install_client(), ScriptedClient, test_bridge_failure_does_not_confirm_stop(), test_cancel_waits_for_final_confirmation(), test_cleanup_error_is_not_reported_as_clean_cancellation(), test_job_completed_before_cancellation_took_effect(), test_late_cancellation_preserves_output_details() (+3 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.06
Nodes (46): is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+38 more)

### Community 2 - "report.py"
Cohesion: 0.10
Nodes (22): format_number(), build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows() (+14 more)

### Community 3 - "common.py"
Cohesion: 0.07
Nodes (28): unique_field_name(), tool(), Param, detect_territory(), Territory, add_to_memory(), extent_wgs84(), make_field() (+20 more)

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.12
Nodes (25): _crs(), _DerivedControl, _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs() (+17 more)

### Community 6 - "_rewrite"
Cohesion: 0.22
Nodes (13): _analysis_outside_validity(), _implicit_mask(), _read_bands(), _rewrite(), _rgb_mask_differs(), _rgb_without_photometric(), _set_pixel(), mutate() (+5 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "habitat_typology_join"
Cohesion: 0.15
Nodes (6): find_file(), name_key(), open_table(), _sibling(), test_open_table_zip(), test_versions_aligned()

### Community 10 - "shapefile.py"
Cohesion: 0.08
Nodes (25): truncate_field_names(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages() (+17 more)

### Community 11 - "test_landcover_segmentation_task.py"
Cohesion: 0.10
Nodes (40): _abort(), _aoi_wkb(), _blocking(), controlled_until_cancelled(), expect_busy(), guard_free(), isolated(), make_dispatcher() (+32 more)

### Community 12 - "prepare.py"
Cohesion: 0.23
Nodes (9): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+1 more)

### Community 13 - "numpy"
Cohesion: 0.15
Nodes (7): _diagnostics(), _isopleth_geometries(), _isopleths(), _style(), _pixel_labels(), _slope_aspect(), _surface_factors()

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (25): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+17 more)

### Community 15 - "colors.py"
Cohesion: 0.08
Nodes (19): contrast_ratio(), darken(), lighten(), mix(), parse_color(), readable_text_color(), relative_luminance(), to_rgba_string() (+11 more)

### Community 16 - "CynogisPlugin"
Cohesion: 0.11
Nodes (6): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin, remove_and_release_connection()

### Community 17 - "core/referentials.py"
Cohesion: 0.13
Nodes (18): check_rules(), _covers(), map_cirad(), map_feature(), map_ocsge(), _segments(), test_cirad_974_2020_ombre_et_code_inconnu(), test_cirad_974_2020_par_code() (+10 more)

### Community 18 - "_segmentation_manager"
Cohesion: 0.14
Nodes (16): _segment_step(), _segmentation_manager(), generator(), test_i1_reponse_finale_inconnue(), test_segment_annulation_attend_le_callback_et_reste_idempotente(), test_segment_annulation_depuis_qgis_sans_demande(), test_segment_annulation_tardive_conserve_la_sortie(), test_segment_detachee_erreur_technique_reste_un_echec() (+8 more)

### Community 19 - "feature_request"
Cohesion: 0.08
Nodes (23): convert_length(), distance_area(), feature_request(), iter_geometries(), kernel_density_points(), _collect(), count_observations(), count_points_in_polygon() (+15 more)

### Community 21 - "Tests des jobs"
Cohesion: 0.18
Nodes (20): PreparationCancelledError, make_obia(), _req(), test_annulation_obia_detachee_attend_le_callback_reel(), test_callback_tardif_detache_ne_finalise_pas_deux_fois(), test_callbacks_de_terminaison_restent_raccordes(), test_detachement_ne_demande_aucune_annulation_ni_ne_change_le_statut(), test_double_detachement_sans_effet_supplementaire() (+12 more)

### Community 22 - "collections_abc"
Cohesion: 0.09
Nodes (19): distinct_colors(), interpolate_ramp(), to_hex(), validate_colors(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes() (+11 more)

### Community 23 - "json"
Cohesion: 0.18
Nodes (7): decode_request(), _protocol_error(), _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "math"
Cohesion: 0.10
Nodes (24): correlate(), correlation_pairs(), correlation_pvalue(), describe_categorical(), describe_full(), interpret_shape(), kurtosis(), linear_fit() (+16 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.11
Nodes (10): EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible(), test_describe_summary_vide() (+2 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "FakeExecutor"
Cohesion: 0.11
Nodes (9): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_cancel_all_continues_after_one_job_fails(), test_echec_de_fermeture_detache_reste_un_echec_technique(), generator(), test_notes_ajoutees_aux_warnings() (+1 more)

### Community 28 - "compute_breaks"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "fields.py"
Cohesion: 0.13
Nodes (16): coerce_record(), coerce_value(), _parse_date(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict(), test_coerce_value(), test_coerce_value_date_invalide() (+8 more)

### Community 30 - "audit.py"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.13
Nodes (8): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 32 - "dev_setup.py"
Cohesion: 0.22
Nodes (12): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+4 more)

### Community 33 - "Données terrain CSV"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.16
Nodes (14): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus(), test_half_plane_contient_le_milieu_cote_a() (+6 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "tasks.py"
Cohesion: 0.10
Nodes (11): AlgCall, Fetch, LandcoverSegmentationTask, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor (+3 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.10
Nodes (14): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), to_ascii(), test_liste_blanche() (+6 more)

### Community 38 - "_run"
Cohesion: 0.07
Nodes (39): _edit_manifest(), _failing_close(), _failing_replace(), _keep(), _kernel(), _manifest(), _read_segments(), _run() (+31 more)

### Community 39 - "Distances"
Cohesion: 0.11
Nodes (14): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), to_float(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible() (+6 more)

### Community 40 - "persist.py"
Cohesion: 0.25
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
Cohesion: 0.11
Nodes (22): build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees() (+14 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.18
Nodes (12): Criterion, level_for(), level_number(), Override, parse_criteria(), parse_overrides(), parse_thresholds(), score() (+4 more)

### Community 46 - "fetch_wfs_layer"
Cohesion: 0.23
Nodes (6): service_label(), _bbox_wgs84(), _cached_source(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.18
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "describe"
Cohesion: 0.28
Nodes (5): describe(), describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum()

### Community 49 - "check_surfaces.py"
Cohesion: 0.18
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 50 - "common.py"
Cohesion: 0.11
Nodes (18): clean_number(), crs_info(), enum_name(), file_format(), layer_kind(), source_path(), territory_info(), get_layer_info() (+10 more)

### Community 51 - "Tests zonage"
Cohesion: 0.15
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 52 - "test_prepare_landcover_tool.py"
Cohesion: 0.14
Nodes (21): abort_test_process(), Env, environment(), final_response(), done(), make_geotiff(), params(), patched() (+13 more)

### Community 53 - "PreparationControl"
Cohesion: 0.11
Nodes (17): PreparationControl, SegmentationCancelledError, SegmentationControl, test_callback_failure_is_not_hidden(), test_cancellation_before_callback(), test_cancellation_check_failure_is_not_hidden(), test_cancellation_requested_during_callback(), progress() (+9 more)

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "test_landcover_guard.py"
Cohesion: 0.19
Nodes (15): expect_busy(), in_thread(), is_free(), isolated_property(), patched(), step(), test_executor_addtask_refusal_releases_guard(), test_executor_constructor_failure_releases_guard() (+7 more)

### Community 56 - "ToolResult"
Cohesion: 0.07
Nodes (42): ToolResult, check_batch_size(), describe_summary(), FieldType, resolve_type(), begin_edit(), geometry_from_wkt(), get_vector_layer() (+34 more)

### Community 57 - "test_landcover_segment.py"
Cohesion: 0.14
Nodes (30): segment_rgb(), SlicConfig, assert_contract(), forbidden_slic(), irregular_mask_with_hole(), raises(), random_rgb(), rng() (+22 more)

### Community 58 - "Dispatcher"
Cohesion: 0.11
Nodes (7): Request, Response, BridgeServer, Dispatcher, finish(), collecting(), render_notes()

### Community 59 - "ErrorCode"
Cohesion: 0.07
Nodes (27): ErrorCode, clean_name(), unique_path(), mentions_natura2000(), export_atlas_pdf(), _from_template(), _overview_extent(), crs_from_text() (+19 more)

### Community 60 - "plugin.py"
Cohesion: 0.08
Nodes (11): run_cleanup_steps(), QgsLogHandler, setup_logging(), teardown_logging(), Cynogis Plugin Icon (icon.svg), Green Map Location Pin, test_cleanup_accepts_empty_sequence(), test_cleanup_collects_multiple_errors() (+3 more)

### Community 61 - "erc_variant_compare"
Cohesion: 0.24
Nodes (6): _check_layers(), _distances(), erc_variant_compare(), impact_quantification(), _intersect(), _zones()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "test_landcover_task_finished.py"
Cohesion: 0.12
Nodes (17): isolated_guard(), make_task(), _obia_job(), tool(), patched(), Recorder, spin(), step() (+9 more)

### Community 64 - "ToolError"
Cohesion: 0.06
Nodes (27): ToolError, _allowed(), describe_algorithm(), list_algorithms(), run_algorithm(), get_raster_layer(), check_landscape(), compute_ndvi() (+19 more)

### Community 65 - "Pause"
Cohesion: 0.28
Nodes (6): Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 66 - "Provenance"
Cohesion: 0.18
Nodes (9): describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_describe_multiple_sources_and_missing(), test_pre_diagnostic(), test_prescan_sections_lists_sources_with_origin() (+1 more)

### Community 67 - "test_jobs.py"
Cohesion: 0.12
Nodes (22): boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), sans_etape(), telechargement() (+14 more)

### Community 68 - "Zoning"
Cohesion: 0.20
Nodes (7): cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, test_cache_meta_roundtrip_and_matching(), test_par_territoire()

### Community 69 - "test_detached_landcover_task.py"
Cohesion: 0.25
Nodes (15): guard_free(), isolated(), make_sample(), patched(), _req(), spin(), start_job(), stop_tasks() (+7 more)

### Community 70 - "privacy.py"
Cohesion: 0.23
Nodes (6): is_sensitive_field(), mask_sensitive(), sensitive_fields(), test_mask_sensitive_hides_only_sensitive_values(), test_sensitive_fields_in_filter_columns(), test_sensitive()

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

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "core/landscape.py"
Cohesion: 0.08
Nodes (22): apply_mapping(), classes_for(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register() (+14 more)

### Community 78 - "render_map"
Cohesion: 0.17
Nodes (4): render_map(), _open_project(), _overview_map(), _project_facts()

### Community 79 - "pytest"
Cohesion: 0.10
Nodes (28): LandcoverConfig, PreparationConfig, _validate_number(), validate_rgb_bands(), obia_prepare_test(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config() (+20 more)

### Community 80 - "find_source_file"
Cohesion: 0.10
Nodes (11): find_source_file(), referentials_directory(), Source, sources_for(), _clipped(), list_reference_sources(), _open(), test_fichier_cirad_sous_son_nom_d_origine() (+3 more)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "re"
Cohesion: 0.21
Nodes (10): _columns(), match_taxa(), read_statuses(), Statuses, Taxon, listed(), _values(), test_match_taxa() (+2 more)

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "pyqgis.py"
Cohesion: 0.15
Nodes (5): _as_generator(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm()

### Community 85 - "regulatory_zoning_intersect"
Cohesion: 0.25
Nodes (4): fetch_wfs_layer(), _is_cancel(), regulatory_prescan(), regulatory_zoning_intersect()

### Community 86 - "core/zoning.py"
Cohesion: 0.19
Nodes (5): assess(), bbox_covers(), should_replace_cache(), zoning_state(), test_bbox_rules()

### Community 89 - "_prepare"
Cohesion: 0.22
Nodes (8): _full_aoi(), islands(), _islands_mask(), _other_crs(), _prepare(), sample(), _texture(), _wkt()

### Community 99 - "test_bridge_lifecycle.py"
Cohesion: 0.06
Nodes (35): Bar, critical(), fake_remove(), fake_write(), FakeBridgeServer, FakeDispatcher, FakeListener, FakeSocket (+27 more)

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

### Community 107 - "build_plugin.py"
Cohesion: 0.24
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 108 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 109 - "core/impacts.py"
Cohesion: 0.17
Nodes (9): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), test_anneaux(), test_comparaison_variantes(), test_poids_enjeu() (+1 more)

### Community 110 - "ToolResult"
Cohesion: 0.11
Nodes (20): range_labels(), _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _distinct_values() (+12 more)

### Community 111 - "core/project_audit.py"
Cohesion: 0.15
Nodes (23): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+15 more)

### Community 112 - "_status"
Cohesion: 0.26
Nodes (11): _detached(), _outcome(), finisher(), _status(), test_i1_diagnostic_avec_statut_inattendu(), test_i1_echec_jamais_declasse_ni_code_inconnu_rejete(), test_i1_erreur_technique_apres_detachement(), test_i1_interrogations_repetees_stables() (+3 more)

### Community 113 - "_finish_detached_job"
Cohesion: 0.22
Nodes (9): DetachedJobOutcome, _detail_text(), _finish_detached_job(), test_outcome_annulation_tardive_conserve_le_repertoire(), test_outcome_details_de_l_erreur_principale_prioritaires(), test_outcome_n_extrait_jamais_un_chemin_du_message(), test_outcome_rejette_les_chemins_non_textuels(), test_outcome_repli_sur_le_resultat() (+1 more)

### Community 115 - "geometry_kind"
Cohesion: 0.07
Nodes (31): Pacer, needs_priority_field(), convert_area(), compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer() (+23 more)

### Community 116 - "dispatcher.py"
Cohesion: 0.09
Nodes (3): Executor, Level, register_detail_provider()

### Community 118 - "Recorder"
Cohesion: 0.14
Nodes (6): Recorder, test_double_annulation_tardive_apres_99(), test_double_slic_annule_puis_echoue(), test_double_slic_demande_l_annulation(), test_real_annulation_a_99_supprime_le_temporaire(), test_real_controle_sequence_exacte()

### Community 119 - "to_json_value"
Cohesion: 0.08
Nodes (14): field_type_name(), to_json_value(), check_geometries(), _geometry_repr(), get_features(), get_field_values(), select_features(), _read() (+6 more)

### Community 120 - "Zoning"
Cohesion: 0.18
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_root_env_override()

### Community 121 - "_spy_manager"
Cohesion: 0.40
Nodes (5): _spy_manager(), generator(), test_apres_detachement_le_finisseur_n_est_plus_appele(), test_sans_detachement_le_finisseur_normal_est_appele(), test_succes_detache_sans_sortie_complete()

### Community 122 - "test_double_rmtree_en_echec"
Cohesion: 0.33
Nodes (4): _failing_write(), test_double_nettoyage_impossible_apres_annulation(), test_double_rmtree_en_echec(), blocked()

### Community 123 - "inspect_landcover_inputs"
Cohesion: 0.19
Nodes (5): _build_preparation_step(), inspect_landcover_inputs(), prepare_landcover_inputs(), _read_aoi_geometry(), _reject()

### Community 124 - "PrepareLandcover"
Cohesion: 0.29
Nodes (6): PrepareLandcover, _crs_wkt(), expect_busy_start(), make_obia_dispatcher(), obia(), tool()

### Community 126 - "risky_names"
Cohesion: 0.24
Nodes (6): blocking_calls(), risky_names(), _details(), test_appels_bloquants(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 131 - "_overlay"
Cohesion: 0.29
Nodes (3): is_agricultural(), _overlay(), test_is_agricultural()

### Community 133 - "landcover_guard.py"
Cohesion: 0.50
Nodes (3): acquire_landcover_guard(), release(), _application()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 956 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `common.py`, `landcover_guard.py`, `shapefile.py`, `test_landcover_segmentation_task.py`, `_segmentation_manager`, `feature_request`, `JobManager`, `json`, `test_dispatcher.py`, `FakeExecutor`, `ToolRegistry`, `tasks.py`, `fetch_wfs_layer`, `Schéma des paramètres`, `common.py`, `test_landcover_guard.py`, `ToolResult`, `Dispatcher`, `ErrorCode`, `plugin.py`, `erc_variant_compare`, `test_landcover_task_finished.py`, `test_jobs.py`, `render_map`, `find_source_file`, `pyqgis.py`, `regulatory_zoning_intersect`, `test_bridge_lifecycle.py`, `ToolResult`, `_status`, `_finish_detached_job`, `geometry_kind`, `dispatcher.py`, `to_json_value`, `inspect_landcover_inputs`, `PrepareLandcover`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Are the 110 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 110 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05822784810126582 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `tools/webservices.py`, `common.py`, `landcover_guard.py`, `shapefile.py`, `test_landcover_segmentation_task.py`, `_segmentation_manager`, `feature_request`, `JobManager`, `json`, `test_dispatcher.py`, `FakeExecutor`, `ToolRegistry`, `tasks.py`, `Schéma des paramètres`, `common.py`, `test_landcover_guard.py`, `ToolResult`, `Dispatcher`, `plugin.py`, `erc_variant_compare`, `test_landcover_task_finished.py`, `ToolError`, `test_jobs.py`, `render_map`, `find_source_file`, `pyqgis.py`, `regulatory_zoning_intersect`, `test_bridge_lifecycle.py`, `ToolResult`, `_status`, `_finish_detached_job`, `geometry_kind`, `dispatcher.py`, `to_json_value`, `inspect_landcover_inputs`, `PrepareLandcover`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Are the 164 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 164 INFERRED edges - model-reasoned connections that need verification._
- **Should `report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09803921568627451 - nodes in this community are weakly interconnected._