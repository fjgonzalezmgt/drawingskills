# Lean Six Sigma Diagram Patterns for draw.io

## Source Notes

draw.io references used for implementation details:

- https://www.drawio.com/docs/reference/diagram-generation/
- https://www.drawio.com/docs/reference/diagram-generation/style-reference/
- https://www.drawio.com/docs/manual/advanced/custom-shape-libraries/

The draw.io style reference lists `mxgraph.lean_mapping.*` as a built-in stencil family. Use it for icon fidelity whenever the native symbol exists; otherwise, use portable core shapes.

Native Lean Mapping stencil ids:

- `mxgraph.lean_mapping.finished_goods_to_customer`
- `mxgraph.lean_mapping.go_see_production_scheduling`
- `mxgraph.lean_mapping.kaizen_lightening_burst`
- `mxgraph.lean_mapping.kanban_post`
- `mxgraph.lean_mapping.load_leveling`
- `mxgraph.lean_mapping.move_by_forklift`
- `mxgraph.lean_mapping.mrp_erp`
- `mxgraph.lean_mapping.operator`
- `mxgraph.lean_mapping.quality_problem`
- `mxgraph.lean_mapping.verbal`
- `mxgraph.lean_mapping.airplane_7`
- `mxgraph.lean_mapping.manual_info_flow`
- `mxgraph.lean_mapping.electronic_info_flow`

## SIPOC

Purpose: define process scope at the start of Define/Measure.

Layout:

- Five equal columns: Suppliers, Inputs, Process, Outputs, Customers.
- Use a strong header row and a large body cell per column.
- Process column should show 4 to 7 high-level steps, not detailed tasks.
- Add CTQ or VOC notes below when relevant.

Common placeholders:

- Suppliers: internal teams, vendors, systems
- Inputs: forms, orders, materials, specs
- Process: verb phrases
- Outputs: products, reports, approvals
- Customers: external customer, downstream process, regulator

## Value Stream Map

Purpose: show current/future state material and information flow.

Minimum elements:

- Supplier on the left, customer on the right.
- Production control or information source above process boxes.
- Process boxes in sequence with data boxes below.
- Inventory/wait markers between process boxes.
- Material flow arrows across the process stream.
- Information flow arrows from control/customer/supplier.
- Timeline at the bottom: value-added time vs waiting time.
- Summary metrics: customer demand, takt time, total lead time, total process time.

Native stencil use:

- Production control / planning: `mrp_erp`, optionally `load_leveling`.
- Information flow: `manual_info_flow` and `electronic_info_flow`.
- Pull/visual control: `kanban_post`.
- Improvement/risk: `kaizen_lightening_burst`, `quality_problem`.
- Labor/material handling: `operator`, `move_by_forklift`, `finished_goods_to_customer`.

Use core rectangles for process boxes and data boxes so the metric text remains easy to edit.

QA: because VSM has a dedicated draw.io stencil family, run `visual_lint_drawio.py --strict --require-stencil-family lean_mapping` before delivery. If this fails, add the correct native VSM symbols instead of replacing them with generic icons.

Data box fields:

- CT: cycle time
- C/O: changeover
- Uptime
- Operators
- Yield or FPY
- Batch size

## Process Flow and Swimlane

Purpose: expose handoffs, rework loops, decisions, approvals, and controls.

Use:

- Rounded rectangle for start/end.
- Rectangle for process.
- Diamond for decision.
- Parallelogram for input/output or data.
- Document shape for form/report.
- Dashed edges for information-only flow.
- Swimlanes by role, department, system, site, or shift.

Keep connector paths orthogonal. Place rework loops below the main flow and label them.

## Fishbone / Ishikawa

Purpose: structure possible causes for a problem.

Default categories:

- Manpower / People
- Machine / Equipment
- Method / Process
- Material
- Measurement
- Mother Nature / Environment

For services, consider replacing categories with People, Process, Policy, Technology, Measurement, Environment.

Put the effect/problem statement in a box at the right. Use one main spine and diagonal bones. Keep causes short; add evidence tags only when needed.

## DMAIC and PDCA

DMAIC:

- Define: problem, customer, CTQ, charter
- Measure: baseline, data plan, MSA
- Analyze: root causes, hypotheses, verified drivers
- Improve: countermeasures, pilots, mistake-proofing
- Control: control plan, response plan, handoff

PDCA:

- Plan: target and hypothesis
- Do: experiment or pilot
- Check: results and learning
- Act: standardize or adjust

Use these for roadmaps, phase gates, or project summaries.

## A3

Purpose: one-page problem-solving narrative.

Recommended sections:

- Background
- Current state
- Problem statement
- Target condition
- Root cause analysis
- Countermeasures
- Implementation plan
- Results / follow-up

Use a grid, not floating cards. The A3 must read as one coherent page.

## Spaghetti Diagram

Purpose: show movement waste.

Use a simple layout or imported background image. Trace observed movement with colored polylines. Include a small legend with distance, trips, time window, and observer/date.

## Control Plan / FMEA Visual

For a diagrammatic control plan, show process step -> CTQ/risk -> control -> frequency/owner -> reaction plan.

For FMEA summaries, focus visual attention on high RPN/AP or high severity items, controls, and recommended actions. Keep detailed ranking tables in a spreadsheet when they become dense.
