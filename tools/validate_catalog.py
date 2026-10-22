#!/usr/bin/env python3
"""Validate the Stereograph Archive catalog (schema v1) and, optionally,
its preservation fixity manifest.

Stdlib only. Controlled lists and the required-field set are read from
schema/catalog.schema.json so the schema file stays the single source of
truth; the structural checks are implemented here directly.

Usage:
  python3 tools/validate_catalog.py [--catalog data.json] [--fixity] [--v2]
                                    [--preservation ~/workspace/stereogram-archive-preservation]

With --v2 (Phase 1), the per-item records in records/ are also
validated against schema/catalog-v2.schema.json, and the generated
outputs (data.json and catalog-v2.json) are checked to be in sync
with the records: regenerate in memory and compare bytes.

Exit status: 0 when there are no errors (warnings are reported but do
not fail), 1 on any error.
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

BASE = Path(__file__).parent.parent
DEFAULT_PRESERVATION = Path.home() / 'workspace' / 'stereogram-archive-preservation'
ID_RE = re.compile(r'^STA-(\d{4})$')

TYPE_CHECKS = {
    'string': lambda v: isinstance(v, str),
    'integer': lambda v: isinstance(v, int) and not isinstance(v, bool),
    'number': lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    'array': lambda v: isinstance(v, list),
    'object': lambda v: isinstance(v, dict),
}


def is_jpeg(path):
    try:
        with open(path, 'rb') as fh:
            return fh.read(3) == b'\xff\xd8\xff'
    except OSError:
        return False


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def year_span(year_text):
    """Best-effort (lo, hi) year span stated by a v1 display date string,
    or None when the string states no usable span ('Undated', etc.)."""
    t = year_text.strip()
    if not t or t == 'Undated':
        return None
    spans = []
    for m in re.finditer(r'(1[78]\d\d|19\d\d)s\b', t):
        y = int(m.group(1))
        spans.append((y, y + 99) if y % 100 == 0 else (y, y + 9))
    rest = re.sub(r'(1[78]\d\d|19\d\d)s\b', ' ', t)
    for m in re.finditer(r'\b(1[78]\d\d|19\d\d)\b', rest):
        y = int(m.group(1))
        spans.append((y, y))
    if not spans:
        return None
    return min(s[0] for s in spans), max(s[1] for s in spans)


def main():
    ap = argparse.ArgumentParser(description='Validate the archive catalog (schema v1)')
    ap.add_argument('--catalog', default=str(BASE / 'data.json'))
    ap.add_argument('--schema', default=str(BASE / 'schema' / 'catalog.schema.json'))
    ap.add_argument('--fixity', action='store_true',
                    help='also verify fixity-manifest coverage and rectified hashes')
    ap.add_argument('--v2', action='store_true',
                    help='also validate records/ against the v2 schema and '
                         'check the generated outputs are in sync')
    ap.add_argument('--records', default=str(BASE / 'records'),
                    help='records directory (for --v2)')
    ap.add_argument('--preservation', default=str(DEFAULT_PRESERVATION),
                    help='preservation store root (for --fixity)')
    args = ap.parse_args()

    errors, warnings = [], []

    schema = json.loads(Path(args.schema).read_text())
    item_schema = schema['$defs']['item']
    required = item_schema['required']
    props = item_schema['properties']
    enums = {k: v['items']['enum'] if v.get('type') == 'array' and 'items' in v
             else v.get('enum') for k, v in props.items()}

    try:
        catalog = json.loads(Path(args.catalog).read_text())
    except Exception as e:
        print(f'ERROR: catalog does not parse: {e}')
        return 1
    if not isinstance(catalog, list):
        print('ERROR: catalog root is not an array')
        return 1

    seen_id, seen_source, seen_title = {}, {}, {}
    prev_acc = 0
    warn_unrecorded_coll = warn_unrecorded_place = warn_empty_blurb = 0
    warn_date = []

    for idx, it in enumerate(catalog):
        tag = it.get('id', f'index {idx}') if isinstance(it, dict) else f'index {idx}'
        if not isinstance(it, dict):
            errors.append(f'{tag}: item is not an object')
            continue
        for field in required:
            if field not in it:
                errors.append(f'{tag}: missing required field "{field}"')
        for field, spec in props.items():
            if field not in it:
                continue
            v = it[field]
            t = spec.get('type')
            if t and not TYPE_CHECKS[t](v):
                errors.append(f'{tag}: field "{field}" should be {t}, got {type(v).__name__}')
                continue
            enum = enums.get(field)
            if enum:
                if isinstance(v, list):
                    for el in v:
                        if el not in enum:
                            errors.append(f'{tag}: field "{field}" value "{el}" not in {enum}')
                elif v not in enum:
                    errors.append(f'{tag}: field "{field}" value "{v}" not in {enum}')
            pat = spec.get('pattern')
            if pat and isinstance(v, str) and not re.match(pat, v):
                errors.append(f'{tag}: field "{field}" value "{v}" fails pattern {pat}')

        m = ID_RE.match(it.get('id', '') if isinstance(it.get('id'), str) else '')
        if not m:
            errors.append(f'{tag}: id does not match ^STA-\\d{{4}}$')
            acc = None
        else:
            acc = int(m.group(1))
            if acc in seen_id:
                errors.append(f'{tag}: duplicate id (also at index {seen_id[acc]})')
            seen_id[acc] = idx
            if acc <= prev_acc:
                errors.append(f'{tag}: ids not in ascending order (previous accession {prev_acc})')
            prev_acc = max(prev_acc, acc)
        for key, seen in (('source', seen_source), ('title', seen_title)):
            v = it.get(key)
            if isinstance(v, str):
                if v in seen:
                    errors.append(f'{tag}: duplicate {key} (also {seen[v]})')
                seen[v] = tag

        if isinstance(it.get('w'), int) and it['w'] <= 0:
            errors.append(f'{tag}: w must be positive')
        if isinstance(it.get('h'), int) and it['h'] <= 0:
            errors.append(f'{tag}: h must be positive')

        rect = it.get('rect')
        if isinstance(rect, str):
            rp = BASE / rect
            if not rp.exists():
                errors.append(f'{tag}: rect file missing: {rect}')
            elif rp.stat().st_size == 0:
                errors.append(f'{tag}: rect file empty: {rect}')
            elif not is_jpeg(rp):
                errors.append(f'{tag}: rect file is not a JPEG: {rect}')

        px = it.get('px')
        if isinstance(px, dict):
            for k in ('s', 'L', 'R', 'g', 'ar'):
                if k not in px:
                    errors.append(f'{tag}: px missing "{k}"')
            for k, want in (('L', 6), ('R', 6), ('g', 2)):
                v = px.get(k)
                if not (isinstance(v, list) and len(v) == want
                        and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v)):
                    errors.append(f'{tag}: px.{k} must be {want} numbers')
            if 'ar' in px and not isinstance(px['ar'], (int, float)):
                errors.append(f'{tag}: px.ar must be a number')
            if 's' in px and not (isinstance(px['s'], str) and px['s']):
                errors.append(f'{tag}: px.s must be a non-empty string')

        # ---- warnings (legacy debt; reported, never fatal) ----
        if it.get('coll') == 'Source unrecorded':
            warn_unrecorded_coll += 1
        if it.get('place') == 'Place unrecorded':
            warn_unrecorded_place += 1
        if it.get('blurb') == '':
            warn_empty_blurb += 1
        if isinstance(it.get('year'), str) and isinstance(it.get('sy'), int):
            span = year_span(it['year'])
            if span and not (span[0] <= it['sy'] <= span[1]):
                warn_date.append(f'{tag}: sy {it["sy"]} outside stated span '
                                   f'{span[0]}–{span[1]} ("{it["year"]}")')

    if warn_date:
        warnings.append(f'{len(warn_date)} item(s) whose sy falls outside the span '
                          f'stated by their year string (legacy date debt):')
        warnings.extend('  ' + w for w in warn_date)
    if warn_unrecorded_coll:
        warnings.append(f'{warn_unrecorded_coll} item(s) with coll = "Source unrecorded"')
    if warn_unrecorded_place:
        warnings.append(f'{warn_unrecorded_place} item(s) with place = "Place unrecorded"')
    if warn_empty_blurb:
        warnings.append(f'{warn_empty_blurb} item(s) with an empty blurb '
                          f'(source record has no description)')

    if args.v2:
        try:
            import build_catalog
            records = build_catalog.load_records(args.records)
        except Exception as e:
            errors.append(f'v2: records failed validation: {e}')
            records = None
        if records is not None:
            if len(records) != len(catalog):
                errors.append(f'v2: {len(records)} records but '
                              f'{len(catalog)} catalog items')
            if [r['id'] for r in records] != [it.get('id') for it in catalog]:
                errors.append('v2: record ids do not match catalog ids in order')
            data_bytes = Path(args.catalog).read_bytes()
            if build_catalog.render_data_json(records).encode() != data_bytes:
                errors.append('v2: data.json is out of sync with records/ '
                              '(run tools/build_catalog.py)')
            v2_path = BASE / 'catalog-v2.json'
            if not v2_path.exists():
                errors.append('v2: catalog-v2.json is missing '
                              '(run tools/build_catalog.py)')
            elif build_catalog.render_catalog_v2(records).encode() \
                    != v2_path.read_bytes():
                errors.append('v2: catalog-v2.json is out of sync with '
                              'records/ (run tools/build_catalog.py)')

    if args.fixity:
        pres = Path(args.preservation)
        man_path = pres / 'fixity-manifest.json'
        if not man_path.exists():
            errors.append(f'fixity: manifest not found at {man_path}')
        else:
            manifest = json.loads(man_path.read_text())
            for it in catalog:
                sid = it.get('id')
                entry = manifest.get(sid)
                if not entry:
                    errors.append(f'fixity: {sid}: no fixity-manifest entry')
                    continue
                for kind in ('master', 'rectified'):
                    if kind not in entry:
                        errors.append(f'fixity: {sid}: manifest entry lacks "{kind}"')
                rec = entry.get('rectified') or {}
                rp = BASE / (it.get('rect') or '')
                if rec.get('sha256') and rp.exists():
                    actual = sha256_of(rp)
                    if actual != rec['sha256']:
                        errors.append(f'fixity: {sid}: rectified sha256 mismatch '
                                      f'(manifest {rec["sha256"][:12]}…, file {actual[:12]}…)')
                master = entry.get('master') or {}
                if master.get('status') == 'ok':
                    mp = pres / (master.get('file') or '')
                    if not mp.exists():
                        errors.append(f'fixity: {sid}: master file missing: {master.get("file")}')
                    elif master.get('bytes') is not None and mp.stat().st_size != master['bytes']:
                        errors.append(f'fixity: {sid}: master byte size mismatch '
                                      f'(manifest {master["bytes"]}, file {mp.stat().st_size})')

    print(f'catalog: {args.catalog}')
    print(f'items: {len(catalog)}')
    for w in warnings:
        print('WARNING:', w)
    for e in errors:
        print('ERROR:', e)
    print(f'result: {len(errors)} error(s), {len(warnings)} warning group(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
