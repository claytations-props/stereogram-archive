# UI round 19 — "/" finds the search box, and Random finally opens a card

Date: 2026-11-25

Scope: navigation and structure only. The round-18 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 3,833 items (repo
browse.json; the live site showed 3,727 at the audit walk because the
wave21 imports landed during the round, and 3,833 at verification once
GitHub Pages caught up).

Tree check first: at the round's start the wave21 nightly import was
mid-run — the scout had left docs/harvest-queue.md modified with four
remainder JSONs untracked, and merge_batch.py for
wave21-poughkeepsie-rem2 was running — but the import touches records/
and catalog JSON only, never index.html or vr.html (the round-18
precedent). By the time the edits were committed the wave21 run had
finished and committed (4b84cf70, 106 merged STA-3733–STA-3838) and
the tree was clean apart from my two files. Pull --rebase before push;
no conflicts, nothing staged but my own files.

## Paths walked

Live browser walk of vrparlor.com (03:42–03:53 EST, ~1920px viewport)
plus source audit: gallery landing → search → card → step → back;
Show more and the view switches; the How to view button; Parlor flat
page load, wall paging, Find search (a match and a no-match), Random
in browse, keyboard stepping, set switching. The phone steps were not
executed live — the walk browser provides no way to resize to ~390px
— so the phone CSS rules stay covered by the harness regression
checks, as in earlier rounds.

## Gallery friction found

- No key reached the search box. Nothing on screen named a key for
  it, and no key did it — the only slashes on the page were in
  ordinary words like "red/cyan". A keyboard visitor had to click or
  Tab to the search box; the viewer already names its own keys, the
  toolbar named none.

## Parlor friction found

- A no-match Find lied. The status line said 'No cards match
  "zzzqqq"' while the wall still showed the full first page of Falls
  & Rivers — the message and the wall disagreed, and the visitor was
  left reading "no cards match" above a wall full of cards.
- Random while browsing never opened a card. It paged the wall to the
  random card's page and changed the caption to a card the visitor
  could not see — the wall stayed in browsing mode, the status stayed
  "Browsing All cards…", and the only way to see the card was to find
  its tile and click it. The gallery's Surprise me opens the viewer on
  its pick; the Parlor's Random did half the job.
- The flat Parlor's keyboard shortcuts were unnamed. The only
  keyboard mention anywhere on the flat page was "arrow keys flip
  cards" — Shift+arrows jumping ten and Home/End going to the ends
  appeared nowhere, although the gallery viewer has named its own
  keys since round 17 and the flat row's own double arrows do the
  same jumps.

## Walk observations that are not defects

- The Parlor loaded on Falls & Rivers at the audit walk and on the
  Robert N. Dennis Collection (2,064 items) at the verification walk:
  the saved-state restore, by design (round 15 holds).
- Clearing a Parlor search returns to All cards, not the previous
  set: the round-11 design, round 15 holds. The audit walk re-flagged
  it; the behavior stands.
- The count line reads "SHOWING 3727 OF 3727 ITEMS" while only 48
  cards are rendered: the count names the filtered total, and the Show
  more button names what remains ("SHOW MORE ITEMS · 3679
  REMAINING"). That is the established reading since round 5; changing
  the first number to the rendered count would churn the count line's
  long-standing meaning for a marginal gain. Recorded, not changed.
- PREV/NEXT in the Parlor flat row: the audit walk read them as
  disabled while browsing Falls & Rivers. The harness settles it: on
  wall page 1 of a 32-page set only the spent direction (Prev) reads
  disabled and Next is live; both read disabled only on a one-page
  set (the Niagara search set the walk had just used), which is the
  round-7 design. Not a defect.
- The viewer briefly shows the previous card's image on a step: the
  old image fades out over 250ms while the new one loads (round 11
  design).
- The Featured shelf shows about 7 of its 12 tiles at 1920px: the
  edge buttons ride the shelf by design (round 14), and the rest are
  reachable by scrolling.

## Gallery changes shipped

1. "/" focuses the search box. Pressing "/" anywhere outside a text
   field puts the cursor in the search box, the way archives and mail
   apps do it; the box names the key in its hover title ("Press / to
   focus the search box"). Inside the viewer, or inside any input,
   "/" types as itself — the viewer stays open and the search box
   behind it is untouched.

## Parlor changes shipped

2. A no-match search names the set still showing. The status line now
   reads 'No cards match "zzzqqq". Still showing Robert N. Dennis
   Collection. Try another word, or browse a set.' — the message and
   the wall agree again, and the visitor knows nothing changed. The
   search itself is unchanged: a no-match still keeps the old set.
3. Random always opens the random card. In both states now, the way
   the gallery's Surprise me opens the viewer: while browsing it
   switches to reading first, then opens the pick. Going back to the
   shelves lands the wall on that card's page. The button's work is a
   named randomCard function, so the harness can test it.
4. The flat page names its keyboard shortcuts. One dim line under the
   control row reads "Arrow keys step · Shift + Arrow jumps · Home /
   End first / last", in wording true in both states (arrows step
   cards while reading and page the wall while browsing; Shift+Arrow
   jumps ten cards or to the first/last wall page). It hides on phones
   with the top panel text, where there is no keyboard to use them
   with.

## Deliberately not changed

- The round-15/17/18 deliberately-not-changed lists still stand in
  full, except where this round supersedes one line: the Parlor
  no-match status now names the set still showing (change 2 amends
  the round-11 search behavior's message, not its set handling — a
  no-match search still keeps the old set).
- No bigger change was needed: the audit found small clear wins, so
  the Nov 1 bigger-change latitude was not invoked. A Places view
  was considered and rejected again: places are free text with
  near-duplicate variants, so a list would show the same place
  three times unless the catalog data were normalized, which bigger
  changes never touch.
- The count line's "Showing N of M" reading stands (see the walk
  observation above): N is the filtered total, and the Show more
  button names what is left to render.
- The viewer still has no copy-link button (round 15 holds): the
  address bar carries the #STA-#### link, and the viewer already
  offers Save, VR Parlor, and the source links.
- Clearing a Parlor search still returns to All cards on the same
  card, not the pre-search set (round 11 design).
- The Timeline sort control still shows its stale value while
  disabled, with no explanation that date order is forced (round 15
  holds: the count line already names the order).
- Register rows still carry no open affordance beyond hover
  highlight and their button role (round 15 holds).

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–18), so the round-19 harness runs the
real index.html in jsdom with a fetch stub serving the repo's
browse.json, data.json, search chunks, and per-item records from
disk, and an Image stub that fires onload (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round19-jsdom.cjs).
Expectations are computed from the repo's own browse.json, so a
catalog import between rounds does not stale them.

- 87 checks, 0 failures: the round-17/18 suite still holds in full
  (full catalog renders, newest-first default, full-screen focus
  mode, viewer keyboard paths, Featured shelf, search narrowing,
  reveal on the toolbar, back-to-top, view switches keeping the
  Show-more expansion, How to view under the toolbar); the round-19
  checks hold: the search box names "/" in its title, "/" focuses
  it from the page, "/" inside the box types as itself, and "/"
  does nothing while the viewer is open. The edited script passes
  node --check. (The jsdom scrollIntoView TypeError in the harness
  output is the known jsdom limitation, as in round 18: the How to
  view toggle it follows still passes.)
- One staleness fix inside the harness itself: the round-18 literal
  "23 Niagara matches" went stale — wave20/21 added 23 genuine
  Niagara cards — so the count is computed from the repo's
  browse.json now (46; the slim and full-text hay agree).

Headless harness, Parlor: the full vr.html needs CDN three.js, so
the shipped functions are extracted from vr.html (not copied) and
executed against stubbed state (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round19-parlor-check.mjs,
which supersedes the round-18 Parlor harness).

- 136 checks, 0 failures: the round-17/18 suite still holds in full
  (search, save, keyboard, wall jump, cabinet labels); the round-19
  checks hold: a no-match search reports it, names the set still
  showing ("Still showing Search: \"niagara\"" with an old search
  active, "Still showing All cards" from All cards), and keeps the
  old search; Random while browsing switches to reading and opens a
  random card, Random while reading opens one without switching
  state, Random with no set does nothing, the button wires the named
  randomCard and the old browse-only wall jump is gone; the keyboard
  hint line exists under the control row with all three shortcuts,
  is styled dim and right-aligned, and hides on phones; and the flat
  wall buttons follow the wall page — on page 1 of 32 only Prev is
  spent, on the last page only Next is spent, on a one-page set both
  are spent, and in reading both stay live. The vr.html module
  script passes node --check.

Live verification: after push, curl confirmed the new code served
(the first curl right after the push still showed the old deploy —
GitHub Pages needed a few minutes, as in round 17 — and a re-check
after a pause showed the new code: index.html carries the "/"
handler and title, vr.html carries the still-showing message,
randomCard, and the kbdhint; browse.json serves 3,833 items; both
pages 200). A live browser walk (04:00–04:07 EST) then confirmed
all four changes: pressing "/" put the cursor in the search box and
typing "niagara" narrowed to "SHOWING 46 OF 3833 ITEMS · SEARCH:
"NIAGARA""; pressing "/" inside the viewer left it open with the
search box still reading "niagara"; a Find for "zzzqqq" read 'No
cards match "zzzqqq". Still showing Robert N. Dennis Collection.
Try another word, or browse a set.' with the wall unchanged;
clicking Random while browsing opened a card (STA-2542 "Champion
Spring in Winter…" → STA-2679 "Front Piazza, Grand Hotel, Saratoga,
N.Y", URL #STA-2679, status the reading text); the dim line under
the control row reads "Arrow keys step · Shift + Arrow jumps ·
Home / End first / last"; and the regression spot-check held (Show
more 48 → 96, Register kept the 96 rows STA-3838 down to STA-3743).
No console errors were observed on either page (none observed in the
page views; no console panel is exposed in the walk browser).

What only a headset can judge: whether the in-room control row still
reads clearly in VR now that it shows only inside a session, and
whether the eight-pill reading row still feels uncrowded at arm's
length (held from round 10). Those are Clay's call in the headset.

## Commits (one per change, each revertible on its own)

1. `1c7efc36` — Gallery: "/" focuses the search box
2. `b0787c54` — Parlor: a no-match search names the set still showing
3. `95f6b283` — Parlor: Random always opens the random card
4. `fe2a6142` — Parlor: name the flat keyboard shortcuts under the control row

## Veto list

1. Gallery search key: pressing "/" anywhere outside a text field now
   puts the cursor in the search box, instead of there being no key
   to reach it; inside the viewer, or inside any input, "/" still
   types as itself.
2. Parlor no-match search: the status line now names the set still
   showing ("Still showing Robert N. Dennis Collection"), instead of
   saying only "No cards match" above a wall full of cards.
3. Parlor Random: clicking Random while browsing now opens the random
   card, instead of only paging the wall to its page and changing the
   caption to a card that could not be seen.
4. Parlor keyboard hint: a dim line under the control row now names
   the shortcuts (arrow keys step, Shift + Arrow jumps, Home / End
   first / last), instead of the flat page mentioning only "arrow
   keys flip cards".
