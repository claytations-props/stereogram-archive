# Ingest SOP — How a Batch Enters the Archive

As of Phase 0 (October 21, 2026). The pipeline is: harvest → dedupe →
review → merge (assigns STA numbers) → validate → one atomic commit →
push → live verify. Tools: `tools/batch_engine.py` (staging only),
`tools/merge_batch.py` (merge + publish), `tools/validate_catalog.py`
(schema, catalog, and fixity checks).

## 1. Harvest (staging only)

```
TMPDIR=~/workspace/.tmp ~/workspace/.venvs/cv/bin/python tools/batch_engine.py \
  --query "<commons search>" --count N --staging staging/<batch-name>
# or: --files "File:..." "File:..." --staging staging/<batch-name>
```

- The engine filters to public-domain / CC0 licenses (Commons
  `LicenseShortName`), dedupes against the published catalog by source
  URL, filename, and normalized title, rectifies each scan with the
  pipeline's quality gates, and writes a `manifest.json`.
- Candidates get batch-local IDs (`CAND-01`, …). Staged pair files are
  named by candidate ID. **No STA numbers exist before merge.**
- For every passed candidate the engine also downloads the **original**
  file into `staging/<batch-name>/masters/` and records its SHA-256,
  byte size, Commons page ID, and Commons SHA-1 in the manifest.
- The manifest records the query or file list and run start/finish
  timestamps and the engine version.

## 2. Dedupe inside the run

- After rectification, the engine compares passed candidates' source
  scans pairwise (resized grayscale Pearson correlation). A later
  candidate at correlation ≥ 0.99 against an earlier kept one is the
  same scan (typically a `.jpg`/`.png` double upload on Commons) and is
  moved to `skipped_duplicates` in the manifest with its correlation.
  Genuinely different negatives score well below 0.99 and are kept.

## 3. Review

- Read the manifest: passed, held (with gate reasons), license skips,
  duplicates, errors. Held items stay held; they are not forced in.
- Descriptive text is never edited by hand. Titles, descriptions,
  places, and dates come from the source records (Archive Policy §4).
  Engine heuristics for place/year/collection may be corrected only from
  information in the item's own title, category, or source record.

## 4. Merge and publish

```
~/workspace/.venvs/cv/bin/python tools/merge_batch.py --staging staging/<batch-name> --push
```

The merge tool, in order:

1. Loads the manifest's passed candidates (legacy manifests with
   provisional STA-style IDs are treated as candidates and remapped).
2. Assigns the next STA numbers exactly once, in manifest order.
3. Copies pair files into `rect/` as `(accession − 1).jpg`, sets each
   entry's `rect` field, and builds a v2 record per item (see below),
   written to `records/STA-####.json` — the catalog of record.
4. Copies staged masters into the preservation store
   (`~/workspace/stereogram-archive-preservation/masters/STA-####/`) and
   updates `fixity-manifest.json`, hashing the new rectified files too.
5. Regenerates `data.json` and `catalog-v2.json` from ALL records with
   `tools/build_catalog.py`, then runs `tools/validate_catalog.py --v2`
   (v2 records, generated-output sync, v1 checks, fixity). **On any
   validation failure the merge rolls back: catalog outputs, records,
   `rect/`, and the preservation store are restored and the tool exits
   nonzero with the reason.**
6. Stages `data.json`, `catalog-v2.json`, the new `records/` files, and
   the new `rect/` files and creates ONE atomic commit:
   `Add N stereographs (<batch>) — STA-####–STA-####`.
7. With `--push`: pushes, then polls the live `data.json` (cache-busted)
   until it matches the local catalog byte for byte, allowing for
   GitHub Pages rebuild lag.

How a v2 record is built at merge (all mechanical — `tools/v2fields.py`):

- The date guard runs first: a candidate year whose only title evidence
  is the creator's life dates — a life range, a "b. YYYY" birth year, a
  "d. YYYY" death year, or a birth-uncertainty form ("1818 or 1824-after
  1901") — becomes Undated (year `Undated`, sy 1900, era `undated`),
  unless the title states the view's own date. A real view date stated
  in the title wins.
- `repository` / `collection_name` / `publisher` come from the `coll`
  split table in the Data Dictionary; `creator` / `creator_dates` are
  extracted from the title's "by …" attribution; `date_edtf` /
  `date_start` / `date_end` follow the dictionary's EDTF conventions;
  `rights_uri` / `rights_basis` follow its rights rules;
  `publisher_series` stays null unless the batch's source evidence
  states one.
- Source pins: page ID and SHA-1 come from the staged master record.
  `source_revision_id` is null at merge time; a later pin pass fills it
  from the Commons API by page ID (as the Phase 1 migration did).

## 5. Staging retention

- `staging/` is git-ignored working space, not part of the repository.
- Keep a batch's `manifest.json` and review notes until its merge has
  been verified live. After a verified merge, the batch's downloads and
  staged masters may be deleted: originals live in the preservation
  store, pairs live in `rect/`, and the manifest's facts that matter
  (IDs, hashes) are in the fixity manifest and the commit.
- Never delete the staging folder of a batch that has not been merged.
