#!/usr/bin/env python3
"""Build a draw.io <mxlibrary> custom shape library."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
import urllib.parse
from pathlib import Path
from xml.etree import ElementTree as ET


def fragment(label: str, style: str, w: int, h: int) -> str:
    model = ET.Element(
        "mxGraphModel",
        {
            "dx": "0",
            "dy": "0",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "0",
            "math": "0",
            "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    cell = ET.SubElement(root, "mxCell", {"id": "2", "value": label, "style": style, "vertex": "1", "parent": "1"})
    ET.SubElement(cell, "mxGeometry", {"width": str(w), "height": str(h), "as": "geometry"})
    return ET.tostring(model, encoding="unicode", short_empty_elements=True)


def native_fragment(label: str, family: str, shape_id: str, w: int, h: int, extra_style: str = "") -> str:
    return fragment(label, f"shape=mxgraph.{family}.{shape_id};whiteSpace=wrap;html=1;{extra_style}", w, h)


def positive_int(value: object, field: str, title: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"entry {title!r} has invalid {field}: {value!r}") from exc
    if number <= 0:
        raise ValueError(f"entry {title!r} has non-positive {field}: {number}")
    return number


def validate_xml_fragment(xml: str, title: str) -> None:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise ValueError(f"entry {title!r} has invalid XML fragment: {exc}") from exc
    if root.tag not in {"mxGraphModel", "mxfile", "mxCell", "object"}:
        raise ValueError(f"entry {title!r} XML fragment root should be mxGraphModel, mxfile, mxCell, or object")


def sample_lean_spec() -> dict:
    return {
        "tags": "lean six sigma quality vsm kaizen sipoc kanban ctq waste",
        "entries": [
            {
                "title": "CTQ card",
                "tags": "ctq critical to quality customer",
                "w": 180,
                "h": 90,
                "xml": fragment(
                    "<b>CTQ</b><br>Metric: ___<br>Target: ___",
                    "rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;align=left;verticalAlign=top;spacing=10;",
                    180,
                    90,
                ),
            },
            {
                "title": "Waste tag",
                "tags": "muda waste delay defect rework",
                "w": 170,
                "h": 70,
                "xml": fragment(
                    "<b>Waste</b><br>Type: ___",
                    "rounded=1;whiteSpace=wrap;html=1;fillColor=#F8CECC;strokeColor=#B85450;align=left;verticalAlign=top;spacing=10;",
                    170,
                    70,
                ),
            },
            {
                "title": "Kaizen burst",
                "tags": "kaizen improvement opportunity burst",
                "w": 140,
                "h": 100,
                "xml": native_fragment("Kaizen<br>___", "lean_mapping", "kaizen_lightening_burst", 140, 100, "aspect=fixed;"),
            },
            {
                "title": "Kanban post",
                "tags": "kanban post pull replenishment card",
                "w": 80,
                "h": 130,
                "xml": native_fragment("Kanban", "lean_mapping", "kanban_post", 80, 130, "aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;"),
            },
            {
                "title": "VSM data box",
                "tags": "vsm value stream map data box cycle time",
                "w": 170,
                "h": 105,
                "xml": fragment(
                    "CT: ___<br>C/O: ___<br>Uptime: ___<br>FPY: ___",
                    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;align=left;verticalAlign=top;spacing=8;fontSize=11;",
                    170,
                    105,
                ),
            },
            {
                "title": "Inventory triangle",
                "tags": "vsm inventory queue wait wip",
                "w": 80,
                "h": 80,
                "xml": fragment(
                    "I<br>___",
                    "triangle;whiteSpace=wrap;html=1;fillColor=#F8CECC;strokeColor=#B85450;fontStyle=1;",
                    80,
                    80,
                ),
            },
            {
                "title": "MRP ERP",
                "tags": "vsm production control mrp erp schedule",
                "w": 100,
                "h": 140,
                "xml": native_fragment("MRP / ERP", "lean_mapping", "mrp_erp", 100, 140, "aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;"),
            },
            {
                "title": "Electronic info flow",
                "tags": "vsm information flow electronic forecast schedule",
                "w": 170,
                "h": 32,
                "xml": native_fragment("Electronic info", "lean_mapping", "electronic_info_flow", 170, 32, "aspect=fixed;"),
            },
            {
                "title": "Operator",
                "tags": "vsm operator labor person",
                "w": 100,
                "h": 95,
                "xml": native_fragment("Operator", "lean_mapping", "operator", 100, 95, "aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;"),
            },
            {
                "title": "Quality problem",
                "tags": "vsm quality defect problem",
                "w": 95,
                "h": 110,
                "xml": native_fragment("Quality", "lean_mapping", "quality_problem", 95, 110, "aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;"),
            },
        ],
    }


def sample_architecture_spec() -> dict:
    return {
        "tags": "software architecture infrastructure analytics cloud data mlops api service topology",
        "entries": [
            {
                "title": "System boundary",
                "tags": "c4 boundary system context container",
                "w": 260,
                "h": 160,
                "xml": fragment(
                    "System boundary",
                    "swimlane;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;startSize=28;fillColor=#F5F5F5;strokeColor=#666666;fontStyle=1;",
                    260,
                    160,
                ),
            },
            {
                "title": "API service",
                "tags": "api service microservice rest grpc",
                "w": 180,
                "h": 80,
                "xml": fragment(
                    "<b>API Service</b><br>REST / gRPC",
                    "rounded=1;whiteSpace=wrap;html=1;fillColor=#EAF4FE;strokeColor=#1565C0;fontColor=#0B1F33;",
                    180,
                    80,
                ),
            },
            {
                "title": "Async worker",
                "tags": "worker job async batch compute",
                "w": 180,
                "h": 80,
                "xml": fragment(
                    "<b>Worker</b><br>async job",
                    "rounded=1;whiteSpace=wrap;html=1;fillColor=#EAF4FE;strokeColor=#1565C0;dashed=1;fontColor=#0B1F33;",
                    180,
                    80,
                ),
            },
            {
                "title": "Event bus",
                "tags": "queue event stream kafka pubsub messaging",
                "w": 190,
                "h": 80,
                "xml": native_fragment("Event Bus", "eip", "message_1", 190, 80, "aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;"),
            },
            {
                "title": "Warehouse",
                "tags": "warehouse lakehouse analytics database",
                "w": 180,
                "h": 95,
                "xml": fragment(
                    "<b>Warehouse</b><br>curated data",
                    "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#2F1A45;",
                    180,
                    95,
                ),
            },
            {
                "title": "Data quality gate",
                "tags": "data quality validation dq control",
                "w": 190,
                "h": 100,
                "xml": native_fragment("Data Quality", "eip", "content_filter", 190, 100, "aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;"),
            },
            {
                "title": "Governance catalog",
                "tags": "catalog governance lineage metadata privacy",
                "w": 210,
                "h": 80,
                "xml": fragment(
                    "<b>Catalog</b><br>lineage / policies",
                    "rounded=1;whiteSpace=wrap;html=1;fillColor=#F8CECC;strokeColor=#B85450;fontColor=#4A1D1B;",
                    210,
                    80,
                ),
            },
            {
                "title": "Feature store",
                "tags": "mlops feature store model registry ml ai",
                "w": 190,
                "h": 80,
                "xml": fragment(
                    "<b>Feature Store</b><br>training / serving",
                    "rounded=1;whiteSpace=wrap;html=1;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#2F1A45;",
                    190,
                    80,
                ),
            },
            {
                "title": "Observability",
                "tags": "observability monitoring logs metrics traces alerts",
                "w": 210,
                "h": 100,
                "xml": native_fragment("Observability", "eip", "wire_tap", 210, 100, "aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;"),
            },
            {
                "title": "Security control",
                "tags": "security control waf iam firewall secrets",
                "w": 130,
                "h": 130,
                "xml": native_fragment("Firewall / Security", "networks", "firewall", 130, 130, "aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;"),
            },
        ],
    }


def file_to_data_uri(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        suffix = path.suffix.lower()
        if suffix == ".svg":
            mime = "image/svg+xml"
        elif suffix in {".jpg", ".jpeg"}:
            mime = "image/jpeg"
        elif suffix == ".gif":
            mime = "image/gif"
        else:
            mime = "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def normalize_entry(entry: dict, base_dir: Path) -> dict:
    title = str(entry.get("title", ""))
    if not title:
        raise ValueError("library entries need a title")
    out = {
        "title": title,
        "w": positive_int(entry.get("w"), "w", title),
        "h": positive_int(entry.get("h"), "h", title),
    }
    if entry.get("tags"):
        out["tags"] = entry["tags"]
    if entry.get("xml_path"):
        out["xml"] = (base_dir / entry["xml_path"]).read_text(encoding="utf-8")
    elif entry.get("xml"):
        out["xml"] = entry["xml"]
    elif entry.get("data_path"):
        out["data"] = file_to_data_uri(base_dir / entry["data_path"])
    elif entry.get("data"):
        out["data"] = entry["data"]
    else:
        raise ValueError(f"entry {title!r} needs xml/xml_path or data/data_path")
    if out.get("xml"):
        validate_xml_fragment(str(out["xml"]), title)
    if out.get("data") and not str(out["data"]).startswith("data:"):
        raise ValueError(f"entry {title!r} data should be a data URI")
    for key in ("aspect", "style"):
        if entry.get(key):
            out[key] = entry[key]
    return out


def build_library(spec: dict, base_dir: Path) -> ET.Element:
    attrs = {}
    if spec.get("tags"):
        attrs["tags"] = str(spec["tags"])
    root = ET.Element("mxlibrary", attrs)
    entries = [normalize_entry(entry, base_dir) for entry in spec.get("entries", [])]
    if not entries:
        raise ValueError("library spec has no entries")
    root.text = json.dumps(entries, ensure_ascii=False, separators=(",", ":"))
    return root


def write_library(spec: dict, base_dir: Path, output: Path) -> None:
    root = build_library(spec, base_dir)
    output.write_text(ET.tostring(root, encoding="unicode", short_empty_elements=True), encoding="utf-8")


def load_url(raw_url: str) -> str:
    return "https://app.diagrams.net/?splash=0&clibs=U" + urllib.parse.quote(raw_url, safe="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", nargs="?", help="Library JSON spec path")
    parser.add_argument("output", nargs="?", help="Output .xml library path")
    parser.add_argument("--sample-lean", metavar="OUTPUT", help="Write a built-in Lean Six Sigma sample library")
    parser.add_argument("--sample-architecture", metavar="OUTPUT", help="Write a built-in software/infrastructure/analytics sample library")
    parser.add_argument("--hosted-url", help="Print a diagrams.net clibs URL for a hosted raw library URL")
    args = parser.parse_args(argv)

    if args.hosted_url:
        print(load_url(args.hosted_url))
        return 0
    if args.sample_lean:
        write_library(sample_lean_spec(), Path.cwd(), Path(args.sample_lean))
        return 0
    if args.sample_architecture:
        write_library(sample_architecture_spec(), Path.cwd(), Path(args.sample_architecture))
        return 0
    if not args.spec or not args.output:
        parser.error("provide spec and output, --sample-lean OUTPUT, or --hosted-url URL")
    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    write_library(spec, spec_path.parent, Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
