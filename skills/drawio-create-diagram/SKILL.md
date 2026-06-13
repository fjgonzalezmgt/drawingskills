---
name: drawio-create-diagram
description: Create, edit, repair, and validate native draw.io/diagrams.net diagrams in .drawio, .xml, mxfile, or mxGraphModel format. Use when Codex must turn text, code, process descriptions, architecture notes, infrastructure notes, software diagrams, analytics architecture, or tabular data into draw.io XML; inspect or fix draw.io files; generate editor URLs; or produce reusable diagrams/templates. Also trigger for drawing.io, diagrams.net, mxGraphModel, mxfile, drawio XML, diagrama draw.io, or diagramas para diagrams.net.
---

# draw.io Diagram Builder

## Quick Start

Create uncompressed XML first. Prefer a full `<mxfile>` when saving a `.drawio` file, and a bare `<mxGraphModel>` only for fragments that will be pasted or imported.

Use `scripts/drawio_json_to_xml.py` for routine node-and-edge diagrams. Use `scripts/validate_drawio.py` before delivering any `.drawio` or `.xml` file.

Read `references/drawio-xml-reference.md` when the task needs exact style syntax, editor URLs, groups, layers, or source links. Read `references/drawio-stencil-map.md` before choosing shapes for a domain-specific diagram.

## Workflow

1. Identify the diagram type and audience: process flow, system architecture, table-like map, timeline, hierarchy, concept map, or custom template.
2. Choose a layout before writing XML. Use a consistent grid, leave connector clearance, and avoid overlapping labels.
3. Generate plain, readable XML. Do not generate compressed/base64 diagram payloads as the stored file.
4. Include mandatory cells in every graph model:
   - `<mxCell id="0" />`
   - `<mxCell id="1" parent="0" />`
5. Give every diagram element a unique id. Vertices use `vertex="1"`; edges use `edge="1"`. Do not set both.
6. Use semicolon-separated style strings: `key=value;key=value;`.
7. Prefer the native draw.io stencil family for the domain: Lean VSM uses `mxgraph.lean_mapping`, Kubernetes uses `mxgraph.kubernetes`, network topology uses `mxgraph.networks`, integration/pipelines use `mxgraph.eip`, and process maps use `mxgraph.flowchart`.
8. XML-escape labels, especially HTML labels and ampersands.
9. Validate the result with `scripts/validate_drawio.py`.

## Script Usage

Generate a diagram from JSON:

```bash
python scripts/drawio_json_to_xml.py spec.json output.drawio
```

Generate a sample and print an editor URL:

```bash
python scripts/drawio_json_to_xml.py --sample output.drawio --print-url
```

Validate:

```bash
python scripts/validate_drawio.py output.drawio
```

## JSON Spec Shape

Use this shape for `drawio_json_to_xml.py`:

```json
{
  "title": "Process map",
  "page": {"name": "Page-1", "width": 1100, "height": 850},
  "nodes": [
    {"id": "start", "label": "Start", "kind": "terminator", "x": 80, "y": 100, "w": 120, "h": 50},
    {"id": "step1", "label": "Do work", "kind": "process", "x": 260, "y": 95, "w": 150, "h": 60}
  ],
  "edges": [
    {"id": "e1", "source": "start", "target": "step1", "label": ""}
  ]
}
```

Supported node `kind` values: `process`, `terminator`, `decision`, `data`, `document`, `database`, `text`, `container`, `note`, `warning`, `success`, `actor`, `system`, `service`, `api`, `ui`, `worker`, `queue`, `event-bus`, `cache`, `object-storage`, `data-lake`, `warehouse`, `analytics`, `ml`, `cloud`, `network`, `security`, `observability`, `external`.

Add a raw draw.io style with `style`, or append properties with `extra_style`. Use `value` and `label` interchangeably only when adapting specs; normalize to `label` before generation.

## Delivery Rules

Deliver the `.drawio` file when the user wants to open or edit the diagram. Include a generated diagrams.net editor URL only when useful; keep the file as the durable artifact.

If the user asks for PNG/SVG/PDF export, prefer draw.io Desktop CLI when available. If no exporter is available, deliver the editable `.drawio` and explain the export gap briefly.

When exact built-in stencil names are uncertain, use core shapes that render everywhere, then note where a user can swap to specialized stencils in the editor.
