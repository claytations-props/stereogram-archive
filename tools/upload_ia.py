#!/usr/bin/env python3
"""Upload the Stereograph Archive's images to the Internet Archive
(Phase 2 Part B — see docs/PARTB_IA_PLAN.md for the full plan and
the CORS/URL verification checklist that gates the site switchover).

Two public items are created/maintained:

  stereogram-archive-images   mediatype image
      rect/<n>.jpg                       the 1,026 rectified pairs
      thumbs/<STA>/w<width>.jpg          original-scan thumbnail ladder
      thumbs-rect/<STA>/w<width>.jpg     rectified-pair thumbnail ladder
      → ASSET_BASE becomes
        https://archive.org/download/stereogram-archive-images/

  stereogram-archive-masters  mediatype data
      masters/<STA>/<original filename>  the 1,026 preservation masters,
                                         paths exactly as in the local
                                         preservation store

Credentials come ONLY from the ia tool's own config file,
~/.config/internetarchive/ia.ini ([s3] access/secret), read by the
internetarchive package itself. Nothing secret is accepted on the
command line, and nothing secret is printed or logged.

Uploads are resumable and idempotent: every upload call passes
checksum=True, so a file whose remote MD5 already matches is
skipped by IAS3, and verify=True, so each uploaded file's MD5 is
checked against what IAS3 received. A separate --verify pass
compares the full remote file list (name, size, MD5) against local
hashes before the move is declared done.

Usage:
  ~/workspace/.venvs/cv/bin/python tools/upload_ia.py --dry-run --item images
  ~/workspace/.venvs/cv/bin/python tools/upload_ia.py --test
  ~/workspace/.venvs/cv/bin/python tools/upload_ia.py --item images
  ~/workspace/.venvs/cv/bin/python tools/upload_ia.py --item masters
  ~/workspace/.venvs/cv/bin/python tools/upload_ia.py --item images --verify

Progress is logged to stdout and to
~/workspace/stereogram-archive-assets/upload-ia.log.
"""
import argparse, hashlib, json, os, sys, time
from pathlib import Path

HOME = Path.home()
DEFAULT_PRES = HOME / 'workspace' / 'stereogram-archive-preservation'
DEFAULT_ASSETS = HOME / 'workspace' / 'stereogram-archive-assets'
DEFAULT_REPO = Path(__file__).parent.parent
DEFAULT_LOG = DEFAULT_ASSETS / 'upload-ia.log'

IMAGES_ITEM = 'stereogram-archive-images'
MASTERS_ITEM = 'stereogram-archive-masters'
TEST_ITEM = 'stereogram-archive-test'

# Item descriptions mirror the archive site's own About/footer text
# (index.html) — factual wording about the collection, no new claims.
ABOUT_TAIL = (
    ' All photographs are public domain or CC0, via Wikimedia Commons, '
    'from collections including the Robert N. Dennis Collection of '
    'Stereoscopic Views (NYPL), the Library of Congress, the Met Open '
    'Access, the National Archives, and the Getty Open Content program. '
    'Every pair carries a measured condition report from the archive '
    'rectification process.')

METADATA = {
    IMAGES_ITEM: {
        'title': 'The Stereograph Archive - Rectified Pairs and Thumbnails',
        'mediatype': 'image',
        'creator': 'Claytations Props',
        'description': (
            'Rectified stereoscopic pairs and thumbnail ladders from the '
            'Stereograph Archive, a public archive of stereoscopic '
            'photographs. The Stereograph Archive gathers public domain '
            'stereoscopic photographs, the 3D postcards of the nineteenth '
            'century, from the great open collections: the Robert N. '
            'Dennis Collection at NYPL, the Library of Congress, the Met, '
            'the Getty, and the National Archives. Every pair here is '
            'measured by the archive rectification process: the halves '
            'are registered to a fraction of a percent and the depth is '
            'budgeted for comfortable viewing.' + ABOUT_TAIL),
        'subject': 'stereographs; stereoscopic photography; vintage '
                   'photography; 3D photography',
    },
    MASTERS_ITEM: {
        'title': 'The Stereograph Archive - Preservation Masters',
        'mediatype': 'data',
        'creator': 'Claytations Props',
        'description': (
            'Preservation masters (original source scans) for the '
            'Stereograph Archive, a public archive of stereoscopic '
            'photographs. Each file is the original scan from which the '
            'archive rectified pair was produced, stored under its '
            'original filename in masters/<STA>/ directories matching '
            'the archive fixity manifest (SHA-256 recorded per file).' +
            ABOUT_TAIL),
        'subject': 'stereographs; stereoscopic photography; vintage '
                   'photography; digital preservation',
    },
    TEST_ITEM: {
        'title': 'Stereograph Archive - Part B Test (STA-0001)',
        'mediatype': 'image',
        'creator': 'Claytations Props',
        'description': (
            'Technical test item for the Stereograph Archive image move '
            '(Phase 2 Part B): one card (STA-0001) - its rectified pair, '
            'six thumbnails, and its preservation master - uploaded to '
            'verify URLs, checksums, and cross-origin headers before '
            'the full move.'),
        'subject': 'stereographs; test',
    },
}

BATCH = 50  # files per upload call


class Logger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.fh = open(self.path, 'a', buffering=1)

    def __call__(self, msg):
        line = f'{time.strftime("%Y-%m-%dT%H:%M:%S")} {msg}'
        print(line, flush=True)
        self.fh.write(line + '\n')


def md5_of(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_of(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_manifest(pres):
    return json.loads((pres / 'fixity-manifest.json').read_text())


def images_plan(repo, assets, manifest, only_sta=None):
    """{remote_name: local_path} for the images item."""
    plan = {}
    for sta in sorted(manifest):
        if only_sta and sta != only_sta:
            continue
        rect_rel = (manifest[sta].get('rectified') or {}).get('file')
        if rect_rel:
            plan[rect_rel.replace('\\', '/')] = repo / rect_rel
        for ladder in ('thumbs', 'thumbs-rect'):
            d = assets / ladder / sta
            if d.is_dir():
                for f in sorted(d.glob('*.jpg')):
                    plan[f'{ladder}/{sta}/{f.name}'] = f
    return plan


def masters_plan(pres, manifest, only_sta=None):
    """{remote_name: local_path} for the masters item. The remote
    name is the master path exactly as recorded in the fixity
    manifest (masters/<STA>/<original filename>)."""
    plan = {}
    for sta in sorted(manifest):
        if only_sta and sta != only_sta:
            continue
        master = manifest[sta].get('master') or {}
        if master.get('status') == 'ok' and master.get('file'):
            plan[master['file'].replace('\\', '/')] = pres / master['file']
    return plan


def test_plan(repo, assets, pres, manifest):
    plan = {}
    plan.update(images_plan(repo, assets, manifest, only_sta='STA-0001'))
    plan.update(masters_plan(pres, manifest, only_sta='STA-0001'))
    return plan


def require_config():
    """Fail early, with instructions, if the ia config has no keys.
    Values are never printed."""
    from internetarchive.config import get_config
    s3 = get_config().get('s3') or {}
    if not s3.get('access') or not s3.get('secret'):
        sys.exit('No S3 keys in ~/.config/internetarchive/ia.ini. '
                 'Run `ia configure` once (or create the file with an '
                 '[s3] access/secret section) and rerun.')
    return True


def upload_plan(session, identifier, plan, metadata, log):
    item = session.get_item(identifier)
    # This VM reaches the internet through an egress proxy that
    # re-signs TLS with its own CA (SSL_CERT_FILE / REQUESTS_CA_BUNDLE
    # point at its bundle). Plain requests honors those variables;
    # the ia S3 upload path verifies against certifi instead and
    # fails with CERTIFICATE_VERIFY_FAILED. Pass the environment's
    # bundle explicitly when one is set; on a normal machine nothing
    # is set and requests' defaults apply.
    ca_bundle = os.environ.get('REQUESTS_CA_BUNDLE') or \
        os.environ.get('SSL_CERT_FILE')
    request_kwargs = {'verify': ca_bundle} if ca_bundle else {}
    names = sorted(plan)
    total_bytes = sum(plan[n].stat().st_size for n in names)
    log(f'{identifier}: {len(names)} files, {total_bytes / 1e6:.1f} MB '
        f'to upload (existing files with matching MD5 are skipped)')
    failures = []
    for i in range(0, len(names), BATCH):
        batch = {n: str(plan[n]) for n in names[i:i + BATCH]}
        try:
            responses = item.upload(
                batch, metadata=metadata, checksum=True, verify=True,
                retries=5, retries_sleep=10, verbose=False,
                request_kwargs=request_kwargs)
            bad = [r for r in responses
                   if getattr(r, 'status_code', 200) >= 400]
            if bad:
                failures.append(
                    f'batch @{i}: HTTP {bad[0].status_code}')
                log(f'  batch @{i}: HTTP {bad[0].status_code} — '
                    f'will be retried on rerun (idempotent)')
            else:
                log(f'  files {i + 1}-{i + len(batch)} of '
                    f'{len(names)} uploaded/verified')
        except Exception as e:
            failures.append(f'batch @{i}: {e}')
            log(f'  batch @{i}: ERROR {e} — rerun resumes here')
    return failures


def verify_plan(session, identifier, plan, manifest, log):
    """Compare the remote file list with local size + MD5 for every
    planned file. Masters and rectified pairs are additionally
    checked against the fixity manifest's SHA-256 values at the
    local end (the local file must hash to the manifest value
    before its MD5 is trusted)."""
    # IA's metadata service indexes new files asynchronously — after
    # an upload the file list can lag S3 by minutes (observed on the
    # Part B test item). Poll until every planned file appears (or
    # the attempts run out) before judging anything missing.
    remote = {}
    for attempt in range(8):
        item = session.get_item(identifier)
        remote = {}
        for f in item.files:  # internetarchive 5.x: list of dicts
            remote[f['name']] = (int(f.get('size') or 0),
                                 (f.get('md5') or '').lower())
        if all(n in remote for n in plan):
            break
        if attempt < 7:
            log(f'{identifier}: metadata still indexing '
                f'({sum(1 for n in plan if n in remote)}/{len(plan)} '
                f'files listed) — waiting 45s')
            time.sleep(45)
    missing, wrong, checked = [], [], 0
    fixity = {}
    for sta, entry in manifest.items():
        for role in ('master', 'rectified'):
            e = entry.get(role) or {}
            if e.get('file') and e.get('sha256'):
                fixity[e['file'].replace('\\', '/')] = e['sha256']
    for name in sorted(plan):
        local = plan[name]
        size = local.stat().st_size
        digest = md5_of(local)
        if name in fixity and sha256_of(local) != fixity[name]:
            wrong.append(f'{name}: local file does not match the '
                         f'fixity manifest SHA-256')
            continue
        if name not in remote:
            missing.append(name)
        elif remote[name] != (size, digest):
            wrong.append(f'{name}: remote (size {remote[name][0]}, '
                         f'md5 {remote[name][1][:8]}…) != local '
                         f'(size {size}, md5 {digest[:8]}…)')
        else:
            checked += 1
    log(f'{identifier}: verified {checked} files OK; '
        f'{len(missing)} missing; {len(wrong)} mismatched')
    for n in missing[:20]:
        log(f'  MISSING {n}')
    for n in wrong[:20]:
        log(f'  WRONG {n}')
    return missing, wrong


def describe(identifier, plan):
    names = sorted(plan)
    total = sum(plan[n].stat().st_size for n in names)
    print(f'{identifier}: {len(names)} files, {total / 1e6:.1f} MB')
    for n in names[:5]:
        print(f'  {n}')
    if len(names) > 5:
        print(f'  … and {len(names) - 5} more')


def main():
    ap = argparse.ArgumentParser(description='Upload the Stereograph '
                                               'Archive images to the '
                                               'Internet Archive')
    ap.add_argument('--item', choices=['images', 'masters'],
                    help='which item to upload')
    ap.add_argument('--test', action='store_true',
                    help='upload STA-0001 only, to the scratch item '
                         'stereogram-archive-test')
    ap.add_argument('--verify', action='store_true',
                    help='after uploading (or alone, if --item/--test '
                         'is repeated) compare remote vs local')
    ap.add_argument('--verify-only', action='store_true',
                    help='only run the verification pass')
    ap.add_argument('--dry-run', action='store_true',
                    help='print the file plan; no network writes')
    ap.add_argument('--preservation', default=str(DEFAULT_PRES))
    ap.add_argument('--assets', default=str(DEFAULT_ASSETS))
    ap.add_argument('--repo', default=str(DEFAULT_REPO))
    ap.add_argument('--log', default=str(DEFAULT_LOG))
    args = ap.parse_args()

    if not args.item and not args.test:
        sys.exit('Choose --item images, --item masters, or --test.')

    pres, assets, repo = Path(args.preservation), Path(args.assets), \
        Path(args.repo)
    manifest = load_manifest(pres)

    if args.test:
        identifier, plan = TEST_ITEM, test_plan(repo, assets, pres,
                                                manifest)
    elif args.item == 'images':
        identifier, plan = IMAGES_ITEM, images_plan(repo, assets,
                                                    manifest)
    else:
        identifier, plan = MASTERS_ITEM, masters_plan(pres, manifest)

    missing_local = [n for n, p in plan.items() if not p.is_file()]
    if missing_local:
        sys.exit(f'{len(missing_local)} planned files are missing '
                 f'locally, e.g. {missing_local[0]} — run '
                 f'tools/build_thumbs.py / check the stores first.')

    if args.dry_run:
        describe(identifier, plan)
        return 0

    require_config()
    import internetarchive as ia
    session = ia.get_session()
    log = Logger(args.log)
    log(f'=== {identifier}: {"verify-only" if args.verify_only else "upload"} '
        f'run, {len(plan)} files planned ===')

    failures = []
    if not args.verify_only:
        failures = upload_plan(session, identifier, plan,
                               METADATA[identifier], log)
    if args.verify or args.verify_only or args.test:
        missing, wrong = verify_plan(session, identifier, plan,
                                     manifest, log)
        failures += [f'missing: {n}' for n in missing]
        failures += [f'wrong: {n}' for n in wrong]

    if failures:
        log(f'DONE WITH {len(failures)} PROBLEM(S) — rerun to resume')
        return 1
    log('DONE — all files uploaded and verified')
    return 0


if __name__ == '__main__':
    sys.exit(main())
