#!/usr/bin/env python3
"""Visual layout lint for uncompressed draw.io XML files.

This is a geometry-based QA pass. It does not render draw.io stencils, but it catches
the most common visual defects before a human or browser screenshot review.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


@dataclass
class Issue:
    severity: str
    path: str
    page: int
    cell_id: str
    message: str


@dataclass
class Box:
    cell_id: str
    label: str
    style: str
    x: float
    y: float
    w: float
    h: float
    parent: str

    @property
    def area(self) -> float:
        return max(0.0, self.w) * max(0.0, self.h)

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h


@dataclass
class Edge:
    cell_id: str
    label: str
    style: str
    source: str
    target: str


KNOWN_STENCILS = {
    "lean_mapping": {
        "finished_goods_to_customer",
        "go_see_production_scheduling",
        "kaizen_lightening_burst",
        "kanban_post",
        "load_leveling",
        "move_by_forklift",
        "mrp_erp",
        "operator",
        "quality_problem",
        "verbal",
        "airplane_7",
        "manual_info_flow",
        "electronic_info_flow",
    },
    "flowchart": {
        "process",
        "decision",
        "terminator",
        "data",
        "document",
        "database",
        "predefined_process",
        "manual_operation",
        "manual_input",
        "on-page_reference",
        "off-page_reference",
    },
    "kubernetes": {
        "ing",
        "svc",
        "deploy",
        "pod",
        "cm",
        "secret",
        "pvc",
        "pv",
        "ns",
        "node",
        "job",
        "cronjob",
        "sts",
        "rs",
        "netpol",
    },
    "networks": {
        "cloud",
        "firewall",
        "load_balancer",
        "server",
        "web_server",
        "storage",
        "users",
        "router",
        "switch",
        "wireless_hub",
        "desktop_pc",
        "laptop",
    },
    "eip": {
        "channel_adapter",
        "message_1",
        "message_store",
        "message_translator",
        "content_filter",
        "wire_tap",
        "service_activator",
        "process_manager",
        "aggregator",
        "splitter",
        "content_based_router",
    },
}

ICON_STENCIL_FAMILIES = {"lean_mapping", "kubernetes", "networks", "eip"}
COMMON_UNVERIFIED_FAMILIES = {
    "aws4",
    "azure",
    "gcp",
    "cisco",
    "bpmn",
    "uml",
    "er",
    "pid",
    "mockup",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def iter_graph_models(root: ET.Element) -> list[ET.Element]:
    name = local_name(root.tag)
    if name == "mxGraphModel":
        return [root]
    if name == "mxfile":
        return [elem for elem in root.iter() if local_name(elem.tag) == "mxGraphModel"]
    return []


def number(value: str | None, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except ValueError:
        return default


def font_size(style: str) -> float:
    match = re.search(r"(?:^|;)fontSize=([0-9.]+)", style)
    return number(match.group(1), 12.0) if match else 12.0


def clean_label(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<br\\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    return value.strip()


def is_container(box: Box) -> bool:
    style = box.style
    return "swimlane" in style or "container=1" in style


def is_native_icon(box: Box) -> bool:
    return "shape=mxgraph." in box.style


def is_text_only(box: Box) -> bool:
    style = box.style
    return style.startswith("text;") or "strokeColor=none" in style and "fillColor=none" in style


def contained(inner: Box, outer: Box, tolerance: float = 4.0) -> bool:
    return (
        inner.x >= outer.x - tolerance
        and inner.y >= outer.y - tolerance
        and inner.right <= outer.right + tolerance
        and inner.bottom <= outer.bottom + tolerance
    )


def intersection(a: Box, b: Box) -> float:
    x1 = max(a.x, b.x)
    y1 = max(a.y, b.y)
    x2 = min(a.right, b.right)
    y2 = min(a.bottom, b.bottom)
    if x2 <= x1 or y2 <= y1:
        return 0.0
    return (x2 - x1) * (y2 - y1)


def stencil_ref(style: str) -> tuple[str, str] | None:
    match = re.search(r"(?:^|;)shape=mxgraph\.([A-Za-z0-9_]+)\.([A-Za-z0-9_.-]+)", style)
    if not match:
        return None
    return match.group(1), match.group(2)


def normalize_family(value: str) -> str:
    value = value.strip()
    if value.startswith("mxgraph."):
        value = value.removeprefix("mxgraph.")
    return value.split(".", 1)[0]


def parse_required_families(values: list[str]) -> set[str]:
    families: set[str] = set()
    for value in values:
        for part in value.split(","):
            if part.strip():
                families.add(normalize_family(part))
    return families


def on_grid(value: float, step: float, tolerance: float = 0.01) -> bool:
    if step <= 0:
        return True
    return abs(value - round(value / step) * step) <= tolerance


def extract_boxes(model: ET.Element) -> list[Box]:
    root = next((child for child in model if local_name(child.tag) == "root"), None)
    if root is None:
        return []
    boxes: list[Box] = []
    for cell in root:
        if local_name(cell.tag) != "mxCell" or cell.get("vertex") != "1":
            continue
        geom = next((child for child in cell if local_name(child.tag) == "mxGeometry"), None)
        if geom is None:
            continue
        boxes.append(
            Box(
                cell_id=cell.get("id", ""),
                label=clean_label(cell.get("value", "")),
                style=cell.get("style", ""),
                x=number(geom.get("x")),
                y=number(geom.get("y")),
                w=number(geom.get("width")),
                h=number(geom.get("height")),
                parent=cell.get("parent", "1"),
            )
        )
    return boxes


def extract_edges(model: ET.Element) -> list[Edge]:
    root = next((child for child in model if local_name(child.tag) == "root"), None)
    if root is None:
        return []
    edges: list[Edge] = []
    for cell in root:
        if local_name(cell.tag) != "mxCell" or cell.get("edge") != "1":
            continue
        edges.append(
            Edge(
                cell_id=cell.get("id", ""),
                label=clean_label(cell.get("value", "")),
                style=cell.get("style", ""),
                source=cell.get("source", ""),
                target=cell.get("target", ""),
            )
        )
    return edges


def lint_label(path: str, page: int, box: Box, issues: list[Issue]) -> None:
    if not box.label:
        return
    if is_native_icon(box):
        if len(box.label) > 28 and "verticalLabelPosition=bottom" not in box.style:
            issues.append(Issue("warn", path, page, box.cell_id, "native stencil label is long without bottom label positioning"))
        return
    size = font_size(box.style)
    usable_w = max(1.0, box.w - 16.0)
    chars_per_line = max(1, int(usable_w / max(1.0, size * 0.55)))
    lines = 0
    for part in box.label.splitlines() or [box.label]:
        words = part.split()
        if not words:
            lines += 1
            continue
        current = 0
        for word in words:
            word_len = len(word)
            if word_len * size * 0.55 > usable_w:
                issues.append(Issue("warn", path, page, box.cell_id, f"long word may overflow label: {word[:40]}"))
            if current == 0:
                current = word_len
            elif current + 1 + word_len <= chars_per_line:
                current += 1 + word_len
            else:
                lines += 1
                current = word_len
        lines += 1
    needed_h = lines * size * 1.25 + 12
    if needed_h > box.h * 1.2 and not is_text_only(box):
        issues.append(
            Issue(
                "warn",
                path,
                page,
                box.cell_id,
                f"label may not fit: needs about {math.ceil(needed_h)}px height, box has {box.h:g}px",
            )
        )


def lint_stencils(path: Path, page: int, boxes: list[Box], required_families: set[str], issues: list[Issue]) -> None:
    seen_families: dict[str, str] = {}
    reported_unverified: set[str] = set()
    for box in boxes:
        ref = stencil_ref(box.style)
        if not ref:
            continue
        family, shape_id = ref
        seen_families.setdefault(family, box.cell_id)
        if family in KNOWN_STENCILS and shape_id not in KNOWN_STENCILS[family]:
            issues.append(Issue("warn", str(path), page, box.cell_id, f"unrecognized mxgraph.{family} stencil id: {shape_id}"))
        elif family not in KNOWN_STENCILS and family not in COMMON_UNVERIFIED_FAMILIES and family not in reported_unverified:
            reported_unverified.add(family)
            issues.append(Issue("info", str(path), page, box.cell_id, f"native stencil family is not in the local map: mxgraph.{family}"))
        if family in ICON_STENCIL_FAMILIES and "aspect=fixed" not in box.style:
            issues.append(Issue("warn", str(path), page, box.cell_id, "native icon stencil should usually include aspect=fixed"))

    missing = sorted(required_families - set(seen_families))
    for family in missing:
        issues.append(Issue("error", str(path), page, "", f"required native stencil family not used: mxgraph.{family}"))


def lint_edges(path: Path, page: int, edges: list[Edge], issues: list[Issue]) -> None:
    for edge in edges:
        if edge.source and edge.target:
            if edge.source == edge.target:
                issues.append(Issue("warn", str(path), page, edge.cell_id, "edge source and target are the same"))
            if "edgeStyle=orthogonalEdgeStyle" not in edge.style and "elbowEdgeStyle" not in edge.style:
                issues.append(Issue("warn", str(path), page, edge.cell_id, "source/target edge should use an orthogonal or elbow edge style"))
        if edge.label and len(edge.label) > 42:
            issues.append(Issue("warn", str(path), page, edge.cell_id, "edge label is long; shorten it or move detail into nearby text"))
        if "html=1" not in edge.style:
            issues.append(Issue("warn", str(path), page, edge.cell_id, "edge style should include html=1 for consistent labels"))


def lint_canvas_use(path: Path, page: int, page_w: float, page_h: float, boxes: list[Box], issues: list[Issue]) -> None:
    visible = [box for box in boxes if not is_text_only(box)]
    if len(visible) < 3:
        return
    min_x = min(box.x for box in visible)
    min_y = min(box.y for box in visible)
    max_x = max(box.right for box in visible)
    max_y = max(box.bottom for box in visible)
    content_w = max_x - min_x
    content_h = max_y - min_y
    if content_w < page_w * 0.45 and content_h < page_h * 0.45:
        issues.append(
            Issue(
                "info",
                str(path),
                page,
                "",
                f"diagram uses a small part of the page ({content_w:g}x{content_h:g} of {page_w:g}x{page_h:g})",
            )
        )
    if min_x < 16 or min_y < 16:
        issues.append(Issue("warn", str(path), page, "", "visible content is very close to the page edge"))


def lint_grid(path: Path, page: int, boxes: list[Box], step: float, issues: list[Issue]) -> None:
    for box in boxes:
        values = {"x": box.x, "y": box.y, "width": box.w, "height": box.h}
        off_grid = [name for name, value in values.items() if not on_grid(value, step)]
        if off_grid:
            issues.append(Issue("warn", str(path), page, box.cell_id, f"geometry is off the {step:g}px grid: {', '.join(off_grid)}"))


def lint_model(
    path: Path,
    page: int,
    model: ET.Element,
    required_families: set[str],
    check_grid: bool,
    grid_step: float,
) -> list[Issue]:
    issues: list[Issue] = []
    page_w = number(model.get("pageWidth"), 850.0)
    page_h = number(model.get("pageHeight"), 1100.0)
    boxes = extract_boxes(model)
    edges = extract_edges(model)

    for box in boxes:
        if box.w <= 0 or box.h <= 0:
            issues.append(Issue("error", str(path), page, box.cell_id, "non-positive geometry"))
            continue
        if box.w < 12 or box.h < 12:
            issues.append(Issue("warn", str(path), page, box.cell_id, f"very small element: {box.w:g}x{box.h:g}"))
        if box.x < -2 or box.y < -2 or box.right > page_w + 2 or box.bottom > page_h + 2:
            issues.append(
                Issue(
                    "error",
                    str(path),
                    page,
                    box.cell_id,
                    f"element outside page bounds ({box.x:g},{box.y:g},{box.w:g},{box.h:g}) page={page_w:g}x{page_h:g}",
                )
            )
        lint_label(str(path), page, box, issues)

    lint_stencils(path, page, boxes, required_families, issues)
    lint_edges(path, page, edges, issues)
    lint_canvas_use(path, page, page_w, page_h, boxes, issues)
    if check_grid:
        lint_grid(path, page, boxes, grid_step, issues)

    visible = [box for box in boxes if not is_text_only(box)]
    for index, a in enumerate(visible):
        for b in visible[index + 1 :]:
            if a.parent != b.parent:
                continue
            if is_container(a) and contained(b, a) or is_container(b) and contained(a, b):
                continue
            if is_container(a) or is_container(b):
                continue
            overlap = intersection(a, b)
            if overlap <= 0:
                continue
            ratio = overlap / max(1.0, min(a.area, b.area))
            if ratio >= 0.15:
                issues.append(Issue("warn", str(path), page, f"{a.cell_id},{b.cell_id}", f"visual overlap ratio {ratio:.2f}"))

    return issues


def lint_file(path: Path, required_families: set[str], check_grid: bool, grid_step: float) -> list[Issue]:
    root = ET.parse(path).getroot()
    models = iter_graph_models(root)
    if not models:
        return [Issue("error", str(path), 0, "", "root must be <mxfile> or <mxGraphModel>")]
    issues: list[Issue] = []
    for page, model in enumerate(models, start=1):
        issues.extend(lint_model(path, page, model, required_families, check_grid, grid_step))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="draw.io XML files to lint visually")
    parser.add_argument("--json", action="store_true", help="Emit JSON issues")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings as well as errors")
    parser.add_argument(
        "--require-stencil-family",
        action="append",
        default=[],
        metavar="FAMILY",
        help="Require at least one mxgraph stencil family, e.g. lean_mapping, kubernetes, networks, eip. Repeat or comma-separate.",
    )
    parser.add_argument("--check-grid", action="store_true", help="Warn when vertex geometry is not aligned to the grid")
    parser.add_argument("--grid-step", type=float, default=5.0, help="Grid size for --check-grid, default 5")
    args = parser.parse_args(argv)

    required_families = parse_required_families(args.require_stencil_family)
    issues: list[Issue] = []
    for value in args.paths:
        issues.extend(lint_file(Path(value), required_families, args.check_grid, args.grid_step))

    if args.json:
        print(json.dumps([asdict(issue) for issue in issues], indent=2))
    else:
        for issue in issues:
            print(f"{issue.severity.upper()}: {issue.path} page {issue.page} cell {issue.cell_id}: {issue.message}")
        if not issues:
            print("OK: no visual lint issues")

    has_errors = any(issue.severity == "error" for issue in issues)
    has_warnings = any(issue.severity == "warn" for issue in issues)
    if has_errors or args.strict and has_warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
