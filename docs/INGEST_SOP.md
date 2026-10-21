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
   entry's `rect` field, and appends the entries to `data.json`.
4. Copies staged masters into the preservation store
   (`~/workspace/stereogram-archive-preservation/masters/STA-####/`) and
   updates `fixity-manifest.json`, hashing the new rectified files too.
5. Runs `tools/validate_catalog.py` (catalog + fixity). **On any
   validation failure the merge rolls back: `data.json` and `rect/` are
   left untouched and the tool exits nonzero with the reason.**
6. Stages `data.json` and the new `rect/` files and creates ONE atomic
   commit: `Add N stereographs (<batch>) — STA-####–STA-####`.
7. With `--push`: pushes, then polls the live `data.json` (cache-busted)
   until it matches the local catalog byte for byte, allowing for
   GitHub Pages rebuild lag.

## 5. Staging retention

- `staging/` is git-ignored working space, not part of the repository.
- Keep a batch's `manifest.json` and review notes until its merge has
  been verified live. After a verified merge, the batch's downloads and
  staged masters may be deleted: originals live in the preservation
  store, pairs live in `rect/`, and the manifest's facts that matter
  (IDs, hashes) are in the fixity manifest and the commit.
- Never delete the staging folder of a batch that has not been merged.
