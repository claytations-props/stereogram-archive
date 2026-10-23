# UI round 3 — navigation audit

Date: 2026-10-23

Scope: navigation and structure only. The round-2 paper catalogue-card
language, squared chrome, gold primary action, tabular numerals, and
two-column phone grid stay as they are.

## Paths walked

Gallery: landing → shelf or collection → card → next card → back;
search → result → card → back to the same results.

VR Parlor: enter → choose a set → read → switch set → exit.

## Gallery friction found

1. The series chips are the fastest shelf navigation, but their counts
   are only visible farther down the page in the Finding Aid. On a
   phone the Finding Aid starts collapsed, so the main shelf controls
   give no sense of shelf size before a tap.
2. Search, era, collection, and series can combine, but there is no
   single reset. The empty state tells the visitor to clear the search
   even though no clear control exists.
3. The result count names only some active context. It omits the
   search text, era, and Reading List state, so a visitor returning
   from a card has to reconstruct where they were.
4. The viewer says "Close" rather than naming its destination, and it
   does not say which result is open or how large the current result
   list is. The underlying state does survive, but the path back is
   not legible.
5. The five stereo-mode names appear without point-of-use guidance.
   The explanation lives in a separate "How to view" section behind
   the viewer, after the choice has already been made.
6. "Request an item" discards the current search/filter context and
   chooses from the whole catalog. A visitor working inside a result
   set gets pulled out of it.

## Gallery changes shipped

1. Series and Reading List chips now carry live counts.
2. A "Clear search & filters" button appears in the toolbar whenever
   search or a filter is active; it resets search, era, collection,
   and series together.
3. The result count now names the active search, era, collection,
   series, or Reading List context.
4. The viewer close control reads "Back to results," and a context
   line in the viewer gives the open card's position in the current
   result list plus that list's context.
5. A one-line hint under the viewer modes changes with the selected
   mode and says what that mode is for.
6. "Request an item" now chooses from the current filtered results.
   With no active context, that remains the whole catalog.

## Parlor friction found

1. A plain Parlor entry still opened in reading state, including an
   entry restored from saved state. The shelves existed, but a new
   visitor met one card first and had to discover them.
2. Direct record links did need to keep opening their card; the fault
   was the default entry, not the record path.
3. There was no direct set switcher while reading. The only route was
   to leave the card, enter browse, change the wall, and then open a
   card.
4. The set panel was one undifferentiated list. It fit the current
   seventeen sets only narrowly and would overflow its panel as more
   collections arrive.
5. The current set and position were present in the caption and the
   flat page's card text, but not as a clear, persistent location
   label in the flat controls.

## Parlor changes shipped

1. Plain Parlor entry now lands on the shelves/browse wall. A saved
   set and card remain selected and highlighted there. `?set=` entry
   also lands on that set's wall.
2. `#STA-####` direct record links still open directly in reading
   state, in the set supplied by the link or the card's own context.
3. The flat controls gain a set selector with counts. Changing it
   while reading switches the set without leaving reading state;
   changing it while browsing retargets the wall.
4. The 3D set panel is grouped under Start, Collections, and Series,
   carries counts, highlights the current set, and pages when the
   groups no longer fit.
5. The flat card panel gains a persistent "current set" line with
   the card's position. In the headset, the caption plaque continues
   to carry the same set and position line.

## Deliberately not changed

- Filter state was not moved into the gallery URL. Opening and
  closing a card already preserves it in-page, and changing the URL
  contract would put the record permalink scheme at risk.
- Browser Back was not rebound to close the viewer. `#STA-####`
  remains a record permalink first.
- The Parlor's browse wall, reading controls, projector change,
  record-card behavior, and photo treatment were not redesigned.
- No visual restyle was made. New controls reuse the existing dark
  panels, brass accent, squared corners, and type.
