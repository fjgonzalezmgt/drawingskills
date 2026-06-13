# Software, Infrastructure, and Analytics Diagram Patterns

## Source Notes

Use the base draw.io XML guidance from `drawio-create-diagram` when available. draw.io's style reference lists core shape families plus stencil families such as `mxgraph.uml.*`, `mxgraph.aws4.*`, `mxgraph.azure.*`, `mxgraph.gcp.*`, `mxgraph.kubernetes.*`, `mxgraph.er.*`, `mxgraph.eip.*`, and networking libraries.

Prefer portable core shapes first. Use branded/vendor stencils when the user asks for AWS/Azure/GCP/Kubernetes icon fidelity.

## C4 and Software Architecture

Context diagram:

- Put the system of interest at the center.
- Put people and external systems around it.
- Draw only important relationships.
- Label relationship intent, not implementation trivia.
- Add a system boundary when scope is ambiguous.

Container diagram:

- Show deployable/runtime units: SPA/mobile app, API gateway, backend services, workers, database, cache, queue, object storage, third-party systems.
- Show protocols and ownership of state.
- Distinguish synchronous calls from async/event flow.
- Group containers by trust boundary, runtime environment, or bounded context.

Component/service diagram:

- Use it only when the user asks for internals of one container/service.
- Show controllers/handlers, domain services, repositories/adapters, clients, events, and persistence.
- Keep interfaces explicit.

Sequence diagram:

- Use vertical lifelines for actors/systems.
- Put time top-to-bottom.
- Use solid arrows for requests, dashed arrows for responses/events.
- Label retries, timeouts, and async queues.

## Infrastructure and Topology

Deployment/topology diagrams should show:

- Users/clients and ingress path.
- Edge controls: DNS, CDN, WAF, firewall, VPN, API gateway, load balancer.
- Network boundaries: internet, DMZ/public subnet, private subnet, data subnet, on-prem, cloud account/subscription/project, region, availability zone.
- Compute: VMs, containers, serverless, Kubernetes nodes/pods.
- State: database, object storage, file storage, cache, queue/stream.
- Platform services: identity, secrets, CI/CD, artifact registry.
- Operations: metrics, logs, traces, alerts, backup/DR.

Use boundary boxes for environments and zones. Put security controls on crossings. Avoid drawing every port unless the user asks for a network-level diagram.

## Cloud Architecture

Use a vendor-neutral layout unless the user requests a provider:

- Edge: DNS/CDN/WAF.
- Network: VPC/VNet/project, public/private/data subnets.
- Compute: app services, containers, functions, Kubernetes.
- Integration: API gateway, queue, event bus, stream.
- Data: relational DB, warehouse, lake/object store, cache, search.
- Security: IAM, KMS, secrets, firewall/security groups.
- Observability: logs, metrics, tracing, alerting.

If using vendor icons, keep labels readable and do not depend on icons alone.

## Kubernetes

Show:

- Cluster boundary.
- Namespace boundary when relevant.
- Ingress/controller.
- Service objects.
- Deployments/statefulsets and pods.
- ConfigMaps, Secrets, PVC/PV.
- External dependencies and managed data stores.
- Observability sidecars/agents if relevant.

Use arrows from ingress -> service -> pods -> data. Show config/secrets as dependencies, not as request path.

## Data and Analytics Architecture

A complete analytics architecture usually includes:

- Sources: applications, operational DBs, files, SaaS, IoT, logs.
- Ingestion: batch, CDC, streaming, API ingestion.
- Landing/raw storage.
- Processing/transformation: ELT/ETL, orchestration, streaming processing.
- Quality and validation gates.
- Curated storage: warehouse, lakehouse, marts, feature store.
- Catalog, lineage, governance, security, privacy.
- Consumption: BI dashboards, analytics notebooks, reverse ETL, ML/AI apps, APIs.
- Operations: monitoring, cost, SLAs, data observability.

Use different edge styles:

- Solid arrows for primary movement.
- Dashed arrows for metadata, quality signals, or control plane.
- Teal or blue for data flow; amber/red for control/risk.

## Lakehouse

Show bronze/silver/gold as separate zones:

- Bronze: raw immutable landing.
- Silver: cleaned/conformed data.
- Gold: business-ready marts/features.

Add catalog/governance across all zones. Add compute engines above or beside the zones. Add BI/ML/API consumers on the right.

## MLOps

Show the full loop:

- Data sources and labeling.
- Feature engineering and feature store.
- Training pipeline and experiment tracking.
- Model registry.
- Deployment target: batch scoring, real-time API, edge, or embedded app.
- Monitoring: performance, drift, bias/fairness, latency, cost.
- Feedback loop to data and retraining.

Keep training and serving paths visually distinct.

## CI/CD and DevOps

Show:

- Source repository.
- Build/test/security scan.
- Artifact/container registry.
- Deployment environments: dev, test, staging, prod.
- Approval gates and rollback.
- Observability and incident feedback.

Use pipeline lanes when the workflow is more important than runtime topology.
