# Graph Report - cynogis  (2026-11-09)

## Corpus Check
- 146 files · ~108,073 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2279 nodes · 6810 edges · 103 communities (80 shown, 23 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 583 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e2c45d2b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- tools/webservices.py
- report.py
- ToolResult
- pathlib
- test_landcover_prepare.py
- feature_request
- Métriques paysagères
- Documentation projet
- PreparationControl
- list_coefficients
- test_landscape.py
- prepare.py
- math
- Coefficients de surface
- collections_abc
- CynogisPlugin
- find_source_file
- tool
- CoefficientSpec
- render_map
- Tests des jobs
- make_confirmer
- json
- stats.py
- Journal d'édition
- test_dispatcher.py
- ErrorCode
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
- Distances
- Historique des styles
- HABREF
- Tests de style
- core/stakes.py
- Téléchargement WFS
- Schéma des paramètres
- tasks.py
- Notes et warnings des jobs
- layers.py
- Tests zonage
- shapefile.py
- Feuille de route
- tools/atlas.py
- BridgeError
- get_vector_layer
- Dispatcher
- describe_groups
- Cache des zonages
- Plan d'échantillonnage
- export.py
- core/landscape.py
- test_project_audit.py
- Fraîcheur des sources
- _vector_facts
- core/referentials.py
- elongation
- core/zoning.py
- ToolResult
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
- fetch_wfs_layer
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
- Security rules (no bypass, no overwrite, no sensitive species/cadastral data)
- install.ps1
- Phase 3 : Tracabilite et confidentialite
- list_style_options
- app
- is_agricultural
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

## Communities (103 total, 23 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.12
Nodes (8): call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job(), main()

### Community 1 - "tools/webservices.py"
Cohesion: 0.06
Nodes (43): Fetch, is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs() (+35 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "ToolResult"
Cohesion: 0.16
Nodes (5): Pacer, Level, Param, convert_area(), geometry_kind()

### Community 4 - "pathlib"
Cohesion: 0.06
Nodes (21): column_key(), sanitize_field_name(), clean_name(), normalize(), to_ascii(), is_sensitive_field(), mask_sensitive(), sensitive_fields() (+13 more)

### Community 5 - "test_landcover_prepare.py"
Cohesion: 0.12
Nodes (23): _crs(), _read(), _rectangle(), _run(), sample(), test_already_cancelled_preparation_creates_no_output(), test_cancellation_cleans_own_outputs(), progress() (+15 more)

### Community 6 - "feature_request"
Cohesion: 0.06
Nodes (38): convert_length(), add_to_memory(), distance_area(), feature_request(), iter_geometries(), make_field(), polygon_parts(), _save_isopleths() (+30 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.09
Nodes (22): division_index(), edge_density(), effective_mesh_size(), largest_patch_index(), patch_density(), shape_index(), simpson_index(), summarize_patches() (+14 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "PreparationControl"
Cohesion: 0.18
Nodes (9): PreparationCancelledError, PreparationControl, test_callback_failure_is_not_hidden(), test_cancellation_before_callback(), test_cancellation_check_failure_is_not_hidden(), test_cancellation_requested_during_callback(), progress(), test_default_control_does_nothing() (+1 more)

### Community 11 - "test_landscape.py"
Cohesion: 0.15
Nodes (10): classes_for(), suggest_mapping(), validate_codes(), check_rules(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_suggest_mapping_reconnait_les_libelles(), test_suggest_mapping_valeurs_inconnues() (+2 more)

### Community 12 - "prepare.py"
Cohesion: 0.07
Nodes (23): _aoi_mask(), _check(), _dataset(), _json_number(), prepare_native_inputs(), _read_source(), _srs(), _verify_raster() (+15 more)

### Community 13 - "math"
Cohesion: 0.14
Nodes (10): circularity(), dominance(), fractal_dimension(), interpret_metrics(), mean_patch_size(), shannon_evenness(), shannon_index(), test_shannon_deux_classes_egales() (+2 more)

### Community 14 - "Coefficients de surface"
Cohesion: 0.10
Nodes (24): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), _ratio() (+16 more)

### Community 15 - "collections_abc"
Cohesion: 0.05
Nodes (36): contrast_ratio(), darken(), distinct_colors(), interpolate_ramp(), lighten(), mix(), parse_color(), relative_luminance() (+28 more)

### Community 16 - "CynogisPlugin"
Cohesion: 0.11
Nodes (5): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin

### Community 17 - "find_source_file"
Cohesion: 0.13
Nodes (9): find_source_file(), referentials_directory(), Source, sources_for(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent() (+1 more)

### Community 18 - "tool"
Cohesion: 0.06
Nodes (27): tool(), _allowed(), describe_algorithm(), run_algorithm(), expression_context(), prepare_expression(), kernel_density_points(), export_table() (+19 more)

### Community 21 - "Tests des jobs"
Cohesion: 0.13
Nodes (24): boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req(), sans_etape() (+16 more)

### Community 22 - "make_confirmer"
Cohesion: 0.33
Nodes (3): build_details(), make_confirmer(), confirm()

### Community 23 - "json"
Cohesion: 0.21
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "stats.py"
Cohesion: 0.09
Nodes (25): correlate(), correlation_pairs(), correlation_pvalue(), describe_categorical(), describe_full(), interpret_shape(), kurtosis(), linear_fit() (+17 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.10
Nodes (12): check_batch_size(), describe_summary(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations() (+4 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "ErrorCode"
Cohesion: 0.07
Nodes (20): ErrorCode, unique_field_name(), crs_from_text(), get_raster_layer(), import_field_data(), _read(), inspect_landcover_inputs(), _read_aoi_geometry() (+12 more)

### Community 28 - "styling.py"
Cohesion: 0.06
Nodes (42): clean_values(), compute_breaks(), _dedupe(), equal_interval(), format_number(), natural_breaks(), pretty_breaks(), quantile_breaks() (+34 more)

### Community 29 - "fields.py"
Cohesion: 0.12
Nodes (17): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict(), test_coerce_value() (+9 more)

### Community 30 - "audit.py"
Cohesion: 0.27
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.18
Nodes (5): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec

### Community 32 - "dev_setup.py"
Cohesion: 0.11
Nodes (17): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version(), check_python(), ensure_venv() (+9 more)

### Community 33 - "Données terrain CSV"
Cohesion: 0.14
Nodes (11): parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo(), test_colonnes_terrain() (+3 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.10
Nodes (17): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), _as_multipolygon(), _closer_parts(), records() (+9 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "test_referentials.py"
Cohesion: 0.22
Nodes (10): map_cirad(), map_feature(), test_cirad_974_2020_ombre_et_code_inconnu(), test_cirad_974_2020_par_code(), test_cirad_974_millesimes_meme_nomenclature(), test_cirad_976_2023_par_code(), test_map_cirad_canne_selon_territoire(), test_map_cirad_repli_mots_cles() (+2 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.14
Nodes (10): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), list_algorithms(), test_liste_blanche(), test_recherche_multi_termes() (+2 more)

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 41 - "Historique des styles"
Cohesion: 0.15
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.09
Nodes (26): readable_text_color(), build_categories(), describe_options(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol() (+18 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.08
Nodes (22): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+14 more)

### Community 46 - "Téléchargement WFS"
Cohesion: 0.17
Nodes (7): service_label(), _bbox_wgs84(), _cached_source(), _local_source(), _only_fields(), Source, _sources()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "tasks.py"
Cohesion: 0.05
Nodes (15): AlgCall, Executor, Job, JobManager, Pause, run_now(), _FetchTask, _Handle (+7 more)

### Community 49 - "Notes et warnings des jobs"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 50 - "layers.py"
Cohesion: 0.12
Nodes (19): clean_number(), crs_info(), enum_name(), extent_wgs84(), file_format(), get_layer(), layer_kind(), source_path() (+11 more)

### Community 51 - "Tests zonage"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 52 - "shapefile.py"
Cohesion: 0.10
Nodes (17): truncate_field_names(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages() (+9 more)

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "tools/atlas.py"
Cohesion: 0.09
Nodes (17): Box, layout_boxes(), page_size(), unique_path(), _build(), export_atlas_pdf(), _from_template(), _label() (+9 more)

### Community 56 - "BridgeError"
Cohesion: 0.23
Nodes (6): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario(), handle()

### Community 57 - "get_vector_layer"
Cohesion: 0.08
Nodes (39): ToolError, begin_edit(), geometry_from_wkt(), get_vector_layer(), is_shapefile(), layer_field_types(), refresh_layer(), select_ids() (+31 more)

### Community 58 - "Dispatcher"
Cohesion: 0.13
Nodes (6): Response, BridgeServer, Dispatcher, finish(), collecting(), render_notes()

### Community 59 - "describe_groups"
Cohesion: 0.22
Nodes (6): describe(), describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 61 - "Cache des zonages"
Cohesion: 0.15
Nodes (10): cache_matches(), cache_meta(), cache_paths(), cache_root(), _inpn(), read_cache_meta(), Zoning, _write_cache() (+2 more)

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "export.py"
Cohesion: 0.11
Nodes (9): _output_path(), _project_target(), save_project(), _save_project_details(), _write_csv(), write_document(), write_pdf(), write_report() (+1 more)

### Community 64 - "core/landscape.py"
Cohesion: 0.20
Nodes (6): apply_mapping(), ndvi_deviation(), ndvi_range(), register(), test_apply_mapping_insensible_aux_accents(), test_ndvi_controle()

### Community 65 - "test_project_audit.py"
Cohesion: 0.20
Nodes (18): audit(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons() (+10 more)

### Community 66 - "Fraîcheur des sources"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 67 - "_vector_facts"
Cohesion: 0.15
Nodes (6): _error_kind(), geometry_report(), _layer_facts(), _raster_facts(), _vector_facts(), _scan_sidecars()

### Community 68 - "core/referentials.py"
Cohesion: 0.20
Nodes (7): _covers(), map_ocsge(), Rule, _segments(), test_map_ocsge_a_verifier(), test_map_ocsge_comparaison_par_segments(), test_map_ocsge_territoire()

### Community 70 - "core/zoning.py"
Cohesion: 0.19
Nodes (6): assess(), bbox_covers(), should_replace_cache(), zoning_state(), test_bbox_rules(), test_pre_diagnostic()

### Community 71 - "ToolResult"
Cohesion: 0.10
Nodes (15): ToolResult, detect_territory(), rect_to_list(), check_geometries(), _geometry_repr(), habitat_typology_join(), _territory(), list_reference_sources() (+7 more)

### Community 73 - "geometry_kind"
Cohesion: 0.06
Nodes (34): compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), area_m2() (+26 more)

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
Cohesion: 0.22
Nodes (8): build_sections(), severity_counts(), verdict(), _yes_no(), audit_project(), _open_project(), _overview_map(), _project_facts()

### Community 79 - "pytest"
Cohesion: 0.10
Nodes (28): LandcoverConfig, PreparationConfig, _validate_number(), validate_rgb_bands(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config(), test_equal_area_thresholds_are_allowed() (+20 more)

### Community 80 - "Phase 1 surfaces"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "re"
Cohesion: 0.12
Nodes (14): _columns(), find_file(), match_taxa(), open_table(), read_statuses(), Statuses, Taxon, _sibling() (+6 more)

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "pyqgis.py"
Cohesion: 0.09
Nodes (11): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+3 more)

### Community 86 - "fetch_wfs_layer"
Cohesion: 0.18
Nodes (6): for_territory(), fetch_wfs_layer(), _is_cancel(), regulatory_prescan(), _wfs_features(), test_par_territoire()

### Community 87 - "BridgeResult"
Cohesion: 0.22
Nodes (8): BridgeResult, CatalogClient, FakeClient, test_catalogue_relu_seulement_si_le_pont_change(), test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 102 - "elevation_sample"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 103 - "Security rules (no bypass, no overwrite, no sensitive species/cadastral data)"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 107 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `3.2/3.3 Donnees sensibles et filtrage RGPD`, `Green Map Location Pin`, `Phase 0 : Outillage du developpement` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 779 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `get_vector_layer` to `tools/webservices.py`, `ToolResult`, `feature_request`, `find_source_file`, `tool`, `render_map`, `Tests des jobs`, `json`, `test_dispatcher.py`, `ErrorCode`, `styling.py`, `ToolRegistry`, `Téléchargement WFS`, `Schéma des paramètres`, `tasks.py`, `Notes et warnings des jobs`, `layers.py`, `.__init__`, `tools/atlas.py`, `Dispatcher`, `export.py`, `ToolResult`, `geometry_kind`, `core/project_audit.py`, `pyqgis.py`, `fetch_wfs_layer`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Are the 95 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 95 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `3.2/3.3 Donnees sensibles et filtrage RGPD` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Why does `tool()` connect `tool` to `tools/webservices.py`, `ToolResult`, `feature_request`, `list_coefficients`, `render_map`, `Tests des jobs`, `test_dispatcher.py`, `ErrorCode`, `styling.py`, `ToolRegistry`, `Catalogue d'algorithmes`, `Notes et warnings des jobs`, `layers.py`, `tools/atlas.py`, `get_vector_layer`, `export.py`, `ToolResult`, `geometry_kind`, `core/project_audit.py`, `pyqgis.py`, `fetch_wfs_layer`, `list_style_options`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 145 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 145 INFERRED edges - model-reasoned connections that need verification._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06442058496853018 - nodes in this community are weakly interconnected._