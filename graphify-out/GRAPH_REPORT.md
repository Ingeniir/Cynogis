# Graph Report - cynogis  (2026-11-11)

## Corpus Check
- 156 files · ~117,721 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2588 nodes · 7602 edges · 123 communities (98 shown, 25 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 739 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e6667b3a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BridgeResult
- tools/webservices.py
- report.py
- ToolResult
- geometry_report
- test_landcover_prepare.py
- ToolError
- Métriques paysagères
- Documentation projet
- privacy.py
- shapefile.py
- test_project_audit.py
- prepare.py
- check_surfaces.py
- Coefficients de surface
- colors.py
- CynogisPlugin
- core/referentials.py
- run_to_project
- feature_request
- JobManager
- Tests des jobs
- palettes.py
- json
- stats.py
- Journal d'édition
- test_dispatcher.py
- AlgCall
- compute_breaks
- fields.py
- audit.py
- ToolRegistry
- dev_setup.py
- Données terrain CSV
- Résolution des recouvrements
- allocate
- test_detached_landcover_task.py
- Catalogue d'algorithmes
- tools/project_audit.py
- Distances
- Executor
- Historique des styles
- core/atlas.py
- HABREF
- Tests de style
- core/stakes.py
- fetch_wfs_layer
- Schéma des paramètres
- ProcessingExecutor
- tool
- common.py
- Tests zonage
- add_to_group
- assess
- Feuille de route
- test_landcover_guard.py
- ToolError
- mentions_natura2000
- Dispatcher
- to_float
- run_cleanup_steps
- Cache des zonages
- Plan d'échantillonnage
- test_landcover_task_finished.py
- _vector_facts
- AlgCall
- Provenance
- test_job_lance_pendant_la_confirmation
- test_webservices.py
- _overlay
- core/webservices.py
- test_connection.py
- app.py
- CatalogClient
- Guide d'installation
- list_style_options
- Règles métier réglementaires
- core/landscape.py
- PreparationControl
- pytest
- Territory
- Règles d'architecture
- re
- Adding a tool (@tool decorator, Param, docstring)
- pyqgis.py
- find_source_file
- core/zoning.py
- contrast_ratio
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
- elevation_sample
- Security rules (no bypass, no overwrite, no sensitive species/cadastral data)
- Phase 3 : Tracabilite et confidentialite
- BridgeError
- install.ps1
- list_coefficients
- jobs.py
- core/impacts.py
- prepare_expression
- build_plugin.py
- math
- _finish_detached_job
- os
- core/zoning.py
- logging
- describe
- TaskExecutor
- client.py
- test_version.py
- _sibling
- ping

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 221 edges
2. `ErrorCode` - 199 edges
3. `ToolResult` - 108 edges
4. `get_vector_layer()` - 102 edges
5. `feature_request()` - 73 edges
6. `geometry_kind()` - 60 edges
7. `require_field()` - 56 edges
8. `to_json_value()` - 52 edges
9. `distance_area()` - 51 edges
10. `Level` - 47 edges

## Surprising Connections (you probably didn't know these)
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `3.4 Audit des garde-fous` --semantically_similar_to--> `Security rules (no bypass, no overwrite, no sensitive species/cadastral data)`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `2.3 Exclure Natura 2000` --semantically_similar_to--> `Natura 2000 not applicable in overseas departments`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `2.6 Pre-diagnostic 100 % deterministe` --semantically_similar_to--> `Deterministic pre-diagnostic, never LLM-written`  [INFERRED] [semantically similar]
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

## Communities (123 total, 25 thin omitted)

### Community 0 - "BridgeResult"
Cohesion: 0.17
Nodes (16): BridgeResult, app(), test_wait_job_annule_dans_qgis(), scenario(), install_client(), ScriptedClient, test_bridge_failure_does_not_confirm_stop(), test_cancel_waits_for_final_confirmation() (+8 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.13
Nodes (16): Fetch, capabilities_url(), search_layers(), WebService, wfs_params(), wms_params(), _catalog(), _crs() (+8 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "ToolResult"
Cohesion: 0.13
Nodes (12): clean_name(), unique_path(), Level, tool(), Param, detect_territory(), make_field(), _save_isopleths() (+4 more)

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.14
Nodes (23): _crs(), _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs(), progress() (+15 more)

### Community 6 - "ToolError"
Cohesion: 0.06
Nodes (23): ToolError, build_table(), add_to_memory(), polygon_parts(), export_table(), _project_target(), save_project(), _save_project_details() (+15 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "privacy.py"
Cohesion: 0.23
Nodes (6): is_sensitive_field(), mask_sensitive(), sensitive_fields(), test_mask_sensitive_hides_only_sensitive_values(), test_sensitive_fields_in_filter_columns(), test_sensitive()

### Community 10 - "shapefile.py"
Cohesion: 0.10
Nodes (17): truncate_field_names(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages() (+9 more)

### Community 11 - "test_project_audit.py"
Cohesion: 0.20
Nodes (18): audit(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons() (+10 more)

### Community 12 - "prepare.py"
Cohesion: 0.23
Nodes (9): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+1 more)

### Community 13 - "check_surfaces.py"
Cohesion: 0.17
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (25): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+17 more)

### Community 15 - "colors.py"
Cohesion: 0.10
Nodes (17): darken(), distinct_colors(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), validate_colors() (+9 more)

### Community 17 - "core/referentials.py"
Cohesion: 0.10
Nodes (22): check_rules(), _covers(), map_cirad(), map_feature(), map_ocsge(), Rule, _segments(), Source (+14 more)

### Community 18 - "run_to_project"
Cohesion: 0.05
Nodes (26): unique_field_name(), _allowed(), describe_algorithm(), run_algorithm(), kernel_density_points(), buffer(), dissolve(), extract() (+18 more)

### Community 19 - "feature_request"
Cohesion: 0.09
Nodes (23): convert_length(), feature_request(), iter_geometries(), check_landscape(), _collect(), count_observations(), count_points_in_polygon(), distance_layer() (+15 more)

### Community 20 - "JobManager"
Cohesion: 0.15
Nodes (5): collecting(), Job, JobManager, test_jobmanager_double_finalization_error_fails_job(), test_cancel_all_continues_after_one_job_fails()

### Community 21 - "Tests des jobs"
Cohesion: 0.15
Nodes (31): PreparationCancelledError, make(), make_obia(), _req(), test_annulation(), test_annulation_obia_detachee_attend_le_callback_reel(), test_annulation_pendant_une_pause(), test_boucle_avec_pauses() (+23 more)

### Community 22 - "palettes.py"
Cohesion: 0.10
Nodes (16): interpolate_ramp(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors(), validate_palette() (+8 more)

### Community 23 - "json"
Cohesion: 0.21
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "stats.py"
Cohesion: 0.12
Nodes (21): correlate(), correlation_pairs(), correlation_pvalue(), describe_categorical(), describe_full(), interpret_shape(), linear_fit(), pearson() (+13 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.10
Nodes (11): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+3 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.30
Nodes (12): crash(), double(), make(), metier(), _req(), supprimer(), test_destroy_with_confirmation(), test_errors() (+4 more)

### Community 27 - "AlgCall"
Cohesion: 0.11
Nodes (12): AlgCall, FakeExecutor, _spy_manager(), generator(), test_apres_detachement_le_finisseur_n_est_plus_appele(), test_echec_de_fermeture_detache_reste_un_echec_technique(), generator(), algo() (+4 more)

### Community 28 - "compute_breaks"
Cohesion: 0.11
Nodes (24): clean_values(), compute_breaks(), _dedupe(), equal_interval(), format_number(), natural_breaks(), pretty_breaks(), quantile_breaks() (+16 more)

### Community 29 - "fields.py"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+10 more)

### Community 30 - "audit.py"
Cohesion: 0.25
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.11
Nodes (8): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 32 - "dev_setup.py"
Cohesion: 0.23
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 33 - "Données terrain CSV"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.10
Nodes (17): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), _as_multipolygon(), _closer_parts(), records() (+9 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "test_detached_landcover_task.py"
Cohesion: 0.14
Nodes (25): PrepareLandcover, PreparationConfig, _crs_wkt(), expect_busy_start(), guard_free(), isolated(), make_obia_dispatcher(), obia() (+17 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.09
Nodes (15): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), to_ascii(), list_algorithms() (+7 more)

### Community 38 - "tools/project_audit.py"
Cohesion: 0.11
Nodes (11): build_sections(), severity_counts(), verdict(), _yes_no(), render_map(), write_document(), write_pdf(), audit_project() (+3 more)

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

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
Cohesion: 0.17
Nodes (7): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "ProcessingExecutor"
Cohesion: 0.09
Nodes (8): LandcoverPreparationTask, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, forget(), _take_layers()

### Community 49 - "tool"
Cohesion: 0.06
Nodes (40): Pacer, convert_area(), compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas() (+32 more)

### Community 50 - "common.py"
Cohesion: 0.06
Nodes (29): _overview_extent(), clean_number(), crs_from_text(), crs_info(), enum_name(), extent_wgs84(), get_layer(), get_raster_layer() (+21 more)

### Community 51 - "Tests zonage"
Cohesion: 0.18
Nodes (6): getfeature_url(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 52 - "add_to_group"
Cohesion: 0.47
Nodes (3): add_to_group(), add_to_project(), _output_item()

### Community 53 - "assess"
Cohesion: 0.40
Nodes (3): assess(), zoning_state(), test_pre_diagnostic()

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "test_landcover_guard.py"
Cohesion: 0.15
Nodes (16): expect_busy(), in_thread(), is_free(), isolated_property(), patched(), RefusingTaskManager, step(), test_executor_addtask_refusal_releases_guard() (+8 more)

### Community 56 - "ToolError"
Cohesion: 0.05
Nodes (61): ToolResult, describe_summary(), ErrorCode, begin_edit(), field_type_name(), geometry_from_wkt(), get_vector_layer(), is_shapefile() (+53 more)

### Community 57 - "mentions_natura2000"
Cohesion: 0.24
Nodes (6): is_natura2000_layer(), mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 58 - "Dispatcher"
Cohesion: 0.12
Nodes (5): Response, BridgeServer, Dispatcher, finish(), render_notes()

### Community 60 - "run_cleanup_steps"
Cohesion: 0.11
Nodes (6): run_cleanup_steps(), test_cleanup_accepts_empty_sequence(), test_cleanup_collects_multiple_errors(), test_cleanup_continues_after_failure(), test_cleanup_does_not_swallow_process_interruptions(), test_cleanup_executes_every_step_in_order()

### Community 61 - "Cache des zonages"
Cohesion: 0.18
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.25
Nodes (3): _Sampler, _segment(), _systematic()

### Community 63 - "test_landcover_task_finished.py"
Cohesion: 0.13
Nodes (16): isolated_guard(), make_task(), _obia_job(), tool(), patched(), Recorder, spin(), step() (+8 more)

### Community 64 - "_vector_facts"
Cohesion: 0.13
Nodes (11): file_format(), layer_kind(), source_path(), list_layers(), _summary(), _tree(), _visible(), _layer_facts() (+3 more)

### Community 65 - "AlgCall"
Cohesion: 0.32
Nodes (5): Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), steps()

### Community 66 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 67 - "test_job_lance_pendant_la_confirmation"
Cohesion: 0.10
Nodes (13): note(), boucle(), calcul(), effacer(), erreur_avant(), job_invalide(), lecture(), mesure_invalide() (+5 more)

### Community 68 - "test_webservices.py"
Cohesion: 0.16
Nodes (16): catalog(), choose_crs(), parse_capabilities(), test_catalog_keeps_builtins_and_adds_valid_user_service(), test_catalog_rejects_malformed_file(), test_catalog_rejects_unsafe_or_invalid_entries(), test_choose_crs(), test_lizmap_service_url_keeps_its_query() (+8 more)

### Community 69 - "_overlay"
Cohesion: 0.29
Nodes (3): is_agricultural(), _overlay(), test_is_agricultural()

### Community 70 - "core/webservices.py"
Cohesion: 0.23
Nodes (10): check_url(), _child_text(), _children_text(), _crs_list(), _local(), normalize_crs(), _parse_capabilities(), parse_service() (+2 more)

### Community 71 - "test_connection.py"
Cohesion: 0.18
Nodes (11): conn_file(), _deny_unlink(), test_invalid_json_ignored_by_default(), test_invalid_json_raises_in_strict_mode(), test_missing_file_is_accepted(), test_other_instance_file_is_kept(), test_permission_error_on_delete_is_silent_by_default(), test_permission_error_on_delete_raises_in_strict_mode() (+3 more)

### Community 72 - "app.py"
Cohesion: 0.17
Nodes (7): call_tool(), _cancel_and_observe(), _fetch_specs(), list_tools(), _progress_token(), _to_tool(), _wait_job()

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "core/landscape.py"
Cohesion: 0.08
Nodes (23): apply_mapping(), classes_for(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register() (+15 more)

### Community 78 - "PreparationControl"
Cohesion: 0.22
Nodes (8): PreparationControl, test_callback_failure_is_not_hidden(), test_cancellation_before_callback(), test_cancellation_check_failure_is_not_hidden(), test_cancellation_requested_during_callback(), progress(), test_default_control_does_nothing(), test_progress_is_forwarded()

### Community 79 - "pytest"
Cohesion: 0.12
Nodes (25): LandcoverConfig, validate_rgb_bands(), test_decorator_checks(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config(), test_equal_area_thresholds_are_allowed(), test_extremely_large_number_is_rejected() (+17 more)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "re"
Cohesion: 0.14
Nodes (14): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+6 more)

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "pyqgis.py"
Cohesion: 0.09
Nodes (12): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+4 more)

### Community 85 - "find_source_file"
Cohesion: 0.12
Nodes (8): find_source_file(), referentials_directory(), _clipped(), list_reference_sources(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 86 - "core/zoning.py"
Cohesion: 0.16
Nodes (8): cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, regulatory_prescan(), test_cache_meta_roundtrip_and_matching(), test_par_territoire()

### Community 87 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 99 - "test_bridge_lifecycle.py"
Cohesion: 0.06
Nodes (35): Bar, critical(), fake_remove(), fake_write(), FakeBridgeServer, FakeDispatcher, FakeListener, FakeSocket (+27 more)

### Community 101 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 102 - "elevation_sample"
Cohesion: 0.06
Nodes (29): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+21 more)

### Community 103 - "Security rules (no bypass, no overwrite, no sensitive species/cadastral data)"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 104 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

### Community 105 - "BridgeError"
Cohesion: 0.18
Nodes (8): main(), BridgeError, QgisBridgeClient, FakeClient, test_client_reponse_illisible(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 108 - "jobs.py"
Cohesion: 0.10
Nodes (3): acquire_landcover_guard(), release(), _application()

### Community 109 - "core/impacts.py"
Cohesion: 0.19
Nodes (8): compare_variants(), direct_label(), ring_labels(), stake_weight(), test_anneaux(), test_comparaison_variantes(), test_poids_enjeu(), test_tableau()

### Community 110 - "prepare_expression"
Cohesion: 0.15
Nodes (6): export_atlas_pdf(), _from_template(), expression_context(), prepare_expression(), stake_scoring(), _local_source()

### Community 111 - "build_plugin.py"
Cohesion: 0.27
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 112 - "math"
Cohesion: 0.17
Nodes (5): _validate_number(), kurtosis(), percentile(), skewness(), _cut()

### Community 113 - "_finish_detached_job"
Cohesion: 0.22
Nodes (9): DetachedJobOutcome, _detail_text(), _finish_detached_job(), test_outcome_annulation_tardive_conserve_le_repertoire(), test_outcome_details_de_l_erreur_principale_prioritaires(), test_outcome_n_extrait_jamais_un_chemin_du_message(), test_outcome_rejette_les_chemins_non_textuels(), test_outcome_repli_sur_le_resultat() (+1 more)

### Community 114 - "os"
Cohesion: 0.24
Nodes (4): new_token(), remove_connection_file(), write_connection_file(), remove_and_release_connection()

### Community 115 - "core/zoning.py"
Cohesion: 0.24
Nodes (5): bbox_covers(), should_replace_cache(), status(), test_bbox_rules(), test_statut()

### Community 116 - "logging"
Cohesion: 0.33
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 117 - "describe"
Cohesion: 0.28
Nodes (5): describe(), describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 876 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `ToolResult`, `run_to_project`, `feature_request`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `AlgCall`, `ToolRegistry`, `test_detached_landcover_task.py`, `tools/project_audit.py`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `tool`, `common.py`, `add_to_group`, `test_landcover_guard.py`, `ToolError`, `Dispatcher`, `test_landcover_task_finished.py`, `test_job_lance_pendant_la_confirmation`, `pyqgis.py`, `find_source_file`, `test_bridge_lifecycle.py`, `elevation_sample`, `jobs.py`, `prepare_expression`, `_finish_detached_job`?**
  _High betweenness centrality (0.129) - this node is a cross-community bridge._
- **Are the 106 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 106 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13446969696969696 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `tools/webservices.py`, `ToolResult`, `ToolError`, `run_to_project`, `feature_request`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `AlgCall`, `ToolRegistry`, `test_detached_landcover_task.py`, `tools/project_audit.py`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `tool`, `common.py`, `add_to_group`, `test_landcover_guard.py`, `Dispatcher`, `test_landcover_task_finished.py`, `test_job_lance_pendant_la_confirmation`, `pyqgis.py`, `find_source_file`, `test_bridge_lifecycle.py`, `elevation_sample`, `jobs.py`, `prepare_expression`, `_finish_detached_job`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 156 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 156 INFERRED edges - model-reasoned connections that need verification._
- **Should `report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10967741935483871 - nodes in this community are weakly interconnected._