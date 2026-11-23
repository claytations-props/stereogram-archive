# UI round 18 — the search box you can still see, and a way back up

Date: 2026-11-23

Scope: navigation and structure only. The round-17 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 3,613 items (repo
browse.json; the live site agrees — the wave19 imports landed during
the round, so the count moved from 3,604 at the round's start).

Tree check first: at the round's start the wave19 nightly import was
mid-run — phase 3 for rockport had committed minutes earlier and the
paced IA upload was still running in the assets directory — but the
tree was clean apart from the old untracked IA upload log, and the
import touches records/ and the Archive only, never index.html or
vr.html. Two more import commits landed during the round (tagging
provincetown and nantucket, then phase 3 for lexington); each was
pulled in with --rebase before the push and none touched the UI
files.

## Paths walked

Live browser walk of vrparlor.com (03:42–03:49 EST, ~1920px viewport)
plus source audit: gallery landing → shelf/collection → card → next
card → back; search → result → card → back to the same results;
Show more and the long grid; view switches; the How to view button;
Parlor flat page load, wall, control row, Find search, set switching.
The headset landing and in-room row were not walked live this round
(round 11 covered them).

## Gallery friction found

- A search scrolled the count line into view but the search box
  scrolled off screen with it. Typing "Niagara" left "SHOWING 23 OF
  3593 ITEMS · SEARCH: "NIAGARA"" at the very top edge of the
  viewport, while the search box and the "CLEAR SEARCH & FILTERS"
  button sat above it, out of sight — so the typed query could not
  be seen, edited, or cleared without scrolling back up. The round-15
  reveal landed the count line 16px below the top of the screen, and
  the round-16 toolbar change (it scrolls away with the page now)
  left nothing above the count line on screen. The two changes
  interacted: the reveal's target assumed a sticky toolbar that no
  longer exists.
- There was no way back to the top. After Show more a few times the
  visitor is hundreds of cards down the page with only grid cards in
  view — the toolbar is not sticky since round 16 — and the only way
  back to the search and sort controls was scrolling manually all
  the way up. No back-to-top control existed anywhere on the page.
- Switching views reset the Show-more expansion. Shelves, Register,
  and Timeline show the same list in different presentations, but
  every view switch reset `shown` to 48 cards: a visitor who had
  opened 144 cards lost their place on each switch, and the remaining
  count jumped back to 3545.
- "How to view" landed at the bottom of the page. The button toggles
  the How to see the 3D box, but the box lived below the grid, so
  opening it scrolled the visitor past the whole grid to the footer
  section, far from the toolbar they had just tapped.

## Parlor friction found

- The finding-aid cabinet truncated its own longest names. The
  cabinet's set labels were cut at 300px, so the rows read "Robert N.
  Dennis Collect…", "International Stereoscopi…", "Keystone View
  Compan…", "The Metropolitan Museu…" — the collection a visitor
  most needs to recognize is the one they cannot read.

## Walk observations that are not defects

- The gallery showed 3,593 items while the Parlor showed 3,604:
  the walk ran minutes after the wave19-rockport commit, and the
  served browse.json was one batch behind the served vr.json — the
  known GitHub Pages lag (rounds 15 and 17), not a data divergence.
  Both agree at 3,613 now.
- Featured shelf tiles step through the whole catalog, not the
  twelve tiles: clicking STA-0001 opens "Result 1 of 3613 · All
  items" and Next steps to STA-0002. That is the standing design
  (round 15: shelf cards open into the full catalog).
- Set switching in the Parlor "always resets to Card 1": the walk
  read STA-0006 as a Falls & Rivers card, but STA-0006 is the Grand
  Canyon — Mountains & Canyons, not Falls & Rivers — so resetting to
  Card 1 was correct. selectSet already keeps the current card when
  it belongs to the new set; verified in code and against the data.
- The flat Prev/« buttons read disabled in wall view at Card 6:
  in browse they page the wall, and Card 6 sits on wall page 1,
  which has no previous page. That is the round-7 design, not a bug.
- The viewer briefly shows the previous card's image on a step:
  the old image fades out over 250ms while the new one loads
  (round 11 design).
- The Timeline's 1820s band shows two cards per row because the band
  holds two items, not because the layout wastes width.
- "VR NOT SUPPORTED" reads as a button: three.js's own disabled
  button state (round 15 holds).
- Wall tiles briefly show as black rectangles while they load:
  network loading (round 15 holds).

## Gallery changes shipped

1. Search, filter, and view actions reveal the toolbar, not the
   count line. maybeReveal now lands the toolbar's own top at the
   top of the screen, so the query, the filters, and the count line
   are all in view with the results below them — instead of the
   count line sitting at the top edge with the search box scrolled
   off screen above it. The reveal still fires exactly once per
   action, and only for actions that change what the list holds.
2. A back-to-top button. "↑ Top" rides the bottom-right corner once
   the page is scrolled past the toolbar (800px), and smooth-scrolls
   back to the top. It is a plain button in the squared chrome, it
   sits below the viewer in z-order so it never shows over a card,
   and it hides again at the top.
3. View switches keep the Show-more expansion. The expansion resets
   only when the list itself changes (search, filter, sort,
   collection); switching between Shelves, Register, and Timeline
   keeps how much of the list is shown. A search or a filter still
   resets it to 48.
4. The How to view box lives under the toolbar now, so opening it
   shows it where the visitor is — directly below the controls they
   just tapped — instead of scrolling them to the bottom of the page.
   The box itself, and the toggle, are unchanged.

## Parlor changes shipped

5. The finding-aid cabinet labels get room and shrink before they
   shorten. The label budget goes from 300px to 390px — the count is
   a short number right-aligned at 484, so the room is there — and a
   long label steps its size down (29 to 25) before it ever
   shortens, the way the caption plaque already does. "Robert N.
   Dennis Collection" and "Keystone View Company" now read in full;
   "The Metropolitan Museum of Art" reads in full one size down;
   the longest name still shortens, but shows far more of itself.

## Deliberately not changed

- The round-15 deliberately-not-changed list still stands in full,
  except where this round supersedes one line: the reveal's offset
  (round 15 change 1, as amended by round 16) now targets the
  toolbar top — the old count-line target is replaced by change 1
  above, not kept alongside it.
- No bigger change was needed: the audit found small clear wins, so
  the Nov 1 bigger-change latitude was not invoked. A Places view
  was considered and rejected again: places are free text with
  near-duplicate variants, so a list would show the same place
  three times unless the catalog data were normalized, which bigger
  changes never touch.
- The Timeline mis-grouping the walk flagged — STA-2489, "An
  allegorical painting, by Conkey, G. W. (George W.), 1837-ca.
  1900", filed under "1830s" although its year is "c. 1885" — is a
  catalog-data issue, not a UI one: its sort year (sy=1837) was
  taken from the creator's birth year in the title, not the
  photograph's date. A scan of the whole catalog finds only three
  cards whose sort year sits more than 30 years from the year in
  their year field, and the other two are a 1900 placeholder for an
  uncertain date (STA-0006) and a vague "1800s" (STA-0020). The one
  wrong sort year belongs to the import pipeline, and UI rounds
  never touch catalog data — so it is recorded here, not fixed here.
- "Surprise me" still labels nothing in the viewer: the visitor
  clicked Surprise me, and the position line says where they landed
  ("Result 1480 of 3613 · All items"). The randomness is the tap
  itself, not something the viewer needs to announce.
- The Featured shelf's › arrow still overlaps the seventh tile at
  desktop width: the edge buttons ride the shelf by design (round
  14), and the tile is reachable by scrolling.
- The Timeline sort control still shows its stale value while
  disabled, with no explanation that date order is forced (round 15
  holds: the count line already names the order).
- Register rows still carry no open affordance beyond hover
  highlight and their button role (round 15 holds).

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–17), so the round-18 harness runs the
real index.html in jsdom with a fetch stub serving the repo's
browse.json, data.json, search chunks, and per-item records from
disk, and an Image stub that fires onload (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round18-jsdom.cjs).
Expectations are computed from the repo's own browse.json, so a
catalog import between rounds does not stale them. scrollTo and
getBoundingClientRect are stubbed in the harness: the toolbar sits at
top 500 and the count line at 700, so a reveal aimed at the toolbar
reads 484 and one aimed at the count line reads 684.

- 83 checks, 0 failures: the round-17 suite still holds in full
  (full catalog renders, newest-first default, full-screen focus
  mode, viewer keyboard paths, Featured shelf, search narrowing);
  the round-18 checks hold: Show more expands the grid to 96 cards
  and Register, Timeline, and Shelves all keep the 96 on a view
  switch, while a search narrows to its 23 matches and clearing it
  resets the expansion to 48; a typed search fires exactly one
  reveal and it lands on the toolbar (top 484), not the count line
  (684); the back-to-top button exists with its label, is hidden at
  the top, is fixed below the viewer in z-order, is wired to the
  scroll position, appears once scrolled down, scrolls to the top
  on a tap, and hides again at the top; the How to view box sits
  directly under the toolbar, starts hidden, opens there, and
  closes again. The edited script passes node --check.

Headless harness, Parlor: the full vr.html needs CDN three.js, so
the shipped functions are extracted from vr.html (not copied) and
executed against stubbed state (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round18-parlor-check.mjs,
which supersedes the round-17 Parlor harness). drawSetPanel runs in
its own eval against a stubbed 2d context whose measureText models
Georgia at ~0.48em a character, ~0.52em bold.

- 120 checks, 0 failures: the round-17 suite still holds in full
  (search, save, keyboard, wall jump); the round-18 checks hold:
  the cabinet draws "Robert N. Dennis Collection" in full at 29px
  when not current, "Keystone View Company" in full, "The
  Metropolitan Museum of Art" in full one size down (27px), the
  longest label still shortens but shows far more than the old
  budget allowed, the old 300px cut is gone from the painter, the
  painter budgets 390px and shrinks before shortening, and Dennis
  still reads in full as the bold current set (27px). The vr.html
  module script passes node --check.

Live verification: after push, curl confirmed the new code served
(index.html carries the toolbar reveal, the top button and its
wiring, lastListSig, and the How to view box under the toolbar;
vr.html carries the 390px budget; browse.json serves 3,613 items;
both pages 200). A live browser walk (04:05–04:07 EST, ?v=18)
then confirmed all five changes: typing "Niagara" left the search
box with "Niagara" in it, the "CLEAR SEARCH & FILTERS" button, and
"SHOWING 23 OF 3613 ITEMS · SEARCH: "NIAGARA"" all visible in one
viewport, with the toolbar at the top and the count line below the
Finding Aid; after two Show-more clicks the grid showed 144 cards
("SHOW MORE ITEMS · 3469 REMAINING"), a "↑ TOP" button appeared in
the bottom-right corner, and tapping it returned the page to the
top with the button gone again; Register, Timeline, and Shelves
each kept the 144-card expansion (3469 remaining in every view);
"HOW TO VIEW" opened the "How to see the 3D" box directly under
the toolbar, above the Finding Aid; and the Parlor cabinet read
"Robert N. Dennis Collection" (1984), "International Stereoscopic
View Co." (1), and "Keystone View Company" (58) in full, with no
"…" truncation — the longest name reads in full live, where the
harness model only promised it would show far more. No console
errors were observed on either page (none observed in the page
views; no console panel is exposed in the walk browser).

What only a headset can judge: whether the in-room control row still
reads clearly in VR now that it shows only inside a session, and
whether the eight-pill reading row still feels uncrowded at arm's
length (held from round 10). Those are Clay's call in the headset.

## Commits (one per change, each revertible on its own)

1. `642a8b34` — Gallery: reveal lands on the toolbar, so the search box stays in view
2. `cea6e0dd` — Gallery: back-to-top button after scrolling past the toolbar
3. `18b400d9` — Gallery: view switches keep the Show-more expansion
4. `b7ac7c9c` — Gallery: How to view box moves under the toolbar
5. `c7dc1d85` — Parlor: cabinet labels get room and shrink before they shorten

## Veto list

1. Gallery reveal: after a search, filter, or view switch the page
   now scrolls so the toolbar (search box, filters, Clear button)
   sits at the top of the screen with the results below it, instead
   of the count line sitting at the very top edge with the search
   box scrolled off screen.
2. Gallery back-to-top: a small "↑ Top" button now appears in the
   bottom-right corner once the page is scrolled past the toolbar,
   and returns to the top on a tap, instead of there being no way
   back to the search and sort controls except scrolling manually.
3. Gallery view switches: switching between Shelves, Register, and
   Timeline now keeps how many cards are shown (Show-more
   expansion), instead of resetting to 48 cards on every switch;
   a search or a filter still resets it to 48.
4. Gallery How to view: the "How to see the 3D" box now opens
   directly under the toolbar, instead of below the grid at the
   bottom of the page.
5. Parlor finding aid: the cabinet's set labels now read in full
   where they fit ("Robert N. Dennis Collection", "Keystone View
   Company"), shrinking a size before shortening, instead of being
   cut off with "…" at 300px.
