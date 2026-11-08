# Graph Report - cynogis  (2026-11-08)

## Corpus Check
- 141 files · ~105,272 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2199 nodes · 6601 edges · 120 communities (92 shown, 28 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 539 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a69f7561`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- tools/webservices.py
- report.py
- common.py
- privacy.py
- export_atlas_pdf
- Proximité et observations
- Métriques paysagères
- Documentation projet
- ToolError
- BridgeServer
- core/landscape.py
- numpy
- registry.py
- Coefficients de surface
- Couleurs
- CynogisPlugin
- find_source_file
- run_to_project
- test_terrain.py
- collections_abc
- Tests des jobs
- shapefiles.py
- json
- math
- Journal d'édition
- test_dispatcher.py
- tools/terrain.py
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
- test_stats_full.py
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
- layers.py
- Tests zonage
- check_surface_3d
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
- prepare_expression
- naming.py
- test_project_audit.py
- Fraîcheur des sources
- build_plugin.py
- Rule
- Pauses et run_now
- is_natura2000_layer
- tool
- geometry_kind
- geometry_kind
- Guide d'installation
- plugin.py
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
- core/terrain.py
- Security rules (no bypass, no overwrite, no sensitive species/cadastral data)
- format_number
- altitude_band
- install.ps1
- Phase 3 : Tracabilite et confidentialite
- request_commit
- numpy
- app
- detect_overlaps
- Any
- _closer_parts
- test_job_lance_pendant_la_confirmation
- _reject
- run_algorithm
- check_batch_size
- _geometry_repr
- utm_scale

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

## Communities (120 total, 28 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.16
Nodes (8): call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job(), main()

### Community 1 - "tools/webservices.py"
Cohesion: 0.07
Nodes (42): is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+34 more)

### Community 2 - "report.py"
Cohesion: 0.07
Nodes (28): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), mentions_natura2000() (+20 more)

### Community 3 - "common.py"
Cohesion: 0.14
Nodes (5): Level, detect_territory(), Territory, describe_algorithm(), is_optional()

### Community 4 - "privacy.py"
Cohesion: 0.21
Nodes (6): is_sensitive_field(), mask_sensitive(), sensitive_fields(), _is_empty(), test_mask_sensitive_hides_only_sensitive_values(), test_sensitive_fields_in_filter_columns()

### Community 5 - "export_atlas_pdf"
Cohesion: 0.13
Nodes (7): unique_path(), export_atlas_pdf(), field_type_name(), layer_field_types(), export_layer(), save_style_file(), _field_kind()

### Community 6 - "Proximité et observations"
Cohesion: 0.09
Nodes (21): unique_field_name(), to_float(), feature_request(), iter_geometries(), _collect(), count_observations(), count_points_in_polygon(), distance_layer() (+13 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 8 - "Documentation projet"
Cohesion: 0.05
Nodes (49): Alignement de version (0.1.0, build_plugin --bump, test_version), Architecture deux processus (serveur MCP + plugin QGIS via pont TCP), Catalogue des outils (105 + 4 internes), Catalogue d'outils relayé et cache tools_cache.json, Compatibilité QGIS 3.38+ (Qt5) et 4.x (Qt6) via compat.py, Confidentialité : masquage des champs sensibles (privacy.py), Confirmation humaine DESTROY (register_detail_provider), ~/.cynogis/connection.json (découverte du pont) (+41 more)

### Community 9 - "ToolError"
Cohesion: 0.08
Nodes (26): ErrorCode, ToolError, build_table(), add_to_memory(), group_key(), make_field(), _write_csv(), write_table() (+18 more)

### Community 11 - "core/landscape.py"
Cohesion: 0.08
Nodes (20): classes_for(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match(), suggest_mapping() (+12 more)

### Community 12 - "numpy"
Cohesion: 0.20
Nodes (6): elevation_sample(), _pixel_labels(), _read_window(), _sector_index(), _slope_aspect(), _surface_factors()

### Community 13 - "registry.py"
Cohesion: 0.08
Nodes (3): collecting(), needs_priority_field(), register_detail_provider()

### Community 14 - "Coefficients de surface"
Cohesion: 0.09
Nodes (25): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+17 more)

### Community 15 - "Couleurs"
Cohesion: 0.10
Nodes (17): darken(), distinct_colors(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), validate_colors() (+9 more)

### Community 17 - "find_source_file"
Cohesion: 0.13
Nodes (9): find_source_file(), referentials_directory(), Source, sources_for(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent() (+1 more)

### Community 18 - "run_to_project"
Cohesion: 0.13
Nodes (14): get_vector_layer(), _delete_field_details(), _merge_details(), buffer(), dissolve(), extract(), fix_geometries(), _name() (+6 more)

### Community 19 - "test_terrain.py"
Cohesion: 0.22
Nodes (7): degrees_to_percent(), percent_to_degrees(), reclass_table(), test_conversion_pente_aller_retour(), test_pente_45_degres_vaut_cent_pourcent(), test_reclass_table_degres(), test_reclass_table_pourcentage()

### Community 20 - "collections_abc"
Cohesion: 0.09
Nodes (17): interpolate_ramp(), all_palettes(), describe_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors() (+9 more)

### Community 21 - "Tests des jobs"
Cohesion: 0.16
Nodes (20): boucle(), erreur_avant(), lecture(), make(), _req(), sans_etape(), telechargement(), test_annulation() (+12 more)

### Community 22 - "shapefiles.py"
Cohesion: 0.07
Nodes (27): truncate_field_names(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages() (+19 more)

### Community 23 - "json"
Cohesion: 0.29
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 24 - "math"
Cohesion: 0.14
Nodes (16): correlate(), correlation_pairs(), correlation_pvalue(), describe(), describe_full(), interpret_shape(), kurtosis(), linear_fit() (+8 more)

### Community 25 - "Journal d'édition"
Cohesion: 0.12
Nodes (9): EditEntry, EditJournal, journal(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible(), test_describe_summary_vide(), test_summary_filtre() (+1 more)

### Community 26 - "test_dispatcher.py"
Cohesion: 0.30
Nodes (12): crash(), double(), make(), metier(), _req(), supprimer(), test_destroy_with_confirmation(), test_errors() (+4 more)

### Community 27 - "tools/terrain.py"
Cohesion: 0.25
Nodes (5): classify_slope(), derive_terrain(), _flow_accumulation(), list_slope_classes(), _metric_raster()

### Community 28 - "styling.py"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 29 - "fields.py"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+10 more)

### Community 30 - "audit.py"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 31 - "ToolRegistry"
Cohesion: 0.18
Nodes (5): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec

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
Cohesion: 0.28
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 36 - "test_referentials.py"
Cohesion: 0.11
Nodes (20): check_rules(), _covers(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), _segments(), test_cirad_974_2020_ombre_et_code_inconnu() (+12 more)

### Community 37 - "Catalogue d'algorithmes"
Cohesion: 0.14
Nodes (10): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), list_algorithms(), test_liste_blanche(), test_recherche_multi_termes() (+2 more)

### Community 38 - "test_stats_full.py"
Cohesion: 0.18
Nodes (8): ranks(), test_describe_full_shape(), test_empty(), test_outlier_detected(), test_pairs_skip_missing(), test_pearson_and_spearman(), test_ranks_ties(), test_sensitive()

### Community 39 - "Distances"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 40 - "tasks.py"
Cohesion: 0.17
Nodes (4): Fetch, _FetchTask, _Handle, ProcessingExecutor

### Community 41 - "Historique des styles"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 42 - "TAXREF"
Cohesion: 0.20
Nodes (11): _columns(), match_taxa(), read_statuses(), Statuses, Taxon, taxon_status_join(), listed(), _values() (+3 more)

### Community 43 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Tests de style"
Cohesion: 0.10
Nodes (24): build_categories(), describe_options(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques() (+16 more)

### Community 45 - "core/stakes.py"
Cohesion: 0.10
Nodes (20): compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number(), Override (+12 more)

### Community 46 - "Téléchargement WFS"
Cohesion: 0.11
Nodes (13): cache_matches(), for_territory(), _inpn(), service_label(), Zoning, _bbox_wgs84(), _cached_source(), fetch_wfs_layer() (+5 more)

### Community 47 - "Schéma des paramètres"
Cohesion: 0.17
Nodes (11): _check(), object_schema(), Param, _type_ok(), validate_params(), test_decorator_checks(), test_defaults_applied(), test_integer_float_coerced() (+3 more)

### Community 49 - "Notes et warnings des jobs"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 50 - "layers.py"
Cohesion: 0.09
Nodes (24): _overview_extent(), clean_number(), crs_info(), enum_name(), extent_wgs84(), file_format(), get_layer(), get_raster_layer() (+16 more)

### Community 51 - "Tests zonage"
Cohesion: 0.13
Nodes (9): getfeature_url(), status(), test_age_never_negative_and_tolerates_garbage(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut() (+1 more)

### Community 53 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 54 - "Feuille de route"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 55 - "Mise en page atlas"
Cohesion: 0.18
Nodes (9): Box, layout_boxes(), page_size(), _build(), _from_template(), _label(), _north_arrow(), test_formats() (+1 more)

### Community 56 - "BridgeError"
Cohesion: 0.21
Nodes (5): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 57 - "get_vector_layer"
Cohesion: 0.09
Nodes (27): begin_edit(), geometry_from_wkt(), is_shapefile(), refresh_layer(), select_ids(), wkt_to_layer_crs(), add_features(), add_field() (+19 more)

### Community 58 - "Dispatcher"
Cohesion: 0.19
Nodes (3): Dispatcher, finish(), render_notes()

### Community 59 - "describe_groups"
Cohesion: 0.17
Nodes (7): describe_categorical(), describe_groups(), test_categorical_entropy(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 60 - "_vector_facts"
Cohesion: 0.16
Nodes (6): check_geometries(), _error_kind(), geometry_report(), _layer_facts(), _raster_facts(), _vector_facts()

### Community 61 - "Cache des zonages"
Cohesion: 0.12
Nodes (11): bbox_covers(), cache_meta(), cache_paths(), cache_root(), read_cache_meta(), should_replace_cache(), _only_fields(), _write_cache() (+3 more)

### Community 62 - "Plan d'échantillonnage"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 63 - "prepare_expression"
Cohesion: 0.12
Nodes (7): expression_context(), prepare_expression(), kernel_density_points(), _save_isopleths(), export_table(), descriptive_stats(), _local_source()

### Community 64 - "naming.py"
Cohesion: 0.17
Nodes (8): apply_mapping(), clean_name(), normalize(), to_ascii(), test_apply_mapping_insensible_aux_accents(), test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

### Community 65 - "test_project_audit.py"
Cohesion: 0.09
Nodes (27): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+19 more)

### Community 66 - "Fraîcheur des sources"
Cohesion: 0.14
Nodes (12): age_days(), assess(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), zoning_state() (+4 more)

### Community 67 - "build_plugin.py"
Cohesion: 0.22
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 69 - "Pauses et run_now"
Cohesion: 0.27
Nodes (6): AlgCall, Pause, run_now(), test_run_now(), algo(), steps()

### Community 70 - "is_natura2000_layer"
Cohesion: 0.38
Nodes (4): test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 71 - "tool"
Cohesion: 0.09
Nodes (11): tool(), export_map_image(), save_project(), get_features(), get_field_values(), select_features(), suggest_landscape_mapping(), list_reference_sources() (+3 more)

### Community 72 - "geometry_kind"
Cohesion: 0.09
Nodes (14): Pacer, get_class(), geometry_kind(), polygon_parts(), require_field(), check_landscape(), classify_landscape(), compute_ndvi() (+6 more)

### Community 73 - "geometry_kind"
Cohesion: 0.10
Nodes (25): compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), area_m2() (+17 more)

### Community 74 - "Guide d'installation"
Cohesion: 0.22
Nodes (10): scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Dépôt QGIS privé (plugins.xml), Tableau de dépannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN…) (+2 more)

### Community 75 - "plugin.py"
Cohesion: 0.11
Nodes (8): new_token(), remove_connection_file(), write_connection_file(), QgsLogHandler, setup_logging(), teardown_logging(), Cynogis Plugin Icon (icon.svg), Green Map Location Pin

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
Cohesion: 0.14
Nodes (19): LandcoverConfig, _validate_number(), validate_rgb_bands(), test_config_is_immutable(), test_config_is_json_serializable(), test_default_config(), test_equal_area_thresholds_are_allowed(), test_extremely_large_number_is_rejected() (+11 more)

### Community 80 - "Phase 1 surfaces"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 81 - "Règles d'architecture"
Cohesion: 0.33
Nodes (4): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Cynogis (CLAUDE.md working rules), ~/.cynogis/tools_cache.json catalogue cache

### Community 82 - "re"
Cohesion: 0.13
Nodes (7): find_file(), name_key(), open_table(), _sibling(), _source(), test_open_table_zip(), test_versions_aligned()

### Community 83 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.40
Nodes (4): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471

### Community 84 - "execute_pyqgis"
Cohesion: 0.16
Nodes (5): _as_generator(), execute_pyqgis(), _failure(), _fetch(), _run_algorithm()

### Community 87 - "BridgeResult"
Cohesion: 0.22
Nodes (8): BridgeResult, CatalogClient, FakeClient, test_catalogue_relu_seulement_si_le_pont_change(), test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 89 - "ToolResult"
Cohesion: 0.13
Nodes (19): ToolResult, _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _distinct_values() (+11 more)

### Community 102 - "core/terrain.py"
Cohesion: 0.16
Nodes (9): aspect_sector(), distribution(), slope_class(), SlopeClass, test_aspect_sector(), test_aspect_sector_plat(), test_distribution(), test_slope_class() (+1 more)

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

### Community 108 - "request_commit"
Cohesion: 0.24
Nodes (7): describe_summary(), _commit_details(), _editing_layers(), get_pending_edits(), request_commit(), rollback_edits(), _targets()

### Community 109 - "numpy"
Cohesion: 0.22
Nodes (4): _isopleth_geometries(), _isopleths(), _style(), _clean()

### Community 111 - "detect_overlaps"
Cohesion: 0.27
Nodes (5): convert_area(), convert_length(), detect_overlaps(), test_conversions(), test_unknown_unit()

### Community 112 - "Any"
Cohesion: 0.33
Nodes (3): _input_layers(), _needs_main_thread(), _take_layers()

### Community 114 - "test_job_lance_pendant_la_confirmation"
Cohesion: 0.33
Nodes (4): calcul(), effacer(), test_job_lance_pendant_la_confirmation(), confirm()

## Knowledge Gaps
- **40 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `3.2/3.3 Donnees sensibles et filtrage RGPD`, `Green Map Location Pin`, `Phase 0 : Outillage du developpement` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 760 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `tools/webservices.py`, `report.py`, `common.py`, `privacy.py`, `export_atlas_pdf`, `Proximité et observations`, `BridgeServer`, `numpy`, `registry.py`, `find_source_file`, `run_to_project`, `Tests des jobs`, `shapefiles.py`, `json`, `test_dispatcher.py`, `tools/terrain.py`, `ToolRegistry`, `tasks.py`, `TAXREF`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `layers.py`, `Mise en page atlas`, `get_vector_layer`, `Dispatcher`, `_vector_facts`, `prepare_expression`, `test_project_audit.py`, `tool`, `geometry_kind`, `geometry_kind`, `plugin.py`, `re`, `execute_pyqgis`, `ToolResult`, `request_commit`, `detect_overlaps`, `_reject`, `run_algorithm`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Are the 95 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 95 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `3.2/3.3 Donnees sensibles et filtrage RGPD` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/webservices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06690140845070422 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `tools/webservices.py`, `report.py`, `common.py`, `privacy.py`, `export_atlas_pdf`, `Proximité et observations`, `BridgeServer`, `numpy`, `registry.py`, `find_source_file`, `run_to_project`, `Tests des jobs`, `shapefiles.py`, `json`, `test_dispatcher.py`, `tools/terrain.py`, `ToolRegistry`, `tasks.py`, `TAXREF`, `Téléchargement WFS`, `Schéma des paramètres`, `Gestionnaire de jobs`, `Notes et warnings des jobs`, `layers.py`, `Mise en page atlas`, `get_vector_layer`, `Dispatcher`, `_vector_facts`, `prepare_expression`, `test_project_audit.py`, `tool`, `geometry_kind`, `geometry_kind`, `plugin.py`, `re`, `execute_pyqgis`, `ToolResult`, `request_commit`, `detect_overlaps`, `_reject`, `run_algorithm`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 145 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 145 INFERRED edges - model-reasoned connections that need verification._
- **Should `report.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06918238993710692 - nodes in this community are weakly interconnected._