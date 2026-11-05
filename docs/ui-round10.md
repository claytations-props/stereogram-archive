# UI round 10 — navigation audit, two small wins and one bigger change

Date: 2026-11-05

Scope: navigation and structure only. The round-9 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 1,775 items (round 9
was written at 1,575; the +200 came from wave 6 imports, not from
this round).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html. The nightly import had already landed (wave 6, through
STA-1775) before this round started, and no import process was running
during the round.

## Paths walked

Gallery: landing → shelf or collection → card → next card → back;
search → result → card → back to the same results; register view;
Timeline view; Reading List; empty state; viewer modes and keyboard
paths.

VR Parlor: enter → shelves → set → reading → switch set → exit;
the flat control row in both states; the headset landing.

## Gallery friction found

Two small clear wins, both about keyboard and screen-reader users
reaching things sighted visitors already had:

- The view toggle (Shelves / Register / Timeline) is a three-way
  switch whose active state existed only as a class, so a screen
  reader could not tell which view was showing. The chips and the
  viewer mode buttons already carry aria-pressed; the toggle did not.
- The viewer stepped one card and ten cards, but had no way to jump
  to the first or last result. Home and End complete the set.

Everything else on the gallery paths was already fixed in rounds
4–9, and the round-9 deliberately-not-changed list still stands.

## The bigger change

The audit found a dead end in the Parlor's core loop rather than a
small fix: the Parlor could already browse the Reading List — it is
a first-class set there, with its own cabinet rows and flat-selector
entry — but it could not add to it. A card loved in the headset had
to be saved later from the flat gallery, by leaving the Parlor,
finding the card again, and hearting it. That was held in round 4
as "a feature, not a navigation fix," which is exactly what the
Nov 1 bigger-change latitude licenses: one new feature per round
when no small win clears the bar. So this round ships it.

## Gallery changes shipped

1. The view toggle buttons carry aria-pressed, updated in setView
   alongside the class, so the active view is announced.
2. Home and End in the viewer jump to the first and last result.
   They run after the input early-return, so the wiggle speed
   slider keeps its native Home and End behavior.

## Parlor change shipped

3. Save to Reading List from the Parlor. A Save toggle sits in the
   flat control row (♡ Save / ♥ Saved, with aria-pressed), and a
   SAVE pill joins the in-room row beside RECORD (SAVE dim / SAVED
   bright, the same dim language RECORD uses). Both follow the card
   on display, synced from drawCaption on every card change, and
   both write the same stereoFavs key the gallery hearts build, so
   the list is one list in both places. The Reading List set
   appears, grows, and shrinks live: the flat set selector rebuilds
   with its new count and the finding-aid cabinet redraws.
   Removing the card being read from its own set steps to the card
   that slides into its place; removing the last one falls back to
   All cards on the same card. Catalog data is untouched, and no
   comfort invariant changes: the beam, the projector dip, RECORD
   starting hidden, and the sound toggle are exactly as they were.
   The row gains one pill and now measures 2.37 m wide against a
   2.68 m wall. The pill carries the word SAVE, not a heart glyph:
   the in-room labels are drawn on canvas in Georgia, and the flat
   button carries the heart.

## Parlor friction found

None besides the bigger change above. The flat set selector already
carries counts, the flat row already follows state and disables at
the wall ends, the crumb already names the wall page while browsing,
and the landing already names the set and card it will open on.

## Deliberately not changed

- The round-9 deliberately-not-changed list still stands in full:
  viewer stepping wraps; Clear does not reset sort or view; Finding
  Aid collection rows do not toggle off; Recent Accessions shelf
  cards open into the full catalog; filter state is not in the
  gallery URL and Browser Back is not rebound to close the viewer;
  series chip and era dropdown counts stay catalog-wide; the viewer
  Escape key still does not close from inside the wiggle speed
  slider; the in-room 3D paging buttons are unchanged; no visual
  restyle.
- No map view was built. Places in the catalog are still free text
  with no coordinates, so a map would still need a geocoding pass
  over catalog data first (held from round 9).
- No shareable Reading List link was built. A list URL would need a
  new filter state and persistence semantics (a shared list is not
  the visitor's own list); the Parlor save completes the in-room
  loop first, and sharing stays a candidate for a later round.
- No copy-link button was added to the viewer. The URL bar already
  carries the #STA-#### permalink for the card on display as you
  step, so the share path exists; a button would only label it.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–9), so the round-10 harness runs the
real index.html in jsdom instead, with a fetch stub serving the
repo's browse.json, data.json, search chunks, and per-item records
from disk (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round10-jsdom.cjs).
Expectations are computed from the repo's own browse.json and search
chunks this round, so a catalog import between rounds does not stale
them:

- 41 checks, 0 failures: full catalog renders (1775 of 1775, 48
  cards on the first page); era options read exactly 1775 / 926 /
  436 / 116 / 297; "Show more" reads "Show more items · 1727
  remaining" (round 5 holds); search narrows (Niagara → 23) and the
  empty state shows its clear button with "Request an item" disabled
  (rounds 5 and 6 hold); empty-state clear restores the catalog;
  count line reads "Sorted: Oldest first" for the old-first sort
  (round 4 holds); viewer opens with "Result 1 of 1775 · All items",
  jump forward lands on "Result 11 of 1775", Shift+ArrowRight on
  "Result 21 of 1775", End jumps to "Result 1775 of 1775", Home
  returns to "Result 1 of 1775", jump back from the first wraps to
  "Result 1766 of 1775", and the viewer closes back to the results;
  Research Notes carries target _blank and rel noopener (round 7
  holds); shelf tiles and Finding Aid rows carry tabindex 0 and
  button role (round 7 holds); Tab from the viewer's last control
  wraps to its first (vFav) and Shift+Tab from its first wraps to
  its last (vFull), and ArrowRight still steps to "Result 1767 of
  1775" after the trap checks (round 8 holds); Enter on a shelf tile
  opens "Result 1775 of 1775 · All items"; register rows carry
  tabindex 0 and Enter on one opens "Result 1 of 1775 · All items";
  Timeline view shows while the grid hides, the first band reads
  "1820s · 2 items", the 1850s band carries its full filtered count
  of 238 items, the sort control reads disabled and the count line
  reads "In date order" in Timeline view, the first Timeline card
  opens the chronological first item (STA-0695, "Result 1 of 1775 ·
  All items"), leaving Timeline re-enables the sort and restores the
  grid, and with the era filter set to Undated the Timeline shows
  exactly one band, "Undated · 297 items", with no 1900s band; the
  view toggle reads aria-pressed true on Shelves at load, follows
  Register and Timeline on click, and Shelves reads false while
  another view is active. The edited script also passes a syntax
  parse with no errors.

Headless harness, Parlor: the full vr.html needs CDN three.js, so
the shipped save functions are extracted from vr.html (not copied)
and executed against stubbed state (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round10-parlor-check.mjs):

- 30 checks, 0 failures: saving stores the STA id in stereoFavs
  and the Reading List set appears with 1 item; the flat button
  reads "♥ Saved" with aria-pressed true and the pill redraws
  "SAVED" bright; the set selector rebuilds with "Reading List ·
  1"; the cabinet redraws on save and the wall is not rebuilt when
  its set did not change; unsaving clears the list, drops the set,
  and returns the button and pill to "♡ Save" / "SAVE" dim;
  removing the card being read from a two-item Reading List steps
  to the card that slid into its place and rebuilds the wall;
  removing the last item falls back to All cards on the same card;
  saving while browsing a collection re-points that set and the
  selector carries the new count; toggling with no current card is
  a no-op; call-site checks confirm drawCaption syncs the save UI,
  the flat Save button wires the toggle, the in-room row handles
  the save action, the SAVE pill sits in the control row and starts
  dim like RECORD, and the toggle guards no current card. Both
  vr.html script blocks also pass node --check with no syntax
  errors.

Live-verified on vrparlor.com after push: index.html and vr.html
both 200, live catalog 1,775. The served index.html carries the
view-toggle aria-pressed markup and the Home/End handler; the
served vr.html carries toggleSaveCurrent and syncSaveUI. A live
browser check of the flat Parlor (02:46–02:47 CST) confirmed the
room loads cleanly with no error: status "Browsing All cards.
Click a card on the wall to open it, or go back to the card.", the
wall showing 24 tiles (STA-0001–STA-0024, page 1 of 74), the
finding-aid cabinet on the left, and the flat control row fitting
on one line with "♡ SAVE" at the far right. In the 3D row the SAVE
pill reads between READ and EXIT while browsing (RECORD is hidden
in browse state, per round 8, so 7 pills show there and 8 while
reading).

What only a headset can judge: whether the eight-pill reading row
still feels uncrowded at arm's length, and whether SAVE reads
clearly beside RECORD. Those are Clay's call in the headset.

## Commits (one per change, each revertible on its own)

1. `9dc3337` — Gallery: view toggle buttons announce the active view
2. `817edb0` — Gallery: Home and End jump to the first and last result in the viewer
3. `c1cffd3` — Parlor: save the card being read to the Reading List

## Veto list

1. Gallery view toggle buttons announce the active view with aria-pressed.
2. Gallery viewer Home and End jump to the first and last result.
3. Parlor Save to Reading List: a Save toggle in the flat control row and a SAVE pill in the in-room row, writing the same list the gallery hearts build.
