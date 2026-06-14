# draw.io Custom Shape Library Format

## Source Notes

Primary references:

- https://www.drawio.com/docs/reference/format-custom-shape-library/
- https://www.drawio.com/docs/manual/advanced/custom-shape-libraries/
- https://github.com/jgraph/drawio-libs

## File Shape

A custom shape library is an XML file with a single `<mxlibrary>` node. The node text is a JSON array.

```xml
<mxlibrary tags="lean six sigma quality">
[
  {
    "title": "Example",
    "w": 120,
    "h": 60,
    "xml": "&lt;mxGraphModel&gt;...&lt;/mxGraphModel&gt;"
  }
]
</mxlibrary>
```

The `tags` attribute is optional and is added to entries for sidebar search.

## Entry Properties

Required:

- `w`: width in pixels
- `h`: height in pixels
- `xml` or `data`

Optional:

- `title`: hover/sidebar title
- `tags`: space-separated search tags
- `aspect`: for image entries, usually `fixed`
- `style`: extra style applied to image entries

## XML Entries

Use `xml` for editable shapes, groups, fragments, and templates. The value is an `<mxGraphModel>` string. In the final XML file, `<` and `>` must be XML-escaped in the `<mxlibrary>` text. JSON string quotes must also remain valid.

The helper script writes the JSON as XML text so escaping is handled automatically.

Keep `w` and `h` aligned with the fragment's visible geometry. Mismatched dimensions can crop native icons in the sidebar or leave thumbnails with large blank margins. Generated libraries should reject XML fragments that do not parse.

## Data Entries

Use `data` for image entries:

- `data:image/png;base64,...`
- `data:image/jpeg;base64,...`
- `data:image/svg+xml;base64,...`
- `data:image/gif;base64,...`

SVGs can be bundled as images, but they are not native editable draw.io shapes.

## Loading and Sharing

Local use:

- Open draw.io.
- Use File > Open Library from > Device.
- Select the `.xml` library file.

Hosted use:

- Upload the library to a web-accessible location.
- Use a raw file URL when hosted on GitHub.
- URL-encode the raw URL.
- Load it with `https://app.diagrams.net/?splash=0&clibs=U<encoded-url>`.

Multiple libraries can be separated with semicolons, and each URL value is prefixed with `U`.

## Lean Six Sigma Library Strategy

For Lean Six Sigma, package frequently reused fragments rather than too many tiny icons:

- CTQ card
- Waste tag
- Kaizen burst
- Kanban card
- VSM data box
- Inventory triangle
- SIPOC column starter
- Control plan block

Use built-in draw.io shape libraries during actual diagram creation when icon fidelity matters. The included Lean sample uses `mxgraph.lean_mapping.*` for Kaizen, Kanban Post, MRP/ERP, information flow, Operator, and Quality Problem.

## Software, Infrastructure, and Analytics Library Strategy

Package reusable architecture fragments:

- System boundary
- API/service card
- Async worker
- Queue/event bus
- Operational database
- Object storage/data lake
- Warehouse/lakehouse
- Data quality gate
- Governance/catalog
- Feature store/model registry
- Observability block
- Security control

Prefer editable XML fragments over raster icons for architecture primitives. Use `mxgraph.kubernetes.*`, `mxgraph.networks.*`, and `mxgraph.eip.*` where those stencils match the shape. Use data URI images only for product logos or vendor icons the user provides.
