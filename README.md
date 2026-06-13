# draw.io Skills for Codex

Libreria de skills para crear diagramas editables de draw.io/diagrams.net desde Codex.

El foco inicial es Lean Six Sigma, mejora continua y calidad, pero el repo tambien incluye capacidades para arquitectura de software, topologias de infraestructura, cloud, Kubernetes, analitica, BI, lakehouse y MLOps.

## Ubicacion en el ecosistema

Este repositorio forma parte de la linea **Codex Skills / AI Workflows** del portfolio tecnico.

Indice maestro:

```text
https://github.com/fjgonzalezmgt/Codex-Skills-AI-Workflows
```

Rol de este repo dentro de la estructura:

```text
Codex Skills / AI Workflows
├── Codex-Skills-AI-Workflows        # indice maestro de la linea
└── drawingskills                    # diagramas draw.io editables desde Codex
```

Su funcion es convertir descripciones tecnicas en diagramas editables, versionables y reutilizables para calidad, mejora continua, analitica y arquitectura tecnica.

## Contenido

```text
skills/
  drawio-create-diagram/              Motor base para generar y validar XML .drawio
  drawio-lean-six-sigma/              Diagramas Lean Six Sigma y excelencia operacional
  drawio-software-infra-analytics/    Software, infraestructura, cloud, datos, BI y MLOps
  drawio-shape-library-builder/       Bibliotecas .xml de shapes reutilizables

examples/
  *.drawio                            Ejemplos Lean Six Sigma y genericos
  software-infra-analytics/*.drawio   Ejemplos de arquitectura
  *-library.xml                       Bibliotecas de shapes para draw.io
```

## Skills

## Uso de librerias nativas de draw.io

Los generadores priorizan stencils nativas cuando draw.io trae una biblioteca apropiada:

- VSM: `mxgraph.lean_mapping.*`
- Kubernetes: `mxgraph.kubernetes.*`
- Topologias de infraestructura: `mxgraph.networks.*`
- Integracion, mensajeria y pipelines: `mxgraph.eip.*`
- Flowcharts/procesos: `mxgraph.flowchart.*` cuando se requiere simbologia estricta

Cuando draw.io no trae una stencil completa para un elemento, por ejemplo cajas de proceso y data boxes de VSM, se usan shapes base editables para conservar texto, metricas y formato.

### `drawio-create-diagram`

Skill base para crear, reparar y validar archivos `.drawio`, `.xml`, `<mxfile>` y `<mxGraphModel>`.

Incluye:

- `scripts/drawio_json_to_xml.py`: convierte una especificacion JSON de nodos y edges a `.drawio`.
- `scripts/validate_drawio.py`: valida estructura basica de archivos draw.io.
- `references/drawio-xml-reference.md`: notas sobre XML, estilos y librerias integradas.

### `drawio-lean-six-sigma`

Skill para VSM, SIPOC, swimlanes, DMAIC, PDCA, A3, Ishikawa/fishbone y otros diagramas de mejora continua.

Genera plantillas con:

```powershell
python .\skills\drawio-lean-six-sigma\scripts\make_lss_template.py --type sipoc --output .\examples\sipoc.drawio --title "SIPOC"
```

Tipos soportados:

```text
sipoc, fishbone, dmaic, pdca, vsm, swimlane, a3
```

### `drawio-software-infra-analytics`

Skill para desarrollo de software, arquitectura tecnica, topologias cloud/on-prem/hibridas, Kubernetes, analitica, BI, lakehouse y MLOps.

Genera plantillas con:

```powershell
python .\skills\drawio-software-infra-analytics\scripts\make_arch_template.py --type data-platform --output .\examples\software-infra-analytics\data-platform.drawio --title "Analytics Architecture"
```

Tipos soportados:

```text
c4-context, c4-container, sequence, deployment-topology, cloud-topology,
kubernetes, data-platform, data-pipeline, lakehouse, mlops
```

### `drawio-shape-library-builder`

Skill para crear bibliotecas `.xml` de shapes reutilizables para draw.io.

Generar biblioteca Lean Six Sigma:

```powershell
python .\skills\drawio-shape-library-builder\scripts\make_mxlibrary.py --sample-lean .\examples\lean-six-sigma-library.xml
```

Generar biblioteca de arquitectura:

```powershell
python .\skills\drawio-shape-library-builder\scripts\make_mxlibrary.py --sample-architecture .\examples\architecture-library.xml
```

## Instalacion en Codex

Para copiar las skills a `~/.codex/skills`:

```powershell
.\install_to_codex.ps1
```

Tambien puedes indicar otro destino:

```powershell
.\install_to_codex.ps1 -Destination "C:\ruta\a\skills"
```

## Uso desde Codex

Ejemplos de prompts:

```text
Usa $drawio-lean-six-sigma para crear un VSM del proceso de compras.
Usa $drawio-software-infra-analytics para crear una arquitectura lakehouse editable en draw.io.
Usa $drawio-create-diagram para convertir esta especificacion JSON en un archivo .drawio.
Usa $drawio-shape-library-builder para crear una biblioteca de shapes de analitica.
```

## Validacion

Validar un `.drawio`:

```powershell
python .\skills\drawio-create-diagram\scripts\validate_drawio.py .\examples\sample.drawio
```

Validar una skill con el validador de Codex:

```powershell
conda run -n f1predictor python C:\Users\fjgon\.codex\skills\.system\skill-creator\scripts\quick_validate.py .\skills\drawio-create-diagram
```

## Abrir en draw.io

Los archivos `.drawio` se pueden abrir en:

- https://app.diagrams.net/
- draw.io Desktop

Las bibliotecas `.xml` se cargan desde draw.io con:

```text
File > Open Library from > Device
```

Si una biblioteca esta publicada como URL raw, se puede cargar con el parametro `clibs` de diagrams.net.

## Notas

- Los archivos generados se guardan como XML sin comprimir para que Codex pueda leerlos, repararlos y versionarlos.
- Las plantillas usan shapes portables de draw.io por defecto. Los stencils de AWS, Azure, GCP, Kubernetes, UML y Lean se pueden usar cuando haga falta fidelidad visual especifica.
- Los ejemplos son artefactos editables, no capturas de pantalla.
