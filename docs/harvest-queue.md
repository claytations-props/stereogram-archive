# Harvest queue — veins for the nightly growth run

Created 2026-10-24 by the nightly growth engine. Seeded from
docs/wave5-scout.md leftovers (publisher veins scouted 2026-10-22 that
were never run — wave 5 ran place veins instead). The nightly run takes
the FIRST queued vein each night, one vein per night.

Entry format: vein name | Commons category | estimated count |
harvest command | why | status.

## Queued

1. **Underwood & Underwood** — `Category:Stereoscopic views by Underwood & Underwood` — 1,217 files — `--query "Underwood & Underwood stereoscopic view" --count 40` — premier American stereo publisher (Spanish-American War, Boxer Rebellion, Boer War, WWI, world tours); fills the thin war shelf and adds named-publisher depth — status: queued
2. **Keystone View Company** — `Category:Stereo cards published by Keystone View Company` — 315 files — `--query "Keystone View Company stereoscopic" --count 35` — major educational publisher; 10 existing cards, engine dedupes the rest — status: queued
3. **C. R. Savage (NYPL)** — `Category:NYPL Stereoscopic views by C. R. Savage` — 164 files — `--query "C. R. Savage stereoscopic view" --count 30` — Utah/Western views, Dennis-collection provenance at NYPL ("No known copyright restrictions"); 0 existing cards — status: queued
4. **Griffith & Griffith** — `Category:Griffith & Griffith` — 101 files (+2 subcats) — `--query "Griffith & Griffith stereoscopic" --count 25` — Philadelphia publisher, fairs/exposition strength; 2 existing cards — status: queued

Scouted 2026-10-24 (nightly run): four more Dennis-provenance place veins
from the NYPL collection, verified against Commons live and checked
against the catalog's place coverage (no deep-coverage duplicates).

5. **New Haven, Connecticut** — `Category:NYPL Stereoscopic views of New Haven, Connecticut` — 131 files — `--query "New Haven stereoscopic" --count 30` — 0 existing cards; Yale-town street/architectural views, Dennis provenance — status: queued
6. **Asbury Park and Ocean Grove, New Jersey** — `Category:NYPL Stereoscopic views of Asbury Park and Ocean Grove, New Jersey` — 212 files — `--query "Asbury Park stereoscopic view" --count 30` — 0 existing cards; seaside-resort shelf (tabernacle, bathers, lakes) — status: queued
7. **Oil region of Pennsylvania and New York** — `Category:NYPL Stereoscopic views of the oil region of Pennsylvania and New York` — 111 files — `--query "oil region stereoscopic" --count 30` — 1 existing card; derricks, well-charging, Bradford/Oil City boomtowns — status: queued
8. **New York Harbor** — `Category:NYPL Stereoscopic views of New York Harbor` — 319 files — `--query "New York Harbor stereoscopic" --count 35` — 24 existing cards (engine dedupes); Kilburn Brothers, Statue of Liberty at Bedloe's Island, naval parades, working waterfront — status: queued

## Done

(none yet — queue starts 2026-10-24)

## Skipped

(none)
