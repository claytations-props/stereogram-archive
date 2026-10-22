#!/usr/bin/env python3
"""Build the local thumbnail ladders for the Stereograph Archive
(Phase 2A, workstream A5 — generation only; nothing is wired to
these files until Part B gives them a public URL).

For every item, two ladders of JPEG derivatives are generated at
widths 250 / 500 / 1000 (height proportional, quality ~82, sRGB):

  thumbs/<STA>/w<width>.jpg       from the ORIGINAL scan — the
                                  preservation master named in the
                                  fixity manifest (what the gallery
                                  cards display)
  thumbs-rect/<STA>/w<width>.jpg  from the rectified pair in rect/
                                  (the VR Parlor's image)

Output goes to the sibling assets directory
~/workspace/stereogram-archive-assets/ — deliberately OUTSIDE the
git repo. When Part B picks a host, that directory's layout is
uploaded as-is and build_catalog.py's ASSET_BASE patterns
({base}thumbs/<STA>/w<width>.jpg, {base}thumbs-rect/<STA>/w<width>.jpg)
point at it.

A derivative is never upscaled: when the source is narrower than a
rung, the rung is written at the source's native width (and logged).
Masters that fail to decode are skipped and logged, never fatal.
Existing non-empty outputs are left alone, so reruns resume.

Usage: ~/workspace/.venvs/cv/bin/python tools/build_thumbs.py
           [--preservation ~/workspace/stereogram-archive-preservation]
           [--assets ~/workspace/stereogram-archive-assets]
           [--repo ~/workspace/stereogram-archive]
Writes a machine-readable run log to <assets>/thumbs-log.json.
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_catalog  # for THUMB_WIDTHS

DEFAULT_PRES = Path.home() / 'workspace' / 'stereogram-archive-preservation'
DEFAULT_ASSETS = Path.home() / 'workspace' / 'stereogram-archive-assets'
DEFAULT_REPO = Path(__file__).parent.parent


def ladder(src_path, out_dir, widths, log, tag):
    """Write one ladder for src_path into out_dir. Returns the number
    of files written (existing non-empty files count as present)."""
    from PIL import Image, ImageOps
    out_dir.mkdir(parents=True, exist_ok=True)
    targets = [out_dir / f'w{w}.jpg' for w in widths]
    if all(t.exists() and t.stat().st_size > 0 for t in targets):
        return len(targets)
    with Image.open(src_path) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode != 'RGB':
            im = im.convert('RGB')
        native_w = im.width
        written = 0
        for w, dest in zip(widths, targets):
            if dest.exists() and dest.stat().st_size > 0:
                written += 1
                continue
            tw = min(w, native_w)
            if tw < w:
                log.append(f'{tag}: source is {native_w}px wide; '
                           f'w{w} written at native width')
            th = max(1, round(im.height * tw / im.width))
            im.resize((tw, th), Image.LANCZOS).save(
                dest, 'JPEG', quality=82, optimize=True)
            written += 1
        return written


def main():
    ap = argparse.ArgumentParser(description='Generate the thumbnail '
                                               'ladders (originals + '
                                               'rectified pairs)')
    ap.add_argument('--preservation', default=str(DEFAULT_PRES))
    ap.add_argument('--assets', default=str(DEFAULT_ASSETS))
    ap.add_argument('--repo', default=str(DEFAULT_REPO))
    args = ap.parse_args()

    pres, assets, repo = Path(args.preservation), Path(args.assets), Path(args.repo)
    manifest = json.loads((pres / 'fixity-manifest.json').read_text())
    widths = build_catalog.THUMB_WIDTHS

    log, failures = [], []
    stats = {'thumbs': [0, 0], 'thumbs-rect': [0, 0]}  # files, bytes
    ids = sorted(manifest)
    for n, sta in enumerate(ids, 1):
        entry = manifest[sta]
        master = entry.get('master') or {}
        if master.get('status') == 'ok' and master.get('file'):
            try:
                c = ladder(pres / master['file'], assets / 'thumbs' / sta,
                           widths, log, f'{sta} thumbs')
                stats['thumbs'][0] += c
            except Exception as e:
                failures.append(f'{sta}: original master failed: {e}')
        else:
            failures.append(f'{sta}: no ok master in fixity manifest')
        rect_file = (entry.get('rectified') or {}).get('file')
        if rect_file:
            try:
                c = ladder(repo / rect_file, assets / 'thumbs-rect' / sta,
                           widths, log, f'{sta} thumbs-rect')
                stats['thumbs-rect'][0] += c
            except Exception as e:
                failures.append(f'{sta}: rectified pair failed: {e}')
        else:
            failures.append(f'{sta}: no rectified file in fixity manifest')
        if n % 100 == 0:
            print(f'  {n}/{len(ids)} items…', flush=True)

    for kind in stats:
        total = 0
        for p in (assets / kind).rglob('*.jpg') if (assets / kind).exists() else []:
            total += p.stat().st_size
        stats[kind][1] = total

    run_log = {'items': len(ids), 'widths': list(widths),
               'thumbs': {'files': stats['thumbs'][0],
                          'bytes': stats['thumbs'][1]},
               'thumbs_rect': {'files': stats['thumbs-rect'][0],
                               'bytes': stats['thumbs-rect'][1]},
               'notes': log, 'failures': failures}
    assets.mkdir(parents=True, exist_ok=True)
    (assets / 'thumbs-log.json').write_text(
        json.dumps(run_log, indent=1, ensure_ascii=False))
    for kind, (files, b) in stats.items():
        avg = b / files if files else 0
        print(f'{kind}: {files} files, {b / 1e6:.1f} MB total, '
              f'{avg / 1024:.0f} KB average')
    print(f'notes: {len(log)}, failures: {len(failures)}')
    for f in failures:
        print('FAIL:', f)
    print(f'log written to {assets / "thumbs-log.json"}')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
