"""Sorties : GeoPackage dans <projet>/mcp_outputs/, jamais écrasé, ajouté au groupe « Cynogis »."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from qgis import processing
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsMapLayer,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsProject,
    QgsRasterLayer,
    QgsVectorFileWriter,
    QgsVectorLayer,
)

from ..core.dispatcher import ToolResult
from ..core.errors import ErrorCode, ToolError
from ..core.naming import clean_name, unique_path
from .common import to_json_value

GROUP = "Cynogis"
OUTPUT_DIRNAME = "mcp_outputs"
FALLBACK_DIR = Path.home() / ".cynogis" / OUTPUT_DIRNAME
_SUFFIXES = {"sink": ".gpkg", "vectorDestination": ".gpkg", "rasterDestination": ".tif"}
logger = logging.getLogger("cynogis.outputs")
_WRITE_OK = getattr(QgsVectorFileWriter, "WriterError", QgsVectorFileWriter).NoError


def output_dir() -> tuple[Path, list[str]]:
    home = QgsProject.instance().homePath()
    warnings: list[str] = []
    if home:
        directory = Path(home) / OUTPUT_DIRNAME
    else:
        directory = FALLBACK_DIR
        warnings.append(f"Projet non enregistré : sorties écrites dans {directory}. "
                        "Demande à l'utilisateur d'enregistrer le projet.")
    directory.mkdir(parents=True, exist_ok=True)
    return directory, warnings


def add_to_project(path: Path, name: str, raster: bool = False) -> QgsMapLayer:
    layer = QgsRasterLayer(str(path), name) if raster else QgsVectorLayer(str(path), name, "ogr")
    if not layer.isValid():
        raise ToolError(ErrorCode.PROCESSING_FAILED, f"Sortie illisible : {path}")
    return add_to_group(layer)


def add_to_group(layer: QgsMapLayer) -> QgsMapLayer:
    """Ajoute une couche au projet, en tête du groupe « Cynogis » (créé au besoin)."""
    project = QgsProject.instance()
    root = project.layerTreeRoot()
    group = root.findGroup(GROUP) or root.insertGroup(0, GROUP)
    project.addMapLayer(layer, False)
    group.insertLayer(0, layer)
    return layer


def is_optional(param: Any) -> bool:
    return bool(param.flags() & Qgis.ProcessingParameterFlag.Optional)


def _run(algorithm_id: str, params: dict[str, Any]) -> dict[str, Any]:
    context = QgsProcessingContext()
    context.setProject(QgsProject.instance())
    feedback = QgsProcessingFeedback()
    try:
        return processing.run(algorithm_id, params, context=context, feedback=feedback)
    except QgsProcessingException as exc:
        raise ToolError(ErrorCode.PROCESSING_FAILED, f"{algorithm_id} : {exc}",
                        {"log": feedback.textLog()[-2000:]}) from exc


def run_in_memory(algorithm_id: str, params: dict[str, Any]) -> QgsVectorLayer:
    """Étape intermédiaire : sortie OUTPUT en couche mémoire, rien d'écrit ni d'ajouté au
    projet. Le résultat final passe ensuite par run_to_project."""
    return _run(algorithm_id, {**params, "OUTPUT": "memory:"})["OUTPUT"]


def run_to_project(algorithm_id: str, params: dict[str, Any], output_name: str) -> ToolResult:
    """Exécute un algorithme Processing ; chaque sortie obligatoire va dans un fichier neuf de
    mcp_outputs/ puis est ajoutée au projet. Les paramètres de sortie sont imposés ici."""
    alg = QgsApplication.processingRegistry().algorithmById(algorithm_id)
    if alg is None:
        raise ToolError(ErrorCode.ALGORITHM_NOT_ALLOWED,
                        f"Algorithme {algorithm_id} indisponible dans cette version de QGIS.")
    directory, warnings = output_dir()
    base = clean_name(output_name)
    destinations = [p for p in alg.destinationParameterDefinitions() if not is_optional(p)]
    targets: dict[str, tuple[Path, bool]] = {}
    for param in destinations:
        suffix = _SUFFIXES.get(param.type())
        if suffix is None:
            raise ToolError(ErrorCode.ALGORITHM_NOT_ALLOWED,
                            f"Sortie {param.name()} de type {param.type()} non gérée.")
        name = base if len(destinations) == 1 else f"{base}_{clean_name(param.name())}"
        targets[param.name()] = (unique_path(directory, name, suffix), suffix == ".tif")

    results = _run(algorithm_id, {**params, **{k: str(p) for k, (p, _) in targets.items()}})

    outputs = [_output_item(key, path, raster, warnings)
               for key, (path, raster) in targets.items()]
    other = {k: to_json_value(v) for k, v in results.items() if k not in targets}
    logger.info("%s → %s", algorithm_id, ", ".join(o["path"] for o in outputs))
    return ToolResult({"algorithm": algorithm_id, "outputs": outputs, "results": other},
                      warnings, [o["path"] for o in outputs])


def save_to_project(layer: QgsVectorLayer, output_name: str) -> ToolResult:
    """Résultat calculé en Python (couche mémoire) → GeoPackage neuf de mcp_outputs/, ajouté au
    projet. Remplace native:savefeatures, dont la sortie « fichier » varie selon les versions
    de QGIS. Même forme de résultat que run_to_project."""
    directory, warnings = output_dir()
    path = unique_path(directory, clean_name(output_name), ".gpkg")
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GPKG"
    options.layerName = path.stem
    error, message, *_ = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer, str(path), QgsProject.instance().transformContext(), options)
    if error != _WRITE_OK:
        raise ToolError(ErrorCode.WRITE_FAILED, f"Écriture de {path} impossible : {message}")
    item = _output_item("OUTPUT", path, False, warnings)
    logger.info("couche mémoire → %s", path)
    return ToolResult({"algorithm": None, "outputs": [item], "results": {}}, warnings, [str(path)])


def _output_item(key: str, path: Path, raster: bool, warnings: list[str]) -> dict[str, Any]:
    layer = add_to_project(path, path.stem, raster)
    item: dict[str, Any] = {"output": key, "layer_id": layer.id(), "name": layer.name(),
                            "path": str(path)}
    if isinstance(layer, QgsVectorLayer):
        item["feature_count"] = layer.featureCount()
        if layer.featureCount() == 0:
            warnings.append(f"{layer.name()} est vide.")
    return item
