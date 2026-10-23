#!/usr/bin/env python3
"""Apply vision-assigned index tags to v2 records (ingest tagging step).

The tagging review (human/agent vision pass over newly merged cards'
thumbs-rect w1000 images, original-scan fallback when the rectified
crop is ambiguous) produces an assignments file like:

    {"assignments": {"STA-1027": {"tags": ["factory", "smokestack"],
                                  "conf": "high"},
                     "STA-1028": {"tags": [], "conf": "low",
                                  "reason": "faded beyond recognition"}}}

This tool applies it to records/STA-####.json with the same
vocabulary/confidence discipline the catalog build enforces:

- every tag must be in tools/tag_vocabulary.json (the build also
  refuses out-of-vocabulary tags, so a violation here fails fast);
- 2-8 tags per tagged card;
- low-confidence / empty-tag cards are skipped (left untagged);
- idempotent: a record whose tags already match the assignment is a
  no-op; a record that already has DIFFERENT tags is never
  overwritten or degraded -- the conflict is reported and the card
  is skipped.

Usage:
    python tools/tag_batch.py --assignments tagging/run-####.json
    python tools/tag_batch.py --assignments f.json --sta STA-1027 STA-1029

After a successful apply, regenerate the catalog outputs and validate:
    python tools/build_catalog.py
    python tools/validate_catalog.py --v2
then commit the record changes + regenerated outputs together.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RECORDS = BASE / 'records'
VOCAB = BASE / 'tools' / 'tag_vocabulary.json'

MIN_TAGS, MAX_TAGS = 2, 8


def load_vocabulary() -> set[str]:
    v = json.loads(VOCAB.read_text())
    return set(sum(v['groups'].values(), []))


def load_assignments(path: Path) -> dict:
    doc = json.loads(path.read_text())
    if isinstance(doc, dict) and 'assignments' in doc:
        return doc['assignments']
    if isinstance(doc, dict):
        return doc  # bare {sta: {...}} also accepted
    raise ValueError('assignments file must be an object')


def apply_one(rec_path: Path, entry: dict, vocab: set[str]) -> str:
    """Apply one assignment. Returns an action string for the report."""
    tags = entry.get('tags') or []
    conf = entry.get('conf', 'high')
    if conf == 'low' or not tags:
        return 'skipped (held / low confidence)'
    unknown = [t for t in tags if t not in vocab]
    if unknown:
        raise ValueError(f'out-of-vocabulary tags: {unknown}')
    if not (MIN_TAGS <= len(tags) <= MAX_TAGS):
        raise ValueError(f'{len(tags)} tags, need {MIN_TAGS}-{MAX_TAGS}')
    rec = json.loads(rec_path.read_text())
    existing = rec.get('tags')
    if existing == tags:
        return 'no-op (identical tags already present)'
    if existing:
        return f'CONFLICT skipped (record already tagged: {existing})'
    rec['tags'] = list(tags)
    # Records are stored 1-space-indented with a trailing newline;
    # preserve that so the diff is one added line per card.
    rec_path.write_text(json.dumps(rec, indent=1, ensure_ascii=False)
                        + '\n')
    return f'tagged ({len(tags)} tags)'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--assignments', required=True,
                    help='JSON assignments file from the tagging review')
    ap.add_argument('--sta', nargs='*',
                    help='only apply these STA ids (default: all in file)')
    args = ap.parse_args()

    vocab = load_vocabulary()
    assignments = load_assignments(Path(args.assignments))
    wanted = set(args.sta) if args.sta else None

    applied = skipped = conflicts = errors = 0
    for sta in sorted(assignments):
        if wanted is not None and sta not in wanted:
            continue
        rec_path = RECORDS / f'{sta}.json'
        if not rec_path.exists():
            print(f'{sta}: ERROR no such record', file=sys.stderr)
            errors += 1
            continue
        try:
            action = apply_one(rec_path, assignments[sta], vocab)
        except ValueError as e:
            print(f'{sta}: ERROR {e}', file=sys.stderr)
            errors += 1
            continue
        print(f'{sta}: {action}')
        if action.startswith('tagged'):
            applied += 1
        elif action.startswith('CONFLICT'):
            conflicts += 1
        else:
            skipped += 1
    print(f'applied={applied} skipped={skipped} conflicts={conflicts} '
          f'errors={errors}')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
