#!/usr/bin/env python3
"""Phase 3 interoperability outputs for the Stereograph Archive.

Standalone generator: reads records/ (the catalog of record) read-only and
writes ONLY these additive outputs:

  iiif/<STA>.json        IIIF Presentation API 3.0 manifest, one per item
  iiif/collection.json   IIIF Collection tying the manifests together
  ld/<STA>.json          schema.org JSON-LD, one per item
  exports/finding-aid.xml  EAD3 finding aid for the whole collection

It never touches tools/build_catalog.py, the validator, the pages, or any
existing generated output (data.json, browse.json, vr.json, search/,
catalog-v2.json); those belong to the catalog build. ASSET_BASE below
mirrors the constant of the same name in tools/build_catalog.py and must
be kept equal to it: manifests and JSON-LD point at the rectified-pair
image exactly where the site serves it from.

Catalog rule (Archive Policy section 4) applies in full: every
descriptive value is copied verbatim from the item's own record; a null
field is omitted, never filled in. Labels used for structure (IIIF
metadata labels, EAD element names, series shelf labels) are the
archive's own existing wording — the series labels are the ones
index.html displays (its CATS table).

Image dimensions: the rectified pair's pixel size is measured, never
derived from the source scan. Resolution order per item: the local
rect/<file> when present (newly merged waves), else a range fetch of
the first bytes of the served IA file and a parse of its JPEG SOF
marker. If neither works, the Canvas falls back to the pair's measured
aspect (2 x the record's `va`, the per-eye aspect measured on the
shipped pixels) at a nominal width, and the image body omits
width/height rather than stating numbers nobody measured.

Generation is deterministic: fixed field order, records in STA order,
and the run validates its own output (every record has a manifest and a
JSON-LD file, all JSON parses, the XML is well-formed, every manifest
image URL equals ASSET_BASE + the record's rect path, and a second
in-process generation is byte-identical to the first).

Usage: python3 tools/build_phase3.py [--repo PATH]
"""

import argparse
import hashlib
import json
import re
import struct
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

SITE_BASE = 'https://vrparlor.com/'
ASSET_BASE = 'https://archive.org/download/stereogram-archive-images/'
IIIF_CONTEXT = 'http://iiif.io/api/presentation/3/context.json'
ARCHIVE_NAME = 'The Stereograph Archive'

# Series shelves: facet key -> the label the site itself displays
# (index.html CATS table), in the site's display order.
SERIES = [
    ('water', 'Falls & Rivers'),
    ('mountains', 'Mountains & Canyons'),
    ('cities', 'Cities & Towns'),
    ('war', 'Civil War'),
    ('world', 'Around the World'),
    ('people', 'People & Comedy'),
    ('oddities', 'Oddities'),
]

PLAIN_EDTF = re.compile(r'^\d{4}(-\d{2}){0,2}$')


# ---------------------------------------------------------------- images

def jpeg_size(data):
    """(width, height) from JPEG bytes, or None."""
    if len(data) < 4 or data[:2] != b'\xff\xd8':
        return None
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack('>HH', data[i + 5:i + 9])
            return (w, h)
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD9:
            i += 2
            continue
        seglen = struct.unpack('>H', data[i + 2:i + 4])[0]
        i += 2 + seglen
    return None


def fetch_rect_size(url):
    """Measure a served rect by its JPEG header (range fetch)."""
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                url, headers={'Range': 'bytes=0-65535',
                              'User-Agent': 'stereogram-archive-phase3'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return jpeg_size(resp.read(65536))
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None


def measure_dims(records, repo):
    """Resolve rect pixel dims for every record; returns (dims, stats)."""
    dims = {}
    todo = []
    for rec in records:
        local = repo / rec['rect']
        size = None
        if local.is_file():
            size = jpeg_size(local.read_bytes()[:262144])
        if size:
            dims[rec['id']] = size + ('local',)
        else:
            todo.append(rec)
    fetched = failed = 0
    if todo:
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(
                lambda r: fetch_rect_size(ASSET_BASE + r['rect']), todo))
        for rec, size in zip(todo, results):
            if size:
                dims[rec['id']] = size + ('ia',)
                fetched += 1
            else:
                failed += 1
    return dims, {'local': len(records) - len(todo), 'ia': fetched,
                  'failed': failed}


def canvas_dims(rec, dims):
    """(width, height, measured?) for the manifest Canvas/image body."""
    if rec['id'] in dims:
        w, h, _src = dims[rec['id']]
        return w, h, True
    va = rec.get('va') or (rec.get('px') or {}).get('ar')
    if va:
        w = 2000
        return w, max(1, round(w / (2 * va))), False
    return 2000, 1000, False


# ------------------------------------------------------------------ IIIF

def meta_entry(label, value):
    return {'label': {'en': [label]}, 'value': {'none': [value]}}


def build_manifest(rec, dims):
    sta = rec['id']
    img_url = ASSET_BASE + rec['rect']
    w, h, measured = canvas_dims(rec, dims)
    canvas_id = f'{SITE_BASE}iiif/{sta}/canvas/1'
    manifest = {
        '@context': IIIF_CONTEXT,
        'id': f'{SITE_BASE}iiif/{sta}.json',
        'type': 'Manifest',
        'label': {'none': [rec['title']]},
    }
    metadata = []
    for label, key in (('Repository', 'repository'),
                       ('Collection', 'collection_name'),
                       ('Publisher', 'publisher'),
                       ('Creator', 'creator'),
                       ('Creator dates', 'creator_dates'),
                       ('Date', 'year'),
                       ('Place', 'place'),
                       ('License', 'license')):
        if rec.get(key):
            metadata.append(meta_entry(label, rec[key]))
    if metadata:
        manifest['metadata'] = metadata
    if rec.get('rights_uri'):
        manifest['rights'] = rec['rights_uri']
    manifest['seeAlso'] = [{
        'id': f'{SITE_BASE}records/{sta}.json',
        'type': 'Dataset',
        'format': 'application/json',
    }]
    thumb = (rec.get('px') or {}).get('s')
    body = {'id': img_url, 'type': 'Image', 'format': 'image/jpeg'}
    if measured:
        body['width'] = w
        body['height'] = h
    if thumb:
        body['thumbnail'] = [{'id': thumb, 'type': 'Image',
                              'format': 'image/jpeg'}]
    manifest['items'] = [{
        'id': canvas_id,
        'type': 'Canvas',
        'width': w,
        'height': h,
        'items': [{
            'id': f'{SITE_BASE}iiif/{sta}/annotationpage/1',
            'type': 'AnnotationPage',
            'items': [{
                'id': f'{SITE_BASE}iiif/{sta}/annotation/1',
                'type': 'Annotation',
                'motivation': 'painting',
                'body': body,
                'target': canvas_id,
            }],
        }],
    }]
    return manifest


def build_collection(records):
    return {
        '@context': IIIF_CONTEXT,
        'id': f'{SITE_BASE}iiif/collection.json',
        'type': 'Collection',
        'label': {'none': [ARCHIVE_NAME]},
        'items': [{
            'id': f"{SITE_BASE}iiif/{rec['id']}.json",
            'type': 'Manifest',
            'label': {'none': [rec['title']]},
        } for rec in records],
    }


# -------------------------------------------------------------- JSON-LD

def build_jsonld(rec):
    sta = rec['id']
    doc = {
        '@context': 'https://schema.org',
        '@type': 'Photograph',
        '@id': f'{SITE_BASE}ld/{sta}.json',
        'name': rec['title'],
        'contentUrl': ASSET_BASE + rec['rect'],
        'identifier': sta,
    }
    if rec.get('creator'):
        doc['creator'] = {'@type': 'Person', 'name': rec['creator']}
    edtf = rec.get('date_edtf')
    if edtf and PLAIN_EDTF.match(edtf):
        doc['dateCreated'] = edtf
    credit = rec.get('repository') or rec.get('collection_name')
    if credit:
        doc['creditText'] = credit
    if rec.get('rights_uri'):
        doc['license'] = rec['rights_uri']
    place = rec.get('place')
    if place and place != 'Place unrecorded':
        doc['contentLocation'] = {'@type': 'Place', 'name': place}
    if rec.get('source'):
        doc['sameAs'] = rec['source']
    return doc


# ------------------------------------------------------------------ EAD

def ead_item(rec):
    sta = rec['id']
    parts = [f'    <c level="item" id="{sta.lower()}">', '     <did>',
             f'      <unitid>{escape(sta)}</unitid>',
             f'      <unittitle>{escape(rec["title"])}</unittitle>']
    if rec.get('year'):
        normal = ''
        if rec.get('date_start') and rec.get('date_end'):
            if rec['date_start'] == rec['date_end']:
                normal = f' normal="{rec["date_start"]}"'
            else:
                normal = f' normal="{rec["date_start"]}/{rec["date_end"]}"'
        parts.append(
            f'      <unitdate{normal}>{escape(rec["year"])}</unitdate>')
    parts.append(
        f'      <dao daotype="derived" '
        f'href={quoteattr(ASSET_BASE + rec["rect"])}/>')
    parts.append('     </did>')
    parts.append('    </c>')
    return '\n'.join(parts)


def build_ead(records):
    by_series = {key: [] for key, _label in SERIES}
    for rec in records:
        facets = rec.get('facets') or []
        if facets:
            # An item hangs on one shelf in the finding aid: its first
            # facet, in the record's own order.
            by_series[facets[0]].append(rec)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<ead xmlns="urn:isbn:1-931666-22-9">',
        ' <control>',
        '  <recordid>vrparlor.com/finding-aid</recordid>',
        '  <filedesc>',
        '   <titlestmt>',
        f'    <titleproper>{ARCHIVE_NAME}</titleproper>',
        '   </titlestmt>',
        '  </filedesc>',
        '  <maintenanceagency>',
        f'   <agencyname>{ARCHIVE_NAME}</agencyname>',
        '  </maintenanceagency>',
        '  <languagedeclaration>',
        '   <language langcode="eng" scriptcode="Latn">English</language>',
        '  </languagedeclaration>',
        ' </control>',
        ' <archdesc level="collection">',
        '  <did>',
        f'   <unittitle>{ARCHIVE_NAME}</unittitle>',
        '   <unitid>vrparlor.com</unitid>',
        '   <physdescstructured coverage="whole" '
        'physdescstructuredtype="spaceoccupied">',
        f'    <quantity>{len(records)}</quantity>',
        '    <unittype>items</unittype>',
        '   </physdescstructured>',
        '  </did>',
        '  <dsc>',
    ]
    for key, label in SERIES:
        items = by_series[key]
        if not items:
            continue
        lines.append(f'   <c level="series" id="series-{key}">')
        lines.append('    <did>')
        lines.append(f'     <unittitle>{escape(label)}</unittitle>')
        lines.append('    </did>')
        for rec in items:
            lines.append(ead_item(rec))
        lines.append('   </c>')
    lines.append('  </dsc>')
    lines.append(' </archdesc>')
    lines.append('</ead>')
    return '\n'.join(lines) + '\n'


# -------------------------------------------------------------- generate

def dump_json(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False) + '\n'


def generate(records, dims):
    """Return {relative path: bytes} for every Phase 3 output."""
    out = {}
    for rec in records:
        out[f"iiif/{rec['id']}.json"] = dump_json(
            build_manifest(rec, dims)).encode('utf-8')
        out[f"ld/{rec['id']}.json"] = dump_json(
            build_jsonld(rec)).encode('utf-8')
    out['iiif/collection.json'] = dump_json(
        build_collection(records)).encode('utf-8')
    out['exports/finding-aid.xml'] = build_ead(records).encode('utf-8')
    return out


def validate(records, out):
    """Self-validation; returns a list of problems (empty = clean)."""
    problems = []
    by_id = {r['id']: r for r in records}
    for sta, rec in by_id.items():
        for path in (f'iiif/{sta}.json', f'ld/{sta}.json'):
            if path not in out:
                problems.append(f'missing {path}')
                continue
            try:
                doc = json.loads(out[path])
            except Exception as exc:
                problems.append(f'{path}: JSON parse failed: {exc}')
                continue
            if path.startswith('iiif/'):
                body = doc['items'][0]['items'][0]['items'][0]['body']
                if body['id'] != ASSET_BASE + rec['rect']:
                    problems.append(f'{path}: image URL mismatch')
                if doc['label']['none'][0] != rec['title']:
                    problems.append(f'{path}: label is not the record title')
            else:
                if doc['contentUrl'] != ASSET_BASE + rec['rect']:
                    problems.append(f'{path}: contentUrl mismatch')
                if doc['name'] != rec['title']:
                    problems.append(f'{path}: name is not the record title')
    try:
        coll = json.loads(out['iiif/collection.json'])
        if len(coll['items']) != len(records):
            problems.append('collection.json: item count != record count')
    except Exception as exc:
        problems.append(f'collection.json: {exc}')
    try:
        root = ET.fromstring(out['exports/finding-aid.xml'])
        ns = '{urn:isbn:1-931666-22-9}'
        items = root.findall(f'.//{ns}c[@level="item"]')
        if len(items) != len(records):
            problems.append(
                f'finding-aid.xml: {len(items)} item components '
                f'!= {len(records)} records')
        daos = root.findall(f'.//{ns}dao')
        for dao in daos:
            href = dao.get('href', '')
            if not href.startswith(ASSET_BASE):
                problems.append(f'finding-aid.xml: dao off base: {href}')
                break
    except Exception as exc:
        problems.append(f'finding-aid.xml: XML parse failed: {exc}')
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args()
    repo = Path(args.repo)

    record_files = sorted((repo / 'records').glob('STA-*.json'))
    records = [json.loads(p.read_text(encoding='utf-8'))
               for p in record_files]
    print(f'records: {len(records)}')

    dims, stats = measure_dims(records, repo)
    print(f"dims: {stats['local']} local, {stats['ia']} via IA headers, "
          f"{stats['failed']} unmeasured (aspect fallback)")

    out = generate(records, dims)
    again = generate(records, dims)
    digest = lambda m: {k: hashlib.sha256(v).hexdigest()
                        for k, v in m.items()}
    if digest(out) != digest(again):
        print('FAIL: generation is not deterministic', file=sys.stderr)
        return 1

    problems = validate(records, out)
    if problems:
        for p in problems[:20]:
            print(f'FAIL: {p}', file=sys.stderr)
        return 1
    print(f'validation: clean ({len(out)} files)')

    for rel, data in sorted(out.items()):
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    n_iiif = sum(1 for k in out if k.startswith('iiif/'))
    n_ld = sum(1 for k in out if k.startswith('ld/'))
    print(f'wrote: {n_iiif} IIIF files (incl. collection), {n_ld} JSON-LD, '
          f'1 EAD = {len(out)} total')
    return 0


if __name__ == '__main__':
    sys.exit(main())
