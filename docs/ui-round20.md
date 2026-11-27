# UI round 20 — sort labels that say what they sort, and a selector that agrees at once

Date: 2026-11-27

Scope: navigation and structure only. The round-19 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 4,044 items (repo
browse.json; the live site showed 3,944 at the audit walk — wave23's
100 items were committed but not yet pushed — and 4,044 at
verification once this round's push carried them).

Tree check first: at the round's start the wave23 nightly import had
finished committing (a46b26f8, 100 merged STA-3952–STA-4051, six
commits ahead of origin) and no import process was running, but its
export phase regenerated the IIIF/JSON-LD/finding-aid files at 02:55
CST, still uncommitted in the tree (exports/finding-aid.xml,
iiif/collection.json, tools/rect_dims.json, plus 100 new iiif/ and
ld/ files). The import touches records/, catalog JSON, and the
exports only, never index.html or vr.html (the round-19 precedent),
and my two files carried only my own changes — verified by hunk
before the split commits. The push carried the finished wave23
record commits along with the five UI commits, as round 19's push
did with wave21's. Nothing staged but my own files; the import's
uncommitted export files were left alone for its own job to commit.
Pull --rebase before push reported the unstaged import changes and
refused — there was nothing incoming to rebase (0 incoming, 11
outgoing), so the push went ahead on the fetched state.

## Paths walked

Live browser walk of vrparlor.com (02:41–02:48 CST, ~1920px viewport)
plus source audit: gallery landing → shelf/collection → card → step
→ back; search → result → card → back to the same results; Show
more and the view switches; the How to view button; Parlor flat page
load, wall paging, Find search (a match and a no-match), Random in
browse, keyboard stepping, set switching. The phone steps were not
executed live — the walk browser provides no way to resize to ~390px
— so the phone CSS rules stay covered by the harness regression
checks, as in earlier rounds.

## Gallery friction found

- The sort labels did not say what they sort. "Newest to the
  collection" (the newest additions to the archive) and "Newest
  first" (the newest photographs by date) read as the same choice,
  and the "Sort: " prefix appeared on one option only.
- Stepping to the next card while scrolled down to the record left
  the new picture above the viewport. The viewer keeps its scroll
  position across cards, and the record sits below the fold on
  opening, so a keyboard step from the record showed the new card's
  record, not its picture.
- A Register row opens its record on click or Enter, but nothing on
  the row said so. The walk concluded a record could "apparently
  only be opened by switching back to Shelves".
- "/" sat dead for a keyboard visitor tabbed onto the era or sort
  dropdown. The round-19 guard excluded selects, although a select
  takes no text — "/" matches no option — so the one place a
  keyboard visitor is most likely to be standing was the one place
  the key did nothing.

## Parlor friction found

- A search or a clear left the set selector disagreeing with the set
  shown. runParlorSearch built the selector from curSet before
  curSet became the search set, and clearParlorSearch built it while
  curSet still named the search set it had just removed — so the
  dropdown named the old set (or no set) until the next card's
  texture load refreshed it through drawCaption. The walk saw the
  dropdown's marked option disagree with the set actually showing.

## Walk observations that are not defects

- The count line reads "SHOWING 3944 OF 3944 ITEMS" while only 48
  cards are rendered: the count names the filtered total, and the
  Show more button names what remains (round 5/19 holds). The walk
  re-flagged it; the reading stands.
- The Featured shelf's › arrow overlaps the seventh tile at desktop
  width: the edge buttons ride the shelf by design (round 14), and
  the tile is reachable by scrolling. The shelf's titles are cut at
  the shelf edge by the same horizontal-strip design.
- The Finding Aid rows are buttons that filter the gallery, and the
  note under the panels says so ("Choose a line in the finding aid
  to pull just those items"); the nested "Browse in VR" link is the
  second target in the row, opening in a new tab (round 15).
- The series chip counts add up past the catalog total (4,306
  against 3,944 at the walk) because cards carry more than one
  series: membership, not a partition (round 15 holds).
- Show More expansion resets on a filter change or a clear: the
  round-18 design (the expansion resets when the list itself
  changes; only a view switch keeps it).
- The era dropdown counts stay catalog-wide while a search is
  active (round 15 holds: the dropdown is the catalog's shape, not
  the result's).
- The Timeline sort control shows its stale value while disabled,
  with no explanation that date order is forced (round 15 holds:
  the count line already names the order). The renamed labels change
  what the stale value reads ("Recently added"), not the behavior.
- The Parlor opening mid-set on a saved card and wall page is the
  saved-state restore, by design (round 15 holds).
- Paging the wall does not change the current card: the wall is a
  shelf to browse, and the caption keeps naming the selected card.
  The gold frame is absent from the new page because the selected
  card is not on it.
- The viewer briefly shows the previous card's image on a step: the
  old image fades out over 250ms while the new one loads (round 11
  design). Wall tiles and grid cards briefly show as black
  rectangles while they load: network loading (round 15 holds).
- The ✕ and ⛶ icons render as empty boxes in the walk browser: the
  browser's font rendering, not the page — every such button carries
  its action in words ("Back to results", "Full screen", "Clear the
  search").
- The walk read the Parlor's clear-search ✕ as doing nothing. The
  harness settles it: clearParlorSearch returns to All cards on the
  same card (round-11 design, re-verified this round), and the
  button carries aria-label "Clear the search". Not reproduced.
- A no-match Find keeps the failed text in the box while the set
  stays put: the box keeps the query so it can be corrected, and
  the status line names the set still showing (round 19). Not
  changed.
- The hero says "1840S — 1920S" while the Finding Aid span reads
  "1820–1928". The 1820 is the same birth-year-derived sort-year
  issue as STA-2489 (STA-0695's "c. 1820" is its creator's birth
  year, not the photograph's date; STA-0582's 1822 is the same), so
  the hero's range is the honest span and the discrepancy belongs
  to the import pipeline's date handling, not to a label. Not
  changed; see the data notes below.
- The Parlor's large scene heading briefly shows the previous card
  after a Find jump: the caption plaque repaints when the new card's
  texture lands, so the heading lags the jump while the set line and
  the caption already show the new card. The status line already
  names the card being loaded. Not changed here — moving the caption
  ahead of the texture load would touch the card-change flow and its
  projector-dip timing, so it is a candidate for a later round, not
  a fifth-minute add-on.

## Gallery changes shipped

1. The sort options name what they sort. "Newest to the collection"
   is "Recently added", "Sort: Accession order" is "Accession order",
   "Oldest first" is "Oldest photographs first", and "Newest first"
   is "Newest photographs first". The count line follows ("Sorted:
   Oldest photographs first"), and the "Sort: " strip in the count
   code is now a no-op guard.
2. Viewer steps return to the picture. A card change brings the
   viewer back to the top, where the picture is, instead of leaving
   the new picture above the viewport when the visitor had scrolled
   down to the record. Mode switches do not call showCurrent, so
   they never scroll.
3. Register rows gain an open affordance. A "›" in a final column
   marks the row as openable, and the row carries its action as its
   title ("Open the record"). The walk browser showed no tooltip
   bubble for the title, so the "›" is the visible cue and the title
   is the assistive-tech name. No role="button" on the row: that
   would override the table row's own semantics; the cue and the
   title are the affordance. This supersedes the round-15 hold
   ("Register rows keep no open affordance beyond hover highlight
   and their button role") — the hold's premise was partly wrong
   (the code never set a button role), and the round-20 walk showed
   a visitor concluding records could only be opened from Shelves.
4. "/" reaches the search box from the era/sort dropdowns too. The
   round-19 guard excluded selects; it covers inputs and textareas
   only now, since a select takes no text. Inside the viewer, or
   inside any input, "/" still types as itself. One limit, found on
   the verification walk: "/" works from a focused dropdown, but
   while the native option list is open the browser keeps the key
   and the page never sees it — a native-popup limitation, not
   something the page can override. Tabbing onto a dropdown leaves
   its list closed, so the keyboard path the change is for works.

## Parlor changes shipped

5. A search or a clear settles the set before the selector is built.
   runParlorSearch assigns curSet before buildSetOptions, and
   clearParlorSearch settles curSet on All cards before
   buildSetOptions, so the dropdown names the set shown at once
   instead of waiting for the next card's texture load to refresh
   it. The search and clear behavior is otherwise unchanged.

## Deliberately not changed

- The round-15/17/18/19 deliberately-not-changed lists still stand
  in full, except where this round supersedes one line: the Register
  rows now carry an open affordance (change 3 amends the round-15
  hold), and the "/" guard no longer excludes selects (change 4
  amends round 19's guard scope).
- No bigger change was needed: the audit found small clear wins, so
  the Nov 1 bigger-change latitude was not invoked. A Places view
  was considered and rejected again: places are free text with
  near-duplicate variants, so a list would show the same place
  three times unless the catalog data were normalized, which bigger
  changes never touch.
- A Timeline decade jump was considered and deferred: reaching the
  1900s means repeated Show More through the 341-item 1850s band,
  but a decade's band only exists in the DOM once Show More has
  expanded the list that far, so a jump would have to expand the
  list to reach its decade — a bigger change needing its own design,
  not a small win.
- A "/" shortcut for the Parlor Find box was considered and
  deferred: the Find box is Tab-reachable with its button beside
  it, and the set dropdown is the Parlor's primary navigation; the
  gallery's "/" was for the front-door search.
- No dismiss control for the Parlor intro panel: the status line
  lives there, and hiding it would hide search feedback.
- Random stays labeled "Random": the crumb names the set it draws
  from, a tooltip is too weak to count as a fix, and renaming it
  would crowd the control row.
- The depth words on cards (Gentle, Moderate, Deep) are still not
  explained on the page: the data dictionary defines depth only as
  derived from the measured range, with no published thresholds or
  plain-language meaning to quote, so no legend was invented.
- Data notes, recorded not fixed (catalog data, not UI): STA-2489
  under "1830s" with year "c. 1885" (round 18 holds — the sort year
  came from the creator's birth year); STA-0695 (sy 1820) and
  STA-0582 (sy 1822) are the same class, creator birth years taken
  as photograph dates; the accession gaps STA-3924 and STA-3920
  are held cards, not missing records.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–19), so the round-20 harness runs the
real index.html in jsdom with a fetch stub serving the repo's
browse.json, data.json, search chunks, and per-item records from
disk, and an Image stub that fires onload (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round20-jsdom.cjs).
Expectations are computed from the repo's own browse.json, so a
catalog import between rounds does not stale them.

- 103 checks, 0 failures: the round-17/18/19 suite still holds in
  full (full catalog renders, newest-first default, full-screen
  focus mode, viewer keyboard paths, Featured shelf, search
  narrowing, reveal on the toolbar, back-to-top, view switches
  keeping the Show-more expansion, How to view under the toolbar,
  "/" focusing the search box); the round-20 checks hold: the sort
  options read "Recently added · Accession order · Oldest
  photographs first · Newest photographs first · Title A–Z ·
  Shuffle", the count line names the photographs for Oldest- and
  Newest-first and carries no suffix on the default; stepping (button
  and keyboard) returns the viewer to the top while a mode switch
  leaves its scroll alone, and opening a card does the same; the
  Register shows 48 rows each carrying the "›" cue and the "Open the
  record" title with a seventh header cell, styled in the paper link
  colour, and a row click still opens its card; "/" focuses the
  search box from the era dropdown and from the sort dropdown. The
  edited script passes node --check. (The jsdom scrollIntoView
  TypeError in the harness output is the known jsdom limitation, as
  in round 19: the How to view toggle it follows still passes.)

Headless harness, Parlor: the full vr.html needs CDN three.js, so
the shipped functions are extracted from vr.html (not copied) and
executed against stubbed state (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round20-parlor-check.mjs,
which supersedes the round-19 Parlor harness).

- 140 checks, 0 failures: the round-17/18/19 suite still holds in
  full (search, save, keyboard, wall jump, cabinet labels, Random
  opening the random card, flat wall buttons); the round-20 checks
  hold: after a search the selector's value is the search set at
  once ("search:niagara"), after clearing it is All cards at once
  ("all"), and in both functions the set is settled before
  buildSetOptions runs (search: set at offset 1047, build at 1104;
  clear: set at 166, build at 567). The vr.html module script
  passes node --check.

Live verification: after push, curl confirmed the new code served
(both pages 200; index.html carries "Recently added" and no longer
"Newest to the collection"; vr.html carries the reordered search;
browse.json serves 4,044 items — GitHub Pages served the new deploy
at once this time, no lag as in round 19).

A live browser walk (03:00–03:04 CST) then confirmed the changes:
the Sort dropdown reads "Recently added", "Accession order",
"Oldest photographs first", "Newest photographs first", "Title
A–Z", "Shuffle", and picking "Oldest photographs first" reads
"SHOWING 4044 OF 4044 ITEMS · SORTED: OLDEST PHOTOGRAPHS FIRST"
with the grid reordered to STA-0695 first; opening STA-0695,
scrolling to its Catalogue Record, and pressing Right Arrow stepped
to STA-0582 with the new picture at the top and no scroll back up;
Register rows each end with a "›" under an empty header, carry
"Open the record" as their title, and a row click opens the viewer;
"/" from a focused Era dropdown lands the cursor in the search box,
but not while the native option list is open (see change 4); a
Parlor Find for "niagara" showed 'Search: "niagara" · 46' in the
SET dropdown at once with the marked option agreeing, and clearing
showed "All cards · 4044" at once with the search option gone; and
the regression spot-check held (a "niagara" search narrows to 46,
Show more 48 → 96). No console errors were observed on either page
(none observed in the page views; no console panel is exposed in
the walk browser).

What only a headset can judge: whether the in-room control row still
reads clearly in VR now that it shows only inside a session, and
whether the eight-pill reading row still feels uncrowded at arm's
length (held from round 10). Those are Clay's call in the headset.

## Commits (one per change, each revertible on its own)

1. `8a707be9` — Gallery: sort options name what they sort
2. `f6270fdd` — Gallery: viewer steps return to the picture
3. `e244e10b` — Gallery: Register rows gain an open affordance
4. `31107f87` — Gallery: "/" reaches the search box from the era/sort dropdowns
5. `ac7fdcd6` — Parlor: search and clear set the selector's value at once

## Veto list

1. Gallery sort: the options now read "Recently added", "Accession
   order", "Oldest photographs first", and "Newest photographs
   first", instead of "Newest to the collection", "Sort: Accession
   order", "Oldest first", and "Newest first".
2. Gallery viewer: stepping to another card now brings the viewer
   back to the top, where the picture is, instead of leaving the new
   picture above the viewport when the visitor had scrolled down to
   the record; switching view modes does not scroll.
3. Gallery Register: each row now ends with a "›" mark and carries
   "Open the record" as its title, instead of giving no sign that a
   row opens its record (no tooltip bubble appeared for the title in
   the walk browser, so the "›" is the visible cue).
4. Gallery search key: pressing "/" now focuses the search box from
   the era or sort dropdown too, instead of doing nothing there —
   except while the native option list is open, where the browser
   keeps the key; inside the viewer, or inside any input, "/" still
   types as itself.
5. Parlor set selector: after a Find, or after clearing a search,
   the dropdown now names the set shown at once, instead of naming
   the old set (or no set) until the next card loads.
