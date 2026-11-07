# UI round 11 — the rectified modes were broken, plus Parlor search

Date: 2026-11-07

Scope: navigation and structure only. The round-10 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are. Catalog: 1,976 items (round 10
was written at 1,775; the +201 came from wave 6 tail and wave 7 imports,
not from this round).

Tree check first: git tree clean, no other job mid-work on index.html
or vr.html. The nightly import landed mid-round (wave7-utica,
STA-1956–STA-1976, commits a837571 and 24f99c6, plus Phase 3 outputs
17c085f) — it touched records/, browse.json, data.json, search/ and
vr.json only, never index.html or vr.html, and the harness expectations
are computed from browse.json on disk, so nothing was stomped.

## Paths walked

Live browser walk of vrparlor.com (02:44–02:53 CST) plus source audit:
gallery landing → shelf/collection → card → next card → back; search →
result → card → back to the same results; register view; Timeline view;
Reading List; empty state; viewer modes and keyboard paths. VR Parlor:
enter → shelves → set → reading → switch set → exit; the flat control
row in both states; the headset landing.

## Gallery friction found

- The four rectified viewer modes were broken for the first 1,026
  cards. Parallel, Cross-Eye and Wiggle showed a blank black frame;
  Anaglyph showed its error. The record's rectified pair is a relative
  rect/NN.jpg, and this site only hosts rect/1026.jpg onward (950
  files, STA-1027–STA-1976); live rect/00.jpg is a 404 while live
  rect/1026.jpg is a 200. The Internet Archive hosts the same files
  from rect/00.jpg onward (the Parlor already loads its pairs from
  there), up to about rect/17xx — the newest rects are not on the
  Archive yet (rect/1900.jpg is a 404 there, rect/1500.jpg a 200).
  So neither host alone covers the catalog; the viewer has to try
  both.
- The viewer picture lagged the title: stepping swapped the title and
  metadata instantly while the previous card's picture stayed until
  the new file loaded — the wrong image under the right title,
  confirmed live on two cards.
- "Request an item" does not request anything. It opens a random card
  from the current results, which the live walk confirmed three times
  (STA-0166, STA-0063, STA-1213 from a Niagara search), with no form
  or explanation. The label promises a request flow that does not
  exist.
- The Parlor had no way to find a card by name: no search field,
  title lookup or place filter anywhere in it. The closest in-Parlor
  route to a Niagara card was SET = Falls & Rivers (348 cards, 15
  wall pages) and scanning thumbnails. Finding a card by title or
  place meant leaving for the gallery.
- In card view on the flat Parlor, the DOM control bar sits directly
  on top of the scene's own control row, both half-legible and hard
  to target. The geometry makes it structural, not viewport luck:
  the in-room row hangs about 29° below the flat camera's horizon,
  near the bottom edge of the view, exactly where the DOM bar sits.

## Gallery changes shipped

1. The rectified viewer modes load from the Internet Archive first,
   then this site, and say so if both fail. A preload tries each host
   in turn (Archive, then this site); Parallel, Cross-Eye and Wiggle
   paint only once a host answers, and Anaglyph routes its image
   through the same loader. The Archive URL matches the one vr.json
   already uses for the Parlor, and the Archive answers
   Access-Control-Allow-Origin: *, so the anaglyph canvas stays clean.
2. The viewer picture fades in on load instead of lingering. The pair
   starts transparent and appears when its file loads, and the
   rectified panels are blanked on every step so they cannot show the
   old card either.
3. "Request an item" becomes "Surprise me", and the About line
   follows it ("let the desk surprise you with a random item"). The
   button opens a random card from the current results; the label now
   says so, matching the button's own id.

## Parlor changes shipped

4. Search the catalog from inside the Parlor (the bigger change). A
   Find box in the flat control row builds a transient Search set from
   the catalog already loaded here (title, place, year, STA id,
   collection, series), opens the first match, and lets Prev/Next
   step through the matches like any other set. The set is listed in
   the flat selector and the finding-aid cabinet with its count;
   clearing it returns to All cards on the same card. A search with
   no matches says so and keeps the previous results. Arrow keys and
   drags are guarded while typing in the box, so they no longer step
   cards or orbit the room. The set is not persisted: a reload falls
   back to All cards on the same card.
5. The in-room control row shows only inside a VR session. On the
   flat page the DOM bar carries every control the flat visitor needs
   (the EXIT pill is a no-op without a session), so the row no longer
   overlaps it. In a session the row is exactly as it was.

## Deliberately not changed

- The round-10 deliberately-not-changed list still stands in full:
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
- No shareable Reading List link was built (held from round 10).
- No copy-link button was added to the viewer. The URL bar already
  carries the #STA-#### permalink for the card on display as you step
  (held from round 10).
- The sticky toolbar covering the top of the shelf and Register rows
  on scroll is normal sticky-header behavior — content scrolls under
  the bar. The "How to view" scroll landing under the bar was not
  verified at the reference size; it stays a candidate for a later
  round with a live check first.
- The Timeline stays decade bands, not a graphic axis or scrubber —
  bands are the shipped design from round 9; a visual timeline is a
  different feature, not a fix.
- Register rows keep no open affordance beyond hover highlight and
  their button role; the whole row is focusable and opens on Enter
  (round 7 holds).
- The era filter matching date ranges that merely overlap a bucket,
  and Oldest-first ordering by the sort year, are data semantics (sy
  is the sort year), not a navigation fix.
- Series chips summing past the catalog total is membership, not a
  partition: a card sits in several series. No copy change was made.
- The finding-aid cabinet's page arrow keeps the same brass disc as
  every other control; its faintness is a judgment call, not a
  defect.
- The catalogue card covering the right half of the pair in flat mode
  keeps its designed position; in the headset it sits to the side.
- "VR NOT SUPPORTED" is three.js's own disabled button state, not a
  control to fix.
- Wall thumbnails filling in progressively on a page turn is network
  loading, not a UI fix.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–10), so the round-11 harness runs the
real index.html in jsdom instead, with a fetch stub serving the
repo's browse.json, data.json, search chunks, and per-item records
from disk, and an Image stub that fires onload (or onerror for a
harness-set URL pattern) so loadRect's host fallback runs in the real
page code (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round11-jsdom.cjs).
Expectations are computed from the repo's own browse.json and search
chunks, so a catalog import between rounds does not stale them:

- 46 checks, 0 failures: full catalog renders (1976 of 1976, 48
  cards on the first page); era options read exactly 1976 / 1056 /
  495 / 116 / 309; "Show more" reads "Show more items · 1928
  remaining" (round 5 holds); search narrows (Niagara → 23) and the
  empty state shows its clear button with "Surprise me" disabled
  (rounds 5 and 6 hold); empty-state clear restores the catalog;
  count line reads "Sorted: Oldest first" for the old-first sort
  (round 4 holds); viewer opens with "Result 1 of 1976 · All items",
  jump forward lands on "Result 11 of 1976", Shift+ArrowRight on
  "Result 21 of 1976", End jumps to "Result 1976 of 1976", Home
  returns to "Result 1 of 1976", jump back from the first wraps to
  "Result 1967 of 1976", and the viewer closes back to the results;
  Research Notes carries target _blank and rel noopener (round 7
  holds); shelf tiles and Finding Aid rows carry tabindex 0 and
  button role (round 7 holds); Tab from the viewer's last control
  wraps to its first (vFav) and Shift+Tab from its first wraps to
  its last (vFull), and ArrowRight still steps to "Result 1968 of
  1976" after the trap checks (round 8 holds); Enter on a shelf tile
  opens "Result 1976 of 1976 · All items"; register rows carry
  tabindex 0 and Enter on one opens "Result 1 of 1976 · All items";
  Timeline view shows while the grid hides, the first band reads
  "1820s · 2 items", the 1850s band carries its full filtered count
  of 256 items, the sort control reads disabled and the count line
  reads "In date order" in Timeline view, the first Timeline card
  opens the chronological first item (STA-0695, "Result 1 of 1976 ·
  All items"), leaving Timeline re-enables the sort and restores the
  grid, and with the era filter set to Undated the Timeline shows
  exactly one band, "Undated · 309 items", with no 1900s band; the
  view toggle reads aria-pressed true on Shelves at load, follows
  Register and Timeline on click, and Shelves reads false while
  another view is active; the viewer picture starts transparent
  until its file loads (round 11); Parallel mode loads the rectified
  pair from the Archive (rect/00.jpg) and falls back to this site
  when the Archive fails (round 11); the Anaglyph path runs through
  the same loader (in jsdom the draw itself reports "blocked"
  because jsdom has no 2d canvas — the loader and error path are
  what the check covers). The edited script also passes a syntax
  parse with no errors.

Headless harness, Parlor: the full vr.html needs CDN three.js, so
the shipped search and save functions are extracted from vr.html
(not copied) and executed against stubbed state (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round11-parlor-check.mjs,
which supersedes the round-10 Parlor harness):

- 64 checks, 0 failures: searching "niagara" builds a transient
  Search set with the 2 matches, spliced after All cards, opens the
  first match, lists "Search: "niagara" · 2" in the set selector and
  in the finding-aid entries on the Start page, shows the clear
  button, and refreshes the status line; a search with no matches
  reports it and keeps the old search; a new search replaces the old
  one; saving while on a search set keeps the search set and adds the
  Reading List set; clearing returns to All cards on the same card,
  empties the box and hides the button; clearing while on another set
  leaves it alone; an empty search clears the set; the round-10 save
  scenarios all still hold through rebuildSets (save/unsave, removal
  stepping to the card that slid into place, last-removal fallback to
  All cards on the same card, collection re-point, no-op with no
  current card); call-site checks confirm the Find box, Find and
  Clear wiring, Enter-to-search, the keydown/drag/click guards, the
  cabinet listing, rebuildSets re-inserting the search set, the
  in-room row showing only in a VR session, and the round-10 save
  wiring (drawCaption sync, flat Save button, in-room SAVE pill dim
  at start). Both vr.html script blocks also pass node --check with
  no syntax errors.

Live verification: NOT YET COMPLETE — the deploy failed, not the
code. The push of the five change commits (be00574) triggered a
Pages build that ran 11m18s and failed: the build itself succeeded,
but the deploy step sat in `syncing_files` for about ten minutes and
then timed out ("Timeout reached, aborting!"), so the deployment was
cancelled and the live site kept serving the pre-round files
(verified by curl at 09:21 and 09:27 UTC: "Request an item" still
served, no Find box, Last-Modified 09:00:04Z). A live browser walk
at 03:12–03:19 CST confirmed the same: 1976-item count live (from
the earlier import deploy), stepping picture matching its title, but
"Surprise me", the rectified modes and the Find box all still absent
— consistent with the old files being served, not with the new code
failing. A `--failed` re-run of the deploy was queued at 09:27:35Z
and had still not started after five minutes. The doc push below
triggers a fresh Pages build; live verification is owed once a
deploy succeeds, and this section must be updated then — do not
treat the harness passes above as live verification.

## Commits (one per change, each revertible on its own)

1. `f4c991c` — Gallery: rectified viewer modes load from the Archive with a site fallback
2. `2071f78` — Gallery: viewer picture fades in on load instead of lingering
3. `90b21fc` — Gallery: 'Request an item' becomes 'Surprise me'
4. `ebab544` — Parlor: search the catalog from inside the Parlor
5. `be00574` — Parlor: in-room control row shows only in VR, not over the flat bar

## Veto list

1. Gallery rectified viewer modes (Parallel, Cross-Eye, Wiggle, Anaglyph) load the pair from the Internet Archive first, then this site, and say so if both fail.
2. Gallery viewer picture fades in when its file loads, instead of the old card's picture lingering under the new title.
3. Gallery "Request an item" button renamed "Surprise me", and the About line follows it.
4. Parlor Find box: search the catalog by title, place or year from inside the Parlor; matches become a Search set you step through like any other set.
5. Parlor in-room control row shows only inside a VR session; on the flat page only the DOM control bar shows.
