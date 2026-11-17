# UI round 15 — results below the fold, a reading list that lies about being empty, and a Parlor that promises VR it cannot give

Date: 2026-11-17

Scope: navigation and structure only. The round-14 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 3,011 items (round 14
was written at 2,805; the +206 came from wave 13 imports, not from
this round).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html. The nightly import had already landed (wave 13, through
STA-3011) before this round started; the paced IA masters upload
running during the round touches the Archive only, never index.html
or vr.html.

## Paths walked

Live browser walk of vrparlor.com (02:41–02:53 CST, 1920×1000 viewport)
plus source audit: gallery landing → shelf/collection → card → next
card → back; search → result → card → back to the same results;
Shuffle and Shuffle again; views Shelves, Register, and Timeline;
Reading List save/unsave from the grid and from the list; viewer
keyboard paths; Finding Aid rows and their Browse in VR links; Parlor
flat page load, wall, control row, Find search, Random, browse vs.
reading button states. The headset landing and in-room row were not
walked live this round (round 11 covered them).

## Gallery friction found

- A search or a filter changed what the list held, but the list sits
  below the shelf and the finding aid: typing "Niagara" in the sticky
  toolbar left the results below the fold with nothing bringing them
  into view. Confirmed live — "SHOWING 23 OF 3011 ITEMS · SEARCH:
  "NIAGARA"" while the page still showed the Finding Aid and Recent
  Accessions. Clicking a Finding Aid row and switching views had the
  same gap: the results changed below the fold.
- The Reading List empty state lied when a search filtered it. With
  one card saved and "Niagara" still typed, the list showed "SHOWING
  0 OF 3011 ITEMS" and "Your reading list is empty. Tap the heart on
  any card to keep it here." — the card was saved, only hidden by the
  search — and the empty-state clear button stayed hidden, so there
  was no offered way back to the saved card. The toolbar "Clear
  search & filters" did restore the catalog but also turned the
  Reading List off, which is the round-5 reset semantics, standing.
- A Finding Aid "Browse in VR" link navigated the gallery tab away to
  vr.html, dropping the gallery's filter state: the walk had
  Rijksmuseum + Falls & Rivers (5 items) and one click on the row's
  VR link lost both filters. The link is a shortcut inside a filter
  row; the main "Enter the VR Parlor" button is the same-tab journey.

## Parlor friction found

- The reading status promised "Press Enter VR when ready" on a
  desktop browser while the only VR control read "VR NOT SUPPORTED".
  updateStatus keyed the promise off navigator.xr existing, which is
  true in desktop Chrome, while the VRButton reports support only
  after its own check resolves. The page contradicted its own control.
- Going back to the card left the crumb stale: after "Back to the
  card" the crumb still read "Current set · All cards · Card 172 of
  3011 · Wall page 16 of 126" while reading, because only renderWall
  refreshed the crumb and setState never did. The reading status had
  no wall page, but the crumb — the persistent location label — kept
  the browse fragment.

## Gallery changes shipped

1. Search, filter, and view actions bring the results into view. A
   reveal flag set by the search input, the era dropdown, series
   chips, collection rows, the clear control, and the view switch
   asks render() to scroll the count line into view afterwards. Sort,
   Shuffle again, Show more, and heart toggles do not scroll: they
   reorder or extend the list already on screen. The scroll offset
   is measured off the live toolbar height: the first version used a
   fixed 120px scroll margin, and the live walk caught the count line
   still hiding behind the toolbar, which runs about 195px tall at
   desktop width. The fix commit (eae8a67) measures the toolbar and
   scrolls the count line to 16px below its bottom edge.
2. The Reading List empty state names the filter when saved cards are
   hidden by it: "No saved cards match the current search or
   filters. Clear them to see your saved cards." — with the
   empty-state clear button shown. Clearing there clears only the
   search and filters and stays on the Reading List, so the saved
   cards come back. A truly empty list keeps the original message
   and no button.
3. Finding Aid "Browse in VR" links open in a new tab (target
   _blank, rel noopener), like Research Notes, so the gallery tab
   keeps its filters. The main "Enter the VR Parlor" button keeps
   its same-tab navigation.

## Parlor changes shipped

4. The reading status promises "Press Enter VR" only once the
   support check has resolved in favour. A vrChecked flag is set
   when initMode's check resolves; before that the old wording
   stands, so a headset browser sees nothing change while the check
   runs, and a desktop browser gets "Drag to look around, arrow keys
   flip cards." instead of a promise its button cannot keep. The
   "VR NOT SUPPORTED" button itself is untouched (three.js's own
   state).
5. The crumb refreshes when the state changes. setState now sets the
   crumb from crumbText(), so leaving the shelves for the card drops
   the wall-page fragment; the wall page is still a browse-only
   fragment, and the browse path already refreshed it through
   renderWall.

## Deliberately not changed

- The round-14 deliberately-not-changed list still stands in full:
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
  round-7 rule, and changing it would overturn it. Relabeling only
  the jump buttons while Prev/Next keep the dual meaning would be
  inconsistent, so no relabeling was done either.
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
- The Parlor opening on a saved card and wall page is the saved-state
  restore, by design.
- Dragging a shelf card sideways still does nothing: the buttons are
  the control, and a drag must not hijack the click that opens the
  card.
- The Timeline bands keep their cards in the DOM while hidden (the
  round-14 focus fix scopes around them rather than clearing them);
  they are display:none, untabbable, and harmless.
- Clearing a Parlor search returns to All cards on the same card,
  not the pre-search set (round 11 design). The walk noted the set
  change; the status and crumb match the set actually shown.
- The toolbar "Clear search & filters" still resets everything,
  including leaving the Reading List (round 5 holds); only the
  empty-state clear in a filtered Reading List stays on the list.
- The Timeline sort control still shows the stale sort value while
  disabled (it reads "Shuffle" while the count line says "In date
  order"); the disabled state is the round-9 design and the count
  line already names the order.
- The viewer Escape key still does not close from inside the wiggle
  speed slider (held); the walk did not surface it and the round was
  full — the round-8 Tab precedent remains the pattern if it is
  taken up later.
- No keyboard hint line was added to the viewer: the walk noted its
  absence, but every control is already a Tab-reachable button, so
  it is discoverability polish for a later round, not a fix.
- Sort, Shuffle again, Show more, and heart toggles do not scroll
  the results into view (change 1 draws the line at actions that
  change what the list holds or which view shows it).
- No bigger change was needed this round: the audit found small
  clear wins, so the Nov 1 bigger-change latitude was not invoked.
  A Places view was considered and rejected again: places are free
  text with near-duplicate variants ("Niagara Falls", "Niagara
  Falls, New York", "Niagara Falls, Ontario" are three rows for one
  falls across 224 distinct place strings), so a list would show the
  same place three times unless the catalog data were normalized,
  which bigger changes never touch.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–14), so the round-15 harness runs the
real index.html in jsdom instead, with a fetch stub serving the
repo's browse.json, data.json, search chunks, and per-item records
from disk, and an Image stub that fires onload (or onerror for a
harness-set URL pattern) so loadRect's host fallback runs in the real
page code (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round15-jsdom.cjs).
Expectations are computed from the repo's own browse.json and search
chunks, so a catalog import between rounds does not stale them. The
round-13 checks run first; the round-14 checks re-seed their own
three-item Reading List from the grid, since the round-13 checks
empty the seeded one; the round-15 checks re-seed again from the
grid for the same reason:

- 95 checks, 0 failures: full catalog renders (3011 of 3011, 48
  cards on the first page); era options read exactly 3011 / 1681 /
  806 / 129 / 395; "Show more" reads "Show more items · 2963
  remaining" (round 5 holds); search narrows (Niagara → 23) and the
  empty state shows its clear button with "Surprise me" disabled
  (rounds 5 and 6 hold); empty-state clear restores the catalog;
  count line reads "Sorted: Oldest first" for the old-first sort
  (round 4 holds); viewer opens with "Result 1 of 3011 · All items",
  jump forward lands on "Result 11 of 3011", Shift+ArrowRight on
  "Result 21 of 3011", End jumps to "Result 3011 of 3011", Home
  returns to "Result 1 of 3011", jump back from the first wraps to
  "Result 3002 of 3011", and the viewer closes back to the results;
  Research Notes carries target _blank and rel noopener (round 7
  holds); shelf tiles and Finding Aid rows carry tabindex 0 and
  button role (round 7 holds); Tab from the viewer's last control
  wraps to its first (vFav) and Shift+Tab from its first wraps to
  its last (vFull), and ArrowRight still steps to "Result 3003 of
  3011" after the trap checks (round 8 holds); Enter on a shelf tile
  opens "Result 3011 of 3011 · All items"; register rows carry
  tabindex 0 and Enter on one opens "Result 1 of 3011 · All items";
  Timeline view shows while the grid hides, the first band reads
  "1820s · 2 items", the 1850s band carries its full filtered count
  of 291 items, the sort control reads disabled and the count line
  reads "In date order" in Timeline view, the first Timeline card
  opens the chronological first item (STA-0695, "Result 1 of 3011 ·
  All items"), leaving Timeline re-enables the sort and restores the
  grid, and with the era filter set to Undated the Timeline shows
  exactly one band, "Undated · 395 items", with no 1900s band; the
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
  overflows (round 14); the reveal measures the sticky toolbar for
  its offset and exactly one reveal fires for a typed search, a
  series chip, a collection row, an era choice, and a Timeline
  switch, while changing the sort, Show more, and a heart toggle
  fire none (round 15); the round-15 seed saves three cards
  from the grid, the Reading List shows them, a search matching no
  saved card empties the list to "Showing 0 of 3011 items · Reading
  List · Search: "zzzzqqq"" with the new filtered-empty message and
  the clear button shown, clearing from that state restores "Showing
  3 of 3011 items · Reading List" with the search box empty and the
  Reading List chip still pressed, and a truly empty list keeps the
  original message with the clear button hidden (round 15); all 17
  Finding Aid Browse in VR links carry target _blank and rel
  noopener while the main Enter the VR Parlor button keeps no target
  (round 15). The edited script also passes a syntax parse with no
  errors.

Headless harness, Parlor: the full vr.html needs CDN three.js, so
the shipped set functions are extracted from vr.html (not copied)
and executed against stubbed state (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round15-parlor-check.mjs,
which supersedes the round-14 Parlor harness):

- 87 checks, 0 failures: the round-11 search scenarios all still
  hold, the round-10 save scenarios all still hold through
  rebuildSets, the round-12 Recent Accessions set still holds, the
  round-14 status refresh holds (the same-card refresh redraws the
  caption, wall highlight, persist, and status exactly once, and
  refresh with no current card touches nothing), and the round-15
  checks hold: with VR support resolved absent, the reading status
  reads "Drag to look around, arrow keys flip cards." with no Enter
  VR promise; with support resolved present it promises "Press Enter
  VR when ready."; while the check is still running it keeps the old
  promise; the browse status is untouched; the support check marks
  itself resolved before the landing or flat start; the reading
  status no longer keys the promise off navigator.xr alone; setState
  refreshes the crumb, and the crumb names the wall page only while
  browsing. Both vr.html script blocks pass node --check with no
  syntax errors.

Live verification: after push, curl confirmed the new code served
(index.html carries the reveal, the filtered-empty message, the
new-tab VR links, and the measured offset; vr.html carries vrChecked
and the setState crumb refresh; browse.json serves 3,011 items; both
pages 200). A live browser walk (03:04–03:08 CST) then confirmed
four of the five behaviors and caught the fifth half-working: typing
"Niagara" scrolled to the results but the count line stayed hidden
behind the toolbar, because the first version's fixed 120px scroll
margin was short of the toolbar's ~195px height; the filtered-empty
Reading List showed "No saved cards match the current search or
filters. Clear them to see your saved cards." with its clear button,
and clearing restored the three saved cards with the search box
empty and the list still active, while a truly empty list kept the
original message with no clear button; a Finding Aid "Browse in VR"
link opened vr.html in a new tab with the gallery tab and its
filters intact; the flat Parlor reading status read "Rectified and
comfort checked by the overlay pipeline. Drag to look around, arrow
keys flip cards." with no Enter VR promise and the VR button reading
"VR NOT SUPPORTED"; and the crumb dropped from "CURRENT SET ·
ROBERT N. DENNIS COLLECTION · CARD 1 OF 1676 · WALL PAGE 8 OF 70"
to "CURRENT SET · ROBERT N. DENNIS COLLECTION · CARD 1 OF 1676"
after "Back to the card". The reveal was fixed in the same round
(eae8a67: the offset is measured off the live toolbar height). Two
re-checks of the fix first failed on a stale deploy — GitHub Pages
serves index.html with Cache-Control: max-age=600 and the walk
browser still held the old file, so both ran the old code (the same
~1,441px scroll both times). A third re-check on a cache-busting
URL (03:14–03:15 CST) passed all three triggers: "Niagara",
"Falls & Rivers", and the Dennis collection row each left the count
line fully visible about 20px below the toolbar's bottom edge
(y≈218). Both pages load cleanly with no errors.

What only a headset can judge: whether the in-room control row still
reads clearly in VR now that it shows only inside a session, and
whether the eight-pill reading row still feels uncrowded at arm's
length (held from round 10). Those are Clay's call in the headset.

## Commits (one per change, each revertible on its own)

1. `63ad648` — Gallery: search, filter and view actions bring the results into view
   Follow-up: `eae8a67` — Gallery: reveal offset measures the sticky toolbar height
2. `4b643b3` — Gallery: Reading List empty state names the filter hiding saved cards
3. `4ef6a62` — Gallery: Finding Aid Browse in VR links open in a new tab
4. `f2b92ba` — Parlor: status promises Enter VR only where VR is actually supported
5. `c8d1a29` — Parlor: crumb refreshes when leaving the shelves for the card

## Veto list

1. Gallery search, filters, and view switches now bring the results
   into view (scrolling the count line to just below the toolbar),
   where typing a search used to leave the new results below the
   fold.
2. Gallery Reading List: when saved cards are only hidden by a
   search or a filter, the empty state now says so and offers a
   clear button that restores the saved cards without leaving the
   list, instead of claiming the list is empty.
3. Gallery Finding Aid "Browse in VR" links now open in a new tab,
   like Research Notes, instead of navigating the gallery tab away
   and dropping its filters.
4. Parlor status: on a browser with no VR support the reading status
   now says to drag and use the arrow keys, instead of promising
   "Press Enter VR when ready" while the VR button reads
   "VR NOT SUPPORTED".
5. Parlor crumb: leaving the shelves for the card now drops the
   stale "Wall page …" fragment from the crumb, instead of showing
   it while reading.
