"""Construit le zip installable du plugin et, au besoin, un dépôt de plugins QGIS privé.

Usage : python scripts/build_plugin.py [--bump] [--repo DOSSIER]
  --bump        incrémente le dernier chiffre de version de metadata.txt avant la construction
                (indispensable pour que QGIS propose la mise à jour aux postes déjà équipés)
  --repo DOSSIER copie le zip dans DOSSIER (ex. partage réseau) et y écrit plugins.xml ;
                dans QGIS : Extensions > Paramètres > Ajouter, URL file:///DOSSIER/plugins.xml
Sortie : dist/cynogis-<version>.zip (installable par Extensions > Installer depuis un ZIP).
"""
from __future__ import annotations

import argparse
import configparser
import re
import shutil
import sys
import zipfile
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SRC = ROOT / "plugin" / "cynogis"
METADATA = PLUGIN_SRC / "metadata.txt"
DIST = ROOT / "dist"
EXCLUDED_DIRS = {"__pycache__", ".pytest_cache", ".ruff_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def read_metadata() -> dict[str, str]:
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(METADATA, encoding="utf-8")
    return dict(parser["general"])


def bump_version(version: str) -> str:
    """0.1.0 -> 0.1.1 ; 1.2 -> 1.3."""
    parts = version.split(".")
    if not parts[-1].isdigit():
        sys.exit(f"✗ Version « {version} » : dernier élément non numérique, à modifier à la main.")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def write_version(version: str) -> None:
    text = METADATA.read_text(encoding="utf-8")
    METADATA.write_text(re.sub(r"(?m)^version=.*$", f"version={version}", text),
                        encoding="utf-8")


def build_zip(version: str) -> Path:
    DIST.mkdir(exist_ok=True)
    target = DIST / f"cynogis-{version}.zip"
    files = sorted(p for p in PLUGIN_SRC.rglob("*")
                   if p.is_file() and p.suffix not in EXCLUDED_SUFFIXES
                   and not EXCLUDED_DIRS.intersection(p.relative_to(PLUGIN_SRC).parts))
    # Le zip contient le dossier « cynogis/ » : QGIS l'installe sous ce nom dans le profil.
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path("cynogis") / path.relative_to(PLUGIN_SRC))
    return target


def write_repository(repo: Path, zip_path: Path, meta: dict[str, str]) -> Path:
    repo.mkdir(parents=True, exist_ok=True)
    shutil.copy2(zip_path, repo / zip_path.name)
    plugins = ET.Element("plugins")
    plugin = ET.SubElement(plugins, "pyqgis_plugin", name=meta["name"], version=meta["version"])
    fields = {
        "description": meta.get("description", ""),
        "about": meta.get("about", ""),
        "version": meta["version"],
        "qgis_minimum_version": meta.get("qgisminimumversion", "3.38"),
        "qgis_maximum_version": meta.get("qgismaximumversion", "4.99"),
        "file_name": zip_path.name,
        "download_url": (repo / zip_path.name).resolve().as_uri(),
        "author_name": meta.get("author", ""),
        "update_date": date.today().isoformat(),
        "experimental": meta.get("experimental", "False"),
        "deprecated": meta.get("deprecated", "False"),
    }
    for tag, value in fields.items():
        ET.SubElement(plugin, tag).text = value
    xml_path = repo / "plugins.xml"
    ET.ElementTree(plugins).write(xml_path, encoding="utf-8", xml_declaration=True)
    return xml_path


def main() -> None:
    args = argparse.ArgumentParser(description="Construit le zip du plugin Cynogis.")
    args.add_argument("--bump", action="store_true", help="incrémente la version avant build")
    args.add_argument("--repo", type=Path, help="dossier du dépôt de plugins privé")
    opts = args.parse_args()

    meta = read_metadata()
    if opts.bump:
        meta["version"] = bump_version(meta["version"])
        write_version(meta["version"])
        print(f"• Version passée à {meta['version']}")
    zip_path = build_zip(meta["version"])
    print(f"✓ {zip_path}")
    if opts.repo:
        print(f"✓ Dépôt : {write_repository(opts.repo, zip_path, meta)}")


if __name__ == "__main__":
    main()
