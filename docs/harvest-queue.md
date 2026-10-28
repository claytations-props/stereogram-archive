# Harvest queue — veins for the nightly growth run

Created 2026-10-24 by the nightly growth engine. Seeded from
docs/wave5-scout.md leftovers (publisher veins scouted 2026-10-22 that
were never run — wave 5 ran place veins instead). The nightly run takes
the FIRST queued vein each night, one vein per night.

Entry format: vein name | Commons category | estimated count |
harvest command | why | status.

## Queued

1. **Keystone View Company** — `Category:Stereo cards published by Keystone View Company` — 315 files — `--query "Keystone View Company stereoscopic" --count 35` — major educational publisher; 10 existing cards, engine dedupes the rest — status: RUN 2026-10-26 (wave6-keystone): harvested 35 candidates, 19 passed, 2 held (Teachers' Guide — photo boxes not found; Hindu festival dancers, Tanjore — photo boxes not found), 14 same-scan duplicates, 0 license skips, 0 errors; merged as STA-1246–STA-1264; heavily Alaska/Klondike (8 scans of the Chilkoot "Bound for the Klondike" view, 2 of "A Happy Home in Alaska", 2 Golden Stair prep, 2 distant Chilkoot) plus Niagara winter (Luna Island) and Trincomalee street; place fills from titles only (Chilkoot Pass, Alaska / Alaska / Yukon River, Alaska; Trincomalee left Place unrecorded, caption names both Trincomalee and Kandy); shelf fixes: STA-1260 prospectors camp war→oddities, STA-1257 river cities dropped; 19 tagged, 0 held untagged
2. **C. R. Savage (NYPL)** — `Category:NYPL Stereoscopic views by C. R. Savage` — 164 files — `--query "C. R. Savage stereoscopic view" --count 30` — Utah/Western views, Dennis-collection provenance at NYPL ("No known copyright restrictions"); 0 existing cards — status: RUN 2026-10-27 (wave6-savage): harvested 30 candidates, 19 passed, 1 held (Foundation of Temple — no consistent affine between the halves), 10 same-scan duplicates, 0 license skips, 0 errors; merged as STA-1265–STA-1283; all 19 date-guarded to Undated (titles carry only Savage's 1832–1909 life dates); place fills from titles only (Salt Lake City, Utah / Salt Lake City / Salt Lake / Arizona / Little Zion Valley, Southern Utah), rest Place unrecorded; coll left Source unrecorded (engine's category/description check found no Dennis string in the file records); shelf fixes: 12 corrections (Salt Lake keyword water artifacts dropped on 5 town/temple cards, old-mill pair oddities→water, tabernacle interiors oddities→cities, Young residence pair oddities→cities, coach water→people); 18 tagged, 1 held untagged (STA-1266 Salt Lake Temple — no vocabulary term fits a temple facade)
3. **Griffith & Griffith** — `Category:Griffith & Griffith` — 101 files (+2 subcats) — `--query "Griffith & Griffith stereoscopic" --count 25` — Philadelphia publisher, fairs/exposition strength; 2 existing cards — status: RUN 2026-10-28 (wave6-griffith): harvested 27 candidates, 12 passed, 2 held (Atlantic City Boardwalk and bathers, jpg+png of one view — vertical error 0.64%/0.56% exceeds 0.35%), 13 duplicates (11 same-scan jpg/png pairs, 2 already-in-catalog Refugees' Camp at Golden Gate Park), 0 license skips, 0 errors; merged as STA-1284–STA-1295; mostly 1906 San Francisco earthquake views (9 cards) plus Yellowstone trail, Oakland ferry landing, Atlantic City bathers; place fills: Yellowstone, Wyoming from the engine; all 11 others filled after the run from each item's own Commons category (commits b3890c9, a4bacb1): 10 San Francisco, California (all in "Stereo cards of the San Francisco earthquake of 1906") and Atlantic City, New Jersey for the bathers; shelf fixes: 9 corrections (oddities→cities on 6 SF street/ruin cards, oddities→water on Yellowstone river trail, cities→people on Atlantic City bathers, war→cities on Jefferson Square refugee camp, oddities→mountains+cities on Nob Hill); 12 tagged, 0 held untagged; rects (12) and masters (12) uploaded to IA and verified, STA-0871 master straggler still failing as before

Scouted 2026-10-24 (nightly run): four more Dennis-provenance place veins
from the NYPL collection, verified against Commons live and checked
against the catalog's place coverage (no deep-coverage duplicates).

4. **New Haven, Connecticut** — `Category:NYPL Stereoscopic views of New Haven, Connecticut` — 131 files — `--query "New Haven stereoscopic" --count 30` — 0 existing cards; Yale-town street/architectural views, Dennis provenance — status: queued
5. **Asbury Park and Ocean Grove, New Jersey** — `Category:NYPL Stereoscopic views of Asbury Park and Ocean Grove, New Jersey` — 212 files — `--query "Asbury Park stereoscopic view" --count 30` — 0 existing cards; seaside-resort shelf (tabernacle, bathers, lakes) — status: queued
6. **Oil region of Pennsylvania and New York** — `Category:NYPL Stereoscopic views of the oil region of Pennsylvania and New York` — 111 files — `--query "oil region stereoscopic" --count 30` — 1 existing card; derricks, well-charging, Bradford/Oil City boomtowns — status: RUN 2026-10-25 (oil-region batch, Post #10): harvested 30 candidates, 27 passed, 3 held (Charging an oil well with nitroglycerine — photo boxes not found; Oil rig and buildings — gate metrics; Oil wells and tanks Bradford — vertical error 0.4%), 3 duplicates of existing cards, 0 license skips, 0 errors; merged as STA-1219–STA-1245 (commit 8679f7f, pushed 2026-10-25 after the 27 rects were uploaded to IA and verified); place fills from titles only for Oil City / Bradford / Oil Creek / Pennsylvania / Beaumont TX, rest Place unrecorded; 25 tagged, 2 held untagged (STA-1219, STA-1237)
7. **New York Harbor** — `Category:NYPL Stereoscopic views of New York Harbor` — 319 files — `--query "New York Harbor stereoscopic" --count 35` — 24 existing cards (engine dedupes); Kilburn Brothers, Statue of Liberty at Bedloe's Island, naval parades, working waterfront — status: queued

## Done

1. **Underwood & Underwood** — run 2026-10-24 (wave6-underwood) — harvested 40 candidates: 28 merged (STA-1191–STA-1218), 2 held (auto_rects box failure; vertical error 0.46% > 0.35% gate), 10 same-scan duplicates, 0 license skips — 26 tagged, 2 held untagged (STA-1198 bamboo grove, STA-1208 Amritsar fakirs — vocabulary gaps) — card-caption dates corrected on 10 cards (incl. 3 bogus 1865s → 1887/1893/1899) — status: done

## Skipped

(none)
