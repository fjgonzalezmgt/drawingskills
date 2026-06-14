---
name: drawio-create-diagram
description: Create, edit, repair, and validate native draw.io/diagrams.net diagrams in .drawio, .xml, mxfile, or mxGraphModel format. Use when Codex must turn text, code, process descriptions, architecture notes, infrastructure notes, software diagrams, analytics architecture, or tabular data into draw.io XML; inspect or fix draw.io files; generate editor URLs; or produce reusable diagrams/templates. Mandatory final QA requires running scripts/validate_drawio.py and scripts/visual_lint_drawio.py for generated or edited diagrams, then visually inspecting a screenshot/export when a renderer or browser is available. Do not deliver a generated .drawio without reporting these QA results. Also trigger for drawing.io, diagrams.net, mxGraphModel, mxfile, drawio XML, diagrama draw.io, or diagramas para diagrams.net.
---

# draw.io Diagram Builder

## Quick Start

Create uncompressed XML first. Prefer a full `<mxfile>` when saving a `.drawio` file, and a bare `<mxGraphModel>` only for fragments that will be pasted or imported.

Use `scripts/drawio_json_to_xml.py` for routine node-and-edge diagrams. It includes portable core shapes plus native stencil `kind` aliases for Lean VSM, flowchart, Kubernetes, network, and EIP/integration icons. Use `scripts/validate_drawio.py` and `scripts/visual_lint_drawio.py` before delivering any `.drawio` or `.xml` file.

Read `references/drawio-xml-reference.md` when the task needs exact style syntax, editor URLs, groups, layers, or source links. Read `references/drawio-stencil-map.md` before choosing shapes for a domain-specific diagram.

## Mandatory QA Gate

Do not deliver a generated or edited `.drawio` file until this gate is complete:

1. Run `scripts/validate_drawio.py <file>`.
2. Run `scripts/visual_lint_drawio.py --strict <file>`.
3. For diagrams that should use a native family, add `--require-stencil-family <family>` to visual lint, for example `lean_mapping`, `kubernetes`, `networks`, or `eip`.
4. If either command fails, adjust layout/XML and rerun both commands.
5. If a browser, draw.io Desktop, or another renderer is available, inspect an exported image or editor screenshot and adjust obvious visual problems.
6. In the final response, state the result of structural validation, visual lint, stencil-family check when used, and screenshot/export review. If screenshot/export review was unavailable, say so.

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
10. Run `scripts/visual_lint_drawio.py` and adjust geometry until there are no errors and no important warnings.
11. When a renderer/browser is available, visually inspect an exported PNG/SVG or editor screenshot. Check for blank canvas, clipped labels, overlapping nodes, cropped native stencils, unreadable connectors, and excessive whitespace. Adjust and repeat.

## Stencil Selection Contract

Before writing XML, choose the stencil contract:

- **Strict native family**: use when the diagram type has a clear draw.io library, such as VSM, Kubernetes, network topology, or EIP-style pipeline. Use native `shape=mxgraph.<family>.<shape_id>` styles and run visual lint with `--require-stencil-family`.
- **Hybrid**: use native icons for domain-specific symbols and core editable shapes for text-heavy cards, metric boxes, boundaries, timelines, and labels.
- **Portable core shapes**: use when draw.io has no default domain stencil, when exact built-in shape ids are uncertain, or when text editability matters more than icon fidelity.

Native icon stencils should usually include `aspect=fixed;` and labels below the icon with `verticalLabelPosition=bottom;verticalAlign=top;align=center;` unless the stencil itself is a flow line or compact symbol.

## Visual Polish Rules

Use a visible title, consistent spacing, and a page size that fits the actual content. Keep major nodes aligned to a grid, reserve light gray containers for boundaries, and route source/target connectors orthogonally. Use no more than a few semantic fill colors, keep label text short, and move dense notes into separate text boxes instead of overloading icons.

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

Visual layout lint:

```bash
python scripts/visual_lint_drawio.py output.drawio
```

Strict visual lint for final QA:

```bash
python scripts/visual_lint_drawio.py --strict output.drawio
```

Require a native stencil family when the diagram type calls for one:

```bash
python scripts/visual_lint_drawio.py --strict --require-stencil-family kubernetes output.drawio
```

Optionally check generated geometry against a grid:

```bash
python scripts/visual_lint_drawio.py --strict --check-grid --grid-step 5 output.drawio
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

Supported node `kind` values include portable shapes: `process`, `terminator`, `decision`, `data`, `document`, `database`, `text`, `container`, `note`, `warning`, `success`, `actor`, `system`, `service`, `api`, `ui`, `worker`, `queue`, `event-bus`, `cache`, `object-storage`, `data-lake`, `warehouse`, `analytics`, `ml`, `cloud`, `network`, `security`, `observability`, `external`.

Native stencil aliases include:

- Flowchart: `flowchart-process`, `flowchart-decision`, `flowchart-terminator`, `flowchart-data`, `flowchart-document`, `flowchart-database`
- Lean VSM: `vsm-mrp-erp`, `vsm-kanban-post`, `vsm-kaizen`, `vsm-operator`, `vsm-quality-problem`, `vsm-electronic-info-flow`, `vsm-manual-info-flow`, `vsm-forklift`, `vsm-finished-goods`
- Kubernetes: `k8s-ingress`, `k8s-service`, `k8s-deployment`, `k8s-pod`, `k8s-configmap`, `k8s-secret`, `k8s-pvc`, `k8s-namespace`, `k8s-node`
- Network: `network-cloud`, `network-firewall`, `network-load-balancer`, `network-server`, `network-web-server`, `network-storage`, `network-users`, `network-router`, `network-switch`
- EIP/integration: `eip-channel-adapter`, `eip-message`, `eip-message-store`, `eip-transformer`, `eip-content-filter`, `eip-wire-tap`, `eip-service-activator`, `eip-process-manager`

Add a raw draw.io style with `style`, or append properties with `extra_style`. Use `value` and `label` interchangeably only when adapting specs; normalize to `label` before generation.

## Delivery Rules

Deliver the `.drawio` file when the user wants to open or edit the diagram. Include a generated diagrams.net editor URL only when useful; keep the file as the durable artifact.

If the user asks for PNG/SVG/PDF export, prefer draw.io Desktop CLI when available. If no exporter is available, deliver the editable `.drawio` and explain the export gap briefly.

When exact built-in stencil names are uncertain, use core shapes that render everywhere, then note where a user can swap to specialized stencils in the editor.

Before final delivery, report whether structural validation, visual lint, and screenshot/export review were completed. If screenshot/export review was not possible in the current environment, say that explicitly and rely on the geometry lint plus `.drawio` validation.
