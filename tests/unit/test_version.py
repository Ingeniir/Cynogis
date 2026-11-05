import importlib.util
import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "build_plugin.py"
spec = importlib.util.spec_from_file_location("build_plugin", SCRIPT)
build_plugin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_plugin)


def test_versions_aligned():
    """metadata.txt, plugin, serveur et pyproject portent la même version (cf. --bump)."""
    versions = {}
    for path, (pattern, _) in build_plugin.VERSION_FILES.items():
        line = re.search(pattern, path.read_text(encoding="utf-8")).group(0)
        versions[path.name] = re.search(r"\d+(\.\d+)+", line).group(0)
    assert len(set(versions.values())) == 1, versions
