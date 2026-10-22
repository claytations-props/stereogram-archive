#!/usr/bin/env python3
"""Phase 1 one-time migration: data.json (v1) -> records/ (v2).

Stages:
  1. FETCH  — pin every item's Commons source from the API (latest
     revision ID, file SHA-1, exact license URL, license short name,
     DateTimeOriginal) in batches of 50 page IDs taken from the fixity
     manifest; STA-0475 (whose manifest entry had no page ID) is
     resolved by file title. Cached to staging/phase1/api_cache.json.
  2. RECOVER — STA-0475's preservation master was never staged at
     merge; download the original, verify its SHA-1 against Commons,
     and complete its fixity-manifest entry.
  3. BUILD — write records/STA-####.json for all items using
     tools/v2fields.py derivations, applying exactly the authorized
     WS3 corrections (each one self-checked against its evidence and
     logged to staging/phase1/changes.json).

The migration never edits a title or a blurb. Display-field changes
are limited to the correction sets below; docs/migration-phase1.md is
the human-readable log produced from changes.json.

Usage: python3 tools/migrate_phase1.py [--fetch] [--build]
(default: both; --fetch forces a fresh API pass)
"""
import argparse, hashlib, json, re, sys, time
import urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import v2fields

BASE = Path(__file__).parent.parent
PRES = Path.home() / 'workspace' / 'stereogram-archive-preservation'
STAGE = BASE / 'staging' / 'phase1'
API = 'https://commons.wikimedia.org/w/api.php'
UA = {'User-Agent': 'StereographArchivePhase1/1.0 (metadata pinning; '
                   'contact: claytations@gmail.com)'}

# ---------------- authorized WS3 corrections (verified by inspection) ------
UNDATED_IDS = [
    # Leadville: year is the creator's life range / death year in the title
    'STA-0177', 'STA-0178', 'STA-0180', 'STA-0182', 'STA-0183',
    'STA-0184', 'STA-0185', 'STA-0186', 'STA-0188',
    # Minnesota Upton cards: "1818 or 1824-after 1901" life form
    'STA-0251', 'STA-0255', 'STA-0258', 'STA-0263', 'STA-0270',
    # Lake Champlain Stoddard cards: life range 1844-1917
    'STA-0407', 'STA-0410', 'STA-0412', 'STA-0414',
    # birth-year-only forms
    'STA-0423', 'STA-0462', 'STA-0479',
]
REDATE = {  # id -> (new year, evidence in the title's own statement)
    'STA-0187': ('1879', 'the title states the view date "(Apr. 23, (18)79)"'),
    'STA-0305': ('1875', 'the title states "Oceanic Regatta, July 24, 1875"'),
    'STA-0306': ('1875', 'the title states "Oceanic Regatta, July 24, 1875"'),
}
PLACE_FIX = {
    'STA-0208': ('Thousand Islands, Canada',
                 'the title states "Thousand Islands, Canada"'),
    'STA-0395': ('Galena, Illinois',
                 'the title states "Galena, Illinois"'),
}
PUBLISHER_SERIES = {
    'STA-0242': 'Sterographs of the Black Hills',  # as printed in the source text
}


def api(params):
    url = API + '?' + urllib.parse.urlencode({**params, 'format': 'json'})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def fetch_pins(catalog, manifest, force=False):
    cache_path = STAGE / 'api_cache.json'
    if cache_path.exists() and not force:
        return json.loads(cache_path.read_text())
    pins = {}
    by_pageid = {}
    for it in catalog:
        mm = (manifest.get(it['id']) or {}).get('master') or {}
        if mm.get('commons_page_id'):
            by_pageid[mm['commons_page_id']] = it['id']
    pids = sorted(by_pageid)
    print(f'fetch: {len(pids)} page ids in batches of 50')
    for i in range(0, len(pids), 50):
        batch = pids[i:i + 50]
        res = api({'action': 'query', 'prop': 'revisions|imageinfo',
                   'rvprop': 'ids', 'iiprop': 'sha1|extmetadata',
                   'iiextmetadatafilter':
                       'LicenseUrl|LicenseShortName|DateTimeOriginal',
                   'pageids': '|'.join(str(p) for p in batch)})
        for pid_s, pg in (res.get('query', {}).get('pages') or {}).items():
            sid = by_pageid.get(int(pid_s))
            if sid is None:
                continue
            ii = (pg.get('imageinfo') or [{}])[0]
            em = {k: (v.get('value') if isinstance(v, dict) else v)
                  for k, v in (ii.get('extmetadata') or {}).items()}
            pins[sid] = {
                'pageid': int(pid_s),
                'revid': (pg.get('revisions') or [{}])[0].get('revid'),
                'sha1': ii.get('sha1'),
                'license_url': em.get('LicenseUrl'),
                'license_short_name': (em.get('LicenseShortName') or '').strip(),
                'date_hint': str(em.get('DateTimeOriginal') or ''),
            }
        print(f'  batch {i // 50 + 1}: {len(pins)} pinned')
        time.sleep(0.3)
    # STA-0475: no page ID in the manifest; resolve by file title.
    for it in catalog:
        sid = it['id']
        if sid in pins:
            continue
        title = urllib.parse.unquote(
            it['source'].replace('https://commons.wikimedia.org/wiki/', ''))
        res = api({'action': 'query', 'prop': 'revisions|imageinfo',
                   'rvprop': 'ids', 'iiprop': 'sha1|extmetadata',
                   'iiextmetadatafilter':
                       'LicenseUrl|LicenseShortName|DateTimeOriginal',
                   'titles': title})
        for pid_s, pg in (res.get('query', {}).get('pages') or {}).items():
            ii = (pg.get('imageinfo') or [{}])[0]
            em = {k: (v.get('value') if isinstance(v, dict) else v)
                  for k, v in (ii.get('extmetadata') or {}).items()}
            pins[sid] = {
                'pageid': int(pid_s),
                'revid': (pg.get('revisions') or [{}])[0].get('revid'),
                'sha1': ii.get('sha1'),
                'license_url': em.get('LicenseUrl'),
                'license_short_name': (em.get('LicenseShortName') or '').strip(),
                'date_hint': str(em.get('DateTimeOriginal') or ''),
            }
        print(f'fetch: {sid} resolved by title -> page {pins.get(sid, {}).get("pageid")}')
    STAGE.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(pins, indent=1))
    return pins


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def recover_0475(catalog, manifest, pins):
    sid = 'STA-0475'
    entry = manifest.get(sid) or {}
    master = entry.get('master') or {}
    if master.get('status') == 'ok':
        print('recover: STA-0475 master already ok, skipping')
        return False
    it = next(x for x in catalog if x['id'] == sid)
    pin = pins[sid]
    fname = urllib.parse.unquote(it['source']).rsplit('/', 1)[-1]
    fname = fname.replace('File:', '', 1)
    dest_dir = PRES / 'masters' / sid
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / fname
    req = urllib.request.Request(it['full'], headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, 'wb') as fh:
        fh.write(r.read())
    sha1 = hashlib.sha1(dest.read_bytes()).hexdigest()
    if sha1 != pin['sha1']:
        dest.unlink()
        raise RuntimeError(f'STA-0475 download sha1 {sha1} != Commons {pin["sha1"]}')
    now = datetime.now(timezone.utc).isoformat()
    entry['master'] = {
        'file': f'masters/{sid}/{fname}',
        'sha256': sha256_of(dest), 'bytes': dest.stat().st_size,
        'mime': 'image/jpeg' if fname.lower().endswith(('.jpg', '.jpeg')) else '',
        'source_url': it['source'],
        'commons_page_id': pin['pageid'],
        'commons_revision_id': pin['revid'],
        'commons_sha1': pin['sha1'],
        'retrieved_at': now, 'status': 'ok'}
    manifest[sid] = entry
    (PRES / 'fixity-manifest.json').write_text(json.dumps(manifest, indent=1))
    lines = []
    for s in sorted(manifest):
        mrec = (manifest[s].get('master') or {})
        if mrec.get('status') == 'ok' and mrec.get('file'):
            lines.append(f"{mrec['sha256']}  {mrec['file']}")
    (PRES / 'manifest-sha256.txt').write_text('\n'.join(lines) + '\n')
    print(f'recover: STA-0475 master stored ({entry["master"]["bytes"]} bytes, '
          f'sha1 verified against Commons)')
    return True


def build_records(catalog, manifest, pins):
    changes = []
    stats = {'creator': 0, 'creator_dates': 0, 'edtf': 0, 'rights_uri': 0,
             'pin_page': 0, 'pin_rev': 0, 'pin_sha1': 0}
    records_dir = BASE / 'records'
    records_dir.mkdir(exist_ok=True)
    for it in catalog:
        sid = it['id']
        entry = json.loads(json.dumps(it))  # deep copy, key order kept
        # ---- authorized corrections, each self-checked ----
        if sid in UNDATED_IDS:
            forms = v2fields.life_forms(entry['title'])
            assert forms and v2fields.year_matches_life(entry['year'], forms), \
                f'{sid}: year {entry["year"]!r} not confirmed as life form'
            old = (entry['year'], entry['sy'], entry['era'])
            entry['year'], entry['sy'], entry['era'] = 'Undated', 1900, 'undated'
            changes.append({'id': sid, 'field': 'year/sy/era', 'from': old,
                            'to': ('Undated', 1900, 'undated'),
                            'evidence': f"title attribution life form {forms}; "
                                        f"title: {entry['title']}"})
        if sid in REDATE:
            new_year, ev = REDATE[sid]
            assert v2fields.explicit_view_year(entry['title']) == int(new_year), \
                f'{sid}: view year not found in title'
            old = (entry['year'], entry['sy'], entry['era'])
            entry['year'] = new_year
            entry['sy'] = int(new_year)
            entry['era'] = v2fields.era_of(entry['sy'], new_year)
            changes.append({'id': sid, 'field': 'year/sy/era', 'from': old,
                            'to': (entry['year'], entry['sy'], entry['era']),
                            'evidence': ev})
        if sid in PLACE_FIX:
            new_place, ev = PLACE_FIX[sid]
            assert new_place.split(',')[0] in entry['title'], \
                f'{sid}: place not stated in title'
            old = entry['place']
            entry['place'] = new_place
            changes.append({'id': sid, 'field': 'place', 'from': old,
                            'to': new_place, 'evidence': ev})
        # ---- pins: manifest first, API cache as the completing source ----
        mm = (manifest.get(sid) or {}).get('master') or {}
        pin = pins.get(sid, {})
        rec_pins = {
            'license_url': pin.get('license_url'),
            'source_page_id': mm.get('commons_page_id') or pin.get('pageid'),
            'source_revision_id': mm.get('commons_revision_id') or pin.get('revid'),
            'source_sha1': mm.get('commons_sha1') or pin.get('sha1'),
        }
        rec = v2fields.build_v2_record(
            entry, pins=rec_pins,
            publisher_series=PUBLISHER_SERIES.get(sid))
        (records_dir / f'{sid}.json').write_text(
            json.dumps(rec, indent=1, ensure_ascii=False) + '\n')
        stats['creator'] += rec['creator'] is not None
        stats['creator_dates'] += rec['creator_dates'] is not None
        stats['edtf'] += rec['date_edtf'] is not None
        stats['rights_uri'] += rec['rights_uri'] is not None
        stats['pin_page'] += rec['source_page_id'] is not None
        stats['pin_rev'] += rec['source_revision_id'] is not None
        stats['pin_sha1'] += bool(rec['source_sha1'])
    (STAGE / 'changes.json').write_text(json.dumps(
        {'changes': changes, 'stats': stats}, indent=1, ensure_ascii=False))
    return changes, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fetch', action='store_true', help='force a fresh API pass')
    ap.add_argument('--build', action='store_true', help='build only (use cache)')
    args = ap.parse_args()
    catalog = json.loads((BASE / 'data.json').read_text())
    manifest = json.loads((PRES / 'fixity-manifest.json').read_text())
    pins = fetch_pins(catalog, manifest, force=args.fetch or not args.build)
    # cross-checks
    sha_bad = lsn_bad = 0
    for it in catalog:
        sid = it['id']
        pin = pins.get(sid, {})
        mm = (manifest.get(sid) or {}).get('master') or {}
        if mm.get('commons_sha1') and pin.get('sha1') \
                and mm['commons_sha1'] != pin['sha1']:
            sha_bad += 1
            print(f'  WARN {sid}: manifest sha1 != API sha1')
        if pin.get('license_short_name') \
                and pin['license_short_name'] != it['license']:
            lsn_bad += 1
            print(f'  WARN {sid}: API LSN {pin["license_short_name"]!r} != '
                  f'catalog license {it["license"]!r}')
    print(f'cross-checks: sha1 mismatches {sha_bad}, license mismatches {lsn_bad}')
    recover_0475(catalog, manifest, pins)
    manifest = json.loads((PRES / 'fixity-manifest.json').read_text())
    changes, stats = build_records(catalog, manifest, pins)
    print(f'records built: {len(catalog)}; display changes: {len(changes)}')
    print('stats:', stats)
    dto = {sid: pins[sid].get('date_hint') for sid in
           [f'STA-{n:04d}' for n in range(175, 190)]}
    print('Leadville DateTimeOriginal hints:', dto)
    return 0


if __name__ == '__main__':
    sys.exit(main())
