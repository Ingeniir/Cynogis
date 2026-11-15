# Graph Report - cynogis  (2026-11-15)

## Corpus Check
- 157 files · ~120,090 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 4)

## Summary
- 2627 nodes · 7744 edges · 118 communities (96 shown, 22 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 754 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9c66d147`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BridgeResult
- tools/webservices.py
- report.py
- ToolResult
- geometry_report
- test_landcover_prepare.py
- prepare_expression
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
- require_field
- layers.py
- Tests zonage
- test_prepare_landcover_tool.py
- PrepareLandcover
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
- numpy
- AlgCall
- Provenance
- test_job_lance_pendant_la_confirmation
- fetch_wfs_layer
- qgis_pyqt_qtcore
- test_stats_full.py
- test_connection.py
- app.py
- CatalogClient
- Guide d'installation
- list_style_options
- Règles métier réglementaires
- core/landscape.py
- render_map
- pytest
- Env
- Règles d'architecture
- re
- Adding a tool (@tool decorator, Param, docstring)
- pyqgis.py
- landcover_guard.py
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
- test_terrain.py
- Security rules (no bypass, no overwrite, no sensitive species/cadastral data)
- Phase 3 : Tracabilite et confidentialite
- BridgeError
- install.ps1
- list_coefficients
- jobs.py
- core/impacts.py
- ToolError
- units.py
- math
- _finish_detached_job
- RefusingTaskManager
- logging
- TaskExecutor

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 222 edges
2. `ErrorCode` - 200 edges
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

## Communities (118 total, 22 thin omitted)

### Community 0 - "BridgeResult"
Cohesion: 0.18
Nodes (15): BridgeResult, test_wait_job_annule_dans_qgis(), scenario(), install_client(), ScriptedClient, test_bridge_failure_does_not_confirm_stop(), test_cancel_waits_for_final_confirmation(), test_cleanup_error_is_not_reported_as_clean_cancellation() (+7 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.07
Nodes (42): is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+34 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "ToolResult"
Cohesion: 0.13
Nodes (11): Level, tool(), Param, detect_territory(), _overview_extent(), add_to_memory(), extent_wgs84(), polygon_parts() (+3 more)

### Community 4 - "geometry_report"
Cohesion: 0.20
Nodes (4): _error_kind(), geometry_report(), _vector_facts(), _scan_sidecars()

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.09
Nodes (31): PreparationControl, _crs(), _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs() (+23 more)

### Community 6 - "prepare_expression"
Cohesion: 0.09
Nodes (11): expression_context(), prepare_expression(), export_table(), _project_target(), save_project(), _save_project_details(), _write_csv(), write_report() (+3 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "privacy.py"
Cohesion: 0.18
Nodes (6): is_sensitive_field(), mask_sensitive(), sensitive_fields(), test_mask_sensitive_hides_only_sensitive_values(), test_sensitive_fields_in_filter_columns(), test_versions_aligned()

### Community 10 - "shapefile.py"
Cohesion: 0.10
Nodes (17): truncate_field_names(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages() (+9 more)

### Community 11 - "test_project_audit.py"
Cohesion: 0.20
Nodes (18): audit(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons() (+10 more)

### Community 12 - "prepare.py"
Cohesion: 0.25
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
Cohesion: 0.06
Nodes (30): _covers(), find_source_file(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), referentials_directory(), _segments() (+22 more)

### Community 18 - "run_to_project"
Cohesion: 0.05
Nodes (27): get_raster_layer(), _isopleths(), kernel_density_points(), buffer(), dissolve(), extract(), fix_geometries(), _name() (+19 more)

### Community 19 - "feature_request"
Cohesion: 0.05
Nodes (54): build_table(), Pacer, convert_length(), area_m2(), area_method(), dissolved_areas(), distance_area(), feature_request() (+46 more)

### Community 20 - "JobManager"
Cohesion: 0.18
Nodes (4): collecting(), Job, JobManager, test_jobmanager_double_finalization_error_fails_job()

### Community 21 - "Tests des jobs"
Cohesion: 0.10
Nodes (38): PreparationCancelledError, boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), make_obia() (+30 more)

### Community 22 - "palettes.py"
Cohesion: 0.10
Nodes (16): interpolate_ramp(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors(), validate_palette() (+8 more)

### Community 23 - "json"
Cohesion: 0.19
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "stats.py"
Cohesion: 0.14
Nodes (14): correlate(), correlation_pairs(), correlation_pvalue(), describe(), describe_categorical(), describe_groups(), _r(), strength() (+6 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.10
Nodes (12): check_batch_size(), describe_summary(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations() (+4 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "AlgCall"
Cohesion: 0.13
Nodes (6): FakeExecutor, test_cancel_all_continues_after_one_job_fails(), test_echec_de_fermeture_detache_reste_un_echec_technique(), generator(), test_start_refuse_sur_un_gestionnaire_detache(), generator()

### Community 28 - "compute_breaks"
Cohesion: 0.09
Nodes (24): clean_values(), compute_breaks(), _dedupe(), equal_interval(), format_number(), natural_breaks(), pretty_breaks(), quantile_breaks() (+16 more)

### Community 29 - "fields.py"
Cohesion: 0.11
Nodes (19): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), to_ascii(), test_coerce_record_champ_inconnu_strict() (+11 more)

### Community 30 - "audit.py"
Cohesion: 0.15
Nodes (9): new_token(), remove_connection_file(), write_connection_file(), AuditLog, _truncate(), remove_and_release_connection(), test_destroy_params_never_truncated(), test_long_params_truncated() (+1 more)

### Community 31 - "ToolRegistry"
Cohesion: 0.12
Nodes (8): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 32 - "dev_setup.py"
Cohesion: 0.13
Nodes (17): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version(), check_python(), ensure_venv() (+9 more)

### Community 33 - "Données terrain CSV"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.11
Nodes (16): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), _closer_parts(), records(), test_egalite_stable() (+8 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "test_detached_landcover_task.py"
Cohesion: 0.22
Nodes (17): _crs_wkt(), expect_busy_start(), guard_free(), isolated(), make_sample(), patched(), _req(), spin() (+9 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.10
Nodes (14): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+6 more)

### Community 38 - "tools/project_audit.py"
Cohesion: 0.16
Nodes (10): build_sections(), severity_counts(), verdict(), _yes_no(), audit_project(), _layer_facts(), _open_project(), _overview_map() (+2 more)

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
Nodes (7): service_label(), _bbox_wgs84(), _cached_source(), _local_source(), _only_fields(), Source, _sources()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "ProcessingExecutor"
Cohesion: 0.12
Nodes (8): Fetch, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, forget(), _take_layers()

### Community 49 - "require_field"
Cohesion: 0.07
Nodes (19): compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), overlap_warning() (+11 more)

### Community 50 - "layers.py"
Cohesion: 0.08
Nodes (22): clean_number(), crs_info(), enum_name(), file_format(), layer_kind(), source_path(), territory_info(), _build_preparation_step() (+14 more)

### Community 51 - "Tests zonage"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 52 - "test_prepare_landcover_tool.py"
Cohesion: 0.21
Nodes (19): abort_test_process(), environment(), final_response(), done(), params(), patched(), _plain(), request() (+11 more)

### Community 53 - "PrepareLandcover"
Cohesion: 0.14
Nodes (6): PrepareLandcover, LandcoverPreparationTask, make_obia_dispatcher(), obia(), tool(), obia_prepare_test()

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "test_landcover_guard.py"
Cohesion: 0.17
Nodes (16): expect_busy(), in_thread(), is_free(), isolated_property(), patched(), step(), test_executor_addtask_refusal_releases_guard(), test_executor_constructor_failure_releases_guard() (+8 more)

### Community 56 - "ToolError"
Cohesion: 0.05
Nodes (53): ToolResult, unique_field_name(), clean_name(), begin_edit(), crs_from_text(), field_type_name(), geometry_from_wkt(), get_vector_layer() (+45 more)

### Community 57 - "mentions_natura2000"
Cohesion: 0.31
Nodes (5): mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 58 - "Dispatcher"
Cohesion: 0.14
Nodes (5): Response, BridgeServer, Dispatcher, finish(), render_notes()

### Community 59 - "to_float"
Cohesion: 0.33
Nodes (3): to_float(), _sort_key(), test_to_float()

### Community 60 - "run_cleanup_steps"
Cohesion: 0.12
Nodes (6): run_cleanup_steps(), test_cleanup_accepts_empty_sequence(), test_cleanup_collects_multiple_errors(), test_cleanup_continues_after_failure(), test_cleanup_does_not_swallow_process_interruptions(), test_cleanup_executes_every_step_in_order()

### Community 61 - "Cache des zonages"
Cohesion: 0.27
Nodes (5): cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "test_landcover_task_finished.py"
Cohesion: 0.15
Nodes (16): isolated_guard(), make_task(), _obia_job(), tool(), patched(), Recorder, spin(), step() (+8 more)

### Community 64 - "numpy"
Cohesion: 0.16
Nodes (7): _isopleth_geometries(), _style(), _clean(), _pixel_labels(), _sector_index(), _slope_aspect(), _surface_factors()

### Community 65 - "AlgCall"
Cohesion: 0.15
Nodes (12): AlgCall, Pause, run_now(), _spy_manager(), generator(), test_apres_detachement_le_finisseur_n_est_plus_appele(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now() (+4 more)

### Community 66 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 67 - "test_job_lance_pendant_la_confirmation"
Cohesion: 0.22
Nodes (6): note(), job_invalide(), mesure_invalide(), test_job_lance_pendant_la_confirmation(), confirm(), test_notes_ajoutees_aux_warnings()

### Community 68 - "fetch_wfs_layer"
Cohesion: 0.18
Nodes (6): for_territory(), fetch_wfs_layer(), _is_cancel(), regulatory_prescan(), _wfs_features(), test_par_territoire()

### Community 70 - "test_stats_full.py"
Cohesion: 0.18
Nodes (8): ranks(), test_describe_full_shape(), test_empty(), test_outlier_detected(), test_pairs_skip_missing(), test_pearson_and_spearman(), test_ranks_ties(), test_sensitive()

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
Cohesion: 0.06
Nodes (25): apply_mapping(), classes_for(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register() (+17 more)

### Community 78 - "render_map"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 79 - "pytest"
Cohesion: 0.11
Nodes (26): LandcoverConfig, PreparationConfig, _validate_number(), validate_rgb_bands(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config(), test_equal_area_thresholds_are_allowed() (+18 more)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "re"
Cohesion: 0.11
Nodes (15): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+7 more)

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "pyqgis.py"
Cohesion: 0.09
Nodes (11): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+3 more)

### Community 85 - "landcover_guard.py"
Cohesion: 0.38
Nodes (3): acquire_landcover_guard(), release(), _application()

### Community 86 - "core/zoning.py"
Cohesion: 0.14
Nodes (11): assess(), bbox_covers(), cache_matches(), cache_meta(), _inpn(), should_replace_cache(), Zoning, zoning_state() (+3 more)

### Community 87 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 99 - "test_bridge_lifecycle.py"
Cohesion: 0.06
Nodes (35): Bar, critical(), fake_remove(), fake_write(), FakeBridgeServer, FakeDispatcher, FakeListener, FakeSocket (+27 more)

### Community 101 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 102 - "test_terrain.py"
Cohesion: 0.10
Nodes (16): aspect_sector(), degrees_to_percent(), distribution(), percent_to_degrees(), reclass_table(), slope_class(), SlopeClass, test_aspect_sector() (+8 more)

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
Cohesion: 0.08
Nodes (5): Rule, altitude_band(), parse_bands(), Territory, test_tranches_altitude()

### Community 109 - "core/impacts.py"
Cohesion: 0.19
Nodes (8): compare_variants(), direct_label(), ring_labels(), stake_weight(), test_anneaux(), test_comparaison_variantes(), test_poids_enjeu(), test_tableau()

### Community 110 - "ToolError"
Cohesion: 0.06
Nodes (35): ErrorCode, ToolError, unique_path(), _allowed(), describe_algorithm(), run_algorithm(), export_atlas_pdf(), _from_template() (+27 more)

### Community 111 - "units.py"
Cohesion: 0.47
Nodes (3): convert_area(), test_conversions(), test_unknown_unit()

### Community 112 - "math"
Cohesion: 0.19
Nodes (8): describe_full(), interpret_shape(), kurtosis(), linear_fit(), pearson(), percentile(), skewness(), _t95()

### Community 113 - "_finish_detached_job"
Cohesion: 0.22
Nodes (9): DetachedJobOutcome, _detail_text(), _finish_detached_job(), test_outcome_annulation_tardive_conserve_le_repertoire(), test_outcome_details_de_l_erreur_principale_prioritaires(), test_outcome_n_extrait_jamais_un_chemin_du_message(), test_outcome_rejette_les_chemins_non_textuels(), test_outcome_repli_sur_le_resultat() (+1 more)

### Community 116 - "logging"
Cohesion: 0.20
Nodes (5): QgsLogHandler, setup_logging(), teardown_logging(), run(), main()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 885 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `ToolResult`, `prepare_expression`, `core/referentials.py`, `run_to_project`, `feature_request`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `AlgCall`, `ToolRegistry`, `test_detached_landcover_task.py`, `tools/project_audit.py`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `require_field`, `layers.py`, `test_landcover_guard.py`, `ToolError`, `Dispatcher`, `test_landcover_task_finished.py`, `fetch_wfs_layer`, `render_map`, `pyqgis.py`, `landcover_guard.py`, `test_bridge_lifecycle.py`, `jobs.py`, `_finish_detached_job`, `.__init__`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Are the 106 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 106 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06659056316590563 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `tools/webservices.py`, `ToolResult`, `prepare_expression`, `core/referentials.py`, `run_to_project`, `feature_request`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `AlgCall`, `ToolRegistry`, `test_detached_landcover_task.py`, `tools/project_audit.py`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `require_field`, `layers.py`, `test_landcover_guard.py`, `ToolError`, `Dispatcher`, `test_landcover_task_finished.py`, `fetch_wfs_layer`, `render_map`, `pyqgis.py`, `landcover_guard.py`, `test_bridge_lifecycle.py`, `jobs.py`, `_finish_detached_job`, `.__init__`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 157 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 157 INFERRED edges - model-reasoned connections that need verification._
- **Should `report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10846560846560846 - nodes in this community are weakly interconnected._