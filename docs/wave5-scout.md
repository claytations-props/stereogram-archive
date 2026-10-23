# Wave 5 scout — 2026-10-22 (evening, after wave 4 landed at STA-1026)

Wave 4 COMPLETED Oct 22, 2026: +188 (Paris 32, Amsterdam 26, Minneapolis 33,
Norway 29, Brooklyn Bridge 33, Switzerland 35), catalog at 1,026 items
(STA-0001–STA-1026), all pushed with one atomic commit per vein,
validate_catalog.py --v2 at 0 errors. Existing publisher coverage is thin:
9 Underwood, 10 Keystone, 0 Savage, 2 Griffith mentions by title keyword
(all deduped automatically by the engine's skipped_duplicates gate).

Four scouted veins for wave 5. Category file counts verified live on
Commons 2026-10-22; query pools verified deep (harvest_query returned 50/50
candidates = search cap, so pools are larger than the harvest size).

## Vein 1: Underwood & Underwood
- Category: `Category:Stereoscopic views by Underwood & Underwood` — 1,217 files
- Harvest: `--query "Underwood & Underwood stereoscopic view" --count 40`
- Why: the premier American stereo publisher (Spanish-American War, Boxer
  Rebellion, Boer War, WWI, world tours). Fills the thin war shelf (31) and
  adds named-publisher depth. PD-old, engine license gate applies.

## Vein 2: Keystone View Company
- Category: `Category:Stereo cards published by Keystone View Company` — 315 files
- Harvest: `--query "Keystone View Company stereoscopic" --count 35`
- Why: major educational publisher; 10 existing cards, engine dedupes the rest.

## Vein 3: C. R. Savage (NYPL)
- Category: `Category:NYPL Stereoscopic views by C. R. Savage` — 164 files
- Harvest: `--query "C. R. Savage stereoscopic view" --count 30`
- Why: Utah/Western views with Dennis-collection provenance at NYPL
  ("No known copyright restrictions"); 0 existing cards.

## Vein 4: Griffith & Griffith
- Category: `Category:Griffith & Griffith` — 101 files (+2 subcats)
- Harvest: `--query "Griffith & Griffith stereoscopic" --count 25`
- Why: Philadelphia publisher, fairs/exposition strength; 2 existing cards.

Projected yield at wave-4 rates (~80% of candidates pass gates):
~105-115 new cards, landing catalog ~1,130-1,140.

Launch (venv has cv2 at ~/workspace/.venvs/cv):
  cd ~/workspace/stereogram-archive
  ~/workspace/.venvs/cv/bin/python tools/batch_engine.py --query "<q>" --count <n> --staging staging/wave5-<name>

Then per the standing rule: per-card organization checks at merge
(shelf fit vs title, date guard, place fills, creator extraction from title
"by" lines, provenance split), merge_batch, build_catalog.py,
validate_catalog.py --v2, one atomic git push per vein, live-verify
data.json/browse.json, report after.

Clay has NOT directed wave 5 yet — every wave so far started with his
"run"/"keep going". This scout is preparation only; present "wave 5 scouted,
ready to run" and wait for his word.
