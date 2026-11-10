# Graph Report - cynogis  (2026-11-10)

## Corpus Check
- 150 files · ~110,530 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2343 nodes · 6997 edges · 112 communities (89 shown, 23 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 628 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f3ca656d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- tools/webservices.py
- report.py
- common.py
- ToolResult
- test_landcover_prepare.py
- ToolError
- Métriques paysagères
- Documentation projet
- export.py
- distance_area
- test_project_audit.py
- prepare.py
- check_surfaces.py
- Coefficients de surface
- colors.py
- CynogisPlugin
- test_referentials.py
- run_to_project
- tools/proximity.py
- JobManager
- Tests des jobs
- palettes.py
- json
- stats.py
- Journal d'édition
- test_dispatcher.py
- geometry_kind
- compute_breaks
- fields.py
- audit.py
- ToolRegistry
- dev_setup.py
- Données terrain CSV
- Résolution des recouvrements
- allocate
- elevation_sample
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
- require_field
- layers.py
- Tests zonage
- shapefiles.py
- test_sensitive
- Feuille de route
- editing.py
- move_features
- select_ids
- Dispatcher
- describe_groups
- run_cleanup_steps
- Cache des zonages
- Plan d'échantillonnage
- render_map
- re
- AlgCall
- Provenance
- get_vector_layer
- Rule
- tools/referentials.py
- bbox_covers
- ToolError
- format_number
- feature_request
- Guide d'installation
- plugin.py
- Règles métier réglementaires
- core/landscape.py
- jobs.py
- pytest
- build_plugin.py
- Règles d'architecture
- re
- Adding a tool (@tool decorator, Param, docstring)
- pyqgis.py
- find_source_file
- core/zoning.py
- contrast_ratio
- Commandes de dev
- connection.py
- Métadonnées plugin
- Liste blanche algorithmes
- Débogage
- Fin de tâche graphify
- Venv vs Python QGIS
- Compatibilité Qt
- Fichiers locaux
- cynogis-server
- Phase 1 : Fiabilite des calculs de surface
- elevation_sample
- Security rules (no bypass, no overwrite, no sensitive species/cadastral data)
- Phase 3 : Tracabilite et confidentialite
- install.ps1
- list_coefficients
- CoefficientSpec
- check_rules
- is_agricultural

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

## Communities (112 total, 23 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.05
Nodes (35): main(), call_tool(), _cancel_and_observe(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool() (+27 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.06
Nodes (47): is_natura2000_layer(), mentions_natura2000(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs() (+39 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "common.py"
Cohesion: 0.11
Nodes (11): unique_field_name(), detect_territory(), Territory, _overview_extent(), extent_wgs84(), rect_to_list(), territory_info(), _territory() (+3 more)

### Community 4 - "ToolResult"
Cohesion: 0.08
Nodes (18): ToolResult, is_sensitive_field(), mask_sensitive(), sensitive_fields(), field_type_name(), to_json_value(), check_geometries(), _error_kind() (+10 more)

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.08
Nodes (31): PreparationControl, _crs(), _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs() (+23 more)

### Community 6 - "ToolError"
Cohesion: 0.08
Nodes (17): ErrorCode, ToolError, expression_context(), geometry_from_wkt(), prepare_expression(), wkt_to_layer_crs(), export_table(), _write_csv() (+9 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "export.py"
Cohesion: 0.08
Nodes (16): clean_name(), to_ascii(), unique_path(), _build(), export_atlas_pdf(), _from_template(), _north_arrow(), export_map_image() (+8 more)

### Community 10 - "distance_area"
Cohesion: 0.09
Nodes (16): add_to_memory(), distance_area(), make_field(), _isopleths(), kernel_density_points(), _save_isopleths(), _style(), import_field_data() (+8 more)

### Community 11 - "test_project_audit.py"
Cohesion: 0.32
Nodes (13): layer_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique(), test_projet_sain_sans_anomalie() (+5 more)

### Community 12 - "prepare.py"
Cohesion: 0.25
Nodes (9): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+1 more)

### Community 13 - "check_surfaces.py"
Cohesion: 0.17
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 14 - "Coefficients de surface"
Cohesion: 0.10
Nodes (24): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), _ratio() (+16 more)

### Community 15 - "colors.py"
Cohesion: 0.10
Nodes (17): darken(), distinct_colors(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), validate_colors() (+9 more)

### Community 17 - "test_referentials.py"
Cohesion: 0.12
Nodes (19): _covers(), map_cirad(), map_feature(), map_ocsge(), _segments(), Source, sources_for(), test_cirad_974_2020_ombre_et_code_inconnu() (+11 more)

### Community 18 - "run_to_project"
Cohesion: 0.10
Nodes (18): tool(), buffer(), dissolve(), extract(), fix_geometries(), _name(), overlay(), reproject_layer() (+10 more)

### Community 19 - "tools/proximity.py"
Cohesion: 0.10
Nodes (20): to_float(), convert_length(), iter_geometries(), _collect(), count_observations(), count_points_in_polygon(), _distance_m(), distance_matrix() (+12 more)

### Community 20 - "JobManager"
Cohesion: 0.14
Nodes (5): collecting(), Job, JobManager, render_notes(), test_cancel_all_continues_after_one_job_fails()

### Community 21 - "Tests des jobs"
Cohesion: 0.07
Nodes (37): note(), boucle(), calcul(), effacer(), erreur_avant(), FakeExecutor, job_invalide(), lecture() (+29 more)

### Community 22 - "palettes.py"
Cohesion: 0.08
Nodes (18): interpolate_ramp(), all_palettes(), describe_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors() (+10 more)

### Community 23 - "json"
Cohesion: 0.29
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "stats.py"
Cohesion: 0.10
Nodes (25): correlate(), correlation_pairs(), correlation_pvalue(), describe(), describe_categorical(), describe_full(), interpret_shape(), kurtosis() (+17 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.27
Nodes (12): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+4 more)

### Community 27 - "geometry_kind"
Cohesion: 0.14
Nodes (15): area_m2(), area_method(), dissolved_areas(), geometry_kind(), length_m(), overlap_warning(), perimeter_m(), write_table() (+7 more)

### Community 28 - "compute_breaks"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "fields.py"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+10 more)

### Community 30 - "audit.py"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.07
Nodes (10): PermissionPolicy, Level, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer() (+2 more)

### Community 32 - "dev_setup.py"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 33 - "Données terrain CSV"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.16
Nodes (14): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus(), test_half_plane_contient_le_milieu_cote_a() (+6 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "elevation_sample"
Cohesion: 0.12
Nodes (11): altitude_band(), parse_bands(), _isopleth_geometries(), _clean(), elevation_sample(), _pixel_labels(), _read_window(), _sector_index() (+3 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.15
Nodes (10): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), test_liste_blanche(), test_recherche_multi_termes() (+2 more)

### Community 38 - "tools/project_audit.py"
Cohesion: 0.14
Nodes (13): audit(), build_sections(), duplicate_name_findings(), _finding(), add(), project_findings(), severity_counts(), verdict() (+5 more)

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 41 - "Historique des styles"
Cohesion: 0.18
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "core/atlas.py"
Cohesion: 0.27
Nodes (6): Box, layout_boxes(), page_size(), _label(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.10
Nodes (24): build_categories(), describe_options(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques() (+16 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.09
Nodes (21): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+13 more)

### Community 46 - "fetch_wfs_layer"
Cohesion: 0.17
Nodes (7): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (10): _check(), object_schema(), Param, _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid() (+2 more)

### Community 48 - "ProcessingExecutor"
Cohesion: 0.11
Nodes (8): Fetch, LandcoverPreparationTask, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers()

### Community 49 - "require_field"
Cohesion: 0.16
Nodes (11): compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), group_key() (+3 more)

### Community 50 - "layers.py"
Cohesion: 0.09
Nodes (22): clean_number(), crs_info(), enum_name(), file_format(), get_layer(), get_raster_layer(), layer_kind(), source_path() (+14 more)

### Community 51 - "Tests zonage"
Cohesion: 0.19
Nodes (6): getfeature_url(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 52 - "shapefiles.py"
Cohesion: 0.06
Nodes (31): truncate_field_names(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages() (+23 more)

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "editing.py"
Cohesion: 0.15
Nodes (13): describe_summary(), is_shapefile(), add_field(), _commit_details(), _delete_field_details(), _editing_layers(), _field_limit(), get_pending_edits() (+5 more)

### Community 56 - "move_features"
Cohesion: 0.18
Nodes (9): _change_geometries(), _conform(), _geometries(), _measure(), move_features(), _reference_subset(), _snap(), snap_features() (+1 more)

### Community 57 - "select_ids"
Cohesion: 0.15
Nodes (13): begin_edit(), refresh_layer(), select_ids(), add_features(), calculate_field(), _check_count(), delete_features(), _delete_features_details() (+5 more)

### Community 58 - "Dispatcher"
Cohesion: 0.17
Nodes (3): Response, Dispatcher, finish()

### Community 59 - "describe_groups"
Cohesion: 0.22
Nodes (5): describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 60 - "run_cleanup_steps"
Cohesion: 0.15
Nodes (6): run_cleanup_steps(), test_cleanup_accepts_empty_sequence(), test_cleanup_collects_multiple_errors(), test_cleanup_continues_after_failure(), test_cleanup_does_not_swallow_process_interruptions(), test_cleanup_executes_every_step_in_order()

### Community 61 - "Cache des zonages"
Cohesion: 0.18
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "render_map"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 64 - "re"
Cohesion: 0.15
Nodes (6): find_file(), name_key(), open_table(), _sibling(), test_open_table_zip(), test_versions_aligned()

### Community 65 - "AlgCall"
Cohesion: 0.11
Nodes (8): AlgCall, Executor, Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 66 - "Provenance"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 67 - "get_vector_layer"
Cohesion: 0.15
Nodes (9): needs_priority_field(), convert_area(), get_vector_layer(), _as_multipolygon(), _closer_parts(), detect_overlaps(), resolve_overlaps(), test_conversions() (+1 more)

### Community 69 - "tools/referentials.py"
Cohesion: 0.18
Nodes (5): Pacer, polygon_parts(), clip_reference_landcover(), _clipped(), _overlay()

### Community 70 - "bbox_covers"
Cohesion: 0.50
Nodes (3): bbox_covers(), should_replace_cache(), test_bbox_rules()

### Community 71 - "ToolError"
Cohesion: 0.10
Nodes (17): get_class(), check_landscape(), _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized() (+9 more)

### Community 72 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 73 - "feature_request"
Cohesion: 0.22
Nodes (7): feature_request(), _check_layers(), _distances(), erc_variant_compare(), impact_quantification(), _intersect(), _zones()

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "plugin.py"
Cohesion: 0.08
Nodes (15): QgsLogHandler, setup_logging(), teardown_logging(), Cynogis Plugin Icon (icon.svg), Green Map Location Pin, _allowed(), describe_algorithm(), list_algorithms() (+7 more)

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "core/landscape.py"
Cohesion: 0.08
Nodes (21): apply_mapping(), classes_for(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+13 more)

### Community 78 - "jobs.py"
Cohesion: 0.13
Nodes (3): PrepareLandcover, PreparationCancelledError, obia_prepare_test()

### Community 79 - "pytest"
Cohesion: 0.10
Nodes (27): LandcoverConfig, PreparationConfig, _validate_number(), validate_rgb_bands(), test_register_module_without_tools_fails(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config() (+19 more)

### Community 80 - "build_plugin.py"
Cohesion: 0.24
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

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
Cohesion: 0.10
Nodes (11): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+3 more)

### Community 85 - "find_source_file"
Cohesion: 0.18
Nodes (6): find_source_file(), referentials_directory(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 86 - "core/zoning.py"
Cohesion: 0.12
Nodes (13): assess(), cache_matches(), cache_meta(), for_territory(), _inpn(), status(), Zoning, zoning_state() (+5 more)

### Community 87 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 89 - "connection.py"
Cohesion: 0.29
Nodes (3): new_token(), remove_connection_file(), write_connection_file()

### Community 101 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 102 - "elevation_sample"
Cohesion: 0.11
Nodes (16): aspect_sector(), degrees_to_percent(), distribution(), percent_to_degrees(), reclass_table(), slope_class(), SlopeClass, test_aspect_sector() (+8 more)

### Community 103 - "Security rules (no bypass, no overwrite, no sensitive species/cadastral data)"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 104 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Green Map Location Pin`, `1.2 Interdire les surfaces en EPSG:4326`, `1.5 Gestion des doubles comptes` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 800 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `common.py`, `ToolResult`, `export.py`, `distance_area`, `run_to_project`, `tools/proximity.py`, `JobManager`, `Tests des jobs`, `palettes.py`, `json`, `test_dispatcher.py`, `geometry_kind`, `ToolRegistry`, `elevation_sample`, `tools/project_audit.py`, `BridgeServer`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `require_field`, `layers.py`, `shapefiles.py`, `editing.py`, `move_features`, `select_ids`, `Dispatcher`, `render_map`, `get_vector_layer`, `tools/referentials.py`, `ToolError`, `feature_request`, `plugin.py`, `jobs.py`, `pyqgis.py`, `find_source_file`, `server.py`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Are the 95 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 95 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Green Map Location Pin` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.053313587560162905 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `tools/webservices.py`, `common.py`, `ToolResult`, `export.py`, `distance_area`, `run_to_project`, `tools/proximity.py`, `JobManager`, `Tests des jobs`, `palettes.py`, `json`, `test_dispatcher.py`, `geometry_kind`, `ToolRegistry`, `elevation_sample`, `tools/project_audit.py`, `BridgeServer`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `require_field`, `layers.py`, `shapefiles.py`, `editing.py`, `move_features`, `select_ids`, `Dispatcher`, `render_map`, `get_vector_layer`, `tools/referentials.py`, `ToolError`, `feature_request`, `plugin.py`, `jobs.py`, `pyqgis.py`, `find_source_file`, `server.py`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 145 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 145 INFERRED edges - model-reasoned connections that need verification._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05648148148148148 - nodes in this community are weakly interconnected._