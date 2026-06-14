# draw.io XML Reference

## Source Notes

Primary references:

- https://www.drawio.com/docs/reference/diagram-generation/
- https://www.drawio.com/docs/reference/diagram-generation/style-reference/
- https://www.drawio.com/docs/reference/format-custom-shape-library/
- https://www.drawio.com/docs/manual/advanced/diagram-source-edit/
- https://www.drawio.com/docs/manual/advanced/custom-shape-libraries/

## File Structure

Use this full file shape for saved `.drawio` files:

```xml
<mxfile host="app.diagrams.net">
  <diagram id="page-1" name="Page-1">
    <mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

draw.io also accepts a bare `<mxGraphModel>` and wraps it in an `<mxfile>` automatically. Use that only for fragments or import snippets.

## Core Cell Patterns

Vertex:

```xml
<mxCell id="n1" value="Step" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="60" as="geometry" />
</mxCell>
```

Edge:

```xml
<mxCell id="e1" value="" style="endArrow=block;html=1;rounded=1;edgeStyle=orthogonalEdgeStyle;" edge="1" parent="1" source="n1" target="n2">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

Floating edge with absolute endpoints:

```xml
<mxCell id="e2" value="" style="endArrow=block;html=1;rounded=1;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="100" y="100" as="sourcePoint" />
    <mxPoint x="300" y="100" as="targetPoint" />
  </mxGeometry>
</mxCell>
```

## Style Rules

Styles are semicolon-separated `key=value;` pairs. Booleans are `0` or `1`. Colors are `#RRGGBB`, `none`, or `default`.

Common vertex styles:

- Process: `rounded=1;whiteSpace=wrap;html=1;fillColor=#EAF4FE;strokeColor=#1565C0;`
- Decision: `rhombus;whiteSpace=wrap;html=1;fillColor=#FFF2CC;strokeColor=#D6B656;perimeter=rhombusPerimeter;`
- Data: `shape=parallelogram;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#82B366;perimeter=parallelogramPerimeter;`
- Document: `shape=document;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;`
- Database: `shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#E1D5E7;strokeColor=#9673A6;`
- Service/API: `rounded=1;whiteSpace=wrap;html=1;fillColor=#EAF4FE;strokeColor=#1565C0;`
- Queue/event bus: `shape=hexagon;whiteSpace=wrap;html=1;fillColor=#D5E8D4;strokeColor=#82B366;perimeter=hexagonPerimeter2;`
- Cloud/network boundary: `swimlane;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;startSize=28;fillColor=#F5F5F5;strokeColor=#666666;`
- Security/control: `rounded=1;whiteSpace=wrap;html=1;fillColor=#F8CECC;strokeColor=#B85450;`
- Observability/operations: `rounded=1;whiteSpace=wrap;html=1;fillColor=#FFE6CC;strokeColor=#D79B00;`
- Text: `text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;whiteSpace=wrap;`

Common edge styles:

- Orthogonal: `endArrow=block;html=1;rounded=1;edgeStyle=orthogonalEdgeStyle;`
- Dashed information: `endArrow=open;html=1;rounded=1;dashed=1;dashPattern=8 8;edgeStyle=orthogonalEdgeStyle;`
- Association/no arrow: `endArrow=none;html=1;rounded=1;edgeStyle=orthogonalEdgeStyle;`

## Built-In Shape Families

Core and useful libraries include:

- `mxgraph.flowchart.*` for flowcharts
- `mxgraph.bpmn.*` for BPMN
- `mxgraph.uml.*` and `mxgraph.er.*`
- `mxgraph.aws4.*`, `mxgraph.azure.*`, `mxgraph.gcp.*`, `mxgraph.kubernetes.*`
- `mxgraph.pid.*` for piping/instrumentation
- `mxgraph.mockup.*` for wireframes
- `mxgraph.lean_mapping.*` for lean/value stream mapping
- `mxgraph.eip.*` for enterprise integration patterns
- `mxgraph.cisco.*` / network stencil families for network topology
- `mxgraph.pid.*` for piping/instrumentation

Use core shapes when portability matters more than specialized icon fidelity.

## Editor URL

To open generated XML in the online editor, compress the XML for the `#create` hash. The durable file should remain uncompressed.

Hash JSON shape:

```json
{"type":"xml","compressed":true,"data":"BASE64_RAW_DEFLATE","effect":"pop"}
```

The helper script can generate this URL with `--print-url`.

## Validation Checklist

- XML parses cleanly.
- File root is `<mxfile>` or `<mxGraphModel>`.
- Each graph model has `id="0"` and `id="1" parent="0"`.
- IDs are unique within each graph model.
- Vertices and edges are not mixed on the same cell.
- Edges reference existing source/target ids, unless they use explicit `sourcePoint` and `targetPoint`.
- Labels with `<`, `>`, `&`, or quotes are XML-escaped.
- No XML comments are included in generated diagram XML.
- Domain-specific diagrams use expected native stencil families when available; verify with `visual_lint_drawio.py --strict --require-stencil-family <family>`.
- Native icon stencils preserve aspect ratio with `aspect=fixed;` unless the stencil is intentionally stretched, such as a compact information-flow symbol.
- Source/target edges use orthogonal or elbow routing unless a sequence, timeline, or freeform sketch intentionally uses floating endpoints.
