---
name: drawio-lean-six-sigma
description: Create Lean Six Sigma and operational excellence diagrams as editable draw.io/diagrams.net files. Use for value stream maps (VSM), SIPOC, process maps, swimlanes, DMAIC, PDCA, A3, Ishikawa/fishbone, 5S, Kaizen, kanban, control plans, FMEA visuals, spaghetti diagrams, Pareto/storyboard layouts, and Spanish requests like mapa de valor, diagrama de flujo, mapeo de proceso, causa-efecto, mejora continua, or Lean Six Sigma en drawing.io.
---

# draw.io Lean Six Sigma

## Quick Start

Use this skill when the diagram is about process improvement, manufacturing, quality, operations, Lean, Six Sigma, DMAIC, or visual management.

For fast templates, run `scripts/make_lss_template.py`. The VSM template must use native `mxgraph.lean_mapping.*` shapes where draw.io provides them. For detailed XML rules, also use `drawio-create-diagram` if it is available in the environment.

Read `references/lean-six-sigma-patterns.md` before creating a diagram that needs domain-specific structure, symbols, metrics, or layout decisions.

## Diagram Selection

Choose the output by intent:

- SIPOC: scope a process at high level before mapping details.
- Process flow: show sequence, decisions, rework, handoffs, and controls.
- Swimlane: show ownership by department, role, system, or shift.
- VSM: show material and information flow, inventory, cycle time, changeover, uptime, demand, takt, and timeline.
- Fishbone/Ishikawa: structure causes by category and connect them to one effect.
- DMAIC or PDCA: present phase gates, deliverables, or project roadmap.
- A3: one-page problem-solving storyboard.
- Spaghetti: trace movement on a layout; use lines over a floor or cell sketch.
- Control plan/FMEA visuals: show process step, CTQ, risk, control method, frequency, owner, and reaction plan.

## Script Usage

Create an editable template:

```bash
python scripts/make_lss_template.py --type sipoc --output sipoc.drawio --title "Order Fulfillment SIPOC"
```

Supported `--type` values: `sipoc`, `fishbone`, `dmaic`, `pdca`, `vsm`, `swimlane`, `a3`.

Validate generated files with the base skill if present:

```bash
python ../drawio-create-diagram/scripts/validate_drawio.py sipoc.drawio
python ../drawio-create-diagram/scripts/visual_lint_drawio.py sipoc.drawio
```

## Visual Conventions

Use restrained, readable visuals. A Lean Six Sigma diagram is normally a working document, not a poster.

Default palette:

- Process/value-added: `#D5E8D4` fill, `#82B366` stroke
- Information/data: `#DAE8FC` fill, `#6C8EBF` stroke
- Waiting/inventory/waste: `#F8CECC` fill, `#B85450` stroke
- Decision/risk: `#FFF2CC` fill, `#D6B656` stroke
- Neutral containers: `#F5F5F5` fill, `#666666` stroke

Prefer native draw.io Lean Mapping stencils for VSM-specific symbols: MRP/ERP, electronic/manual information flow, Kanban Post, Kaizen burst, Operator, Quality Problem, Load Leveling, Move by Forklift, Finished Goods to Customer, Verbal, and Airplane. Use core editable shapes only for process boxes, data boxes, inventory triangles, and timelines because those text-heavy VSM elements are not provided as complete native stencils.

## Quality Bar

Always include the metrics users expect for the diagram type. For VSM, do not omit takt, CT, C/O, uptime, inventory/wait, customer demand, and a bottom timeline. For SIPOC, keep process steps high level. For fishbone, keep causes short and grouped by category. For A3, preserve a clear left-to-right or top-to-bottom problem-solving story.

Deliver the editable `.drawio` artifact, not just Mermaid or an image, unless the user asks for another format.

Before delivery, run structural validation and visual lint. If a renderer/browser is available, inspect an exported image or screenshot and adjust spacing, label size, page bounds, and connector readability before returning the file.
