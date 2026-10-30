# UI round 7 — navigation audit

Date: 2026-10-30

Scope: navigation and structure only. The round-6 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 1,322 items (round 6
was written at 1,295; the +27 came from wave 6, not from this round).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html (index.html last touched by round 6, vr.html by round 4).
The nightly import had already landed (wave 6, STA-1296–STA-1322)
before this round started.

## Paths walked

Gallery: landing → shelf or collection → card → next card → back;
search → result → card → back to the same results.

VR Parlor: enter → shelves → set → reading → switch set → exit;
the flat control row in both states.

## Gallery friction found

1. The viewer "Research Notes" link opened in the same tab, walking
   away from the viewer and the filtered list behind it. Its sibling
   external links in the same viewer panel ("View source on
   Wikimedia Commons", "Full resolution") already open in a new tab,
   so this one was the odd link out, and the only incidental external
   link inside a stateful overlay.
2. Shelf tiles, Finding Aid rows, and register rows were clickable
   but unreachable by keyboard. Grid cards already take Enter/Space
   with a visible focus ring, so a keyboard visitor could work the
   grid but could not open a Recent Accessions tile, pull a
   collection or series from the Finding Aid, or open a register row
   at all.

## Gallery changes shipped

1. The viewer "Research Notes" link opens in a new tab
   (target="_blank" rel="noopener"), like the source and full
   resolution links beside it. The viewer and its filtered list stay
   open behind it.
2. Shelf tiles, Finding Aid rows (collections and series), and
   register rows take keyboard Enter/Space like grid cards, with
   tabindex, a button role on the tiles and rows (register rows keep
   their table-row context, so no role there), and the same brass
   focus ring the grid cards already have.

## Parlor friction found

1. The flat row's wall paging hit a dead end with no visible state.
   In browse state, flat Prev/Next and the jump buttons page the
   wall, but at the first or last wall page the spent direction
   silently did nothing. The wall header names the page in the 3D
   view, but the flat row itself carries no page position, so a flat
   visitor paging the wall met an unmarked dead tap — the same class
   of fault rounds 4 and 6 fixed for the flat buttons in browse and
   for "Request an item" on empty results.

## Parlor changes shipped

1. Flat Prev/Next/jump buttons disable at the wall ends while
   browsing (Prev and « at the first page, Next and » at the last),
   with a dimmed disabled style matching the gallery's. In reading
   state the same buttons wrap, so they stay live there. Random
   stays live in both states: it always has a destination.

## Deliberately not changed

- Viewer stepping still wraps from the last result to the first,
  and the ten-card jumps wrap the same way; the position line
  ("Result 1313 of 1322") already says where the jump landed
  (held from round 4).
- "Clear search & filters" still does not reset the sort, in the
  toolbar or in the empty state. Sort is not a filter (held from
  round 4).
- Finding Aid collection rows still do not toggle off on a second
  tap. The "All holdings" row and the Clear button already reset a
  collection (held from round 4). The new keyboard behavior fires
  the same action as a click, it does not add a toggle.
- No way to add to the Reading List from inside the Parlor. That is
  a feature, not a navigation fix, and the gallery heart remains the
  one place a list is built (held from round 4).
- Recent Accessions shelf cards still open into the full catalog
  for stepping, not into the 10 recent items. Stepping inside just
  the 10 would trap the visitor there (held from round 5).
- Filter state was not moved into the gallery URL, and Browser Back
  was not rebound to close the viewer — both held from round 3, so
  the record permalink scheme is untouched.
- The viewer's "VR Parlor" link and the Finding Aid "Browse in VR"
  links still navigate in the same tab. Those are deliberate jumps
  that carry the card or set with them, not incidental links out of
  a stateful view.
- The in-room 3D paging buttons are unchanged: the wall header
  already names the page beside them, so their ends are visible.
  Keyboard wall paging at the ends still clamps silently; there is
  no visual affordance to fix for keys.
- No visual restyle was made. New controls reuse the existing
  buttons, brass accent, squared corners, and type.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup ("WebGL domain policy ... supplied by browser-daemon"),
so the round-6 headless-Chrome harness could not run here. The round-7
harness runs the real index.html in jsdom instead, with a fetch stub
serving the repo's browse.json, data.json, search chunks, and per-item
records from disk (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round7-jsdom.cjs;
the Chrome harness is kept, updated, at ui-round7-harness.mjs for a
machine where the managed browser starts):

- 26 checks, 0 failures: full catalog renders (1322 of 1322, 48
  cards on the first page); era options read exactly 1322 / 615 /
  331 / 108 / 268; "Show more" reads "Show more items · 1274
  remaining" (round 5 holds); search narrows (Niagara → 23) and the
  empty state shows its clear button with "Request an item" disabled
  (rounds 5 and 6 hold); empty-state clear restores the catalog;
  count line reads "Sorted: Oldest first" for the old-first sort
  (round 4 holds); viewer opens with "Result 1 of 1322 · All items",
  jump forward lands on "Result 11 of 1322", Shift+ArrowRight on
  "Result 21 of 1322", jump back returns through 11 to 1, jump back
  from the first wraps to "Result 1313 of 1322", and the viewer
  closes back to the results; Research Notes carries target _blank
  and rel noopener; shelf tiles and Finding Aid rows carry tabindex
  0 and button role; Enter on a shelf tile opens "Result 1322 of
  1322 · All items"; register rows carry tabindex 0 and Enter on one
  opens "Result 1 of 1322 · All items".

Parlor: the full vr.html needs CDN three.js, which this headless
Chrome cannot reach, so the flat-button change was verified at the
logic level instead: the shipped syncFlatWallButtons function was
extracted from vr.html (not copied) and executed against stubbed
state (ui-round7-parlor-check.mjs), 7 checks, 0 failures — browse
first page disables Prev/« only, middle page disables nothing, last
page (55 of 56 for the 1,322-card set) disables Next/» only,
single-page set disables all four, reading disables nothing, and
both call sites (renderWall, setState) are present. Both edited
scripts also pass node --check with no syntax errors.

Live-verified on vrparlor.com after push: index.html and vr.html
both 200, served bytes identical to the repo (identical on the
second check, after the Pages deploy caught up with the push), the
new-tab Research Notes link, the shelf-tile keyboard attributes,
and the syncFlatWallButtons code present in the served files.

## Commits (one per change, each revertible on its own)

1. `49f9e2a` — Gallery: viewer Research Notes link opens in a new
   tab
2. `f499939` — Parlor: flat wall-paging buttons disable at the wall
   ends while browsing
3. `80e71aa` — Gallery: shelf tiles, Finding Aid rows, and register
   rows take keyboard Enter/Space like grid cards

## Veto list

1. Gallery viewer Research Notes link opens in a new tab.
2. Parlor flat wall paging buttons disable at the wall ends while browsing.
3. Gallery shelf tiles, Finding Aid rows, and register rows take keyboard Enter and Space like grid cards.
