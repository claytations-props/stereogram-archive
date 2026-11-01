# UI round 8 — navigation audit

Date: 2026-11-01

Scope: navigation and structure only. The round-7 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 1,369 items (round 7
was written at 1,322; the +47 came from wave 6, not from this round:
New York Harbor STA-1323–STA-1342 and Colorado STA-1343–STA-1369).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html (both last touched by round 7, 2026-10-30). The nightly
import had already landed (wave 6, STA-1323–STA-1369) before this
round started.

## Paths walked

Gallery: landing → shelf or collection → card → next card → back;
search → result → card → back to the same results; register view;
Reading List; empty state; viewer modes and keyboard paths.

VR Parlor: enter → shelves → set → reading → switch set → exit;
the flat control row in both states; the headset landing.

## Gallery friction found

1. The viewer is a modal dialog, but Tab walked out of it into the
   background page. A keyboard visitor tabbing past the viewer's last
   control landed on the toolbar and grid behind the overlay, and
   Shift+Tab from its first control landed on the footer behind it,
   even though the dialog carries role="dialog" and aria-modal.
   Round 7 made the page's tiles and rows keyboard reachable; the
   viewer itself still leaked focus.

## Gallery changes shipped

1. Tab cycles within the viewer. Tab from the viewer's last control
   returns to its first, Shift+Tab from its first returns to its
   last, and the rest of the viewer tab order is untouched. The
   check runs before the existing input early-return, so the wiggle
   speed slider tabs along with the rest of the viewer instead of
   being skipped. Arrow stepping, Escape, and the input guard for
   the search and sort controls are unchanged.

## Parlor friction found

1. The flat "Catalogue card" toggle flipped its label while
   browsing, but no card appeared. The record group stays hidden in
   browse state and the in-room record button is hidden there too,
   so the tap's only visible result was a label claiming "on" while
   nothing was on — the same class of fault rounds 4, 6, and 7
   fixed for the flat buttons in browse and for "Request an item"
   on empty results.
2. While browsing, the flat page carried no wall-page position in
   text. The page lives only in the 3D wall header, so a flat
   visitor paging the wall could not read which page they were on
   from the flat controls — the counts-missing-where-a-choice-is-
   made fault. The crumb line (the persistent location label from
   round 3) named only the selected card.

## Parlor changes shipped

1. The flat "Catalogue card" toggle is disabled while browsing, in
   updateHtmlButtons, which setState already calls on every state
   switch including boot. The existing dimmed disabled style
   (already in vr.html) reads the state. The toggle re-enables on
   return to reading, and the record on/off state itself is
   untouched, so a record left on still shows when reading resumes.
2. The flat crumb line names the wall page while browsing, e.g.
   "Current set · All cards · Card 5 of 1369 · Wall page 3 of 58".
   One shared crumbText function serves both call sites: drawCaption
   (card changes) and renderWall (wall paging changes no card, so
   drawCaption does not run there). In reading state the crumb is
   byte-for-byte what it was.

## Deliberately not changed

- Viewer stepping still wraps from the last result to the first,
  and the ten-card jumps wrap the same way; the position line
  ("Result 1361 of 1369") already says where the jump landed
  (held from round 4).
- "Clear search & filters" still does not reset the sort, in the
  toolbar or in the empty state. Sort is not a filter (held from
  round 4).
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
  different number depending on the path taken to it.
- The viewer Escape key still does not close the viewer from inside
  the wiggle speed slider (the input early-return). Untouched; the
  Tab trap deliberately runs before that guard, Escape does not.
- The in-room 3D paging buttons are unchanged: the wall header
  already names the page beside them, so their ends are visible.
  Keyboard wall paging at the ends still clamps silently; there is
  no visual affordance to fix for keys (held from round 7).
- Pre-arming the record from browse is gone as a side effect of
  change 1: the flat toggle no longer flips there. The in-room
  record button was already hidden while browsing, so the flat row
  now matches it; the record state itself still carries across
  the browse-to-reading switch.
- No visual restyle was made. New behavior reuses the existing
  buttons, brass accent, squared corners, and type.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in round 7), so the round-8 harness runs the real
index.html in jsdom instead, with a fetch stub serving the repo's
browse.json, data.json, search chunks, and per-item records from
disk (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round8-jsdom.cjs;
the Chrome harness is unchanged from round 7):

- 30 checks, 0 failures: full catalog renders (1369 of 1369, 48
  cards on the first page); era options read exactly 1369 / 641 /
  352 / 108 / 268; "Show more" reads "Show more items · 1321
  remaining" (round 5 holds); search narrows (Niagara → 23) and the
  empty state shows its clear button with "Request an item" disabled
  (rounds 5 and 6 hold); empty-state clear restores the catalog;
  count line reads "Sorted: Oldest first" for the old-first sort
  (round 4 holds); viewer opens with "Result 1 of 1369 · All items",
  jump forward lands on "Result 11 of 1369", Shift+ArrowRight on
  "Result 21 of 1369", jump back returns through 11 to 1, jump back
  from the first wraps to "Result 1360 of 1369", and the viewer
  closes back to the results; Research Notes carries target _blank
  and rel noopener (round 7 holds); shelf tiles and Finding Aid rows
  carry tabindex 0 and button role (round 7 holds); Tab from the
  viewer's last control wraps to its first (vFav) and Shift+Tab from
  its first wraps to its last (vFull), and ArrowRight still steps
  to "Result 1361 of 1369" after the trap checks; Enter on a shelf
  tile opens "Result 1369 of 1369 · All items"; register rows carry
  tabindex 0 and Enter on one opens "Result 1 of 1369 · All items".

Parlor: the full vr.html needs CDN three.js, which this headless
Chrome cannot reach, so the shipped functions were verified at the
logic level instead (as in round 7): updateHtmlButtons and crumbText
were extracted from vr.html (not copied) and executed against
stubbed state (ui-round8-parlor-check.mjs), 11 checks, 0 failures —
browse disables the Record toggle and retargets the Browse button,
reading re-enables it, browse crumb reads "Current set · All cards
· Card 5 of 1369 · Wall page 3 of 58", reading crumb has no wall
page, last wall page reads "Wall page 58 of 58", single-page set
reads "Wall page 1 of 1", and the renderWall crumb refresh, the
drawCaption crumbText use, and the setState updateHtmlButtons call
are all present in the shipped file. Both edited scripts also pass
node --check with no syntax errors.

Live-verified on vrparlor.com after push: index.html and vr.html
both 200, served bytes identical to the repo (identical on the
second check, after the Pages deploy caught up with the push), the
viewer Tab-trap code present in the served index.html, and the
updateHtmlButtons Record-disable plus crumbText code present in the
served vr.html.

## Commits (one per change, each revertible on its own)

1. `0b20fa5` — Parlor: flat Catalogue card toggle disabled while
   browsing
2. `39c6b43` — Parlor: flat crumb names the wall page while browsing
3. `406e59d` — Gallery: viewer Tab cycles within the dialog

## Veto list

1. Parlor flat Catalogue card toggle disabled while browsing.
2. Parlor flat crumb names the wall page while browsing.
3. Gallery viewer Tab cycles within the dialog.
