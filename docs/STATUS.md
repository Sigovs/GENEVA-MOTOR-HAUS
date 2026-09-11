# Geneva Motor Haus — status (handoff)

Last updated 2026-09-10 (end of day). Preview: https://sigovs.github.io/GENEVA-MOTOR-HAUS/

## Where it stands
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
