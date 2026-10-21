# Data Dictionary — Catalog Schema v1

`data.json` is a JSON array of item objects. Every item carries the same
24 fields. This dictionary states what each field means in v1, where its
value comes from, and which v1 conflations are known Phase 1 debt.
Machine-readable form: `schema/catalog.schema.json`, enforced by
`tools/validate_catalog.py`.

## Identity and files

| Field | Type | Meaning | Source |
|---|---|---|---|
| `id` | string | Accession identifier `STA-####`, assigned once at merge, never reused or renumbered (see Archive Policy §1) | Archive (merge tool) |
| `rect` | string | Repo-relative path of this item's rectified pair, e.g. `rect/174.jpg`. The explicit asset reference: pages must use this field, not derive a path from the ID or array position | Archive (merge tool) |
| `img` | string (URL) | Wikimedia thumbnail URL (1920px) of the source scan; used by the gallery for card/hero display and the viewer's "Original Pair" mode | Wikimedia Commons |
| `full` | string (URL) | Wikimedia URL of the original source file (may be JPG, PNG, or TIFF) | Wikimedia Commons |
| `source` | string (URL) | Wikimedia Commons file page for the scan; the citation link shown on the record | Wikimedia Commons |
| `w`, `h` | integer | Pixel dimensions of the original source file | Wikimedia Commons |

## Descriptive fields (source-derived; never authored — Archive Policy §4)

| Field | Type | Meaning | Source |
|---|---|---|---|
| `title` | string | The source archive's own file title, mechanically cleaned only (file prefix/extension and a trailing Dennis-collection suffix removed) | Source record |
| `blurb` | string | The source record's own description, mechanically cleaned (HTML stripped, whitespace collapsed). Empty string when the source has no description or its description merely restates the title | Source record |
| `place` | string | Depicted place as a display string. v1 values come from the title or a small gazetteer in the batch engine; `Place unrecorded` when unknown | Source record / engine heuristic |
| `year` | string | Display date exactly as presented, e.g. `1882`, `c. 1865`, `1831–1878`, `Undated` | Source record / engine heuristic |
| `sy` | integer | Sort year used for ordering and era derivation. **v1 debt:** semantics are inconsistent across legacy batches — start year for ranges in the engine, midpoint in older cleanup passes, and photographer life dates in some titles were mistaken for item dates (known on several Leadville cards). Phase 1 replaces this with EDTF-normalized start/end dates | Derived |
| `era` | string | One of `early`, `mid`, `late`, `undated`, derived from `sy` | Derived |
| `cats` | array of strings | Subject facet values from the controlled list (`water`, `mountains`, `cities`, `war`, `world`, `people`, `oddities`). Misnamed "series" in the v1 UI; they are facets, not archival series (Archive Policy §3) | Engine heuristic |
| `coll` | string | Provenance label as recorded. **v1 debt:** mixes holding repositories, named collections, publishers, and an access program in one field; `Source unrecorded` is the unknown sentinel (32 items at Phase 0). Phase 1 splits this into holding institution, named collection, and publisher | Source record / engine heuristic |
| `license` | string | Rights label from the source record's license short name: `Public domain`, `No restrictions`, or `CC0`. Ingest accepts only these | Source record |

## Rectification and technical fields (about our copy, not the source)

| Field | Type | Meaning | Source |
|---|---|---|---|
| `vert` | number | Residual vertical error of the rectified pair, percent of height, measured on the shipped pixels | Rectification pipeline |
| `rot` | number | Residual rotation of the rectified pair, degrees | Rectification pipeline |
| `range` | number | Stereo depth range of the rectified pair, percent of frame width | Rectification pipeline |
| `f` | number | Size factor the pair is hung at in the VR Parlor (fraction of full size) after the depth budget is applied | Rectification pipeline |
| `depth` | string | Depth word derived from `range`: `Gentle`, `Moderate`, or `Deep` | Derived |
| `va` | number | Aspect ratio (width/height) of one eye of the rectified pair; equal to `px.ar` in v1 | Rectification pipeline |
| `px` | object | Live-warp parameters for rendering the pair from the source scan in the VR Parlor: `s` = scan URL, `L`/`R` = per-eye affine maps in scan UV space, `g` = per-eye brightness gains, `ar` = eye aspect ratio | Rectification pipeline |
| `cond` | string | Measured condition report sentence generated from the pipeline's own numbers (`vert`, `rot`, `range`, `f`). The single permitted piece of archive-generated text, because it describes our copy, not the image | Generated from measurements |

## Known v1 debt (Phase 1, do not fix piecemeal)

1. `coll` mixes repository / collection / publisher / program roles.
2. `sy` has no single consistent meaning; `year` is free text; some legacy
   dates derive from photographer life dates in titles.
3. `blurb` is the source description verbatim; long Library of Congress
   records include full catalog text (call numbers, repository lines).
4. `cats` are subject facets misnamed "series"; there is no field yet for
   a publisher's printed series.
5. `va` duplicates `px.ar`.
6. Rights are a short label only; no rights URI, credit line, or
   assessment basis is stored yet.
