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
    return (
        '<mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" math="0" shadow="0">'
        "<root>"
        '<mxCell id="0" />'
        '<mxCell id="1" parent="0" />'
        f'<mxCell id="2" value="{label}" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry width="{w}" height="{h}" as="geometry" />'
        "</mxCell>"
        "</root>"
        "</mxGraphModel>"
    )


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
                "xml": fragment(
                    "Kaizen<br>___",
                    "shape=cloud;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#D6B656;fontStyle=1;",
                    140,
                    100,
                ),
            },
            {
                "title": "Kanban card",
                "tags": "kanban pull replenishment card",
                "w": 190,
                "h": 110,
                "xml": fragment(
                    "<b>KANBAN</b><br>Part: ___<br>Qty: ___<br>Location: ___",
                    "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;align=left;verticalAlign=top;spacing=10;",
                    190,
                    110,
                ),
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
                "xml": fragment(
                    "<b>Event Bus</b><br>events / stream",
                    "shape=hexagon;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#82B366;perimeter=hexagonPerimeter2;fontColor=#173B1A;",
                    190,
                    80,
                ),
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
                "h": 80,
                "xml": fragment(
                    "<b>Data Quality</b><br>rules / checks",
                    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#3B2500;",
                    190,
                    80,
                ),
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
                "h": 80,
                "xml": fragment(
                    "<b>Observability</b><br>logs / metrics / traces",
                    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#3B2500;",
                    210,
                    80,
                ),
            },
            {
                "title": "Security control",
                "tags": "security control waf iam firewall secrets",
                "w": 190,
                "h": 80,
                "xml": fragment(
                    "<b>Security</b><br>IAM / WAF / secrets",
                    "rounded=1;whiteSpace=wrap;html=1;fillColor=#F8CECC;strokeColor=#B85450;fontColor=#4A1D1B;",
                    190,
                    80,
                ),
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
    out = {
        "title": entry.get("title", ""),
        "w": entry["w"],
        "h": entry["h"],
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
        raise ValueError(f"entry {entry.get('title', '<untitled>')} needs xml/xml_path or data/data_path")
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
