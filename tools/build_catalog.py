#!/usr/bin/env python3
"""Generate the catalog outputs from the per-item v2 records.

Since Phase 1, records/STA-####.json (schema/catalog-v2.schema.json)
is the catalog of record. This generator is the ONLY writer of:

  data.json         - the v1 item shape plus the appended Phase 1
                      fields; consumed by index.html and vr.html
  catalog-v2.json   - the full v2 records as a single array

Both outputs are deterministic: running the generator twice on the
same records produces byte-identical files. Records are validated
structurally against the v2 schema before anything is written; any
error aborts the build with nothing written.

Usage: python3 tools/build_catalog.py [--records records]
                                      [--out-data data.json]
                                      [--out-v2 catalog-v2.json]
The render_* functions are importable (tools/validate_catalog.py
--v2 uses them for its in-sync check).
"""
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import v2fields

BASE = Path(__file__).parent.parent
ID_RE = re.compile(r'^STA-\d{4}$')

_TYPE_CHECKS = {
    'string': lambda v: isinstance(v, str),
    'integer': lambda v: isinstance(v, int) and not isinstance(v, bool),
    'number': lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    'array': lambda v: isinstance(v, list),
    'object': lambda v: isinstance(v, dict),
    'null': lambda v: v is None,
}


def _type_ok(spec, v):
    t = spec.get('type')
    if t is None:
        return True
    types = t if isinstance(t, list) else [t]
    return any(_TYPE_CHECKS[x](v) for x in types)


def validate_record(rec, schema, tag):
    """Stdlib structural validation of one record against the v2
    schema (types, required, enums, patterns), in the same style as
    tools/validate_catalog.py. Returns a list of error strings."""
    errors = []
    props = schema['properties']
    for field in schema['required']:
        if field not in rec:
            errors.append(f'{tag}: missing required field "{field}"')
    for field, spec in props.items():
        if field not in rec:
            continue
        v = rec[field]
        ref = spec.get('$ref')
        if ref == '#/$defs/nullableString':
            if not (v is None or isinstance(v, str)):
                errors.append(f'{tag}: "{field}" must be a string or null')
            continue
        if ref == '#/$defs/nullableInteger':
            if not (v is None or (isinstance(v, int) and not isinstance(v, bool))):
                errors.append(f'{tag}: "{field}" must be an integer or null')
            continue
        if ref == '#/$defs/px':
            if not isinstance(v, dict):
                errors.append(f'{tag}: "px" must be an object')
                continue
            for k in ('s', 'L', 'R', 'g', 'ar'):
                if k not in v:
                    errors.append(f'{tag}: px missing "{k}"')
            for k, want in (('L', 6), ('R', 6), ('g', 2)):
                vv = v.get(k)
                if not (isinstance(vv, list) and len(vv) == want
                        and all(isinstance(x, (int, float))
                                and not isinstance(x, bool) for x in vv)):
                    errors.append(f'{tag}: px.{k} must be {want} numbers')
            continue
        if not _type_ok(spec, v):
            errors.append(f'{tag}: "{field}" has the wrong type')
            continue
        enum = spec.get('enum')
        if enum and v not in enum:
            errors.append(f'{tag}: "{field}" value {v!r} not in enum')
        items = spec.get('items') or {}
        ienum = items.get('enum')
        if ienum and isinstance(v, list):
            for el in v:
                if el not in ienum:
                    errors.append(f'{tag}: "{field}" value {el!r} not in enum')
        pat = spec.get('pattern')
        if pat and isinstance(v, str) and not re.match(pat, v):
            errors.append(f'{tag}: "{field}" value {v!r} fails pattern')
    extra = set(rec) - set(props)
    if extra:
        errors.append(f'{tag}: unexpected field(s) {sorted(extra)}')
    if isinstance(rec.get('id'), str) and not ID_RE.match(rec['id']):
        errors.append(f'{tag}: id does not match ^STA-\\d{{4}}$')
    if rec.get('facets') != rec.get('cats'):
        errors.append(f'{tag}: facets must mirror cats in v2')
    return errors


def load_records(records_dir):
    schema = json.loads(
        (BASE / 'schema' / 'catalog-v2.schema.json').read_text())
    files = sorted(Path(records_dir).glob('STA-*.json'))
    if not files:
        raise RuntimeError(f'no records found in {records_dir}')
    records, errors = [], []
    for f in files:
        rec = json.loads(f.read_text())
        errors.extend(validate_record(rec, schema, f.stem))
        records.append(rec)
    records.sort(key=lambda r: r['id'])
    ids = [r['id'] for r in records]
    if len(ids) != len(set(ids)):
        errors.append('duplicate record ids')
    if [f.stem for f in files] != ids:
        errors.append('record filenames do not match record ids in order')
    if errors:
        raise RuntimeError('record validation failed:\n  ' + '\n  '.join(errors))
    return records


def render_data_json(records):
    items = [v2fields.generated_item(r) for r in records]
    return json.dumps(items, indent=1, ensure_ascii=False)


def render_catalog_v2(records):
    return json.dumps(records, indent=1, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser(description='Generate data.json and '
                                               'catalog-v2.json from records/')
    ap.add_argument('--records', default=str(BASE / 'records'))
    ap.add_argument('--out-data', default=str(BASE / 'data.json'))
    ap.add_argument('--out-v2', default=str(BASE / 'catalog-v2.json'))
    args = ap.parse_args()
    records = load_records(args.records)
    data_text = render_data_json(records)
    v2_text = render_catalog_v2(records)
    Path(args.out_data).write_text(data_text)
    Path(args.out_v2).write_text(v2_text)
    print(f'generated {args.out_data} and {args.out_v2} '
          f'from {len(records)} records')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except RuntimeError as e:
        print(f'ERROR: {e}')
        sys.exit(1)
