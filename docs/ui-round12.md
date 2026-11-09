# UI round 12 — one-item viewer arrows, the clipped loading line, and a Parlor Recent Accessions set

Date: 2026-11-09

Scope: navigation and structure only. The round-11 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 2,183 items (round 11
was written at 1,976; the +207 came from wave 7 imports, not from
this round).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html. No import landed during the round.

## Paths walked

Live browser walk of vrparlor.com (02:42–02:48 CST, 1920×999 viewport;
the phone-size check could not be done — the walker's window could
not be resized) plus source audit: gallery landing → shelf/collection
→ card → next card → back; search → result → card → back to the same
results; viewer modes and keyboard paths. VR Parlor: flat page load,
wall, control row, Find search; the headset landing and in-room row
were not walked live this round (round 11 covered them).

## Gallery friction found

- In a one-item result list the viewer step arrows looked live but
  stepped nowhere, with no feedback: Next and Previous (and the
  ten-card jumps) re-showed the same card. A single result has
  nowhere to step to, and nothing said so.
- The viewer loading line was squeezed to the far edge of the image
  area and partly clipped in the rectified modes. It sits in the
  slide flex row beside the full-width split, so the split takes the
  row and the line gets what is left. Confirmed in the source as
  well as live (Parallel mode, STA-0001).
- "How to view" was checked live at the round-11 candidate's request:
  the heading lands fully visible, about 200 px below the sticky
  toolbar. No fix needed; the toolbar covering content on ordinary
  manual scroll is the already-held normal sticky-header behavior.

## Parlor friction found

- The gallery's Recent Accessions shelf has no Parlor equivalent. A
  VR visitor could only reach new cards by paging 91 wall pages of
  All cards. The shelf itself is a first-class landing feature; the
  Parlor had no way to it at all.

## Gallery changes shipped

1. The viewer step arrows read disabled on a one-item result list.
   showCurrent disables Previous, Next, and both ten-card jumps
   while the list has a single item, and re-enables them on any
   longer list. The keyboard arrows still wrap, with the position
   line ("Result 1 of 1") saying where they landed.
2. The viewer loading line floats centred over the stage. It is now
   an absolutely positioned overlay on a dark pill, instead of a
   flex item squeezed beside the split.

## Parlor change shipped

3. A Recent Accessions set, mirroring the gallery shelf. deriveSets
   adds the last ten cards, newest first, the same order the gallery
   shelf shows them; it is listed in the flat set selector and in
   the finding-aid cabinet's Start group, with its count. It takes
   the same ?set=recent deep link and saved-state restore as every
   other set. Catalog data is untouched, and no comfort invariant
   changes: the set is a list of indices, like every other set.

## Deliberately not changed

- The round-11 deliberately-not-changed list still stands in full:
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
  so both directions are spent. The card-stepping path there is
  opening a tile or "Back to the card", which switches to reading
  where the same buttons step cards. The live walk flagged it as
  broken; the source and the round-7 doc confirm it is working as
  designed, so no change was made.
- The "Catalogue card: off" button reading disabled in the flat
  Parlor is the round-8 design: the catalogue card has no work while
  browsing, so the toggle reads disabled there. It enables as soon
  as a card is opened.
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
  opened, which the browser scrolls into view. The walk's "landed
  at the results area" is that restored position, not a lost one.
- No bigger change was needed this round: the audit found small
  clear wins, so the Nov 1 bigger-change latitude was not invoked.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–11), so the round-12 harness runs the
real index.html in jsdom instead, with a fetch stub serving the
repo's browse.json, data.json, search chunks, and per-item records
from disk, and an Image stub that fires onload (or onerror for a
harness-set URL pattern) so loadRect's host fallback runs in the real
page code (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round12-jsdom.cjs).
Expectations are computed from the repo's own browse.json and search
chunks, so a catalog import between rounds does not stale them:

- 52 checks, 0 failures: full catalog renders (2183 of 2183, 48
  cards on the first page); era options read exactly 2183 / 1141 /
  599 / 116 / 327; "Show more" reads "Show more items · 2135
  remaining" (round 5 holds); search narrows (Niagara → 23) and the
  empty state shows its clear button with "Surprise me" disabled
  (rounds 5 and 6 hold); empty-state clear restores the catalog;
  count line reads "Sorted: Oldest first" for the old-first sort
  (round 4 holds); viewer opens with "Result 1 of 2183 · All items",
  jump forward lands on "Result 11 of 2183", Shift+ArrowRight on
  "Result 21 of 2183", End jumps to "Result 2183 of 2183", Home
  returns to "Result 1 of 2183", jump back from the first wraps to
  "Result 2174 of 2183", and the viewer closes back to the results;
  Research Notes carries target _blank and rel noopener (round 7
  holds); shelf tiles and Finding Aid rows carry tabindex 0 and
  button role (round 7 holds); Tab from the viewer's last control
  wraps to its first (vFav) and Shift+Tab from its first wraps to
  its last (vFull), and ArrowRight still steps to "Result 2175 of
  2183" after the trap checks (round 8 holds); Enter on a shelf tile
  opens "Result 2183 of 2183 · All items"; register rows carry
  tabindex 0 and Enter on one opens "Result 1 of 2183 · All items";
  Timeline view shows while the grid hides, the first band reads
  "1820s · 2 items", the 1850s band carries its full filtered count
  of 261 items, the sort control reads disabled and the count line
  reads "In date order" in Timeline view, the first Timeline card
  opens the chronological first item (STA-0695, "Result 1 of 2183 ·
  All items"), leaving Timeline re-enables the sort and restores the
  grid, and with the era filter set to Undated the Timeline shows
  exactly one band, "Undated · 327 items", with no 1900s band; the
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
  (round 12). The edited script also passes a syntax parse with no
  errors.

Headless harness, Parlor: the full vr.html needs CDN three.js, so
the shipped set functions are extracted from vr.html (not copied)
and executed against stubbed state (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round12-parlor-check.mjs,
which supersedes the round-11 Parlor harness):

- 72 checks, 0 failures: the round-11 search scenarios all still
  hold (transient Search set with its matches, spliced after All
  cards, first match opens, selector and cabinet carry its count,
  no-match report keeps the old search, replacement, save on a
  search set, clear back to All cards on the same card, clear while
  on another set, empty search clears); the round-10 save scenarios
  all still hold through rebuildSets; the Recent Accessions set is
  the last ten cards newest first, sits in the Start group after All
  cards, is listed in the finding-aid entries on the Start page, and
  is carried in the set selector with its count, and saving while on
  it keeps the set and the current card (round 12); the call-site
  checks confirm the Find box, Find and Clear wiring, Enter-to-
  search, the keydown/drag/click guards, the cabinet listing,
  rebuildSets re-inserting the search set, the in-room row showing
  only in a VR session, and the round-10 save wiring (drawCaption
  sync, flat Save button, in-room SAVE pill dim at start). Both
  vr.html script blocks also pass node --check with no syntax errors.

Live verification: [to be filled after push]

What only a headset can judge: whether the in-room control row still
reads clearly in VR now that it shows only inside a session, and
whether the eight-pill reading row still feels uncrowded at arm's
length (held from round 10). Those are Clay's call in the headset.

## Commits (one per change, each revertible on its own)

1. `90dd00f` — Gallery: viewer loading line floats centred over the stage
2. `2772899` — Gallery: viewer step arrows disable on a one-item result list
3. `11c4028` — Parlor: Recent Accessions set, mirroring the gallery shelf

## Veto list

1. Gallery viewer loading line ("Loading the rectified pair…",
   "Building the 3D view…") now floats centred over the stage on a
   dark pill, instead of sitting squeezed at the edge of the image
   area.
2. Gallery viewer step arrows (Previous, Next, and both ten-card
   jumps) read disabled when the result list has a single item, where
   they used to look live and step nowhere.
3. Parlor Recent Accessions set: the last ten cards, newest first,
   listed in the set selector and the finding-aid cabinet like any
   other set.
