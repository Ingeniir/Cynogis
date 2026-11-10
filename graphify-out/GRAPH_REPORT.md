# Graph Report - cynogis  (2026-11-10)

## Corpus Check
- 147 files · ~109,052 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2303 nodes · 6904 edges · 114 communities (92 shown, 22 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 600 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0cee607a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- tools/webservices.py
- report.py
- ToolResult
- features.py
- test_landcover_prepare.py
- ToolResult
- Métriques paysagères
- Documentation projet
- PreparationControl
- measures.py
- test_landscape.py
- prepare.py
- math
- Coefficients de surface
- colors.py
- CynogisPlugin
- test_referentials.py
- ErrorCode
- tools/proximity.py
- JobManager
- Tests des jobs
- palettes.py
- json
- stats.py
- Journal d'édition
- test_dispatcher.py
- run_to_project
- styling.py
- fields.py
- audit.py
- ToolRegistry
- dev_setup.py
- Données terrain CSV
- Résolution des recouvrements
- allocate
- elevation_sample
- Catalogue d'algorithmes
- editing.py
- Distances
- move_features
- Historique des styles
- core/atlas.py
- HABREF
- Tests de style
- core/stakes.py
- fetch_wfs_layer
- Schéma des paramètres
- ProcessingExecutor
- Notes et warnings des jobs
- layers.py
- Tests zonage
- shapefile.py
- re
- Feuille de route
- shapefiles.py
- build_plugin.py
- select_ids
- Dispatcher
- describe_groups
- risky_names
- Cache des zonages
- Plan d'échantillonnage
- export.py
- ndvi_deviation
- AlgCall
- prescan_sections
- QgsVectorLayer
- Rule
- elongation
- core/zoning.py
- ToolError
- contrast_ratio
- require_field
- Guide d'installation
- logging
- Règles métier réglementaires
- test_landscape.py
- pytest
- Phase 1 surfaces
- Règles d'architecture
- re
- Adding a tool (@tool decorator, Param, docstring)
- execute_pyqgis
- LandscapeClass
- regulatory_prescan
- BridgeResult
- Commandes de dev
- Provenance
- Métadonnées plugin
- Liste blanche algorithmes
- Débogage
- Fin de tâche graphify
- Venv vs Python QGIS
- Compatibilité Qt
- Fichiers locaux
- cynogis-server
- elevation_sample
- Security rules (no bypass, no overwrite, no sensitive species/cadastral data)
- run_algorithm
- PreparationCancelledError
- install.ps1
- Phase 3 : Tracabilite et confidentialite
- list_style_options
- test_job_lance_pendant_la_confirmation
- app
- Territory
- list_slope_classes
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

## Communities (114 total, 22 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.09
Nodes (13): main(), call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job() (+5 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.07
Nodes (41): capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list(), _local() (+33 more)

### Community 2 - "report.py"
Cohesion: 0.12
Nodes (18): build_markdown(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections(), test_html_echappe_les_balises(), test_html_structure_minimale() (+10 more)

### Community 3 - "ToolResult"
Cohesion: 0.09
Nodes (4): Level, Param, detect_territory(), register_detail_provider()

### Community 4 - "features.py"
Cohesion: 0.09
Nodes (14): Pacer, is_sensitive_field(), mask_sensitive(), sensitive_fields(), check_geometries(), _error_kind(), geometry_report(), _geometry_repr() (+6 more)

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.12
Nodes (23): _crs(), _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs(), progress() (+15 more)

### Community 6 - "ToolResult"
Cohesion: 0.08
Nodes (30): ToolResult, unique_field_name(), add_to_memory(), feature_request(), geometry_kind(), iter_geometries(), make_field(), polygon_parts() (+22 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.08
Nodes (25): division_index(), edge_density(), effective_mesh_size(), largest_patch_index(), patch_density(), shannon_evenness(), shape_index(), simpson_index() (+17 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "PreparationControl"
Cohesion: 0.22
Nodes (8): PreparationControl, test_callback_failure_is_not_hidden(), test_cancellation_before_callback(), test_cancellation_check_failure_is_not_hidden(), test_cancellation_requested_during_callback(), progress(), test_default_control_does_nothing(), test_progress_is_forwarded()

### Community 10 - "measures.py"
Cohesion: 0.08
Nodes (25): get_class(), convert_area(), area_m2(), area_method(), dissolved_areas(), distance_area(), length_m(), perimeter_m() (+17 more)

### Community 11 - "test_landscape.py"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 12 - "prepare.py"
Cohesion: 0.19
Nodes (10): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+2 more)

### Community 13 - "math"
Cohesion: 0.14
Nodes (8): circularity(), dominance(), fractal_dimension(), interpret_metrics(), mean_patch_size(), shannon_index(), utm_scale(), test_shannon_deux_classes_egales()

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (26): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+18 more)

### Community 15 - "colors.py"
Cohesion: 0.10
Nodes (17): darken(), distinct_colors(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), validate_colors() (+9 more)

### Community 16 - "CynogisPlugin"
Cohesion: 0.11
Nodes (5): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin

### Community 17 - "test_referentials.py"
Cohesion: 0.06
Nodes (30): _covers(), find_source_file(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), referentials_directory(), _segments() (+22 more)

### Community 18 - "ErrorCode"
Cohesion: 0.08
Nodes (25): ErrorCode, tool(), export_atlas_pdf(), _from_template(), get_vector_layer(), delete_field(), export_map_image(), save_project() (+17 more)

### Community 19 - "tools/proximity.py"
Cohesion: 0.11
Nodes (16): convert_length(), _collect(), count_observations(), count_points_in_polygon(), _distance_m(), distance_matrix(), _eee_patches(), _field() (+8 more)

### Community 20 - "JobManager"
Cohesion: 0.13
Nodes (4): collecting(), Executor, Job, JobManager

### Community 21 - "Tests des jobs"
Cohesion: 0.14
Nodes (28): boucle(), erreur_avant(), lecture(), make(), make_obia(), _req(), sans_etape(), telechargement() (+20 more)

### Community 22 - "palettes.py"
Cohesion: 0.10
Nodes (16): interpolate_ramp(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors(), validate_palette() (+8 more)

### Community 23 - "json"
Cohesion: 0.21
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "stats.py"
Cohesion: 0.09
Nodes (25): correlate(), correlation_pairs(), correlation_pvalue(), describe_categorical(), describe_full(), interpret_shape(), kurtosis(), linear_fit() (+17 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "run_to_project"
Cohesion: 0.18
Nodes (8): is_optional(), _run(), run_to_project(), classify_slope(), derive_terrain(), _flow_accumulation(), _metric_raster(), zonal_statistics()

### Community 28 - "styling.py"
Cohesion: 0.07
Nodes (43): clean_values(), compute_breaks(), _dedupe(), equal_interval(), format_number(), natural_breaks(), pretty_breaks(), quantile_breaks() (+35 more)

### Community 29 - "fields.py"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+10 more)

### Community 30 - "audit.py"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.13
Nodes (8): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 32 - "dev_setup.py"
Cohesion: 0.24
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

### Community 36 - "elevation_sample"
Cohesion: 0.11
Nodes (10): _clean(), elevation_sample(), _pixel_labels(), _read_window(), _sector_index(), _slope_aspect(), _surface_factors(), check_surface_3d() (+2 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 38 - "editing.py"
Cohesion: 0.15
Nodes (13): describe_summary(), is_shapefile(), add_field(), _commit_details(), _delete_field_details(), _editing_layers(), _field_limit(), get_pending_edits() (+5 more)

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 40 - "move_features"
Cohesion: 0.18
Nodes (9): _change_geometries(), _conform(), _geometries(), _measure(), move_features(), _reference_subset(), _snap(), snap_features() (+1 more)

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
Cohesion: 0.09
Nodes (21): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+13 more)

### Community 46 - "fetch_wfs_layer"
Cohesion: 0.14
Nodes (10): cache_matches(), Zoning, _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), _local_source(), Source (+2 more)

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "ProcessingExecutor"
Cohesion: 0.10
Nodes (9): Fetch, PrepareLandcover, LandcoverPreparationTask, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor (+1 more)

### Community 49 - "Notes et warnings des jobs"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 50 - "layers.py"
Cohesion: 0.10
Nodes (23): _overview_extent(), clean_number(), crs_info(), enum_name(), extent_wgs84(), file_format(), get_layer(), get_raster_layer() (+15 more)

### Community 51 - "Tests zonage"
Cohesion: 0.16
Nodes (8): getfeature_url(), test_describe_multiple_sources_and_missing(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_prescan_sections_lists_sources_with_origin(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 52 - "shapefile.py"
Cohesion: 0.06
Nodes (30): truncate_field_names(), run_now(), build_sections(), severity_counts(), verdict(), companion_paths(), export_plan(), looks_like_mojibake() (+22 more)

### Community 53 - "re"
Cohesion: 0.16
Nodes (4): find_file(), open_table(), _sibling(), test_versions_aligned()

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "shapefiles.py"
Cohesion: 0.09
Nodes (16): clean_name(), to_ascii(), unique_path(), crs_from_text(), _output_path(), add_to_group(), add_to_project(), output_dir() (+8 more)

### Community 56 - "build_plugin.py"
Cohesion: 0.26
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 57 - "select_ids"
Cohesion: 0.16
Nodes (12): begin_edit(), refresh_layer(), select_ids(), add_features(), calculate_field(), _check_count(), delete_features(), _delete_features_details() (+4 more)

### Community 58 - "Dispatcher"
Cohesion: 0.13
Nodes (5): Response, BridgeServer, Dispatcher, finish(), render_notes()

### Community 59 - "describe_groups"
Cohesion: 0.22
Nodes (6): describe(), describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 60 - "risky_names"
Cohesion: 0.24
Nodes (6): blocking_calls(), risky_names(), _details(), test_appels_bloquants(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 61 - "Cache des zonages"
Cohesion: 0.16
Nodes (8): cache_meta(), cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_meta_roundtrip_and_matching(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "export.py"
Cohesion: 0.08
Nodes (13): build_html(), _escape_cell(), mentions_natura2000(), _project_target(), render_map(), _save_project_details(), write_document(), write_pdf() (+5 more)

### Community 64 - "ndvi_deviation"
Cohesion: 0.50
Nodes (3): ndvi_deviation(), ndvi_range(), test_ndvi_controle()

### Community 65 - "AlgCall"
Cohesion: 0.20
Nodes (6): AlgCall, Pause, test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 66 - "prescan_sections"
Cohesion: 0.29
Nodes (5): age_days(), describe_sources(), freshness(), prescan_sections(), test_age_never_negative_and_tolerates_garbage()

### Community 67 - "QgsVectorLayer"
Cohesion: 0.18
Nodes (5): expression_context(), field_type_name(), geometry_from_wkt(), layer_field_types(), wkt_to_layer_crs()

### Community 70 - "core/zoning.py"
Cohesion: 0.16
Nodes (7): bbox_covers(), _inpn(), service_label(), should_replace_cache(), status(), test_bbox_rules(), test_statut()

### Community 71 - "ToolError"
Cohesion: 0.08
Nodes (24): ToolError, to_float(), prepare_expression(), export_table(), _write_csv(), _apply(), apply_categorized_style(), apply_graduated_style() (+16 more)

### Community 72 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 73 - "require_field"
Cohesion: 0.09
Nodes (18): compute_coefficients(), _geometries(), landscape_metrics(), list_coefficients(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of() (+10 more)

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "logging"
Cohesion: 0.33
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "test_landscape.py"
Cohesion: 0.16
Nodes (9): apply_mapping(), score_match(), suggest_mapping(), test_apply_mapping_insensible_aux_accents(), test_merge_nomenclature_refuse(), test_score_match_exact_et_mot_cle(), test_score_match_mots_entiers(), test_suggest_mapping_reconnait_les_libelles() (+1 more)

### Community 79 - "pytest"
Cohesion: 0.10
Nodes (27): LandcoverConfig, PreparationConfig, _validate_number(), validate_rgb_bands(), obia_prepare_test(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config() (+19 more)

### Community 80 - "Phase 1 surfaces"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "re"
Cohesion: 0.18
Nodes (12): _columns(), match_taxa(), name_key(), read_statuses(), Statuses, Taxon, listed(), _values() (+4 more)

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "execute_pyqgis"
Cohesion: 0.16
Nodes (5): _as_generator(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm()

### Community 85 - "LandscapeClass"
Cohesion: 0.25
Nodes (4): LandscapeClass, merge_nomenclature(), register(), test_merge_nomenclature_valide()

### Community 86 - "regulatory_prescan"
Cohesion: 0.17
Nodes (7): is_natura2000_layer(), assess(), for_territory(), zoning_state(), regulatory_prescan(), test_par_territoire(), test_pre_diagnostic()

### Community 87 - "BridgeResult"
Cohesion: 0.22
Nodes (8): BridgeResult, CatalogClient, FakeClient, test_catalogue_relu_seulement_si_le_pont_change(), test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 89 - "Provenance"
Cohesion: 0.36
Nodes (3): Provenance, provenance_from_data(), test_provenance_roundtrip_and_kind_check()

### Community 102 - "elevation_sample"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 103 - "Security rules (no bypass, no overwrite, no sensitive species/cadastral data)"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 104 - "run_algorithm"
Cohesion: 0.29
Nodes (3): _allowed(), describe_algorithm(), run_algorithm()

### Community 107 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

### Community 108 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 109 - "test_job_lance_pendant_la_confirmation"
Cohesion: 0.33
Nodes (4): calcul(), effacer(), test_job_lance_pendant_la_confirmation(), confirm()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `3.2/3.3 Donnees sensibles et filtrage RGPD`, `Green Map Location Pin`, `Phase 0 : Outillage du developpement` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 786 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `ToolResult`, `features.py`, `ToolResult`, `measures.py`, `test_referentials.py`, `ErrorCode`, `tools/proximity.py`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `run_to_project`, `ToolRegistry`, `elevation_sample`, `editing.py`, `move_features`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `Notes et warnings des jobs`, `layers.py`, `shapefile.py`, `shapefiles.py`, `select_ids`, `Dispatcher`, `export.py`, `QgsVectorLayer`, `require_field`, `execute_pyqgis`, `run_algorithm`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Are the 95 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 95 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `3.2/3.3 Donnees sensibles et filtrage RGPD` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09041835357624832 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `tools/webservices.py`, `ToolResult`, `features.py`, `ToolResult`, `measures.py`, `test_referentials.py`, `tools/proximity.py`, `JobManager`, `Tests des jobs`, `json`, `test_dispatcher.py`, `run_to_project`, `ToolRegistry`, `elevation_sample`, `editing.py`, `move_features`, `fetch_wfs_layer`, `Schéma des paramètres`, `ProcessingExecutor`, `Notes et warnings des jobs`, `layers.py`, `shapefile.py`, `shapefiles.py`, `select_ids`, `Dispatcher`, `export.py`, `QgsVectorLayer`, `ToolError`, `require_field`, `execute_pyqgis`, `run_algorithm`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 145 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 145 INFERRED edges - model-reasoned connections that need verification._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06873706004140787 - nodes in this community are weakly interconnected._