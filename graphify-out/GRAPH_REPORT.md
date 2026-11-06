# Graph Report - cynogis  (2026-11-06)

## Corpus Check
- 138 files · ~103,605 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2160 nodes · 6487 edges · 109 communities (88 shown, 21 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 521 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c6bd69eb`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- tools/webservices.py
- report.py
- common.py
- fields.py
- shapefiles.py
- Proximité et observations
- Métriques paysagères
- Documentation projet
- ToolResult
- Protocole et pont TCP
- core/landscape.py
- numpy
- test_landscape.py
- Coefficients de surface
- Couleurs
- Plugin et démarrage
- core/referentials.py
- tool
- test_terrain.py
- resolve_colors
- Tests des jobs
- shapefile.py
- json
- math
- Journal d'édition
- test_dispatcher.py
- Infos couches
- styling.py
- Champs et types
- audit.py
- ToolRegistry
- BridgeServer
- Données terrain CSV
- Résolution des recouvrements
- allocate
- describe_algorithm
- Catalogue d'algorithmes
- Audit de projet (tests)
- Distances
- tasks.py
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
- style.py
- Feuille de route
- Mise en page atlas
- BridgeError
- move_features
- add_field
- describe_groups
- core/zoning.py
- Cache des zonages
- Plan d'échantillonnage
- to_json_value
- unique_path
- test_project_audit.py
- Fraîcheur des sources
- palettes.py
- Validation des éditions
- Pauses et run_now
- is_natura2000_layer
- ErrorCode
- calculate_field
- require_field
- Guide d'installation
- log.py
- Règles métier réglementaires
- QgsVectorLayer
- confirm.py
- units.py
- Phase 1 surfaces
- Règles d'architecture
- geometry_report
- Adding a tool (@tool decorator, Param, docstring)
- execute_pyqgis
- bbox_covers
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
- save_project
- Territory
- list_style_options
- _closer_parts
- install.ps1
- _tree
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

## Communities (109 total, 21 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.12
Nodes (8): call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job(), main()

### Community 1 - "tools/webservices.py"
Cohesion: 0.06
Nodes (43): Fetch, is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs() (+35 more)

### Community 2 - "report.py"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 3 - "common.py"
Cohesion: 0.15
Nodes (5): Pacer, Level, Param, detect_territory(), polygon_parts()

### Community 4 - "fields.py"
Cohesion: 0.11
Nodes (10): FieldType, sanitize_field_name(), clean_name(), to_ascii(), is_sensitive_field(), mask_sensitive(), sensitive_fields(), test_mask_sensitive_hides_only_sensitive_values() (+2 more)

### Community 5 - "shapefiles.py"
Cohesion: 0.13
Nodes (13): looks_like_mojibake(), crs_from_text(), add_to_group(), add_to_project(), output_dir(), _output_item(), check_shapefile(), export_layer() (+5 more)

### Community 6 - "Proximité et observations"
Cohesion: 0.10
Nodes (21): convert_length(), feature_request(), iter_geometries(), _collect(), count_observations(), count_points_in_polygon(), distance_layer(), _distance_m() (+13 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (32): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), fractal_dimension(), interpret_metrics(), largest_patch_index() (+24 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "ToolResult"
Cohesion: 0.08
Nodes (33): ToolError, needs_priority_field(), add_to_memory(), area_m2(), area_method(), distance_area(), geometry_kind(), make_field() (+25 more)

### Community 10 - "Protocole et pont TCP"
Cohesion: 0.14
Nodes (6): Request, Response, Dispatcher, finish(), collecting(), render_notes()

### Community 11 - "core/landscape.py"
Cohesion: 0.13
Nodes (9): apply_mapping(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), test_apply_mapping_insensible_aux_accents(), test_merge_nomenclature_valide() (+1 more)

### Community 12 - "numpy"
Cohesion: 0.14
Nodes (8): _isopleth_geometries(), _isopleths(), _style(), _clean(), _pixel_labels(), _sector_index(), _slope_aspect(), _surface_factors()

### Community 13 - "test_landscape.py"
Cohesion: 0.12
Nodes (13): classes_for(), score_match(), suggest_mapping(), validate_codes(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_merge_nomenclature_refuse() (+5 more)

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (25): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+17 more)

### Community 15 - "Couleurs"
Cohesion: 0.09
Nodes (20): contrast_ratio(), darken(), distinct_colors(), lighten(), mix(), parse_color(), relative_luminance(), to_hex() (+12 more)

### Community 16 - "Plugin et démarrage"
Cohesion: 0.12
Nodes (5): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin

### Community 17 - "core/referentials.py"
Cohesion: 0.05
Nodes (32): check_rules(), _covers(), find_source_file(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), referentials_directory() (+24 more)

### Community 18 - "tool"
Cohesion: 0.06
Nodes (31): tool(), _allowed(), run_algorithm(), get_raster_layer(), get_vector_layer(), write_report(), check_geometries(), select_features() (+23 more)

### Community 19 - "test_terrain.py"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 20 - "resolve_colors"
Cohesion: 0.14
Nodes (11): interpolate_ramp(), all_palettes(), get_palette(), resolve_colors(), test_interpolate_ramp_extremites_conservees(), test_interpolate_ramp_longueurs(), test_get_palette_etiree(), test_get_palette_inconnue() (+3 more)

### Community 21 - "Tests des jobs"
Cohesion: 0.12
Nodes (24): app(), boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req() (+16 more)

### Community 22 - "shapefile.py"
Cohesion: 0.11
Nodes (16): truncate_field_names(), companion_paths(), export_plan(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), test_truncate_field_names_sans_doublon() (+8 more)

### Community 23 - "json"
Cohesion: 0.22
Nodes (7): decode_request(), _protocol_error(), _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "math"
Cohesion: 0.09
Nodes (25): correlate(), correlation_pairs(), correlation_pvalue(), describe_categorical(), describe_full(), interpret_shape(), kurtosis(), linear_fit() (+17 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 27 - "Infos couches"
Cohesion: 0.12
Nodes (17): clean_number(), crs_info(), enum_name(), file_format(), layer_kind(), source_path(), territory_info(), get_layer_info() (+9 more)

### Community 28 - "styling.py"
Cohesion: 0.11
Nodes (24): clean_values(), compute_breaks(), _dedupe(), equal_interval(), format_number(), natural_breaks(), pretty_breaks(), quantile_breaks() (+16 more)

### Community 29 - "Champs et types"
Cohesion: 0.14
Nodes (14): elongation(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict(), test_coerce_value(), test_coerce_value_date_invalide(), test_coerce_value_dates(), test_coerce_value_decimal_refuse(), test_resolve_type_alias() (+6 more)

### Community 30 - "audit.py"
Cohesion: 0.25
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.19
Nodes (5): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec

### Community 33 - "Données terrain CSV"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 34 - "Résolution des recouvrements"
Cohesion: 0.16
Nodes (14): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus(), test_half_plane_contient_le_milieu_cote_a() (+6 more)

### Community 35 - "allocate"
Cohesion: 0.23
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "describe_algorithm"
Cohesion: 0.29
Nodes (3): describe_algorithm(), is_optional(), _run()

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 38 - "Audit de projet (tests)"
Cohesion: 0.17
Nodes (12): audit(), build_sections(), duplicate_name_findings(), _finding(), project_findings(), severity_counts(), verdict(), _yes_no() (+4 more)

### Community 39 - "Distances"
Cohesion: 0.11
Nodes (14): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), to_float(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible() (+6 more)

### Community 40 - "tasks.py"
Cohesion: 0.06
Nodes (23): _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers(), build_zip(), bump_version() (+15 more)

### Community 41 - "Historique des styles"
Cohesion: 0.15
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "TAXREF"
Cohesion: 0.11
Nodes (15): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+7 more)

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.16
Nodes (16): build_categories(), normalize_geometry(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees(), test_build_categories_lignes_colorees(), test_build_categories_sans_value(), test_history_pop_vide() (+8 more)

### Community 45 - "Enjeux écologiques"
Cohesion: 0.08
Nodes (22): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+14 more)

### Community 46 - "Téléchargement WFS"
Cohesion: 0.17
Nodes (7): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 47 - "Schéma des paramètres"
Cohesion: 0.18
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 48 - "Gestionnaire de jobs"
Cohesion: 0.13
Nodes (3): Executor, Job, JobManager

### Community 49 - "Notes et warnings des jobs"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 50 - "render_map"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 51 - "Tests zonage"
Cohesion: 0.19
Nodes (6): getfeature_url(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 52 - "check_surfaces.py"
Cohesion: 0.17
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 53 - "style.py"
Cohesion: 0.18
Nodes (8): readable_text_color(), _lookup(), _number(), validate_labels(), test_readable_text_color(), test_validate_labels_halo_deduit(), test_validate_labels_placement_inconnu(), test_validate_labels_sans_source()

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "Mise en page atlas"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 56 - "BridgeError"
Cohesion: 0.26
Nodes (5): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 57 - "move_features"
Cohesion: 0.16
Nodes (12): select_ids(), _change_geometries(), _conform(), _delete_features_details(), _geometries(), _measure(), merge_features(), move_features() (+4 more)

### Community 58 - "add_field"
Cohesion: 0.20
Nodes (7): coerce_record(), coerce_value(), _parse_date(), resolve_type(), is_shapefile(), add_field(), _field_limit()

### Community 59 - "describe_groups"
Cohesion: 0.28
Nodes (5): describe(), describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum()

### Community 60 - "core/zoning.py"
Cohesion: 0.12
Nodes (13): assess(), cache_matches(), cache_meta(), for_territory(), _inpn(), status(), Zoning, zoning_state() (+5 more)

### Community 61 - "Cache des zonages"
Cohesion: 0.18
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), _only_fields(), _write_cache(), test_cache_root_env_override()

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "to_json_value"
Cohesion: 0.10
Nodes (11): unique_field_name(), to_json_value(), export_table(), _write_csv(), _geometry_repr(), get_features(), habitat_typology_join(), get_layer_style() (+3 more)

### Community 64 - "unique_path"
Cohesion: 0.18
Nodes (6): unique_path(), _output_path(), save_style_file(), test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

### Community 65 - "test_project_audit.py"
Cohesion: 0.29
Nodes (14): layer_findings(), add(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique() (+6 more)

### Community 66 - "Fraîcheur des sources"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 67 - "palettes.py"
Cohesion: 0.22
Nodes (5): landscape_palette(), load_user_palettes(), register_palette(), validate_palette(), test_validate_palette_trop_courte()

### Community 68 - "Validation des éditions"
Cohesion: 0.15
Nodes (11): describe_summary(), _commit_details(), _delete_field_details(), _editing_layers(), get_pending_edits(), _merge_details(), _reference_subset(), request_commit() (+3 more)

### Community 69 - "Pauses et run_now"
Cohesion: 0.24
Nodes (7): AlgCall, Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 70 - "is_natura2000_layer"
Cohesion: 0.31
Nodes (5): mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 71 - "ErrorCode"
Cohesion: 0.11
Nodes (14): ErrorCode, export_atlas_pdf(), _from_template(), _overview_extent(), expression_context(), extent_wgs84(), get_layer(), prepare_expression() (+6 more)

### Community 72 - "calculate_field"
Cohesion: 0.18
Nodes (9): begin_edit(), refresh_layer(), add_features(), calculate_field(), _check_count(), delete_features(), delete_field(), _record() (+1 more)

### Community 73 - "require_field"
Cohesion: 0.09
Nodes (19): compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), dissolved_areas() (+11 more)

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "log.py"
Cohesion: 0.33
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 76 - "Règles métier réglementaires"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 77 - "QgsVectorLayer"
Cohesion: 0.20
Nodes (5): field_type_name(), geometry_from_wkt(), layer_field_types(), wkt_to_layer_crs(), _field_kind()

### Community 78 - "confirm.py"
Cohesion: 0.22
Nodes (4): build_details(), make_confirmer(), confirm(), register_detail_provider()

### Community 79 - "units.py"
Cohesion: 0.47
Nodes (3): convert_area(), test_conversions(), test_unknown_unit()

### Community 80 - "Phase 1 surfaces"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 81 - "Règles d'architecture"
Cohesion: 0.22
Nodes (6): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), Job response and polling (get_job_status / cancel_job), run_to_project / save_to_project output pipeline, ~/.cynogis/tools_cache.json catalogue cache

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.17
Nodes (10): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Permission levels READ / CREATE / MODIFY / DESTROY, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471, 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD (+2 more)

### Community 84 - "execute_pyqgis"
Cohesion: 0.09
Nodes (11): blocking_calls(), risky_names(), _as_generator(), _details(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm() (+3 more)

### Community 85 - "bbox_covers"
Cohesion: 0.50
Nodes (3): bbox_covers(), should_replace_cache(), test_bbox_rules()

### Community 87 - "BridgeResult"
Cohesion: 0.22
Nodes (8): BridgeResult, CatalogClient, FakeClient, test_catalogue_relu_seulement_si_le_pont_change(), test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 89 - "ToolResult"
Cohesion: 0.11
Nodes (21): ToolResult, get_class(), check_landscape(), _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style() (+13 more)

### Community 102 - "save_project"
Cohesion: 0.50
Nodes (3): _project_target(), save_project(), _save_project_details()

### Community 104 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Green Map Location Pin`, `Phase 0 : Outillage du developpement`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 749 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolResult` to `tools/webservices.py`, `common.py`, `shapefiles.py`, `Proximité et observations`, `Protocole et pont TCP`, `core/referentials.py`, `tool`, `Tests des jobs`, `json`, `test_dispatcher.py`, `Infos couches`, `ToolRegistry`, `BridgeServer`, `Audit de projet (tests)`, `tasks.py`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `render_map`, `move_features`, `add_field`, `to_json_value`, `unique_path`, `Validation des éditions`, `ErrorCode`, `calculate_field`, `require_field`, `QgsVectorLayer`, `execute_pyqgis`, `ToolResult`, `save_project`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 94 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Green Map Location Pin` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `tools/webservices.py`, `common.py`, `shapefiles.py`, `Proximité et observations`, `ToolResult`, `Protocole et pont TCP`, `core/referentials.py`, `tool`, `Tests des jobs`, `json`, `test_dispatcher.py`, `Infos couches`, `ToolRegistry`, `BridgeServer`, `Audit de projet (tests)`, `tasks.py`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `render_map`, `move_features`, `add_field`, `to_json_value`, `unique_path`, `Validation des éditions`, `calculate_field`, `require_field`, `QgsVectorLayer`, `execute_pyqgis`, `ToolResult`, `save_project`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 143 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 143 INFERRED edges - model-reasoned connections that need verification._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06442058496853018 - nodes in this community are weakly interconnected._