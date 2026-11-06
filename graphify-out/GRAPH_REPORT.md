# Graph Report - cynogis  (2026-11-06)

## Corpus Check
- 138 files · ~102,942 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2137 nodes · 6439 edges · 108 communities (86 shown, 22 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 515 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d1808d91`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- Services web WFS/WMS
- report.py
- select_ids
- require_field
- Proximité et observations
- Métriques paysagères
- Documentation projet
- ToolResult
- Protocole et pont TCP
- get_class
- ToolError
- test_landscape.py
- Coefficients de surface
- Couleurs
- Plugin et démarrage
- Référentiels d'occupation du sol
- check_shapefile
- Terrain et pentes
- Palettes
- Tests des jobs
- Contrôle des shapefiles
- detect_territory
- stats.py
- Journal d'édition
- Exécution en tâche de fond
- Infos couches
- classify.py
- Champs et types
- run_in_memory
- ToolRegistry
- plugin.py
- Données terrain CSV
- Résolution des recouvrements
- allocate
- tool
- Catalogue d'algorithmes
- Audit de projet (tests)
- Distances
- Installation développeur
- Historique des styles
- TAXREF
- HABREF
- Tests de style
- Enjeux écologiques
- Téléchargement WFS
- Schéma des paramètres
- Gestionnaire de jobs
- Notes et warnings des jobs
- Audit de projet
- Tests zonage
- contrast_ratio
- Level
- Feuille de route
- Mise en page atlas
- Build du plugin
- move_features
- protocol.py
- pytest
- json
- Cache des zonages
- Plan d'échantillonnage
- get_vector_layer
- core/landscape.py
- bbox_covers
- Fraîcheur des sources
- Cohérence des versions
- Validation des éditions
- Pauses et run_now
- AuditLog
- styling.py
- QgsVectorLayer
- Faits de couches
- Guide d'installation
- Contrôle du code PyQGIS
- Règles métier réglementaires
- _geometry_repr
- check_surfaces.py
- Contrôle des géométries
- Phase 1 surfaces
- Règles d'architecture
- Règles de sécurité
- Règles d'ajout d'outil
- tools/algorithms.py
- Phase 3 traçabilité
- Catégories de coefficients
- BridgeResult
- Commandes de dev
- test_territory.py
- Métadonnées plugin
- Liste blanche algorithmes
- Débogage
- Fin de tâche graphify
- Venv vs Python QGIS
- Compatibilité Qt
- Fichiers locaux
- cynogis-server
- format_number
- regulatory_prescan
- layer_field_types
- organize_layers
- install.ps1
- Rule

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 201 edges
2. `ErrorCode` - 183 edges
3. `tool()` - 154 edges
4. `ToolResult` - 106 edges
5. `get_vector_layer()` - 100 edges
6. `feature_request()` - 67 edges
7. `geometry_kind()` - 60 edges
8. `require_field()` - 56 edges
9. `to_json_value()` - 52 edges
10. `distance_area()` - 51 edges

## Surprising Connections (you probably didn't know these)
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `2.3 Exclure Natura 2000` --semantically_similar_to--> `Natura 2000 not applicable in overseas departments`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `2.6 Pre-diagnostic 100 % deterministe` --semantically_similar_to--> `Deterministic pre-diagnostic, never LLM-written`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
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

## Communities (108 total, 22 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.10
Nodes (13): main(), call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job() (+5 more)

### Community 1 - "Services web WFS/WMS"
Cohesion: 0.06
Nodes (45): is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+37 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 4 - "select_ids"
Cohesion: 0.15
Nodes (13): begin_edit(), refresh_layer(), select_ids(), add_features(), calculate_field(), _check_count(), delete_features(), _delete_features_details() (+5 more)

### Community 5 - "require_field"
Cohesion: 0.16
Nodes (10): compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), overlap_warning() (+2 more)

### Community 6 - "Proximité et observations"
Cohesion: 0.08
Nodes (24): to_float(), convert_area(), convert_length(), feature_request(), iter_geometries(), _collect(), count_observations(), count_points_in_polygon() (+16 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (33): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), fractal_dimension(), interpret_metrics(), largest_patch_index() (+25 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "ToolResult"
Cohesion: 0.06
Nodes (41): ToolResult, Pacer, needs_priority_field(), add_to_memory(), area_m2(), area_method(), dissolved_areas(), distance_area() (+33 more)

### Community 10 - "Protocole et pont TCP"
Cohesion: 0.12
Nodes (6): Response, BridgeServer, Dispatcher, finish(), collecting(), render_notes()

### Community 11 - "get_class"
Cohesion: 0.18
Nodes (8): get_class(), LandscapeClass, merge_nomenclature(), score_match(), test_merge_nomenclature_refuse(), test_merge_nomenclature_valide(), test_score_match_exact_et_mot_cle(), test_score_match_mots_entiers()

### Community 12 - "ToolError"
Cohesion: 0.05
Nodes (35): ErrorCode, ToolError, export_atlas_pdf(), _from_template(), crs_from_text(), prepare_expression(), export_table(), _write_csv() (+27 more)

### Community 13 - "test_landscape.py"
Cohesion: 0.13
Nodes (11): classes_for(), suggest_mapping(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_suggest_mapping_reconnait_les_libelles() (+3 more)

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (25): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+17 more)

### Community 15 - "Couleurs"
Cohesion: 0.10
Nodes (18): darken(), distinct_colors(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string() (+10 more)

### Community 16 - "Plugin et démarrage"
Cohesion: 0.11
Nodes (5): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin

### Community 17 - "Référentiels d'occupation du sol"
Cohesion: 0.07
Nodes (27): _covers(), find_source_file(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), referentials_directory(), _segments() (+19 more)

### Community 18 - "check_shapefile"
Cohesion: 0.18
Nodes (8): looks_like_mojibake(), check_shapefile(), load_layer(), _mojibake_hint(), _scan_sidecars(), set_layer_encoding(), _text_sample(), test_mojibake()

### Community 19 - "Terrain et pentes"
Cohesion: 0.09
Nodes (20): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+12 more)

### Community 20 - "Palettes"
Cohesion: 0.09
Nodes (16): validate_colors(), all_palettes(), describe_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors() (+8 more)

### Community 21 - "Tests des jobs"
Cohesion: 0.12
Nodes (24): app(), boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req() (+16 more)

### Community 22 - "Contrôle des shapefiles"
Cohesion: 0.11
Nodes (15): truncate_field_names(), companion_paths(), export_plan(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), test_truncate_field_names_sans_doublon() (+7 more)

### Community 23 - "detect_territory"
Cohesion: 0.25
Nodes (3): detect_territory(), Territory, _overview_extent()

### Community 24 - "stats.py"
Cohesion: 0.09
Nodes (25): correlate(), correlation_pairs(), correlation_pvalue(), describe_categorical(), describe_full(), interpret_shape(), kurtosis(), linear_fit() (+17 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 26 - "Exécution en tâche de fond"
Cohesion: 0.13
Nodes (6): _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers()

### Community 27 - "Infos couches"
Cohesion: 0.15
Nodes (17): clean_number(), crs_info(), enum_name(), extent_wgs84(), get_layer(), get_raster_layer(), layer_kind(), rect_to_list() (+9 more)

### Community 28 - "classify.py"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "Champs et types"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+10 more)

### Community 30 - "run_in_memory"
Cohesion: 0.32
Nodes (3): _run(), run_in_memory(), distance_layer()

### Community 32 - "plugin.py"
Cohesion: 0.08
Nodes (10): QgsLogHandler, setup_logging(), teardown_logging(), Cynogis Plugin Icon (icon.svg), Green Map Location Pin, ping(), build_details(), make_confirmer() (+2 more)

### Community 33 - "Données terrain CSV"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.16
Nodes (14): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus(), test_half_plane_contient_le_milieu_cote_a() (+6 more)

### Community 35 - "allocate"
Cohesion: 0.28
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "tool"
Cohesion: 0.06
Nodes (29): unique_field_name(), tool(), _isopleth_geometries(), _isopleths(), kernel_density_points(), _style(), buffer(), dissolve() (+21 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.15
Nodes (10): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), test_liste_blanche(), test_recherche_multi_termes() (+2 more)

### Community 38 - "Audit de projet (tests)"
Cohesion: 0.18
Nodes (19): audit(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), _yes_no(), severities() (+11 more)

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 40 - "Installation développeur"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 41 - "Historique des styles"
Cohesion: 0.18
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "TAXREF"
Cohesion: 0.21
Nodes (10): _columns(), match_taxa(), read_statuses(), Statuses, Taxon, listed(), _values(), test_match_taxa() (+2 more)

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.10
Nodes (24): build_categories(), describe_options(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques() (+16 more)

### Community 45 - "Enjeux écologiques"
Cohesion: 0.09
Nodes (21): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+13 more)

### Community 46 - "Téléchargement WFS"
Cohesion: 0.14
Nodes (10): Fetch, service_label(), _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), _local_source(), Source (+2 more)

### Community 47 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (10): _check(), object_schema(), Param, _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid() (+2 more)

### Community 48 - "Gestionnaire de jobs"
Cohesion: 0.13
Nodes (3): Executor, Job, JobManager

### Community 49 - "Notes et warnings des jobs"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 50 - "Audit de projet"
Cohesion: 0.11
Nodes (11): build_sections(), severity_counts(), verdict(), export_map_image(), render_map(), write_document(), write_pdf(), audit_project() (+3 more)

### Community 51 - "Tests zonage"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 52 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 53 - "Level"
Cohesion: 0.16
Nodes (16): PermissionPolicy, Level, decorator(), ToolSpec, crash(), double(), make(), metier() (+8 more)

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "Mise en page atlas"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 56 - "Build du plugin"
Cohesion: 0.22
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 57 - "move_features"
Cohesion: 0.18
Nodes (9): _change_geometries(), _conform(), _geometries(), _measure(), move_features(), _reference_subset(), _snap(), snap_features() (+1 more)

### Community 58 - "protocol.py"
Cohesion: 0.19
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 59 - "pytest"
Cohesion: 0.15
Nodes (9): elongation(), describe(), describe_groups(), test_register_module_without_tools_fails(), test_elongation(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum() (+1 more)

### Community 60 - "json"
Cohesion: 0.17
Nodes (9): assess(), cache_matches(), cache_meta(), _inpn(), read_cache_meta(), Zoning, zoning_state(), test_cache_meta_roundtrip_and_matching() (+1 more)

### Community 61 - "Cache des zonages"
Cohesion: 0.28
Nodes (4): cache_paths(), cache_root(), _write_cache(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.18
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "get_vector_layer"
Cohesion: 0.08
Nodes (20): is_sensitive_field(), mask_sensitive(), sensitive_fields(), get_vector_layer(), length_m(), to_json_value(), check_geometries(), get_features() (+12 more)

### Community 64 - "core/landscape.py"
Cohesion: 0.20
Nodes (6): apply_mapping(), ndvi_deviation(), ndvi_range(), register(), test_apply_mapping_insensible_aux_accents(), test_ndvi_controle()

### Community 65 - "bbox_covers"
Cohesion: 0.50
Nodes (3): bbox_covers(), should_replace_cache(), test_bbox_rules()

### Community 66 - "Fraîcheur des sources"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 67 - "Cohérence des versions"
Cohesion: 0.15
Nodes (6): find_file(), name_key(), open_table(), _sibling(), test_open_table_zip(), test_versions_aligned()

### Community 68 - "Validation des éditions"
Cohesion: 0.18
Nodes (10): describe_summary(), _commit_details(), _delete_field_details(), _editing_layers(), get_pending_edits(), _merge_details(), request_commit(), rollback_edits() (+2 more)

### Community 69 - "Pauses et run_now"
Cohesion: 0.24
Nodes (7): AlgCall, Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 70 - "AuditLog"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 71 - "styling.py"
Cohesion: 0.08
Nodes (16): clean_name(), to_ascii(), unique_path(), mentions_natura2000(), _output_path(), _project_target(), save_project(), _save_project_details() (+8 more)

### Community 72 - "QgsVectorLayer"
Cohesion: 0.22
Nodes (6): expression_context(), geometry_from_wkt(), is_shapefile(), wkt_to_layer_crs(), add_field(), _field_limit()

### Community 73 - "Faits de couches"
Cohesion: 0.29
Nodes (5): file_format(), source_path(), _layer_facts(), _raster_facts(), _vector_facts()

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "Contrôle du code PyQGIS"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 78 - "check_surfaces.py"
Cohesion: 0.27
Nodes (3): check_surface_3d(), square(), synthetic_dem()

### Community 80 - "Phase 1 surfaces"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "Règles de sécurité"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 83 - "Règles d'ajout d'outil"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "tools/algorithms.py"
Cohesion: 0.24
Nodes (5): _allowed(), describe_algorithm(), list_algorithms(), run_algorithm(), is_optional()

### Community 85 - "Phase 3 traçabilité"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

### Community 87 - "BridgeResult"
Cohesion: 0.39
Nodes (6): BridgeResult, FakeClient, test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 89 - "test_territory.py"
Cohesion: 0.38
Nodes (4): test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 102 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 103 - "regulatory_prescan"
Cohesion: 0.40
Nodes (3): for_territory(), regulatory_prescan(), test_par_territoire()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Green Map Location Pin`, `Phase 0 : Outillage du developpement`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 736 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `Services web WFS/WMS`, `dispatcher.py`, `select_ids`, `require_field`, `Proximité et observations`, `ToolResult`, `Protocole et pont TCP`, `Référentiels d'occupation du sol`, `check_shapefile`, `Tests des jobs`, `Exécution en tâche de fond`, `Infos couches`, `run_in_memory`, `plugin.py`, `tool`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `Audit de projet`, `Level`, `move_features`, `protocol.py`, `Plan d'échantillonnage`, `get_vector_layer`, `Validation des éditions`, `styling.py`, `QgsVectorLayer`, `tools/algorithms.py`, `organize_layers`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 94 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Green Map Location Pin` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10420168067226891 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `Services web WFS/WMS`, `dispatcher.py`, `select_ids`, `require_field`, `Proximité et observations`, `ToolResult`, `Protocole et pont TCP`, `Référentiels d'occupation du sol`, `check_shapefile`, `Tests des jobs`, `Exécution en tâche de fond`, `Infos couches`, `run_in_memory`, `plugin.py`, `tool`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `Audit de projet`, `Level`, `move_features`, `protocol.py`, `Plan d'échantillonnage`, `get_vector_layer`, `Validation des éditions`, `styling.py`, `QgsVectorLayer`, `tools/algorithms.py`, `organize_layers`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Are the 142 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 142 INFERRED edges - model-reasoned connections that need verification._
- **Should `Services web WFS/WMS` be split into smaller, more focused modules?**
  _Cohesion score 0.059940059940059943 - nodes in this community are weakly interconnected._