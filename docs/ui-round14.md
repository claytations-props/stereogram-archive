# UI round 14 — the heart that lost focus, a shelf with no handle, and a stale Parlor status line

Date: 2026-11-15

Scope: navigation and structure only. The round-13 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 2,805 items (round 13
was written at 2,390; the +415 came from wave 10 and wave 11 imports,
not from this round).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html. The nightly import had already landed (wave 11, through
STA-2805) and pushed before this round started; the paced IA masters
upload running at round start had finished before any edit, and it
touches the Archive only, never index.html or vr.html. The live site
read 2,702 items during the walk and 2,805 on a re-check minutes later:
GitHub Pages was still deploying wave 11 when the walk ran, not a
catalog problem.

## Paths walked

Live browser walk of vrparlor.com (02:42–02:51 CST, 1920×999 viewport)
plus source audit: gallery landing → shelf/collection → card → next
card → back; search → result → card → back to the same results;
Shuffle and Shuffle again; Reading List save/unsave from the grid and
from the viewer; Parlor flat page load, wall, control row, Find search,
Random, browse vs. reading button states. The headset landing and
in-room row were not walked live this round (round 11 covered them).

## Gallery friction found

- Saving a card from the grid with the keyboard lost focus. The heart
  toggle rebuilds the grid, which destroyed the button focus was on:
  focus fell to the top of the page and the next Tab restarted at the
  first card (STA-0001), however far down the grid the saved card was.
  Confirmed live, on both save and unsave, and in the source
  (fb.onclick calls render(), which rebuilds every card).
- The Recent Accessions shelf has no sideways control. Ten cards, about
  six and a half visible at desktop width, and the only ways across
  were the thin scrollbar or a wheel/trackpad gesture; dragging a card
  did nothing (a dead gesture — it neither scrolled nor opened the
  card). A mouse visitor had no visible handle to reach the last three
  cards.

## Parlor friction found

- Clearing a Find search on the same card left the status line stale:
  after "Clear the search ✕" the set was back to All cards, the card
  and the crumb were right, but the status line still read "Browsing
  Search: "niagara". Click a card on the wall to open it, or go back
  to the card." showPos's same-card path refreshed the caption but
  not the status line, and clearParlorSearch relies on showPos for the
  refresh. The same hole covered any other same-card refresh (saving
  while the Reading List set appears or disappears).

## Gallery changes shipped

1. A keyboard heart toggle on a grid card keeps focus on the same
   card's heart after the rebuild. When the card leaves the list
   (unsaving from the Reading List grid) focus moves to the card that
   slid into its place, and when the list is now empty it moves to
   the Reading List chip. Mouse toggles leave focus alone. The lookup
   stays inside the current view's own container: the Timeline bands
   keep their cards in the DOM while hidden, and an unscoped query
   handed focus to a card the visitor could not see (caught by the
   harness, which visits Timeline before the Reading List checks).
2. The Recent Accessions shelf gets ‹ › buttons riding its edges,
   reusing the viewer's round step buttons. They step one tile at a
   time and read disabled at each end, like the Parlor's flat wall
   buttons.

## Parlor change shipped

3. The status line refreshes when the card does not change. showPos's
   same-card funnel (refreshContext) now calls updateStatus alongside
   the caption, wall highlight, and persist, so both showPos paths
   leave the status current. No comfort invariant changes: this is
   the flat status text only.

## Deliberately not changed

- The round-13 deliberately-not-changed list still stands in full:
  viewer stepping wraps; Clear does not reset sort or view; Finding
  Aid collection rows do not toggle off; Recent Accessions shelf
  cards open into the full catalog; filter state is not in the
  gallery URL and Browser Back is not rebound to close the viewer;
  series chip and era dropdown counts stay catalog-wide; the viewer
  Escape key still does not close from inside the wiggle speed
  slider; the in-room 3D paging buttons are unchanged; no visual
  restyle; no map view (places are still free text with no
  coordinates); no shareable Reading List link; no copy-link button
  in the viewer; the sticky toolbar covering the top of the shelf
  and Register rows on scroll is normal sticky-header behavior; the
  Timeline stays decade bands; Register rows keep no open affordance
  beyond hover highlight and their button role; era overlap and
  Oldest-first ordering are data semantics; series chips summing past
  the catalog total is membership, not a partition; the finding-aid
  cabinet's page arrow keeps the same brass disc; the catalogue card
  keeps its designed position in flat mode; "VR NOT SUPPORTED" is
  three.js's own disabled button state; wall thumbnails filling in
  progressively on a page turn is network loading.
- The flat Parlor Prev/Next reading disabled in a one-page search
  set is the round-7 design, not a bug: in browse state the flat
  buttons page the wall, and a 23-card search set has one wall page,
  so both directions are spent. The walk re-flagged it as confusing;
  the source and the round-7 doc confirm it is working as designed,
  and the crumb already says "Wall page 1 of 1", so no change was
  made. The same walk note covers the buttons changing meaning
  between browse (wall pages) and reading (cards): that is the
  round-7 rule, and changing it would overturn it.
- Unsaving a card in the viewer silently moves the viewer to another
  saved card: that is the round-13 shipped behavior (veto item 2),
  mirroring the Parlor since round 10, and the position line says
  where it landed ("Result 1 of 1"). The walk re-flagged it as
  unannounced; the behavior stands.
- "Clear search & filters" still does not reset the sort (round 4/5
  holds: sort is not a filter), so clearing a Shuffle leaves the
  list shuffled. The walk noted it; the count line says "Shuffled".
- Grid images and Parlor wall tiles briefly showing as black
  rectangles while they load is network loading, not a defect.
- The Finding Aid panels looking empty in one walk screenshot and
  populated on re-read is the same paint artifact as round 13, not
  reproduced as a defect.
- The Parlor opening on a saved card and wall page (STA-0169, page 8
  of 113 in the walk) is the saved-state restore, by design.
- Dragging a shelf card sideways still does nothing: the buttons are
  the control, and a drag must not hijack the click that opens the
  card.
- The Timeline bands keep their cards in the DOM while hidden (the
  round-14 focus fix scopes around them rather than clearing them);
  they are display:none, untabbable, and harmless.
- No bigger change was needed this round: the audit found small
  clear wins, so the Nov 1 bigger-change latitude was not invoked.
  A Places view was considered and rejected as the bigger candidate:
  places are free text with near-duplicate variants ("Niagara Falls",
  "Niagara Falls, New York", "Niagara Falls, Ontario" are three
  rows for one falls across 224 distinct place strings), so a list
  would show the same place three times unless the catalog data were
  normalized, which bigger changes never touch.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–13), so the round-14 harness runs the
real index.html in jsdom instead, with a fetch stub serving the
repo's browse.json, data.json, search chunks, and per-item records
from disk, and an Image stub that fires onload (or onerror for a
harness-set URL pattern) so loadRect's host fallback runs in the real
page code (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round14-jsdom.cjs).
Expectations are computed from the repo's own browse.json and search
chunks, so a catalog import between rounds does not stale them. The
round-13 checks run first; the round-14 checks re-seed their own
three-item Reading List from the grid, since the round-13 checks
empty the seeded one:

- 77 checks, 0 failures: full catalog renders (2805 of 2805, 48
  cards on the first page); era options read exactly 2805 / 1546 /
  755 / 126 / 378; "Show more" reads "Show more items · 2757
  remaining" (round 5 holds); search narrows (Niagara → 23) and the
  empty state shows its clear button with "Surprise me" disabled
  (rounds 5 and 6 hold); empty-state clear restores the catalog;
  count line reads "Sorted: Oldest first" for the old-first sort
  (round 4 holds); viewer opens with "Result 1 of 2805 · All items",
  jump forward lands on "Result 11 of 2805", Shift+ArrowRight on
  "Result 21 of 2805", End jumps to "Result 2805 of 2805", Home
  returns to "Result 1 of 2805", jump back from the first wraps to
  "Result 2796 of 2805", and the viewer closes back to the results;
  Research Notes carries target _blank and rel noopener (round 7
  holds); shelf tiles and Finding Aid rows carry tabindex 0 and
  button role (round 7 holds); Tab from the viewer's last control
  wraps to its first (vFav) and Shift+Tab from its first wraps to
  its last (vFull), and ArrowRight still steps to "Result 2797 of
  2805" after the trap checks (round 8 holds); Enter on a shelf tile
  opens "Result 2805 of 2805 · All items"; register rows carry
  tabindex 0 and Enter on one opens "Result 1 of 2805 · All items";
  Timeline view shows while the grid hides, the first band reads
  "1820s · 2 items", the 1850s band carries its full filtered count
  of 287 items, the sort control reads disabled and the count line
  reads "In date order" in Timeline view, the first Timeline card
  opens the chronological first item (STA-0695, "Result 1 of 2805 ·
  All items"), leaving Timeline re-enables the sort and restores the
  grid, and with the era filter set to Undated the Timeline shows
  exactly one band, "Undated · 378 items", with no 1900s band; the
  view toggle reads aria-pressed true on Shelves at load, follows
  Register and Timeline on click, and Shelves reads false while
  another view is active; the viewer picture starts transparent
  until its file loads (round 11); Parallel mode loads the rectified
  pair from the Archive (rect/00.jpg) and falls back to this site
  when the Archive fails (round 11); the Anaglyph path runs through
  the same loader (in jsdom the draw itself reports "blocked"
  because jsdom has no 2d canvas — the loader and error path are
  what the check covers); a one-item search ("sta-0001") narrows to
  exactly 1, the viewer opens at "Result 1 of 1 · Search:
  "sta-0001"" with all four step arrows disabled, and clearing the
  search and reopening shows them live again (round 12); the loading
  line's stylesheet rule positions it absolutely at 50%/50% with a
  -50%/-50% translate, and it computes as absolutely positioned
  (round 12); the Shuffle again button is hidden while the sort is
  Accession order, shows while Shuffle is the sort with the count
  line reading "Shuffled", draws a fresh order on click (first three
  cards change), keeps the "Shuffled" count line after the re-shuffle,
  and hides again off Shuffle (round 13); the Reading List holds the
  three seeded items, the viewer opens on the third at "Result 3 of
  3 · Reading List", unsaving it slides the viewer to "Result 2 of
  2" on the card that slid into place, unsaving again lands on
  "Result 1 of 1", and unsaving the last card closes the viewer onto
  the empty Reading List state (round 13); the round-14 seed saves
  three cards from the grid (chip "♥ Reading List · 3"); a keyboard
  heart toggle keeps focus on the same card's heart with the chip at
  4 and aria-pressed true, a keyboard unsave keeps focus there with
  the chip back at 3 and aria-pressed false, a mouse toggle does not
  move focus (activeElement is body) and a mouse unsave restores the
  three-item list; in the Reading List grid, unsaving the second card
  moves focus to the card that slid into place (STA-0003) with the
  count at 2, unsaving the first card moves focus to the new first
  card (STA-0003) with the count at 1, and unsaving the last card
  focuses the Reading List chip with the empty state showing (round
  14); the shelf has back/forward buttons with the right aria-labels
  and the navbtn class inside a shelfbox, Next steps one tile
  forward (+170) and Prev one tile back (−170) via scrollBy, Prev is
  disabled at the start with Next live, Prev is live mid-shelf with
  Next disabled at the end, and both are disabled when nothing
  overflows (round 14). The edited script also passes a syntax parse
  with no errors.

Headless harness, Parlor: the full vr.html needs CDN three.js, so
the shipped set functions are extracted from vr.html (not copied)
and executed against stubbed state (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round14-parlor-check.mjs,
which supersedes the round-12 Parlor harness):

- 78 checks, 0 failures: the round-11 search scenarios all still
  hold, the round-10 save scenarios all still hold through
  rebuildSets, the round-12 Recent Accessions set still holds, and
  the round-14 status refresh holds: the same-card refresh redraws
  the caption, wall highlight, persist, and status exactly once,
  refresh with no current card touches nothing, clearing a search on
  the same card returns to All cards and the same-card funnel then
  refreshes the status, the showPos same-card branch goes through
  refreshContext, and refreshContext covers the status line. Both
  vr.html script blocks pass node --check with no syntax errors.

Live verification: after push, curl confirmed the new code served
(index.html carries the shelf buttons and the focus restore; vr.html
carries the status refresh in refreshContext; browse.json serves
2,805 items; both pages 200). A live browser walk (03:03–03:08 CST)
then confirmed all three behaviors: Tabbing to the STA-0008 heart
and pressing Enter saved it with focus staying on the heart (gold
ring visible, no jump to the top of the grid), the next Tab moved to
STA-0009, and unsaving it the same way kept focus on the heart again
with the chip back at "♥ Reading List · 0"; the Recent Accessions
shelf shows ‹ › buttons at its edges, each click stepping one tile
(STA-2804, then STA-2803, then the last cards with STA-2796 at the
edge), with › disabled at the end and ‹ disabled back at the start;
in the flat Parlor a "Niagara" Find followed by clearing the search
returned to All cards with the status line reading "Browsing All
cards", not the stale search text. The walk noted the Parlor landed
on STA-0001 after clearing rather than the pre-search card: that is
the specified behavior (clear returns to All cards on the card on
display, and the search had opened STA-0001 as its first match), not
a defect. Both pages load cleanly with no errors.

What only a headset can judge: whether the in-room control row still
reads clearly in VR now that it shows only inside a session, and
whether the eight-pill reading row still feels uncrowded at arm's
length (held from round 10). Those are Clay's call in the headset.

## Commits (one per change, each revertible on its own)

1. `b3265b4` — Gallery: grid heart toggle keeps keyboard focus on the same card
2. `5b50640` — Gallery: Recent Accessions shelf gets sideways scroll buttons
3. `fe270b3` — Parlor: status line refreshes when the card does not change

## Veto list

1. Gallery grid heart: saving or unsaving a card from the grid with
   the keyboard now keeps focus on that card's heart (or on the card
   that slid into its place, or on the Reading List chip when the
   list empties), instead of dropping focus to the top of the page.
2. Gallery Recent Accessions shelf: ‹ › buttons at its edges step it
   one tile at a time and read disabled at each end, where there used
   to be no sideways control at all.
3. Parlor status line: it now refreshes when the card does not change,
   so clearing a Find search no longer leaves "Browsing Search: ..."
   on screen after the set has gone back to All cards.
