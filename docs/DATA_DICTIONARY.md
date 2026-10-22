# Data Dictionary — Catalog Schema v2

The catalog of record is the set of per-item records in `records/`
(`records/STA-####.json`), one file per item, conforming to
`schema/catalog-v2.schema.json` (draft 2020-12). `data.json` and
`catalog-v2.json` are **generated access outputs**, produced by
`tools/build_catalog.py` from the records; never edit them by hand.
`data.json` keeps the v1 item shape plus the appended v2 fields, so the
site pages consume it unchanged in structure. `tools/validate_catalog.py
--v2` validates the records and checks both generated outputs are in
sync. The Phase 1 migration is logged in `docs/migration-phase1.md`.

Every descriptive value is carried verbatim from the source record,
extracted mechanically from the source's own statements, or assigned by
rule as a controlled identifier. No descriptive text is authored
(Archive Policy §4).

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
| `place` | string | Depicted place as a display string, from the title or the source record; `Place unrecorded` when unknown | Source record |
| `year` | string | Display date exactly as presented, e.g. `1882`, `c. 1865`, `Undated`. v2 rule: a year whose only evidence is the creator's life dates is not a date for the photograph — the record is `Undated` (see the date guard in `tools/v2fields.py`) | Source record |
| `sy` | integer | Sort year used for ordering and era derivation. Retained for v1 compatibility; the authoritative normalized dates are `date_start` / `date_end` below | Derived |
| `era` | string | One of `early`, `mid`, `late`, `undated`, derived from `sy` | Derived |
| `cats` | array of strings | Subject facet values from the controlled list (`water`, `mountains`, `cities`, `war`, `world`, `people`, `oddities`). Facets, not archival series (Archive Policy §3). Named `facets` in the v2 model; the generated `data.json` keeps the key `cats` | Engine heuristic |
| `coll` | string | v1 provenance label, retained verbatim in every record for provenance. Its information content is split into `repository` / `collection_name` / `publisher` below | Source record |
| `license` | string | Rights label from the source record's license short name: `Public domain`, `No restrictions`, or `CC0`. Ingest accepts only these | Source record |

## v2 fields (Phase 1)

| Field | Type | Meaning | Derivation |
|---|---|---|---|
| `repository` | string \| null | Holding institution | Split of `coll` by rule (table below) |
| `collection_name` | string \| null | Named collection within the repository | Split of `coll` by rule (table below) |
| `publisher` | string \| null | Publisher imprint | Split of `coll` by rule (table below) |
| `creator` | string \| null | Photographer / maker, exactly as printed in the title's own "by …" attribution. Null when the title carries no attribution | Mechanical extraction from `title` |
| `creator_dates` | string \| null | The creator's life dates exactly as printed in that same attribution (e.g. `1843–1942`, `b. 1851`, `1818 or 1824-after 1901`). Never used as the item's date | Mechanical extraction from `title` |
| `date_edtf` | string \| null | The item's date in EDTF (ISO 8601-2), normalized from `year` only where the year states real evidence (conventions below). Null when Undated | Rule from `year` |
| `date_start`, `date_end` | integer \| null | Year bounds matching `date_edtf`, for range queries and sorting | Rule from `year` |
| `rights_uri` | string \| null | Controlled rights identifier (RightsStatements.org or Creative Commons), assigned by rule from `license` | Rule (below) |
| `rights_basis` | string | The basis for the rights assignment: the source archive's own rights marking, or the recorded Commons license evidence URL where the label has no controlled URI | Source record / Commons API |
| `publisher_series` | string \| null | The publisher's printed series, only where the item's own source record states it. Honestly sparse: 1 of 515 records at migration | Source record |
| `source_page_id` | integer | Wikimedia Commons page ID of the source file — the stable source pin | Fixity manifest / Commons API |
| `source_revision_id` | integer \| null | Revision ID of the Commons file page the metadata was taken from. May be null on freshly merged items until a pin pass fills it from the API | Commons API |
| `source_sha1` | string | SHA-1 of the source file as recorded by Wikimedia Commons; cross-checked against the preservation master's hash at migration | Fixity manifest / Commons API |

### The `coll` split

| v1 `coll` | repository | collection_name | publisher |
|---|---|---|---|
| `Robert N. Dennis Collection` | New York Public Library | Robert N. Dennis Collection of Stereoscopic Views | — |
| `Library of Congress` | Library of Congress | — | — |
| `The Metropolitan Museum of Art` | The Metropolitan Museum of Art | — | — |
| `National Archives` | National Archives | — | — |
| `Keystone View Company` | — | — | Keystone View Company |
| `International Stereoscopic View Co.` | — | — | International Stereoscopic View Co. |
| `Getty Open Content` | — | — | — (an access program, not a role) |
| `Source unrecorded` | — | — | — (unknown stays unknown) |

### EDTF conventions

- Explicit single year `YYYY` → `YYYY`; start = end = YYYY.
- A stated work range `YYYY–YYYY` → interval `YYYY/YYYY`; start/end are
  the stated bounds.
- `c. YYYY` → `YYYY~` (approximate); start/end = YYYY ± 5.
- `c. YYYY–YYYY` → `YYYY~/YYYY~`; start/end = the outer bounds ∓/± 5.
- A decade `YYY0s` → `YYY X` decade form (e.g. `1880s` → `188X`);
  start/end = the decade's bounds.
- A century `1800s` / `1900s` (in the source's "1800s–1920s" style) →
  `18XX` / `19XX`; bounds are the stated centuries' spans.
- `Date uncertain, 1800s–1920s` → `18XX/19XX`, start 1800, end 1929.
- `Undated` → `date_edtf`, `date_start`, `date_end` all null.

### Rights rules

- `Public domain` → `https://rightsstatements.org/vocab/NoC-US/1.0/`
  (No Copyright — United States), on the basis of the source archive's
  own public-domain marking.
- `CC0` → the exact Creative Commons deed URL recorded on the item's
  Commons page (at migration:
  `http://creativecommons.org/publicdomain/zero/1.0/deed.en`).
- `No restrictions` → `rights_uri` is null. The label's Commons evidence
  is the Flickr Commons "no known copyright restrictions" usage page,
  which is not a RightsStatements or Creative Commons identifier;
  `rights_basis` records that evidence instead of inventing a URI.

## Rectification and technical fields (about our copy, not the source)

| Field | Type | Meaning | Source |
|---|---|---|---|
| `vert` | number | Residual vertical error of the rectified pair, percent of height, measured on the shipped pixels | Rectification pipeline |
| `rot` | number | Residual rotation of the rectified pair, degrees | Rectification pipeline |
| `range` | number | Stereo depth range of the rectified pair, percent of frame width | Rectification pipeline |
| `f` | number | Size factor the pair is hung at in the VR Parlor (fraction of full size) after the depth budget is applied | Rectification pipeline |
| `depth` | string | Depth word derived from `range`: `Gentle`, `Moderate`, or `Deep` | Derived |
| `va` | number | Aspect ratio (width/height) of one eye of the rectified pair; equal to `px.ar` | Rectification pipeline |
| `px` | object | Live-warp parameters for rendering the pair from the source scan in the VR Parlor: `s` = scan URL, `L`/`R` = per-eye affine maps in scan UV space, `g` = per-eye brightness gains, `ar` = eye aspect ratio | Rectification pipeline |
| `cond` | string | Measured condition report sentence generated from the pipeline's own numbers (`vert`, `rot`, `range`, `f`). The single permitted piece of archive-generated text, because it describes our copy, not the image | Generated from measurements |

## Remaining known debt

1. `blurb` is the source description verbatim; long Library of Congress
   records include full catalog text (call numbers, repository lines).
   Whether to trim is the archivist's open call — do not trim without it.
2. `sy` remains as a v1 compatibility field; new consumers should use
   `date_start` / `date_end`.
3. `va` duplicates `px.ar` (kept for v1 consumers).
4. `publisher_series` is populated only where the source record states
   a series; backfilling it would require a per-item source review.
