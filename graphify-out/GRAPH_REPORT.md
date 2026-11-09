# Graph Report - cynogis  (2026-11-09)

## Corpus Check
- 144 files · ~107,341 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2249 nodes · 6735 edges · 117 communities (98 shown, 19 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 553 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b516907d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- tools/webservices.py
- report.py
- ToolResult
- privacy.py
- test_landcover_prepare.py
- feature_request
- Métriques paysagères
- Documentation projet
- tools/impacts.py
- core/webservices.py
- test_landscape.py
- prepare.py
- collections_abc
- Coefficients de surface
- Couleurs
- CynogisPlugin
- find_source_file
- run_to_project
- test_webservices.py
- save_palette
- Tests des jobs
- shapefiles.py
- json
- stats.py
- Journal d'édition
- tool
- run_to_project
- styling.py
- fields.py
- audit.py
- ToolRegistry
- dev_setup.py
- Données terrain CSV
- Résolution des recouvrements
- allocate
- test_referentials.py
- Catalogue d'algorithmes
- correlate
- Distances
- tasks.py
- Historique des styles
- nearest_features
- HABREF
- Tests de style
- core/stakes.py
- Téléchargement WFS
- Schéma des paramètres
- Gestionnaire de jobs
- Notes et warnings des jobs
- layers.py
- Tests zonage
- shapefile.py
- contrast_ratio
- Feuille de route
- Mise en page atlas
- BridgeError
- get_vector_layer
- Dispatcher
- describe_groups
- _vector_facts
- Cache des zonages
- Plan d'échantillonnage
- ToolError
- core/landscape.py
- test_project_audit.py
- Fraîcheur des sources
- _vector_facts
- core/referentials.py
- Pauses et run_now
- core/zoning.py
- to_json_value
- profile_table
- geometry_kind
- Guide d'installation
- logging
- Règles métier réglementaires
- get_class
- core/project_audit.py
- pytest
- Phase 1 surfaces
- Règles d'architecture
- re
- Adding a tool (@tool decorator, Param, docstring)
- pyqgis.py
- sidecar_report
- regulatory_prescan
- BridgeResult
- Commandes de dev
- ToolResult
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
- format_number
- _summary
- install.ps1
- Phase 3 : Tracabilite et confidentialite
- list_style_options
- kernel_density_points
- app
- detect_overlaps
- is_agricultural
- resolve_overlaps
- choose_crs
- _reject
- Cynogis Plugin Icon (icon.svg)

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 205 edges
2. `ErrorCode` - 187 edges
3. `tool()` - 156 edges
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

## Communities (117 total, 19 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.12
Nodes (8): call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job(), main()

### Community 1 - "tools/webservices.py"
Cohesion: 0.13
Nodes (16): is_natura2000_layer(), search_layers(), WebService, wfs_params(), wms_params(), add_to_group(), _catalog(), _crs() (+8 more)

### Community 2 - "report.py"
Cohesion: 0.10
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "ToolResult"
Cohesion: 0.13
Nodes (5): ToolResult, Level, Param, describe_algorithm(), is_optional()

### Community 4 - "privacy.py"
Cohesion: 0.23
Nodes (6): is_sensitive_field(), mask_sensitive(), sensitive_fields(), test_mask_sensitive_hides_only_sensitive_values(), test_sensitive_fields_in_filter_columns(), test_sensitive()

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.17
Nodes (17): _crs(), _read(), _rectangle(), _run(), sample(), test_different_crs_is_rejected(), test_empty_analysis_is_rejected(), test_failed_write_cleans_only_its_directory() (+9 more)

### Community 6 - "feature_request"
Cohesion: 0.08
Nodes (32): unique_field_name(), to_float(), add_to_memory(), distance_area(), feature_request(), geometry_kind(), iter_geometries(), make_field() (+24 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (35): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+27 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "tools/impacts.py"
Cohesion: 0.11
Nodes (11): Pacer, polygon_parts(), write_table(), _check_layers(), _distances(), erc_variant_compare(), impact_quantification(), _intersect() (+3 more)

### Community 10 - "core/webservices.py"
Cohesion: 0.23
Nodes (10): check_url(), _child_text(), _children_text(), _crs_list(), _local(), normalize_crs(), _parse_capabilities(), parse_service() (+2 more)

### Community 11 - "test_landscape.py"
Cohesion: 0.15
Nodes (10): classes_for(), suggest_mapping(), validate_codes(), check_rules(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_suggest_mapping_reconnait_les_libelles(), test_suggest_mapping_valeurs_inconnues() (+2 more)

### Community 12 - "prepare.py"
Cohesion: 0.10
Nodes (16): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+8 more)

### Community 13 - "collections_abc"
Cohesion: 0.13
Nodes (9): distinct_colors(), validate_colors(), landscape_palette(), resolve_colors(), _lookup(), test_distinct_colors_sans_doublon(), test_validate_colors_message_indexe(), test_resolve_colors_priorite_aux_couleurs() (+1 more)

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (26): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+18 more)

### Community 15 - "Couleurs"
Cohesion: 0.11
Nodes (16): darken(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), with_alpha() (+8 more)

### Community 16 - "CynogisPlugin"
Cohesion: 0.11
Nodes (5): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin

### Community 17 - "find_source_file"
Cohesion: 0.13
Nodes (9): find_source_file(), referentials_directory(), Source, sources_for(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent() (+1 more)

### Community 18 - "run_to_project"
Cohesion: 0.10
Nodes (18): describe_summary(), get_vector_layer(), _commit_details(), _delete_field_details(), _editing_layers(), get_pending_edits(), _merge_details(), request_commit() (+10 more)

### Community 19 - "test_webservices.py"
Cohesion: 0.19
Nodes (15): capabilities_url(), catalog(), parse_capabilities(), test_catalog_keeps_builtins_and_adds_valid_user_service(), test_catalog_rejects_malformed_file(), test_catalog_rejects_unsafe_or_invalid_entries(), test_lizmap_service_url_keeps_its_query(), test_normalize_crs() (+7 more)

### Community 20 - "save_palette"
Cohesion: 0.12
Nodes (10): all_palettes(), get_palette(), load_user_palettes(), register_palette(), validate_palette(), save_palette(), test_get_palette_etiree(), test_get_palette_inconnue() (+2 more)

### Community 21 - "Tests des jobs"
Cohesion: 0.13
Nodes (23): boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req(), sans_etape() (+15 more)

### Community 22 - "shapefiles.py"
Cohesion: 0.11
Nodes (14): clean_name(), unique_path(), looks_like_mojibake(), crs_from_text(), _output_path(), output_dir(), check_shapefile(), export_layer() (+6 more)

### Community 23 - "json"
Cohesion: 0.21
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "stats.py"
Cohesion: 0.14
Nodes (12): correlation_pvalue(), describe_full(), interpret_shape(), kurtosis(), percentile(), ranks(), skewness(), _t95() (+4 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.11
Nodes (10): EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible(), test_describe_summary_vide() (+2 more)

### Community 26 - "tool"
Cohesion: 0.08
Nodes (25): note(), tool(), decorator(), list_coefficients(), _project_target(), save_project(), _save_project_details(), list_landscape_classes() (+17 more)

### Community 27 - "run_to_project"
Cohesion: 0.12
Nodes (11): compute_ndvi(), extract_ravines(), add_to_project(), _output_item(), _run(), run_to_project(), classify_slope(), derive_terrain() (+3 more)

### Community 28 - "styling.py"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "fields.py"
Cohesion: 0.08
Nodes (22): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), to_ascii(), test_coerce_record_champ_inconnu_strict() (+14 more)

### Community 30 - "audit.py"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.13
Nodes (7): PermissionPolicy, spec_of(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 32 - "dev_setup.py"
Cohesion: 0.11
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

### Community 36 - "test_referentials.py"
Cohesion: 0.22
Nodes (10): map_cirad(), map_feature(), test_cirad_974_2020_ombre_et_code_inconnu(), test_cirad_974_2020_par_code(), test_cirad_974_millesimes_meme_nomenclature(), test_cirad_976_2023_par_code(), test_map_cirad_canne_selon_territoire(), test_map_cirad_repli_mots_cles() (+2 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 38 - "correlate"
Cohesion: 0.15
Nodes (12): correlate(), correlation_pairs(), describe_categorical(), linear_fit(), pearson(), _r(), strength(), weighted_stats() (+4 more)

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 40 - "tasks.py"
Cohesion: 0.13
Nodes (7): Fetch, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers()

### Community 41 - "Historique des styles"
Cohesion: 0.15
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "nearest_features"
Cohesion: 0.15
Nodes (7): _collect(), _distance_m(), distance_matrix(), _hull(), _label(), nearest_features(), _point_hits()

### Community 43 - "HABREF"
Cohesion: 0.11
Nodes (15): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), mentions_natura2000(), test_correspondances() (+7 more)

### Community 44 - "Tests de style"
Cohesion: 0.12
Nodes (21): build_categories(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees(), test_build_categories_lignes_colorees() (+13 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.09
Nodes (21): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+13 more)

### Community 46 - "Téléchargement WFS"
Cohesion: 0.16
Nodes (8): service_label(), _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "Gestionnaire de jobs"
Cohesion: 0.13
Nodes (3): Executor, Job, JobManager

### Community 49 - "Notes et warnings des jobs"
Cohesion: 0.18
Nodes (3): FakeExecutor, job_invalide(), test_notes_ajoutees_aux_warnings()

### Community 50 - "layers.py"
Cohesion: 0.18
Nodes (11): clean_number(), crs_info(), enum_name(), get_layer(), get_raster_layer(), territory_info(), get_layer_info(), get_raster_info() (+3 more)

### Community 51 - "Tests zonage"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 52 - "shapefile.py"
Cohesion: 0.15
Nodes (10): truncate_field_names(), companion_paths(), export_plan(), size_messages(), test_truncate_field_names_sans_doublon(), test_export_plan_renommage(), test_export_plan_type_non_supporte(), test_mojibake() (+2 more)

### Community 53 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "Mise en page atlas"
Cohesion: 0.17
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 56 - "BridgeError"
Cohesion: 0.23
Nodes (6): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario(), handle()

### Community 57 - "get_vector_layer"
Cohesion: 0.08
Nodes (30): check_batch_size(), begin_edit(), field_type_name(), geometry_from_wkt(), is_shapefile(), layer_field_types(), refresh_layer(), select_ids() (+22 more)

### Community 58 - "Dispatcher"
Cohesion: 0.12
Nodes (6): Response, BridgeServer, Dispatcher, finish(), collecting(), render_notes()

### Community 59 - "describe_groups"
Cohesion: 0.24
Nodes (6): describe(), describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 60 - "_vector_facts"
Cohesion: 0.29
Nodes (3): check_geometries(), _error_kind(), geometry_report()

### Community 61 - "Cache des zonages"
Cohesion: 0.18
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "ToolError"
Cohesion: 0.06
Nodes (22): ErrorCode, ToolError, _allowed(), run_algorithm(), export_atlas_pdf(), _from_template(), expression_context(), prepare_expression() (+14 more)

### Community 64 - "core/landscape.py"
Cohesion: 0.20
Nodes (6): apply_mapping(), ndvi_deviation(), ndvi_range(), register(), test_apply_mapping_insensible_aux_accents(), test_ndvi_controle()

### Community 65 - "test_project_audit.py"
Cohesion: 0.25
Nodes (15): audit(), layer_findings(), project_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata() (+7 more)

### Community 66 - "Fraîcheur des sources"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 67 - "_vector_facts"
Cohesion: 0.17
Nodes (8): file_format(), layer_kind(), source_path(), _layer_facts(), _overview_map(), _project_facts(), _raster_facts(), _vector_facts()

### Community 68 - "core/referentials.py"
Cohesion: 0.20
Nodes (7): _covers(), map_ocsge(), Rule, _segments(), test_map_ocsge_a_verifier(), test_map_ocsge_comparaison_par_segments(), test_map_ocsge_territoire()

### Community 69 - "Pauses et run_now"
Cohesion: 0.24
Nodes (7): AlgCall, Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 70 - "core/zoning.py"
Cohesion: 0.19
Nodes (8): bbox_covers(), cache_matches(), cache_meta(), _inpn(), should_replace_cache(), Zoning, test_bbox_rules(), test_cache_meta_roundtrip_and_matching()

### Community 71 - "to_json_value"
Cohesion: 0.11
Nodes (12): detect_territory(), Territory, _overview_extent(), extent_wgs84(), rect_to_list(), to_json_value(), _geometry_repr(), get_features() (+4 more)

### Community 72 - "profile_table"
Cohesion: 0.25
Nodes (4): correlation_matrix(), _field_kind(), _is_empty(), profile_table()

### Community 73 - "geometry_kind"
Cohesion: 0.08
Nodes (25): compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), area_m2() (+17 more)

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "logging"
Cohesion: 0.33
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "get_class"
Cohesion: 0.18
Nodes (8): get_class(), LandscapeClass, merge_nomenclature(), score_match(), test_merge_nomenclature_refuse(), test_merge_nomenclature_valide(), test_score_match_exact_et_mot_cle(), test_score_match_mots_entiers()

### Community 78 - "core/project_audit.py"
Cohesion: 0.26
Nodes (8): build_sections(), duplicate_name_findings(), _finding(), add(), severity_counts(), verdict(), _yes_no(), audit_project()

### Community 79 - "pytest"
Cohesion: 0.10
Nodes (27): LandcoverConfig, PreparationConfig, _validate_number(), validate_rgb_bands(), test_register_module_without_tools_fails(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config() (+19 more)

### Community 80 - "Phase 1 surfaces"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "re"
Cohesion: 0.10
Nodes (16): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+8 more)

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "pyqgis.py"
Cohesion: 0.09
Nodes (12): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+4 more)

### Community 85 - "sidecar_report"
Cohesion: 0.24
Nodes (6): sidecar_messages(), sidecar_report(), SidecarReport, test_sidecar_complet(), test_sidecar_incomplet(), test_sidecar_sans_prj()

### Community 86 - "regulatory_prescan"
Cohesion: 0.20
Nodes (6): assess(), for_territory(), zoning_state(), regulatory_prescan(), test_par_territoire(), test_pre_diagnostic()

### Community 87 - "BridgeResult"
Cohesion: 0.22
Nodes (8): BridgeResult, CatalogClient, FakeClient, test_catalogue_relu_seulement_si_le_pont_change(), test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 89 - "ToolResult"
Cohesion: 0.13
Nodes (17): _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _distinct_values(), _kind() (+9 more)

### Community 102 - "elevation_sample"
Cohesion: 0.08
Nodes (21): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+13 more)

### Community 103 - "Security rules (no bypass, no overwrite, no sensitive species/cadastral data)"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 104 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 105 - "_summary"
Cohesion: 0.29
Nodes (4): list_layers(), _summary(), _tree(), _visible()

### Community 107 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

### Community 108 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 109 - "kernel_density_points"
Cohesion: 0.29
Nodes (3): _isopleths(), kernel_density_points(), _style()

### Community 111 - "detect_overlaps"
Cohesion: 0.43
Nodes (4): convert_area(), convert_length(), test_conversions(), test_unknown_unit()

### Community 113 - "resolve_overlaps"
Cohesion: 0.17
Nodes (5): needs_priority_field(), _as_multipolygon(), _closer_parts(), detect_overlaps(), resolve_overlaps()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `3.2/3.3 Donnees sensibles et filtrage RGPD`, `Phase 0 : Outillage du developpement`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 770 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `ToolResult`, `feature_request`, `tools/impacts.py`, `find_source_file`, `run_to_project`, `save_palette`, `Tests des jobs`, `shapefiles.py`, `json`, `tool`, `run_to_project`, `ToolRegistry`, `tasks.py`, `nearest_features`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `layers.py`, `get_vector_layer`, `Dispatcher`, `_vector_facts`, `_vector_facts`, `to_json_value`, `profile_table`, `geometry_kind`, `pyqgis.py`, `ToolResult`, `elevation_sample`, `kernel_density_points`, `resolve_overlaps`, `_reject`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 95 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 95 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `3.2/3.3 Donnees sensibles et filtrage RGPD` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `tools/webservices.py`, `ToolResult`, `feature_request`, `tools/impacts.py`, `find_source_file`, `run_to_project`, `save_palette`, `Tests des jobs`, `shapefiles.py`, `json`, `tool`, `run_to_project`, `ToolRegistry`, `tasks.py`, `nearest_features`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `layers.py`, `get_vector_layer`, `Dispatcher`, `_vector_facts`, `to_json_value`, `profile_table`, `geometry_kind`, `pyqgis.py`, `ToolResult`, `elevation_sample`, `kernel_density_points`, `resolve_overlaps`, `_reject`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 145 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 145 INFERRED edges - model-reasoned connections that need verification._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1268939393939394 - nodes in this community are weakly interconnected._