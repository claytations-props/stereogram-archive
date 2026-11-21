# UI round 17 — keyboard shortcuts you can find, and one shelf too many

Date: 2026-11-21

Scope: navigation and structure only. The round-16 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 3,434 items (repo
browse.json; the live site showed 3,346 at the walk below because the
wave17 imports through STA-3439 had committed minutes earlier and
GitHub Pages had not served them yet).

Tree check first: at the round's start the wave17 phase-3 build was
mid-run — a `git pull --rebase` failed once on its unstaged writes —
so the round waited until it landed (119cd603, wave17-wheeling
STA-3426–STA-3439) and the tree was clean again before any edit. The
only untracked file is an old IA upload log, which no change touches.
The paced IA uploader running during the round works in the assets
directory only, never index.html or vr.html.

## Paths walked

Live browser walk of vrparlor.com (02:42–02:45 CST, ~1920px viewport)
plus source audit: gallery landing → shelf/collection → card → next
card → back; search → result → card → back to the same results;
viewer keyboard paths including the wiggle slider; Parlor flat page
load, wall paging, keyboard stepping, Find search. The headset
landing and in-room row were not walked live this round (round 11
covered them).

## Gallery friction found

- Escape and F were dead with focus in the wiggle speed slider.
  The viewer keydown handler checked them after the input
  early-return, and the slider is the one input inside the viewer.
  Confirmed live: two Escapes and an F press with the slider focused
  left the viewer open in its normal layout.
- The viewer has keyboard shortcuts no button names — arrows step,
  Shift+arrows jump ten, Home/End go to the ends, F toggles full
  screen — and nothing on screen said so. A full-page text search
  in the live walk found no mention of keyboard, arrow keys, Home/End,
  Esc, F, or shortcuts anywhere in the viewer. Round 15 deferred
  this as discoverability polish for a later round; this is that
  round.
- The Recent Accessions shelf showed the same ten cards the grid
  opens with, in the same order. Since round 16 the grid opens on
  the newest additions, the shelf's original purpose — surfacing new
  cards when the grid opened oldest-first — is gone. Confirmed live:
  shelf STA-3351 through STA-3342, identical to the grid's first ten
  (the live site was still serving the pre-wave17 catalog at the
  walk, so the ids are the then-newest ten).

## Parlor friction found

- The flat Parlor keyboard had no ten-card jump. Shift+ArrowRight
  while browsing advanced the wall one page, exactly like plain
  ArrowRight, and while reading it stepped one card; Home/End did
  nothing. The gallery viewer jumps ten with Shift+arrows and to the
  ends with Home/End, and the flat row's own double arrows do the
  same. Confirmed live in browse state; the reading state follows
  from the same handler in source.

## Walk observations that are not defects

- The Parlor opened mid-collection at STA-2080: the saved-state
  restore, by design (round 15 holds).
- After a Parlor search, the caption plaque still showed the previous
  card while the crumb already read the search set: the plaque waits
  on the new card's texture load, the crumb is set synchronously by
  renderWall. Texture-load timing, not a stale caption.
- Prev/Next and the double arrows read disabled in a one-page search
  set: the round-7 design (in browse the flat buttons page the wall,
  and a 23-card search set has one wall page).

## Gallery changes shipped

1. Escape and F work from inside the wiggle speed slider. Both keys
   now run before the input early-return in the viewer keydown
   handler, like Tab already did since round 8. The arrows, Home,
   and End stay behind the guard, so the slider keeps its own arrow
   keys.
2. The viewer names its keyboard shortcuts. One dim line under the
   mode hint reads "Arrow keys step · Shift + Arrow jumps 10 ·
   Home / End first / last · F full screen · Esc close". It sits in
   the viewer header, so it hides with the header in full-screen
   mode, and it hides on phones with the mode hint.
3. The Recent Accessions shelf is gone. The grid opens on the newest
   additions since round 16, so the shelf duplicated the grid's first
   page exactly. The Featured shelf stays as the curated strip, the
   Parlor keeps its own Recent Accessions set, and a note where the
   section was says why it was removed. The shared shelf styles and
   edge-button rules stay for the Featured shelf.

## Parlor changes shipped

4. The flat Parlor keyboard matches the gallery viewer and its own
   double-arrow buttons: Shift+arrows jump ten cards while reading
   (first/last wall page while browsing) and Home/End go to the
   first/last card (first/last wall page while browsing). The
   handler is named parlorKey so the harness can extract and test it;
   typing in the search box still steps nothing.

## Deliberately not changed

- The round-15 deliberately-not-changed list still stands in full.
- No bigger change was needed: the audit found small clear wins, so
  the Nov 1 bigger-change latitude was not invoked. A Places view
  was considered and rejected again: places are free text with
  near-duplicate variants, so a list would show the same place
  three times unless the catalog data were normalized, which bigger
  changes never touch.
- The round-16 open thread about the landing page feeling crowded
  on a phone is partly answered by change 3: the landing loses one
  shelf and the duplicated ten cards. The hero, finding aid, and
  Featured shelf were not collapsed further.
- The viewer Escape key now closes from the wiggle slider, but the
  arrows, Home, and End still do not fire from inside it — that is
  the guard doing its job, so the slider keeps its own keys.
- The keyboard hint line is not a button and is not in the Tab
  order: it names keys, it does not need focus.
- The Parlor thumbstick still steps one card (or one wall page):
  only the keyboard gained the ten-card jump, matching the gallery
  viewer's Shift+arrows and the flat row's double arrows.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–16), so the round-17 harness runs the
real index.html in jsdom with a fetch stub serving the repo's
browse.json, data.json, search chunks, and per-item records from
disk, and an Image stub that fires onload (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round17-jsdom.cjs).
The round-15 harness's shelf checks are retired here, not re-run:
the shelf they tested is gone by design, and the round-14
edge-button checks are ported to the Featured shelf, which now
carries that behavior. Expectations are computed from the repo's own
browse.json, so a catalog import between rounds does not stale them:

- 63 checks, 0 failures: full catalog renders (3434 of 3434, 48
  cards on the first page); the default sort is newest to the
  collection with STA-3439 first, switching to accession order
  starts at STA-0001 with "Sorted: Accession order" and no doubled
  prefix, and switching back restores STA-3439 first (round 16
  holds); full-screen focus mode still works by button, picture tap,
  and F key, Escape leaves full screen first and closes on a second
  press, and full screen survives stepping (round 16 holds); the
  Featured shelf renders 12 tiles from STA-0001 to STA-0027 with its
  edge buttons, and a tile opens El Capitan in the viewer (round 16
  holds); search still narrows (Niagara → 23) and the viewer jump
  still lands on "Result 11 of 3434" (round 15 holds); the Recent
  Accessions shelf, its buttons, and its builder are all gone with
  a removal note where the section was, and the grid's first ten are
  the newest ten (STA-3439–STA-3430); the Featured edge buttons
  read disabled at each end, step one tile (±170), and both read
  disabled when nothing overflows (round 14 holds); the keyboard
  hint line exists in the viewer header naming all five shortcuts,
  styled dim and centred, hidden on phones; Escape on the wiggle
  slider closes the viewer, F on the slider toggles full screen both
  ways, Escape on the slider leaves full screen first and closes on
  a second press, and ArrowRight on the slider does not step the
  viewer. The edited script passes node --check.

Headless harness, Parlor: the full vr.html needs CDN three.js, so
the shipped functions are extracted from vr.html (not copied) and
executed against stubbed state (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round17-parlor-check.mjs,
which supersedes the round-15 Parlor harness):

- 105 checks, 0 failures: the round-11 search scenarios all still
  hold, the round-10 save scenarios all still hold through
  rebuildSets, the round-12 Recent Accessions set still holds, the
  round-14 status refresh holds, the round-15 Enter VR wording and
  crumb checks hold, and the round-17 keyboard checks hold:
  reading ArrowRight/ArrowLeft step one card, Shift+arrows jump ten
  (navShow curPos±10), Home/End go to the first/last card, browse
  arrows page the wall one page, Shift+arrows jump to the first/last
  wall page, Home/End do the same, browse Escape returns to the
  card, and typing in an input steps nothing; the handler is the
  named parlorKey wired by addEventListener. The vr.html module
  script passes node --check.

Live verification: (to be filled after push)

What only a headset can judge: whether the in-room control row still
reads clearly in VR now that it shows only inside a session, and
whether the eight-pill reading row still feels uncrowded at arm's
length (held from round 10). Those are Clay's call in the headset.

## Commits (one per change, each revertible on its own)

1. `2cfb92d7` — Viewer: Escape and F work from inside the wiggle speed slider
2. `e5987490` — Viewer: keyboard shortcut hint line under the mode hint
3. `81da8f99` — Gallery: remove the Recent Accessions shelf, it duplicates the grid
4. `3c6f19f5` — Parlor: keyboard Shift+arrows jump ten, Home/End first/last

## Veto list

1. Viewer Escape and F: pressing Escape or F with focus in the
   wiggle speed slider now closes the viewer or toggles full screen,
   instead of doing nothing there.
2. Viewer keyboard hint: a line under the view-mode buttons now
   names the shortcuts (arrow keys step, Shift+Arrow jumps 10,
   Home/End first/last, F full screen, Esc close), instead of the
   viewer never saying what its keys do.
3. Recent Accessions shelf: the shelf above the grid is gone,
   instead of showing the same ten newest cards the grid opens with.
4. Parlor keyboard: Shift+arrows now jump ten cards while reading
   (first/last wall page while browsing) and Home/End go to the
   first/last card (first/last wall page while browsing), instead of
   Shift+arrows moving one card or one wall page and Home/End doing
   nothing.
