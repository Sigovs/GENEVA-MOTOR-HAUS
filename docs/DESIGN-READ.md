# Geneva Motor Haus — Design Read (homepage)

2026-09-10 · **v2, the same day** · Design DNA from `/Users/alex/Desktop/WORK/design_dna/TASTE.md` (canonical Mac path).

> **Superseded values (2026-09-14).** This Read records the decisions of 10 Sep. Since then the ground
> is `#161617` (not `#15100C`), the eyebrow plate is `#313C29` with `#DFD4AF`, and the entrance motion
> is a set of roles on every page. The current tokens, components and rules are in **`ds.html`**, which
> reads its values from the live CSS.
Brief: the client's AAN ticket (`from client/`), recorded verbatim in `DISCOVERY.md`.

```
Delivery: BUILD — the client chose the direction ("They want the new CMC design"); Alex set how it is read (v2, below).
Reading this as a dealership homepage for enthusiast buyers — half of them out of state, buying from photos — leaning enthusiast-editorial in daylight.
Mandate: REDESIGN — Geneva's badge, its colours, its live site's sections in their order and its own facts carry through; CMC index_3 supplies the LANGUAGE (dark editorial ground, uncut dealer photography, the stage, pill controls, one-shot reveals), never its layouts one for one.
Style mode: PURE — auction-editorial (confirmed), executed with a brand-derived display face and one brand-derived device; unifying principle: n/a.
Dimensionality: ABSENT — depth is carried by tone and photography; the one signature move is a 2D map, not a scene.
```

## Why the Read was re-run (Alex, 2026-09-10)

> "It is too 1:1 CMC, and we can never do that. When Kirsten says *They want the new CMC
> design*, we still keep to it, but regulate it our own way, as designers."
>
> "*The sections he has on his live site is what he wants* — is this respected?"

It was not. v1 forked CMC's index_3 **skeleton** section for section — masthead, lower-left
claim, stage, step plates straddling a seam, a big-number stats row, a centred financing
card, a two-column about, carded reviews, even CMC's own line *"Come see what's on the
floor."* — and changed only tokens, words and one chapter. And it carried 4 of the live
site's 8 featured cars, none of its four tiles, one of its four tabs, no map and no
floating Sell button.

**The rule taken from it** (memory: `new-x-design-means-interpret`): another client's
site is the *language*. The skeleton and the character are this client's.

**Concept.** *One haus in Wisconsin, shipping far.* The cars are shown where they
actually live — the lot, the showroom, a drive in spring — and the page carries them
from that door to a buyer who may never see it.

**Peak:** the stage — eight cars, uncut photographs. **Signature move:** *the reach* —
light leaving the door in Burlington across the lower 48, the 500 / 1,000 / 1,500-mile rings
appearing as it reaches them; once, 2.1 s, then still (v1, rings drawn on the scroll, was
rejected by Alex 2026-09-10).

## What carries — three columns, not two

| From Geneva — identity and skeleton (fixed) | From CMC index_3 — the language (approved) | Geneva's own departures (designed) |
|---|---|---|
| The adjusted badge; barn red `#BC0F0D`, cream lettering, wood-dark ground | Dark editorial ground; uncut dealer photography | **Zilla Slab** display — the slab lettering on the badge. Alex chose it from four rendered on the real hero (Inter Tight, Zilla Slab, Archivo Expanded, Fraunces) |
| **The live site's sections, in its order** — 8 featured, 4 tiles, 4 tabs, sell, reviews, newsletter, contact + map, floating Sell | The stage: one large photograph beside an index | **The name centred between the two 911s** — the live site's own gesture, set on the asphalt the pair leaves empty |
| Their words and facts, trimmed, never extended | Pill controls, micro eyebrows, the one-shot reveal system | **The gable** — the barn roof in the badge, the timber gables over the building's doors — replacing CMC's S-curve shelf, used once |
| The ticket: header search, shipping, warranty kept, CMC's services / Karma / random sections removed | The masthead rail | A ledger index; ruled steps, not plates; open reviews, not avatar cards; four tiles under one lintel |

## Palette — derived, stated (color I5)

| Token | Value | Derivation | Measured |
|---|---|---|---|
| `--bg` | `#15100C` | the badge's wood ground `#24180C`, one step darker so photographs hold | ink 16.4:1 |
| `--bg-raised` | `#211A13` | the same wood, one step up | ink 14.9:1 |
| `--ink` | `#F3EEE6` | warm off-white toward the lettering; never #FFF | — |
| `--ink-3` | ink @ .54 | floor for 14px on the darkest ground | 5.4:1 on sunk |
| `--bone` | `#ECE4D6` | the lettering cream, lifted to a reading ground — the one light chapter | bone-ink 14.5:1 |
| `--accent` / action | `#BC0F0D` / `#A80E0B` | the barn roof in the adjusted logo, median of 80,943 px | ink on it 5.66 / 6.65:1; on bone 5.18:1; vs bg 2.89 → fills and hover only on the dark ground |

**Type.** Display `Zilla Slab` 500–700 (tracking −0.012em; −0.03 was Inter Tight's and
clots a slab); body and labels `Instrument Sans`. Two families, no mono. Verified in the
render at the sizes set: 116px claim, 40px titles, 14px price pills, step numerals.

## Hero declaration (v2)

| | |
|---|---|
| event | The haus is open: two 911s on the lot, the name between them. One slide. |
| viewport ownership | full first screen, masthead counted |
| scene treatment | environment — their own lot and steel building, daylight |
| object scale | as photographed: two cars ≈ 55% of frame width, both whole |
| focal point | the name, then the navy 997 at the right |
| negative space | the asphalt below and between the cars — it carries the name; darkened by one bottom ramp built from `--bg-rgb` |
| text safe zone | centre-bottom, 64% × 38% (desktop); below the photograph on a phone |
| desktop crop | `object-position: 70% 62%` — the 5:4 media box trims a 4:3 frame; both 997s are whole only between 68% and 76% |
| mobile crop | separate composition: the photograph is its own field in the top 52svh, the navy 997 whole (the grey 997's tail leaves at the left edge — stated); the type centred below on the ground |
| asset suitability | 4032×3024 phone frame, hard light — suitable at 1440; soft past 2560 (declared) |

Governing event components: `.hero__media` (subject) · `.hero__scrim` (field) ·
`.hero__claim` / `.claim` (identity) · `.hero__meter`, `.lede` (support) · `.cta-row`
(**Browse inventory · Contact us** — the live site's pair; *Sell your car* rides in the
floating pill). Excluded: masthead, read bar.

## Composition — short form (v2)

- **Artistic image:** a daylight working garage that sells cars people drive — or ship — across states for.
- **Masses:** (1) hero · (2) the stage, eight cars — dominant after the hero · (3) four tiles — a directory, low rank · (4) the haus — four answers beside one headline · (5) the distance map — the one wide pause · (6) the bone chapter under the gable: sell, steps, warranty · (7) reviews · (8) newsletter band · (9) contact + map, footer.
- **Centre:** semantic = the cars; optical = the stage photograph; action = header search + stage.
- **Rhythm:** dark · dark · rule · dark · **map (pause)** · **bone, under the gable** · dark · sunk band · dark.
- **Device budget:** one new device — the gable — used once. Tiles and haus separate by hairline, the system's existing grammar.
- **Diagnosis avoided:** C20 — shipping stays support; the stage stays the peak.

## Section map (v2) — the live site's order

| # | Live site | Geneva |
|---|---|---|
| 1 | Hero — the name, centred; BROWSE INVENTORY · CONTACT US | the name centred between the 911s; their CTA pair |
| 2 | Featured Inventory — 8, carousel | the stage with all 8, a ledger index, dated prices |
| 3 | Tiles — Reviews / Financing / About Us / Touch | the four tiles, their labels; **CMC's Financing and About chapters removed** (Alex: "only tiles, as Shane has them") |
| 4 | Tabs — Selection / Reputation / Process / Service | opened, side by side; trimmed; the template claims ("over 12 years", "thousands of satisfied customers", "maintenance programs") left out — ledger `notUsed`; Reputation carried by Patrick's own words |
| 5 | — (ticket 4: "needs a shipping section") | the distance map + three buyers' quotes |
| 6 | Sell your car | the bone chapter under the gable; four ruled steps |
| 7 | — (ticket 4: "wants to keep warranties") | warranty, in the same bone chapter |
| 8 | Reviews — carousel | twelve reviews, open |
| 9 | Newsletter | its own band |
| 10 | Contact / Location + Google map | their title, a Google map of 600 Faust Rd, hours, directions |
| — | floating SELL YOUR CAR | kept; stood down over the hero, the Sell chapter, contact and footer (U10) |
| — | sticky info bar (address · phone · email) | **not carried** — the phone is in the bar, the address and email in Contact; stated |
| — | marquee | **not carried** — its copy is superlatives ("premier destination", "unmatched"), CP6 |

## MOTION READ

```
Subject          A dealership's cars (static) — and one temporal fact: they travel far from this door.
Journey          see what this is → browse eight cars → pick a door → why here → learn they ship → sell → buyers' words → the door
Static verdict   Yes — every reveal stripped, hierarchy, reading order and every means survive.
Time adds        Distance. Light leaving the door in Burlington and reaching 500, then 1,000, then 1,500 miles at equal intervals says "the car goes to you" in the one medium a static map cannot.
Register         ordinary — a dealership homepage; nothing heightened is claimed.
Primary idea     per viewport: shipping band → THE REACH plays once. The hero is a single still.
Stable           prices, mileage, the quotes, nav, search, every CTA. Quotes are never hidden to be revealed.
Roles            section entry → hierarchy (inherited, one-shot) · stage focus-pull → state change (inherited) · THE REACH → spatial explanation (the one signature move) · floating pill → feedback of place (stands down where it repeats). CMC's "Sell rides over the pinned band" was REMOVED: the band is taller than a screen and its CTA was never visible in real scrolling (C14 outranks the device).
Transport        the reader. One-shot at 60% in view, 2.1 s, no pin, no hijack, never replays.
Learning         none.
Mobile           re-authored: the map full width between copy and quotes; the same reach at the map's own scale; labels are HTML so they keep 14px.
Reduced motion   never armed: the lit map, every ring and label; nothing moves.
Cost             transform + opacity on two circles and three paths, one IntersectionObserver, ~0 payload.
Cut              v1 of the map move (rings drawn on the scroll — read as a loading spinner, fragments at every resting frame, rejected by Alex) · a straight route line with pins · a car icon travelling a line (MJ10) · arcs to named destinations (none supplied — CP7) · quotes revealed one by one (MJ7) · a count-up on "23" (the stats row went with v1's CMC Selection chapter).
```

**Implementation route:** Genjutsu `cast`, light scope, stack = vanilla CSS → `css-native`.
Map geometry: us-atlas 3.0.1 (US Census Bureau boundaries, public domain), lower 48, Albers —
`docs/source/us-map-lower48-albers.json`.

## Critique panel — on v2

1. **Composition** — four tiles straight after the stage could read as a second index. *Accept* — type only, hairline-ruled, lower rank than the stage; they are doors, not stock.
2. **Brand advocate (the client asked for CMC)** — is it still "the new CMC design"? *Accept* — the ground, photography, stage, controls and motion are CMC's; a client who liked CMC recognises it, and nothing on it is CMC's own.
3. **Contrarian** — a slab display risks rustic kitsch. *Reject* — Zilla Slab is a text slab with editorial proportions; kitsch would be wood type or a Clarendon. Proved on the page's own strings (claim, prices, step numerals).
4. **Content** — the tabs are template copy. *Accept* — trimmed to what reviews corroborate; Reputation is a customer's sentence; the rest recorded in `notUsed`.
5. **User advocate** — a floating pill covers content bottom-right. *Accept* — stood down over the hero, the Sell chapter, contact and the footer; counted as a persistent mass (U10).

| # | Point | Disposition |
|---|---|---|
| 1 | Tiles as a second index | accept — type only, low rank |
| 2 | Still "the new CMC design"? | accept — language kept, nothing CMC-specific |
| 3 | Slab = kitsch | reject — proved in the render |
| 4 | Template tab copy | accept — trimmed, notUsed |
| 5 | Floating pill over content | accept — stood down where it repeats |

*v1's panel (route band as a second hero; barn red as a hairline; photo quality vs CMC's film)
still holds and is not repeated.*
