# stereogram-archive
The Stereograph Archive - a dark gallery of public domain vintage stereograph photographs

Catalog schema: **v1** (fields documented in [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md); machine-readable schema in [schema/catalog.schema.json](schema/catalog.schema.json), enforced by `tools/validate_catalog.py`).

Project documentation:

- [Archive Policy](docs/ARCHIVE_POLICY.md) — identifier policy, preservation policy, arrangement note
- [Data Dictionary](docs/DATA_DICTIONARY.md) — every catalog field, its meaning, source, and known v1 debt
- [Ingest SOP](docs/INGEST_SOP.md) — how batches are harvested, deduplicated, merged, validated, and published
