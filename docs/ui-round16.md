# UI round 16 — see the picture big, and a Featured shelf

Date: 2026-11-17

Scope: navigation and structure only. Clay-directed this round, not the
scheduled audit: on a phone the pictures could never be seen big
because the viewer header and the landing-page banners crowded them,
and Clay asked for a featured collection of the best views.

Catalog: 3,011 items. No catalog data touched.

## What Clay said

- "you can't see them really big because all the junk around fit is
  in the way. especially on mobile. All those banners get in the way
  of using the actual site."
- "also a featured collection would be cool with the best of the
  archive. Really interesting ones"

## Gallery changes shipped

1. Viewer full-screen focus mode. A "Full screen" button in the
   viewer header hides the header (title, buttons, mode row) and the
   record below, so the picture fills the screen. The button, a tap
   on the picture, the F key, or the floating exit button bring the
   chrome back. Esc leaves full screen first, then closes on a
   second press. Full screen survives stepping to the next card, and
   closing the viewer resets it. In full screen the eye and wiggle
   panels size off the viewport height, not just their width, so a
   landscape phone fills the screen instead of leaving the picture a
   thin strip. A 2:1 picture on a portrait phone is still only half
   the screen wide by geometry; turning the phone sideways is what
   makes it fill the screen, and that is in the report to Clay.
2. Mobile mode row slimmed. On a phone the view-mode row wrapped to
   three rows of buttons above the picture. It is one sideways
   scrolling row now, and the hint line under it is hidden, so the
   picture starts higher and reads bigger even before full screen.
3. Featured shelf. "Featured · The Best of the Archive" sits above
   the toolbar with twelve hand-picked views: Niagara (STA-0001),
   the Full Moon (STA-0026), Fort Sumter (STA-0014), El Capitan
   (STA-0034), the Grand Canyon (STA-0006), the Pyramid of Gizeh
   (STA-0156), the Brooklyn Bridge (STA-0960), the 1906 earthquake
   (STA-0764), Yellowstone bison (STA-0109), the Niagara daredevil
   (STA-0037), an 1850s gas balloon (STA-0025), and a 1911
   Antarctic iceberg (STA-0027). Same shelf pattern as Recent
   Accessions, same keyboard behavior, its own edge buttons. The
   shelf-button sync is shared between the two shelves now. The
   list is site presentation only and lives in index.html, never in
   records/; every ID was checked against browse.json and a missing
   card would be skipped.
4. Toolbar scrolls away. The toolbar used to stick to the top while
   scrolling, always covering the top of the page. It scrolls up
   with the rest of the page now. The search-results reveal no
   longer measures the toolbar height for its scroll offset, since
   there is no sticky bar to clear anymore.

## Deliberately not changed

- The landing-page hero, finding aid, and Recent Accessions shelf
  were not removed or collapsed further: the finding aid already
  hides behind a tap-to-open toggle on phones, and the complaint
  was about seeing a picture big, which the full-screen mode
  answers. If the landing page itself still feels crowded on a
  phone, that is a next round.
- No bigger change was needed: the audit found small clear wins, so
  the Nov 1 bigger-change latitude was not invoked.

## Verification

Headless harness, gallery: the managed Chromium in this VM refuses
direct startup (as in rounds 7–15), so the round-16 harness runs the
real index.html in jsdom with a fetch stub serving the repo's
browse.json, data.json, search chunks, and per-item records from
disk, and an Image stub that fires onload (harness at
~/workspace/goals/stereograph-archive/hidden_files/ui-round16-jsdom.cjs):

- 33 checks, 0 failures, plus 3 more for the toolbar change: the
  toolbar rule carries no sticky positioning, it keeps its banner
  styling, and the reveal no longer measures the toolbar height.
  Both inline script blocks pass node --check.
- Live verification: a desktop-width browser walk (1919 x 998, the
  cloud browser could not be resized to a phone width) measured the
  picture before and after full screen on STA-0001: normal 1100 x
  541 px with the header taking the top ~210 px, full screen 1919 x
  959 px, about 3.2x the area, header, mode buttons and Catalogue
  Record all gone, the floating exit button present, and tapping the
  picture returning the viewer exactly to its normal size. The
  phone-specific mode row (single sideways-scrolling row, no hint)
  was NOT verified live — it rests on the harness CSS checks. One
  caching note from the walk: the first load showed no Full screen
  button at all until a fresh cache-busted reload; a visitor on a
  cached copy may need a hard refresh to see it.

## Commits (one per change, each revertible on its own)

1. `5f37cb1` — Viewer: full-screen focus mode, slimmer mobile mode row
2. `b3855c0` — Gallery: Featured shelf with twelve of the best views
3. `fb4b0ae` — Gallery: toolbar scrolls away with the page

## Veto list

1. Viewer full-screen mode: a Full screen button hides the header
   and the record below so the picture fills the screen, instead of
   the picture sitting small under all the viewer chrome.
2. Mobile mode row: the view-mode buttons are one sideways
   scrolling row with no hint line under them, instead of three
   wrapped rows above the picture.
3. Featured shelf: twelve of the best views sit above the toolbar
   under "Featured · The Best of the Archive", instead of the page
   opening straight onto the toolbar and the full catalog.
4. Toolbar: it scrolls up with the rest of the page now, instead of
   sticking to the top and always covering the top of the screen.
