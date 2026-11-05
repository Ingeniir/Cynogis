# Graph Report - cynogis  (2026-11-05)

## Corpus Check
- 137 files · ~101,908 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2119 nodes · 6416 edges · 101 communities (83 shown, 18 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 517 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dd55527f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- common.py
- Shapefiles et encodage
- Serveur MCP stdio
- styling.py
- geometry_kind
- test_fields.py
- metrics.py
- Coefficients (cœur)
- Feuille de route Cynogis
- dispatcher.py
- Données de terrain
- HABREF
- app.py
- math
- ErrorCode
- tools/terrain.py
- tool
- test_jobs.py
- _clipped
- core/stakes.py
- EditJournal
- test_terrain.py
- elevation_sample
- common.py
- Métriques paysagères
- classify.py
- check_surfaces.py
- core/project_audit.py
- Modèle de sécurité (à ne jamais contourner)
- TAXREF
- core/atlas.py
- test_fields.py (2)
- Point d'entrée du plugin
- Feuille de route
- palettes.py
- find_source_file
- classify.py (2)
- Provenance
- to_float
- core/project_audit.py (2)
- shapefile.py
- Construction du ZIP
- protocol.py
- tasks.py
- Historique des styles
- ToolError
- Installation développeur
- dev_setup.py
- features.py
- Journal d'audit
- Guide d'installation Cynogis (poste entreprise)
- Requêtes WFS
- Catalogue des outils (105 + 4 internes)
- tasks.py (2)
- FakeExecutor
- core/landscape.py
- ToolRegistry
- Dispatcher
- test_stats.py
- run_algorithm
- core/terrain.py
- build_plugin.py
- audit_project
- core/sampling.py
- check_rules
- AuditLog
- core/sampling.py (2)
- BridgeServer
- Rule
- prescan_sections
- Règles réglementaires
- degrees_to_percent
- Adding a tool (@tool decorator, Param, docstring)
- Rapport des fonctionnalités
- contrast_ratio
- get_palette
- Phase 1 : Fiabilite des calculs de surface
- EditJournal (2)
- format_number
- require_field
- bbox_covers
- Phase 2 : Robustesse reglementaire (pre-diagnostic)
- shapefiles.py
- Phase 1 : Fiabilite des calculs de surface
- tools/habref.py
- metadata.txt (Cynogis Reunion-Mayotte 0.1.0)
- Contraintes core et compat Qt
- Contrôle de code PyQGIS (2)
- Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])
- End of task: graphify update and graphify-out commit
- Python 3.14 venv vs QGIS Python 3.12
- Qt5/Qt6 compatibility via compat.py (QGIS 3.x and 4.x)
- export.py (2)
- Adding a tool (@tool decorator, Param, docstring)
- test_naming.py
- CoefficientSpec
- plugin.py

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
- `test_describe_empty_and_single()` --calls--> `describe()`  [INFERRED]
  tests/unit/test_stats.py → plugin/cynogis/core/stats.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `2.6 Pre-diagnostic 100 % deterministe` --semantically_similar_to--> `Deterministic pre-diagnostic, never LLM-written`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `3.4 Audit des garde-fous` --semantically_similar_to--> `Security rules (no bypass, no overwrite, no sensitive species/cadastral data)`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Déploiement d'un poste (partage, plugin, serveur, client MCP)** — installation_network_share, installation_private_qgis_repo, installation_uv_tool_install, installation_cynogis_server_exe, installation_mcp_client_setup, installation_verification_ping [EXTRACTED 1.00]
- **Garde-fous de sécurité Cynogis** — raport_permission_levels, raport_human_confirmation, raport_algorithm_whitelist, raport_no_overwrite_outputs, raport_audit_log, raport_edit_journal, raport_privacy_masking, raport_restricted_network [EXTRACTED 1.00]
- **Non-negotiable regulatory business rules** — claude_territory_crs, claude_area_measurement_rule, claude_surface_3d_rule, claude_natura2000_exclusion, claude_regulatory_thresholds_config, claude_deterministic_prediagnostic [EXTRACTED 1.00]
- **Regles metier codifiees par la phase 2** — claude_natura2000_exclusion, claude_deterministic_prediagnostic, docs_roadmap_phase2_reglementaire [INFERRED 0.85]
- **Règles métier réglementaires (surfaces, 3D, Natura 2000, territoires)** — raport_surface_rules, raport_surface_3d, raport_natura2000_exclusion, raport_territories, raport_regulatory_prescan [INFERRED 0.85]
- **Fiabilite des surfaces (regles, roadmap 1.1-1.3, helpers)** — docs_roadmap_1_1_reference_tests, docs_roadmap_1_2_forbid_4326, docs_roadmap_1_3_surface_method, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.95]

## Communities (101 total, 18 thin omitted)

### Community 0 - "common.py"
Cohesion: 0.06
Nodes (46): is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+38 more)

### Community 1 - "Shapefiles et encodage"
Cohesion: 0.05
Nodes (16): AlgCall, Executor, Fetch, Job, JobManager, Pause, run_now(), _FetchTask (+8 more)

### Community 2 - "Serveur MCP stdio"
Cohesion: 0.08
Nodes (25): to_float(), feature_request(), iter_geometries(), to_json_value(), check_landscape(), suggest_landscape_mapping(), _collect(), count_observations() (+17 more)

### Community 3 - "styling.py"
Cohesion: 0.07
Nodes (22): clean_name(), unique_path(), sensitive_fields(), mentions_natura2000(), export_atlas_pdf(), _from_template(), _overview_extent(), expression_context() (+14 more)

### Community 4 - "geometry_kind"
Cohesion: 0.06
Nodes (33): Pacer, get_class(), needs_priority_field(), add_to_memory(), area_m2(), area_method(), distance_area(), geometry_kind() (+25 more)

### Community 5 - "test_fields.py"
Cohesion: 0.07
Nodes (23): export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), _error_kind(), geometry_report() (+15 more)

### Community 6 - "metrics.py"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 7 - "Coefficients (cœur)"
Cohesion: 0.11
Nodes (21): _covers(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), _segments(), Source, sources_for() (+13 more)

### Community 8 - "Feuille de route Cynogis"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 9 - "dispatcher.py"
Cohesion: 0.11
Nodes (6): render_notes(), Level, Param, _territory(), list_reference_sources(), register_detail_provider()

### Community 10 - "Données de terrain"
Cohesion: 0.12
Nodes (15): darken(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), test_interpolate_ramp_extremites_conservees() (+7 more)

### Community 11 - "HABREF"
Cohesion: 0.10
Nodes (26): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), list_categories() (+18 more)

### Community 12 - "app.py"
Cohesion: 0.08
Nodes (19): main(), call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job() (+11 more)

### Community 13 - "math"
Cohesion: 0.10
Nodes (25): correlate(), correlation_pairs(), correlation_pvalue(), describe_categorical(), describe_full(), interpret_shape(), kurtosis(), linear_fit() (+17 more)

### Community 14 - "ErrorCode"
Cohesion: 0.11
Nodes (14): ErrorCode, export_table(), _write_csv(), _read(), _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style() (+6 more)

### Community 15 - "tools/terrain.py"
Cohesion: 0.11
Nodes (12): unique_field_name(), detect_territory(), Territory, make_field(), import_field_data(), habitat_typology_join(), save_to_project(), create_layer() (+4 more)

### Community 16 - "tool"
Cohesion: 0.07
Nodes (24): tool(), list_coefficients(), save_project(), check_geometries(), buffer(), dissolve(), extract(), fix_geometries() (+16 more)

### Community 17 - "test_jobs.py"
Cohesion: 0.12
Nodes (25): app(), boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req() (+17 more)

### Community 18 - "_clipped"
Cohesion: 0.18
Nodes (6): find_source_file(), referentials_directory(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 19 - "core/stakes.py"
Cohesion: 0.09
Nodes (21): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+13 more)

### Community 20 - "EditJournal"
Cohesion: 0.11
Nodes (22): build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees() (+14 more)

### Community 21 - "test_terrain.py"
Cohesion: 0.21
Nodes (8): aspect_sector(), distribution(), slope_class(), test_aspect_sector(), test_aspect_sector_plat(), test_distribution(), test_slope_class(), test_slope_class_negative()

### Community 22 - "elevation_sample"
Cohesion: 0.12
Nodes (10): _isopleth_geometries(), _isopleths(), _style(), _clean(), elevation_sample(), _pixel_labels(), _read_window(), _sector_index() (+2 more)

### Community 23 - "common.py"
Cohesion: 0.10
Nodes (23): clean_number(), crs_info(), enum_name(), extent_wgs84(), file_format(), get_raster_layer(), layer_kind(), rect_to_list() (+15 more)

### Community 24 - "Métriques paysagères"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 25 - "classify.py"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 26 - "check_surfaces.py"
Cohesion: 0.19
Nodes (6): check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 27 - "core/project_audit.py"
Cohesion: 0.14
Nodes (13): audit(), build_sections(), duplicate_name_findings(), _finding(), add(), project_findings(), severity_counts(), verdict() (+5 more)

### Community 28 - "Modèle de sécurité (à ne jamais contourner)"
Cohesion: 0.16
Nodes (16): Liste blanche ALGORITHMS de run_algorithm, Audit de chaque appel (get_audit_log), Journal d'édition JOURNAL (tampon, request_commit), execute_pyqgis (dernier recours, codecheck indicatif), Confirmation humaine DESTROY (register_detail_provider), Limites connues (JOURNAL en mémoire, un job à la fois…), Sorties jamais écrasées (mcp_outputs, suffixe _2), Niveaux READ / CREATE / MODIFY / DESTROY (+8 more)

### Community 29 - "TAXREF"
Cohesion: 0.10
Nodes (11): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+3 more)

### Community 30 - "core/atlas.py"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 31 - "test_fields.py (2)"
Cohesion: 0.06
Nodes (28): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), to_ascii(), _check() (+20 more)

### Community 32 - "Point d'entrée du plugin"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 33 - "Feuille de route"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 34 - "palettes.py"
Cohesion: 0.11
Nodes (12): distinct_colors(), validate_colors(), with_alpha(), landscape_palette(), register_palette(), resolve_colors(), validate_palette(), test_distinct_colors_sans_doublon() (+4 more)

### Community 35 - "find_source_file"
Cohesion: 0.14
Nodes (14): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+6 more)

### Community 36 - "classify.py (2)"
Cohesion: 0.12
Nodes (15): _comparable(), half_plane_corners(), rank_records(), summarize_resolution(), _closer_parts(), records(), test_egalite_stable(), test_half_plane_centres_confondus() (+7 more)

### Community 37 - "Provenance"
Cohesion: 0.36
Nodes (3): Provenance, provenance_from_data(), test_provenance_roundtrip_and_kind_check()

### Community 38 - "to_float"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 39 - "core/project_audit.py (2)"
Cohesion: 0.32
Nodes (13): layer_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique(), test_projet_sain_sans_anomalie() (+5 more)

### Community 40 - "shapefile.py"
Cohesion: 0.14
Nodes (3): truncate_field_names(), companion_paths(), test_truncate_field_names_sans_doublon()

### Community 41 - "Construction du ZIP"
Cohesion: 0.13
Nodes (11): assess(), cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, zoning_state(), regulatory_prescan() (+3 more)

### Community 42 - "protocol.py"
Cohesion: 0.21
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 43 - "tasks.py"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Historique des styles"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 45 - "ToolError"
Cohesion: 0.08
Nodes (40): ToolResult, describe_summary(), ToolError, begin_edit(), geometry_from_wkt(), get_vector_layer(), is_shapefile(), refresh_layer() (+32 more)

### Community 46 - "Installation développeur"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 47 - "dev_setup.py"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 48 - "features.py"
Cohesion: 0.10
Nodes (13): is_sensitive_field(), mask_sensitive(), field_type_name(), length_m(), _geometry_repr(), get_features(), get_field_values(), correlation_matrix() (+5 more)

### Community 49 - "Journal d'audit"
Cohesion: 0.13
Nodes (10): getfeature_url(), status(), test_describe_multiple_sources_and_missing(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_prescan_sections_lists_sources_with_origin(), test_read_cache_meta_rejects_bad_files() (+2 more)

### Community 50 - "Guide d'installation Cynogis (poste entreprise)"
Cohesion: 0.12
Nodes (20): Cynogis (CLAUDE.md working rules), scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Fichiers propres au poste (connection.json, tools_cache.json, audit/) (+12 more)

### Community 51 - "Requêtes WFS"
Cohesion: 0.11
Nodes (5): new_token(), remove_connection_file(), write_connection_file(), classFactory(), CynogisPlugin

### Community 52 - "Catalogue des outils (105 + 4 internes)"
Cohesion: 0.29
Nodes (7): Outils internes (list_tools, get_job_status, cancel_job), Nomenclature fermée des paysages, regulatory_prescan (pré-diagnostic déterministe), surface_3d (complément, jamais référence réglementaire), Catalogue des outils (105 + 4 internes), Enchaînements typiques attendus de l'IA, Feature domains (~100 tools)

### Community 53 - "tasks.py (2)"
Cohesion: 0.17
Nodes (7): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), Source, _sources(), _wfs_features()

### Community 54 - "FakeExecutor"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 55 - "core/landscape.py"
Cohesion: 0.08
Nodes (22): apply_mapping(), classes_for(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+14 more)

### Community 56 - "ToolRegistry"
Cohesion: 0.13
Nodes (8): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 57 - "Dispatcher"
Cohesion: 0.13
Nodes (5): Response, BridgeServer, Dispatcher, finish(), collecting()

### Community 58 - "test_stats.py"
Cohesion: 0.22
Nodes (5): describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 59 - "run_algorithm"
Cohesion: 0.29
Nodes (3): _allowed(), describe_algorithm(), run_algorithm()

### Community 60 - "core/terrain.py"
Cohesion: 0.22
Nodes (4): altitude_band(), parse_bands(), SlopeClass, test_tranches_altitude()

### Community 61 - "build_plugin.py"
Cohesion: 0.22
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 62 - "audit_project"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 63 - "core/sampling.py"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 65 - "AuditLog"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 66 - "core/sampling.py (2)"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 67 - "BridgeServer"
Cohesion: 0.24
Nodes (5): cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_root_env_override()

### Community 69 - "prescan_sections"
Cohesion: 0.29
Nodes (5): age_days(), describe_sources(), freshness(), prescan_sections(), test_age_never_negative_and_tolerates_garbage()

### Community 70 - "Règles réglementaires"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 71 - "degrees_to_percent"
Cohesion: 0.22
Nodes (7): degrees_to_percent(), percent_to_degrees(), reclass_table(), test_conversion_pente_aller_retour(), test_pente_45_degres_vaut_cent_pourcent(), test_reclass_table_degres(), test_reclass_table_pourcentage()

### Community 72 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.17
Nodes (10): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Permission levels READ / CREATE / MODIFY / DESTROY, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471, 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD (+2 more)

### Community 74 - "Rapport des fonctionnalités"
Cohesion: 0.25
Nodes (5): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Job response and polling (get_job_status / cancel_job), run_to_project / save_to_project output pipeline, ~/.cynogis/tools_cache.json catalogue cache

### Community 75 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 76 - "get_palette"
Cohesion: 0.22
Nodes (6): all_palettes(), get_palette(), load_user_palettes(), test_get_palette_etiree(), test_get_palette_inconnue(), test_load_user_palettes_ignore_les_erreurs()

### Community 77 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 78 - "EditJournal (2)"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 81 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 83 - "require_field"
Cohesion: 0.09
Nodes (20): describe(), convert_area(), convert_length(), compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer() (+12 more)

### Community 84 - "bbox_covers"
Cohesion: 0.50
Nodes (3): bbox_covers(), should_replace_cache(), test_bbox_rules()

### Community 85 - "Phase 2 : Robustesse reglementaire (pre-diagnostic)"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 86 - "shapefiles.py"
Cohesion: 0.13
Nodes (9): crs_from_text(), layer_field_types(), add_to_group(), add_to_project(), is_optional(), _output_item(), _run(), run_in_memory() (+1 more)

### Community 103 - "test_naming.py"
Cohesion: 0.50
Nodes (3): test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

### Community 107 - "plugin.py"
Cohesion: 0.19
Nodes (5): QgsLogHandler, setup_logging(), teardown_logging(), Cynogis Plugin Icon (icon.svg), Green Map Location Pin

## Knowledge Gaps
- **34 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Add-a-tool example (README)`, `3.2/3.3 Donnees sensibles et filtrage RGPD`, `Green Map Location Pin` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 729 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `common.py`, `Shapefiles et encodage`, `Serveur MCP stdio`, `styling.py`, `geometry_kind`, `test_fields.py`, `dispatcher.py`, `ErrorCode`, `tools/terrain.py`, `tool`, `test_jobs.py`, `_clipped`, `elevation_sample`, `common.py`, `core/project_audit.py`, `test_fields.py (2)`, `Feuille de route`, `protocol.py`, `features.py`, `tasks.py (2)`, `FakeExecutor`, `ToolRegistry`, `Dispatcher`, `run_algorithm`, `audit_project`, `require_field`, `shapefiles.py`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 94 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Add-a-tool example (README)` to the rest of the system?**
  _34 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05842259006815969 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ErrorCode` to `common.py`, `Shapefiles et encodage`, `Serveur MCP stdio`, `styling.py`, `geometry_kind`, `test_fields.py`, `dispatcher.py`, `tools/terrain.py`, `tool`, `test_jobs.py`, `_clipped`, `elevation_sample`, `common.py`, `core/project_audit.py`, `test_fields.py (2)`, `Feuille de route`, `protocol.py`, `ToolError`, `features.py`, `tasks.py (2)`, `FakeExecutor`, `ToolRegistry`, `Dispatcher`, `run_algorithm`, `audit_project`, `require_field`, `shapefiles.py`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 142 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 142 INFERRED edges - model-reasoned connections that need verification._
- **Should `Shapefiles et encodage` be split into smaller, more focused modules?**
  _Cohesion score 0.05267778753292362 - nodes in this community are weakly interconnected._