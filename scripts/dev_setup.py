"""Prépare le poste de dev (PyCharm) : autocomplétion PyQGIS + lien du plugin.

Usage (avec le Python du .venv) : python scripts/dev_setup.py [--no-link] [--no-stubs]
Prérequis : .qgis_env.json généré par scripts/qgis_env_snippet.py dans QGIS.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_SRC = ROOT / "plugin" / "cynogis"
ENV_FILE = ROOT / ".qgis_env.json"
PTH_NAME = "cynogis_dev.pth"
IS_WINDOWS = os.name == "nt"


def ensure_venv() -> None:
    if sys.prefix == sys.base_prefix:
        sys.exit("✗ Lance ce script avec le Python du .venv (terminal PyCharm ou venv activé).")


def load_env() -> dict:
    if not ENV_FILE.exists():
        sys.exit("✗ .qgis_env.json introuvable : exécute d'abord "
                 "scripts/qgis_env_snippet.py dans QGIS.")
    return json.loads(ENV_FILE.read_text(encoding="utf-8"))


def check_python(env: dict) -> None:
    qgis_py = tuple(int(x) for x in env["python_version"].split(".")[:2])
    here = sys.version_info[:2]
    if here != qgis_py:
        print(f"⚠ venv en Python {here[0]}.{here[1]}, QGIS en Python {qgis_py[0]}.{qgis_py[1]} : "
              f"recrée le venv en {qgis_py[0]}.{qgis_py[1]} pour éviter les faux positifs.")
    else:
        print(f"✓ Python {here[0]}.{here[1]} identique à celui de QGIS {env['qgis_version']}")


def qt_major(env: dict) -> int:
    return int(env["qt_version"].split(".")[0])


def has_native_stubs(qgis_python_dir: Path) -> bool:
    pkg = qgis_python_dir / "qgis"
    return pkg.is_dir() and next(pkg.glob("**/*core*.pyi"), None) is not None


def write_pth(env: dict) -> None:
    qgis_dir = Path(env["qgis_python_dir"])
    entries = [ROOT / "plugin", qgis_dir, qgis_dir / "plugins"]  # plugins → module `processing`
    entries = [p for p in entries if p.is_dir()]
    site = Path(sysconfig.get_paths()["purelib"])
    pth = site / PTH_NAME
    pth.write_text("\n".join(str(p) for p in entries) + "\n", encoding="utf-8")
    print(f"✓ {pth.name} écrit dans le venv ({len(entries)} chemins)")


def install_stubs(env: dict, native: bool) -> None:
    qt = qt_major(env)
    pkgs: list[str] = []
    pre: list[str] = []
    if native:
        print("✓ Stubs QGIS natifs trouvés (.pyi) : qgis-stubs inutile")
    else:
        print("⚠ Pas de .pyi dans l'installation QGIS : installation de qgis-stubs")
        pkgs.append("qgis-stubs>=1.0" if qt == 6 else "qgis-stubs<1")
        if qt == 6:
            pre = ["--pre"]
    pkgs.append("PyQt6" if qt == 6 else "PyQt5-stubs")  # dev uniquement, jamais dans le plugin
    subprocess.run([sys.executable, "-m", "pip", "install", *pre, *pkgs], check=True)
    print(f"✓ Stubs installés : {', '.join(pkgs)}")


def _is_link(p: Path) -> bool:
    try:
        os.readlink(p)  # symlinks ET jonctions Windows
        return True
    except (OSError, ValueError):
        return False


def link_plugin(env: dict) -> None:
    plugins_dir = Path(env["plugins_dir"])
    plugins_dir.mkdir(parents=True, exist_ok=True)
    target = plugins_dir / PLUGIN_SRC.name
    if _is_link(target):
        print(f"✓ Lien déjà présent : {target}")
        return
    if target.exists():
        sys.exit(f"✗ {target} existe et n'est pas un lien : renomme-le puis relance.")
    if IS_WINDOWS:  # jonction : pas besoin de droits administrateur
        subprocess.run(["cmd", "/c", "mklink", "/J", str(target), str(PLUGIN_SRC)],
                       check=True, capture_output=True)
    else:
        target.symlink_to(PLUGIN_SRC, target_is_directory=True)
    print(f"✓ Plugin lié : {target} → {PLUGIN_SRC}")


def print_client_config() -> None:
    py = Path(sys.executable)
    cfg = {"mcpServers": {"cynogis": {"command": str(py), "args": ["-m", "cynogis_server"]}}}
    print("\nConfiguration du client MCP (ex. claude_desktop_config.json) :")
    print(json.dumps(cfg, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-link", action="store_true",
                        help="ne pas lier le plugin au profil QGIS")
    parser.add_argument("--no-stubs", action="store_true", help="ne pas installer de stubs")
    args = parser.parse_args()

    ensure_venv()
    env = load_env()
    check_python(env)
    write_pth(env)
    if not args.no_stubs:
        install_stubs(env, has_native_stubs(Path(env["qgis_python_dir"])))
    if not args.no_link:
        link_plugin(env)
    print_client_config()
    print("\n→ Dans PyCharm : recharge les chemins de l'interpréteur (voir README) "
          "puis attends l'indexation.")


if __name__ == "__main__":
    main()
