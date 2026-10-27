# Installation de Cynogis sur un poste de l'entreprise

Guide pour équiper un PC Windows d'un chargé d'études. Compter **15 minutes** par poste.

Cynogis comporte trois éléments, tous nécessaires :

```
Claude Code / Claude Desktop / Codex   ← l'assistant IA (client MCP)
            │ lance automatiquement
            ▼
  serveur Cynogis (cynogis-server.exe)  ← traducteur MCP ↔ QGIS
            │ connexion locale 127.0.0.1 + jeton
            ▼
  plugin Cynogis dans QGIS              ← exécute les traitements
```

Dans ce guide, `\\SERVEUR\Cynogis` désigne le partage réseau de l'entreprise : remplacez-le par le
vrai chemin.

---

## 0. Préparer le partage réseau (administrateur, une fois par version)

Sur le poste de développement, dans le dossier du projet :

```bash
.venv/Scripts/python scripts/build_plugin.py --bump --repo "\\SERVEUR\Cynogis\plugins"
uv build --wheel --out-dir "\\SERVEUR\Cynogis\serveur"
```

Contenu attendu du partage :

```
\\SERVEUR\Cynogis\
├── plugins\          plugins.xml + cynogis-<version>.zip   (dépôt QGIS privé)
├── serveur\          cynogis_server-<version>-py3-none-any.whl
├── referentials\     TAXREF, BDC Statuts, HABREF, OCS GE, CIRAD (.gpkg / .shp / .geojson)
├── web_services.json (facultatif : services WMS/WFS propres à l'entreprise)
└── palettes.json     (facultatif : palettes de couleurs de l'entreprise)
```

---

## 1. Prérequis

| Élément | Version | Remarque |
|---|---|---|
| Windows | 10 ou 11 | aucun droit administrateur nécessaire |
| QGIS | 3.38 à 4.x | version LTR conseillée |
| Compte Claude | Pro, Max ou Team | ou un compte ChatGPT pour Codex |
| Accès réseau | partage `\\SERVEUR\Cynogis` + Internet | Internet : installation de `uv`, flux WMS/WFS, l'IA elle-même |

---

## 2. Installer le plugin QGIS

1. Ouvrir QGIS → **Extensions → Installer/Gérer les extensions → Paramètres**.
2. Cocher **« Afficher les extensions expérimentales »**.
3. **Ajouter…** un dépôt :
   - Nom : `Cynogis entreprise`
   - URL : `file:///SERVEUR/Cynogis/plugins/plugins.xml`
4. Onglet **Toutes** → rechercher **Cynogis Réunion-Mayotte** → **Installer**.

Le bouton **« Serveur Cynogis »** apparaît dans la barre d'outils.

> Les mises à jour sont ensuite proposées automatiquement par QGIS (onglet *Évolutives*).
>
> Sans dépôt : *Installer depuis un ZIP* → `\\SERVEUR\Cynogis\plugins\cynogis-<version>.zip`
> (mais pas de mise à jour automatique).

---

## 3. Installer le serveur Cynogis

### 3.1 Installer `uv` (gestionnaire Python, sans droits admin)

Dans **PowerShell** :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Fermer puis rouvrir PowerShell, et vérifier :

```powershell
uv --version
```

### 3.2 Installer le serveur

```powershell
uv tool install (Get-ChildItem \\SERVEUR\Cynogis\serveur\*.whl | Sort-Object LastWriteTime | Select-Object -Last 1).FullName
```

`uv` télécharge lui-même Python et la bibliothèque `mcp` : rien d'autre à installer. Le serveur est
placé dans `%USERPROFILE%\.local\bin\cynogis-server.exe`.

> **Mise à jour du serveur** : relancer la même commande en ajoutant `--force` après `install`.

---

## 4. Copier la configuration partagée

```powershell
New-Item -ItemType Directory -Force "$HOME\.cynogis" | Out-Null
Copy-Item \\SERVEUR\Cynogis\web_services.json, \\SERVEUR\Cynogis\palettes.json "$HOME\.cynogis\" -ErrorAction SilentlyContinue
```

**Référentiels** : plutôt que de les copier sur chaque poste, pointer vers le partage (tout le monde
utilise ainsi les mêmes versions) :

```powershell
setx CYNOGIS_REFERENTIALS_DIR "\\SERVEUR\Cynogis\referentials"
```

Redémarrer QGIS ensuite pour qu'il voie la variable.

> ⚠️ Ne **jamais** copier `connection.json`, `tools_cache.json` ni le dossier `audit\` d'un autre
> poste : ils sont propres à chaque machine (`connection.json` contient un jeton régénéré à chaque
> démarrage du plugin).

---

## 5. Brancher l'assistant IA

Choisir **un** des clients ci-dessous.

### Option A — Claude Code (terminal)

```powershell
claude mcp add --scope user cynogis -- "$HOME\.local\bin\cynogis-server.exe"
```

### Option B — Claude Desktop

Ouvrir `%APPDATA%\Claude\claude_desktop_config.json` (Claude Desktop → Paramètres → Développeur →
Modifier la configuration) et ajouter, en remplaçant `PRENOM.NOM` par le nom du compte Windows :

```json
{
  "mcpServers": {
    "cynogis": {
      "command": "C:\\Users\\PRENOM.NOM\\.local\\bin\\cynogis-server.exe"
    }
  }
}
```

Quitter complètement Claude Desktop (icône de la barre des tâches → Quitter) puis le relancer.

### Option C — Codex

Ajouter dans `%USERPROFILE%\.codex\config.toml` :

```toml
[mcp_servers.cynogis]
command = 'C:\Users\PRENOM.NOM\.local\bin\cynogis-server.exe'
```

---

## 6. Vérifier que tout fonctionne

1. Ouvrir QGIS et un projet (de préférence **enregistré** : les résultats iront dans
   `<dossier du projet>\mcp_outputs\`).
2. Cliquer sur **« Serveur Cynogis »** (le bouton reste enfoncé).
3. Dans l'assistant IA, écrire :
   > Lance ping sur Cynogis, puis donne-moi les infos du projet et la liste des couches.
4. L'IA doit répondre avec les versions de QGIS et du plugin, le SCR et les couches.

---

## 7. Utilisation au quotidien

- **Avant chaque session** : ouvrir QGIS → ouvrir le projet → cliquer sur **« Serveur Cynogis »**.
- Les résultats apparaissent dans le groupe **« Cynogis »** du projet et dans `mcp_outputs\`,
  sans jamais écraser un fichier existant.
- Les actions sensibles (suppression, enregistrement sur disque, écrasement du projet, code PyQGIS)
  ouvrent une **fenêtre de confirmation dans QGIS** : lire le résumé avant d'accepter.
- Le journal **Cynogis** (Vue → Panneaux → Journal des messages, onglet « Cynogis ») trace chaque
  action.

---

## 8. Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `QGIS_UNAVAILABLE` | pont non démarré | cliquer sur « Serveur Cynogis » dans QGIS |
| L'IA ne voit aucun outil Cynogis | client mal configuré | vérifier le chemin de `cynogis-server.exe` (étape 5), redémarrer le client |
| `uv` ou `cynogis-server` introuvable | PowerShell non rouvert | fermer / rouvrir PowerShell ; vérifier `%USERPROFILE%\.local\bin` |
| Le plugin n'apparaît pas dans QGIS | extensions expérimentales masquées | cocher « Afficher les extensions expérimentales » (étape 2) |
| `BUSY` | un traitement long est en cours | attendre la fin, ou l'annuler depuis l'assistant |
| Référentiel « absent » | variable non vue par QGIS | vérifier `CYNOGIS_REFERENTIALS_DIR`, redémarrer QGIS |
| Accents illisibles dans une couche | encodage du shapefile | demander à l'IA : « corrige l'encodage de la couche X » |
| `[UNKNOWN] Erreur inconnue` | bug du plugin | noter la demande faite et prévenir l'administrateur Cynogis |
| Pare-feu / proxy bloque `uv` | réseau d'entreprise | demander l'accès à `astral.sh`, `pypi.org` et `files.pythonhosted.org` |

---

## 9. Désinstallation

```powershell
uv tool uninstall cynogis-server
claude mcp remove cynogis          # si Claude Code
Remove-Item -Recurse "$HOME\.cynogis"
```

Puis, dans QGIS : *Extensions → Installer/Gérer les extensions → Cynogis → Désinstaller*.
