# Tagging pilot — vision-assigned index tags on 40 cards

Date: 2026-10-22. Status: pilot published; Clay judges hit quality live
before any full-catalog run.

## What this is (and is not)

Tags are an INDEX layer, separate from the catalog record. Per the
Archive Policy source-fidelity rule, titles, places, dates and blurbs
remain the source archives' own words, untouched. A tag is a
machine-assigned subject term describing what is visibly pictured,
stored in a new optional `tags` field on the item's record, labeled
"Index tags" wherever displayed (the Catalogue Record), and carried
into the full-text search haystack so pictured content is searchable.
Tags never enter any catalog text field.

## Vocabulary

`tools/tag_vocabulary.json` — 189 terms in 9 groups (animals; built
environment; interiors & exhibits; landscape & nature; people &
activity; transport; war, events & damage; water; work & industry).
Lowercase, singular. The tagger may only choose listed terms;
`tools/build_catalog.py` now refuses a record whose tags are not all
in the vocabulary, so the constraint is enforced by the build, not by
convention.

## Slice

40 cards, deterministic stride picks inside every series shelf
(cities 9, mountains 7, water 6, oddities 6, world 4, people 4, war 4;
two stride collisions on multi-shelf cards replaced by continuing the
stride, giving 40 unique cards). Shelf coverage of the 40: all seven
shelves. Collections: Robert N. Dennis 19, Source unrecorded 16,
Keystone View Company 2, Rijksmuseum 3.

Each card's rectified pair (thumbs-rect w1000) was viewed; tags
describe what is visible in the picture. 38 cards tagged (125 tag
assignments, 3.29 per tagged card, 67 distinct terms used);
2 held at low confidence — no tags published for them.

## The 40 cards

| STA | Shelf(s) | Title (truncated) | Index tags | Conf. |
|---|---|---|---|---|
| STA-0082 | cities | Vicksburg and the Heights, by A. L. Blanks | church, courthouse, house | high |
| STA-0165 | cities, people | People posing with train engine that derailed at bridge, by H. P. McInto | locomotive, train wreck, crowd, bridge | high |
| STA-0382 | cities | Michigan Ave., north from 13th Street, by Lovejoy & Foster | main street, storefront | high |
| STA-0531 | mountains, cities | Sugar Loaf Mountain and Webster's Station. (no. 615) (NYPL b11707292-G89 | wagon, mountain, rock formation, forest, pine tree | high |
| STA-0587 | cities | Ether Monument in Public Garden, Boston | monument, statue, row houses, garden, children | high |
| STA-0677 | cities, mountains | Railroad bridge, Watkins Glen, N.Y, by Hope, J. D., 1846-1929 3 | passenger train, trestle bridge, bridge, gorge | high |
| STA-0797 | cities | Bank safes being guarded, from Robert N. Dennis collection of stereoscop | soldiers, ruins | high |
| STA-0897 | water, cities | Falls of St. Anthony--building the great apron, by Beal's Gallery | construction, dam, river | high |
| STA-0984 | water, cities | East River bridge, N.Y, from Robert N. Dennis collection of stereoscopic | suspension bridge, sailing ship, harbor | high |
| STA-0098 | water, mountains | The Basin, Franconia, New Hampshire (NYPL b11708055-G91F020 004F) | rock formation, forest, pine tree, waterfall | high |
| STA-0285 | mountains | South Gorge, Isles of Shoals, by Davis Brothers | rock formation, gorge, ocean | high |
| STA-0650 | mountains | A couple relaxing on logs in Watkins Glen, by Hope, J. D., 1846-1929 | waterfall, gorge, rock formation, portrait group | high |
| STA-0686 | mountains | Entrance, Watkins Glen, by R. D. Crum 2 | staircase, gorge, rock formation, waterfall | high |
| STA-0722 | mountains | Mt. Cannon, Franconia (NYPL b11708043-G91F019 248F) | forest, mountain | high |
| STA-0758 | mountains, cities | Portland & Ogdensburg Railroad, Crawford Notch, N.H, from Robert N. Denn | passenger train, railroad tracks, mountain, forest | high |
| STA-0833 | mountains | Summit House, after a frosty night, Mt. Washington, N.H, by Bierstadt Br | snow, ice, mountain, rock formation | high |
| STA-0064 | water | Niagara River (rapids by moonlight), Niagara Falls, N.Y., U.S.A, by Keys | rapids, river, waves | high |
| STA-0216 | water | Wreck of steamer Chautauqua, after the explosion of her boiler at Whitne | steamboat, shipwreck | high |
| STA-0405 | water | Cut-Whitehall and Saratoga Railroad, steamboat landing, Lake Champlain | railroad tracks, rock formation | high |
| STA-0628 | water | Congress Spring, Saratoga, from Robert N. Dennis collection of stereosco | crowd, portrait group, children | high |
| STA-0745 | mountains, cities, water | Nancy's Brook and Bridge, White Mountains, by Pease, N. W. (Nathan W.),  | waterfall, creek, bridge, forest | high |
| STA-0929 | water | Silver cascade, near St. Anthony | waterfall, river, rock formation | high |
| STA-0178 | oddities | Shafts and mines "Little Pittsburg" and "Little Chief.", by Thurlow, J., | mine, mining | high |
| STA-0252 | oddities | Stripping off the surface dirt covering the Morris open pit mine, Mesabi | steam shovel, mining, mine, workers, freight train | high |
| STA-0321 | oddities | Diana's Bath Water Gap Pa, by R. Newell & Sons | waterfall, creek, forest | high |
| STA-0379 | oddities | Bird's-eye view from Shot tower, N.W | factory, warehouse, main street | high |
| STA-0455 | oddities | Oldest house, Salem, Mass | — held — | low |
| STA-0515 | oddities | Town square, by William S. Robbins & Co. | church, horse-drawn carriage, house | high |
| STA-0840 | world | Gezicht op het interieur van een synagoge in Parijs, Frankrijk Intérieur | room interior | high |
| STA-0874 | people, world | Twee Noord-Afrikaanse mannen tijdens de tentoonstelling Oud-Holland in 1 | portrait group, exposition | high |
| STA-0943 | mountains, world | Rømbøl i Hardanger - no-nb digifoto 20150205 00155 bldsa stereo 0300 | fjord, mountain, snow, forest, farmhouse | high |
| STA-1009 | water, world | Gezicht op de Thunersee nabij Thun, Zwitserland Environs de Thoune (tite | lake, mansion | high |
| STA-0055 | people | A Happy family (NYPL b11708207-G91F081 047F) | family, portrait group, children | high |
| STA-0480 | people | A group of students on the steps of their school, by J. S. Lefavour 2 | children, portrait group, schoolhouse, crowd | high |
| STA-0036 | war | Fort Pulaski, by Wilson, J. N. (Jerome Nelson), 1827-1897 | fort, meadow | high |
| STA-0052 | war | 1st N.Y., Bat. K, S.E. of Stannard's Column, Gettysburg, Pa | monument, memorial, cannon | high |
| STA-0231 | water, mountains, war | Sioux camp in Castle Creek valley, by Illingworth, W. H. (William H.), 1 | — held — | low |
| STA-0280 | war | "Camp Peace", Faribault Minn | tents, camping, dog, snow, hunting | high |
| STA-0054 | people | Portrait of a family on porch stairs (NYPL b11708207-G91F081 019F) | portrait group, family, house, garden | high |
| STA-0164 | cities, people | People posing with train engine that derailed at bridge, by H. P. McInto | locomotive, train wreck, crowd, bridge | high |

## Held (low confidence — no tags published)

- **STA-0455** ("Oldest house, Salem, Mass") — heavily faded and
  distant at review size; the small carriage party by the gate cannot
  be verified, only "house" is resolvable. Held rather than guess.
- **STA-0231** ("Sioux camp in Castle Creek valley") — the camp is a
  distant scatter of small pale shapes at the resolution limit;
  tents and horses cannot be verified from the image alone. Held
  rather than tag from the title.

## Vocabulary-gap candidates (seen, but no honest term existed)

Not published as tags; candidates for a vocabulary v2 decision.

- **trees** (generic) — STA-0082, STA-0382: scattered park/street
  trees; "forest"/"pine tree"/"palm tree" do not fit.
- **safe** (bank safe) — STA-0797: the rows of guarded bank safes are
  the literal subject of the card.
- **derrick** (derrick crane) — STA-0897: the construction derrick at
  the Falls of St. Anthony apron works.
- **pavilion** — STA-0628: the Congress Spring pavilion; "gazebo"
  undersells a large colonnaded structure.
- **synagogue** — STA-0840: a synagogue interior, tagged only
  "room interior" because "church interior" would be wrong.
- **headframe** — STA-0178: the mine shaft headframes are the subject.
- **town square** — STA-0515: the Plymouth square itself.
- **pier** — STA-0984: prominent waterfront piers under the East
  River bridge (a "pier" tag was assigned in review and struck for
  being out of vocabulary — the discipline working as intended).

## Proof: demo queries, before vs after

Result sets computed with the page's own rule (lowercased substring
match over the search-chunk haystacks), baseline = the pre-pilot
chunks, after = the rebuilt chunks. Every pilot card gained by these
terms was verified clean: the term appears nowhere in that card's
title, place or blurb — text search alone could not find it there.

| Query | Before | After |
|---|---|---|
| locomotive | (none) | STA-0164, STA-0165 |
| crowd | (none) | STA-0164, STA-0165, STA-0480, STA-0628 |
| dog | STA-0087, STA-1024 | STA-0087, STA-0280, STA-1024 |

Notes: "locomotive" existed nowhere in the text index (the wreck
cards' titles say "train engine"). "dog" gains STA-0280, "Camp
Peace", whose photograph is built around a dog lying on furs in
front of the tent. Other 0-to-N terms from the pilot: portrait group
(0→6), train wreck (0→2), passenger train (0→2), staircase (0→1:
STA-0686, "Entrance, Watkins Glen"), steam shovel (1→2: STA-0252),
suspension bridge (9→10: STA-0984).

## Findings worth keeping

- **STA-0405**: the source title says "steamboat landing, Lake
  Champlain", but the scanned pair shows two men at a railroad
  switch in a rock cut — no boat at all. Vision tags (railroad
  tracks, rock formation) describe the card a visitor actually sees;
  a reminder that source titles can describe a series, not a frame.
- **STA-0036** (Fort Pulaski): the rectified w1000 crop showed only
  the foreground field — the fort sits on the horizon in the full
  scan. Tagging review should fall back to the original scan when
  the rectified crop is empty.
- **STA-0164 / STA-0165** are two scans of the same derailment and
  received identical tag sets independently — a small consistency
  signal for the method.

## Pipeline changes

- `schema/catalog-v2.schema.json`: optional `tags` (array of strings).
- `tools/build_catalog.py`: haystack appends a record's tags;
  record validation rejects any tag outside the vocabulary.
- `index.html`: the Catalogue Record gains one row, "Index tags",
  shown only when the record has tags. No other UI change.
- Rebuild is deterministic (two consecutive builds byte-identical);
  `tools/validate_catalog.py --v2` reports 0 errors.
