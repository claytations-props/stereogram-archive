# Tagging full run — vision-assigned index tags on the whole catalog

Date: 2026-10-23 (overnight run). Method and vocabulary discipline from
the pilot (docs/tagging-pilot.md). Every card: rectified w1000 viewed,
original-scan fallback when the rect crop was ambiguous; title as
context only; 2–8 vocabulary terms; low-confidence cards held with a
reason, never guessed.

## Vocabulary v2

196 terms: the pilot's 189 + 7 gap candidates that had recurred in the
pilot (trees, pier, town square, pavilion, synagogue, derrick,
headframe). `safe` stayed a candidate (single known occurrence).
build_catalog.py enforces the vocabulary at build time (the check was
not weakened). New candidates this run: 41 mentions, 38 distinct, none
recurring 3+ times (barrels, city hall, bison at 2x each) — all stay
candidates, none added.

## Per-wave results

Each wave: tag_batch.py apply → build_catalog.py → validate_catalog.py
--v2 = 0 errors → one commit + push.

| Wave | Cards | Tagged | Held | Commit | Spot-check |
|---|---|---|---|---|---|
| 1 | 124 | 119 | 5 | 6b782fc | 8/10 |
| 2 | 124 | 118 | 6 | 5225b20 | 10/10 |
| 3 | 124 | 121 | 3 | 8a75813 | 8/10 |
| 4 | 124 | 117 | 7 | ecc90aa | 10/10 |
| 5 | 123 | 120 | 3 | b8d4a26 | 10/10 |
| 6 | 123 | 118 | 5 | 6184b7c | 10/10 |
| 7 | 123 | 120 | 3 | dca6454 | 10/10 |
| 8 | 123 | 114 | 9 | e7465f6 | 10/10 |
| **Total** | **988** | **947** | **41** | | **76/80** |

Catalog total after the run: 985 of 1,026 cards tagged (38 pilot +
947 new), 41 held. Spot-check accuracy 95% (76/80); the 4 misses were
minor second-tag quibbles, corrected in the fix-up pass.

Quality control: validation of the wave files caught 84 single-tag
cards (rule is 2–8); a fix-up vision pass re-reviewed all 84 — 56
gained a genuine second tag, 22 were held, 6 were corrected then held,
and 8 stubborn singles were reviewed by hand: 2 earned a second tag
(STA-0610 palm tree+beach; STA-0934 room interior+construction), 6
held (no second vocabulary term honestly exists).

## Holds

Pilot holds reviewed with original-scan fallback:
- STA-0455 ("Oldest house, Salem, Mass") — RESOLVED: wave 5 and wave 7
  independently tagged house, trees with high confidence.
- STA-0231 ("Sioux camp in Castle Creek valley") — HELD (waves 4 and 7
  agree: distant scatter of pale shapes at the resolution limit; camp
  not verifiable from the image alone).

New holds this run (41 total, low confidence — no tags published):

- Wave 1 (5): STA-0386, STA-0459 (faded beyond resolution), STA-0615,
  STA-0648 (single boulder fills frame), STA-0882.
- Wave 2 (6): STA-0026 (full moon visible — no moon term in
  vocabulary), STA-0079, STA-0270, STA-0288, STA-0567, STA-0575.
- Wave 3 (3): STA-0130, STA-0453, STA-0601 (palm grove, not forest).
- Wave 4 (7): STA-0020, STA-0231, STA-0487, STA-0585, STA-0844,
  STA-0885, STA-0893.
- Wave 5 (3): STA-0224 (wave-1 single tag was wrong — actually a
  walled-city scale model), STA-0512 (tag unverifiable), STA-0803.
- Wave 6 (5): STA-0456, STA-0464, STA-0472, STA-0481, STA-0820.
- Wave 7 (3): STA-0068, STA-0433, STA-0572.
- Wave 8 (9): STA-0049, STA-0351, STA-0367, STA-0385, STA-0401,
  STA-0466, STA-0483, STA-0516 (rect crop showed only card backing;
  original scan verified church), STA-0598.

Full one-line reasons live in ~/workspace/tagging-waves/waveN.json
per card.

## Vocabulary-gap candidates this run

41 mentions / 38 distinct terms; none reached the "plainly recurring"
bar, so none were added. Top: barrels 2x, city hall 2x, bison 2x;
then cabin, fish, boat house, stove, puppet theater, moon, vineyard,
llama, mosque, float, fog bell, fire engine, town hall, safe, gate,
reindeer, tightrope walker, ship model, ore dock, photographer, bee,
ladder, cotton bale, sea turtle, observation tower, arch, tomb (1x
each). `moon` (STA-0026) and `bee` (STA-0885) are the most likely
future additions if they recur.

## Accuracy

Spot-checks: ~10 random tagged cards per wave re-viewed against their
images, 76/80 correct (95%). Errors found were over-eager second tags
(e.g. a rect crop showing only card backing, a wrong "storefront");
all corrected or held in the fix-up pass. Two independent taggers
agreed exactly on STA-0455 (house, trees) and on holding STA-0231 —
the same consistency signal the pilot saw on STA-0164/STA-0165.

## Pipeline changes this run

- `tools/tag_batch.py` (new): applies a vision-review assignments
  file to records with vocabulary + 2–8-count validation; idempotent,
  never overwrites or degrades existing tags; held cards skipped.
- `docs/INGEST_SOP.md`: new §5 documents the post-merge tagging step
  (review → assignments file → tag_batch.py → rebuild → validate →
  commit + push), so future waves ship tagged.
- `docs/speed-switchover-prep.md` (new): measured baselines and the
  queued post-switchover changes (ASSET_BASE wiring, hosted thumbnail
  ladder for grid/hero/recent, optional viewer w1000 rung).
