#!/usr/bin/env python3
"""Generate a simple native draw.io .drawio file from a JSON node/edge spec."""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.parse
import uuid
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


def native_stencil(family: str, shape_id: str, extra: str = "") -> str:
    return f"shape=mxgraph.{family}.{shape_id};whiteSpace=wrap;html=1;{extra}"


def icon_stencil(family: str, shape_id: str, extra: str = "") -> str:
    return native_stencil(
        family,
        shape_id,
        "aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;align=center;" + extra,
    )


STYLE_PRESETS = {
    "process": "rounded=1;whiteSpace=wrap;html=1;fillColor=#EAF4FE;strokeColor=#1565C0;fontColor=#0B1F33;",
    "terminator": "rounded=1;arcSize=50;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#173B1A;",
    "decision": "rhombus;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#3B2F00;perimeter=rhombusPerimeter;",
    "data": "shape=parallelogram;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#82B366;perimeter=parallelogramPerimeter;",
    "document": "shape=document;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;",
    "database": "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;",
    "text": "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;",
    "container": "swimlane;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;startSize=28;fillColor=#F5F5F5;strokeColor=#666666;",
    "note": "shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;darkOpacity=0.05;fillColor=#FFF2CC;strokeColor=#D6B656;",
    "warning": "rounded=1;whiteSpace=wrap;html=1;fillColor=#F8CECC;strokeColor=#B85450;fontColor=#4A1D1B;",
    "success": "rounded=1;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#173B1A;",
    "actor": "shape=umlActor;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#D6B656;fontColor=#3B2F00;",
    "system": "rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0B1F33;fontStyle=1;",
    "service": "rounded=1;whiteSpace=wrap;html=1;fillColor=#EAF4FE;strokeColor=#1565C0;fontColor=#0B1F33;",
    "api": "rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0B1F33;fontStyle=1;",
    "ui": "rounded=1;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontColor=#0B1F33;",
    "worker": "rounded=1;whiteSpace=wrap;html=1;fillColor=#EAF4FE;strokeColor=#1565C0;fontColor=#0B1F33;dashed=1;",
    "queue": "shape=hexagon;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#173B1A;perimeter=hexagonPerimeter2;",
    "event-bus": "shape=hexagon;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#82B366;fontColor=#173B1A;perimeter=hexagonPerimeter2;fontStyle=1;",
    "cache": "rounded=1;whiteSpace=wrap;html=1;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#2F1A45;dashed=1;",
    "object-storage": "rounded=1;whiteSpace=wrap;html=1;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#2F1A45;",
    "data-lake": "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#2F1A45;",
    "warehouse": "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#2F1A45;fontStyle=1;",
    "analytics": "rounded=1;whiteSpace=wrap;html=1;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#2F1A45;",
    "ml": "rounded=1;whiteSpace=wrap;html=1;fillColor=#E1D5E7;strokeColor=#9673A6;fontColor=#2F1A45;fontStyle=1;",
    "cloud": "shape=cloud;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#666666;fontColor=#1F2933;",
    "network": "swimlane;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;startSize=28;fillColor=#F5F5F5;strokeColor=#666666;fontColor=#1F2933;fontStyle=1;",
    "security": "rounded=1;whiteSpace=wrap;html=1;fillColor=#F8CECC;strokeColor=#B85450;fontColor=#4A1D1B;fontStyle=1;",
    "observability": "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#D79B00;fontColor=#3B2500;",
    "external": "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#666666;fontColor=#1F2933;",
    "flowchart-process": native_stencil("flowchart", "process"),
    "flowchart-decision": native_stencil("flowchart", "decision"),
    "flowchart-terminator": native_stencil("flowchart", "terminator"),
    "flowchart-data": native_stencil("flowchart", "data"),
    "flowchart-document": native_stencil("flowchart", "document"),
    "flowchart-database": native_stencil("flowchart", "database"),
    "vsm-mrp-erp": icon_stencil("lean_mapping", "mrp_erp"),
    "vsm-kanban-post": icon_stencil("lean_mapping", "kanban_post"),
    "vsm-kaizen": icon_stencil("lean_mapping", "kaizen_lightening_burst"),
    "vsm-operator": icon_stencil("lean_mapping", "operator"),
    "vsm-quality-problem": icon_stencil("lean_mapping", "quality_problem"),
    "vsm-electronic-info-flow": native_stencil("lean_mapping", "electronic_info_flow", "aspect=fixed;"),
    "vsm-manual-info-flow": native_stencil("lean_mapping", "manual_info_flow", "aspect=fixed;"),
    "vsm-forklift": native_stencil("lean_mapping", "move_by_forklift", "aspect=fixed;"),
    "vsm-finished-goods": native_stencil("lean_mapping", "finished_goods_to_customer", "aspect=fixed;"),
    "k8s-ingress": icon_stencil("kubernetes", "ing"),
    "k8s-service": icon_stencil("kubernetes", "svc"),
    "k8s-deployment": icon_stencil("kubernetes", "deploy"),
    "k8s-pod": icon_stencil("kubernetes", "pod"),
    "k8s-configmap": icon_stencil("kubernetes", "cm"),
    "k8s-secret": icon_stencil("kubernetes", "secret"),
    "k8s-pvc": icon_stencil("kubernetes", "pvc"),
    "k8s-namespace": icon_stencil("kubernetes", "ns"),
    "k8s-node": icon_stencil("kubernetes", "node"),
    "network-cloud": icon_stencil("networks", "cloud"),
    "network-firewall": icon_stencil("networks", "firewall"),
    "network-load-balancer": icon_stencil("networks", "load_balancer"),
    "network-server": icon_stencil("networks", "server"),
    "network-web-server": icon_stencil("networks", "web_server"),
    "network-storage": icon_stencil("networks", "storage"),
    "network-users": icon_stencil("networks", "users"),
    "network-router": icon_stencil("networks", "router"),
    "network-switch": icon_stencil("networks", "switch"),
    "eip-channel-adapter": icon_stencil("eip", "channel_adapter"),
    "eip-message": icon_stencil("eip", "message_1"),
    "eip-message-store": icon_stencil("eip", "message_store"),
    "eip-transformer": icon_stencil("eip", "message_translator"),
    "eip-content-filter": icon_stencil("eip", "content_filter"),
    "eip-wire-tap": icon_stencil("eip", "wire_tap"),
    "eip-service-activator": icon_stencil("eip", "service_activator"),
    "eip-process-manager": icon_stencil("eip", "process_manager"),
}

EDGE_PRESETS = {
    "default": "endArrow=block;html=1;rounded=1;edgeStyle=orthogonalEdgeStyle;",
    "info": "endArrow=open;html=1;rounded=1;dashed=1;dashPattern=8 8;edgeStyle=orthogonalEdgeStyle;",
    "none": "endArrow=none;html=1;rounded=1;edgeStyle=orthogonalEdgeStyle;",
    "async": "endArrow=open;html=1;rounded=1;dashed=1;dashPattern=8 8;strokeColor=#2F855A;edgeStyle=orthogonalEdgeStyle;",
    "data-flow": "endArrow=block;html=1;rounded=1;strokeColor=#6C8EBF;edgeStyle=orthogonalEdgeStyle;",
    "control": "endArrow=open;html=1;rounded=1;dashed=1;dashPattern=3 3;strokeColor=#D79B00;edgeStyle=orthogonalEdgeStyle;",
}


def prettify(root: ET.Element) -> str:
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", short_empty_elements=True)


def style_for(item: dict[str, Any], presets: dict[str, str], default: str) -> str:
    if "style" in item and item["style"]:
        style = str(item["style"])
    else:
        style = presets.get(str(item.get("kind", default)), presets[default])
    extra = str(item.get("extra_style", ""))
    if extra and not extra.endswith(";"):
        extra += ";"
    if style and not style.endswith(";"):
        style += ";"
    return style + extra


def add_geometry(parent: ET.Element, attrs: dict[str, Any], points: list[dict[str, Any]] | None = None) -> None:
    geom = ET.SubElement(parent, "mxGeometry", {k: str(v) for k, v in attrs.items()})
    if points:
        arr = ET.SubElement(geom, "Array", {"as": "points"})
        for point in points:
            ET.SubElement(arr, "mxPoint", {"x": str(point["x"]), "y": str(point["y"])})


def add_node(root: ET.Element, node: dict[str, Any]) -> None:
    node_id = str(node["id"])
    label = str(node.get("label", node.get("value", "")))
    cell = ET.SubElement(
        root,
        "mxCell",
        {
            "id": node_id,
            "value": label,
            "style": style_for(node, STYLE_PRESETS, "process"),
            "vertex": "1",
            "parent": str(node.get("parent", "1")),
        },
    )
    add_geometry(
        cell,
        {
            "x": node.get("x", 0),
            "y": node.get("y", 0),
            "width": node.get("w", node.get("width", 120)),
            "height": node.get("h", node.get("height", 60)),
            "as": "geometry",
        },
    )


def add_edge(root: ET.Element, edge: dict[str, Any]) -> None:
    attrs = {
        "id": str(edge["id"]),
        "value": str(edge.get("label", edge.get("value", ""))),
        "style": style_for(edge, EDGE_PRESETS, "default"),
        "edge": "1",
        "parent": str(edge.get("parent", "1")),
    }
    if edge.get("source"):
        attrs["source"] = str(edge["source"])
    if edge.get("target"):
        attrs["target"] = str(edge["target"])
    cell = ET.SubElement(root, "mxCell", attrs)
    geom = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    for key, as_name in (("source_point", "sourcePoint"), ("target_point", "targetPoint")):
        if key in edge:
            point = edge[key]
            ET.SubElement(geom, "mxPoint", {"x": str(point["x"]), "y": str(point["y"]), "as": as_name})
    if edge.get("points"):
        arr = ET.SubElement(geom, "Array", {"as": "points"})
        for point in edge["points"]:
            ET.SubElement(arr, "mxPoint", {"x": str(point["x"]), "y": str(point["y"])})


def build_mxgraph_model(spec: dict[str, Any]) -> ET.Element:
    page = spec.get("page", {})
    model_attrs = {
        "dx": page.get("dx", 0),
        "dy": page.get("dy", 0),
        "grid": page.get("grid", 1),
        "gridSize": page.get("gridSize", 10),
        "guides": page.get("guides", 1),
        "tooltips": page.get("tooltips", 1),
        "connect": page.get("connect", 1),
        "arrows": page.get("arrows", 1),
        "fold": page.get("fold", 1),
        "page": page.get("page", 1),
        "pageScale": page.get("pageScale", 1),
        "pageWidth": page.get("width", page.get("pageWidth", 1100)),
        "pageHeight": page.get("height", page.get("pageHeight", 850)),
        "math": page.get("math", 0),
        "shadow": page.get("shadow", 0),
    }
    model = ET.Element("mxGraphModel", {k: str(v) for k, v in model_attrs.items()})
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    for node in spec.get("nodes", []):
        add_node(root, node)
    for edge in spec.get("edges", []):
        add_edge(root, edge)
    return model


def build_mxfile(spec: dict[str, Any]) -> ET.Element:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": now,
            "agent": "Codex drawio-create-diagram",
            "version": "26.0.0",
            "type": "device",
        },
    )
    page = spec.get("page", {})
    diagram = ET.SubElement(
        mxfile,
        "diagram",
        {"id": str(page.get("id", f"page-{uuid.uuid4().hex[:8]}")), "name": str(page.get("name", spec.get("title", "Page-1")))},
    )
    diagram.append(build_mxgraph_model(spec))
    return mxfile


def validate_spec(spec: dict[str, Any]) -> None:
    ids: set[str] = set()
    for group_name in ("nodes", "edges"):
        for item in spec.get(group_name, []):
            if "id" not in item:
                raise ValueError(f"{group_name} entry is missing id")
            item_id = str(item["id"])
            if item_id in {"0", "1"}:
                raise ValueError(f"{item_id} is reserved for draw.io structural cells")
            if item_id in ids:
                raise ValueError(f"duplicate id: {item_id}")
            ids.add(item_id)
    for edge in spec.get("edges", []):
        for endpoint in ("source", "target"):
            if edge.get(endpoint) and str(edge[endpoint]) not in ids:
                raise ValueError(f"edge {edge['id']} references unknown {endpoint}: {edge[endpoint]}")


def editor_url(xml: str) -> str:
    encoded = urllib.parse.quote(xml, safe="")
    compressor = zlib.compressobj(level=9, wbits=-15)
    compressed = compressor.compress(encoded.encode("utf-8")) + compressor.flush()
    payload = {
        "type": "xml",
        "compressed": True,
        "data": base64.b64encode(compressed).decode("ascii"),
        "effect": "pop",
    }
    return "https://app.diagrams.net/?pv=0&grid=0#create=" + urllib.parse.quote(json.dumps(payload, separators=(",", ":")))


def sample_spec() -> dict[str, Any]:
    return {
        "title": "Sample process",
        "page": {"name": "Process", "width": 1100, "height": 850},
        "nodes": [
            {"id": "start", "label": "Start", "kind": "terminator", "x": 80, "y": 120, "w": 120, "h": 50},
            {"id": "step1", "label": "Receive request", "kind": "process", "x": 270, "y": 115, "w": 150, "h": 60},
            {"id": "decision", "label": "Complete?", "kind": "decision", "x": 500, "y": 105, "w": 120, "h": 80},
            {"id": "end", "label": "Done", "kind": "terminator", "x": 720, "y": 120, "w": 120, "h": 50},
            {"id": "note1", "label": "Add cycle time or owner metadata as needed.", "kind": "note", "x": 270, "y": 230, "w": 220, "h": 80},
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "step1"},
            {"id": "e2", "source": "step1", "target": "decision"},
            {"id": "e3", "source": "decision", "target": "end", "label": "Yes"},
            {"id": "e4", "source": "decision", "target": "step1", "label": "No", "kind": "info"},
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", nargs="?", help="JSON spec path. Omit with --sample.")
    parser.add_argument("output", nargs="?", default="diagram.drawio", help="Output .drawio path.")
    parser.add_argument("--sample", nargs="?", const="diagram.drawio", help="Use a built-in sample spec, optionally writing to this output path.")
    parser.add_argument("--mxgraph-only", action="store_true", help="Write only the mxGraphModel fragment.")
    parser.add_argument("--print-url", action="store_true", help="Print a diagrams.net editor URL.")
    args = parser.parse_args(argv)

    if args.sample is not None:
        spec = sample_spec()
        output = args.sample
    else:
        if not args.spec:
            parser.error("spec is required unless --sample is used")
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        output = args.output

    validate_spec(spec)
    root = build_mxgraph_model(spec) if args.mxgraph_only else build_mxfile(spec)
    xml = prettify(root)
    Path(output).write_text(xml, encoding="utf-8")
    if args.print_url:
        print(editor_url(xml))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
