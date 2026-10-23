# Step 4 speed prep — queued behind the IA image switchover

Written 2026-10-23 (overnight run). Switchover NOT complete tonight
(images item ~1,2xx/7,182), so nothing below was applied; these are the
measured, ready-to-apply changes for the run that does the switchover.

## Measured baselines (live, GitHub Pages, 2026-10-23)

| Slot | Now | Size / time |
|---|---|---|
| Gallery initial payload (browse.json) | Pages JSON | 85.3 KB, ~1.2 s |
| Search (index + one 250-item chunk) | Pages JSON | 187 B + ~14.8 KB |
| Record open (records/STA-####.json) | Pages JSON | ~1 KB |
| Grid card image | Wikimedia Commons 500px thumb of original scan | ~48 KB (measured STA-0082), Commons CDN |
| Hero image (Item of the Day) | Commons 1280px thumb | ~150–250 KB |
| Viewer (pair/parallel/cross/wiggle/anaglyph) | repo-local rect/NN.jpg via relative `rect` field | avg 277 KB, 1.06 s (rect/81.jpg = 397 KB) |
| Parlor texture | same rect/ file via vr.json `rect` | same |

Local/hosted ladder rungs (same content, averages over 40 cards):

| Rung | thumbs/ (original scan) | thumbs-rect/ (rectified) |
|---|---|---|
| w250 | 8.0 KB | 8.1 KB |
| w500 | 26.7 KB | 28.5 KB |
| w1000 | 89.7 KB | 89.9 KB |

## Queued changes (apply in this order after switchover + verify)

1. **Set ASSET_BASE** in `tools/build_catalog.py` to
   `https://archive.org/download/stereogram-archive-images/`,
   regenerate, validate 0 errors, commit + push, live-verify.
   This alone moves the viewer and the Parlor onto IA-hosted rects:
   `render_data_json` and `render_vr_json` already prefix every
   `rect` field with the asset base (verified in code 2026-10-23), so
   `rectUrl(d)` in index.html and the Parlor's texture path keep
   working unchanged — no HTML edits needed for those two slots.
   Live-verify: fetch a data.json rect URL (200, byte-identical to
   repo rect/), fetch one vr.json rect URL, open the viewer and the
   Parlor from the live site.

2. **Grid + hero + recent accessions → hosted `thumbs/` ladder.**
   index.html's `thumb(d,w)` currently builds Wikimedia Commons URLs.
   Replace with an asset-base ladder, same scan content:
   ```js
   const ASSET_BASE='https://archive.org/download/stereogram-archive-images/';
   const ladder=(d,w)=>ASSET_BASE+'thumbs/'+d.id+'/w'+w+'.jpg';
   ```
   - grid cards (now thumb 500): `ladder(d,500)` — ~27 KB vs ~48 KB
   - recent accessions (now thumb 250): `ladder(d,250)` — ~8 KB
   - hero (now thumb 1280): `ladder(d,1000)` — ~90 KB vs ~150–250 KB
   - keep the `data-full` / Original Pair links pointing at Commons
     (`d.img`/`d.full`) — unchanged behavior.
   Displayed content stays the original scan (not the rectified pair),
   so nothing visually changes; bytes drop ~45% per slot and all
   images come from one cacheable host. Live-verify: grid, hero, and
   recent cards render; spot-compare one card's pixels against the
   Commons version.

3. **Optional follow-up (measure first): viewer w1000 rung.**
   Viewer currently needs the full rect (anaglyph reads pixels).
   Serving `thumbs-rect/<STA>/w1000.jpg` (~90 KB) for the pair/
   parallel/cross/wiggle modes and keeping the full rect only for
   anaglyph would cut viewer image bytes ~68%. Not queued as
   automatic — decide after measuring displayed-size quality.

## What NOT to do

- No payload trims to browse.json/data.json/search chunks were
  justified: 85 KB / 238 KB / 15 KB are already lean; chunks load
  lazily. catalog-v2.json (291 KB) is not fetched by any page.
- No redesign, no behavior changes beyond the URL swaps above.
