# Graph Report - cynogis  (2026-11-10)

## Corpus Check
- 152 files · ~112,687 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2422 nodes · 7177 edges · 109 communities (90 shown, 19 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 642 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a4ff59b3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- tools/webservices.py
- report.py
- ToolResult
- geometry_report
- test_landcover_prepare.py
- habitat_typology_join
- Métriques paysagères
- Documentation projet
- pathlib
- shapefile.py
- test_project_audit.py
- prepare.py
- check_surfaces.py
- Coefficients de surface
- colors.py
- CynogisPlugin
- test_referentials.py
- run_to_project
- ErrorCode
- JobManager
- Tests des jobs
- collections_abc
- json
- stats.py
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
- _read_window
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
- shapefiles.py
- regulatory_prescan
- Feuille de route
- get_palette
- ToolError
- mentions_natura2000
- Dispatcher
- to_float
- run_cleanup_steps
- Cache des zonages
- Plan d'échantillonnage
- render_map
- _summary
- AlgCall
- Provenance
- units.py
- core/referentials.py
- _overlay
- Source
- ToolError
- format_number
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
- install.ps1
- list_coefficients
- confirm.py
- classes_for

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 206 edges
2. `ErrorCode` - 187 edges
3. `tool()` - 157 edges
4. `ToolResult` - 108 edges
5. `get_vector_layer()` - 102 edges
6. `feature_request()` - 73 edges
7. `geometry_kind()` - 60 edges
8. `require_field()` - 56 edges
9. `to_json_value()` - 52 edges
10. `distance_area()` - 51 edges

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

## Communities (109 total, 19 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.05
Nodes (36): QgsLogHandler, setup_logging(), teardown_logging(), main(), call_tool(), _cancel_and_observe(), _fetch_specs(), list_tools() (+28 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.07
Nodes (42): is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+34 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "ToolResult"
Cohesion: 0.15
Nodes (7): ToolResult, Level, Param, _project_target(), save_project(), _save_project_details(), output_dir()

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.12
Nodes (23): _crs(), _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs(), progress() (+15 more)

### Community 6 - "habitat_typology_join"
Cohesion: 0.08
Nodes (12): unique_path(), _isopleth_geometries(), export_map_image(), export_table(), _output_path(), _write_csv(), write_report(), habitat_typology_join() (+4 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "pathlib"
Cohesion: 0.10
Nodes (12): clean_name(), to_ascii(), is_sensitive_field(), mask_sensitive(), sensitive_fields(), test_clean_name(), test_normalize(), test_unique_path_never_overwrites() (+4 more)

### Community 10 - "shapefile.py"
Cohesion: 0.12
Nodes (14): companion_paths(), export_plan(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), test_export_plan_renommage(), test_export_plan_type_non_supporte() (+6 more)

### Community 11 - "test_project_audit.py"
Cohesion: 0.20
Nodes (18): audit(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons() (+10 more)

### Community 12 - "prepare.py"
Cohesion: 0.17
Nodes (12): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+4 more)

### Community 13 - "check_surfaces.py"
Cohesion: 0.17
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (25): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+17 more)

### Community 15 - "colors.py"
Cohesion: 0.12
Nodes (15): darken(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), test_interpolate_ramp_extremites_conservees() (+7 more)

### Community 16 - "CynogisPlugin"
Cohesion: 0.11
Nodes (6): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin, remove_and_release_connection()

### Community 17 - "test_referentials.py"
Cohesion: 0.22
Nodes (10): map_cirad(), map_feature(), test_cirad_974_2020_ombre_et_code_inconnu(), test_cirad_974_2020_par_code(), test_cirad_974_millesimes_meme_nomenclature(), test_cirad_976_2023_par_code(), test_map_cirad_canne_selon_territoire(), test_map_cirad_repli_mots_cles() (+2 more)

### Community 18 - "run_to_project"
Cohesion: 0.09
Nodes (15): _allowed(), describe_algorithm(), run_algorithm(), kernel_density_points(), compute_ndvi(), extract_ravines(), is_optional(), _run() (+7 more)

### Community 19 - "ErrorCode"
Cohesion: 0.05
Nodes (48): ErrorCode, unique_field_name(), convert_length(), add_to_memory(), distance_area(), expression_context(), feature_request(), geometry_kind() (+40 more)

### Community 20 - "JobManager"
Cohesion: 0.17
Nodes (3): collecting(), Job, JobManager

### Community 21 - "Tests des jobs"
Cohesion: 0.10
Nodes (33): PreparationCancelledError, boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), make_obia() (+25 more)

### Community 22 - "collections_abc"
Cohesion: 0.11
Nodes (12): distinct_colors(), validate_colors(), with_alpha(), landscape_palette(), register_palette(), resolve_colors(), validate_palette(), test_distinct_colors_sans_doublon() (+4 more)

### Community 23 - "json"
Cohesion: 0.19
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "stats.py"
Cohesion: 0.09
Nodes (29): correlate(), correlation_pairs(), correlation_pvalue(), describe(), describe_categorical(), describe_full(), describe_groups(), interpret_shape() (+21 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.10
Nodes (12): check_batch_size(), describe_summary(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations() (+4 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "FakeExecutor"
Cohesion: 0.13
Nodes (6): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_cancel_all_continues_after_one_job_fails(), test_notes_ajoutees_aux_warnings()

### Community 28 - "compute_breaks"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "fields.py"
Cohesion: 0.10
Nodes (20): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), truncate_field_names(), test_coerce_record_champ_inconnu_strict() (+12 more)

### Community 30 - "audit.py"
Cohesion: 0.28
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.18
Nodes (5): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec

### Community 32 - "dev_setup.py"
Cohesion: 0.13
Nodes (17): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version(), check_python(), ensure_venv() (+9 more)

### Community 33 - "Données terrain CSV"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.12
Nodes (15): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), _closer_parts(), records(), test_egalite_stable(), test_half_plane_centres_confondus() (+7 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "_read_window"
Cohesion: 0.24
Nodes (5): _pixel_labels(), _read_window(), _sector_index(), _slope_aspect(), _surface_factors()

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 38 - "tools/project_audit.py"
Cohesion: 0.14
Nodes (14): build_sections(), severity_counts(), verdict(), _yes_no(), file_format(), layer_kind(), source_path(), audit_project() (+6 more)

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 41 - "Historique des styles"
Cohesion: 0.15
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
Cohesion: 0.08
Nodes (22): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+14 more)

### Community 46 - "fetch_wfs_layer"
Cohesion: 0.12
Nodes (10): service_label(), _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), _local_source(), _only_fields(), Source (+2 more)

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "ProcessingExecutor"
Cohesion: 0.10
Nodes (9): Fetch, PrepareLandcover, LandcoverPreparationTask, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor (+1 more)

### Community 49 - "tool"
Cohesion: 0.05
Nodes (49): Pacer, tool(), needs_priority_field(), compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer() (+41 more)

### Community 50 - "common.py"
Cohesion: 0.06
Nodes (28): detect_territory(), export_atlas_pdf(), _from_template(), _overview_extent(), begin_edit(), clean_number(), crs_info(), enum_name() (+20 more)

### Community 51 - "Tests zonage"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 52 - "shapefiles.py"
Cohesion: 0.12
Nodes (13): looks_like_mojibake(), crs_from_text(), layer_field_types(), add_to_group(), add_to_project(), _output_item(), check_shapefile(), export_layer() (+5 more)

### Community 53 - "regulatory_prescan"
Cohesion: 0.20
Nodes (6): assess(), for_territory(), zoning_state(), regulatory_prescan(), test_par_territoire(), test_pre_diagnostic()

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "get_palette"
Cohesion: 0.22
Nodes (6): all_palettes(), get_palette(), load_user_palettes(), test_get_palette_etiree(), test_get_palette_inconnue(), test_load_user_palettes_ignore_les_erreurs()

### Community 56 - "ToolError"
Cohesion: 0.07
Nodes (36): ToolError, geometry_from_wkt(), is_shapefile(), refresh_layer(), select_ids(), wkt_to_layer_crs(), add_features(), add_field() (+28 more)

### Community 57 - "mentions_natura2000"
Cohesion: 0.31
Nodes (5): mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 58 - "Dispatcher"
Cohesion: 0.12
Nodes (5): Response, BridgeServer, Dispatcher, finish(), render_notes()

### Community 60 - "run_cleanup_steps"
Cohesion: 0.11
Nodes (6): run_cleanup_steps(), test_cleanup_accepts_empty_sequence(), test_cleanup_collects_multiple_errors(), test_cleanup_continues_after_failure(), test_cleanup_does_not_swallow_process_interruptions(), test_cleanup_executes_every_step_in_order()

### Community 61 - "Cache des zonages"
Cohesion: 0.27
Nodes (5): cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "render_map"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 64 - "_summary"
Cohesion: 0.29
Nodes (4): list_layers(), _summary(), _tree(), _visible()

### Community 65 - "AlgCall"
Cohesion: 0.24
Nodes (7): AlgCall, Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 66 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 67 - "units.py"
Cohesion: 0.47
Nodes (3): convert_area(), test_conversions(), test_unknown_unit()

### Community 68 - "core/referentials.py"
Cohesion: 0.20
Nodes (7): _covers(), map_ocsge(), Rule, _segments(), test_map_ocsge_a_verifier(), test_map_ocsge_comparaison_par_segments(), test_map_ocsge_territoire()

### Community 69 - "_overlay"
Cohesion: 0.29
Nodes (3): is_agricultural(), _overlay(), test_is_agricultural()

### Community 70 - "Source"
Cohesion: 0.33
Nodes (3): Source, sources_for(), test_sources_for_territoire()

### Community 71 - "ToolError"
Cohesion: 0.13
Nodes (17): _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _distinct_values(), _kind() (+9 more)

### Community 72 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

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
Cohesion: 0.09
Nodes (17): apply_mapping(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+9 more)

### Community 78 - "PreparationControl"
Cohesion: 0.17
Nodes (8): PreparationControl, test_callback_failure_is_not_hidden(), test_cancellation_before_callback(), test_cancellation_check_failure_is_not_hidden(), test_cancellation_requested_during_callback(), progress(), test_default_control_does_nothing(), test_progress_is_forwarded()

### Community 79 - "pytest"
Cohesion: 0.10
Nodes (27): LandcoverConfig, PreparationConfig, _validate_number(), validate_rgb_bands(), obia_prepare_test(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config() (+19 more)

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

### Community 85 - "find_source_file"
Cohesion: 0.15
Nodes (7): find_source_file(), referentials_directory(), _clipped(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 86 - "core/zoning.py"
Cohesion: 0.19
Nodes (8): bbox_covers(), cache_matches(), cache_meta(), _inpn(), should_replace_cache(), Zoning, test_bbox_rules(), test_cache_meta_roundtrip_and_matching()

### Community 87 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 99 - "test_bridge_lifecycle.py"
Cohesion: 0.05
Nodes (42): Bar, critical(), fake_remove(), fake_write(), FakeBridgeServer, FakeDispatcher, FakeListener, FakeSocket (+34 more)

### Community 101 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 102 - "elevation_sample"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 103 - "Security rules (no bypass, no overwrite, no sensitive species/cadastral data)"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 104 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

### Community 108 - "confirm.py"
Cohesion: 0.14
Nodes (4): build_details(), make_confirmer(), confirm(), register_detail_provider()

### Community 110 - "classes_for"
Cohesion: 0.20
Nodes (7): classes_for(), validate_codes(), check_rules(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 830 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `ToolResult`, `habitat_typology_join`, `run_to_project`, `ErrorCode`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `FakeExecutor`, `ToolRegistry`, `_read_window`, `tools/project_audit.py`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `tool`, `common.py`, `shapefiles.py`, `Dispatcher`, `render_map`, `ToolError`, `pyqgis.py`, `find_source_file`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Are the 95 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 95 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `1.2 Interdire les surfaces en EPSG:4326` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05094905094905095 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `tools/webservices.py`, `ToolResult`, `habitat_typology_join`, `run_to_project`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `FakeExecutor`, `ToolRegistry`, `_read_window`, `tools/project_audit.py`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `tool`, `common.py`, `shapefiles.py`, `ToolError`, `Dispatcher`, `render_map`, `ToolError`, `pyqgis.py`, `find_source_file`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 145 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 145 INFERRED edges - model-reasoned connections that need verification._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06690140845070422 - nodes in this community are weakly interconnected._