# draw.io Native Stencil Map

Use native draw.io stencils when they exist. Use core shapes only for elements that are not available in the domain stencil or need editable text-heavy boxes.

The style format is:

```text
shape=mxgraph.<family>.<shape_id>;whiteSpace=wrap;html=1;
```

Shape ids are normally the stencil name lowercased with spaces replaced by underscores.

For native icon-like stencils, usually add:

```text
aspect=fixed;verticalLabelPosition=bottom;verticalAlign=top;align=center;
```

Do not force native stencils onto text-heavy elements. Metric boxes, process cards, control-plan cells, legends, timelines, and architecture boundaries should stay as editable core shapes unless the user explicitly asks for icon fidelity.

## Lean / Value Stream Mapping

Use `mxgraph.lean_mapping.*` for VSM-specific icons:

- `finished_goods_to_customer`
- `go_see_production_scheduling`
- `kaizen_lightening_burst`
- `kanban_post`
- `load_leveling`
- `move_by_forklift`
- `mrp_erp`
- `operator`
- `quality_problem`
- `verbal`
- `airplane_7`
- `manual_info_flow`
- `electronic_info_flow`

Use core shapes for VSM process boxes, data boxes, inventory triangles, and timelines because the native lean stencil does not provide all of those text-heavy elements.

JSON aliases in `scripts/drawio_json_to_xml.py`: `vsm-mrp-erp`, `vsm-kanban-post`, `vsm-kaizen`, `vsm-operator`, `vsm-quality-problem`, `vsm-electronic-info-flow`, `vsm-manual-info-flow`, `vsm-forklift`, `vsm-finished-goods`.

QA: run `visual_lint_drawio.py --strict --require-stencil-family lean_mapping` for VSM diagrams.

## Flowcharts and Process Maps

Use `mxgraph.flowchart.*` when a specialized flowchart symbol is needed:

- `process`
- `decision`
- `terminator`
- `data`
- `document`
- `database`
- `predefined_process`
- `manual_operation`
- `manual_input`
- `on-page_reference`
- `off-page_reference`

Core draw.io shapes are acceptable for simple rectangles/diamonds when editability and styling matter more than strict stencil identity.

JSON aliases: `flowchart-process`, `flowchart-decision`, `flowchart-terminator`, `flowchart-data`, `flowchart-document`, `flowchart-database`.

## Kubernetes

Use `mxgraph.kubernetes.*` for Kubernetes resources:

- `ing`
- `svc`
- `deploy`
- `pod`
- `cm`
- `secret`
- `pvc`
- `pv`
- `ns`
- `node`
- `job`
- `cronjob`
- `sts`
- `rs`
- `netpol`

Use swimlane/core containers for cluster and namespace boundaries when a large editable boundary is needed.

JSON aliases: `k8s-ingress`, `k8s-service`, `k8s-deployment`, `k8s-pod`, `k8s-configmap`, `k8s-secret`, `k8s-pvc`, `k8s-namespace`, `k8s-node`.

QA: run `visual_lint_drawio.py --strict --require-stencil-family kubernetes`.

## Network and Infrastructure

Use `mxgraph.networks.*` for generic infrastructure and topology:

- `cloud`
- `firewall`
- `load_balancer`
- `server`
- `web_server`
- `storage`
- `users`
- `router`
- `switch`
- `wireless_hub`
- `desktop_pc`
- `laptop`

Use `mxgraph.aws4.*`, `mxgraph.azure.*`, or `mxgraph.gcp.*` only when the user requests a specific cloud provider and exact icon fidelity matters.

JSON aliases: `network-cloud`, `network-firewall`, `network-load-balancer`, `network-server`, `network-web-server`, `network-storage`, `network-users`, `network-router`, `network-switch`.

QA: run `visual_lint_drawio.py --strict --require-stencil-family networks` for vendor-neutral topology diagrams.

## Integration, Messaging, and Data Pipelines

Use `mxgraph.eip.*` for Enterprise Integration Patterns:

- `channel_adapter`
- `message_1`
- `message_store`
- `message_translator`
- `content_filter`
- `wire_tap`
- `service_activator`
- `process_manager`
- `aggregator`
- `splitter`
- `content_based_router`

Use cylinders and simple cards for warehouses, lakes, marts, semantic layers, and governance where no exact native stencil exists.

JSON aliases: `eip-channel-adapter`, `eip-message`, `eip-message-store`, `eip-transformer`, `eip-content-filter`, `eip-wire-tap`, `eip-service-activator`, `eip-process-manager`.

QA: run `visual_lint_drawio.py --strict --require-stencil-family eip` for EIP-style messaging, orchestration, and pipeline diagrams.

## UML and Software Design

Use core UML styles such as `shape=umlActor` for actors. draw.io does not ship a dedicated C4 stencil in the standard stencil directory, so C4 context/container diagrams should use portable shapes plus clear C4 labels and boundaries.
