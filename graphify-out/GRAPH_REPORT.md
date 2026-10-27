# Graph Report - cynogis  (2026-10-27)

## Corpus Check
- 133 files · ~98,448 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 2065 nodes · 6252 edges · 101 communities (89 shown, 12 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 514 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b7cbea45`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- common.py
- editing.py
- Services web OGC
- tool
- Shapefiles et encodage
- styling.py
- ToolResult
- Métriques paysagères
- Serveur MCP stdio
- render_map
- tools/proximity.py
- Coefficients (cœur)
- shapefiles.py
- HABREF
- core/impacts.py
- Tests des jobs
- Référentiels OCS (cœur)
- Dispatcher
- core/landscape.py
- Impacts et enjeux
- report.py (2)
- classify.py
- EditJournal
- Dérivés de terrain
- pytest
- Styles (cœur)
- TAXREF
- collections_abc
- Données de terrain
- Point d'entrée du plugin
- Résolution des chevauchements
- numpy
- Liste blanche d'algorithmes
- to_float
- numpy (2)
- Historique des styles
- prescan_sections
- fetch_wfs_layer
- tools/proximity.py (2) (3)
- ToolRegistry
- Installation développeur
- tools/terrain.py
- units.py
- tasks.py
- tasks.py (2)
- find_source_file
- Requêtes WFS
- Exécuteur factice
- core/project_audit.py
- describe
- Security model (six guardrails)
- Journal d'audit
- Fichier de connexion
- merge_features
- Zoning
- tools/project_audit.py
- Construction du ZIP
- Feuille de route
- Guide d'installation
- math
- Tests du dispatcher
- BridgeServer
- Découpe de transects
- Schéma des paramètres
- core/atlas.py
- to_json_value
- core/zoning.py
- core/sampling.py
- Chemins du cache
- Protocole et découverte
- pathlib
- Règles réglementaires
- tasks.py (5)
- assess
- Contrôle de code PyQGIS
- mix
- refresh_layer
- Rapport des fonctionnalités
- Phase 3 : Tracabilite et confidentialite
- Phase 1 : Fiabilite des calculs de surface
- Provenance
- require_field
- format_number
- Surfaces via area_m2(distance_area) + area_method
- run_algorithm
- naming.py
- to_float
- list_style_options
- export.py (2)
- test_job_lance_pendant_la_confirmation
- _summary
- mentions_natura2000
- plugin.py
- Paquet serveur
- app

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 198 edges
2. `ErrorCode` - 180 edges
3. `tool()` - 151 edges
4. `ToolResult` - 103 edges
5. `get_vector_layer()` - 97 edges
6. `feature_request()` - 64 edges
7. `geometry_kind()` - 58 edges
8. `require_field()` - 53 edges
9. `distance_area()` - 50 edges
10. `to_json_value()` - 49 edges

## Surprising Connections (you probably didn't know these)
- `1.3 Methode plane ou ellipsoidale documentee` --semantically_similar_to--> `Surfaces : toujours indiquer la méthode`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `note() : avertissements remontés par un helper` --references--> `note()`  [EXTRACTED]
  CLAUDE.md → plugin/cynogis/core/jobs.py
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `Surfaces via area_m2(distance_area) + area_method` --references--> `distance_area()`  [EXTRACTED]
  CLAUDE.md → plugin/cynogis/tools/common.py

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Exécution non bloquante des traitements** — claude_nonblocking_jobs, claude_job_response, claude_pacer, claude_fetch_http, claude_job_cancellation [EXTRACTED 1.00]
- **Chaîne client MCP -> serveur -> pont -> plugin** — claude_generic_mcp_server, claude_tcp_bridge, claude_bridge_protocol_v1, claude_connection_discovery, claude_tools_cache [EXTRACTED 1.00]
- **Cynogis safety guardrails** — claude_permission_levels, claude_algorithm_whitelist, raport_restricted_network, raport_audit_log, claude_edit_buffer [EXTRACTED 1.00]
- **Garde-fous Cynogis** — claude_permission_levels, claude_edit_buffer, claude_algorithm_whitelist, readme_audit_log, readme_execute_pyqgis [EXTRACTED 1.00]
- **Deploiement poste entreprise** — installation_network_share, installation_private_plugin_repo, installation_uv_tool_install, installation_shared_config, installation_referentials_dir, installation_mcp_clients [EXTRACTED 1.00]
- **Regles metier codifiees par la phase 2** — claude_natura2000_exclusion, claude_thresholds_config_rule, claude_deterministic_prediagnostic, docs_roadmap_phase2_reglementaire [INFERRED 0.85]
- **Règles de calcul des surfaces** — claude_crs_rule, claude_surface_method_rule, claude_surface_helper_rule, claude_dissolve_by_class_rule, claude_surface_3d_rule [INFERRED 0.85]
- **Long job execution flow** — raport_long_job_flow, raport_internal_tools [INFERRED 0.85]
- **Fiabilite des surfaces (regles, roadmap 1.1-1.3, helpers)** — claude_crs_rule, claude_surface_method_rule, claude_surface_helper_rule, docs_roadmap_1_1_reference_tests, docs_roadmap_1_2_forbid_4326, docs_roadmap_1_3_surface_method, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.95]

## Communities (101 total, 12 thin omitted)

### Community 0 - "common.py"
Cohesion: 0.12
Nodes (4): Level, Param, polygon_parts(), register_detail_provider()

### Community 1 - "editing.py"
Cohesion: 0.06
Nodes (37): ErrorCode, ToolError, unique_field_name(), _from_template(), _polygon_layer(), begin_edit(), crs_from_text(), expression_context() (+29 more)

### Community 2 - "Services web OGC"
Cohesion: 0.06
Nodes (46): Fetch, is_natura2000_layer(), capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs() (+38 more)

### Community 3 - "tool"
Cohesion: 0.14
Nodes (11): tool(), get_field_values(), buffer(), dissolve(), extract(), fix_geometries(), _name(), overlay() (+3 more)

### Community 4 - "Shapefiles et encodage"
Cohesion: 0.10
Nodes (20): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), truncate_field_names(), test_coerce_record_champ_inconnu_strict() (+12 more)

### Community 5 - "styling.py"
Cohesion: 0.19
Nodes (12): _apply(), apply_categorized_style(), apply_graduated_style(), apply_landscape_style(), apply_single_style(), _categorized(), _distinct_values(), _kind() (+4 more)

### Community 6 - "ToolResult"
Cohesion: 0.06
Nodes (34): ToolResult, unique_path(), detect_territory(), export_atlas_pdf(), _overview_extent(), clean_number(), crs_info(), enum_name() (+26 more)

### Community 7 - "Métriques paysagères"
Cohesion: 0.09
Nodes (22): division_index(), edge_density(), effective_mesh_size(), largest_patch_index(), patch_density(), shape_index(), simpson_index(), summarize_patches() (+14 more)

### Community 8 - "Serveur MCP stdio"
Cohesion: 0.07
Nodes (22): QgsLogHandler, setup_logging(), teardown_logging(), main(), call_tool(), _fetch_specs(), list_tools(), _progress_token() (+14 more)

### Community 9 - "render_map"
Cohesion: 0.20
Nodes (3): render_map(), write_document(), write_pdf()

### Community 10 - "tools/proximity.py"
Cohesion: 0.06
Nodes (48): Pacer, compute_coefficients(), add_to_memory(), area_m2(), area_method(), distance_area(), feature_request(), geometry_kind() (+40 more)

### Community 11 - "Coefficients (cœur)"
Cohesion: 0.08
Nodes (27): CoefficientSpec, compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key() (+19 more)

### Community 12 - "shapefiles.py"
Cohesion: 0.09
Nodes (20): companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), check_shapefile() (+12 more)

### Community 13 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 14 - "core/impacts.py"
Cohesion: 0.13
Nodes (10): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), _zones(), test_anneaux(), test_comparaison_variantes() (+2 more)

### Community 15 - "Tests des jobs"
Cohesion: 0.17
Nodes (19): boucle(), erreur_avant(), lecture(), make(), _req(), sans_etape(), telechargement(), test_annulation() (+11 more)

### Community 16 - "Référentiels OCS (cœur)"
Cohesion: 0.10
Nodes (22): check_rules(), _covers(), map_cirad(), map_feature(), map_ocsge(), Rule, _segments(), Source (+14 more)

### Community 17 - "Dispatcher"
Cohesion: 0.14
Nodes (6): Request, Response, Dispatcher, finish(), collecting(), render_notes()

### Community 18 - "core/landscape.py"
Cohesion: 0.08
Nodes (23): apply_mapping(), classes_for(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register() (+15 more)

### Community 19 - "Impacts et enjeux"
Cohesion: 0.18
Nodes (12): Criterion, level_for(), level_number(), Override, parse_criteria(), parse_overrides(), parse_thresholds(), score() (+4 more)

### Community 20 - "report.py (2)"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 21 - "classify.py"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 22 - "EditJournal"
Cohesion: 0.08
Nodes (17): check_batch_size(), describe_summary(), EditEntry, EditJournal, _commit_details(), _editing_layers(), get_pending_edits(), rollback_edits() (+9 more)

### Community 23 - "Dérivés de terrain"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 24 - "pytest"
Cohesion: 0.12
Nodes (14): contrast_ratio(), parse_color(), readable_text_color(), relative_luminance(), to_rgba_string(), with_alpha(), test_contraste_extremes(), test_distinct_colors_sans_doublon() (+6 more)

### Community 25 - "Styles (cœur)"
Cohesion: 0.11
Nodes (22): build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees() (+14 more)

### Community 26 - "TAXREF"
Cohesion: 0.12
Nodes (15): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+7 more)

### Community 27 - "collections_abc"
Cohesion: 0.08
Nodes (19): distinct_colors(), interpolate_ramp(), to_hex(), validate_colors(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes() (+11 more)

### Community 28 - "Données de terrain"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 30 - "Résolution des chevauchements"
Cohesion: 0.10
Nodes (17): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), _as_multipolygon(), _closer_parts(), records() (+9 more)

### Community 31 - "numpy"
Cohesion: 0.12
Nodes (10): _isopleth_geometries(), _isopleths(), _style(), _clean(), elevation_sample(), _pixel_labels(), _read_window(), _sector_index() (+2 more)

### Community 32 - "Liste blanche d'algorithmes"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 33 - "to_float"
Cohesion: 0.14
Nodes (12): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), test_distance_matrix_cases_absentes(), test_nearest_egalite_reproductible(), test_nearest_k_et_distance_max() (+4 more)

### Community 34 - "numpy (2)"
Cohesion: 0.15
Nodes (7): Commandes de développement (pytest, ruff, ping, check_surfaces), check_dissolved(), check_site(), check_surface_3d(), square(), synthetic_dem(), utm_scale()

### Community 35 - "Historique des styles"
Cohesion: 0.15
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 36 - "prescan_sections"
Cohesion: 0.25
Nodes (6): age_days(), describe_sources(), freshness(), prescan_sections(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing()

### Community 37 - "fetch_wfs_layer"
Cohesion: 0.16
Nodes (8): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), _local_source(), Source, _sources(), _wfs_features()

### Community 38 - "tools/proximity.py (2) (3)"
Cohesion: 0.11
Nodes (14): convert_length(), _geometries(), landscape_metrics(), _load_zones(), _reference_areas(), _zones_of(), dissolved_areas(), length_m() (+6 more)

### Community 39 - "ToolRegistry"
Cohesion: 0.13
Nodes (8): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec, build_details(), make_confirmer(), confirm()

### Community 40 - "Installation développeur"
Cohesion: 0.23
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 41 - "tools/terrain.py"
Cohesion: 0.13
Nodes (11): get_raster_layer(), compute_ndvi(), is_optional(), _run(), run_to_project(), classify_slope(), derive_terrain(), _flow_accumulation() (+3 more)

### Community 42 - "units.py"
Cohesion: 0.47
Nodes (3): convert_area(), test_conversions(), test_unknown_unit()

### Community 43 - "tasks.py"
Cohesion: 0.12
Nodes (7): AlgCall, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers()

### Community 44 - "tasks.py (2)"
Cohesion: 0.12
Nodes (3): Executor, Job, JobManager

### Community 45 - "find_source_file"
Cohesion: 0.14
Nodes (7): find_source_file(), referentials_directory(), _clipped(), _open(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent()

### Community 46 - "Requêtes WFS"
Cohesion: 0.15
Nodes (7): getfeature_url(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_prescan_sections_lists_sources_with_origin(), test_read_cache_meta_rejects_bad_files(), test_url_getfeature()

### Community 48 - "Exécuteur factice"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 49 - "core/project_audit.py"
Cohesion: 0.15
Nodes (23): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+15 more)

### Community 50 - "describe"
Cohesion: 0.18
Nodes (7): describe(), describe_groups(), _r(), descriptive_stats(), test_describe_basic(), test_describe_empty_and_single(), test_groups_sorted_by_sum()

### Community 51 - "Security model (six guardrails)"
Cohesion: 0.14
Nodes (16): Liste blanche ALGORITHMS (run_algorithm), Édition dans le tampon (begin_edit, JOURNAL, request_commit), Fetch : téléchargement HTTP dans une QgsTask, Annulation du job (suppression couche / fermeture projet), Réponse « job » (get_job_status / cancel_job, BUSY), Jobs non bloquants (yield from, QgsTask), Pacer (rend la main à QGIS toutes les 100 ms), Niveaux de permission READ/CREATE/MODIFY/DESTROY (+8 more)

### Community 52 - "Journal d'audit"
Cohesion: 0.27
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 53 - "Fichier de connexion"
Cohesion: 0.18
Nodes (8): decode_request(), _protocol_error(), save_palette(), _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 54 - "merge_features"
Cohesion: 0.15
Nodes (13): _change_geometries(), _check_count(), _conform(), _geometries(), _measure(), merge_features(), move_features(), _record() (+5 more)

### Community 55 - "Zoning"
Cohesion: 0.18
Nodes (8): cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, regulatory_prescan(), test_cache_meta_roundtrip_and_matching(), test_par_territoire()

### Community 56 - "tools/project_audit.py"
Cohesion: 0.11
Nodes (12): file_format(), layer_kind(), source_path(), _error_kind(), geometry_report(), _layer_facts(), _open_project(), _overview_map() (+4 more)

### Community 57 - "Construction du ZIP"
Cohesion: 0.23
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 58 - "Feuille de route"
Cohesion: 0.14
Nodes (12): Feuille de route Cynogis, Jalons, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique), Phase 2 : Robustesse réglementaire (pré-diagnostic), Phase 3 : Traçabilité et confidentialité (+4 more)

### Community 59 - "Guide d'installation"
Cohesion: 0.14
Nodes (14): Guide d'installation poste entreprise, Clients MCP (Claude Code, Claude Desktop, Codex), Partage reseau \\SERVEUR\Cynogis, Depot QGIS prive (plugins.xml), CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...), Depannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN...), Installation du serveur via uv tool (cynogis-server.exe), metadata.txt (Cynogis Reunion-Mayotte 0.1.0) (+6 more)

### Community 60 - "math"
Cohesion: 0.11
Nodes (12): circularity(), dominance(), elongation(), fractal_dimension(), interpret_metrics(), mean_patch_size(), shannon_evenness(), shannon_index() (+4 more)

### Community 61 - "Tests du dispatcher"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 63 - "Découpe de transects"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 64 - "Schéma des paramètres"
Cohesion: 0.18
Nodes (9): _check(), object_schema(), _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid(), test_items_enum() (+1 more)

### Community 65 - "core/atlas.py"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 66 - "to_json_value"
Cohesion: 0.15
Nodes (6): to_json_value(), _geometry_repr(), get_features(), check_landscape(), execute_pyqgis(), get_layer_style()

### Community 67 - "core/zoning.py"
Cohesion: 0.24
Nodes (5): bbox_covers(), should_replace_cache(), status(), test_bbox_rules(), test_statut()

### Community 68 - "core/sampling.py"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 69 - "Chemins du cache"
Cohesion: 0.24
Nodes (5): cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_root_env_override()

### Community 70 - "Protocole et découverte"
Cohesion: 0.12
Nodes (14): Protocole du pont v1 (JSON-lines + jeton), Découverte via connection.json (CYNOGIS_CONNECTION_FILE), Cynogis (pilotage QGIS par IA via MCP), Serveur MCP générique (relais list_tools / call_tool), Débogage : recharger le plugin, bouton Serveur GeoMCP, Pont TCP local (plugin QGIS <-> serveur MCP), Cache du catalogue d'outils (tools_cache.json), Configuration partagee (web_services.json, palettes.json) (+6 more)

### Community 71 - "pathlib"
Cohesion: 0.25
Nodes (3): new_token(), remove_connection_file(), write_connection_file()

### Community 72 - "Règles réglementaires"
Cohesion: 0.27
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 73 - "tasks.py (5)"
Cohesion: 0.32
Nodes (6): Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 74 - "assess"
Cohesion: 0.40
Nodes (3): assess(), zoning_state(), test_pre_diagnostic()

### Community 75 - "Contrôle de code PyQGIS"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 76 - "mix"
Cohesion: 0.25
Nodes (5): darken(), lighten(), mix(), test_lighten_darken(), test_mix_milieu()

### Community 77 - "refresh_layer"
Cohesion: 0.22
Nodes (5): refresh_layer(), _qcolor(), _refresh(), set_labels(), undo_style()

### Community 78 - "Rapport des fonctionnalités"
Cohesion: 0.25
Nodes (9): Ecological impact study workflow (ERC), Ecology referentials (TAXREF, BDC Statuts, HABREF, zonings), Ecology, proximity, stakes and impacts tools, Internal tools (list_tools, get_job_status, cancel_job), Landscape diagnosis workflow, Closed landscape nomenclature, Coefficients, landscape, terrain tools, Tool catalog (101 + 4 internal) (+1 more)

### Community 79 - "Phase 3 : Tracabilite et confidentialite"
Cohesion: 0.22
Nodes (8): Fin de tâche : graphify update, Conventions (Ruff, QgsTask, une branche par fonctionnalité), 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, 3.4 Audit des garde-fous, Phase 0 : Outillage du developpement, Phase 3 : Tracabilite et confidentialite

### Community 80 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.25
Nodes (7): 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Phase 1 : Fiabilite des calculs de surface, Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica)

### Community 81 - "Provenance"
Cohesion: 0.36
Nodes (3): Provenance, provenance_from_data(), test_provenance_roundtrip_and_kind_check()

### Community 82 - "require_field"
Cohesion: 0.29
Nodes (3): is_agricultural(), _overlay(), test_is_agricultural()

### Community 83 - "format_number"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 84 - "Surfaces via area_m2(distance_area) + area_method"
Cohesion: 0.29
Nodes (5): Procédure d'ajout d'un outil (@tool), note() : avertissements remontés par un helper, Contrat de retour (dict / ToolResult / ToolError), Code conventions (writing a tool), Shared helpers to reuse (tools/common.py, outputs.py)

### Community 85 - "run_algorithm"
Cohesion: 0.29
Nodes (3): _allowed(), describe_algorithm(), run_algorithm()

### Community 86 - "naming.py"
Cohesion: 0.24
Nodes (5): clean_name(), to_ascii(), test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

### Community 87 - "to_float"
Cohesion: 0.33
Nodes (3): to_float(), _sort_key(), test_to_float()

### Community 88 - "list_style_options"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 90 - "test_job_lance_pendant_la_confirmation"
Cohesion: 0.33
Nodes (4): calcul(), effacer(), test_job_lance_pendant_la_confirmation(), confirm()

### Community 91 - "_summary"
Cohesion: 0.29
Nodes (4): list_layers(), _summary(), _tree(), _visible()

### Community 92 - "mentions_natura2000"
Cohesion: 0.31
Nodes (5): mentions_natura2000(), test_detect(), test_is_natura2000_layer(), test_mentions_natura2000(), test_natura2000_absent_du_code()

## Knowledge Gaps
- **29 isolated node(s):** `cynogis-server`, `Audit log (get_audit_log)`, `Restricted network (webservices catalogue)`, `Shared helpers to reuse (tools/common.py, outputs.py)`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 709 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `editing.py` to `common.py`, `Services web OGC`, `tool`, `styling.py`, `ToolResult`, `render_map`, `tools/proximity.py`, `shapefiles.py`, `Tests des jobs`, `Dispatcher`, `numpy`, `fetch_wfs_layer`, `tools/proximity.py (2) (3)`, `ToolRegistry`, `tools/terrain.py`, `tasks.py`, `tasks.py (2)`, `find_source_file`, `Exécuteur factice`, `describe`, `Fichier de connexion`, `merge_features`, `tools/project_audit.py`, `Tests du dispatcher`, `BridgeServer`, `Schéma des paramètres`, `to_json_value`, `refresh_layer`, `run_algorithm`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Are the 92 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 92 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `Audit log (get_audit_log)`, `Restricted network (webservices catalogue)` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12089201877934272 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `editing.py` to `common.py`, `Services web OGC`, `tool`, `styling.py`, `ToolResult`, `render_map`, `tools/proximity.py`, `shapefiles.py`, `Tests des jobs`, `Dispatcher`, `numpy`, `fetch_wfs_layer`, `tools/proximity.py (2) (3)`, `ToolRegistry`, `tools/terrain.py`, `tasks.py`, `tasks.py (2)`, `find_source_file`, `Exécuteur factice`, `describe`, `Fichier de connexion`, `merge_features`, `tools/project_audit.py`, `Tests du dispatcher`, `BridgeServer`, `Schéma des paramètres`, `to_json_value`, `refresh_layer`, `run_algorithm`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 140 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 140 INFERRED edges - model-reasoned connections that need verification._
- **Should `editing.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06354642313546423 - nodes in this community are weakly interconnected._