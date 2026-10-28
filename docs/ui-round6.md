# UI round 6 — navigation audit

Date: 2026-10-28

Scope: navigation and structure only. The round-5 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 1,295 items (round 5
was written at 1,264; the +31 came from wave 6, not from this round).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html (index.html last touched by round 5, vr.html by round 4).
The nightly import had already landed (wave 6, STA-1265–STA-1295)
before this round started.

## Paths walked

Gallery: landing → shelf or collection → card → next card → back;
search → result → card → back to the same results.

VR Parlor: enter → shelves → set → reading → switch set → exit;
the flat control row in both states.

## Gallery friction found

1. The viewer was the one place still stepping one card at a time.
   The Parlor got ten-card jump buttons in round 4, but the gallery
   viewer kept only ‹ › and the arrow keys, so walking a long
   result list (up to all 1,295 cards) meant one tap per card.
2. "Request an item" on an empty result list silently did nothing.
   The button stays live in the toolbar while the empty state below
   says nothing matches, so a tap on it is a dead end with no
   visible result — the same class of fault round 4 fixed for the
   flat Parlor buttons in browse state.

## Gallery changes shipped

1. The viewer header gains « 10 and 10 » jump buttons beside Save
   and Back to results. They step ten cards through the current
   result list, wrapping exactly like the existing single steps, and
   Shift+ArrowLeft / Shift+ArrowRight do the same from the keyboard.
   The buttons sit in the sticky header rather than on the image so
   they never cover the pair on a phone.
2. "Request an item" is disabled while the filtered list is empty
   and re-enabled as soon as results exist, with a dimmed disabled
   style so the state reads. Its click handler already ignored an
   empty list; now the button says so instead of silently nothing.

## Parlor friction found

None that cleared the bar. The flat set selector already carries
counts, the wall header already names the wall page in the flat view
as well as in the room, the flat controls already follow state and
already have jump buttons (round 4), the browse button already
retargets its label ("Back to the card" while browsing), and the
flat card panel already links back to the gallery on the open card
(`index.html#STA-####`). No Parlor change shipped this round;
vr.html is untouched.

## Deliberately not changed

- Viewer stepping still wraps from the last result to the first,
  and the ten-card jumps wrap the same way; the position line
  ("Result 1286 of 1295") already says where the jump landed
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
  the record permalink scheme is untouched.
- No visual restyle was made. New controls reuse the existing
  buttons, brass accent, squared corners, and type.

## Verification

Headless harness (the real gallery page in headless Chrome over
file URLs, full 1,295-card catalog; the Parlor check is the
unchanged-file case below, as vr.html is untouched this round):

- 21 checks, 0 failures: full catalog renders (1295 of 1295, 48
  cards on the first page); era options read exactly 1295 / 604 /
  315 / 108 / 268; "Show more" reads "Show more items · 1247
  remaining" (round 5 holds); search narrows (Niagara → 23) and
  the empty state shows its clear button (round 5 holds); on empty
  results "Request an item" is disabled, and the empty-state clear
  restores the catalog with the button enabled again; count line
  reads "Sorted: Oldest first" for the old-first sort (round 4
  holds); viewer opens with "Result 1 of 1295 · All items", jump
  forward lands on "Result 11 of 1295", Shift+ArrowRight on
  "Result 21 of 1295", jump back returns through 11 to 1, jump back
  from the first wraps to "Result 1286 of 1295", and the viewer
  closes back to the results.
- Parlor: vr.html byte-identical to its round-4 state (no commit
  this round touches it), so its round-4/5 verification still
  stands; the live check below confirms the served copy is the
  same file.

## Commits (one per change, each revertible on its own)

1. `1a84576` — Gallery: viewer jump buttons step ten cards,
   Shift+arrow does the same
2. `f02f627` — Gallery: disable Request an item while the result
   list is empty

## Veto list

1. Gallery viewer jump buttons step ten cards, Shift+arrow does the same.
2. Gallery Request an item disabled while the result list is empty.
