# Graph Report - cynogis  (2026-10-26)

## Corpus Check
- 135 files · ~95,883 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2031 nodes · 5629 edges · 105 communities (84 shown, 21 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 338 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Outils d'édition
- Proximité et styles
- Confirmation et utilitaires
- Services web OGC
- Export et erreurs métier
- Métriques paysagères
- Shapefiles et encodage
- Serveur MCP stdio
- Proximité PyQGIS
- Dérivés de terrain
- Territoires et champs
- Coefficients (cœur)
- Registre d'outils
- Impacts et enjeux
- Classes de paysage
- Méthode de surface
- Rapports HTML/Markdown
- Classification de valeurs
- Tests des jobs
- Journal d'édition
- Styles (cœur)
- Géotraitements
- Typage des champs
- Référentiels OCS (cœur)
- Coefficients (outils)
- Itération des géométries
- Règles de surface SCR
- Tâches QgsTask
- Palettes de couleurs
- Opérations sur couleurs
- TAXREF
- Algorithmes et sorties
- Données de terrain
- Résolution des chevauchements
- Zonages WFS (outils)
- Densité de noyau
- Liste blanche d'algorithmes
- Historique des styles
- Schéma des paramètres
- HABREF
- Fichier de connexion
- Parties surfaciques
- Feuille de route
- Pont TCP
- Gestionnaire de jobs
- Emprises et formats
- Installation développeur
- Protocole et découverte
- Audit de projet (cœur)
- Cache des zonages
- Point d'entrée du plugin
- Mise en page d'atlas
- Tests d'audit de projet
- Infos couches et SCR
- Construction du ZIP
- Guide d'installation
- Sources des référentiels
- Tests du dispatcher
- Dispatcher
- Découpe de transects
- Ajout d'outils et permissions
- Fraîcheur des zonages
- Registre des outils
- Journal d'audit
- Étapes de job
- Exécuteur de jobs
- Pauses et contrôle géométrique
- Plans d'échantillonnage
- Chemins du cache
- Requêtes WFS
- Règles de paysage
- Contrôle de code PyQGIS
- Contraste des couleurs
- Catalogue de palettes
- Rapport des fonctionnalités
- Exécuteur factice
- Tests de surfaces
- Règles réglementaires
- Sécurité et traçabilité
- Journal QGIS
- Croisement des zonages
- Provenance des données
- Liste des couches
- Carte d'ensemble
- Contraintes d'architecture
- Options de style
- Libellés de légende
- Conversion d'unités
- Bilan de zonage
- Règles de cache
- Tests de nommage
- Spécification de coefficient
- Correspondance OCS GE
- Statut de zone
- Représentation géométrique
- Archive HABREF
- Ouverture de référentiel
- Tests de territoire
- Fixtures de test
- Compatibilité Qt
- Paquet serveur

## God Nodes (most connected - your core abstractions)
1. `ToolError` - 115 edges
2. `ErrorCode` - 97 edges
3. `get_vector_layer()` - 94 edges
4. `tool()` - 82 edges
5. `feature_request()` - 63 edges
6. `geometry_kind()` - 57 edges
7. `ToolResult` - 53 edges
8. `require_field()` - 51 edges
9. `to_json_value()` - 49 edges
10. `distance_area()` - 45 edges

## Surprising Connections (you probably didn't know these)
- `area_method()` --implements--> `1.3 Methode plane ou ellipsoidale documentee`  [INFERRED]
  plugin/cynogis/tools/common.py → docs/ROADMAP.md
- `test_history_pop_vide()` --uses--> `StyleHistory`  [INFERRED]
  tests/unit/test_style.py → plugin/cynogis/core/stylehistory.py
- `test_response_encode_job_id()` --uses--> `Response`  [INFERRED]
  tests/unit/test_jobs.py → plugin/cynogis/bridge/protocol.py
- `area_m2()` --implements--> `1.2 Interdire les surfaces en EPSG:4326`  [INFERRED]
  plugin/cynogis/tools/common.py → docs/ROADMAP.md
- `Surfaces via area_m2(distance_area(crs)) + area_method` --references--> `area_method()`  [EXTRACTED]
  CLAUDE.md → plugin/cynogis/tools/common.py

## Import Cycles
- 3-file cycle: `plugin/cynogis/__init__.py -> plugin/cynogis/plugin.py -> plugin/cynogis/tools/system.py -> plugin/cynogis/__init__.py`

## Hyperedges (group relationships)
- **Cynogis safety guardrails** — claude_permission_levels, claude_algorithm_whitelist, raport_restricted_network, raport_audit_log, claude_edit_buffer [EXTRACTED 1.00]
- **Garde-fous Cynogis** — claude_permission_levels, claude_edit_buffer, claude_algorithm_whitelist, readme_audit_log, readme_execute_pyqgis [EXTRACTED 1.00]
- **Deploiement poste entreprise** — installation_network_share, installation_private_plugin_repo, installation_uv_tool_install, installation_shared_config, installation_referentials_dir, installation_mcp_clients [EXTRACTED 1.00]
- **Long job execution flow** — raport_long_job_flow, raport_internal_tools [INFERRED 0.85]
- **Fiabilite des surfaces (regles, roadmap 1.1-1.3, helpers)** — claude_crs_rule, claude_surface_method_rule, claude_surface_helper_rule, docs_roadmap_1_1_reference_tests, docs_roadmap_1_2_forbid_4326, docs_roadmap_1_3_surface_method, plugin_cynogis_tools_common_area_m2, plugin_cynogis_tools_common_area_method [INFERRED 0.95]
- **Regles metier codifiees par la phase 2** — claude_natura2000_exclusion, claude_thresholds_config_rule, claude_deterministic_prediagnostic, docs_roadmap_phase2_reglementaire [INFERRED 0.85]
- **Garde-fous securite (permissions, confirmation, audit, sorties, donnees sensibles)** — claude_security_rules, claude_permission_levels, claude_outputs_no_overwrite, claude_sensitive_data_rule, docs_roadmap_3_4_guardrail_audit [INFERRED 0.85]

## Communities (105 total, 21 thin omitted)

### Community 0 - "Outils d'édition"
Cohesion: 0.07
Nodes (37): begin_edit(), field_type_name(), geometry_from_wkt(), is_shapefile(), layer_field_types(), refresh_layer(), select_ids(), wkt_to_layer_crs() (+29 more)

### Community 1 - "Proximité et styles"
Cohesion: 0.05
Nodes (36): distance_matrix(), nearest(), _order_key(), ordered_ring(), setback_status(), describe(), describe_groups(), _r() (+28 more)

### Community 2 - "Confirmation et utilitaires"
Cohesion: 0.07
Nodes (11): PermissionPolicy, Level, spec_of(), decorator(), ToolSpec, Cynogis Plugin Icon (icon.svg), Green Map Location Pin, build_details() (+3 more)

### Community 3 - "Services web OGC"
Cohesion: 0.07
Nodes (35): capabilities_url(), catalog(), check_url(), _child_text(), _children_text(), choose_crs(), _crs_list(), _local() (+27 more)

### Community 4 - "Export et erreurs métier"
Cohesion: 0.07
Nodes (23): ErrorCode, ToolError, clean_name(), unique_path(), export_atlas_pdf(), _from_template(), export_map_image(), export_table() (+15 more)

### Community 5 - "Métriques paysagères"
Cohesion: 0.06
Nodes (34): circularity(), division_index(), dominance(), edge_density(), effective_mesh_size(), elongation(), fractal_dimension(), interpret_metrics() (+26 more)

### Community 6 - "Shapefiles et encodage"
Cohesion: 0.08
Nodes (24): companion_paths(), export_plan(), looks_like_mojibake(), sidecar_messages(), sidecar_report(), SidecarReport, size_messages(), crs_from_text() (+16 more)

### Community 7 - "Serveur MCP stdio"
Cohesion: 0.08
Nodes (19): main(), call_tool(), _fetch_specs(), list_tools(), _progress_token(), run(), _to_tool(), _wait_job() (+11 more)

### Community 8 - "Proximité PyQGIS"
Cohesion: 0.09
Nodes (18): add_to_memory(), _collect(), count_observations(), count_points_in_polygon(), distance_layer(), _distance_m(), distance_matrix(), distance_to_sensitive_features() (+10 more)

### Community 9 - "Dérivés de terrain"
Cohesion: 0.07
Nodes (23): altitude_band(), aspect_sector(), degrees_to_percent(), distribution(), parse_bands(), percent_to_degrees(), reclass_table(), slope_class() (+15 more)

### Community 10 - "Territoires et champs"
Cohesion: 0.10
Nodes (14): ToolResult, truncate_field_names(), unique_field_name(), detect_territory(), Territory, import_field_data(), _read(), habitat_typology_join() (+6 more)

### Community 11 - "Coefficients (cœur)"
Cohesion: 0.10
Nodes (25): compute_all(), coverage_ratio(), density(), floor_area_ratio(), footprint_ratio(), interpret(), _key(), list_categories() (+17 more)

### Community 12 - "Registre d'outils"
Cohesion: 0.07
Nodes (18): tool(), list_algorithms(), select_features(), execute_pyqgis(), save_palette(), undo_style(), ping(), classify_slope() (+10 more)

### Community 13 - "Impacts et enjeux"
Cohesion: 0.09
Nodes (21): build_table(), compare_variants(), direct_label(), ring_labels(), stake_weight(), Criterion, level_for(), level_number() (+13 more)

### Community 14 - "Classes de paysage"
Cohesion: 0.09
Nodes (17): apply_mapping(), get_class(), LandscapeClass, merge_nomenclature(), ndvi_deviation(), ndvi_range(), register(), score_match() (+9 more)

### Community 15 - "Méthode de surface"
Cohesion: 0.10
Nodes (12): area_method(), geometry_kind(), check_landscape(), classify_landscape(), compute_ndvi(), extract_ravines(), list_landscape_classes(), suggest_landscape_mapping() (+4 more)

### Community 16 - "Rapports HTML/Markdown"
Cohesion: 0.11
Nodes (20): build_html(), build_markdown(), _escape_cell(), _image_src(), normalize_sections(), normalize_table(), table_to_rows(), sections() (+12 more)

### Community 17 - "Classification de valeurs"
Cohesion: 0.13
Nodes (20): clean_values(), compute_breaks(), _dedupe(), equal_interval(), natural_breaks(), pretty_breaks(), quantile_breaks(), standard_deviation_breaks() (+12 more)

### Community 18 - "Tests des jobs"
Cohesion: 0.13
Nodes (23): boucle(), calcul(), effacer(), erreur_avant(), lecture(), make(), _req(), sans_etape() (+15 more)

### Community 19 - "Journal d'édition"
Cohesion: 0.10
Nodes (12): check_batch_size(), describe_summary(), EditEntry, EditJournal, journal(), test_check_batch_size(), test_clear_cible(), test_count_for_operations() (+4 more)

### Community 20 - "Styles (cœur)"
Cohesion: 0.11
Nodes (22): build_categories(), _lookup(), normalize_geometry(), _number(), validate_labels(), validate_symbol(), test_build_categories_couleurs_automatiques(), test_build_categories_couleurs_imposees() (+14 more)

### Community 21 - "Géotraitements"
Cohesion: 0.14
Nodes (12): get_vector_layer(), make_field(), buffer(), create_study_area_buffers(), dissolve(), extract(), fix_geometries(), _name() (+4 more)

### Community 22 - "Typage des champs"
Cohesion: 0.10
Nodes (19): coerce_record(), coerce_value(), FieldType, _parse_date(), resolve_type(), sanitize_field_name(), to_ascii(), test_coerce_record_champ_inconnu_strict() (+11 more)

### Community 23 - "Référentiels OCS (cœur)"
Cohesion: 0.13
Nodes (18): _covers(), is_agricultural(), map_cirad(), map_feature(), map_ocsge(), _segments(), test_cirad_974_2020_ombre_et_code_inconnu(), test_cirad_974_2020_par_code() (+10 more)

### Community 24 - "Coefficients (outils)"
Cohesion: 0.13
Nodes (12): compute_coefficients(), _geometries(), landscape_metrics(), list_coefficients(), _load_zones(), _polygon_layer(), _reference_areas(), _zones_of() (+4 more)

### Community 25 - "Itération des géométries"
Cohesion: 0.14
Nodes (12): feature_request(), group_key(), iter_geometries(), get_field_values(), _check_layers(), _distances(), erc_variant_compare(), impact_quantification() (+4 more)

### Community 26 - "Règles de surface SCR"
Cohesion: 0.15
Nodes (11): 1.2 Interdire les surfaces en EPSG:4326, area_m2(), distance_area(), length_m(), perimeter_m(), descriptive_stats(), habitat_area_stats(), measure() (+3 more)

### Community 27 - "Tâches QgsTask"
Cohesion: 0.12
Nodes (7): Fetch, _FetchTask, _Handle, _input_layers(), _needs_main_thread(), ProcessingExecutor, _take_layers()

### Community 28 - "Palettes de couleurs"
Cohesion: 0.11
Nodes (12): distinct_colors(), validate_colors(), with_alpha(), landscape_palette(), register_palette(), resolve_colors(), validate_palette(), test_distinct_colors_sans_doublon() (+4 more)

### Community 29 - "Opérations sur couleurs"
Cohesion: 0.12
Nodes (15): darken(), interpolate_ramp(), lighten(), mix(), parse_color(), to_hex(), to_rgba_string(), test_interpolate_ramp_extremites_conservees() (+7 more)

### Community 30 - "TAXREF"
Cohesion: 0.14
Nodes (13): _columns(), find_file(), match_taxa(), name_key(), open_table(), read_statuses(), Statuses, Taxon (+5 more)

### Community 31 - "Algorithmes et sorties"
Cohesion: 0.15
Nodes (10): _allowed(), describe_algorithm(), run_algorithm(), add_to_group(), add_to_project(), is_optional(), _output_item(), _run() (+2 more)

### Community 32 - "Données de terrain"
Cohesion: 0.13
Nodes (12): column_key(), parse_count(), parse_date(), parse_number(), read_csv(), standardize(), suggest_columns(), test_colonnes_kobo() (+4 more)

### Community 33 - "Résolution des chevauchements"
Cohesion: 0.14
Nodes (15): _comparable(), half_plane_corners(), needs_priority_field(), rank_records(), summarize_resolution(), records(), test_egalite_stable(), test_half_plane_centres_confondus() (+7 more)

### Community 34 - "Zonages WFS (outils)"
Cohesion: 0.14
Nodes (9): _bbox_wgs84(), _cached_source(), fetch_wfs_layer(), _is_cancel(), _local_source(), Source, _sources(), _wfs_features() (+1 more)

### Community 35 - "Densité de noyau"
Cohesion: 0.13
Nodes (7): expression_context(), prepare_expression(), _isopleth_geometries(), _isopleths(), kernel_density_points(), _save_isopleths(), _style()

### Community 36 - "Liste blanche d'algorithmes"
Cohesion: 0.15
Nodes (10): AlgorithmSpec, get_spec(), is_allowed(), _matches(), search_algorithms(), normalize(), test_liste_blanche(), test_recherche_multi_termes() (+2 more)

### Community 37 - "Historique des styles"
Cohesion: 0.16
Nodes (6): StyleHistory, StyleSnapshot, test_history_derniere_couche(), test_history_ignore_xml_vide(), test_history_profondeur_limitee(), test_history_push_pop()

### Community 38 - "Schéma des paramètres"
Cohesion: 0.19
Nodes (10): _check(), object_schema(), Param, _type_ok(), validate_params(), test_defaults_applied(), test_integer_float_coerced(), test_invalid() (+2 more)

### Community 39 - "HABREF"
Cohesion: 0.17
Nodes (10): correspond(), Habitat, _index(), load_correspondences(), load_typology(), match_habitats(), test_correspondances(), test_load_typology_filtre_la_typologie() (+2 more)

### Community 40 - "Fichier de connexion"
Cohesion: 0.17
Nodes (10): new_token(), remove_connection_file(), write_connection_file(), decode_request(), _protocol_error(), _line(), test_decode_invalid(), test_decode_valid() (+2 more)

### Community 41 - "Parties surfaciques"
Cohesion: 0.15
Nodes (6): polygon_parts(), _territory(), clip_reference_landcover(), _clipped(), list_reference_sources(), _overlay()

### Community 42 - "Feuille de route"
Cohesion: 0.11
Nodes (18): 1.1 Tests de surfaces de reference (2975 / 4471), 1.4 Surface projetee / surface 3D (MNT), 1.5 Gestion des doubles comptes, 1.6 Validation des geometries en entree, Feuille de route Cynogis, Jalons, Phase 1 : Fiabilite des calculs de surface, Phase 4 : Specificites de Mayotte (Chido, Fani Maore, cadastre) (+10 more)

### Community 45 - "Emprises et formats"
Cohesion: 0.18
Nodes (9): _overview_extent(), extent_wgs84(), file_format(), layer_kind(), rect_to_list(), source_path(), territory_info(), _layer_facts() (+1 more)

### Community 46 - "Installation développeur"
Cohesion: 0.24
Nodes (11): check_python(), ensure_venv(), has_native_stubs(), install_stubs(), _is_link(), link_plugin(), load_env(), main() (+3 more)

### Community 47 - "Protocole et découverte"
Cohesion: 0.16
Nodes (14): Protocole du pont v1 (JSON-lines), Decouverte via ~/.cynogis/connection.json, Cynogis (CLAUDE.md), Workflow Graphify (graphify update, GRAPH_REPORT.md), Reponse job (get_job_status / cancel_job), Phase 0 : Outillage du developpement, Configuration partagee (web_services.json, palettes.json), Architecture and operation (+6 more)

### Community 48 - "Audit de projet (cœur)"
Cohesion: 0.21
Nodes (10): audit(), build_sections(), duplicate_name_findings(), _finding(), add(), project_findings(), severity_counts(), verdict() (+2 more)

### Community 49 - "Cache des zonages"
Cohesion: 0.18
Nodes (7): cache_matches(), cache_meta(), for_territory(), _inpn(), Zoning, test_cache_meta_roundtrip_and_matching(), test_par_territoire()

### Community 51 - "Mise en page d'atlas"
Cohesion: 0.19
Nodes (8): Box, layout_boxes(), page_size(), _build(), _label(), _north_arrow(), test_formats(), test_zones_dans_la_page_sans_chevauchement()

### Community 52 - "Tests d'audit de projet"
Cohesion: 0.32
Nodes (13): layer_findings(), severities(), test_audit_trie_par_gravite_et_detecte_doublons(), test_carte_d_ensemble_inseree_apres_le_projet(), test_couche_invalide_critique_et_seule(), test_couche_memoire_modifiee_et_raster_sans_nodata(), test_projet_non_enregistre_et_geographique(), test_projet_sain_sans_anomalie() (+5 more)

### Community 53 - "Infos couches et SCR"
Cohesion: 0.25
Nodes (9): clean_number(), crs_info(), enum_name(), get_layer(), get_raster_layer(), get_layer_info(), get_raster_info(), _info() (+1 more)

### Community 54 - "Construction du ZIP"
Cohesion: 0.23
Nodes (6): build_zip(), bump_version(), main(), read_metadata(), write_repository(), write_version()

### Community 55 - "Guide d'installation"
Cohesion: 0.14
Nodes (14): Guide d'installation poste entreprise, Clients MCP (Claude Code, Claude Desktop, Codex), Partage reseau \\SERVEUR\Cynogis, Depot QGIS prive (plugins.xml), CYNOGIS_REFERENTIALS_DIR (TAXREF, HABREF, OCS GE...), Depannage (QGIS_UNAVAILABLE, BUSY, UNKNOWN...), Installation du serveur via uv tool (cynogis-server.exe), metadata.txt (Cynogis Reunion-Mayotte 0.1.0) (+6 more)

### Community 56 - "Sources des référentiels"
Cohesion: 0.15
Nodes (8): find_source_file(), referentials_directory(), Source, sources_for(), test_fichier_cirad_sous_son_nom_d_origine(), test_find_source_file(), test_find_source_file_dossier_absent(), test_sources_for_territoire()

### Community 57 - "Tests du dispatcher"
Cohesion: 0.30
Nodes (12): crash(), double(), make(), metier(), _req(), supprimer(), test_destroy_with_confirmation(), test_errors() (+4 more)

### Community 58 - "Dispatcher"
Cohesion: 0.27
Nodes (3): Request, Dispatcher, finish()

### Community 59 - "Découpe de transects"
Cohesion: 0.21
Nodes (4): _cut(), _Sampler, _segment(), _systematic()

### Community 60 - "Ajout d'outils et permissions"
Cohesion: 0.20
Nodes (10): Procedure d'ajout d'un outil (@tool), Edition dans le tampon + journal JOURNAL, Niveaux de permission READ / CREATE / MODIFY / DESTROY, Audit log (get_audit_log), Code conventions (writing a tool), execute_pyqgis (DESTROY, last resort), Known limits and pending validations, Restricted network (webservices catalogue) (+2 more)

### Community 61 - "Fraîcheur des zonages"
Cohesion: 0.23
Nodes (7): age_days(), describe_sources(), freshness(), prescan_sections(), test_age_never_negative_and_tolerates_garbage(), test_describe_multiple_sources_and_missing(), test_prescan_sections_lists_sources_with_origin()

### Community 63 - "Journal d'audit"
Cohesion: 0.36
Nodes (5): AuditLog, _truncate(), test_destroy_params_never_truncated(), test_long_params_truncated(), test_writes_jsonl_and_filters()

### Community 64 - "Étapes de job"
Cohesion: 0.24
Nodes (7): AlgCall, Pause, run_now(), test_pacer_ne_cede_qu_apres_l_intervalle(), test_run_now(), algo(), steps()

### Community 66 - "Pauses et contrôle géométrique"
Cohesion: 0.20
Nodes (4): Pacer, check_geometries(), _error_kind(), geometry_report()

### Community 67 - "Plans d'échantillonnage"
Cohesion: 0.25
Nodes (6): allocate(), unit_id(), test_allocation_egale_et_strate_vide(), test_allocation_impossible(), test_allocation_proportionnelle(), test_unit_id()

### Community 68 - "Chemins du cache"
Cohesion: 0.20
Nodes (6): cache_paths(), cache_root(), read_cache_meta(), test_cache_root_env_override(), test_freshness(), test_read_cache_meta_rejects_bad_files()

### Community 69 - "Requêtes WFS"
Cohesion: 0.22
Nodes (4): getfeature_url(), test_getfeature_url_first_page_has_no_startindex(), test_getfeature_url_pagination_and_cql(), test_url_getfeature()

### Community 70 - "Règles de paysage"
Cohesion: 0.20
Nodes (7): classes_for(), validate_codes(), check_rules(), test_classes_for_territoire_inconnu(), test_classes_specifiques_territoire(), test_validate_codes(), test_tables_coherentes_avec_la_nomenclature()

### Community 71 - "Contrôle de code PyQGIS"
Cohesion: 0.31
Nodes (4): risky_names(), _details(), test_code_anodin_ou_invalide(), test_repere_modules_et_appels_sensibles()

### Community 72 - "Contraste des couleurs"
Cohesion: 0.22
Nodes (5): contrast_ratio(), readable_text_color(), relative_luminance(), test_contraste_extremes(), test_readable_text_color()

### Community 73 - "Catalogue de palettes"
Cohesion: 0.22
Nodes (6): all_palettes(), get_palette(), load_user_palettes(), test_get_palette_etiree(), test_get_palette_inconnue(), test_load_user_palettes_ignore_les_erreurs()

### Community 74 - "Rapport des fonctionnalités"
Cohesion: 0.25
Nodes (9): Ecological impact study workflow (ERC), Ecology referentials (TAXREF, BDC Statuts, HABREF, zonings), Ecology, proximity, stakes and impacts tools, Editing tools (buffer then human commit), Landscape diagnosis workflow, Closed landscape nomenclature, Coefficients, landscape, terrain tools, Tool catalog (101 + 4 internal) (+1 more)

### Community 76 - "Tests de surfaces"
Cohesion: 0.32
Nodes (4): Commande check_surfaces.py (surfaces de reference), check_site(), square(), utm_scale()

### Community 77 - "Règles réglementaires"
Cohesion: 0.25
Nodes (5): 2.1 Fichier de configuration des seuils, 2.3 Exclure Natura 2000, 2.4/2.5 Zonages Reunion et Mayotte, 2.6 Pre-diagnostic 100 % deterministe, Phase 2 : Robustesse reglementaire (pre-diagnostic)

### Community 78 - "Sécurité et traçabilité"
Cohesion: 0.29
Nodes (5): 1.3 Methode plane ou ellipsoidale documentee, 3.1 Encart de tracabilite automatique, 3.2/3.3 Donnees sensibles et filtrage RGPD, 3.4 Audit des garde-fous, Phase 3 : Tracabilite et confidentialite

### Community 79 - "Journal QGIS"
Cohesion: 0.32
Nodes (3): QgsLogHandler, setup_logging(), teardown_logging()

### Community 81 - "Provenance des données"
Cohesion: 0.36
Nodes (3): Provenance, provenance_from_data(), test_provenance_roundtrip_and_kind_check()

### Community 82 - "Liste des couches"
Cohesion: 0.29
Nodes (4): list_layers(), _summary(), _tree(), _visible()

### Community 83 - "Carte d'ensemble"
Cohesion: 0.25
Nodes (3): _overview_map(), _project_facts(), _raster_facts()

### Community 84 - "Contraintes d'architecture"
Cohesion: 0.29
Nodes (3): Liste blanche ALGORITHMS (run_algorithm), Journal d'audit ~/.cynogis/audit, execute_pyqgis (dernier recours)

### Community 85 - "Options de style"
Cohesion: 0.29
Nodes (4): describe_palettes(), describe_options(), list_style_options(), test_describe_options_contenu()

### Community 86 - "Libellés de légende"
Cohesion: 0.33
Nodes (4): format_number(), range_labels(), test_format_number_francais(), test_range_labels()

### Community 87 - "Conversion d'unités"
Cohesion: 0.50
Nodes (4): convert_area(), convert_length(), test_conversions(), test_unknown_unit()

### Community 88 - "Bilan de zonage"
Cohesion: 0.40
Nodes (3): assess(), zoning_state(), test_pre_diagnostic()

### Community 89 - "Règles de cache"
Cohesion: 0.50
Nodes (3): bbox_covers(), should_replace_cache(), test_bbox_rules()

### Community 90 - "Tests de nommage"
Cohesion: 0.50
Nodes (3): test_clean_name(), test_normalize(), test_unique_path_never_overwrites()

## Knowledge Gaps
- **26 isolated node(s):** `cynogis-server`, `Green Map Location Pin`, `Configuration partagee (web_services.json, palettes.json)`, `Long job flow (AlgCall, Fetch, Pause, Pacer)`, `Audit log (get_audit_log)` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 696 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ToolError` connect `Export et erreurs métier` to `Proximité et styles`, `Confirmation et utilitaires`, `Services web OGC`, `Shapefiles et encodage`, `Dérivés de terrain`, `Territoires et champs`, `Registre d'outils`, `Tests des jobs`, `Itération des géométries`, `Tâches QgsTask`, `Algorithmes et sorties`, `Schéma des paramètres`, `Fichier de connexion`, `Pont TCP`, `Gestionnaire de jobs`, `Infos couches et SCR`, `Tests du dispatcher`, `Dispatcher`, `Pauses et contrôle géométrique`, `Exécuteur factice`, `Carte d'ensemble`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 47 inferred relationships involving `ToolError` (e.g. with `Response` and `BridgeServer`) actually correct?**
  _`ToolError` has 47 INFERRED edges - model-reasoned connections that need verification._
- **What connects `cynogis-server`, `Green Map Location Pin`, `Configuration partagee (web_services.json, palettes.json)` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Outils d'édition` be split into smaller, more focused modules?**
  _Cohesion score 0.07404664938911515 - nodes in this community are weakly interconnected._
- **Why does `ErrorCode` connect `Export et erreurs métier` to `Proximité et styles`, `Confirmation et utilitaires`, `Services web OGC`, `Shapefiles et encodage`, `Dérivés de terrain`, `Territoires et champs`, `Registre d'outils`, `Tests des jobs`, `Itération des géométries`, `Tâches QgsTask`, `Algorithmes et sorties`, `Schéma des paramètres`, `Fichier de connexion`, `Pont TCP`, `Gestionnaire de jobs`, `Infos couches et SCR`, `Tests du dispatcher`, `Dispatcher`, `Pauses et contrôle géométrique`, `Exécuteur factice`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 70 inferred relationships involving `ErrorCode` (e.g. with `decode_request()` and `_protocol_error()`) actually correct?**
  _`ErrorCode` has 70 INFERRED edges - model-reasoned connections that need verification._
- **Should `Proximité et styles` be split into smaller, more focused modules?**
  _Cohesion score 0.052429667519181586 - nodes in this community are weakly interconnected._