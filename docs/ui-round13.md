# UI round 13 — Shuffle again, and the viewer keeping a card it no longer lists

Date: 2026-11-11

Scope: navigation and structure only. The round-12 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 2,390 items (round 12
was written at 2,183; the +207 came from wave 8 imports, not from
this round).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html. The nightly import had already landed (wave 8, through
STA-2390) before this round started, and the paced IA masters upload
running during the round touches the Archive only, never index.html
or vr.html.

## Paths walked

Live browser walk of vrparlor.com (02:42–02:48 CST, 1920×999 viewport)
plus source audit: gallery landing → shelf/collection → card → next
card → back; search → result → card → back to the same results;
viewer modes and keyboard paths; Parlor flat page load, wall, control
row, Find search, Random in both states. The headset landing and
in-room row were not walked live this round (round 11 covered them).

## Gallery friction found

- Shuffle is a one-way door. Choosing Shuffle reorders the grid once,
  but choosing it again does nothing: the select already holds that
  value, so no change event fires and the order stays put. The live
  walk confirmed it — Shuffle twice in a row left the order identical
  (STA-0718, STA-2343, STA-0302… both times), and the only way to a
  fresh order was to pick another sort and come back. A visitor who
  wants a new shuffle has no control that says so.
- Unsaving the card on display while browsing the Reading List left
  the viewer showing a card the list no longer contains. Confirmed
  in the harness against the pre-fix code: viewing the third of three
  saved cards and unsaving it left the viewer on that removed card
  reading "Result 3 of 3" while the list behind it had shrunk to two.
  Stepping then jumped to "Result 2 of 2", so the stale card and the
  stale count were both visible until the next step. The Parlor fixed
  the same hole in its own reading state in round 10; the gallery
  viewer never got the matching fix.

## Parlor friction found

- None that clears the bar. The walk's two Parlor observations are
  both working as designed: in browse state the flat Next/Prev page
  the wall, so on a one-page search set they read disabled (round 7),
  and Random in browse moves the selection to a random card's wall
  page instead of opening it, while in reading it opens a random card
  (round 7). The walk confirmed both behave exactly that way.

## Gallery changes shipped

1. A "Shuffle again" button beside the sort control. It shows only
   while Shuffle is the active sort, and draws a fresh order without
   making the visitor switch sorts away and back. The dropdown itself
   is untouched: picking Shuffle still shuffles once, and the button
   is the re-shuffle control.
2. Unsaving the card on display in the viewer while browsing the
   Reading List moves the viewer to the card that slid into its place
   (clamped to the new last card when it was the last one), and closes
   the viewer if the list is now empty. Saving a card, or unsaving
   while browsing any other list, changes nothing: the card stays in
   those lists, so the viewer keeps showing it.

## Deliberately not changed

- The round-12 deliberately-not-changed list still stands in full:
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
  so both directions are spent. The live walk flagged it as
  confusing; the source and the round-7 doc confirm it is working as
  designed, so no change was made.
- The flat Parlor Random button keeps its two-state behavior (round 7):
  in browse it jumps the wall to a random card's page and highlights
  it, in reading it opens a random card. The walk noted the
  difference; the wall does visibly jump and the card is highlighted,
  so it is not a dead tap, and changing it would overturn the round-7
  rule that flat buttons work the wall while browsing.
- The "Catalogue card: off" button reading disabled in the flat Parlor
  browse state is the round-8 design: the catalogue card has no work
  while browsing. It enables as soon as a card is opened.
- Viewer stepping still wraps with no label that it wraps (held from
  round 4); the position line already says where a jump landed.
- The viewer opening dimmed with "Loading the full record…" is the
  designed async record load, not a defect.
- The Find clear button stays icon-only; it carries an aria-label
  and a title. Long collection and series names stay truncated with
  ellipses in the cabinet and wall captions; that is the designed
  label length.
- Back from the viewer does not restore an exact scroll position:
  the page keeps its scroll offset while the viewer is open (body
  overflow hidden), and closing returns focus to the card that was
  opened, which the browser scrolls into view.
- The walk's screenshot of the Finding Aid Series panel as an empty
  cream rectangle while scrolled down was not reproduced: both panels
  render fully on return to the top, and nothing in the source renders
  the aid lazily or on scroll, so it reads as a paint artifact in the
  walk's screenshots, not a defect. If it recurs live, it is a
  candidate for a later round with a reproducible case.
- No bigger change was needed this round: the audit found small
  clear wins, so the Nov 1 bigger-change latitude was not invoked.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–12), so the round-13 harness runs the
real index.html in jsdom instead, with a fetch stub serving the
repo's browse.json, data.json, search chunks, and per-item records
from disk, and an Image stub that fires onload (or onerror for a
harness-set URL pattern) so loadRect's host fallback runs in the real
page code (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round13-jsdom.cjs).
Expectations are computed from the repo's own browse.json and search
chunks, so a catalog import between rounds does not stale them. The
harness seeds a three-item Reading List in localStorage before the
page script reads it, for the unsave-in-viewer checks:

- 62 checks, 0 failures: full catalog renders (2390 of 2390, 48
  cards on the first page); era options read exactly 2390 / 1249 /
  645 / 116 / 380; "Show more" reads "Show more items · 2342
  remaining" (round 5 holds); search narrows (Niagara → 23) and the
  empty state shows its clear button with "Surprise me" disabled
  (rounds 5 and 6 hold); empty-state clear restores the catalog;
  count line reads "Sorted: Oldest first" for the old-first sort
  (round 4 holds); viewer opens with "Result 1 of 2390 · All items",
  jump forward lands on "Result 11 of 2390", Shift+ArrowRight on
  "Result 21 of 2390", End jumps to "Result 2390 of 2390", Home
  returns to "Result 1 of 2390", jump back from the first wraps to
  "Result 2381 of 2390", and the viewer closes back to the results;
  Research Notes carries target _blank and rel noopener (round 7
  holds); shelf tiles and Finding Aid rows carry tabindex 0 and
  button role (round 7 holds); Tab from the viewer's last control
  wraps to its first (vFav) and Shift+Tab from its first wraps to
  its last (vFull), and ArrowRight still steps to "Result 2382 of
  2390" after the trap checks (round 8 holds); Enter on a shelf tile
  opens "Result 2390 of 2390 · All items"; register rows carry
  tabindex 0 and Enter on one opens "Result 1 of 2390 · All items";
  Timeline view shows while the grid hides, the first band reads
  "1820s · 2 items", the 1850s band carries its full filtered count
  of 268 items, the sort control reads disabled and the count line
  reads "In date order" in Timeline view, the first Timeline card
  opens the chronological first item (STA-0695, "Result 1 of 2390 ·
  All items"), leaving Timeline re-enables the sort and restores the
  grid, and with the era filter set to Undated the Timeline shows
  exactly one band, "Undated · 354 items", with no 1900s band; the
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
  3 · Reading List", unsaving it slides the viewer to "Result 2 of 2"
  on the card that slid into place, unsaving again lands on "Result
  1 of 1", and unsaving the last card closes the viewer onto the
  empty Reading List state (round 13). The edited script also passes
  a syntax parse with no errors.

Headless harness, Parlor: vr.html is untouched this round, so the
round-12 Parlor harness was re-run as a regression check (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round12-parlor-check.mjs):

- 72 checks, 0 failures: the round-11 search scenarios all still
  hold, the round-10 save scenarios all still hold through
  rebuildSets, the round-12 Recent Accessions set still holds, and
  both vr.html script blocks pass node --check with no syntax errors.

Live verification: after push, curl confirmed the new code served
(index.html carries the reshuffle button and the viewer unsave
guard). A live browser walk (02:54–02:57 CST) then confirmed the
behavior: choosing Shuffle shows "SHOWING 2390 OF 2390 ITEMS ·
SHUFFLED" with a "↻ SHUFFLE AGAIN" button beside the sort control,
and clicking it draws a fresh order (first three cards STA-1014,
STA-1774, STA-0757, none of the previous first three STA-1359,
STA-1208, STA-2195) while the count line still reads "Shuffled";
choosing Accession order restores STA-0001–STA-0003 first and the
button is gone. For the unsave fix, three cards were hearted
(STA-0001–STA-0003), the Reading List read 3, and the viewer opened
on the third at "Result 3 of 3 · Reading List"; unsaving it slid the
viewer to "Result 2 of 2" on STA-0002, unsaving again to "Result 1
of 1" on STA-0001 with all four step arrows disabled, and unsaving
the last card closed the viewer onto the empty Reading List state
("SHOWING 0 OF 2390 ITEMS · READING LIST", "Your reading list is
empty…", chip "♥ READING LIST · 0", hash cleared). Both pages load
cleanly: the flat Parlor shows its wall, set selector ("All cards ·
2390", "Recent Accessions · 10"), and crumb, resuming at STA-0169,
the card left open in the previous session. No errors or unexpected
states at any step.

What only a headset can judge: whether the in-room control row still
reads clearly in VR now that it shows only inside a session, and
whether the eight-pill reading row still feels uncrowded at arm's
length (held from round 10). Those are Clay's call in the headset.

## Commits (one per change, each revertible on its own)

1. `da3ef79` — Gallery: Shuffle again button re-shuffles without leaving the Shuffle sort
2. `49a9c7d` — Gallery: viewer moves to the next card when its card is unsaved from the Reading List

## Veto list

1. Gallery "Shuffle again" button beside the sort control: it shows
   only while Shuffle is the active sort, and draws a fresh order on
   click, where picking Shuffle again in the dropdown used to do
   nothing.
2. Gallery viewer: unsaving the card on display while browsing the
   Reading List now moves the viewer to the card that slid into its
   place (and closes the viewer if the list is empty), instead of
   leaving the removed card on screen with a count that no longer
   existed.
