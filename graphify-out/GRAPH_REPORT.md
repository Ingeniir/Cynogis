# Graph Report - cynogis  (2026-11-05)

## Corpus Check
- 137 files · ~102,123 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2123 nodes · 6423 edges · 116 communities (92 shown, 24 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 517 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0d2a2282`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- common.py
- Shapefiles et encodage
- Serveur MCP stdio
- tool
- add_to_memory
- shapefile.py
- metrics.py
- Coefficients (cœur)
- Feuille de route Cynogis
- dispatcher.py
- Données de terrain
- HABREF
- app.py
- stats.py
- ErrorCode
- save_to_project
- run_to_project
- test_jobs.py
- _clipped
- core/stakes.py
- EditJournal
- core/terrain.py
- ToolError
- common.py
- Métriques paysagères
- classify.py
- math
- core/project_audit.py
- Modèle de sécurité (à ne jamais contourner)
- TAXREF
- core/atlas.py
- test_fields.py (2)
- Point d'entrée du plugin
- Feuille de route
- naming.py
- find_source_file
- classify.py (2)
- Provenance
- to_float
- core/project_audit.py (2)
- export.py
- Construction du ZIP
- protocol.py
- tasks.py
- Historique des styles
- ToolError
- Installation développeur
- dev_setup.py
- privacy.py
- Journal d'audit
- Guide d'installation Cynogis (poste entreprise)
- Requêtes WFS
- Catalogue des outils (105 + 4 internes)
- tasks.py (2)
- FakeExecutor
- core/landscape.py
- schema.py
- Dispatcher
- test_stats.py
- prepare_expression
- client.py
- build_plugin.py
- audit_project
- core/sampling.py
- classes_for
- AuditLog
- core/sampling.py (2)
- BridgeServer
- Rule
- prescan_sections
- Règles réglementaires
- get_vector_layer
- Adding a tool (@tool decorator, Param, docstring)
- core/impacts.py
- Rapport des fonctionnalités
- contrast_ratio
- resolve_colors
- Phase 1 : Fiabilite des calculs de surface
- EditJournal (2)
- Pacer
- add_features
- format_number
- Any
- geometry_kind
- describe_full
- Phase 2 : Robustesse reglementaire (pre-diagnostic)
- check_shapefile
- Phase 1 : Fiabilite des calculs de surface
- open_table
- metadata.txt (Cynogis Reunion-Mayotte 0.1.0)
- Contraintes core et compat Qt
- Contrôle de code PyQGIS (2)
- Debugging (reload plugin, QGIS_UNAVAILABLE, [UNKNOWN])
- End of task: graphify update and graphify-out commit
- Python 3.14 venv vs QGIS Python 3.12
- Qt5/Qt6 compatibility via compat.py (QGIS 3.x and 4.x)
- export.py (2)
- Adding a tool (@tool decorator, Param, docstring)
- mentions_natura2000
- check_geometries
- CoefficientSpec
- BridgeResult
- regulatory_prescan
- plugin.py
- units.py
- re
- list_coefficients
- elongation
- is_agricultural
- _geometry_repr
- descriptive_stats
- Cynogis Plugin Icon (icon.svg)

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
- **Garde-fous de sécurité Cynogis** — raport_permission_levels, raport_human_confirmation, raport_algorithm_whitelist, raport_no_overwrite_outputs, raport_audit_log, raport_edit_journal, raport_privacy_masking, raport_restricted_network [EXTRACTED 1.00]
- **Non-negotiable regulatory business rules** — claude_territory_crs, claude_area_measurement_rule, claude_surface_3d_rule, claude_natura2000_exclusion, claude_regulatory_thresholds_config, claude_deterministic_prediagnostic [EXTRACTED 1.00]
- **Regles metier codifiees par la phase 2** — claude_natura2000_exclusion, claude_deterministic_prediagnostic, docs_roadmap_phase2_reglementaire [INFERRED 0.85]
- **Règles métier réglementaires (surfaces, 3D, Natura 2000, territoires)** — raport_surface_rules, raport_surface_3d, raport_natura2000_exclusion, raport_territories, raport_regulatory_prescan [INFERRED 0.85]
- **Fiabilite des surfaces (regles, roadmap 1.1-1.3, helpers)** — docs_roadmap_1_1_reference_tests, docs_roadmap_1_2_forbid_4326, docs_roadmap_1_3_surface_method, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.95]

## Communities (116 total, 24 thin omitted)

### Community 0 - "common.py"
Cohesion: 0.07
Nodes (40): capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list(), _local() (+32 more)

### Community 1 - "Shapefiles et encodage"
Cohesion: 0.06
Nodes (14): AlgCall, Job, JobManager, Pause, run_now(), _FetchTask, _Handle, _input_layers() (+6 more)

### Community 2 - "Serveur MCP stdio"
Cohesion: 0.10
Nodes (19): feature_request(), iter_geometries(), _collect(), count_observations(), count_points_in_polygon(), _distance_m(), distance_matrix(), distance_to_sensitive_features() (+11 more)

### Community 3 - "tool"
Cohesion: 0.07
Nodes (22): ToolResult, unique_path(), tool(), export_atlas_pdf(), get_layer(), export_map_image(), _output_path(), write_report() (+14 more)

### Community 4 - "add_to_memory"
Cohesion: 0.10
Nodes (17): build_table(), add_to_memory(), group_key(), make_field(), polygon_parts(), _isopleth_geometries(), _save_isopleths(), write_table() (+9 more)

### Community 5 - "shapefile.py"
Cohesion: 0.11
Nodes (16): truncate_field_names(), companion_paths(), export_plan(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), test_truncate_field_names_sans_doublon() (+8 more)

### Community 6 - "metrics.py"
Cohesion: 0.07
Nodes (31): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), interpret_metrics(), largest_patch_index(), mean_patch_size() (+23 more)

### Community 7 - "Coefficients (cœur)"
Cohesion: 0.12
Nodes (19): _covers(), map_cirad(), map_feature(), map_ocsge(), _segments(), Source, sources_for(), test_cirad_974_2020_ombre_et_code_inconnu() (+11 more)

### Community 8 - "Feuille de route Cynogis"
Cohesion: 0.13
Nodes (13): Feuille de route Cynogis, Jalons, Phase 0 : Outillage du developpement, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic) (+5 more)

### Community 10 - "Données de terrain"
Cohesion: 0.10
Nodes (20): darken(), distinct_colors(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string() (+12 more)

### Community 11 - "HABREF"
Cohesion: 0.10
Nodes (24): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), _ratio() (+16 more)

### Community 12 - "app.py"
Cohesion: 0.16
Nodes (8): call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job(), main()

### Community 13 - "stats.py"
Cohesion: 0.22
Nodes (9): correlate(), correlation_pvalue(), linear_fit(), pearson(), _r(), ranks(), strength(), test_pearson_and_spearman() (+1 more)

### Community 14 - "ErrorCode"
Cohesion: 0.12
Nodes (18): to_float(), _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _distinct_values() (+10 more)

### Community 15 - "save_to_project"
Cohesion: 0.10
Nodes (12): unique_field_name(), crs_from_text(), _write_csv(), import_field_data(), _read(), habitat_typology_join(), save_to_project(), distance_layer() (+4 more)

### Community 16 - "run_to_project"
Cohesion: 0.08
Nodes (17): _allowed(), describe_algorithm(), run_algorithm(), buffer(), dissolve(), extract(), fix_geometries(), _name() (+9 more)

### Community 17 - "test_jobs.py"
Cohesion: 0.12
Nodes (25): app(), boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req() (+17 more)

### Community 18 - "_clipped"
Cohesion: 0.18
Nodes (6): find_source_file(), referentials_directory(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 19 - "core/stakes.py"
Cohesion: 0.19
Nodes (12): Criterion, level_for(), level_number(), Override, parse_criteria(), parse_overrides(), parse_thresholds(), score() (+4 more)

### Community 20 - "EditJournal"
Cohesion: 0.11
Nodes (22): build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees() (+14 more)

### Community 21 - "core/terrain.py"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 22 - "ToolError"
Cohesion: 0.09
Nodes (20): _protocol_error(), ErrorCode, ToolError, get_raster_layer(), check_landscape(), execute_pyqgis(), _source(), classify_slope() (+12 more)

### Community 23 - "common.py"
Cohesion: 0.08
Nodes (24): detect_territory(), Territory, _overview_extent(), clean_number(), crs_info(), enum_name(), extent_wgs84(), file_format() (+16 more)

### Community 24 - "Métriques paysagères"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 25 - "classify.py"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 26 - "math"
Cohesion: 0.12
Nodes (7): fractal_dimension(), kurtosis(), percentile(), skewness(), check_surface_3d(), synthetic_dem(), utm_scale()

### Community 27 - "core/project_audit.py"
Cohesion: 0.14
Nodes (13): audit(), build_sections(), duplicate_name_findings(), _finding(), add(), project_findings(), severity_counts(), verdict() (+5 more)

### Community 28 - "Modèle de sécurité (à ne jamais contourner)"
Cohesion: 0.16
Nodes (16): Liste blanche ALGORITHMS de run_algorithm, Audit de chaque appel (get_audit_log), Journal d'édition JOURNAL (tampon, request_commit), execute_pyqgis (dernier recours, codecheck indicatif), Confirmation humaine DESTROY (register_detail_provider), Limites connues (JOURNAL en mémoire, un job à la fois…), Sorties jamais écrasées (mcp_outputs, suffixe _2), Niveaux READ / CREATE / MODIFY / DESTROY (+8 more)

### Community 29 - "TAXREF"
Cohesion: 0.11
Nodes (10): EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible(), test_describe_summary_vide() (+2 more)

### Community 30 - "core/atlas.py"
Cohesion: 0.17
Nodes (9): Box, layout_boxes(), page_size(), _build(), _from_template(), _label(), _north_arrow(), test_formats() (+1 more)

### Community 31 - "test_fields.py (2)"
Cohesion: 0.11
Nodes (18): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict() (+10 more)

### Community 32 - "Point d'entrée du plugin"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 33 - "Feuille de route"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 34 - "naming.py"
Cohesion: 0.11
Nodes (12): clean_name(), to_ascii(), all_palettes(), landscape_palette(), load_user_palettes(), register_palette(), validate_palette(), test_clean_name() (+4 more)

### Community 35 - "find_source_file"
Cohesion: 0.18
Nodes (11): _columns(), match_taxa(), name_key(), read_statuses(), Statuses, Taxon, listed(), _values() (+3 more)

### Community 36 - "classify.py (2)"
Cohesion: 0.10
Nodes (17): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), _as_multipolygon(), _closer_parts(), records() (+9 more)

### Community 37 - "Provenance"
Cohesion: 0.36
Nodes (3): Provenance, provenance_from_data(), test_provenance_roundtrip_and_kind_check()

### Community 38 - "to_float"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 39 - "core/project_audit.py (2)"
Cohesion: 0.32
Nodes (13): layer_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique(), test_projet_sain_sans_anomalie() (+5 more)

### Community 40 - "export.py"
Cohesion: 0.11
Nodes (7): _project_target(), save_project(), _save_project_details(), build_details(), make_confirmer(), confirm(), register_detail_provider()

### Community 41 - "Construction du ZIP"
Cohesion: 0.14
Nodes (11): assess(), bbox_covers(), cache_matches(), cache_meta(), _inpn(), should_replace_cache(), Zoning, zoning_state() (+3 more)

### Community 42 - "protocol.py"
Cohesion: 0.42
Nodes (6): decode_request(), _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 43 - "tasks.py"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 44 - "Historique des styles"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 45 - "ToolError"
Cohesion: 0.10
Nodes (26): begin_edit(), is_shapefile(), refresh_layer(), select_ids(), add_field(), calculate_field(), _change_geometries(), _check_count() (+18 more)

### Community 46 - "Installation développeur"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 47 - "dev_setup.py"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 48 - "privacy.py"
Cohesion: 0.29
Nodes (5): is_sensitive_field(), mask_sensitive(), sensitive_fields(), test_mask_sensitive_hides_only_sensitive_values(), test_sensitive_fields_in_filter_columns()

### Community 49 - "Journal d'audit"
Cohesion: 0.12
Nodes (10): getfeature_url(), status(), test_describe_multiple_sources_and_missing(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_prescan_sections_lists_sources_with_origin(), test_read_cache_meta_rejects_bad_files() (+2 more)

### Community 50 - "Guide d'installation Cynogis (poste entreprise)"
Cohesion: 0.12
Nodes (20): Cynogis (CLAUDE.md working rules), scripts/build_plugin.py --bump --repo, Variable CYNOGIS_REFERENTIALS_DIR, cynogis-server.exe, Guide d'installation Cynogis (poste entreprise), Branchement du client MCP (Claude Code, Claude Desktop, Codex), Partage réseau \\SERVEUR\Cynogis (plugins, serveur, referentials), Fichiers propres au poste (connection.json, tools_cache.json, audit/) (+12 more)

### Community 51 - "Requêtes WFS"
Cohesion: 0.10
Nodes (6): new_token(), remove_connection_file(), write_connection_file(), BridgeServer, classFactory(), CynogisPlugin

### Community 52 - "Catalogue des outils (105 + 4 internes)"
Cohesion: 0.29
Nodes (7): Outils internes (list_tools, get_job_status, cancel_job), Nomenclature fermée des paysages, regulatory_prescan (pré-diagnostic déterministe), surface_3d (complément, jamais référence réglementaire), Catalogue des outils (105 + 4 internes), Enchaînements typiques attendus de l'IA, Feature domains (~100 tools)

### Community 53 - "tasks.py (2)"
Cohesion: 0.14
Nodes (10): Fetch, service_label(), _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), _local_source(), Source (+2 more)

### Community 54 - "FakeExecutor"
Cohesion: 0.14
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 55 - "core/landscape.py"
Cohesion: 0.10
Nodes (16): apply_mapping(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match(), suggest_mapping() (+8 more)

### Community 56 - "schema.py"
Cohesion: 0.14
Nodes (10): _check(), object_schema(), Param, _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid() (+2 more)

### Community 57 - "Dispatcher"
Cohesion: 0.08
Nodes (12): Request, Response, Dispatcher, finish(), collecting(), Executor, render_notes(), PermissionPolicy (+4 more)

### Community 58 - "test_stats.py"
Cohesion: 0.22
Nodes (6): describe(), describe_groups(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum(), test_to_float()

### Community 59 - "prepare_expression"
Cohesion: 0.12
Nodes (8): expression_context(), geometry_from_wkt(), prepare_expression(), wkt_to_layer_crs(), _isopleths(), kernel_density_points(), _style(), export_table()

### Community 60 - "client.py"
Cohesion: 0.18
Nodes (5): main(), BridgeError, QgisBridgeClient, test_client_reponse_illisible(), scenario()

### Community 61 - "build_plugin.py"
Cohesion: 0.23
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 62 - "audit_project"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 63 - "core/sampling.py"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 64 - "classes_for"
Cohesion: 0.17
Nodes (8): classes_for(), validate_codes(), check_rules(), list_landscape_classes(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

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

### Community 71 - "get_vector_layer"
Cohesion: 0.20
Nodes (9): describe_summary(), get_vector_layer(), _commit_details(), _editing_layers(), get_pending_edits(), request_commit(), rollback_edits(), _targets() (+1 more)

### Community 72 - "Adding a tool (@tool decorator, Param, docstring)"
Cohesion: 0.17
Nodes (10): Adding a tool (@tool decorator, Param, docstring), Edit buffer + core/edits.py JOURNAL, core/jobs.py::note warnings from shared helpers, Permission levels READ / CREATE / MODIFY / DESTROY, Territory CRS: Reunion EPSG:2975, Mayotte EPSG:4471, 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD (+2 more)

### Community 73 - "core/impacts.py"
Cohesion: 0.19
Nodes (8): compare_variants(), direct_label(), ring_labels(), stake_weight(), test_anneaux(), test_comparaison_variantes(), test_poids_enjeu(), test_tableau()

### Community 74 - "Rapport des fonctionnalités"
Cohesion: 0.25
Nodes (5): Bridge protocol v1 (JSON-lines + token), ~/.cynogis/connection.json discovery file, Job response and polling (get_job_status / cancel_job), run_to_project / save_to_project output pipeline, ~/.cynogis/tools_cache.json catalogue cache

### Community 75 - "contrast_ratio"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 76 - "resolve_colors"
Cohesion: 0.25
Nodes (6): get_palette(), resolve_colors(), test_get_palette_etiree(), test_get_palette_inconnue(), test_resolve_colors_priorite_aux_couleurs(), test_resolve_colors_sans_rien()

### Community 77 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.29
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 78 - "EditJournal (2)"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 79 - "Pacer"
Cohesion: 0.21
Nodes (4): Pacer, clip_reference_landcover(), _clipped(), _overlay()

### Community 80 - "add_features"
Cohesion: 0.17
Nodes (5): check_batch_size(), field_type_name(), layer_field_types(), add_features(), _field_kind()

### Community 81 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 82 - "Any"
Cohesion: 0.20
Nodes (6): correlation_pairs(), describe_categorical(), weighted_stats(), test_categorical_entropy(), test_pairs_skip_missing(), test_weighted_median()

### Community 83 - "geometry_kind"
Cohesion: 0.08
Nodes (32): get_class(), compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of() (+24 more)

### Community 84 - "describe_full"
Cohesion: 0.24
Nodes (7): describe_full(), interpret_shape(), _t95(), test_describe_full_shape(), test_empty(), test_outlier_detected(), test_sensitive()

### Community 85 - "Phase 2 : Robustesse reglementaire (pre-diagnostic)"
Cohesion: 0.22
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 86 - "check_shapefile"
Cohesion: 0.15
Nodes (9): looks_like_mojibake(), add_to_group(), add_to_project(), _output_item(), check_shapefile(), load_layer(), _mojibake_hint(), set_layer_encoding() (+1 more)

### Community 88 - "open_table"
Cohesion: 0.22
Nodes (4): find_file(), open_table(), _sibling(), test_open_table_zip()

### Community 102 - "mentions_natura2000"
Cohesion: 0.31
Nodes (5): mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

### Community 103 - "check_geometries"
Cohesion: 0.29
Nodes (3): check_geometries(), _error_kind(), geometry_report()

### Community 105 - "BridgeResult"
Cohesion: 0.39
Nodes (6): BridgeResult, FakeClient, test_wait_job_annule_dans_qgis(), scenario(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 106 - "regulatory_prescan"
Cohesion: 0.29
Nodes (4): is_natura2000_layer(), for_territory(), regulatory_prescan(), test_par_territoire()

### Community 107 - "plugin.py"
Cohesion: 0.33
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 108 - "units.py"
Cohesion: 0.43
Nodes (4): convert_area(), convert_length(), test_conversions(), test_unknown_unit()

## Knowledge Gaps
- **34 isolated node(s):** `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Add-a-tool example (README)`, `Green Map Location Pin`, `Territoires Réunion EPSG:2975 / Mayotte EPSG:4471` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 731 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `ToolError` to `common.py`, `Shapefiles et encodage`, `Serveur MCP stdio`, `tool`, `add_to_memory`, `dispatcher.py`, `ErrorCode`, `save_to_project`, `run_to_project`, `test_jobs.py`, `_clipped`, `common.py`, `core/project_audit.py`, `core/atlas.py`, `Feuille de route`, `export.py`, `protocol.py`, `ToolError`, `Requêtes WFS`, `tasks.py (2)`, `FakeExecutor`, `schema.py`, `Dispatcher`, `prepare_expression`, `audit_project`, `get_vector_layer`, `Pacer`, `add_features`, `geometry_kind`, `check_shapefile`, `check_geometries`, `descriptive_stats`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 94 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `metadata.txt (Cynogis Reunion-Mayotte 0.1.0)`, `Add-a-tool example (README)` to the rest of the system?**
  _34 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07155399473222125 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `ToolError` to `common.py`, `Shapefiles et encodage`, `Serveur MCP stdio`, `tool`, `add_to_memory`, `dispatcher.py`, `ErrorCode`, `save_to_project`, `run_to_project`, `test_jobs.py`, `_clipped`, `common.py`, `core/project_audit.py`, `core/atlas.py`, `Feuille de route`, `export.py`, `protocol.py`, `ToolError`, `Requêtes WFS`, `tasks.py (2)`, `FakeExecutor`, `schema.py`, `Dispatcher`, `prepare_expression`, `audit_project`, `get_vector_layer`, `Pacer`, `add_features`, `geometry_kind`, `check_shapefile`, `check_geometries`, `descriptive_stats`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 142 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 142 INFERRED edges - model-reasoned connections that need verification._
- **Should `Shapefiles et encodage` be split into smaller, more focused modules?**
  _Cohesion score 0.05669199298655757 - nodes in this community are weakly interconnected._