# Geneva Motor Haus — status (handoff)

Last updated 2026-09-11. Preview: https://sigovs.github.io/GENEVA-MOTOR-HAUS/

## FINALE v2 — `index_finale_v2.html` (2026-09-11) — Alex's working copy ("finale 3")
- A clone of `index_finale.html` with its own `assets/css/geneva-final-v2.css`, `assets/js/main-final-v2.js`
  and `assets/js/geneva-final-v2.js`. `index_finale.html` stays as the reference; the shared base
  (tokens / main / v2 / v3) and the images are unchanged.
- Palette (Alex): the ground is **#151414**, not the brown #15100C. The dark family is re-derived in `:root`
  of geneva-final-v2.css (F21). tokens.css is untouched, so index / index_finale keep the brown.
- Featured = Figma 46:829 (F20): the index2 catalogue. On the left, the photo and a bar (counter, arrows,
  View all). On the right, the plate and the index of eight. The panels are bone (`--fi-panel`; Figma
  drew #C9C9C9). Two fixes to the frame: the dimmed rows were raised to AA, and all eight rows are shown
  where Figma clipped the eighth.
- Sell = Figma 46:828 (F19): a stepped bone card on the dark with air on the sides, the showroom
  render and the four step plates inside it.
  - The step follows Alex's reference: a 49° fall with 32u fillets; every corner is 32u.
  - The step drifts ±3% with scroll, on desktop only and not under reduced motion.
  - The top of the card is feathered where it rides over the pinned Shipping.
- The haus image is now a BMW M4 render (`passion-m4.jpg`).
- Two visual breaks (F23): day after the tiles, dusk after Warranty. Their stand-in copy makes no new claims.
- The main navigation has pill hovers (F22).
- The supplied renders are not photographs and carry no captions: sell-showroom, passion-m4, break-day
  and break-dusk. The sources are in `assets/finale 3/`.
- Eyebrows (F24): every eyebrow over a heading is the same plate — #1B2926, 22px tall, the label at
  14px uppercase with equal air either side; the plate is the label's own width. Sixteen of them: hero, the four tile kickers, the haus eyebrow and its four
  kickers, Shipping, Warranty, Reviews, the newsletter's, the two breaks. The ruled running heads, the
  footer's column heads and the e-mail label are not eyebrows and keep their own form.
- Removed at Alex's word (2026-09-11): the Featured date line ("Prices and mileage as listed on
  10 Sep 2026") and the haus foot line (600 Faust Rd / Nationwide transportation available).
  KNOWN COMPROMISE with CP5: the Featured prices are now undated on screen, and they were read from
  the live site on 10 Sep 2026. Before launch, feed them live or date them again. The haus line
  "23 vehicles in stock, $9,000 to $170,000 — as listed on 10 Sep 2026" still carries its date.
- Waiting for Alex: the step-plate hover (a throwaway `_preview-sell-motion.html`, local only), and
  whether the plates become links to /sell-your-car.
- Live: https://sigovs.github.io/GENEVA-MOTOR-HAUS/index_finale_v2.html

## FINAL — `index_finale.html` (2026-09-11, committed 338e509) — the reference for finale v2
- A copy of v2 (`index.html`) refined, not redesigned. Isolated assets: `assets/css/geneva-final.css`
  (fork of geneva.css), `assets/js/main-final.js` (fork of main.js, one selector), `assets/js/geneva-final.js`.
  `index.html` / `index2.html` and their assets are untouched.
- Header `.gf-head`: centred badge (116px) as the anchor before the scroll, search + 3 routes left,
  3 routes + phone right; past 96px it settles to a 72px solid bar with a 50px badge — same objects,
  same line. CMC's glass rail, `nav-glass` filter and the read-position bar are gone.
- Hero type: enters from below on load (32px, 760ms, 90ms stagger), leaves on the scroll by
  view-timeline — the name opens outward, the place line rises out, the sentence and CTAs sink;
  "Burlington, Wisconsin" leaves with the rest. JS fallback where scroll timelines are unsupported;
  nothing moves under reduced motion.
- Featured inventory `.gf-cars`: a native scroll-snap carousel of eight cards, 4 · 2 · 1 in view,
  arrows in the gutters (disabled at the ends, no wrap), "View all inventory" centred under it.
- Sell steps: four cards (4 · 2 · 1). Contact/Location section replaced by the full-width Google
  embed (`#contact`) and a four-column footer (badge · showroom · routes · hours) + legal row.
- No persistent underlines anywhere; the floating Sell pill also stands down over the carousel.
- Final pass (2026-09-11): one grid (`--page-max` 1240 / `--page-gutter`), every content block on it;
  vertical scale `--sec` / `--sec-lg`; hero type rises and fades as one group on the scroll; Shipping is a
  sticky chapter (pinned with its foot on the window's foot, `--ship-h` from geneva-final.js) that Sell rides
  over; Shipping title slides in from the side, Sell title lines from opposite sides; the four tiles are plates
  with numerals; the haus chapter is image-led (supplied render `passion.jpg`, declared non-photographic) with
  the four answers in two columns of air. The map's six destinations are ILLUSTRATIVE (Alex: "simulate") —
  confirm with the client or replace before launch.
- Live: https://sigovs.github.io/GENEVA-MOTOR-HAUS/index_finale.html · local `python -m http.server 8765`

## v3 — Geneva's own art direction — `index2.html` (2026-09-11, uncommitted, first two screens only)
- Brief (Alex): v2 read as CMC with Geneva colours. Not a polish pass — a new art direction:
  contemporary European collector-car showroom + automotive editorial + small specialist dealer.
- Lives beside v2, not over it: `index2.html` + `assets/css/tokens-v3.css` + `assets/css/geneva-v3.css`
  + `assets/js/geneva.js`. `index.html`, `tokens.css` and `geneva.css` are the v2 page, untouched.
  `main-v3.js` is a fork of main.js with the three v3 edits; `main.js` is untouched.
- Redesigned: the global system (tokens), the header, the hero, the featured inventory. The lower
  sections are v2, re-toned by the tokens only, and wait on approval of these two screens.
- System: charcoal `#151414` / ivory `#F1ECE3` / oxblood `#6F1D26` (+ `--accent-lit #B03A43` as
  the only red mark allowed on the dark ground) / umber `#2A2220` as the supporting brown.
  Instrument Sans is the voice; Zilla Slab keeps ONE role — the year numerals in the catalogue.
  Controls are 52px rectangles (2px corners), no pills.
- Header `.gmh-head`: full-width masthead on the ground, sticky, badge 68px, six routes, search as
  a hairline field, the phone as text; under 1200 the routes and field move into the menu.
- Hero `.gmh-hero`: the lot photograph edge to edge, copy bottom-left, caption bottom-right.
  Their own line as the headline. Phone: photo (scaled from its top-right) then type on the ground.
- Catalogue `.gmh-cat`: one photograph bleeding to the left edge, a lot plate (year in the slab,
  marque/model, price · mileage, See details), an index of the eight. `assets/js/geneva.js`
  drives it; main.js's stage and hero IIFEs return early (their selectors are gone).
- The floating Sell pill now also stands down over `#inventory` (it covered the index).
- Known: the gable (15e) and the v2 lower-page rules are still in geneva-v3.css from section 4 on.
  When the system propagates, the gable is the first barn signal to go.
- Preview: `python -m http.server 8765` in the project folder → http://127.0.0.1:8765/index2.html
  (v2 stays at /index.html).

## Where it stands (v2)
- **Homepage v2** is built on the live site's skeleton (genevamotorhaus.com sections, in its order)
  and executed in the CMC index_3 language. It is not 1:1 CMC, per Alex.
- Decisions made by Alex:
  - display face **Zilla Slab**;
  - Financing / About are **tiles only**;
  - the shipping map move is "the reach" (plays once; scroll-drawn rings were rejected);
  - no placeholders — nothing further expected from the client.
- Reasoning: `docs/DESIGN-READ.md`. Facts and the verbatim ticket: `docs/DISCOVERY.md`.
  Every claim's source: `docs/content-ledger.json`.

## Gates (design_dna `npm run gates -- <this folder>`)
- Pass (machine): Gate 1 (A1 desktop 100%, mobile 91.4%), composition, hero (both viewports),
  content ledger (118 claims, 0 uncovered), vault.
- Waiting for Alex (human only — never filled by the builder):
  - hero `humanConfirmed`;
  - Gate 2 section inventory and the 12 detector dispositions;
  - authorship fields for the operations;
  - the nine Gate 3 product questions.

## Open choices
- The contact map loads on click (door-photo facade). It can load immediately, as on the live site
  (one change).
- Not carried from the live site: the sticky address bar, and the marquee (superlatives).
- The template claims on the live site are left out until the client confirms them:
  "over 12 years", "thousands of satisfied customers", "maintenance programs".

## Working notes
- Bump `?v=N` on every CSS/JS edit (index.html), or browsers serve the cached file.
- Geneva rules live only in `assets/css/geneva.css` (§15 = the departures from CMC), all under `.is-gmh`.
- Local only, not in the repo: `assets/img/source/` (harvested originals), `from client/`.
