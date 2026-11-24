"""Tests d'intégration sous le Python de QGIS, dans des processus et dossiers isolés.

    .venv/Scripts/python scripts/run_qgis_integration.py [--qgis-python LANCEUR] [--keep]
                                                         [-- ARGUMENTS PYTEST]

Sans argument pytest : « -q -rs tests/integration ». Les résultats affichés ici sont ceux
du Python de QGIS ; « .venv/Scripts/python -m pytest » donne ceux du venv, où les modules
PyQGIS/GDAL sont ignorés (voir tests/integration/_pyqgis_abi.py).

Lanceur de l'interpréteur QGIS, dans l'ordre : --qgis-python, variable CYNOGIS_QGIS_PYTHON,
puis .qgis_env.json (scripts/qgis_env_snippet.py) : <python_prefix>/../../bin/python-qgis.bat.
Aucune version de Python n'est supposée : une sonde interroge l'interpréteur trouvé.

Aucune installation : si pytest manque côté QGIS, les fichiers des distributions pures
nécessaires (pytest, pluggy, iniconfig, pygments, colorama, packaging si absent) sont copiés
depuis l'interpréteur qui exécute ce script vers un dossier temporaire, ajouté EN FIN de
sys.path. Toute extension binaire ou incompatibilité Requires-Python fait échouer le lancement.

Isolation : profil QGIS (QGIS_CUSTOM_CONFIG_PATH), HOME/USERPROFILE, TEMP/TMP et
CYNOGIS_CONNECTION_FILE pointent vers un dossier temporaire ; PYTHON* hérités retirés ;
pas de bytecode ; Qt hors écran. APPDATA est conservé : il porte le site utilisateur du
Python de QGIS (scikit-image du prototype OBIA). La session QGIS ouverte n'est pas touchée.
Dossier temporaire supprimé après succès, conservé (chemin affiché) après échec ou --keep.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".qgis_env.json"
DEFAULT_ARGS = ["-q", "-rs", "tests/integration"]
BINARY_SUFFIXES = {".pyd", ".so", ".dll", ".dylib", ".exe"}
PROBE_TAG = "CYNOGIS_PROBE "
_PROBE = f"""
import importlib.util, json, sys
print({PROBE_TAG!r} + json.dumps({{
    "version": list(sys.version_info[:3]), "executable": sys.executable,
    "prefix": sys.prefix,
    "has": {{n: importlib.util.find_spec(n) is not None for n in ("pytest", "packaging")}},
}}))
"""


def _fail(message: str) -> NoReturn:
    sys.exit(f"✗ {message}")


def find_launcher(explicit: str | None) -> Path:
    candidate = explicit or os.environ.get("CYNOGIS_QGIS_PYTHON")
    if not candidate and ENV_FILE.is_file():
        prefix = json.loads(ENV_FILE.read_text(encoding="utf-8")).get("python_prefix")
        if prefix:
            candidate = str(Path(prefix).parents[1] / "bin" / "python-qgis.bat")
    if not candidate:
        _fail("interpréteur QGIS introuvable : --qgis-python, CYNOGIS_QGIS_PYTHON ou "
              ".qgis_env.json (scripts/qgis_env_snippet.py dans QGIS).")
    path = Path(candidate)
    if not path.is_file():
        _fail(f"lanceur QGIS absent : {path}")
    return path


def command(launcher: Path, *args: str) -> str | list[str]:
    """Un .bat passe par cmd : /s préserve les guillemets des chemins avec espaces."""
    if os.name == "nt" and launcher.suffix.lower() in {".bat", ".cmd"}:
        return f'cmd.exe /d /s /c "{subprocess.list2cmdline([str(launcher), *args])}"'
    return [str(launcher), *args]


def isolated_env(work: Path, bundle: Path | None, pytest_args: list[str]) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if not k.upper().startswith("PYTHON") and k.upper() != "VIRTUAL_ENV"}
    folders = {name: work / name for name in ("home", "qgis_profile", "temp", "connection")}
    for folder in folders.values():
        folder.mkdir()
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "QT_QPA_PLATFORM": "offscreen",
        "HOME": str(folders["home"]),
        "USERPROFILE": str(folders["home"]),
        "QGIS_CUSTOM_CONFIG_PATH": str(folders["qgis_profile"]),
        "TEMP": str(folders["temp"]),
        "TMP": str(folders["temp"]),
        "CYNOGIS_CONNECTION_FILE": str(folders["connection"] / "connection.json"),
        "CYNOGIS_PYTEST_BUNDLE": str(bundle) if bundle else "",
        "CYNOGIS_PYTEST_ARGS": json.dumps(pytest_args),
        "CYNOGIS_ISOLATION_ROOT": str(work),
    })
    return env


def probe(launcher: Path, work: Path, env: dict[str, str]) -> dict:
    script = work / "probe.py"
    script.write_text(_PROBE, encoding="utf-8")
    result = subprocess.run(command(launcher, str(script)), env=env, cwd=work,
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=120, check=False)
    line = next((ln for ln in result.stdout.splitlines() if ln.startswith(PROBE_TAG)), None)
    if line is None:
        _fail(f"sonde de l'interpréteur QGIS en échec :\n{result.stderr[-2000:]}")
    info = json.loads(line[len(PROBE_TAG):])
    if Path(info["prefix"]).resolve() == Path(sys.prefix).resolve():
        _fail("le lanceur désigne l'interpréteur courant, pas celui de QGIS.")
    return info


def build_bundle(work: Path, info: dict) -> Path | None:
    """Copie des distributions pures de pytest, ou None si QGIS fournit déjà pytest."""
    if info["has"]["pytest"]:
        return None
    from packaging.specifiers import SpecifierSet  # dépendance de pytest, côté lanceur

    target = ".".join(str(n) for n in info["version"])
    names = ["pytest", "pluggy", "iniconfig", "pygments"]
    if os.name == "nt":
        names.append("colorama")
    if not info["has"]["packaging"]:
        names.append("packaging")
    bundle = work / "pytest_bundle"
    for name in names:
        try:
            dist = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            _fail(f"{name} absent de l'interpréteur lanceur ({sys.executable}).")
        requires = dist.metadata.get("Requires-Python")
        if requires and target not in SpecifierSet(requires):
            _fail(f"{name} {dist.version} exige Python {requires}, QGIS fournit {target}.")
        for file in dist.files or ():
            if file.parts[0] == ".." or "__pycache__" in file.parts or file.suffix == ".pyc":
                continue  # scripts d'entrée hors site-packages, bytecode
            if file.suffix.lower() in BINARY_SUFFIXES:
                _fail(f"{name} contient une extension binaire ({file}) : copie refusée.")
            destination = bundle / file
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(dist.locate_file(file)), destination)
    return bundle


def bootstrap() -> int:
    """Exécuté par le Python de QGIS : pytest du bundle en fin de sys.path, puis tests."""
    bundle = os.environ.get("CYNOGIS_PYTEST_BUNDLE")
    if bundle:
        sys.path.append(bundle)
    isolation = Path(os.environ["CYNOGIS_ISOLATION_ROOT"])
    for name in ("HOME", "QGIS_CUSTOM_CONFIG_PATH", "TEMP", "CYNOGIS_CONNECTION_FILE"):
        if isolation not in Path(os.environ[name]).parents:
            print(f"✗ isolation non respectée : {name}", file=sys.stderr)
            return 2
    import pytest

    print(f"=== Python de QGIS {sys.version.split()[0]} ({sys.executable}) ; "
          f"pytest {pytest.__version__} ===", flush=True)
    return int(pytest.main(["-p", "no:cacheprovider",
                            *json.loads(os.environ["CYNOGIS_PYTEST_ARGS"])]))


def main() -> int:
    if sys.argv[1:2] == ["--bootstrap"]:
        return bootstrap()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--qgis-python", help="lanceur de l'interpréteur Python de QGIS")
    parser.add_argument("--keep", action="store_true", help="conserver le dossier isolé")
    parser.add_argument("pytest_args", nargs="*", help="arguments pytest (après --)")
    options = parser.parse_args()

    launcher = find_launcher(options.qgis_python)
    work = Path(tempfile.mkdtemp(prefix="cynogis_qgis_it_"))
    code = 1
    try:
        env = isolated_env(work, None, options.pytest_args or DEFAULT_ARGS)
        info = probe(launcher, work, env)
        bundle = build_bundle(work, info)
        env["CYNOGIS_PYTEST_BUNDLE"] = str(bundle) if bundle else ""
        print(f"--- Lancement sous le Python de QGIS {'.'.join(map(str, info['version']))} "
              f"({info['executable']}) ; pytest {'copié' if bundle else 'de QGIS'}", flush=True)
        code = subprocess.run(command(launcher, str(Path(__file__).resolve()), "--bootstrap"),
                              env=env, cwd=ROOT, check=False).returncode
        print(f"=== Résultat sous le Python de QGIS : code {code} "
              f"({'succès' if code == 0 else 'échec'}) ===", flush=True)
        return code
    finally:
        if code == 0 and not options.keep:
            shutil.rmtree(work, ignore_errors=True)
        else:
            print(f"Dossier isolé conservé : {work}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
