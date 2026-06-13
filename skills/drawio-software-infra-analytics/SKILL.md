---
name: drawio-software-infra-analytics
description: Create editable draw.io/diagrams.net diagrams for software development, infrastructure topology, cloud architecture, DevOps, security, Kubernetes, data engineering, analytics, BI, lakehouse, data mesh, and MLOps. Use for C4 context/container/component diagrams, UML-style component/deployment/sequence diagrams, API/service maps, CI/CD pipelines, network topology, cloud/on-prem/hybrid architecture, data platform architecture, ETL/ELT pipelines, streaming architecture, semantic/BI layers, ML training/deployment/monitoring flows, and Spanish requests such as arquitectura de software, topologia de infraestructura, arquitectura de analitica, arquitectura de datos, diagrama devops, nube, kubernetes, lakehouse, BI, or MLOps en draw.io.
---

# draw.io Software, Infrastructure, and Analytics

## Quick Start

Use this skill when the diagram is about software systems, infrastructure, cloud/network topology, data platforms, analytics, BI, or ML/AI operations.

For fast editable templates, run `scripts/make_arch_template.py`. For low-level XML rules, validation, editor URLs, and JSON-to-drawio generation, also use `drawio-create-diagram` if it is available.

Read `references/software-infra-analytics-patterns.md` before creating diagrams that need correct architecture layering, notation choices, or domain-specific elements.

## Diagram Selection

Choose the diagram by the user's intent:

- C4 context: explain system boundary, people, external systems, and major interactions.
- C4 container: show deployable/runtime units such as UI, API, service, database, queue, cache, and external integrations.
- Component/service map: explain internals of one service or bounded context.
- Sequence: show temporal request/response, async events, retries, and failure branches.
- Deployment/topology: show environments, zones, networks, compute, data stores, observability, security controls, and user ingress.
- Cloud topology: show VPC/VNet/project, public/private subnets, edge, workloads, managed services, connectivity, and security.
- Kubernetes: show ingress, services, deployments/pods, config, secrets, persistent storage, and observability.
- Data platform: show sources, ingestion, storage zones, transformation, serving, governance, BI, ML, and consumers.
- Pipeline: show orchestration, batch/stream movement, quality checks, lineage, and failure handling.
- Lakehouse: show bronze/silver/gold zones, catalog/governance, compute engines, and consumption.
- MLOps: show data, feature store, training, experiment tracking, registry, deployment, monitoring, and feedback.

## Script Usage

Create an editable template:

```bash
python scripts/make_arch_template.py --type data-platform --output data-platform.drawio --title "Analytics Architecture"
```

Supported `--type` values: `c4-context`, `c4-container`, `sequence`, `deployment-topology`, `cloud-topology`, `kubernetes`, `data-platform`, `data-pipeline`, `lakehouse`, `mlops`.

Validate generated files with the base skill:

```bash
python ../drawio-create-diagram/scripts/validate_drawio.py data-platform.drawio
```

## Visual Conventions

Use native draw.io stencils when they match the domain: `mxgraph.kubernetes.*` for Kubernetes, `mxgraph.networks.*` for generic topology, `mxgraph.eip.*` for messaging/integration/data pipelines, and cloud provider stencils when the provider is specified. Architecture diagrams should still be editable and understandable if specialized provider icons are unavailable.

Default visual language:

- People and external actors: pale yellow.
- Applications/services/APIs: blue.
- Data stores and analytical stores: purple.
- Messaging/event streaming: teal.
- Security/governance/observability: red or amber.
- Network/environment boundaries: light gray containers.
- Data/async flow: dashed lines.
- Runtime/request flow: solid arrows.

## Quality Bar

Every architecture diagram should answer: who uses it, what runs where, how data or requests move, what crosses a boundary, which systems own state, and where controls/monitoring live.

Label edges with protocols or flow meaning when useful: HTTPS, REST, gRPC, SQL, CDC, events, batch, stream, metrics, logs, traces.

For analytics architectures, include governance and data quality unless the user explicitly asks for a minimal diagram.

Deliver an editable `.drawio` file, not only a screenshot or Mermaid, unless the user asks for another format.
