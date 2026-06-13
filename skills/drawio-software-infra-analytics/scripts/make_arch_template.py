#!/usr/bin/env python3
"""Create editable draw.io templates for software, infrastructure, and analytics architecture diagrams."""

from __future__ import annotations

import argparse
import uuid
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


COLORS = {
    "actor": ("#FFF2CC", "#D6B656"),
    "app": ("#DAE8FC", "#6C8EBF"),
    "service": ("#EAF4FE", "#1565C0"),
    "data": ("#E1D5E7", "#9673A6"),
    "event": ("#D5E8D4", "#82B366"),
    "security": ("#F8CECC", "#B85450"),
    "ops": ("#FFE6CC", "#D79B00"),
    "neutral": ("#F5F5F5", "#666666"),
    "white": ("#FFFFFF", "#666666"),
}


def style(kind: str, extra: str = "") -> str:
    fill, stroke = COLORS[kind]
    base = f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontColor=#1F2933;"
    return base + extra


def graph(title: str, width: int = 1600, height: int = 1000) -> tuple[ET.Element, ET.Element]:
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "agent": "Codex drawio-software-infra-analytics",
            "version": "26.0.0",
            "type": "device",
        },
    )
    diagram = ET.SubElement(mxfile, "diagram", {"id": f"page-{uuid.uuid4().hex[:8]}", "name": title[:40] or "Architecture"})
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


def edge(root: ET.Element, cell_id: str, source: str, target: str, label: str = "", kind: str = "sync") -> None:
    if kind == "async":
        edge_style = "endArrow=open;html=1;rounded=1;dashed=1;dashPattern=8 8;strokeColor=#2F855A;edgeStyle=orthogonalEdgeStyle;"
    elif kind == "meta":
        edge_style = "endArrow=open;html=1;rounded=1;dashed=1;dashPattern=3 3;strokeColor=#D79B00;edgeStyle=orthogonalEdgeStyle;"
    elif kind == "none":
        edge_style = "endArrow=none;html=1;rounded=1;edgeStyle=orthogonalEdgeStyle;"
    else:
        edge_style = "endArrow=block;html=1;rounded=1;strokeColor=#1F2933;edgeStyle=orthogonalEdgeStyle;"
    cell = ET.SubElement(
        root,
        "mxCell",
        {"id": cell_id, "value": label, "style": edge_style, "edge": "1", "parent": "1", "source": source, "target": target},
    )
    ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})


def floating_edge(root: ET.Element, cell_id: str, x1: int, y1: int, x2: int, y2: int, label: str = "", edge_style: str = "") -> None:
    style_value = edge_style or "endArrow=block;html=1;rounded=1;strokeColor=#1F2933;"
    cell = ET.SubElement(root, "mxCell", {"id": cell_id, "value": label, "style": style_value, "edge": "1", "parent": "1"})
    geom = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    ET.SubElement(geom, "mxPoint", {"x": str(x1), "y": str(y1), "as": "sourcePoint"})
    ET.SubElement(geom, "mxPoint", {"x": str(x2), "y": str(y2), "as": "targetPoint"})


def title(root: ET.Element, text: str, width: int) -> None:
    vertex(root, "title", text, 40, 24, width - 80, 44, "text;html=1;strokeColor=none;fillColor=none;fontSize=24;fontStyle=1;align=left;verticalAlign=middle;")


def boundary(root: ET.Element, cell_id: str, label: str, x: int, y: int, w: int, h: int) -> None:
    vertex(root, cell_id, label, x, y, w, h, "swimlane;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;startSize=28;fillColor=#F5F5F5;strokeColor=#666666;fontStyle=1;")


def build_c4_context(name: str) -> ET.Element:
    mxfile, root = graph(name, 1400, 850)
    title(root, name, 1400)
    boundary(root, "boundary", "System landscape", 300, 120, 780, 520)
    vertex(root, "user", "Customer / User", 80, 300, 160, 80, style("actor", "shape=umlActor;fontStyle=1;"))
    vertex(root, "system", "System of Interest<br><span style=\"font-size:11px\">Core product or platform</span>", 580, 310, 220, 100, style("service", "fontStyle=1;fontSize=15;"))
    vertex(root, "admin", "Admin / Operator", 80, 470, 160, 80, style("actor", "shape=umlActor;fontStyle=1;"))
    vertex(root, "external1", "Payment / External API", 1130, 240, 190, 80, style("app"))
    vertex(root, "external2", "Identity Provider", 1130, 390, 190, 80, style("security"))
    vertex(root, "analytics", "Analytics Platform", 1130, 540, 190, 80, style("data"))
    edge(root, "e1", "user", "system", "Uses")
    edge(root, "e2", "admin", "system", "Operates")
    edge(root, "e3", "system", "external1", "API calls")
    edge(root, "e4", "system", "external2", "OIDC / SSO")
    edge(root, "e5", "system", "analytics", "Events", "async")
    return mxfile


def build_c4_container(name: str) -> ET.Element:
    mxfile, root = graph(name, 1500, 900)
    title(root, name, 1500)
    boundary(root, "boundary", "System boundary", 260, 120, 900, 610)
    vertex(root, "user", "User", 70, 340, 130, 70, style("actor", "shape=umlActor;fontStyle=1;"))
    vertex(root, "web", "Web / Mobile UI", 340, 210, 180, 80, style("app", "fontStyle=1;"))
    vertex(root, "api", "API Gateway", 610, 210, 180, 80, style("service", "fontStyle=1;"))
    vertex(root, "svc", "Domain Service", 610, 370, 180, 80, style("service", "fontStyle=1;"))
    vertex(root, "worker", "Async Worker", 340, 520, 180, 80, style("service"))
    vertex(root, "queue", "Queue / Event Bus", 610, 520, 180, 80, style("event", "shape=hexagon;perimeter=hexagonPerimeter2;"))
    vertex(root, "db", "Operational DB", 870, 370, 170, 90, "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;fontStyle=1;")
    vertex(root, "cache", "Cache", 870, 520, 170, 70, style("data"))
    vertex(root, "external", "External System", 1240, 320, 180, 80, style("app"))
    edge(root, "e1", "user", "web", "HTTPS")
    edge(root, "e2", "web", "api", "REST/GraphQL")
    edge(root, "e3", "api", "svc", "Internal API")
    edge(root, "e4", "svc", "db", "SQL")
    edge(root, "e5", "svc", "queue", "Publishes", "async")
    edge(root, "e6", "queue", "worker", "Consumes", "async")
    edge(root, "e7", "worker", "cache", "Updates")
    edge(root, "e8", "svc", "external", "API")
    return mxfile


def build_sequence(name: str) -> ET.Element:
    mxfile, root = graph(name, 1400, 850)
    title(root, name, 1400)
    actors = [("client", "Client", 120), ("api", "API", 370), ("service", "Service", 620), ("queue", "Queue", 870), ("db", "Database", 1120)]
    for cid, label, x in actors:
        vertex(root, cid, label, x, 120, 150, 50, style("app" if cid != "db" else "data", "fontStyle=1;"))
        floating_edge(root, f"life_{cid}", x + 75, 170, x + 75, 700, "", "endArrow=none;html=1;rounded=0;dashed=1;dashPattern=6 6;strokeColor=#999999;")
    messages = [
        ("m1", 195, 230, 445, 230, "1. Request", "sync"),
        ("m2", 445, 300, 695, 300, "2. Validate and process", "sync"),
        ("m3", 695, 370, 1195, 370, "3. Read/write", "sync"),
        ("m4", 695, 450, 945, 450, "4. Publish event", "async"),
        ("m5", 945, 520, 695, 520, "5. Ack/event", "async"),
        ("m6", 445, 610, 195, 610, "6. Response", "meta"),
    ]
    for mid, x1, y1, x2, y2, label, kind in messages:
        if kind == "async":
            edge_style = "endArrow=open;html=1;rounded=0;dashed=1;dashPattern=8 8;strokeColor=#2F855A;"
        elif kind == "meta":
            edge_style = "endArrow=open;html=1;rounded=0;dashed=1;dashPattern=3 3;strokeColor=#6C8EBF;"
        else:
            edge_style = "endArrow=block;html=1;rounded=0;strokeColor=#1F2933;"
        floating_edge(root, mid, x1, y1, x2, y2, label, edge_style)
    return mxfile


def build_deployment_topology(name: str) -> ET.Element:
    mxfile, root = graph(name, 1600, 1000)
    title(root, name, 1600)
    boundary(root, "internet", "Internet / External", 50, 120, 220, 720)
    boundary(root, "edge", "Edge / DMZ", 320, 120, 260, 720)
    boundary(root, "private", "Private Application Zone", 630, 120, 500, 720)
    boundary(root, "datazone", "Data Zone", 1180, 120, 340, 720)
    vertex(root, "users", "Users / Partners", 90, 330, 140, 80, style("actor", "shape=umlActor;fontStyle=1;"))
    vertex(root, "dns", "DNS / CDN", 365, 220, 170, 70, style("app"))
    vertex(root, "waf", "WAF / Firewall", 365, 340, 170, 70, style("security", "fontStyle=1;"))
    vertex(root, "lb", "Load Balancer", 365, 460, 170, 70, style("service"))
    vertex(root, "app1", "App Service A", 700, 270, 170, 75, style("service"))
    vertex(root, "app2", "App Service B", 920, 270, 170, 75, style("service"))
    vertex(root, "worker", "Worker / Job", 810, 430, 170, 75, style("service"))
    vertex(root, "queue", "Queue / Stream", 810, 590, 170, 75, style("event", "shape=hexagon;perimeter=hexagonPerimeter2;"))
    vertex(root, "db", "Primary DB", 1240, 280, 170, 90, "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;")
    vertex(root, "obj", "Object Storage", 1240, 450, 170, 80, style("data"))
    vertex(root, "obs", "Logs / Metrics / Traces", 1240, 610, 190, 80, style("ops"))
    for i, pair in enumerate([("users", "dns"), ("dns", "waf"), ("waf", "lb"), ("lb", "app1"), ("lb", "app2"), ("app1", "db"), ("app2", "db"), ("app1", "queue"), ("queue", "worker"), ("worker", "obj")]):
        edge(root, f"e{i}", pair[0], pair[1])
    edge(root, "obs1", "app1", "obs", "telemetry", "meta")
    edge(root, "obs2", "worker", "obs", "telemetry", "meta")
    return mxfile


def build_cloud_topology(name: str) -> ET.Element:
    mxfile, root = graph(name, 1600, 1000)
    title(root, name, 1600)
    boundary(root, "cloud", "Cloud account / subscription / project", 240, 110, 1280, 760)
    boundary(root, "public", "Public subnet", 300, 190, 330, 570)
    boundary(root, "private", "Private subnet", 680, 190, 360, 570)
    boundary(root, "data", "Data subnet / managed services", 1090, 190, 360, 570)
    vertex(root, "internet", "Internet users", 50, 390, 140, 80, style("actor", "shape=umlActor;fontStyle=1;"))
    vertex(root, "edge", "DNS / CDN / WAF", 365, 270, 190, 80, style("security", "fontStyle=1;"))
    vertex(root, "gateway", "API Gateway / LB", 365, 420, 190, 80, style("service"))
    vertex(root, "compute", "Compute<br>containers / functions / VMs", 760, 270, 190, 90, style("service", "fontStyle=1;"))
    vertex(root, "k8s", "Kubernetes / App Platform", 760, 440, 190, 90, style("app"))
    vertex(root, "events", "Event bus / Queue", 760, 610, 190, 80, style("event", "shape=hexagon;perimeter=hexagonPerimeter2;"))
    vertex(root, "db", "Managed DB", 1180, 270, 180, 90, "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;")
    vertex(root, "lake", "Object Storage / Lake", 1180, 440, 180, 80, style("data"))
    vertex(root, "obs", "Monitoring / SIEM", 1180, 610, 180, 80, style("ops"))
    for i, pair in enumerate([("internet", "edge"), ("edge", "gateway"), ("gateway", "compute"), ("gateway", "k8s"), ("compute", "db"), ("k8s", "db"), ("compute", "events"), ("events", "lake")]):
        edge(root, f"e{i}", pair[0], pair[1])
    edge(root, "eobs1", "compute", "obs", "logs/metrics", "meta")
    edge(root, "eobs2", "k8s", "obs", "logs/metrics", "meta")
    return mxfile


def build_kubernetes(name: str) -> ET.Element:
    mxfile, root = graph(name, 1500, 950)
    title(root, name, 1500)
    boundary(root, "cluster", "Kubernetes cluster", 230, 110, 980, 720)
    boundary(root, "ns", "Namespace: application", 300, 190, 840, 520)
    vertex(root, "user", "Client", 60, 360, 130, 70, style("actor", "shape=umlActor;fontStyle=1;"))
    vertex(root, "ingress", "Ingress Controller", 350, 260, 180, 70, style("service"))
    vertex(root, "svc", "Service", 590, 260, 150, 70, style("service"))
    vertex(root, "deploy", "Deployment", 820, 230, 200, 70, style("app", "fontStyle=1;"))
    vertex(root, "pods", "Pods<br>replicas: n", 820, 340, 200, 90, style("app"))
    vertex(root, "config", "ConfigMap", 360, 520, 160, 65, style("neutral"))
    vertex(root, "secret", "Secret", 560, 520, 160, 65, style("security"))
    vertex(root, "pvc", "PVC / PV", 820, 520, 180, 70, style("data"))
    vertex(root, "db", "External DB", 1260, 350, 170, 90, "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;")
    vertex(root, "obs", "Prometheus / Logs", 1260, 540, 180, 80, style("ops"))
    for i, pair in enumerate([("user", "ingress"), ("ingress", "svc"), ("svc", "pods"), ("deploy", "pods"), ("pods", "db")]):
        edge(root, f"e{i}", pair[0], pair[1])
    edge(root, "cfg", "config", "pods", "mount/env", "meta")
    edge(root, "sec", "secret", "pods", "secret ref", "meta")
    edge(root, "vol", "pods", "pvc", "volume")
    edge(root, "mon", "pods", "obs", "metrics/logs", "meta")
    return mxfile


def build_data_platform(name: str) -> ET.Element:
    mxfile, root = graph(name, 1700, 1000)
    title(root, name, 1700)
    columns = [
        ("Sources", 60),
        ("Ingestion", 300),
        ("Storage", 540),
        ("Transform", 800),
        ("Serving", 1060),
        ("Consumption", 1320),
    ]
    for label, x in columns:
        boundary(root, f"b_{label.lower()}", label, x, 120, 210, 660)
    vertex(root, "apps", "Apps / SaaS / APIs", 90, 230, 150, 70, style("app"))
    vertex(root, "opsdb", "Operational DBs", 90, 370, 150, 80, "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;")
    vertex(root, "files", "Files / IoT / Logs", 90, 520, 150, 70, style("data"))
    vertex(root, "batch", "Batch / ELT", 330, 260, 150, 70, style("service"))
    vertex(root, "cdc", "CDC / Streaming", 330, 430, 150, 70, style("event", "shape=hexagon;perimeter=hexagonPerimeter2;"))
    vertex(root, "raw", "Raw / Landing", 575, 230, 150, 80, style("data"))
    vertex(root, "lake", "Data Lake", 575, 380, 150, 80, style("data"))
    vertex(root, "quality", "Data Quality", 830, 260, 150, 70, style("ops"))
    vertex(root, "transform", "Transform / Model", 830, 430, 150, 70, style("service"))
    vertex(root, "warehouse", "Warehouse / Lakehouse", 1090, 260, 160, 90, "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;")
    vertex(root, "semantic", "Semantic Layer", 1090, 450, 160, 70, style("data"))
    vertex(root, "bi", "BI Dashboards", 1350, 230, 160, 70, style("app"))
    vertex(root, "notebooks", "Analytics / Notebooks", 1350, 370, 160, 70, style("app"))
    vertex(root, "ml", "ML / AI Apps", 1350, 510, 160, 70, style("app"))
    vertex(root, "gov", "Catalog / Lineage / Governance / Privacy", 540, 830, 710, 70, style("security", "fontStyle=1;"))
    for i, pair in enumerate([("apps", "batch"), ("opsdb", "cdc"), ("files", "batch"), ("batch", "raw"), ("cdc", "lake"), ("raw", "quality"), ("lake", "transform"), ("quality", "warehouse"), ("transform", "warehouse"), ("warehouse", "semantic"), ("semantic", "bi"), ("warehouse", "notebooks"), ("warehouse", "ml")]):
        edge(root, f"e{i}", pair[0], pair[1], "", "async" if pair[1] in {"cdc", "lake"} else "sync")
    for i, target in enumerate(["raw", "lake", "warehouse", "semantic"]):
        edge(root, f"g{i}", target, "gov", "metadata", "meta")
    return mxfile


def build_data_pipeline(name: str) -> ET.Element:
    mxfile, root = graph(name, 1600, 900)
    title(root, name, 1600)
    boundary(root, "batch_lane", "Batch pipeline", 80, 150, 1380, 260)
    boundary(root, "stream_lane", "Streaming pipeline", 80, 460, 1380, 260)
    steps = [
        ("batch_src", "Source files / DB", 150, 240, "data"),
        ("orchestrator", "Orchestrator", 390, 240, "ops"),
        ("extract", "Extract / Load", 630, 240, "service"),
        ("quality", "Quality checks", 870, 240, "ops"),
        ("mart", "Data mart", 1110, 240, "data"),
        ("stream_src", "Events / CDC", 150, 550, "event"),
        ("broker", "Broker / Stream", 390, 550, "event"),
        ("process", "Stream processing", 630, 550, "service"),
        ("dq", "Validation / DLQ", 870, 550, "security"),
        ("sink", "Real-time sink", 1110, 550, "data"),
    ]
    for sid, label, x, y, kind in steps:
        cell_style = style(kind, "fontStyle=1;" if kind in {"event", "ops"} else "")
        if kind == "data" and sid in {"mart", "sink"}:
            cell_style = "shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;"
        vertex(root, sid, label, x, y, 170, 75, cell_style)
    for i, pair in enumerate([("batch_src", "orchestrator"), ("orchestrator", "extract"), ("extract", "quality"), ("quality", "mart"), ("stream_src", "broker"), ("broker", "process"), ("process", "dq"), ("dq", "sink")]):
        edge(root, f"e{i}", pair[0], pair[1], "", "async" if pair[0] in {"stream_src", "broker", "process"} else "sync")
    vertex(root, "lineage", "Lineage / SLA / Alerts", 1260, 380, 170, 80, style("ops"))
    edge(root, "lin1", "quality", "lineage", "metrics", "meta")
    edge(root, "lin2", "dq", "lineage", "metrics", "meta")
    return mxfile


def build_lakehouse(name: str) -> ET.Element:
    mxfile, root = graph(name, 1600, 900)
    title(root, name, 1600)
    vertex(root, "sources", "Data sources<br>apps, DBs, SaaS, files", 70, 360, 180, 90, style("app"))
    vertex(root, "ingest", "Ingestion<br>batch / CDC / stream", 310, 360, 190, 90, style("event", "shape=hexagon;perimeter=hexagonPerimeter2;"))
    zones = [("bronze", "Bronze<br>raw immutable", 580, "#F8CECC", "#B85450"), ("silver", "Silver<br>cleaned / conformed", 820, "#DAE8FC", "#6C8EBF"), ("gold", "Gold<br>business-ready marts", 1060, "#D5E8D4", "#82B366")]
    for zid, label, x, fill, stroke in zones:
        vertex(root, zid, label, x, 300, 180, 180, f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontStyle=1;fontSize=15;")
    vertex(root, "catalog", "Catalog / Governance / Security", 600, 560, 620, 80, style("security", "fontStyle=1;"))
    vertex(root, "compute", "Compute engines<br>SQL / Spark / notebooks", 720, 160, 360, 80, style("service"))
    vertex(root, "consumers", "BI / ML / APIs / Reverse ETL", 1310, 350, 210, 100, style("app", "fontStyle=1;"))
    for i, pair in enumerate([("sources", "ingest"), ("ingest", "bronze"), ("bronze", "silver"), ("silver", "gold"), ("gold", "consumers")]):
        edge(root, f"e{i}", pair[0], pair[1], "")
    for i, target in enumerate(["bronze", "silver", "gold"]):
        edge(root, f"cat{i}", target, "catalog", "metadata", "meta")
        edge(root, f"cmp{i}", "compute", target, "read/write", "meta")
    return mxfile


def build_mlops(name: str) -> ET.Element:
    mxfile, root = graph(name, 1650, 950)
    title(root, name, 1650)
    boundary(root, "train", "Training path", 70, 150, 930, 300)
    boundary(root, "serve", "Serving path", 70, 520, 930, 270)
    boundary(root, "monitor", "Monitoring and feedback", 1060, 150, 470, 640)
    vertex(root, "data", "Data sources", 130, 250, 150, 75, style("data"))
    vertex(root, "features", "Feature engineering<br>Feature Store", 350, 235, 180, 105, style("data", "fontStyle=1;"))
    vertex(root, "training", "Training pipeline", 610, 250, 170, 75, style("service"))
    vertex(root, "experiments", "Experiment tracking", 810, 250, 150, 75, style("ops"))
    vertex(root, "registry", "Model Registry", 610, 600, 180, 80, style("data", "fontStyle=1;"))
    vertex(root, "deploy", "Deployment<br>batch or real-time", 350, 590, 180, 100, style("service"))
    vertex(root, "app", "ML/AI Application", 130, 600, 160, 80, style("app"))
    vertex(root, "perf", "Performance / Drift / Bias", 1130, 260, 220, 85, style("ops"))
    vertex(root, "logs", "Predictions / Feedback", 1130, 430, 220, 85, style("event"))
    vertex(root, "retrain", "Retraining trigger", 1130, 600, 220, 85, style("security"))
    for i, pair in enumerate([("data", "features"), ("features", "training"), ("training", "experiments"), ("training", "registry"), ("registry", "deploy"), ("deploy", "app"), ("app", "logs"), ("logs", "perf"), ("perf", "retrain"), ("retrain", "training")]):
        edge(root, f"e{i}", pair[0], pair[1], "", "async" if pair[0] in {"app", "logs", "perf", "retrain"} else "sync")
    return mxfile


BUILDERS = {
    "c4-context": build_c4_context,
    "c4-container": build_c4_container,
    "sequence": build_sequence,
    "deployment-topology": build_deployment_topology,
    "cloud-topology": build_cloud_topology,
    "kubernetes": build_kubernetes,
    "data-platform": build_data_platform,
    "data-pipeline": build_data_pipeline,
    "lakehouse": build_lakehouse,
    "mlops": build_mlops,
}


def write_xml(root: ET.Element, path: Path) -> None:
    ET.indent(root, space="  ")
    path.write_text(ET.tostring(root, encoding="unicode", short_empty_elements=True), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", choices=sorted(BUILDERS), required=True, help="Template type")
    parser.add_argument("--output", required=True, help="Output .drawio path")
    parser.add_argument("--title", default="", help="Diagram title")
    args = parser.parse_args()
    title_text = args.title or f"{args.type} architecture"
    write_xml(BUILDERS[args.type](title_text), Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
