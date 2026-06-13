#!/usr/bin/env python3
"""Create editable draw.io templates for common Lean Six Sigma diagrams."""

from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


PALETTE = {
    "process": ("#D5E8D4", "#82B366"),
    "info": ("#DAE8FC", "#6C8EBF"),
    "waste": ("#F8CECC", "#B85450"),
    "risk": ("#FFF2CC", "#D6B656"),
    "neutral": ("#F5F5F5", "#666666"),
    "white": ("#FFFFFF", "#666666"),
}


def style(fill: str, stroke: str, extra: str = "") -> str:
    base = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontColor=#1F2933;"
    return base + extra


def stencil(family: str, shape_id: str, extra: str = "") -> str:
    base = f"shape=mxgraph.{family}.{shape_id};whiteSpace=wrap;html=1;"
    return base + extra


LEAN = {
    "finished_goods_to_customer": stencil("lean_mapping", "finished_goods_to_customer", "aspect=fixed;"),
    "go_see_production_scheduling": stencil("lean_mapping", "go_see_production_scheduling", "aspect=fixed;"),
    "kaizen_lightening_burst": stencil("lean_mapping", "kaizen_lightening_burst", "aspect=fixed;"),
    "kanban_post": stencil("lean_mapping", "kanban_post", "aspect=fixed;"),
    "load_leveling": stencil("lean_mapping", "load_leveling", "aspect=fixed;"),
    "move_by_forklift": stencil("lean_mapping", "move_by_forklift", "aspect=fixed;"),
    "mrp_erp": stencil("lean_mapping", "mrp_erp", "aspect=fixed;"),
    "operator": stencil("lean_mapping", "operator", "aspect=fixed;"),
    "quality_problem": stencil("lean_mapping", "quality_problem", "aspect=fixed;"),
    "verbal": stencil("lean_mapping", "verbal", "aspect=fixed;"),
    "airplane_7": stencil("lean_mapping", "airplane_7", "aspect=fixed;"),
    "manual_info_flow": stencil("lean_mapping", "manual_info_flow", "aspect=fixed;"),
    "electronic_info_flow": stencil("lean_mapping", "electronic_info_flow", "aspect=fixed;"),
}


def graph(title: str, width: int = 1400, height: int = 900) -> tuple[ET.Element, ET.Element]:
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "agent": "Codex drawio-lean-six-sigma",
            "version": "26.0.0",
            "type": "device",
        },
    )
    diagram = ET.SubElement(mxfile, "diagram", {"id": f"page-{uuid.uuid4().hex[:8]}", "name": title[:40] or "Lean Six Sigma"})
    model = ET.SubElement(
        diagram,
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
            "page": "1",
            "pageScale": "1",
            "pageWidth": str(width),
            "pageHeight": str(height),
            "math": "0",
            "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    return mxfile, root


def vertex(root: ET.Element, cell_id: str, label: str, x: int, y: int, w: int, h: int, cell_style: str) -> None:
    cell = ET.SubElement(root, "mxCell", {"id": cell_id, "value": label, "style": cell_style, "vertex": "1", "parent": "1"})
    ET.SubElement(cell, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})


def edge(root: ET.Element, cell_id: str, source: str, target: str, label: str = "", extra: str = "") -> None:
    edge_style = "endArrow=block;html=1;rounded=1;edgeStyle=orthogonalEdgeStyle;" + extra
    cell = ET.SubElement(
        root,
        "mxCell",
        {"id": cell_id, "value": label, "style": edge_style, "edge": "1", "parent": "1", "source": source, "target": target},
    )
    ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})


def floating_edge(root: ET.Element, cell_id: str, x1: int, y1: int, x2: int, y2: int, label: str = "", extra: str = "") -> None:
    edge_style = "endArrow=block;html=1;rounded=1;" + extra
    cell = ET.SubElement(root, "mxCell", {"id": cell_id, "value": label, "style": edge_style, "edge": "1", "parent": "1"})
    geom = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    ET.SubElement(geom, "mxPoint", {"x": str(x1), "y": str(y1), "as": "sourcePoint"})
    ET.SubElement(geom, "mxPoint", {"x": str(x2), "y": str(y2), "as": "targetPoint"})


def title(root: ET.Element, text: str, width: int) -> None:
    vertex(root, "title", text, 40, 24, width - 80, 44, "text;html=1;strokeColor=none;fillColor=none;fontSize=24;fontStyle=1;align=left;verticalAlign=middle;")


def build_sipoc(name: str) -> ET.Element:
    mxfile, root = graph(name, 1400, 850)
    title(root, name, 1400)
    headers = ["Suppliers", "Inputs", "Process", "Outputs", "Customers"]
    fill, stroke = PALETTE["info"]
    body_fill, body_stroke = PALETTE["white"]
    x0, y0, col_w, gap = 50, 110, 250, 12
    for i, header in enumerate(headers):
        x = x0 + i * (col_w + gap)
        vertex(root, f"h{i}", header, x, y0, col_w, 52, style(fill, stroke, "fontStyle=1;fontSize=16;"))
        body = "<br>".join([f"{header[:-1] if header.endswith('s') else header} 1", "Item 2", "Item 3", "Item 4"])
        vertex(root, f"b{i}", body, x, y0 + 64, col_w, 430, style(body_fill, body_stroke, "align=left;verticalAlign=top;spacing=14;"))
    vertex(root, "ctq", "CTQ / VOC notes<br>Need, metric, target, source", 50, 640, 1320, 90, style(*PALETTE["risk"], extra="align=left;verticalAlign=top;spacing=12;"))
    return mxfile


def build_fishbone(name: str) -> ET.Element:
    mxfile, root = graph(name, 1400, 850)
    title(root, name, 1400)
    vertex(root, "effect", "Effect / Problem statement", 1070, 360, 260, 95, style(*PALETTE["waste"], extra="fontStyle=1;fontSize=16;"))
    floating_edge(root, "spine", 150, 405, 1070, 405, "", "endArrow=block;strokeWidth=3;")
    categories = [
        ("people", "People", 250, 180, 360, 340),
        ("machine", "Machine / Equipment", 470, 180, 560, 340),
        ("method", "Method / Process", 700, 180, 750, 340),
        ("material", "Material", 250, 630, 360, 470),
        ("measure", "Measurement", 470, 630, 560, 470),
        ("env", "Environment", 700, 630, 750, 470),
    ]
    for idx, (cid, label, x, y, x2, y2) in enumerate(categories):
        vertex(root, cid, f"<b>{label}</b><br>Cause 1<br>Cause 2<br>Cause 3", x, y - 55, 190, 90, style(*PALETTE["neutral"], extra="align=left;verticalAlign=top;spacing=8;"))
        floating_edge(root, f"bone{idx}", x2, y2, x2 + 120, 405, "", "endArrow=none;strokeWidth=2;")
    return mxfile


def build_dmaic(name: str) -> ET.Element:
    mxfile, root = graph(name, 1400, 650)
    title(root, name, 1400)
    phases = [
        ("Define", "Problem, customer, CTQ, charter"),
        ("Measure", "Baseline, data plan, MSA"),
        ("Analyze", "Root causes, verified drivers"),
        ("Improve", "Countermeasures, pilot"),
        ("Control", "Control plan, handoff"),
    ]
    x, y, w, h = 70, 180, 230, 145
    for i, (phase, notes) in enumerate(phases):
        sid = f"p{i}"
        vertex(root, sid, f"<b>{phase}</b><br>{notes}", x + i * (w + 25), y, w, h, "shape=singleArrow;whiteSpace=wrap;html=1;fillColor=#DAE8FC;strokeColor=#6C8EBF;fontSize=14;fontColor=#1F2933;")
    vertex(root, "deliverables", "Key deliverables / tollgate evidence", 70, 410, 1230, 90, style(*PALETTE["risk"], extra="align=left;verticalAlign=top;spacing=12;"))
    return mxfile


def build_pdca(name: str) -> ET.Element:
    mxfile, root = graph(name, 900, 850)
    title(root, name, 900)
    boxes = [
        ("plan", "Plan<br>Target, hypothesis, plan", 130, 160),
        ("do", "Do<br>Pilot, collect evidence", 520, 160),
        ("check", "Check<br>Compare result to target", 520, 520),
        ("act", "Act<br>Standardize or adjust", 130, 520),
    ]
    for cid, label, x, y in boxes:
        vertex(root, cid, label, x, y, 240, 120, style(*PALETTE["process"], extra="fontSize=15;"))
    edge(root, "e1", "plan", "do")
    edge(root, "e2", "do", "check")
    edge(root, "e3", "check", "act")
    edge(root, "e4", "act", "plan")
    vertex(root, "center", "Learning loop", 330, 365, 230, 90, style(*PALETTE["info"], extra="fontStyle=1;fontSize=16;"))
    return mxfile


def build_vsm(name: str) -> ET.Element:
    mxfile, root = graph(name, 1600, 1000)
    title(root, name, 1600)
    vertex(root, "supplier", "Supplier", 70, 270, 150, 80, style(*PALETTE["neutral"], extra="fontStyle=1;"))
    vertex(root, "forklift", "", 230, 285, 80, 85, LEAN["move_by_forklift"])
    vertex(root, "customer", "Customer<br>Demand: ___ / day<br>Takt: ___", 1360, 270, 170, 100, style(*PALETTE["neutral"], extra="fontStyle=1;"))
    vertex(root, "ship_customer", "", 1255, 300, 95, 30, LEAN["finished_goods_to_customer"])
    vertex(root, "control", "MRP / ERP<br>Production Control", 720, 95, 110, 150, LEAN["mrp_erp"] + "verticalLabelPosition=bottom;verticalAlign=top;")
    vertex(root, "heijunka", "", 865, 145, 120, 36, LEAN["load_leveling"])
    vertex(root, "schedule", "Schedule", 505, 145, 180, 22, LEAN["electronic_info_flow"])
    vertex(root, "forecast", "Forecast", 1010, 145, 180, 22, LEAN["electronic_info_flow"])
    processes = ["Process 1", "Process 2", "Process 3", "Process 4"]
    prev = "supplier"
    for i, label in enumerate(processes):
        x = 320 + i * 245
        pid = f"proc{i}"
        vertex(root, pid, label, x, 290, 160, 80, style(*PALETTE["process"], extra="fontStyle=1;"))
        vertex(root, f"data{i}", "CT: ___<br>C/O: ___<br>Uptime: ___<br>FPY: ___", x, 390, 160, 95, style(*PALETTE["white"], extra="fontSize=11;align=left;verticalAlign=top;spacing=8;"))
        vertex(root, f"operator{i}", "", x + 42, 505, 70, 60, LEAN["operator"])
        edge(root, f"mat{i}", prev, pid, "", "strokeWidth=2;")
        if i:
            vertex(root, f"inv{i}", "I<br>___ pcs<br>___ days", x - 65, 315, 55, 70, "triangle;whiteSpace=wrap;html=1;fillColor=#F8CECC;strokeColor=#B85450;fontSize=11;")
        prev = pid
    edge(root, "mat_end", prev, "customer", "", "strokeWidth=2;")
    edge(root, "info1", "forecast", "customer", "", "endArrow=open;dashed=1;dashPattern=8 8;strokeColor=#6C8EBF;")
    edge(root, "info2", "schedule", "supplier", "", "endArrow=open;dashed=1;dashPattern=8 8;strokeColor=#6C8EBF;")
    vertex(root, "kanban", "", 645, 235, 48, 95, LEAN["kanban_post"])
    vertex(root, "kaizen", "", 1020, 220, 110, 55, LEAN["kaizen_lightening_burst"])
    vertex(root, "quality", "", 1190, 505, 70, 80, LEAN["quality_problem"])
    vertex(root, "timeline_wait", "Waiting / queue time: ___", 320, 680, 840, 45, style(*PALETTE["waste"], extra="fontStyle=1;"))
    vertex(root, "timeline_va", "Value-added time: ___", 320, 735, 840, 45, style(*PALETTE["process"], extra="fontStyle=1;"))
    vertex(root, "summary", "Lead time: ___    Process time: ___    VA ratio: ___%", 70, 850, 1460, 55, style(*PALETTE["risk"], extra="fontStyle=1;fontSize=16;"))
    return mxfile


def build_swimlane(name: str) -> ET.Element:
    mxfile, root = graph(name, 1400, 900)
    title(root, name, 1400)
    lanes = ["Customer", "Operations", "Quality", "System"]
    y0, lane_h = 110, 150
    for i, lane in enumerate(lanes):
        y = y0 + i * lane_h
        vertex(root, f"lane{i}", lane, 50, y, 1280, lane_h, "swimlane;whiteSpace=wrap;html=1;horizontal=0;startSize=34;container=1;collapsible=0;recursiveResize=0;fillColor=#F5F5F5;strokeColor=#666666;fontStyle=1;")
    steps = [
        ("s1", "Submit request", 170, y0 + 35, "process"),
        ("s2", "Review request", 390, y0 + lane_h + 35, "process"),
        ("s3", "Complete?", 620, y0 + lane_h + 25, "decision"),
        ("s4", "Inspect", 850, y0 + 2 * lane_h + 35, "process"),
        ("s5", "Record result", 1070, y0 + 3 * lane_h + 35, "process"),
    ]
    for sid, label, x, y, kind in steps:
        if kind == "decision":
            cell_style = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#D6B656;perimeter=rhombusPerimeter;"
            vertex(root, sid, label, x, y, 120, 90, cell_style)
        else:
            vertex(root, sid, label, x, y, 150, 65, style(*PALETTE["process"]))
    for i, (source, target) in enumerate([("s1", "s2"), ("s2", "s3"), ("s3", "s4"), ("s4", "s5")]):
        edge(root, f"e{i}", source, target)
    edge(root, "rework", "s3", "s2", "No", "dashed=1;dashPattern=8 8;")
    return mxfile


def build_a3(name: str) -> ET.Element:
    mxfile, root = graph(name, 1400, 1000)
    title(root, name, 1400)
    sections = [
        ("background", "Background", 50, 110, 410, 150),
        ("current", "Current state", 490, 110, 410, 260),
        ("target", "Target condition", 930, 110, 410, 150),
        ("problem", "Problem statement", 50, 290, 410, 150),
        ("rootcause", "Root cause analysis", 50, 470, 410, 350),
        ("counter", "Countermeasures", 490, 400, 410, 220),
        ("plan", "Implementation plan", 930, 290, 410, 330),
        ("followup", "Results / follow-up", 490, 650, 850, 170),
    ]
    for sid, label, x, y, w, h in sections:
        vertex(root, sid, f"<b>{label}</b><br><br>-", x, y, w, h, style(*PALETTE["white"], extra="align=left;verticalAlign=top;spacing=12;"))
    return mxfile


BUILDERS = {
    "sipoc": build_sipoc,
    "fishbone": build_fishbone,
    "dmaic": build_dmaic,
    "pdca": build_pdca,
    "vsm": build_vsm,
    "swimlane": build_swimlane,
    "a3": build_a3,
}


def write_xml(root: ET.Element, path: Path) -> None:
    ET.indent(root, space="  ")
    path.write_text(ET.tostring(root, encoding="unicode", short_empty_elements=True), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", choices=sorted(BUILDERS), required=True, help="Template type")
    parser.add_argument("--output", required=True, help="Output .drawio path")
    parser.add_argument("--title", default="", help="Diagram title")
    args = parser.parse_args(argv)
    title_text = args.title or f"{args.type.upper()} template"
    root = BUILDERS[args.type](title_text)
    write_xml(root, Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
