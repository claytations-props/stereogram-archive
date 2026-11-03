# UI round 9 — navigation audit, one bigger change

Date: 2026-11-03

Scope: navigation and structure only. The round-8 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 1,575 items (round 8
was written at 1,369; the +206 came from wave 6 imports, not from
this round).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html (both last touched by round 8, 2026-11-01). The nightly
import had already landed (wave 6, through STA-1575) before this
round started.

## Paths walked

Gallery: landing → shelf or collection → card → next card → back;
search → result → card → back to the same results; register view;
Reading List; empty state; viewer modes and keyboard paths.

VR Parlor: enter → shelves → set → reading → switch set → exit;
the flat control row in both states; the headset landing.

## Gallery friction found

No small clear win cleared the bar. The paths above were walked
against rounds 4–8, and what they found was already fixed: viewer
Tab cycles within the dialog (round 8), shelf tiles, Finding Aid
rows, and register rows take keyboard Enter/Space (round 7),
viewer ten-card jumps (round 6), "Request an item" disables on
empty results (round 6), "Show more" names the remainder (round 5),
the count line names the sort (round 4), and the Parlor flat row
follows state, disables at the wall ends, and names the wall page
(rounds 4, 7, 8). The deliberately-not-changed list below holds.

## The bigger change

This is the first round run under the Nov 1 bigger-change latitude,
and the audit found a missing capability rather than a small fix: a
visitor could filter by four broad eras but had no way to walk the
catalog in date order, decade by decade — the one chronological
path a 1840s–1920s archive would reasonably be expected to offer.
The era dropdown jumps 1840s–1860s in one step, and no existing
view answers "what came next." So this round ships one bigger
change instead of manufacturing small ones.

## Gallery change shipped

1. A Timeline view, a third button in the toolbar view toggle
   beside Shelves and Register. It groups the current filtered list
   into decade bands (1820s–1920s) in date order, each band headed
   with its decade and its full filtered count, e.g. "1850s · 236
   items", so a decade's size reads before "Show more" fills it.
   Cards inside a band reuse the existing card grid, heart buttons,
   and keyboard behavior, and opening a card steps through the
   filtered list in date order, not accession order. The count line
   reads "In date order" in this view, and the sort control reads
   disabled there instead of silently being overridden, since date
   order is the view; leaving the view re-enables it. Undated items
   form their own final "Undated" band and are never folded into
   the 1900s: 280 of them carry a placeholder sort year of 1900,
   so a decade read from the sort year alone would lie. The view
   respects the active search, era, collection, and series filters,
   like Shelves and Register do.

## Parlor friction found

None that cleared the bar, and no Parlor change shipped this round;
vr.html is untouched. The flat set selector already carries counts,
the flat row already follows state and disables at the wall ends,
the crumb already names the wall page while browsing, and the
landing already names the set and card it will open on.

## Deliberately not changed

- Viewer stepping still wraps from the last result to the first,
  and the ten-card jumps wrap the same way; the position line
  ("Result 1566 of 1575") already says where the jump landed
  (held from round 4).
- "Clear search & filters" still does not reset the sort, in the
  toolbar or in the empty state. Sort is not a filter (held from
  round 4). The view toggle is likewise not reset by Clear: a view
  is not a filter.
- Finding Aid collection rows still do not toggle off on a second
  tap. The "All holdings" row and the Clear button already reset a
  collection (held from round 4).
- No way to add to the Reading List from inside the Parlor. That is
  a feature, not a navigation fix, and the gallery heart remains the
  one place a list is built (held from round 4).
- Recent Accessions shelf cards still open into the full catalog
  for stepping, not into the 10 recent items. Stepping inside just
  the 10 would trap the visitor there (held from round 5).
- Filter state was not moved into the gallery URL, and Browser Back
  was not rebound to close the viewer — both held from round 3, so
  the record permalink scheme is untouched. Gallery filters still
  do not survive a Parlor round trip; that is the same held URL
  contract, not a new gap.
- Series chip and era dropdown counts stay catalog-wide, not
  contextual to the selected collection. They describe shelf size;
  re-basing them per filter would make the same chip read a
  different number depending on the path taken to it (held from
  round 8).
- The viewer Escape key still does not close the viewer from inside
  the wiggle speed slider (the input early-return). Untouched; the
  Tab trap deliberately runs before that guard, Escape does not
  (held from round 8).
- The in-room 3D paging buttons are unchanged: the wall header
  already names the page beside them, so their ends are visible.
  Keyboard wall paging at the ends still clamps silently; there is
  no visual affordance to fix for keys (held from round 7).
- No map view was built. Places in the catalog are free text with
  no coordinates ("Virginia (attributed)", "Niagara Falls" in two
  countries), so a map would need a geocoding pass over catalog
  data first; the Timeline uses only the sort year already carried
  for every item. A map stays a candidate for a later round, not
  this one.
- No visual restyle was made. The Timeline bands reuse the shelf
  heading, the card grid, the brass accent, squared corners, and
  type.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7 and 8), so the round-9 harness runs
the real index.html in jsdom instead, with a fetch stub serving the
repo's browse.json, data.json, search chunks, and per-item records
from disk (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round9-jsdom.cjs):

- 38 checks, 0 failures: full catalog renders (1575 of 1575, 48
  cards on the first page); era options read exactly 1575 / 785 /
  395 / 110 / 285; "Show more" reads "Show more items · 1527
  remaining" (round 5 holds); search narrows (Niagara → 23) and the
  empty state shows its clear button with "Request an item" disabled
  (rounds 5 and 6 hold); empty-state clear restores the catalog;
  count line reads "Sorted: Oldest first" for the old-first sort
  (round 4 holds); viewer opens with "Result 1 of 1575 · All items",
  jump forward lands on "Result 11 of 1575", Shift+ArrowRight on
  "Result 21 of 1575", jump back returns through 11 to 1, jump back
  from the first wraps to "Result 1566 of 1575", and the viewer
  closes back to the results; Research Notes carries target _blank
  and rel noopener (round 7 holds); shelf tiles and Finding Aid rows
  carry tabindex 0 and button role (round 7 holds); Tab from the
  viewer's last control wraps to its first (vFav) and Shift+Tab from
  its first wraps to its last (vFull), and ArrowRight still steps
  to "Result 1567 of 1575" after the trap checks (round 8 holds);
  Enter on a shelf tile opens "Result 1575 of 1575 · All items";
  register rows carry tabindex 0 and Enter on one opens "Result 1
  of 1575 · All items"; Timeline view shows while the grid hides,
  the first band reads "1820s · 2 items", the 1850s band carries its
  full filtered count of 236 items, the sort control reads disabled
  and the count line reads "In date order" in Timeline view, the
  first Timeline card opens the chronological first item (STA-0695,
  "Result 1 of 1575 · All items"), leaving Timeline re-enables the
  sort and restores the grid, and with the era filter set to
  Undated the Timeline shows exactly one band, "Undated · 285
  items", with no 1900s band. The edited script also passes
  node --check with no syntax errors.

Parlor: vr.html byte-identical to its round-8 state (no commit
this round touches it), so its round-8 verification still stands.

Live-verified on vrparlor.com after push: index.html and vr.html
both 200, the first live check (about a minute after the push)
showed the pre-change toggle (Shelves and Register only), consistent
with GitHub Pages deploy lag as in round 8; the re-check minutes
later showed the Timeline button present beside Shelves and
Register, clicking it gave the count line "Showing 1575 of 1575
items · In date order" and the bands in order "1820s · 2 items",
"1830s · 1 item", "1840s · 1 item", "1850s · 236 items". The
Parlor page loads intact, showing the card wall for all 1575 items.

## Commits (one per change, each revertible on its own)

1. `9de5676` — Gallery: Timeline view groups the filtered list by
   decade, undated kept apart

## Veto list

1. Gallery Timeline view groups the filtered list by decade, with undated items in their own final band.
