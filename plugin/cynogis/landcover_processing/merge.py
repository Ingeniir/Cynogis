"""Fusion déterministe des objets segmentés en unités délimitées.

Sans QGIS, GDAL ni fichiers : tables d'objets et d'arêtes de object_features en entrée.
1. Similarité : fusion gloutonne des paires voisines les plus proches en couleur
   (distance euclidienne des moyennes RGB pondérées par les pixels), tant que la
   distance reste au plus color_distance_max. Désactivée si color_distance_max = 0.
2. Surface minimale : chaque unité plus petite que min_mapping_area_m2 rejoint sa
   voisine la plus proche en couleur (égalité : frontière commune la plus longue,
   puis plus petit identifiant). Une unité sans voisine est conservée et comptée.

Le représentant d'une unité est son plus petit identifiant de segment : le résultat
ne dépend ni de l'ordre des tables ni des égalités de distance.
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class MergeResult:
    """roots[i] : représentant de l'objet i (ordre de la table objects)."""

    roots: list[int]
    merged_by_similarity: int
    merged_by_area: int
    isolated_small_units: int


def merge_segments(objects, edges, *, pixel_area_m2: float, color_distance_max: float,
                   min_mapping_area_m2: float) -> MergeResult:
    ids = [int(v) for v in objects["segment_id"]]
    count = {i: int(c) for i, c in zip(ids, objects["pixel_count"], strict=True)}
    total = {i: [float(m) * count[i] for m in mean]
             for i, mean in zip(ids, objects["rgb_mean"], strict=True)}
    neighbours: dict[int, dict[int, int]] = {i: {} for i in ids}
    for a, b, sides in zip(edges["segment_a"], edges["segment_b"],
                           edges["shared_pixel_sides"], strict=True):
        a, b, sides = int(a), int(b), int(sides)
        if a not in neighbours or b not in neighbours or a == b:
            raise ValueError("Arête vers un objet inconnu ou en boucle.")
        neighbours[a][b] = neighbours[b][a] = sides

    parent = {i: i for i in ids}

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def distance(a: int, b: int) -> float:
        return math.dist([v / count[a] for v in total[a]], [v / count[b] for v in total[b]])

    def union(a: int, b: int) -> int:
        keep, gone = min(a, b), max(a, b)
        parent[gone] = keep
        count[keep] += count.pop(gone)
        total[keep] = [x + y for x, y in zip(total[keep], total.pop(gone), strict=True)]
        moved = neighbours.pop(gone)
        moved.pop(keep, None)
        neighbours[keep].pop(gone, None)
        for other, sides in moved.items():
            neighbours[other].pop(gone)
            merged = neighbours[keep].get(other, 0) + sides
            neighbours[keep][other] = neighbours[other][keep] = merged
        return keep

    by_similarity = 0
    if color_distance_max > 0:
        heap = [(distance(a, b), a, b) for a in ids for b in neighbours[a]
                if a < b and distance(a, b) <= color_distance_max]
        heapq.heapify(heap)
        while heap:
            d, a, b = heapq.heappop(heap)
            if find(a) != a or find(b) != b:
                continue  # entrée périmée : une extrémité a été absorbée
            current = distance(a, b)
            if current != d:
                if current <= color_distance_max:
                    heapq.heappush(heap, (current, a, b))
                continue
            keep = union(a, b)
            by_similarity += 1
            for other in neighbours[keep]:
                d2 = distance(keep, other)
                if d2 <= color_distance_max:
                    heapq.heappush(heap, (d2, min(keep, other), max(keep, other)))

    by_area = isolated = 0
    if min_mapping_area_m2 > 0:
        small = [(count[i] * pixel_area_m2, i) for i in count
                 if count[i] * pixel_area_m2 < min_mapping_area_m2]
        heapq.heapify(small)
        while small:
            area, i = heapq.heappop(small)
            if i not in count or count[i] * pixel_area_m2 != area:
                continue  # absorbée, ou agrandie et déjà réinsérée
            if not neighbours[i]:
                isolated += 1
                continue
            target = min(neighbours[i],
                         key=lambda o, i=i: (distance(i, o), -neighbours[i][o], o))
            keep = union(i, target)
            by_area += 1
            new_area = count[keep] * pixel_area_m2
            if new_area < min_mapping_area_m2:
                heapq.heappush(small, (new_area, keep))

    return MergeResult([find(i) for i in ids], by_similarity, by_area, isolated)
