# install.ps1 - Installation / mise a jour de Cynogis sur un poste Windows
# Usage : powershell -ExecutionPolicy Bypass -File .\install.ps1
#           [-Referentials "E:\referentials"] [-QgisProfile default]
#           [-Agent claude|codex|both|none]
param(
    [string]$Referentials = "",
    [string]$QgisProfile = "default",
    [ValidateSet("", "claude", "codex", "both", "none")]
    [string]$Agent = ""
)
$ErrorActionPreference = "Stop"
$Repo = $PSScriptRoot
$ServerName = "cynogis"

# Lance une commande externe sans que PowerShell 5.1 ne plante sur stderr.
function Invoke-Native([scriptblock]$Cmd) {
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { & $Cmd 2>&1 | Out-Null; return ($LASTEXITCODE -eq 0) }
    catch { return $false }
    finally { $ErrorActionPreference = $old }
}

# ---------------------------------------------------------------- 0. Choix de l'agent
if (-not $Agent) {
    Write-Host "Quel assistant IA brancher sur Cynogis ?"
    Write-Host "  1) Claude Code"
    Write-Host "  2) Codex (OpenAI)"
    Write-Host "  3) Les deux"
    Write-Host "  4) Aucun (configuration manuelle)"
    switch (Read-Host "Choix [1-4]") {
        "1" { $Agent = "claude" }
        "2" { $Agent = "codex" }
        "3" { $Agent = "both" }
        default { $Agent = "none" }
    }
}

# ---------------------------------------------------------------- 1. uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[1/5] Installation de uv..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$HOME\.local\bin;$env:Path"
} else { Write-Host "[1/5] uv deja present" }

# ---------------------------------------------------------------- 2. Serveur MCP
Write-Host "[2/5] Installation du serveur Cynogis..."
uv tool install --force "$Repo"
if ($LASTEXITCODE -ne 0) { throw "Echec de l'installation du serveur" }

$binDir = (uv tool dir --bin).Trim()
$exe = Join-Path $binDir "cynogis-server.exe"
if (-not (Test-Path $exe)) { throw "Executable introuvable : $exe" }
Write-Host "      -> $exe"

# ---------------------------------------------------------------- 3. Plugin QGIS
Write-Host "[3/5] Installation du plugin QGIS..."
$profiles = @("$env:APPDATA\QGIS\QGIS3\profiles\$QgisProfile",
              "$env:APPDATA\QGIS\QGIS4\profiles\$QgisProfile") | Where-Object { Test-Path $_ }
if (-not $profiles) { throw "Profil QGIS introuvable : lancez QGIS une fois, fermez-le, puis relancez ce script." }
foreach ($p in $profiles) {
    $dest = Join-Path $p "python\plugins\cynogis"
    New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
    if (Test-Path $dest) {
        $item = Get-Item $dest -Force
        # Jonction (poste de dev) : supprimer le lien seul. Remove-Item -Recurse
        # sous PowerShell 5.1 suivrait la jonction et viderait le depot source.
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { $item.Delete() }
        else { Remove-Item -Recurse -Force $dest }
    }
    Copy-Item -Recurse "$Repo\plugin\cynogis" $dest
    Get-ChildItem $dest -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
    Write-Host "      -> $dest"
}

# ---------------------------------------------------------------- 4. Referentiels
$refDir = "$HOME\.cynogis\referentials"
New-Item -ItemType Directory -Force $refDir | Out-Null
if (-not $Referentials -and (Test-Path "$Repo\referentials")) { $Referentials = "$Repo\referentials" }
if ($Referentials) {
    $Referentials = $Referentials.TrimEnd('\')   # "E:\ref\" casserait les guillemets de robocopy
    if (-not (Test-Path $Referentials)) { throw "Dossier de referentiels introuvable : $Referentials" }
    Write-Host "[4/5] Copie des referentiels depuis $Referentials..."
    robocopy $Referentials $refDir /E /NFL /NDL /NJH /NJS | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Echec de la copie des referentiels" }
} else { Write-Host "[4/5] Aucun dossier de referentiels fourni (a copier dans $refDir)" }
Get-ChildItem $refDir -File | ForEach-Object { Write-Host ("      {0}  ({1:N0} Mo)" -f $_.Name, ($_.Length / 1MB)) }

# ---------------------------------------------------------------- 5. Branchement IA
Write-Host "[5/5] Configuration de l'assistant IA ($Agent)..."

function Register-ClaudeCode {
    if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
        Write-Warning "Claude Code introuvable (commande 'claude'). Installez-le puis relancez : .\install.ps1 -Agent claude"
        return
    }
    Invoke-Native { claude mcp remove --scope user $ServerName } | Out-Null   # evite le doublon
    if (Invoke-Native { claude mcp add --scope user $ServerName -- $exe }) {
        Write-Host "      Claude Code configure (verifier : claude mcp list)"
    } else {
        Write-Warning "Echec. Commande manuelle : claude mcp add --scope user $ServerName -- `"$exe`""
    }
}

function Register-Codex {
    # Ecriture directe dans ~/.codex/config.toml : `codex mcp add` ne sait pas regler
    # tool_timeout_sec, or le defaut de Codex (60 s) coupe les traitements QGIS longs.
    $codexDir = Join-Path $HOME ".codex"
    $config = Join-Path $codexDir "config.toml"
    New-Item -ItemType Directory -Force $codexDir | Out-Null
    $content = ""
    if (Test-Path $config) {
        Copy-Item $config "$config.bak" -Force
        $content = [System.IO.File]::ReadAllText($config)
    }
    # Retire l'ancienne section cynogis (jusqu'a la section suivante ou la fin du fichier)
    $content = [regex]::Replace($content, "(?ms)^\[mcp_servers\.$ServerName\]\r?\n.*?(?=^\[|\z)", "")
    # Chaine litterale TOML (apostrophes) : pas besoin d'echapper les antislash Windows
    $block = "[mcp_servers.$ServerName]`r`ncommand = '$exe'`r`nargs = []`r`n" +
             "tool_timeout_sec = 3600   # traitements QGIS longs (defaut Codex : 60 s)`r`n"
    $content = if ($content.Trim()) { $content.TrimEnd() + "`r`n`r`n" + $block } else { $block }
    # UTF-8 SANS BOM : PowerShell 5.1 ajoute un BOM par defaut, ce qui peut gener le parseur TOML
    [System.IO.File]::WriteAllText($config, $content, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "      Codex configure via $config (verifier : codex mcp list)"
}

switch ($Agent) {
    "claude" { Register-ClaudeCode }
    "codex"  { Register-Codex }
    "both"   { Register-ClaudeCode; Register-Codex }
    "none"   { Write-Host "      Aucun agent configure." }
}

Write-Host ""
Write-Host "Termine."
Write-Host "Chemin du serveur (Claude Desktop / config manuelle) : $exe"
Write-Host "Dans QGIS : Extensions > Installees > cocher Cynogis, puis bouton 'Serveur Cynogis'."
Write-Host "Ensuite, relancez votre assistant IA et demandez-lui : ping"
