---
name: drawio-shape-library-builder
description: Build, edit, validate, and share custom draw.io/diagrams.net shape libraries in .xml mxlibrary format. Use when Codex must package reusable shapes, icons, diagram fragments, Lean Six Sigma stencils, corporate assets, templates, SVG/PNG/JPG/GIF data URIs, or GitHub-hosted libraries that load with the clibs URL parameter. Also trigger for custom library, shape library, mxlibrary, libreria de formas, biblioteca de imagenes, or libreria drawing.io.
---

# draw.io Shape Library Builder

## Quick Start

Create a draw.io custom shape library when the user wants reusable shapes in the left sidebar, a portable `.xml` library file, or a hosted library URL that opens in diagrams.net.

Use `scripts/make_mxlibrary.py` to assemble libraries from JSON, embedded XML snippets, local SVG/PNG/JPG/GIF files, or built-in samples. Built-in samples must use native draw.io stencils where available.

Read `references/custom-library-format.md` for exact format rules and sharing notes.

## Workflow

1. Decide whether each entry is an editable draw.io XML fragment or an image data URI.
2. Use XML fragments for diagrams, grouped shapes, and reusable editable components.
3. Use image data URIs for logos, icons, and artwork where editability is not required.
4. Add titles and tags so entries are searchable in the sidebar.
5. Keep each entry's `w`/`h` close to the fragment's visible geometry so library previews do not crop or stretch.
6. Generate `<mxlibrary>` XML and validate that it parses; `make_mxlibrary.py` also parses XML fragments and rejects invalid data URIs.
7. If sharing via URL, host the library file and load it with `clibs=U<url-encoded-raw-url>`.

## Script Usage

Create the built-in Lean Six Sigma sample library:

```bash
python scripts/make_mxlibrary.py --sample-lean lean-six-sigma-library.xml
```

Create the built-in software/infrastructure/analytics sample library:

```bash
python scripts/make_mxlibrary.py --sample-architecture architecture-library.xml
```

Create a library from JSON:

```bash
python scripts/make_mxlibrary.py library-spec.json my-library.xml
```

Print a diagrams.net load URL for a hosted raw library:

```bash
python scripts/make_mxlibrary.py --hosted-url "https://raw.githubusercontent.com/org/repo/main/libs/my-library.xml"
```

## JSON Spec Shape

```json
{
  "tags": "lean six sigma quality process",
  "entries": [
    {
      "title": "CTQ card",
      "tags": "ctq customer quality",
      "w": 180,
      "h": 90,
      "xml_path": "fragments/ctq-card.drawio"
    },
    {
      "title": "Company logo",
      "tags": "brand logo",
      "w": 120,
      "h": 60,
      "data_path": "assets/logo.svg",
      "aspect": "fixed",
      "style": "resizable=0;rotatable=0;"
    }
  ]
}
```

Each entry must have `w`, `h`, and either `xml`, `xml_path`, `data`, or `data_path`.

## Delivery Rules

Deliver the `.xml` library file. If the user needs one-click loading, also provide the `https://app.diagrams.net/?splash=0&clibs=U...` URL after the file is hosted at a raw public URL.

Check licenses before bundling third-party icons or vendor logos. Prefer user-provided assets, draw.io built-in editable shapes, or original simple vector fragments.

For polished reusable libraries, prefer native draw.io stencils for domain icons, use editable XML fragments for cards and templates, and avoid mixed-size previews where the sidebar thumbnail crops labels or leaves large blank margins.
