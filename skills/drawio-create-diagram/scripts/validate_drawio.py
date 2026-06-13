#!/usr/bin/env python3
"""Basic structural validation for uncompressed draw.io XML files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def iter_graph_models(root: ET.Element) -> list[ET.Element]:
    name = local_name(root.tag)
    if name == "mxGraphModel":
        return [root]
    if name == "mxfile":
        return [elem for elem in root.iter() if local_name(elem.tag) == "mxGraphModel"]
    return []


def validate_model(model: ET.Element, index: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    root = next((child for child in model if local_name(child.tag) == "root"), None)
    if root is None:
        return [f"model {index}: missing <root>"], warnings

    cells = [cell for cell in root if local_name(cell.tag) == "mxCell"]
    ids: dict[str, ET.Element] = {}
    for cell in cells:
        cell_id = cell.get("id")
        if not cell_id:
            errors.append(f"model {index}: mxCell without id")
            continue
        if cell_id in ids:
            errors.append(f"model {index}: duplicate id {cell_id}")
        ids[cell_id] = cell

    if "0" not in ids:
        errors.append(f"model {index}: missing structural cell id=0")
    if "1" not in ids:
        errors.append(f"model {index}: missing structural cell id=1")
    elif ids["1"].get("parent") != "0":
        errors.append(f"model {index}: structural cell id=1 must have parent=0")

    for cell_id, cell in ids.items():
        is_vertex = cell.get("vertex") == "1"
        is_edge = cell.get("edge") == "1"
        if is_vertex and is_edge:
            errors.append(f"model {index}: cell {cell_id} cannot be both vertex and edge")
        if (is_vertex or is_edge) and cell.find("mxGeometry") is None:
            errors.append(f"model {index}: cell {cell_id} is missing mxGeometry")
        parent = cell.get("parent")
        if cell_id not in {"0", "1"} and parent and parent not in ids:
            errors.append(f"model {index}: cell {cell_id} references unknown parent {parent}")
        if is_edge:
            for endpoint in ("source", "target"):
                target_id = cell.get(endpoint)
                if target_id and target_id not in ids:
                    errors.append(f"model {index}: edge {cell_id} references unknown {endpoint} {target_id}")
            if not cell.get("source") and not cell.get("target"):
                geom = cell.find("mxGeometry")
                has_points = False
                if geom is not None:
                    point_kinds = {point.get("as") for point in geom if local_name(point.tag) == "mxPoint"}
                    has_points = {"sourcePoint", "targetPoint"}.issubset(point_kinds)
                if not has_points:
                    warnings.append(f"model {index}: edge {cell_id} has no source/target or explicit endpoints")

    return errors, warnings


def validate_file(path: Path) -> int:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        print(f"ERROR: XML parse failed: {exc}")
        return 1

    models = iter_graph_models(root)
    if not models:
        print("ERROR: root must be <mxfile> or <mxGraphModel>, with at least one mxGraphModel")
        return 1

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for index, model in enumerate(models, start=1):
        errors, warnings = validate_model(model, index)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    for warning in all_warnings:
        print(f"WARNING: {warning}")
    for error in all_errors:
        print(f"ERROR: {error}")
    if all_errors:
        return 1
    print(f"OK: {path} has {len(models)} mxGraphModel(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="draw.io XML files to validate")
    args = parser.parse_args(argv)
    status = 0
    for value in args.paths:
        status = max(status, validate_file(Path(value)))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
