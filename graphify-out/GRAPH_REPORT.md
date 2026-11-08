# Graph Report - cynogis  (2026-11-08)

## Corpus Check
- 140 files · ~104,259 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2184 nodes · 6540 edges · 112 communities (90 shown, 22 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 535 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2397a47d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- tools/webservices.py
- report.py
- common.py
- privacy.py
- shapefiles.py
- Proximité et observations
- Métriques paysagères
- Documentation projet
- save_to_project
- BridgeServer
- core/landscape.py
- numpy
- classes_for
- Coefficients de surface
- Couleurs
- Plugin et démarrage
- find_source_file
- run_to_project
- test_terrain.py
- collections_abc
- Tests des jobs
- _vector_facts
- json
- math
- Journal d'édition
- test_dispatcher.py
- ToolError
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
- profile_table
- Distances
- tasks.py
- Historique des styles
- TAXREF
- HABREF
- Tests de style
- core/stakes.py
- Téléchargement WFS
- Schéma des paramètres
- Gestionnaire de jobs
- Notes et warnings des jobs
- _output_path
- Tests zonage
- check_surface_3d
- style.py
- Feuille de route
- Mise en page atlas
- BridgeError
- get_vector_layer
- core/impacts.py
- describe_groups
- core/zoning.py
- Cache des zonages
- Plan d'échantillonnage
- to_json_value
- naming.py
- test_project_audit.py
- Fraîcheur des sources
- build_plugin.py
- core/referentials.py
- Pauses et run_now
- is_natura2000_layer
- tool
- Pacer
- geometry_kind
- Guide d'installation
- log.py
- Règles métier réglementaires
- risky_names
- confirm.py
- pytest
- Phase 1 surfaces
- Règles d'architecture
- re
- Adding a tool (@tool decorator, Param, docstring)
- execute_pyqgis
- Executor
- Catégories de coefficients
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
- slope_class
- Security rules (no bypass, no overwrite, no sensitive species/cadastral data)
- format_number
- altitude_band
- install.ps1
- Phase 3 : Tracabilite et confidentialite
- CoefficientSpec
- _isopleth_geometries
- app
- Cynogis Plugin Icon (icon.svg)

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 202 edges
2. `ErrorCode` - 184 edges
3. `tool()` - 154 edges
4. `ToolResult` - 106 edges
5. `get_vector_layer()` - 100 edges
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

## Communities (112 total, 22 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.12
Nodes (8): call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job(), main()

### Community 1 - "tools/webservices.py"
Cohesion: 0.07
Nodes (42): is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+34 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "common.py"
Cohesion: 0.14
Nodes (4): ToolResult, Level, Param, layer_kind()

### Community 4 - "privacy.py"
Cohesion: 0.23
Nodes (6): is_sensitive_field(), mask_sensitive(), sensitive_fields(), test_mask_sensitive_hides_only_sensitive_values(), test_sensitive_fields_in_filter_columns(), test_sensitive()

### Community 5 - "shapefiles.py"
Cohesion: 0.09
Nodes (20): ErrorCode, clean_name(), unique_path(), looks_like_mojibake(), export_atlas_pdf(), _from_template(), crs_from_text(), add_to_group() (+12 more)

### Community 6 - "Proximité et observations"
Cohesion: 0.07
Nodes (29): feature_request(), group_key(), iter_geometries(), polygon_parts(), get_field_values(), _check_layers(), _distances(), erc_variant_compare() (+21 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "save_to_project"
Cohesion: 0.08
Nodes (22): unique_field_name(), detect_territory(), Territory, _overview_extent(), add_to_memory(), extent_wgs84(), make_field(), rect_to_list() (+14 more)

### Community 10 - "BridgeServer"
Cohesion: 0.18
Nodes (5): Response, BridgeServer, finish(), collecting(), render_notes()

### Community 11 - "core/landscape.py"
Cohesion: 0.09
Nodes (17): apply_mapping(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+9 more)

### Community 12 - "numpy"
Cohesion: 0.15
Nodes (9): _isopleths(), _style(), _clean(), elevation_sample(), _pixel_labels(), _read_window(), _sector_index(), _slope_aspect() (+1 more)

### Community 13 - "classes_for"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 14 - "Coefficients de surface"
Cohesion: 0.10
Nodes (24): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), _ratio() (+16 more)

### Community 15 - "Couleurs"
Cohesion: 0.09
Nodes (21): contrast_ratio(), darken(), distinct_colors(), interpolate_ramp(), lighten(), mix(), parse_color(), relative_luminance() (+13 more)

### Community 16 - "Plugin et démarrage"
Cohesion: 0.11
Nodes (5): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin

### Community 17 - "find_source_file"
Cohesion: 0.13
Nodes (10): find_source_file(), referentials_directory(), Source, sources_for(), list_reference_sources(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file() (+2 more)

### Community 18 - "run_to_project"
Cohesion: 0.10
Nodes (14): _allowed(), describe_algorithm(), run_algorithm(), buffer(), dissolve(), extract(), fix_geometries(), _name() (+6 more)

### Community 19 - "test_terrain.py"
Cohesion: 0.16
Nodes (11): aspect_sector(), degrees_to_percent(), percent_to_degrees(), reclass_table(), test_aspect_sector(), test_aspect_sector_plat(), test_conversion_pente_aller_retour(), test_pente_45_degres_vaut_cent_pourcent() (+3 more)

### Community 20 - "collections_abc"
Cohesion: 0.09
Nodes (16): validate_colors(), all_palettes(), describe_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors() (+8 more)

### Community 21 - "Tests des jobs"
Cohesion: 0.13
Nodes (24): boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req(), sans_etape() (+16 more)

### Community 22 - "_vector_facts"
Cohesion: 0.06
Nodes (25): companion_paths(), export_plan(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), file_format(), source_path() (+17 more)

### Community 23 - "json"
Cohesion: 0.19
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "math"
Cohesion: 0.11
Nodes (20): correlate(), correlation_pvalue(), describe_full(), interpret_shape(), kurtosis(), linear_fit(), pearson(), percentile() (+12 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.10
Nodes (11): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+3 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "ToolError"
Cohesion: 0.10
Nodes (12): ToolError, get_raster_layer(), compute_ndvi(), extract_ravines(), get_raster_info(), _source(), classify_slope(), derive_terrain() (+4 more)

### Community 28 - "styling.py"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "fields.py"
Cohesion: 0.10
Nodes (20): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), truncate_field_names(), test_coerce_record_champ_inconnu_strict() (+12 more)

### Community 30 - "audit.py"
Cohesion: 0.28
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.13
Nodes (6): Dispatcher, PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec

### Community 32 - "dev_setup.py"
Cohesion: 0.19
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

### Community 36 - "test_referentials.py"
Cohesion: 0.17
Nodes (13): map_cirad(), map_feature(), test_cirad_974_2020_ombre_et_code_inconnu(), test_cirad_974_2020_par_code(), test_cirad_974_millesimes_meme_nomenclature(), test_cirad_976_2023_par_code(), test_map_cirad_canne_selon_territoire(), test_map_cirad_repli_mots_cles() (+5 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 38 - "profile_table"
Cohesion: 0.13
Nodes (9): correlation_pairs(), to_float(), weighted_stats(), correlation_matrix(), _is_empty(), profile_table(), test_pairs_skip_missing(), test_weighted_median() (+1 more)

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 40 - "tasks.py"
Cohesion: 0.13
Nodes (7): Fetch, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers()

### Community 41 - "Historique des styles"
Cohesion: 0.15
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "TAXREF"
Cohesion: 0.15
Nodes (13): _columns(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon, listed() (+5 more)

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.16
Nodes (16): build_categories(), normalize_geometry(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees(), test_build_categories_lignes_colorees(), test_build_categories_sans_value(), test_history_pop_vide() (+8 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.18
Nodes (12): Criterion, level_for(), level_number(), Override, parse_criteria(), parse_overrides(), parse_thresholds(), score() (+4 more)

### Community 46 - "Téléchargement WFS"
Cohesion: 0.17
Nodes (7): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.18
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 49 - "Notes et warnings des jobs"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 50 - "_output_path"
Cohesion: 0.10
Nodes (10): _output_path(), render_map(), write_document(), write_pdf(), write_report(), audit_project(), _open_project(), _overview_map() (+2 more)

### Community 51 - "Tests zonage"
Cohesion: 0.15
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 53 - "style.py"
Cohesion: 0.14
Nodes (10): readable_text_color(), describe_options(), _lookup(), _number(), validate_labels(), test_readable_text_color(), test_describe_options_contenu(), test_validate_labels_halo_deduit() (+2 more)

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "Mise en page atlas"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 56 - "BridgeError"
Cohesion: 0.26
Nodes (5): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 57 - "get_vector_layer"
Cohesion: 0.07
Nodes (41): describe_summary(), begin_edit(), field_type_name(), geometry_from_wkt(), get_vector_layer(), is_shapefile(), layer_field_types(), refresh_layer() (+33 more)

### Community 58 - "core/impacts.py"
Cohesion: 0.17
Nodes (9): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), test_anneaux(), test_comparaison_variantes(), test_poids_enjeu() (+1 more)

### Community 59 - "describe_groups"
Cohesion: 0.21
Nodes (7): describe(), describe_categorical(), describe_groups(), test_categorical_entropy(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum()

### Community 60 - "core/zoning.py"
Cohesion: 0.12
Nodes (12): assess(), bbox_covers(), cache_matches(), cache_meta(), for_territory(), _inpn(), should_replace_cache(), Zoning (+4 more)

### Community 61 - "Cache des zonages"
Cohesion: 0.18
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.25
Nodes (3): _Sampler, _segment(), _systematic()

### Community 63 - "to_json_value"
Cohesion: 0.08
Nodes (14): clean_number(), crs_info(), enum_name(), expression_context(), prepare_expression(), to_json_value(), export_table(), _geometry_repr() (+6 more)

### Community 64 - "naming.py"
Cohesion: 0.25
Nodes (4): to_ascii(), test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

### Community 65 - "test_project_audit.py"
Cohesion: 0.16
Nodes (22): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+14 more)

### Community 66 - "Fraîcheur des sources"
Cohesion: 0.15
Nodes (11): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+3 more)

### Community 67 - "build_plugin.py"
Cohesion: 0.23
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 68 - "core/referentials.py"
Cohesion: 0.20
Nodes (6): _covers(), is_agricultural(), map_ocsge(), Rule, _segments(), test_is_agricultural()

### Community 69 - "Pauses et run_now"
Cohesion: 0.27
Nodes (6): AlgCall, Pause, run_now(), test_run_now(), algo(), steps()

### Community 70 - "is_natura2000_layer"
Cohesion: 0.31
Nodes (5): mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 71 - "tool"
Cohesion: 0.08
Nodes (13): tool(), export_map_image(), _project_target(), save_project(), _save_project_details(), check_geometries(), get_layer_info(), organize_layers() (+5 more)

### Community 72 - "Pacer"
Cohesion: 0.21
Nodes (4): Pacer, clip_reference_landcover(), _clipped(), _overlay()

### Community 73 - "geometry_kind"
Cohesion: 0.07
Nodes (34): convert_area(), convert_length(), compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas() (+26 more)

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "log.py"
Cohesion: 0.33
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "risky_names"
Cohesion: 0.24
Nodes (6): blocking_calls(), risky_names(), _details(), test_appels_bloquants(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 78 - "confirm.py"
Cohesion: 0.33
Nodes (3): build_details(), make_confirmer(), confirm()

### Community 79 - "pytest"
Cohesion: 0.15
Nodes (15): LandcoverConfig, _validate_number(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config(), test_equal_area_thresholds_are_allowed(), test_extremely_large_number_is_rejected(), test_linear_protection_can_be_disabled() (+7 more)

### Community 80 - "Phase 1 surfaces"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "re"
Cohesion: 0.20
Nodes (3): find_file(), _sibling(), test_versions_aligned()

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "execute_pyqgis"
Cohesion: 0.12
Nodes (6): _as_generator(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm(), register_detail_provider()

### Community 87 - "BridgeResult"
Cohesion: 0.22
Nodes (8): BridgeResult, CatalogClient, FakeClient, test_catalogue_relu_seulement_si_le_pont_change(), test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 89 - "ToolResult"
Cohesion: 0.12
Nodes (19): get_layer(), _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _distinct_values() (+11 more)

### Community 102 - "slope_class"
Cohesion: 0.22
Nodes (5): distribution(), slope_class(), SlopeClass, test_distribution(), test_slope_class_negative()

### Community 103 - "Security rules (no bypass, no overwrite, no sensitive species/cadastral data)"
Cohesion: 0.33
Nodes (4): Job response and polling (get_job_status / cancel_job), Permission levels READ / CREATE / MODIFY / DESTROY, run_to_project / save_to_project output pipeline, 3.4 Audit des garde-fous

### Community 104 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 105 - "altitude_band"
Cohesion: 0.40
Nodes (3): altitude_band(), parse_bands(), test_tranches_altitude()

### Community 107 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Green Map Location Pin`, `Phase 0 : Outillage du developpement`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 754 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `common.py`, `shapefiles.py`, `Proximité et observations`, `save_to_project`, `BridgeServer`, `numpy`, `find_source_file`, `run_to_project`, `Tests des jobs`, `json`, `math`, `test_dispatcher.py`, `ToolRegistry`, `profile_table`, `tasks.py`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `_output_path`, `get_vector_layer`, `to_json_value`, `tool`, `Pacer`, `geometry_kind`, `execute_pyqgis`, `ToolResult`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 94 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Green Map Location Pin` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `shapefiles.py` to `tools/webservices.py`, `common.py`, `Proximité et observations`, `save_to_project`, `BridgeServer`, `numpy`, `find_source_file`, `run_to_project`, `Tests des jobs`, `json`, `math`, `test_dispatcher.py`, `ToolError`, `ToolRegistry`, `profile_table`, `tasks.py`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `_output_path`, `get_vector_layer`, `to_json_value`, `tool`, `Pacer`, `geometry_kind`, `execute_pyqgis`, `ToolResult`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 143 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 143 INFERRED edges - model-reasoned connections that need verification._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06690140845070422 - nodes in this community are weakly interconnected._