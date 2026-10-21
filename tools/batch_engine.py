#!/usr/bin/env python3
"""Batch import engine for the Stereograph Archive — STAGING ONLY.

Harvests candidate stereographs from Wikimedia Commons, filters to
public-domain / CC0 works, dedupes against the live catalog (data.json,
read-only), rectifies each scan with tools/stereo_pipeline.py, applies the
pipeline's own quality gates, and writes draft catalog entries plus baked
pairs into a staging folder with a manifest.json.

It NEVER writes to data.json, index.html, vr.html, condition.json, or the
repo's rect/ folder. Publishing a staged batch is a separate, human step.

Usage:
  python batch_engine.py --query "<commons search query>" --count N --staging staging/<name>
  python batch_engine.py --files "File:..." "File:..." --staging staging/<name>

Draft entries mirror data.json's field set exactly (including px live-warp
params composed from rectify's capture dict). Anything a human should check
before publishing (place, year, depth word, collection) is a heuristic and
the entry is flagged "needs_review" in the manifest. Title and blurb are
NOT written here: per Clay's source-fidelity rule (2026-10-21) they come
straight from the Commons file record — see clean_title / source_blurb.

Environment: run with the OpenCV venv python and TMPDIR pointed at a roomy
disk (the /tmp tmpfs is tiny):
  TMPDIR=~/workspace/.tmp ~/workspace/.venvs/cv/bin/python tools/batch_engine.py ...
"""
import argparse, html, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import cv2
import numpy as np
from stereo_pipeline import (auto_rects, rectify, GATE_VERT, GATE_ROT,
                             GATE_CELL, GATE_POST_RANGE, MIN_AREA_FRAC)

BASE = Path(__file__).parent.parent
API = 'https://commons.wikimedia.org/w/api.php'
UA = {'User-Agent': 'StereographArchiveBatch/1.0 (staging import tool; claytations@gmail.com)'}

# LicenseShortName values accepted as public domain / CC0 (matches the
# license strings already used in data.json).
PD_LICENSES = {'Public domain', 'CC0', 'No restrictions', 'Public Domain Mark'}

COLL_RULES = [  # (needle in category or description, catalog name)
    ('robert n. dennis collection', 'Robert N. Dennis Collection'),
    ('keystone view company', 'Keystone View Company'),
    ('library of congress', 'Library of Congress'),
    ('metropolitan museum', 'The Metropolitan Museum of Art'),
    ('national archives', 'National Archives'),
    ('international stereoscopic', 'International Stereoscopic View Co.'),
    ('getty', 'Getty Open Content'),
]

GAZETTEER = [  # title keyword -> place string (draft heuristic)
    ('niagara', 'Niagara Falls, New York'),
    ('gettysburg', 'Gettysburg, Pennsylvania'),
    ('mount vernon', 'Mount Vernon, Virginia'),
    ('ticonderoga', 'Fort Ticonderoga, New York'),
    ('yosemite', 'Yosemite, California'),
    ('yellowstone', 'Yellowstone, Wyoming'),
    ('natural bridge', 'Natural Bridge, Virginia'),
    ('mammoth cave', 'Mammoth Cave, Kentucky'),
    ('fort pulaski', 'Savannah, Georgia'),
    ('fort monroe', 'Fort Monroe, Virginia'),
    ('richmond', 'Richmond, Virginia'),
    ('antietam', 'Antietam, Maryland'),
    ('harpers ferry', 'Harpers Ferry, West Virginia'),
    ('washington, d', 'Washington, D.C.'),
    ('new york', 'New York, New York'),
    ('san francisco', 'San Francisco, California'),
    ('sacramento', 'Sacramento, California'),
    ('boston', 'Boston, Massachusetts'),
    ('philadelphia', 'Philadelphia, Pennsylvania'),
    ('chicago', 'Chicago, Illinois'),
]

FOREIGN = ['paris', 'london', 'france', 'england', 'scotland', 'ireland', 'italy',
           'rome', 'venice', 'germany', 'berlin', 'switzerland', 'alps', 'egypt',
           'pyramid', 'nile', 'india', 'china', 'japan', 'jerusalem', 'palestine',
           'greece', 'athens', 'norway', 'sweden', 'holland', 'belgium', 'spain',
           'mexico', 'canada', 'montreal', 'quebec', 'toronto', 'havana', 'cuba']

PUBLISHERS = ['Keystone View Company', 'Underwood & Underwood', 'Underwood and Underwood',
              'Strohmeyer & Wyman', 'American Stereoscopic Company', 'E. & H. T. Anthony',
              'Kilburn Brothers', 'B. W. Kilburn']


# ---------------------------------------------------------------- Commons API
def api(params):
    url = API + '?' + urllib.parse.urlencode({**params, 'format': 'json'})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def page_to_candidate(pg):
    ii = (pg.get('imageinfo') or [{}])[0]
    em = {k: (v.get('value') if isinstance(v, dict) else v)
          for k, v in (ii.get('extmetadata') or {}).items()}
    return {
        'file_title': pg.get('title', ''),
        'source': ii.get('descriptionurl', ''),
        'img': ii.get('thumburl') or ii.get('url', ''),
        'full': ii.get('url', ''),
        'w': ii.get('width'), 'h': ii.get('height'),
        'license': (em.get('LicenseShortName') or '').strip(),
        'categories': [c['title'].replace('Category:', '')
                       for c in pg.get('categories', [])],
        'description': clean_description(em.get('ImageDescription')),
        'date_hint': str(em.get('DateTimeOriginal') or ''),
    }


PROPS = {'prop': 'imageinfo|categories', 'iiprop': 'url|size|extmetadata',
         'iiurlwidth': 1920, 'cllimit': 'max', 'clshow': '!hidden'}


def harvest_query(query, count):
    data = api({'action': 'query', 'generator': 'search', 'gsrsearch': query,
                'gsrnamespace': 6, 'gsrlimit': str(min(50, count * 3 + 5)), **PROPS})
    pages = (data.get('query') or {}).get('pages') or {}
    return [page_to_candidate(pg)
            for pg in sorted(pages.values(), key=lambda p: p.get('index', 999))]


def harvest_files(titles):
    data = api({'action': 'query', 'titles': '|'.join(titles), **PROPS})
    pages = (data.get('query') or {}).get('pages') or {}
    return [page_to_candidate(pg) for pg in pages.values() if 'imageinfo' in pg]


# ------------------------------------------------------------------ px params
def px_from_capture(cap, scan_url):
    """Compose a data.json-style px entry from rectify's capture dict.

    The pipeline's baked pair is: left eye = plain sub-crop of the left
    photo; right eye = right photo resized to the left photo's frame,
    warped by the windowed affine A2, then the same sub-crop. Each eye is
    therefore one affine view of the scan; here those affines are expressed
    in UV form exactly like tools/harvest_params.py's px entries:
    scan_uv = (a*u + b*v + c, d*u + e*v + f) over the output eye.
    (Validated: re-rendering from these params measures inside the gates.)
    """
    W, H = cap['scan_wh']
    lw, lh = cap['crop_wh']
    r = cap['rects']
    lx, ly = int(r[0] * W), int(r[1] * H)
    rx, ry = int(r[4] * W), int(r[5] * H)
    rw, rh = int(r[6] * W), int(r[7] * H)
    x0, y0, x1, y1 = cap['crop_rect']
    ow, oh = x1 - x0, y1 - y0
    L = [ow / W, 0.0, (lx + x0 - 0.5) / W, 0.0, oh / H, (ly + y0 - 0.5) / H]
    B = cv2.invertAffineTransform(np.array(cap['A2'], dtype=float))
    sx, sy = rw / lw, rh / lh
    R = [sx * B[0, 0] * ow / W, sx * B[0, 1] * oh / W,
         (rx + sx * (B[0, 0] * (x0 - 0.5) + B[0, 1] * (y0 - 0.5) + B[0, 2])) / W,
         sy * B[1, 0] * ow / H, sy * B[1, 1] * oh / H,
         (ry + sy * (B[1, 0] * (x0 - 0.5) + B[1, 1] * (y0 - 0.5) + B[1, 2])) / H]
    return {'s': scan_url, 'ar': round(ow / oh, 4),
            'L': [round(float(v), 6) for v in L],
            'R': [round(float(v), 6) for v in R],
            'g': [float(g) for g in cap['gains']]}


# ------------------------------------------------------------------ heuristics
COLL_SUFFIX_RE = re.compile(
    r',?\s*from [^,]*[Cc]ollection of stereoscopic views\.?$')


def clean_title(file_title):
    """Source-fidelity title (Clay's rule, 2026-10-21): the Commons file
    page name with no 'File:' prefix and no extension, and ONLY the
    trailing collection suffix removed. No shortening, no rewording, no
    added suffixes — the title is the archive's own, verbatim."""
    t = file_title
    if t.startswith('File:'):
        t = t[len('File:'):]
    t = re.sub(r'\.[A-Za-z0-9]{3,4}$', '', t)
    t = t.replace('_', ' ')
    t = COLL_SUFFIX_RE.sub('', t)
    return t.strip()


def clean_description(raw):
    """Mechanically clean a Commons ImageDescription: strip HTML tags,
    decode entities, collapse whitespace. Nothing reworded or added."""
    if not raw:
        return ''
    s = str(raw)
    s = re.sub(r'(?i)<\s*br\s*/?\s*>', ' ', s)
    s = re.sub(r'(?i)</\s*(p|div|li|tr|ul|ol)\s*>', ' ', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def source_blurb(description, title):
    """Source-fidelity blurb: the source record's own cleaned description,
    or '' when there is none or it merely restates the title (normalized
    comparison: equal, or one contains the other)."""
    desc = clean_description(description)
    if not desc:
        return ''
    dn, tn = norm(desc), norm(title)
    if dn and tn and (dn == tn or tn in dn or dn in tn):
        return ''
    return desc


def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()


def guess_place(title):
    low = title.lower()
    for key, place in GAZETTEER:
        if key in low:
            return place
    return 'Place unrecorded'


def guess_coll(cand):
    # The file title itself names the source for most cards ("..., from
    # Robert N. Dennis collection of stereoscopic views"); the collection
    # category is often hidden on Commons, so categories alone miss it.
    hay = (cand['file_title'] + ' ' + ' '.join(cand['categories'])
           + ' ' + cand['description']).lower()
    for needle, name in COLL_RULES:
        if needle in hay:
            return name
    return 'Source unrecorded'


def guess_year(cand, title):
    # The card's own title is the most authoritative date source (descriptions
    # often mention earlier event years, e.g. an 1892 Gettysburg reunion card
    # whose description talks about the 1863 battle).
    hay = title + ' ' + cand['date_hint'] + ' ' + cand['description']
    m = re.search(r'(1[78]\d\d)\s*[–—-]\s*((?:1[78]|19)\d\d)', hay)
    if m:
        return f'{m.group(1)}–{m.group(2)}', int(m.group(1))
    m = re.search(r'(1[78]\d\d)s\b', hay)
    if m:
        return f'{m.group(1)}s', int(m.group(1)) + 5
    m = re.search(r'\b(1[78]\d\d|19[0-2]\d)\b', hay)
    if m:
        y = int(m.group(1))
        circa = 'circa' if re.search(r'\b(c\.|ca\.|circa)\s*$', hay[:m.start()], flags=re.I) else ''
        return (f'c. {y}' if circa else str(y)), y
    return 'Undated', 1900


def era_of(year, sy):
    if year == 'Undated':
        return 'undated'
    return 'early' if sy < 1870 else ('mid' if sy < 1900 else 'late')


def guess_cats(title, place):
    low = (title + ' ' + place).lower()
    cats = []
    if re.search(r'falls?|river|waterfall|rapids|creek|stream|lake|gorge.*water', low):
        cats.append('water')
    if re.search(r'mountain|canyon|gorge|cliff|peak|summit|valley|rock', low):
        cats.append('mountains')
    if re.search(r'street|broadway|avenue|city|building|hotel|church|bridge|depot|station', low):
        cats.append('cities')
    if re.search(r'gettysburg|civil war|soldier|\bfort\b|battle|regiment|camp\b|army', low):
        cats.append('war')
    if any(k in low for k in FOREIGN):
        cats.append('world')
    if re.search(r'people|portrait|comedy|man\b|woman|men\b|children|group', low):
        cats.append('people')
    return cats[:3] or ['oddities']


def depth_word(range_pct):
    return 'Gentle' if range_pct < 1.5 else ('Moderate' if range_pct < 2.2 else 'Deep')


def cond_sentence(vert, rot, rng, depth, f):
    size = 'full size' if f >= 1.0 else f'{round(f * 100)}% size'
    return (f'Rectified 2026. Halves registered to {round(vert, 2)}% vertical error and '
            f'{round(rot, 2)}° of rotation. Depth measured {depth.lower()} '
            f'({round(rng, 2)}% of frame width); hung in the VR Parlor at {size}.')


def gate_failures(m):
    if 'fail' in m:
        return [m['fail']]
    fails = []
    if m.get('out_rot', 9) > GATE_ROT:
        fails.append(f"rotation {m['out_rot']}° exceeds {GATE_ROT}°")
    if m.get('out_vert', 9) > GATE_VERT:
        fails.append(f"vertical error {m['out_vert']}% exceeds {GATE_VERT}%")
    if m.get('out_cellbad', 9) > GATE_CELL:
        fails.append(f"worst 3x3 cell {m['out_cellbad']}% exceeds {GATE_CELL}%")
    post = m.get('range_deg', 99) * m.get('size_f', 0)
    if post > GATE_POST_RANGE:
        fails.append(f"post-size depth {round(post, 2)}° exceeds {GATE_POST_RANGE}°")
    if m.get('area_frac', 0) < MIN_AREA_FRAC:
        fails.append(f"common area {round(m['area_frac'] * 100)}% below {int(MIN_AREA_FRAC * 100)}%")
    return fails


# --------------------------------------------------------------------- engine
def load_catalog():
    return json.loads((BASE / 'data.json').read_text())


def download(cand, dl_dir):
    name = re.sub(r'[^A-Za-z0-9._-]+', '_',
                  urllib.parse.unquote(Path(urllib.parse.urlparse(cand['img']).path).name))
    path = dl_dir / name
    if not path.exists():
        req = urllib.request.Request(cand['img'], headers=UA)
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    return path


def run(candidates, staging, count=None):
    staging.mkdir(parents=True, exist_ok=True)
    dl_dir = staging / 'downloads'
    dl_dir.mkdir(exist_ok=True)
    manifest_path = staging / 'manifest.json'
    prev = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest = {'passed': list(prev.get('passed', [])),
                'held': [], 'skipped_duplicates': list(prev.get('skipped_duplicates', [])),
                'skipped_license': [], 'errors': []}

    catalog = load_catalog()
    cat_sources = {it['source'] for it in catalog}
    cat_files = {urllib.parse.unquote(it['source'].rsplit('/', 1)[-1]) for it in catalog}
    cat_titles = {norm(it['title']) for it in catalog}
    staged_sources = {p['entry']['source'] for p in manifest['passed']}
    next_acc = max([int(it['id'].split('-')[1]) for it in catalog] +
                   [int(p['entry']['id'].split('-')[1]) for p in manifest['passed']]) + 1

    processed_new = 0
    for cand in candidates:
        if count is not None and processed_new >= count:
            break
        title = clean_title(cand['file_title'])
        tag = cand['file_title']
        try:
            if cand['license'] not in PD_LICENSES:
                manifest['skipped_license'].append(
                    {'title': tag, 'source': cand['source'],
                     'reason': f"license '{cand['license'] or 'unknown'}' is not PD/CC0"})
                print(f'SKIP-LICENSE {tag} ({cand["license"]})', flush=True)
                continue
            file_base = urllib.parse.unquote(cand['file_title'].replace('File:', ''))
            if (cand['source'] in cat_sources or cand['source'] in staged_sources
                    or file_base in cat_files or norm(title) in cat_titles):
                manifest['skipped_duplicates'].append(
                    {'title': tag, 'source': cand['source'],
                     'reason': 'already in the catalog or this staging batch'})
                print(f'SKIP-DUP     {tag}', flush=True)
                continue
            processed_new += 1
            scan_path = download(cand, dl_dir)
            img = cv2.imread(str(scan_path))
            if img is None:
                manifest['errors'].append({'title': tag, 'source': cand['source'],
                                           'reason': 'downloaded scan could not be decoded'})
                print(f'ERROR        {tag}: undecodable scan', flush=True)
                continue
            rects = auto_rects(img)
            if rects is None:
                manifest['held'].append({'title': tag, 'source': cand['source'],
                                         'reason': 'auto_rects could not locate both printed photo boxes',
                                         'metrics': {}})
                print(f'HELD         {tag}: photo boxes not found', flush=True)
                continue
            cap = {}
            pair, m = rectify(img, rects, capture=cap)
            if pair is None or not m.get('pass'):
                fails = gate_failures(m) if m else ['rectify failed']
                manifest['held'].append({'title': tag, 'source': cand['source'],
                                         'reason': '; '.join(fails),
                                         'metrics': {k: m.get(k) for k in
                                                     ('out_vert', 'out_rot', 'out_cellbad',
                                                      'range_deg', 'size_f', 'area_frac',
                                                      'disp_range_pct', 'fit_vert_p90_pct')}})
                print(f'HELD         {tag}: {"; ".join(fails)}', flush=True)
                continue
            acc = next_acc
            next_acc += 1
            pair_name = f'{acc - 1:02d}.jpg'
            cv2.imwrite(str(staging / pair_name), pair,
                        [cv2.IMWRITE_JPEG_QUALITY, 92])
            px = px_from_capture(cap, cand['img'])
            vert, rot = m['out_vert'], m['out_rot']
            rng, f = m['disp_range_pct'], m['size_f']
            depth = depth_word(rng)
            year, sy = guess_year(cand, title)
            place = guess_place(title)
            entry = {
                'title': title, 'place': place, 'year': year, 'sy': sy,
                'era': era_of(year, sy), 'cats': guess_cats(title, place),
                'blurb': source_blurb(cand['description'], title),
                'img': cand['img'], 'full': cand['full'], 'source': cand['source'],
                'license': cand['license'], 'w': cand['w'], 'h': cand['h'],
                'id': f'STA-{acc:04d}', 'coll': guess_coll(cand),
                'vert': vert, 'rot': rot, 'range': rng, 'f': f, 'depth': depth,
                'cond': cond_sentence(vert, rot, rng, depth, f),
                'va': px['ar'], 'px': px,
            }
            manifest['passed'].append({'entry': entry, 'pair': pair_name,
                                       'source_file': cand['file_title'],
                                       'flags': ['needs_review']})
            print(f'PASS         {tag} -> {entry["id"]} '
                  f'(vert {vert}%, rot {rot}°, area {m["area_frac"]})', flush=True)
        except Exception as e:  # one bad candidate must never kill the batch
            manifest['errors'].append({'title': tag, 'source': cand.get('source', ''),
                                       'reason': f'{type(e).__name__}: {e}'})
            print(f'ERROR        {tag}: {e}', flush=True)

    manifest_path.write_text(json.dumps(manifest, indent=1))
    print(f"\n== {staging} ==")
    print(f"passed: {len(manifest['passed'])}  held: {len(manifest['held'])}  "
          f"duplicates skipped: {len(manifest['skipped_duplicates'])}  "
          f"license skipped: {len(manifest['skipped_license'])}  errors: {len(manifest['errors'])}")
    print(f'manifest: {manifest_path}')
    return manifest


def main():
    ap = argparse.ArgumentParser(description='Stereograph Archive batch import (staging only)')
    ap.add_argument('--query', help='Commons search query (File namespace)')
    ap.add_argument('--count', type=int, default=10,
                    help='max NEW candidates to rectify in --query mode (default 10)')
    ap.add_argument('--files', nargs='+', help='explicit Commons file titles ("File:...")')
    ap.add_argument('--staging', required=True, help='staging folder, e.g. staging/batch2')
    args = ap.parse_args()
    staging = Path(args.staging)
    if not staging.is_absolute():
        staging = BASE / staging
    if args.files:
        titles = [t if t.startswith('File:') else 'File:' + t for t in args.files]
        run(harvest_files(titles), staging)
    elif args.query:
        run(harvest_query(args.query, args.count), staging, count=args.count)
    else:
        ap.error('give --query or --files')


if __name__ == '__main__':
    main()
