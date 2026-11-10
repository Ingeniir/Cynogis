# Graph Report - cynogis  (2026-11-10)

## Corpus Check
- 148 files · ~109,907 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2322 nodes · 6959 edges · 105 communities (79 shown, 26 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 622 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `79c7d775`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- tools/webservices.py
- report.py
- common.py
- fields.py
- test_landcover_prepare.py
- ToolError
- Métriques paysagères
- Documentation projet
- PreparationControl
- _style
- test_project_audit.py
- prepare.py
- check_surfaces.py
- Coefficients de surface
- colors.py
- CynogisPlugin
- test_referentials.py
- run_to_project
- feature_request
- JobManager
- Tests des jobs
- palettes.py
- json
- stats.py
- Journal d'édition
- test_dispatcher.py
- _vector_facts
- compute_breaks
- fields.py
- audit.py
- ToolRegistry
- dev_setup.py
- Données terrain CSV
- Résolution des recouvrements
- allocate
- _surface_factors
- Catalogue d'algorithmes
- tools/project_audit.py
- Distances
- BridgeServer
- Historique des styles
- core/atlas.py
- HABREF
- Tests de style
- core/stakes.py
- fetch_wfs_layer
- Schéma des paramètres
- ProcessingExecutor
- Notes et warnings des jobs
- tool
- Tests zonage
- sidecar_report
- test_stats_full.py
- Feuille de route
- BridgeError
- mentions_natura2000
- ErrorCode
- Dispatcher
- describe_groups
- Cache des zonages
- Plan d'échantillonnage
- render_map
- geometry_report
- AlgCall
- Provenance
- _closer_parts
- Rule
- elevation_sample
- bbox_covers
- ToolError
- format_number
- _validate_number
- Guide d'installation
- logging
- Règles métier réglementaires
- core/landscape.py
- jobs.py
- pytest
- _isopleth_geometries
- Règles d'architecture
- re
- Adding a tool (@tool decorator, Param, docstring)
- pyqgis.py
- _is_empty
- core/zoning.py
- BridgeResult
- Commandes de dev
- Métadonnées plugin
- Liste blanche algorithmes
- Débogage
- Fin de tâche graphify
- Venv vs Python QGIS
- Compatibilité Qt
- Fichiers locaux
- cynogis-server
- elevation_sample
- install.ps1
- list_style_options
- test_server_job_cancellation.py
- Cynogis Plugin Icon (icon.svg)

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
- `test_describe_empty_and_single()` --calls--> `describe()`  [INFERRED]
  tests/unit/test_stats.py → plugin/cynogis/core/stats.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `3.4 Audit des garde-fous` --semantically_similar_to--> `Security rules (no bypass, no overwrite, no sensitive species/cadastral data)`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `2.3 Exclure Natura 2000` --semantically_similar_to--> `Natura 2000 not applicable in overseas departments`  [INFERRED] [semantically similar]
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

## Communities (105 total, 26 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.17
Nodes (7): call_tool(), _cancel_and_observe(), _fetch_specs(), list_tools(), _progress_token(), _to_tool(), _wait_job()

### Community 1 - "tools/webservices.py"
Cohesion: 0.06
Nodes (45): is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+37 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "common.py"
Cohesion: 0.11
Nodes (15): unique_field_name(), clean_name(), unique_path(), Level, Param, detect_territory(), add_to_memory(), crs_from_text() (+7 more)

### Community 4 - "fields.py"
Cohesion: 0.10
Nodes (9): sanitize_field_name(), to_ascii(), is_sensitive_field(), mask_sensitive(), sensitive_fields(), Territory, test_mask_sensitive_hides_only_sensitive_values(), test_sensitive_fields_in_filter_columns() (+1 more)

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.12
Nodes (23): _crs(), _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs(), progress() (+15 more)

### Community 6 - "ToolError"
Cohesion: 0.08
Nodes (16): ToolError, expression_context(), prepare_expression(), export_table(), _write_csv(), write_table(), _read(), habitat_typology_join() (+8 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "PreparationControl"
Cohesion: 0.15
Nodes (9): PreparationCancelledError, PreparationControl, test_callback_failure_is_not_hidden(), test_cancellation_before_callback(), test_cancellation_check_failure_is_not_hidden(), test_cancellation_requested_during_callback(), progress(), test_default_control_does_nothing() (+1 more)

### Community 11 - "test_project_audit.py"
Cohesion: 0.20
Nodes (18): audit(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons() (+10 more)

### Community 12 - "prepare.py"
Cohesion: 0.21
Nodes (10): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+2 more)

### Community 13 - "check_surfaces.py"
Cohesion: 0.18
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (26): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+18 more)

### Community 15 - "colors.py"
Cohesion: 0.08
Nodes (23): contrast_ratio(), darken(), distinct_colors(), interpolate_ramp(), lighten(), mix(), parse_color(), readable_text_color() (+15 more)

### Community 16 - "CynogisPlugin"
Cohesion: 0.13
Nodes (5): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin

### Community 17 - "test_referentials.py"
Cohesion: 0.06
Nodes (30): _covers(), find_source_file(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), referentials_directory(), _segments() (+22 more)

### Community 18 - "run_to_project"
Cohesion: 0.07
Nodes (21): _allowed(), describe_algorithm(), run_algorithm(), _isopleths(), kernel_density_points(), buffer(), dissolve(), extract() (+13 more)

### Community 19 - "feature_request"
Cohesion: 0.04
Nodes (62): Pacer, convert_area(), convert_length(), compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer() (+54 more)

### Community 20 - "JobManager"
Cohesion: 0.14
Nodes (3): Executor, Job, JobManager

### Community 21 - "Tests des jobs"
Cohesion: 0.11
Nodes (32): boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), make_obia(), _req() (+24 more)

### Community 22 - "palettes.py"
Cohesion: 0.10
Nodes (15): validate_colors(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors(), validate_palette() (+7 more)

### Community 23 - "json"
Cohesion: 0.22
Nodes (7): decode_request(), _protocol_error(), _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "stats.py"
Cohesion: 0.14
Nodes (17): correlate(), correlation_pvalue(), describe(), describe_categorical(), describe_full(), interpret_shape(), kurtosis(), linear_fit() (+9 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.10
Nodes (12): check_batch_size(), describe_summary(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations() (+4 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "_vector_facts"
Cohesion: 0.13
Nodes (11): file_format(), layer_kind(), source_path(), list_layers(), _summary(), _tree(), _visible(), _layer_facts() (+3 more)

### Community 28 - "compute_breaks"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "fields.py"
Cohesion: 0.10
Nodes (19): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), truncate_field_names(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+11 more)

### Community 30 - "audit.py"
Cohesion: 0.27
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.13
Nodes (8): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 32 - "dev_setup.py"
Cohesion: 0.13
Nodes (17): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version(), check_python(), ensure_venv() (+9 more)

### Community 33 - "Données terrain CSV"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.16
Nodes (14): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus(), test_half_plane_contient_le_milieu_cote_a() (+6 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "_surface_factors"
Cohesion: 0.29
Nodes (4): _pixel_labels(), _sector_index(), _slope_aspect(), _surface_factors()

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.11
Nodes (14): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+6 more)

### Community 38 - "tools/project_audit.py"
Cohesion: 0.22
Nodes (8): build_sections(), severity_counts(), verdict(), _yes_no(), audit_project(), _open_project(), _overview_map(), _project_facts()

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
Cohesion: 0.08
Nodes (22): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+14 more)

### Community 46 - "fetch_wfs_layer"
Cohesion: 0.17
Nodes (7): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "ProcessingExecutor"
Cohesion: 0.08
Nodes (10): Fetch, PrepareLandcover, LandcoverPreparationTask, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor (+2 more)

### Community 49 - "Notes et warnings des jobs"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 50 - "tool"
Cohesion: 0.04
Nodes (45): ToolResult, tool(), export_atlas_pdf(), _from_template(), _overview_extent(), list_coefficients(), clean_number(), crs_info() (+37 more)

### Community 51 - "Tests zonage"
Cohesion: 0.19
Nodes (6): getfeature_url(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 52 - "sidecar_report"
Cohesion: 0.11
Nodes (14): export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), test_export_plan_renommage(), test_export_plan_type_non_supporte() (+6 more)

### Community 53 - "test_stats_full.py"
Cohesion: 0.15
Nodes (9): correlation_pairs(), ranks(), test_categorical_entropy(), test_describe_full_shape(), test_empty(), test_outlier_detected(), test_pairs_skip_missing(), test_ranks_ties() (+1 more)

### Community 54 - "Feuille de route"
Cohesion: 0.10
Nodes (20): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement (+12 more)

### Community 55 - "BridgeError"
Cohesion: 0.26
Nodes (5): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 56 - "mentions_natura2000"
Cohesion: 0.31
Nodes (5): mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 57 - "ErrorCode"
Cohesion: 0.07
Nodes (43): ErrorCode, begin_edit(), field_type_name(), geometry_from_wkt(), get_vector_layer(), is_shapefile(), layer_field_types(), refresh_layer() (+35 more)

### Community 58 - "Dispatcher"
Cohesion: 0.14
Nodes (6): Request, Response, Dispatcher, finish(), collecting(), render_notes()

### Community 59 - "describe_groups"
Cohesion: 0.29
Nodes (4): describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum()

### Community 61 - "Cache des zonages"
Cohesion: 0.18
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "render_map"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 65 - "AlgCall"
Cohesion: 0.24
Nodes (7): AlgCall, Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 66 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 70 - "bbox_covers"
Cohesion: 0.50
Nodes (3): bbox_covers(), should_replace_cache(), test_bbox_rules()

### Community 71 - "ToolError"
Cohesion: 0.10
Nodes (21): range_labels(), to_float(), _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized() (+13 more)

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "logging"
Cohesion: 0.20
Nodes (5): QgsLogHandler, setup_logging(), teardown_logging(), run(), main()

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "core/landscape.py"
Cohesion: 0.07
Nodes (25): apply_mapping(), classes_for(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register() (+17 more)

### Community 79 - "pytest"
Cohesion: 0.11
Nodes (27): LandcoverConfig, PreparationConfig, validate_rgb_bands(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config(), test_equal_area_thresholds_are_allowed(), test_extremely_large_number_is_rejected() (+19 more)

### Community 81 - "Règles d'architecture"
Cohesion: 0.22
Nodes (6): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), Job response and polling (get_job_status / cancel_job), run_to_project / save_to_project output pipeline, ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "re"
Cohesion: 0.11
Nodes (15): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+7 more)

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.17
Nodes (10): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Permission levels READ / CREATE / MODIFY / DESTROY, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471, 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD (+2 more)

### Community 84 - "pyqgis.py"
Cohesion: 0.09
Nodes (12): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+4 more)

### Community 86 - "core/zoning.py"
Cohesion: 0.12
Nodes (13): assess(), cache_matches(), cache_meta(), for_territory(), _inpn(), status(), Zoning, zoning_state() (+5 more)

### Community 87 - "BridgeResult"
Cohesion: 0.17
Nodes (10): BridgeResult, CatalogClient, FakeClient, test_catalogue_relu_seulement_si_le_pont_change(), test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat() (+2 more)

### Community 102 - "elevation_sample"
Cohesion: 0.08
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 108 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 110 - "test_server_job_cancellation.py"
Cohesion: 0.21
Nodes (11): app(), install_client(), ScriptedClient, test_bridge_failure_does_not_confirm_stop(), test_cancel_waits_for_final_confirmation(), test_cleanup_error_is_not_reported_as_clean_cancellation(), test_job_completed_before_cancellation_took_effect(), test_late_cancellation_preserves_output_details() (+3 more)

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `3.2/3.3 Donnees sensibles et filtrage RGPD`, `Green Map Location Pin`, `Phase 0 : Outillage du developpement` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 790 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `common.py`, `test_referentials.py`, `run_to_project`, `feature_request`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `ToolRegistry`, `tools/project_audit.py`, `BridgeServer`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `Notes et warnings des jobs`, `tool`, `ErrorCode`, `Dispatcher`, `render_map`, `elevation_sample`, `ToolError`, `jobs.py`, `pyqgis.py`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Are the 95 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 95 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `3.2/3.3 Donnees sensibles et filtrage RGPD` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.059940059940059943 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `tools/webservices.py`, `common.py`, `ToolError`, `test_referentials.py`, `run_to_project`, `feature_request`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `ToolRegistry`, `tools/project_audit.py`, `BridgeServer`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `Notes et warnings des jobs`, `tool`, `Dispatcher`, `render_map`, `elevation_sample`, `ToolError`, `jobs.py`, `pyqgis.py`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 145 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 145 INFERRED edges - model-reasoned connections that need verification._
- **Should `report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10846560846560846 - nodes in this community are weakly interconnected._