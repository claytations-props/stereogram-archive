#!/usr/bin/env python3
"""Merge a staged batch into the Stereograph Archive catalog.

This is the ONLY tool that assigns STA accession numbers. They are
assigned exactly once, here, in manifest order (see docs/ARCHIVE_POLICY.md
and docs/INGEST_SOP.md).

Supports both Phase 0 manifests (entries carry batch-local CAND-## ids)
and legacy manifests (entries carry provisional STA-style ids from the
old engine — those are treated as candidates and remapped).

Flow: load manifest passed candidates -> assign next STA ids -> copy
pair files into rect/ as (accession-1).jpg and set each entry's rect
field -> append entries to data.json -> copy staged masters into the
preservation store and update its fixity manifest -> run
tools/validate_catalog.py -> on success create ONE atomic git commit
("Add N stereographs (<batch>) — STA-####–STA-####") -> with --push,
push and verify the live data.json matches local byte for byte.

On any validation failure, data.json, rect/, and the fixity manifest
are rolled back to their pre-merge state and the tool exits nonzero.

Usage:
  python tools/merge_batch.py --staging staging/<batch> [--push] [--dry-run]
"""
import argparse, hashlib, json, shutil, subprocess, sys, time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent
DEFAULT_PRESERVATION = Path.home() / 'workspace' / 'stereogram-archive-preservation'
LIVE_DATA = 'https://claytations-props.github.io/stereogram-archive/data.json'


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def dump_catalog(catalog):
    return json.dumps(catalog, indent=1, ensure_ascii=False)


def git(*args, check=True):
    r = subprocess.run(['git', '-C', str(BASE), *args],
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r


def main():
    ap = argparse.ArgumentParser(description='Merge a staged batch into the catalog')
    ap.add_argument('--staging', required=True, help='staging folder, e.g. staging/batch3')
    ap.add_argument('--push', action='store_true', help='push after commit and verify live')
    ap.add_argument('--dry-run', action='store_true',
                    help='print the merge plan and change nothing')
    ap.add_argument('--preservation', default=str(DEFAULT_PRESERVATION),
                    help='preservation store root')
    args = ap.parse_args()

    staging = Path(args.staging)
    if not staging.is_absolute():
        staging = BASE / staging
    pres = Path(args.preservation)
    manifest_path = staging / 'manifest.json'
    if not manifest_path.exists():
        print(f'ERROR: no manifest at {manifest_path}')
        return 1
    manifest = json.loads(manifest_path.read_text())
    passed = manifest.get('passed', [])
    if not passed:
        print('ERROR: manifest has no passed candidates; nothing to merge.')
        return 1

    catalog_path = BASE / 'data.json'
    catalog = json.loads(catalog_path.read_text())
    existing_ids = {it['id'] for it in catalog}
    existing_sources = {it['source'] for it in catalog}
    next_acc = max(int(it['id'].split('-')[1]) for it in catalog) + 1

    plan = []  # (new_entry, pair_source Path, staged_master dict or None)
    for i, p in enumerate(passed):
        acc = next_acc + i
        sta = f'STA-{acc:04d}'
        entry = json.loads(json.dumps(p['entry']))  # deep copy
        old_id = entry.get('id')
        if entry['source'] in existing_sources:
            print(f'ERROR: {old_id}: source already in catalog: {entry["source"]}')
            return 1
        entry['id'] = sta
        entry['rect'] = f'rect/{acc - 1:02d}.jpg'
        pair_src = staging / p['pair']
        if not pair_src.exists():
            print(f'ERROR: {old_id}: staged pair file missing: {pair_src}')
            return 1
        plan.append((entry, pair_src, p.get('master')))
        print(f'plan: {old_id} -> {sta}  ({entry["title"][:60]})')

    first_sta, last_sta = plan[0][0]['id'], plan[-1][0]['id']
    print(f'plan: {len(plan)} item(s), {first_sta}–{last_sta}')
    if args.dry_run:
        print('dry run: nothing changed.')
        return 0

    # ---- apply, with rollback state ----
    data_backup = catalog_path.read_bytes()
    fixity_path = pres / 'fixity-manifest.json'
    fixity_backup = fixity_path.read_bytes() if fixity_path.exists() else None
    bagit_path = pres / 'manifest-sha256.txt'
    bagit_backup = bagit_path.read_bytes() if bagit_path.exists() else None
    added_rects, added_masters = [], []
    try:
        for entry, pair_src, _ in plan:
            dest = BASE / entry['rect']
            shutil.copyfile(pair_src, dest)
            added_rects.append(dest)
        new_catalog = catalog + [e for e, _, _ in plan]
        catalog_path.write_text(dump_catalog(new_catalog))

        # preservation: copy staged masters, update fixity + BagIt manifest
        fixity = json.loads(fixity_backup) if fixity_backup else {}
        now = datetime.now(timezone.utc).isoformat()
        for entry, _, master in plan:
            sta = entry['id']
            rect_file = BASE / entry['rect']
            rec = {'rectified': {'file': entry['rect'],
                                 'sha256': sha256_of(rect_file),
                                 'bytes': rect_file.stat().st_size}}
            if master and master.get('status') == 'ok' and master.get('file'):
                src = staging / master['file']
                dest_dir = pres / 'masters' / sta
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest = dest_dir / src.name
                shutil.copyfile(src, dest)
                added_masters.append(dest)
                rec['master'] = {
                    'file': f'masters/{sta}/{src.name}',
                    'sha256': sha256_of(dest), 'bytes': dest.stat().st_size,
                    'mime': master.get('mime', ''),
                    'source_url': entry['source'],
                    'commons_page_id': master.get('commons_page_id'),
                    'commons_revision_id': master.get('commons_revision_id'),
                    'commons_sha1': master.get('commons_sha1', ''),
                    'retrieved_at': now, 'status': 'ok'}
            else:
                rec['master'] = {'file': None, 'sha256': None, 'bytes': None,
                                 'mime': '', 'source_url': entry['source'],
                                 'commons_page_id': None,
                                 'commons_revision_id': None, 'commons_sha1': '',
                                 'retrieved_at': now, 'status': 'pending',
                                 'reason': 'no staged master recorded at merge'}
            fixity[sta] = rec
        pres.mkdir(parents=True, exist_ok=True)
        fixity_path.write_text(json.dumps(fixity, indent=1))
        lines = []
        for sta in sorted(fixity):
            mrec = fixity[sta].get('master') or {}
            if mrec.get('status') == 'ok' and mrec.get('file'):
                lines.append(f"{mrec['sha256']}  {mrec['file']}")
        bagit_path.write_text('\n'.join(lines) + ('\n' if lines else ''))

        # ---- validate (catalog + fixity) ----
        cmd = [sys.executable, str(BASE / 'tools' / 'validate_catalog.py')]
        if fixity_path.exists():
            cmd += ['--fixity', '--preservation', str(pres)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(r.stdout)
        if r.returncode != 0:
            raise RuntimeError('validation failed; rolling back. ' + r.stderr.strip())
    except Exception as e:
        catalog_path.write_bytes(data_backup)
        for p in added_rects:
            p.unlink(missing_ok=True)
        for p in added_masters:
            p.unlink(missing_ok=True)
        if fixity_backup is not None:
            fixity_path.write_bytes(fixity_backup)
        elif fixity_path.exists():
            fixity_path.unlink()
        if bagit_backup is not None:
            bagit_path.write_bytes(bagit_backup)
        elif bagit_path.exists():
            bagit_path.unlink()
        print(f'ERROR: merge aborted, catalog and rect/ restored: {e}')
        return 1

    # ---- one atomic commit ----
    label = staging.name
    add_paths = ['data.json'] + [e['rect'] for e, _, _ in plan]
    git('add', '--', *add_paths)
    msg = f'Add {len(plan)} stereographs ({label}) — {first_sta}–{last_sta}'
    r = git('commit', '-m', msg, check=False)
    if r.returncode != 0:
        git('reset', '-q', check=False)
        catalog_path.write_bytes(data_backup)
        for p in added_rects:
            p.unlink(missing_ok=True)
        print(f'ERROR: commit failed, rolled back: {r.stderr.strip()}')
        return 1
    commit = git('rev-parse', 'HEAD').stdout.strip()
    print(f'committed {commit[:12]}: {msg}')

    if args.push:
        t0 = time.time()
        r = git('push', 'origin', 'main', check=False)
        if r.returncode != 0:
            print(f'ERROR: push failed (commit {commit[:12]} is intact locally): '
                  f'{r.stderr.strip()}')
            return 1
        print(f'pushed in {time.time() - t0:.2f}s')
        local_bytes = catalog_path.read_bytes()
        deadline = time.time() + 420
        while time.time() < deadline:
            try:
                req = urllib.request.Request(
                    f'{LIVE_DATA}?merge={int(time.time())}',
                    headers={'User-Agent': 'StereographArchiveMerge/1.0'})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if resp.read() == local_bytes:
                        print('live data.json verified byte-identical to local.')
                        return 0
            except Exception:
                pass
            time.sleep(15)
        print('ERROR: live data.json did not match local within 7 minutes.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
