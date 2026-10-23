# Phase 3 — Interoperability Outputs

Phase 3 of the October 21, 2026 design review: additive, machine-generated
outputs so other archives, IIIF consumers, and search engines can ingest
the catalog without screen-scraping the site. Built October 23, 2026 with
`tools/build_phase3.py`, a standalone generator that reads `records/`
(the catalog of record) and writes only the paths below. It does not touch
`tools/build_catalog.py`, the validator, the pages, or any Phase 2A
generated output; the catalog build remains the single owner of those.

## Outputs

| Path | Contents |
|---|---|
| `iiif/<STA>.json` | IIIF Presentation API 3.0 manifest, one per item: a single Canvas painting the item's rectified pair, served from the Internet Archive (`ASSET_BASE` in `tools/build_catalog.py`, currently `https://archive.org/download/stereogram-archive-images/`). |
| `iiif/collection.json` | IIIF Collection listing every manifest, in STA order. |
| `ld/<STA>.json` | schema.org `Photograph` JSON-LD, one per item. |
| `exports/finding-aid.xml` | EAD3 finding aid: collection-level description with one series component per subject shelf and one item component per card. |

First generation (2026-10-23): 1,053 records → 1,053 manifests + 1
collection, 1,053 JSON-LD files, 1 EAD with 1,053 item components.

## Rules carried over from the catalog

- **No authored text.** Every descriptive value is copied verbatim from
  the item's own record: manifest label = record title; IIIF metadata
  entries = repository, collection_name, publisher, creator,
  creator_dates, year (display date), place, license, each omitted when
  the record's field is null; manifest `rights` = the record's
  `rights_uri` when present (absent for the 26 "No restrictions" items,
  whose records carry no controlled rights URI). The JSON-LD follows the
  same rule. The EAD uses the archive's own existing name ("The
  Stereograph Archive") and the series shelf labels exactly as
  `index.html` displays them; item titles, dates, and STA ids are the
  records' own.
- **Deterministic.** Same records in, byte-identical files out (the
  generator builds twice in-process and compares hashes before writing).
- **Self-validating.** Each run checks: every record has a manifest and a
  JSON-LD file; all JSON parses; the EAD is well-formed XML with one item
  component per record; every manifest image URL and every JSON-LD
  `contentUrl` equals `ASSET_BASE` + the record's `rect` path; every EAD
  item links its image under the same base.

## Decisions worth knowing

- **Image dimensions are measured, not copied.** A record's `w`/`h` are
  the *source scan's* dimensions, so the manifests do not use them. Each
  rectified pair's true pixel size is read from the file itself: the
  local `rect/` copy when one is in the working tree (fresh waves),
  otherwise the JPEG header of the served IA file (range fetch). First
  generation: 27 local + 1,026 via IA headers, 0 unmeasured. Items whose
  size cannot be measured get a Canvas in the pair's measured aspect
  (2 × the record's `va`) and an image body without width/height —
  stated nowhere rather than stated wrong.
- **Multi-shelf items hang once in the finding aid**, under their first
  facet in the record's own order (229 of 1,053 items carry two facets).
  Manifests and JSON-LD are per-item and unaffected.
- **JSON-LD `dateCreated`** appears only when the record's `date_edtf`
  is a plain ISO date (518 of 1,053); approximate/uncertain EDTF forms
  (`1865~`, `188X`, intervals) are omitted rather than mis-stated as
  exact. `creator` is modeled as schema.org `Person` for every record —
  the catalog does not distinguish persons from firms in that field.
  `contentLocation` is omitted for the 10 items whose place is
  `Place unrecorded`.
- **Not built:** IIIF image tiles / an image server (manifests reference
  the whole rectified image; tiling is an optional later step) and
  OAI-PMH (only if an aggregator asks). Both were non-goals in the
  design review.

## Regeneration

Run `python3 tools/build_phase3.py` after any merge that changes
`records/`. It picks up whatever records exist at run time, so during
Wave 5 it can be regenerated vein by vein; a final regeneration when the
wave settles folds in the last items. Live endpoints once pushed:
`https://vrparlor.com/iiif/STA-0001.json`,
`https://vrparlor.com/iiif/collection.json`,
`https://vrparlor.com/ld/STA-0001.json`,
`https://vrparlor.com/exports/finding-aid.xml`.
