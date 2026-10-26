# Graph Report - cynogis  (2026-10-26)

## Corpus Check
- 135 files · ~96,302 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2047 nodes · 6031 edges · 95 communities (81 shown, 14 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 455 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- tools/proximity.py
- Services web OGC
- tools/proximity.py (2)
- Métriques paysagères
- styling.py
- ToolResult
- Shapefiles et encodage
- Référentiels OCS (cœur)
- tools/proximity.py (3)
- Tests des jobs
- tool
- ToolError
- common.py
- Opérations sur couleurs
- Serveur MCP stdio
- ErrorCode
- Coefficients (cœur)
- to_float
- common.py (2)
- Impacts et enjeux
- Styles (cœur)
- Dérivés de terrain
- styling.py (2)
- report.py
- report.py (2)
- TAXREF
- Dérivés de terrain (2)
- EditJournal
- Palettes de couleurs
- Schéma des paramètres
- Tâches QgsTask
- Données de terrain
- Résolution des chevauchements
- Liste blanche d'algorithmes
- Classes de paysage
- Plans d'échantillonnage
- Shapefiles et encodage (2)
- Dispatcher
- Fraîcheur des zonages
- HABREF
- Typage des champs
- select_ids
- split_feature
- ToolRegistry
- Historique des styles
- Dispatcher (2)
- Gestionnaire de jobs
- editing.py
- Requêtes WFS
- Installation développeur
- Feuille de route
- Point d'entrée du plugin
- Exécuteur factice
- Tests du dispatcher
- Construction du ZIP
- Exécuteur de jobs
- Phase 1 : Fiabilite des calculs de surface
- Mise en page d'atlas
- Guide d'installation
- Classes de paysage (2)
- report.py (3)
- Rapport des fonctionnalités
- Serveur MCP stdio (2)
- Fichier de connexion
- Zonages WFS (outils)
- Typage des champs (2)
- Découpe de transects
- Security model (six guardrails)
- Protocole et découverte
- core/zoning.py
- QgsVectorLayer
- Protocole et découverte (2)
- Journal d'audit
- Cache des zonages
- Chemins du cache
- Étapes de job
- Contrôle de code PyQGIS
- Procedure d'ajout d'un outil (@tool)
- Règles réglementaires
- Point d'entrée du plugin (2)
- Options de style
- Serveur MCP stdio (3)
- ToolRegistry (2)
- styling.py (3)
- Classes de paysage (3)
- ErrorCode (2)
- Coefficients (cœur) (2)
- Spécification de coefficient
- Référentiels OCS (cœur) (2)
- Compatibilité Qt
- Paquet serveur

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 166 edges
2. `ErrorCode` - 155 edges
3. `tool()` - 141 edges
4. `ToolResult` - 102 edges
5. `get_vector_layer()` - 94 edges
6. `feature_request()` - 63 edges
7. `geometry_kind()` - 57 edges
8. `require_field()` - 51 edges
9. `to_json_value()` - 49 edges
10. `save_to_project()` - 46 edges

## Surprising Connections (you probably didn't know these)
- `3.2/3.3 Donnees sensibles et filtrage RGPD` --semantically_similar_to--> `Donnees d'especes sensibles et cadastrales nominatives jamais envoyees au modele`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `3.4 Audit des garde-fous` --semantically_similar_to--> `Securite : ne jamais contourner permissions, confirmation humaine, audit`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `test_describe_empty_and_single()` --calls--> `describe()`  [INFERRED]
  tests/unit/test_stats.py → plugin/cynogis/core/stats.py
- `1.2 Interdire les surfaces en EPSG:4326` --semantically_similar_to--> `SCR : La Reunion EPSG:2975, Mayotte EPSG:4471, jamais de surface en EPSG:4326`  [INFERRED] [semantically similar]
  docs/ROADMAP.md → CLAUDE.md

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Execution non bloquante dans QGIS** — claude_nonblocking_jobs, claude_job_response, claude_pacer, claude_fetch_http, claude_job_cancellation [EXTRACTED 1.00]
- **Cynogis safety guardrails** — claude_permission_levels, claude_algorithm_whitelist, raport_restricted_network, raport_audit_log, claude_edit_buffer [EXTRACTED 1.00]
- **Garde-fous Cynogis** — claude_permission_levels, claude_edit_buffer, claude_algorithm_whitelist, readme_audit_log, readme_execute_pyqgis [EXTRACTED 1.00]
- **Deploiement poste entreprise** — installation_network_share, installation_private_plugin_repo, installation_uv_tool_install, installation_shared_config, installation_referentials_dir, installation_mcp_clients [EXTRACTED 1.00]
- **Regles metier codifiees par la phase 2** — claude_natura2000_exclusion, claude_thresholds_config_rule, claude_deterministic_prediagnostic, docs_roadmap_phase2_reglementaire [INFERRED 0.85]
- **Garde-fous de controle humain (permissions, tampon, sorties)** — claude_security_rules, claude_permission_levels, claude_edit_buffer, claude_outputs_no_overwrite, claude_algorithm_whitelist [INFERRED 0.85]
- **Regles de fiabilite des surfaces** — claude_crs_rule, claude_surface_method_rule, claude_surface_helper_rule, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.85]
- **Long job execution flow** — raport_long_job_flow, raport_internal_tools [INFERRED 0.85]
- **Fiabilite des surfaces (regles, roadmap 1.1-1.3, helpers)** — claude_crs_rule, claude_surface_method_rule, claude_surface_helper_rule, docs_roadmap_1_1_reference_tests, docs_roadmap_1_2_forbid_4326, docs_roadmap_1_3_surface_method, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.95]

## Communities (95 total, 14 thin omitted)

### Community 0 - "tools/proximity.py"
Cohesion: 0.07
Nodes (39): ToolResult, get_class(), tool(), export_atlas_pdf(), feature_request(), geometry_kind(), get_vector_layer(), prepare_expression() (+31 more)

### Community 1 - "Services web OGC"
Cohesion: 0.07
Nodes (41): Fetch, capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list() (+33 more)

### Community 2 - "tools/proximity.py (2)"
Cohesion: 0.08
Nodes (24): unique_field_name(), describe(), to_float(), convert_area(), convert_length(), iter_geometries(), _collect(), count_observations() (+16 more)

### Community 3 - "Métriques paysagères"
Cohesion: 0.06
Nodes (33): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), fractal_dimension(), interpret_metrics(), largest_patch_index() (+25 more)

### Community 4 - "styling.py"
Cohesion: 0.06
Nodes (27): ErrorCode, ToolError, _from_template(), export_map_image(), save_project(), _write_csv(), write_document(), write_pdf() (+19 more)

### Community 5 - "ToolResult"
Cohesion: 0.09
Nodes (25): _overview_extent(), clean_number(), crs_info(), enum_name(), extent_wgs84(), file_format(), get_layer(), get_raster_layer() (+17 more)

### Community 6 - "Shapefiles et encodage"
Cohesion: 0.07
Nodes (23): truncate_field_names(), companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages() (+15 more)

### Community 7 - "Référentiels OCS (cœur)"
Cohesion: 0.07
Nodes (28): _covers(), find_source_file(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), referentials_directory(), _segments() (+20 more)

### Community 8 - "tools/proximity.py (3)"
Cohesion: 0.10
Nodes (20): compute_coefficients(), _geometries(), landscape_metrics(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of(), area_m2() (+12 more)

### Community 9 - "Tests des jobs"
Cohesion: 0.09
Nodes (26): app(), boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req() (+18 more)

### Community 10 - "tool"
Cohesion: 0.07
Nodes (19): _allowed(), describe_algorithm(), run_algorithm(), buffer(), dissolve(), extract(), fix_geometries(), _name() (+11 more)

### Community 11 - "ToolError"
Cohesion: 0.10
Nodes (18): add_to_memory(), make_field(), _save_isopleths(), write_table(), import_field_data(), create_study_area_buffers(), _check_layers(), _distances() (+10 more)

### Community 12 - "common.py"
Cohesion: 0.11
Nodes (3): render_notes(), _territory(), square()

### Community 13 - "Opérations sur couleurs"
Cohesion: 0.09
Nodes (21): contrast_ratio(), darken(), distinct_colors(), lighten(), mix(), parse_color(), relative_luminance(), to_hex() (+13 more)

### Community 14 - "Serveur MCP stdio"
Cohesion: 0.10
Nodes (12): main(), call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job() (+4 more)

### Community 15 - "ErrorCode"
Cohesion: 0.09
Nodes (10): clean_name(), unique_path(), _output_path(), _project_target(), _save_project_details(), output_dir(), save_style_file(), test_clean_name() (+2 more)

### Community 16 - "Coefficients (cœur)"
Cohesion: 0.10
Nodes (24): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), _ratio() (+16 more)

### Community 17 - "to_float"
Cohesion: 0.08
Nodes (18): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), describe_groups(), _r(), test_distance_matrix_cases_absentes() (+10 more)

### Community 18 - "common.py (2)"
Cohesion: 0.16
Nodes (5): Level, Cynogis Plugin Icon (icon.svg), Green Map Location Pin, is_optional(), list_slope_classes()

### Community 19 - "Impacts et enjeux"
Cohesion: 0.09
Nodes (21): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+13 more)

### Community 20 - "Styles (cœur)"
Cohesion: 0.10
Nodes (24): readable_text_color(), build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_readable_text_color() (+16 more)

### Community 21 - "Dérivés de terrain"
Cohesion: 0.09
Nodes (19): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+11 more)

### Community 22 - "styling.py (2)"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 23 - "report.py"
Cohesion: 0.16
Nodes (22): audit(), build_sections(), duplicate_name_findings(), _finding(), layer_findings(), add(), project_findings(), severity_counts() (+14 more)

### Community 24 - "report.py (2)"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 25 - "TAXREF"
Cohesion: 0.12
Nodes (15): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+7 more)

### Community 26 - "Dérivés de terrain (2)"
Cohesion: 0.10
Nodes (11): _isopleth_geometries(), _isopleths(), kernel_density_points(), _style(), run_in_memory(), _clean(), elevation_sample(), _metric_raster() (+3 more)

### Community 27 - "EditJournal"
Cohesion: 0.11
Nodes (10): check_batch_size(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations(), test_describe_summary_lisible() (+2 more)

### Community 28 - "Palettes de couleurs"
Cohesion: 0.10
Nodes (16): interpolate_ramp(), all_palettes(), get_palette(), landscape_palette(), load_user_palettes(), register_palette(), resolve_colors(), validate_palette() (+8 more)

### Community 29 - "Schéma des paramètres"
Cohesion: 0.14
Nodes (10): _check(), object_schema(), Param, _type_ok(), validate_params(), register_detail_provider(), test_defaults_applied(), test_integer_float_coerced() (+2 more)

### Community 30 - "Tâches QgsTask"
Cohesion: 0.13
Nodes (6): _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers()

### Community 31 - "Données de terrain"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 32 - "Résolution des chevauchements"
Cohesion: 0.14
Nodes (15): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus() (+7 more)

### Community 33 - "Liste blanche d'algorithmes"
Cohesion: 0.13
Nodes (11): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), list_algorithms(), test_liste_blanche() (+3 more)

### Community 34 - "Classes de paysage"
Cohesion: 0.11
Nodes (13): apply_mapping(), classes_for(), suggest_mapping(), validate_codes(), check_rules(), list_landscape_classes(), test_apply_mapping_insensible_aux_accents(), test_classes_for_territoire_inconnu() (+5 more)

### Community 35 - "Plans d'échantillonnage"
Cohesion: 0.12
Nodes (11): elongation(), allocate(), unit_id(), test_elongation(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id() (+3 more)

### Community 36 - "Shapefiles et encodage (2)"
Cohesion: 0.12
Nodes (7): Pacer, check_geometries(), _error_kind(), geometry_report(), clip_reference_landcover(), _clipped(), _overlay()

### Community 37 - "Dispatcher"
Cohesion: 0.17
Nodes (3): Dispatcher, finish(), collecting()

### Community 38 - "Fraîcheur des zonages"
Cohesion: 0.16
Nodes (10): age_days(), describe_sources(), freshness(), prescan_sections(), Provenance, provenance_from_data(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing() (+2 more)

### Community 39 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 40 - "Typage des champs"
Cohesion: 0.14
Nodes (14): coerce_record(), coerce_value(), _parse_date(), sanitize_field_name(), test_coerce_record_champ_inconnu_strict(), test_coerce_record_non_strict(), test_coerce_value(), test_coerce_value_date_invalide() (+6 more)

### Community 41 - "select_ids"
Cohesion: 0.17
Nodes (11): begin_edit(), refresh_layer(), select_ids(), add_features(), _check_count(), delete_features(), _delete_features_details(), merge_features() (+3 more)

### Community 42 - "split_feature"
Cohesion: 0.18
Nodes (9): _change_geometries(), _conform(), _geometries(), _measure(), move_features(), _reference_subset(), _snap(), snap_features() (+1 more)

### Community 43 - "ToolRegistry"
Cohesion: 0.18
Nodes (5): PermissionPolicy, spec_of(), decorator(), ToolRegistry, ToolSpec

### Community 44 - "Historique des styles"
Cohesion: 0.18
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 47 - "editing.py"
Cohesion: 0.18
Nodes (10): describe_summary(), _commit_details(), _delete_field_details(), _editing_layers(), get_pending_edits(), _merge_details(), request_commit(), rollback_edits() (+2 more)

### Community 48 - "Requêtes WFS"
Cohesion: 0.14
Nodes (8): getfeature_url(), status(), test_freshness(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_read_cache_meta_rejects_bad_files(), test_statut(), test_url_getfeature()

### Community 49 - "Installation développeur"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 50 - "Feuille de route"
Cohesion: 0.12
Nodes (14): 1.4 Surface projetee / surface 3D (MNT), Feuille de route Cynogis, Jalons, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre), Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats), Phase 6 : Donnees de reference locales (MNT, DEAL/PEIGEO, Borbonica), Phase 0 : Outillage du développement (prérequis), Phase 1 : Fiabilité des calculs de surface (priorité critique) (+6 more)

### Community 52 - "Exécuteur factice"
Cohesion: 0.15
Nodes (5): note(), FakeExecutor, job_invalide(), mesure_invalide(), test_notes_ajoutees_aux_warnings()

### Community 53 - "Tests du dispatcher"
Cohesion: 0.24
Nodes (13): crash(), double(), make(), metier(), _req(), supprimer(), test_decorator_checks(), test_destroy_with_confirmation() (+5 more)

### Community 54 - "Construction du ZIP"
Cohesion: 0.22
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 56 - "Phase 1 : Fiabilite des calculs de surface"
Cohesion: 0.15
Nodes (12): Fin de tache : graphify update et graphify-out dans le commit, 1.1 Tests de surfaces de reference (2975 / 4471), 1.2 Interdire les surfaces en EPSG:4326, 1.3 Methode plane ou ellipsoidale documentee, 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD (+4 more)

### Community 57 - "Mise en page d'atlas"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 58 - "Guide d'installation"
Cohesion: 0.14
Nodes (14): Guide d'installation poste entreprise, Clients MCP (Claude Code, Claude Desktop, Codex), Partage reseau \\SERVEUR\Cynogis, Depot QGIS prive (plugins.xml), CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...), Depannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN...), Installation du serveur via uv tool (cynogis-server.exe), metadata.txt (Cynogis Reunion-Mayotte 0.1.0) (+6 more)

### Community 59 - "Classes de paysage (2)"
Cohesion: 0.15
Nodes (8): LandscapeClass, merge_nomenclature(), register(), score_match(), test_merge_nomenclature_refuse(), test_merge_nomenclature_valide(), test_score_match_exact_et_mot_cle(), test_score_match_mots_entiers()

### Community 60 - "report.py (3)"
Cohesion: 0.16
Nodes (5): render_map(), audit_project(), _open_project(), _overview_map(), _project_facts()

### Community 61 - "Rapport des fonctionnalités"
Cohesion: 0.18
Nodes (13): Edition dans le tampon (begin_edit, JOURNAL, request_commit), Ecological impact study workflow (ERC), Ecology referentials (TAXREF, BDC Statuts, HABREF, zonings), Ecology, proximity, stakes and impacts tools, Editing tools (buffer then human commit), execute_pyqgis (DESTROY, last resort), Internal tools (list_tools, get_job_status, cancel_job), Known limits and pending validations (+5 more)

### Community 62 - "Serveur MCP stdio (2)"
Cohesion: 0.21
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 63 - "Fichier de connexion"
Cohesion: 0.29
Nodes (8): decode_request(), _protocol_error(), Request, _line(), test_decode_invalid(), test_decode_valid(), test_missing_token_is_unauthorized(), test_response_encode_has_audit_id()

### Community 64 - "Zonages WFS (outils)"
Cohesion: 0.19
Nodes (6): service_label(), _bbox_wgs84(), _cached_source(), _is_cancel(), Source, _sources()

### Community 65 - "Typage des champs (2)"
Cohesion: 0.17
Nodes (8): FieldType, resolve_type(), to_ascii(), is_shapefile(), add_field(), _field_limit(), test_resolve_type_alias(), test_resolve_type_inconnu()

### Community 66 - "Découpe de transects"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 67 - "Security model (six guardrails)"
Cohesion: 0.21
Nodes (7): Liste blanche ALGORITHMS (core/algorithms.py), Niveaux de permission READ / CREATE / MODIFY / DESTROY, Audit log (get_audit_log), Restricted network (webservices catalogue), Security model (six guardrails), Journal d'audit ~/.cynogis/audit, execute_pyqgis (dernier recours)

### Community 68 - "Protocole et découverte"
Cohesion: 0.17
Nodes (9): Decouverte via ~/.cynogis/connection.json, Cache du catalogue d'outils (~/.cynogis/tools_cache.json), Configuration partagee (web_services.json, palettes.json), Architecture and operation, Cynogis project report (RAPORT.md), ~/.cynogis user directory, Long job flow (AlgCall, Fetch, Pause, Pacer), Simple call flow (READ tool) (+1 more)

### Community 69 - "core/zoning.py"
Cohesion: 0.21
Nodes (6): assess(), bbox_covers(), should_replace_cache(), zoning_state(), test_bbox_rules(), test_pre_diagnostic()

### Community 70 - "QgsVectorLayer"
Cohesion: 0.18
Nodes (5): expression_context(), field_type_name(), geometry_from_wkt(), layer_field_types(), wkt_to_layer_crs()

### Community 71 - "Protocole et découverte (2)"
Cohesion: 0.18
Nodes (10): Protocole du pont v1 (JSON-lines, jeton, audit_id), Cynogis (pilotage de QGIS par IA via MCP), Commandes de developpement (pytest, ruff, ping_qgis, inspector, dev_setup), Telechargement HTTP par Fetch dans une QgsTask, Annulation des jobs sur suppression de couche ou fermeture de projet, Reponse job asynchrone (get_job_status / cancel_job), Jobs generateurs non bloquants (yield from, QgsTask), Pacer : cession de la main a QGIS toutes les 100 ms (+2 more)

### Community 72 - "Journal d'audit"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 73 - "Cache des zonages"
Cohesion: 0.20
Nodes (7): cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, test_cache_meta_roundtrip_and_matching(), test_par_territoire()

### Community 74 - "Chemins du cache"
Cohesion: 0.24
Nodes (5): cache_paths(), cache_root(), read_cache_meta(), _write_cache(), test_cache_root_env_override()

### Community 75 - "Étapes de job"
Cohesion: 0.27
Nodes (6): AlgCall, Pause, run_now(), test_run_now(), algo(), steps()

### Community 76 - "Contrôle de code PyQGIS"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 77 - "Procedure d'ajout d'un outil (@tool)"
Cohesion: 0.25
Nodes (6): Procedure d'ajout d'un outil (@tool, Param, docstring), Avertissements remontes par note() vers warnings, Debogage : recharger le plugin, bouton Serveur GeoMCP, erreur UNKNOWN, Contrat de retour d'outil (dict, ToolResult, ToolError), Code conventions (writing a tool), Shared helpers to reuse (tools/common.py, outputs.py)

### Community 78 - "Règles réglementaires"
Cohesion: 0.29
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 79 - "Point d'entrée du plugin (2)"
Cohesion: 0.29
Nodes (3): new_token(), remove_connection_file(), write_connection_file()

### Community 80 - "Options de style"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 81 - "Serveur MCP stdio (3)"
Cohesion: 0.29
Nodes (4): FakeClient, test_wait_job_annule_dans_qgis(), test_wait_job_delai_depasse(), test_wait_job_interroge_jusqu_au_resultat()

### Community 82 - "ToolRegistry (2)"
Cohesion: 0.33
Nodes (3): build_details(), make_confirmer(), confirm()

### Community 83 - "styling.py (3)"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 84 - "Classes de paysage (3)"
Cohesion: 0.50
Nodes (3): ndvi_deviation(), ndvi_range(), test_ndvi_controle()

## Knowledge Gaps
- **31 isolated node(s):** `cynogis-server`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree`, `Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre)`, `Phase 5 : Modules metier (EEE, ERC, FRAGSTATS, habitats)` (+26 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 710 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `styling.py` to `tools/proximity.py`, `Services web OGC`, `tools/proximity.py (2)`, `ToolResult`, `Shapefiles et encodage`, `Référentiels OCS (cœur)`, `tools/proximity.py (3)`, `tool`, `ToolError`, `common.py`, `ErrorCode`, `common.py (2)`, `Dérivés de terrain (2)`, `Schéma des paramètres`, `Tâches QgsTask`, `Plans d'échantillonnage`, `Shapefiles et encodage (2)`, `select_ids`, `split_feature`, `ToolRegistry`, `Dispatcher (2)`, `editing.py`, `Tests du dispatcher`, `report.py (3)`, `Serveur MCP stdio (2)`, `Fichier de connexion`, `Zonages WFS (outils)`, `Typage des champs (2)`, `ErrorCode (2)`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Are the 84 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 84 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `1.5 Gestion des doubles comptes`, `1.6 Validation des geometries en entree` to the rest of the system?**
  _31 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tools/proximity.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06604938271604938 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `styling.py` to `tools/proximity.py`, `Services web OGC`, `tools/proximity.py (2)`, `ToolResult`, `Shapefiles et encodage`, `Référentiels OCS (cœur)`, `tools/proximity.py (3)`, `tool`, `ToolError`, `common.py`, `ErrorCode`, `common.py (2)`, `Dérivés de terrain (2)`, `Schéma des paramètres`, `Tâches QgsTask`, `Plans d'échantillonnage`, `Shapefiles et encodage (2)`, `select_ids`, `split_feature`, `ToolRegistry`, `Dispatcher (2)`, `editing.py`, `Tests du dispatcher`, `report.py (3)`, `Serveur MCP stdio (2)`, `Fichier de connexion`, `Zonages WFS (outils)`, `Typage des champs (2)`, `ErrorCode (2)`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 118 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 118 INFERRED edges - model-reasoned connections that need verification._
- **Should `Services web OGC` be split into smaller, more focused modules?**
  _Cohesion score 0.06533646322378717 - nodes in this community are weakly interconnected._