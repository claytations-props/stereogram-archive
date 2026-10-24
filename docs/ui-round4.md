# UI round 4 — navigation audit

Date: 2026-10-24

Scope: navigation and structure only. The round-3 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 1,218 items (round 3
was written at 1,190; the +28 came from wave 6, not from this round).

## Paths walked

Gallery: landing → shelf or collection → card → next card → back;
search → result → card → back to the same results.

VR Parlor: enter → shelves → set → reading → switch set → exit;
the flat control row in both states.

## Gallery friction found

1. The era dropdown was the one shelf choice still made blind. Series
   chips got counts in round 3 and the Finding Aid rows carry them,
   but the era options showed no size before a tap.
2. The result count did not name the sort. A shuffled or reordered
   list read exactly like accession order, so a visitor returning
   from a card could not tell which ordering they were stepping
   through.

## Gallery changes shipped

1. Era dropdown options now carry live counts (All eras · 1218,
   1840s–1860s · 578, 1870s–1890s · 296, 1900s–1920s · 96,
   Undated · 248).
2. The result count names the non-default sort: "Sorted: Oldest
   first" (and the other orderings), "Shuffled" for shuffle, and
   nothing for the default accession order.

## Parlor friction found

1. The flat Prev/Next buttons stepped cards even while browsing.
   The keyboard and the in-room row already page the wall in browse
   state, so the flat row contradicted both: a tap silently moved
   the selection off the visible wall with no visible result.
   Flat Random had the same fault in browse.
2. The flat row was the only control set without the double-arrow
   jump. Stepping a 1,218-card set one card at a time from the flat
   page was slow, and Random is not a directed move.

## Parlor changes shipped

1. Flat Prev/Next/Random follow the current state: in browse they
   work the wall (Prev/Next page it, Random selects a card and jumps
   the wall to that card's page); in reading they step cards as
   before.
2. Flat jump buttons (« ») join the row: ten cards at a time while
   reading, first/last wall page while browsing — the same behavior
   as the in-room row's double arrows.

## Deliberately not changed

- "Clear search & filters" still does not reset the sort. Sort is
  not a filter, and round 3 scoped that button to search, era,
  collection, and series.
- Finding Aid collection rows still do not toggle off on a second
  tap. The "All holdings" row and the Clear button already reset a
  collection, so this adds no new path.
- No way to add to the Reading List from inside the Parlor. That is
  a feature, not a navigation fix, and the gallery heart remains the
  one place a list is built.
- Viewer stepping still wraps from the last result to the first;
  the position line ("Result 1 of N") already says where the step
  landed.
- Filter state was not moved into the gallery URL, and Browser Back
  was not rebound to close the viewer — both held from round 3, so
  the record permalink scheme is untouched.
- No visual restyle was made. New controls reuse the existing dark
  panels, brass accent, squared corners, and type.

## Verification

Headless harness (the real pages in headless Chrome, local three.js,
stand-in textures, full 1,218-card catalog; run over file URLs
because this Chrome build blocks localhost navigation at the
network layer): 22 checks, 0 failures.

- Gallery: full catalog renders (1218 of 1218); search narrows
  (Niagara → 22) and clears back to 1218; viewer opens with
  "Result 1 of 1218", steps to "Result 2 of 1218", and returns to
  the same results; round-3 chip counts intact.
- Era counts read exactly 1218 / 578 / 296 / 96 / 248; the count
  line reads "Sorted: Oldest first", "Shuffled", and nothing for
  the default sort.
- Parlor: 17 sets, "All cards · 1218" in the set selector, plain
  entry lands on browse (round 3 holds).
- Baseline run confirmed the flat-browse fault before the fix
  (flat Next in browse: wall 0 → 0, card 0 → 1). After the fix:
  flat Next pages the wall with the card unchanged, flat Prev
  returns it, flat Random lands the wall on its card's page,
  flat jump-forward moves 10 cards in reading and back again,
  and flat jumps go to the last wall page (50) and back to the
  first (0) in browse.
- Live-verified on vrparlor.com after push: index.html and vr.html
  both 200, served bytes identical to the repo, flat jump button
  ids and the era-count code present in the served files.

## Commits (one per change, each revertible on its own)

1. `9aabf6d` — Parlor: flat Prev/Next/Random follow the current
   state (wall in browse, cards in reading)
2. `f350f67` — Parlor: flat jump buttons (ten cards in reading,
   first/last wall page in browse)
3. `e0c4a5c` — Gallery: era dropdown options carry live counts
4. `08274f8` — Gallery: result count names the non-default sort

## Veto list

1. Parlor flat Prev/Next/Random follow the current state.
2. Parlor flat jump buttons.
3. Gallery era dropdown options carry live counts.
4. Gallery result count names the non-default sort.
