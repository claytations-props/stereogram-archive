# Archive Policy — The Stereograph Archive

Adopted October 21, 2026 (Phase 0). This document states the rules the
catalog, the tools, and any future redesign must follow. Changes to this
policy should be deliberate, dated, and recorded here.

## 1. Identifier policy

- Every accepted item carries one accession identifier of the form
  `STA-####` (for example `STA-0175`).
- An STA number is assigned **exactly once**, at acceptance time, by
  `tools/merge_batch.py` when a staged batch is merged into the catalog.
  Numbers are assigned in merge order and are never reused and never
  renumbered.
- Candidates in staging carry batch-local candidate IDs (`CAND-01`,
  `CAND-02`, …), never STA numbers. A candidate that is held, rejected,
  or found to be a duplicate never receives an STA number.
- If an item is ever withdrawn, its STA number stays as a tombstone for
  that item; the number is not recycled. Gaps in the sequence are
  acceptable and expected over time.
- Item identity is the STA number, never an item's position in
  `data.json` and never its image filename. Each record names its
  rectified image explicitly in its `rect` field.
- Canonical item URL today: the site URL plus `#STA-####`
  (for example `https://claytations-props.github.io/stereogram-archive/#STA-0175`).
  A future migration to ID-only paths must keep the hash form resolving.

## 2. Preservation policy

- The preservation masters live **outside** the public repository, in
  `~/workspace/stereogram-archive-preservation/` on the archive's working
  machine. For every item, the store holds the original source file
  exactly as retrieved from Wikimedia Commons (`masters/STA-####/…`),
  before any rectification.
- Fixity is SHA-256. `preservation/fixity-manifest.json` records, for
  every item, the master file's hash, byte size, MIME type, Commons page
  and revision IDs, Commons SHA-1, and retrieval timestamp, plus the
  hash and size of the rectified derivative in the repository.
  `preservation/manifest-sha256.txt` is a BagIt-style checksum manifest
  over the master files so the store can be verified with
  `sha256sum -c manifest-sha256.txt`.
- Verification cadence: fixity is checked whenever a batch is merged
  (`tools/validate_catalog.py --fixity` runs as part of the merge), and a
  full re-verification of every master is recommended at least quarterly.
- Copies status, stated honestly: as of adoption, the masters exist on
  one machine (this VM). The rectified access copies are additionally in
  the public GitHub repository, and the upstream originals remain on
  Wikimedia Commons. **An independent off-VM copy of the masters store is
  an open gap** and is the first preservation task of a later phase.
  GitHub (code + access copies) is the dissemination system, not the
  preservation system.

## 3. Arrangement note

- The top level of the archive ("collections", the `coll` field) is a
  **provenance** grouping: where the scan came from.
- The `cats` values (Falls & Rivers, Cities & Towns, Civil War, …) are
  **subject facets** used as browse shelves. The v1 interface labels them
  "series"; that word is a misnomer. A publisher's printed series on a
  card mount is a different concept and becomes its own field in
  Phase 1; the subject values will be renamed facets at the same time.
- Known v1 conflation, recorded as Phase 1 debt: `coll` mixes holding
  repositories (Library of Congress), named collections (Robert N.
  Dennis Collection), publishers (Keystone View Company), and an access
  program (Getty Open Content) in one field. Phase 1 splits these roles.
  **Resolved 2026-10-21 (Phase 1):** the roles now live in `repository`,
  `collection_name`, and `publisher`; `coll` is retained verbatim as the
  recorded provenance label. See §5 and `docs/migration-phase1.md`.

## 4. Source fidelity rule

No text about an image is authored by the archive's operators. Titles,
descriptions (the `blurb` field), places, and dates come from the source
archive's own records (NYPL / Dennis Collection / Wikimedia Commons),
verbatim or mechanically cleaned only. If a source record has no
description, the item shows none. The measured condition report (`cond`)
is the one exception: it is data about our own rectified copy, produced
by the rectification pipeline's measurements.

## 5. Catalog of record (Phase 1 amendment, 2026-10-21)

- The catalog of record is the set of per-item records in `records/`
  (`records/STA-####.json`), conforming to `schema/catalog-v2.schema.json`.
- `data.json` and `catalog-v2.json` are generated access outputs of
  `tools/build_catalog.py`. They are never edited by hand; any change to
  catalog content is made in the records and regenerated.
  `tools/validate_catalog.py --v2` verifies the outputs are in sync.
- v2 field derivations follow the same fidelity rule as §4: values are
  carried verbatim, extracted mechanically from the source's own
  statements, or assigned by rule as controlled identifiers. The
  derivation rules are documented in `docs/DATA_DICTIONARY.md`; the
  migration itself is logged in `docs/migration-phase1.md`.
