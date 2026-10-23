# The Parlor Room — build note (Oct 23, 2026)

The VR Parlor is now a room instead of a void. Three commits, each
revertible on its own:

- `034e57f` — room shell, projection on the front wall, projector, beam, dust
- `1233f22` — shelves as furniture (browse bookcase, reading low shelf,
  finding-aid cabinet)
- `d815e3b` — projector shutter tie-in for the beam, lens, and beam dust

## The room

- Floor 5.6 × 6.0 m of very dark wood at y=0, centered just behind the
  visitor (z=−0.4), with a slightly lighter inlaid centre panel and a
  muted rug. The brass standing ring from the earlier comfort work stays
  on the floor exactly where it was.
- Walls in deep green (0x14211a): the picture wall at z=−3.4, the back
  wall at z=+2.6, side walls at x=±2.8, ceiling at y=3.1 with two dark
  beams. Baseboards and wainscot rails run the side and back walls.
- Two lamp glows: small emissive amber globes with soft sprite halos on
  the side walls. They are set dressing, not light rigs — the scene
  still runs on the same ambient + one warm point light (both dimmed a
  touch for the room: 0.55→0.42 and 18→11). No shadows, no new dynamic
  lights; all materials are flat-shaded boxes and planes.

## The projection

- The stereo pair now hangs on the front wall (image plane z=−3.37)
  instead of floating at 2.3 m. It kept its exact established angular
  size: the 62° / 46° comfort caps in `sizePair` are unchanged, only the
  plane distance moved (portal depth 2.3→1.07 in the size formula;
  sizing distance 2.7→3.77). Same picture, same comfort, on a wall.
- Feathered edges and rounded corners (F=0.15, R=0.05) untouched. The
  projector dip + recorded slide sound behave exactly as before.

## The projector and beam

- A small carousel-style projector on a low table at (0, 0, −0.95),
  below and in front of the visitor: dark body, carousel tray with a
  brass hub, lens barrel, tiny details. It sits under the shelves'
  sightline and never blocks the picture.
- Lens glow: emissive glass disc + soft sprite at the lens.
- Beam: a faint cone from the lens (0, 0.60, −1.27) to the picture
  centre, opacity 0.05, additive, ending at the image plane — a whisper,
  not a spotlight. It exists only in reading state.
- Shutter tie-in: during the slide-change dip the beam, the beam dust,
  and the lens glow cut out with the photo brightness and return with
  the reveal, the way a real Carousel's shutter blocks the lamp.

## The dust

- 140 motes inside the beam cone, seeded along its length but stopping
  at 88% of the way — about 25 cm short of the wall. Nothing crosses the
  image.
- 150 ambient motes: clusters at the two lamp glows, a drift along the
  side walls, a faint layer near the ceiling. The corridor between the
  visitor and the picture is deliberately empty.
- Both clouds are single THREE.Points with the soft round sprite, a few
  hundred particles total, drifting slowly on sine paths in the render
  loop. Cheap enough for Quest budgets.

## The shelves

- Browse: the card wall is now a bookcase in the same position — dark
  wood back panel, uprights, a board under each row of thumbnails,
  crown and plinth. Paging and tiles unchanged.
- The finding aid (set panel) got a wooden cabinet frame and now lives
  in the scene root instead of inside the browse group, so it is
  reachable in BOTH states: sets can be switched from the shelves while
  a card is projected. Rows, counts, grouping (Start / Collections /
  Series), and current-set highlight unchanged.
- Reading: a low shelf under the picture — a wooden base at floor level
  against the picture wall with its own board; the current set's cards
  stand on it as a six-card window that follows the reading position,
  current card highlighted. Picking one projects it.
- Everything else is untouched: the state machine, `navShow()` dip and
  paint-gated reveal, the record card (starts hidden), `parlorState`
  restore, `#STA-####` deep links, session enter/exit brightness
  restore, the flat controls and the "Current set · Card X of N" line.

## Verification

Headless harness (the real page, local three.js, stand-in texture,
sampled live catalog): zero exceptions, zero console errors. Entry lands
on browse with the beam hidden and a full 24-tile page; opening a tile
enters reading with the beam lit at 0.05 and a six-card shelf window;
stepping fires the dip (brightness and beam both reach 0 and return,
paint-gated); RECORD toggles; set switching works from reading and from
the flat selector; returning to browse hides the beam again.

What only a headset can judge: the room's dimness and scale, shelf
reach, the projection's size on the wall, and whether the low reading
shelf sits comfortably under the picture.

## Fix pass (Oct 23, after Clay's first headset visit)

Clay, from inside the room: the projector was way too distracting and
blocked sight lines to the buttons; he wanted the beam to fade as it
travels, dimmer, ending at the image's edges (no circle); and the dust
subtle everywhere in the room except in front of the image. Three
commits, one per piece, so each can be vetoed on its own:

1. **Projector placement** — the carousel projector shrinks about 20%
   and drops: it stands forward at z = −1.05 on a lower, smaller table
   (top y 0.30). Body centre y 0.37, tray r 0.115, lens height 0.42
   (was 0.60). Its whole silhouette tops out at y ≈ 0.46, well below
   the low control cluster's sight lines. The lens glass shrinks to
   r 0.024 and the glow sprite to an 0.11 m soft glint peaking at
   0.35 opacity (was a 0.30 m disc at 0.5) — no visible circle.
2. **Dust** — the beam dust cloud is gone entirely. One room cloud of
   300 small motes (size 0.011, opacity 0.30, slow drift) spreads
   evenly through the whole room volume. Seeding rejects anything
   inside the beam frustum (cross-sections widened ×1.18 + 0.06, more
   than the ±0.045 worst-case drift, so no mote can wander in) and
   anything in the slab in front of the picture's face. The dust no
   longer cuts during slide changes; it is room air, not beam air.
3. **Beam** — the round cone is replaced by a rectangular frustum:
   12 vertices, 3 rings of 4 corners. The near ring hugs the lens
   (0.030 × 0.024 half-extents at the lens point (0, 0.42, −1.27));
   the far ring IS the presenting picture's rect — refit by
   `fitBeam()` whenever the picture is sized or the state changes,
   reading the flat pair plane's geometry, or the eye planes' live
   per-card rect when a headset is presenting. Brightness fades
   along the length via vertex colours: ring factors 1 → 0.30 → 0
   (a (1−t)² falloff in three rings), warm tint (1.0, 0.875, 0.682).
   Peak opacity 0.034 (was a flat 0.05), so the wall end contributes
   nothing. The shutter tie-in is unchanged: beam and lens glow still
   cut to zero with the dip and return with the reveal.

Verification: harness 35/35 — zero exceptions; browse entry with the
beam hidden; projector top measured at y 0.464 from the scene graph;
beam far-ring vertices equal the picture rect's corners to ~1e-7 in
both flat and eye-plane fits; vertex-colour rings read 1 / 0.30 / 0;
300 dust motes with zero inside the corridor or the screen slab under
a recomputed drift-proof test, and motes present in every room region
(near the side walls, high, low, behind the visitor); the dip drives
beam and glow to 0 and back to 0.034 / 0.35.

What only a headset can judge: whether the projector still distracts,
whether the beam reads as light rather than geometry, and whether the
dust is as subtle as intended. Those are Clay's call in the headset.
