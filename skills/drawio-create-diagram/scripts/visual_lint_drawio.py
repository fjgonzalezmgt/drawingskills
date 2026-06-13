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


def lint_label(path: str, page: int, box: Box, issues: list[Issue]) -> None:
    if not box.label or is_native_icon(box):
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


def lint_model(path: Path, page: int, model: ET.Element) -> list[Issue]:
    issues: list[Issue] = []
    page_w = number(model.get("pageWidth"), 850.0)
    page_h = number(model.get("pageHeight"), 1100.0)
    boxes = extract_boxes(model)

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


def lint_file(path: Path) -> list[Issue]:
    root = ET.parse(path).getroot()
    models = iter_graph_models(root)
    if not models:
        return [Issue("error", str(path), 0, "", "root must be <mxfile> or <mxGraphModel>")]
    issues: list[Issue] = []
    for page, model in enumerate(models, start=1):
        issues.extend(lint_model(path, page, model))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="draw.io XML files to lint visually")
    parser.add_argument("--json", action="store_true", help="Emit JSON issues")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on warnings as well as errors")
    args = parser.parse_args(argv)

    issues: list[Issue] = []
    for value in args.paths:
        issues.extend(lint_file(Path(value)))

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
