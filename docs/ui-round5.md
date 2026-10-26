# UI round 5 — navigation audit

Date: 2026-10-26

Scope: navigation and structure only. The round-4 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 1,264 items (round 4
was written at 1,218; the +46 came from wave 6, not from this round).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html (index.html last touched by the Oct 25 traffic commit,
vr.html by round 4). The nightly import had already landed (wave 6,
STA-1246–STA-1264) before this round started.

## Paths walked

Gallery: landing → shelf or collection → card → next card → back;
search → result → card → back to the same results.

VR Parlor: enter → shelves → set → reading → switch set → exit;
the flat Parlor controls.

## Gallery friction found

1. The result count line duplicated the era count. Round 4 put live
   counts into the era dropdown options, but the count line builds
   its "Era:" label from the option's text, so it read "Era:
   1840s–1860s · 604" — the size twice, once as label and once as
   count, and the count line is the one place that should name the
   context cleanly.
2. The empty state told the visitor to clear the search, but the
   only clear control sat up in the toolbar. A visitor who had
   scrolled down to the empty message had to scroll back up to act
   on it. Round 3 shipped the toolbar button; the message itself
   still had no control beside it.
3. "Show more items" gave no sense of how much was left. The count
   line at the top says "Showing 48 of 1264 items", but the button
   is the decision point, reached after scrolling past 48 cards,
   with the top count long out of sight.

## Gallery changes shipped

1. The count line uses the era option's base label, so it reads
   "Era: 1840s–1860s" with no trailing count.
2. The empty state carries its own "Clear search & filters" button,
   wired to the same reset as the toolbar button (search, era,
   collection, series; sort still not reset, per round 4). The
   Reading List empty state keeps no button: clearing there would
   abandon the list view instead of filling it.
3. The "Show more" button names what remains, e.g. "Show more items
   · 1216 remaining".

## Parlor friction found

None that cleared the bar. The flat set selector already carries
counts, the wall header already names the wall page ("Cards a–b of
N · Page X of Y") in the flat view as well as in the room, and the
flat controls already follow state (round 4). No Parlor change
shipped this round; vr.html is untouched.

## Deliberately not changed

- Viewer stepping still wraps from the last result to the first;
  the position line ("Result 1 of N") already says where the step
  landed (held from round 4).
- Finding Aid collection rows still do not toggle off on a second
  tap. The "All holdings" row and the Clear button already reset a
  collection (held from round 4).
- "Clear search & filters" still does not reset the sort, in the
  toolbar or in the empty state. Sort is not a filter (held from
  round 4).
- No way to add to the Reading List from inside the Parlor. That is
  a feature, not a navigation fix, and the gallery heart remains the
  one place a list is built (held from round 4).
- Recent Accessions shelf cards still open into the full catalog
  for stepping, not into the 10 recent items. Stepping inside just
  the 10 would trap the visitor there (wrap would return to the
  first recent item with no route onward except Back).
- Filter state was not moved into the gallery URL, and Browser Back
  was not rebound to close the viewer — both held from round 3, so
  the record permalink scheme is untouched.
- No visual restyle was made. New controls reuse the existing
  buttons, brass accent, squared corners, and type.

## Verification

Headless harness (the real gallery page in headless Chrome over
file URLs, full 1,264-card catalog; the Parlor check runs the same
vr.html with a local three.js in place of the CDN copy, as in round
4, because this headless Chrome has no proxy for unpkg):

- Baseline run before the fixes confirmed all three faults: count
  line "Era: 1840s–1860s · 604"; empty state with no clear button;
  "Show more items" with no remaining count.
- After the fixes, 13 gallery checks, 0 failures: full catalog
  renders (1264 of 1264); era options read exactly 1264 / 604 /
  313 / 98 / 249; count line after era=early reads "Showing 604 of
  1264 items · Era: 1840s–1860s"; search narrows (era + Niagara →
  8) and the empty state shows its clear button; clicking it
  restores q empty, era all, 1264 of 1264; viewer opens with
  "Result 1 of 1264 · All items", steps to "Result 2 of 1264", and
  closes; "Show more" reads "Show more items · 1216 remaining";
  round-3 chip counts intact.
- Parlor: 17 sets, "All cards · 1264" in the set selector, plain
  entry on the shelves path as in round 4. (A card texture fetch
  reports skipped in this headless run, as remote images do without
  a proxy; the set selector and counts are what this check covers,
  and vr.html is unchanged this round.)
- Live-verified on vrparlor.com after push: index.html and vr.html
  both 200, served bytes identical to the repo (identical on the
  third check, after the Pages deploy caught up with the push), the
  era-label fix, the empty-state button, and the remaining-count
  code present in the served index.html.

## Commits (one per change, each revertible on its own)

1. `310c95b` — Gallery: count line uses the era name without its
   dropdown count
2. `333f46f` — Gallery: empty state carries its own Clear search &
   filters button
3. `e02b3a0` — Gallery: Show more button names how many items remain

## Veto list

1. Gallery count line uses the era name without its dropdown count.
2. Gallery empty state carries its own Clear search and filters button.
3. Gallery Show more button names how many items remain.
