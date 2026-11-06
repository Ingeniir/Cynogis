# Graph Report - cynogis  (2026-11-06)

## Corpus Check
- 138 files · ~103,431 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2155 nodes · 6487 edges · 108 communities (86 shown, 22 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 519 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6e294716`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- json
- tools/webservices.py
- report.py
- dispatcher.py
- fields.py
- feature_request
- Proximité et observations
- Métriques paysagères
- Documentation projet
- ToolResult
- Protocole et pont TCP
- core/landscape.py
- tools/terrain.py
- test_landscape.py
- Coefficients de surface
- Couleurs
- Plugin et démarrage
- find_source_file
- ToolError
- test_terrain.py
- Palettes
- Tests des jobs
- tools/project_audit.py
- core/webservices.py
- math
- Journal d'édition
- Exécution en tâche de fond
- Infos couches
- styling.py
- Champs et types
- _isopleth_geometries
- ToolRegistry
- test_webservices.py
- Données terrain CSV
- Résolution des recouvrements
- allocate
- run_algorithm
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
- render_map
- Tests zonage
- check_surfaces.py
- core/referentials.py
- Feuille de route
- Mise en page atlas
- test_referentials.py
- move_features
- os
- describe_groups
- core/zoning.py
- Cache des zonages
- Plan d'échantillonnage
- get_vector_layer
- core/terrain.py
- test_project_audit.py
- Fraîcheur des sources
- fetch_wfs_layer
- Validation des éditions
- Pauses et run_now
- is_natura2000_layer
- tool
- calculate_field
- landscape_metrics
- Guide d'installation
- log.py
- Règles métier réglementaires
- _overview_map
- classify_slope
- check_rules
- Phase 1 surfaces
- Règles d'architecture
- Règles de sécurité
- Règles d'ajout d'outil
- execute_pyqgis
- Phase 3 traçabilité
- Catégories de coefficients
- BridgeResult
- Commandes de dev
- Pacer
- Métadonnées plugin
- Liste blanche algorithmes
- Débogage
- Fin de tâche graphify
- Venv vs Python QGIS
- Compatibilité Qt
- Fichiers locaux
- cynogis-server
- choose_crs
- list_style_options
- _closer_parts
- install.ps1
- CoefficientSpec
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
- `test_describe_empty_and_single()` --calls--> `describe()`  [INFERRED]
  tests/unit/test_stats.py → plugin/cynogis/core/stats.py
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

### Community 0 - "json"
Cohesion: 0.06
Nodes (37): decode_request(), _protocol_error(), AuditLog, _truncate(), main(), call_tool(), _fetch_specs(), list_tools() (+29 more)

### Community 1 - "tools/webservices.py"
Cohesion: 0.14
Nodes (15): search_layers(), WebService, wfs_params(), wms_params(), _catalog(), _crs(), _layer(), _layers() (+7 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "dispatcher.py"
Cohesion: 0.09
Nodes (7): render_notes(), Level, Param, _project_target(), _save_project_details(), register_detail_provider(), test_decorator_checks()

### Community 4 - "fields.py"
Cohesion: 0.11
Nodes (10): sanitize_field_name(), clean_name(), to_ascii(), unique_path(), _output_path(), save_style_file(), test_clean_name(), test_normalize() (+2 more)

### Community 5 - "feature_request"
Cohesion: 0.17
Nodes (10): build_table(), group_key(), polygon_parts(), write_table(), _check_layers(), _distances(), erc_variant_compare(), impact_quantification() (+2 more)

### Community 6 - "Proximité et observations"
Cohesion: 0.07
Nodes (28): describe(), to_float(), convert_area(), convert_length(), iter_geometries(), length_m(), perimeter_m(), measure() (+20 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "ToolResult"
Cohesion: 0.10
Nodes (24): ToolResult, compute_coefficients(), _reference_areas(), add_to_memory(), area_m2(), area_method(), dissolved_areas(), distance_area() (+16 more)

### Community 10 - "Protocole et pont TCP"
Cohesion: 0.16
Nodes (5): Request, Response, Dispatcher, finish(), test_response_encode_job_id()

### Community 11 - "core/landscape.py"
Cohesion: 0.14
Nodes (9): apply_mapping(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), test_apply_mapping_insensible_aux_accents(), test_merge_nomenclature_valide() (+1 more)

### Community 12 - "tools/terrain.py"
Cohesion: 0.18
Nodes (8): _clean(), elevation_sample(), list_slope_classes(), _pixel_labels(), _read_window(), _sector_index(), _slope_aspect(), _surface_factors()

### Community 13 - "test_landscape.py"
Cohesion: 0.12
Nodes (13): classes_for(), score_match(), suggest_mapping(), validate_codes(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_merge_nomenclature_refuse() (+5 more)

### Community 14 - "Coefficients de surface"
Cohesion: 0.11
Nodes (24): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), _ratio() (+16 more)

### Community 15 - "Couleurs"
Cohesion: 0.09
Nodes (21): contrast_ratio(), darken(), distinct_colors(), interpolate_ramp(), lighten(), mix(), parse_color(), relative_luminance() (+13 more)

### Community 16 - "Plugin et démarrage"
Cohesion: 0.12
Nodes (3): BridgeServer, classFactory(), CynogisPlugin

### Community 17 - "find_source_file"
Cohesion: 0.13
Nodes (9): find_source_file(), referentials_directory(), Source, sources_for(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent() (+1 more)

### Community 18 - "ToolError"
Cohesion: 0.07
Nodes (26): ErrorCode, ToolError, export_atlas_pdf(), _from_template(), expression_context(), get_raster_layer(), prepare_expression(), _isopleths() (+18 more)

### Community 19 - "test_terrain.py"
Cohesion: 0.16
Nodes (11): aspect_sector(), degrees_to_percent(), percent_to_degrees(), reclass_table(), test_aspect_sector(), test_aspect_sector_plat(), test_conversion_pente_aller_retour(), test_pente_45_degres_vaut_cent_pourcent() (+3 more)

### Community 20 - "Palettes"
Cohesion: 0.10
Nodes (15): validate_colors(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors(), validate_palette() (+7 more)

### Community 21 - "Tests des jobs"
Cohesion: 0.13
Nodes (23): app(), boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req() (+15 more)

### Community 22 - "tools/project_audit.py"
Cohesion: 0.06
Nodes (32): truncate_field_names(), unique_field_name(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport (+24 more)

### Community 23 - "core/webservices.py"
Cohesion: 0.23
Nodes (10): check_url(), _child_text(), _children_text(), _crs_list(), _local(), normalize_crs(), _parse_capabilities(), parse_service() (+2 more)

### Community 24 - "math"
Cohesion: 0.10
Nodes (25): correlate(), correlation_pairs(), correlation_pvalue(), describe_categorical(), describe_full(), interpret_shape(), kurtosis(), linear_fit() (+17 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 26 - "Exécution en tâche de fond"
Cohesion: 0.13
Nodes (6): _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers()

### Community 27 - "Infos couches"
Cohesion: 0.09
Nodes (23): _overview_extent(), clean_number(), crs_info(), enum_name(), extent_wgs84(), file_format(), layer_kind(), rect_to_list() (+15 more)

### Community 28 - "styling.py"
Cohesion: 0.06
Nodes (40): clean_values(), compute_breaks(), _dedupe(), equal_interval(), format_number(), natural_breaks(), pretty_breaks(), quantile_breaks() (+32 more)

### Community 29 - "Champs et types"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict(), test_coerce_value() (+10 more)

### Community 31 - "ToolRegistry"
Cohesion: 0.13
Nodes (8): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 32 - "test_webservices.py"
Cohesion: 0.20
Nodes (14): capabilities_url(), catalog(), parse_capabilities(), test_catalog_keeps_builtins_and_adds_valid_user_service(), test_catalog_rejects_malformed_file(), test_catalog_rejects_unsafe_or_invalid_entries(), test_lizmap_service_url_keeps_its_query(), test_normalize_crs() (+6 more)

### Community 33 - "Données terrain CSV"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.14
Nodes (15): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus() (+7 more)

### Community 35 - "allocate"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "run_algorithm"
Cohesion: 0.22
Nodes (4): _allowed(), describe_algorithm(), run_algorithm(), is_optional()

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 38 - "Audit de projet (tests)"
Cohesion: 0.20
Nodes (11): audit(), build_sections(), duplicate_name_findings(), _finding(), add(), project_findings(), severity_counts(), verdict() (+3 more)

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 40 - "Installation développeur"
Cohesion: 0.13
Nodes (17): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version(), check_python(), ensure_venv() (+9 more)

### Community 41 - "Historique des styles"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "TAXREF"
Cohesion: 0.09
Nodes (20): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+12 more)

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.10
Nodes (24): readable_text_color(), build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_readable_text_color() (+16 more)

### Community 45 - "Enjeux écologiques"
Cohesion: 0.10
Nodes (20): compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number(), Override (+12 more)

### Community 46 - "Téléchargement WFS"
Cohesion: 0.14
Nodes (8): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), _local_source(), _only_fields(), Source, _sources()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.18
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "Gestionnaire de jobs"
Cohesion: 0.11
Nodes (4): collecting(), Executor, Job, JobManager

### Community 49 - "Notes et warnings des jobs"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 50 - "render_map"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 51 - "Tests zonage"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 52 - "check_surfaces.py"
Cohesion: 0.17
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 53 - "core/referentials.py"
Cohesion: 0.15
Nodes (8): _covers(), is_agricultural(), map_cirad(), Rule, _segments(), test_is_agricultural(), test_map_cirad_canne_selon_territoire(), test_map_cirad_repli_mots_cles()

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "Mise en page atlas"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 56 - "test_referentials.py"
Cohesion: 0.22
Nodes (11): map_feature(), map_ocsge(), test_cirad_974_2020_ombre_et_code_inconnu(), test_cirad_974_2020_par_code(), test_cirad_974_millesimes_meme_nomenclature(), test_cirad_976_2023_par_code(), test_map_feature_selon_la_source(), test_map_ocsge() (+3 more)

### Community 57 - "move_features"
Cohesion: 0.14
Nodes (15): select_ids(), _change_geometries(), _check_count(), _conform(), delete_features(), _delete_features_details(), _geometries(), _measure() (+7 more)

### Community 58 - "os"
Cohesion: 0.12
Nodes (3): new_token(), remove_connection_file(), write_connection_file()

### Community 59 - "describe_groups"
Cohesion: 0.22
Nodes (5): describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 60 - "core/zoning.py"
Cohesion: 0.14
Nodes (11): assess(), bbox_covers(), cache_matches(), cache_meta(), _inpn(), should_replace_cache(), Zoning, zoning_state() (+3 more)

### Community 61 - "Cache des zonages"
Cohesion: 0.27
Nodes (5): cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_root_env_override()

### Community 63 - "get_vector_layer"
Cohesion: 0.08
Nodes (22): is_sensitive_field(), mask_sensitive(), sensitive_fields(), feature_request(), get_vector_layer(), require_field(), to_json_value(), export_table() (+14 more)

### Community 64 - "core/terrain.py"
Cohesion: 0.15
Nodes (8): altitude_band(), distribution(), parse_bands(), slope_class(), SlopeClass, test_distribution(), test_slope_class_negative(), test_tranches_altitude()

### Community 65 - "test_project_audit.py"
Cohesion: 0.35
Nodes (12): layer_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique(), test_projet_sain_sans_anomalie() (+4 more)

### Community 66 - "Fraîcheur des sources"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 67 - "fetch_wfs_layer"
Cohesion: 0.20
Nodes (6): Fetch, for_territory(), fetch_wfs_layer(), regulatory_prescan(), _wfs_features(), test_par_territoire()

### Community 68 - "Validation des éditions"
Cohesion: 0.15
Nodes (11): describe_summary(), _commit_details(), _delete_field_details(), _editing_layers(), get_pending_edits(), _merge_details(), _reference_subset(), request_commit() (+3 more)

### Community 69 - "Pauses et run_now"
Cohesion: 0.24
Nodes (7): AlgCall, Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 70 - "is_natura2000_layer"
Cohesion: 0.24
Nodes (6): is_natura2000_layer(), mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 71 - "tool"
Cohesion: 0.08
Nodes (14): tool(), get_layer(), delete_field(), export_map_image(), save_project(), write_report(), select_features(), organize_layers() (+6 more)

### Community 72 - "calculate_field"
Cohesion: 0.12
Nodes (12): begin_edit(), field_type_name(), geometry_from_wkt(), is_shapefile(), layer_field_types(), refresh_layer(), wkt_to_layer_crs(), add_features() (+4 more)

### Community 73 - "landscape_metrics"
Cohesion: 0.27
Nodes (5): _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _zones_of()

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "log.py"
Cohesion: 0.32
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "_overview_map"
Cohesion: 0.33
Nodes (3): _open_project(), _overview_map(), _project_facts()

### Community 78 - "classify_slope"
Cohesion: 0.40
Nodes (3): classify_slope(), derive_terrain(), _flow_accumulation()

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

### Community 84 - "execute_pyqgis"
Cohesion: 0.10
Nodes (11): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+3 more)

### Community 85 - "Phase 3 traçabilité"
Cohesion: 0.50
Nodes (4): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, Phase 3 : Tracabilite et confidentialite

### Community 87 - "BridgeResult"
Cohesion: 0.39
Nodes (6): BridgeResult, FakeClient, test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 89 - "Pacer"
Cohesion: 0.12
Nodes (8): Pacer, get_class(), habitat_area_stats(), _r4(), shape_indices(), clip_reference_landcover(), _clipped(), _overlay()

### Community 104 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Green Map Location Pin`, `Phase 0 : Outillage du developpement`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 745 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `json`, `tools/webservices.py`, `dispatcher.py`, `fields.py`, `feature_request`, `Proximité et observations`, `ToolResult`, `Protocole et pont TCP`, `tools/terrain.py`, `Plugin et démarrage`, `find_source_file`, `Tests des jobs`, `tools/project_audit.py`, `Exécution en tâche de fond`, `Infos couches`, `styling.py`, `ToolRegistry`, `run_algorithm`, `TAXREF`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `render_map`, `move_features`, `get_vector_layer`, `fetch_wfs_layer`, `Validation des éditions`, `tool`, `calculate_field`, `landscape_metrics`, `_overview_map`, `classify_slope`, `execute_pyqgis`, `Pacer`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 94 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Green Map Location Pin` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.05517503805175038 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `json`, `tools/webservices.py`, `dispatcher.py`, `fields.py`, `feature_request`, `Proximité et observations`, `ToolResult`, `Protocole et pont TCP`, `tools/terrain.py`, `Plugin et démarrage`, `find_source_file`, `Tests des jobs`, `tools/project_audit.py`, `Exécution en tâche de fond`, `Infos couches`, `styling.py`, `ToolRegistry`, `run_algorithm`, `TAXREF`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `render_map`, `move_features`, `get_vector_layer`, `fetch_wfs_layer`, `Validation des éditions`, `tool`, `calculate_field`, `landscape_metrics`, `_overview_map`, `classify_slope`, `execute_pyqgis`, `Pacer`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 143 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 143 INFERRED edges - model-reasoned connections that need verification._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1425287356321839 - nodes in this community are weakly interconnected._