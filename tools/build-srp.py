#!/usr/bin/env python3
"""Geneva Motor Haus — build srp.html from assets/data/inventory-2026-09-14.json.

The page is generated: rerun with --force after changing the data or this
template (the flag stops an accidental overwrite of experiments made in the
page itself). The lot card lives in tools/gmh_cards.py, shared with the VDPs.

The header, the menu and the footer are lifted from index_finale_v2.html at
build time; inventory routes and the search forms point at srp.html.

MEASURES are CMC's SRP, read off the live preview on 2026-09-14
(sigovs.github.io/AAN_PPREVIEW_CHICAGOMOTORCARS/srp.html): the 1700 measure
with a 3.4vw gutter, the 72px marque tiles, the filter block's 32px rhythm,
40px triggers, the 248×42 search, the 296×40 sort, the 3-column grid on
a 2.2vw gap, and the card. The language — ground, faces, plates, pills,
radii — is Geneva's.

    python3 tools/build-srp.py --force
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gmh_cards import ARROW, body_label, card, e  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets/data/inventory-2026-09-14.json"
HOME = ROOT / "index_finale_v2.html"
OUT = ROOT / "srp.html"
LIVE_INVENTORY = "https://www.genevamotorhaus.com/inventory"

if OUT.exists() and "--force" not in sys.argv:
    sys.exit("srp.html exists — rerun with --force to regenerate it.")

V = json.loads(DATA.read_text())["vehicles"]
home = HOME.read_text()

GLASS = ('<svg width="16" height="16" viewBox="0 0 17 17" fill="none" aria-hidden="true">'
         '<circle cx="7.2" cy="7.2" r="5.4" stroke="currentColor" stroke-width="1.4"/>'
         '<path d="m11.4 11.4 3.8 3.8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>')


def between(text, start, end, include_end=True):
    a = text.index(start)
    b = text.index(end, a) + (len(end) if include_end else 0)
    return text[a:b]


chrome_top = between(home, '<span class="scroll-sentinel"', "<main>", include_end=False).replace(LIVE_INVENTORY, "srp.html")
chrome_top = re.sub(r'<a href="srp\.html">Inventory</a>', '<a href="srp.html" aria-current="page">Inventory</a>', chrome_top)
footer = between(home, "<footer", "</footer>").replace(LIVE_INVENTORY, "srp.html")

WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
         "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def in_words(n):
    if n < 20:
        return WORDS[n]
    t, u = divmod(n, 10)
    return TENS[t] + ("-" + WORDS[u] if u else "")


YEAR_BANDS = [("2010 and newer", 2010, 9999), ("2000 – 2009", 2000, 2009), ("1990 – 1999", 1990, 1999), ("Before 1990", 0, 1989)]
PRICE_BANDS = [("Under $15,000", 0, 14999), ("$15,000 – $30,000", 15000, 29999), ("$30,000 – $60,000", 30000, 59999), ("$60,000 and above", 60000, 99999999)]
MILES_BANDS = [("Under 30,000 mi", 0, 29999), ("30,000 – 60,000 mi", 30000, 59999), ("60,000 – 100,000 mi", 60000, 99999), ("100,000 mi and over", 100000, 99999999)]


def opt(name, value, label, n):
    return (f'            <label class="srp-opt"><input type="checkbox" name="{name}" value="{e(str(value))}">'
            f'<span class="srp-opt__name">{e(label)}</span><span class="srp-opt__n">{n}</span></label>')


def band_options(name, bands, field):
    rows = []
    for label, lo, hi in bands:
        n = sum(1 for v in V if lo <= v[field] <= hi)
        if n:  # an option that finds nothing is not offered (CP7)
            rows.append(opt(name, f"{lo}-{hi}", label, n))
    return "\n".join(rows)


def counted(values):
    c = {}
    for x in values:
        if x:
            c[x] = c.get(x, 0) + 1
    return sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))


makes = counted(v["make"] for v in V)
bodies = counted(body_label(v.get("body")) for v in V)
make_opts = "\n".join(opt("make", m, m, n) for m, n in makes)
body_opts = "\n".join(opt("body", b, b, n) for b, n in bodies)
make_tiles = "\n".join(
    f'        <li><button class="srp-make" type="button" data-make="{e(m)}" aria-pressed="false">{e(m)}<span>{n}</span></button></li>'
    for m, n in makes)


def facet(fid, title, options):
    return f"""          <details class="srp-facet" id="{fid}">
            <summary class="srp-facet__trigger">{title}<span class="srp-facet__n" hidden></span></summary>
            <div class="srp-facet__panel">
              <fieldset class="srp-opts"><legend class="u-visually-hidden">{title}</legend>
{options}
              </fieldset>
              <button class="srp-facet__clear" type="button">Clear</button>
            </div>
          </details>"""


cards = "\n".join(card(v, index=i) for i, v in enumerate(V))
count = len(V)

page = f"""<!doctype html>
<!-- ============================================================
     GENEVA MOTOR HAUS — inventory results (SRP)
     ============================================================
     GENERATED by tools/build-srp.py (--force) from
     assets/data/inventory-2026-09-14.json; the card is tools/gmh_cards.py.

     CMC's SRP gives the MEANING and the MEASURES (read off its live preview,
     2026-09-14): how many; the marques as the make filter said shorter; the
     filters in one row that count; the results read back as chips; the
     whole card as the link. The LANGUAGE is the finale page's.

     THE DATA is genevamotorhaus.com rendered and read on 14 Sep 2026 —
     every price and mileage in docs/content-ledger-srp.json, the capture
     date beside the count (CP5). Only fields the listings carry are filtered
     on: make, body (17 of 23 cards name one), year, price, mileage (CP7).
     Three cars have no photograph (gone from the dealer's server); no other
     car's picture stands in.
     ============================================================ -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Inventory — Geneva Motor Haus · Burlington, WI</title>
<meta name="description" content="{count} pre-owned cars at Geneva Motor Haus in Burlington, Wisconsin — search by make, body, year, price and mileage.">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400..700;1,400..700&family=Zilla+Slab:wght@500;600;700&display=swap" rel="stylesheet">

<link rel="icon" href="assets/logos/gmh-icon-64.png" type="image/png">
<link rel="apple-touch-icon" href="assets/logos/gmh-icon-180.png">

<link rel="stylesheet" href="assets/css/tokens.css?v=4">
<link rel="stylesheet" href="assets/css/main.css?v=3">
<link rel="stylesheet" href="assets/css/v2.css?v=3">
<link rel="stylesheet" href="assets/css/v3.css?v=3">
<link rel="stylesheet" href="assets/css/geneva-final-v2.css?v=21">
<link rel="stylesheet" href="assets/css/srp-v2.css?v=9">
</head>
<body class="v2 is-v3 is-gmh is-srp">

{chrome_top}<main>
  <!-- 1 — THE HEAD: how many, and the marques as the make filter said shorter -->
  <section class="srp-head" data-reveal aria-labelledby="srp-title">
    <div class="shell">
      <p class="micro srp-head__eyebrow rv-eyebrow">Inventory</p>
      <h1 class="srp-head__title" id="srp-title"><span class="ttl-line">{in_words(count).capitalize()} cars,</span> <span class="ttl-line">hand-selected in Burlington.</span></h1>
      <div class="srp-makes-wrap">
        <p class="srp-makes__title rv-lede" id="srp-makes-title">Popular makes</p>
        <ul class="srp-makes rv-stagger" style="--rv-from: 3" aria-labelledby="srp-makes-title">
{make_tiles}
        </ul>
      </div>
    </div>
  </section>

  <!-- 2 — THE FILTERS: one row that counts. One set of inputs: the marque
       tiles, the chips and the phone's sheet all read these checkboxes. -->
  <section class="srp-tools" id="srp-tools" data-reveal aria-label="Refine results">
    <div class="shell">
      <div class="srp-tools__box rv-lede">
        <p class="micro srp-tools__eyebrow">Search the inventory</p>
        <div class="srp-tools__row">
          <button class="srp-filters-open" type="button" aria-expanded="false" aria-controls="srp-facets">Filters <span class="srp-filters-open__n" hidden></span></button>
          <div class="srp-facets" id="srp-facets">
            <div class="srp-sheet__head">
              <p class="srp-sheet__title">Filters</p>
              <button class="srp-sheet__close" type="button" aria-label="Close filters"><svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="m1 1 12 12M13 1 1 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button>
            </div>
{facet("f-make", "Make", make_opts)}
{facet("f-body", "Body", body_opts)}
{facet("f-year", "Year", band_options("year", YEAR_BANDS, "year"))}
{facet("f-price", "Price", band_options("price", PRICE_BANDS, "price"))}
{facet("f-miles", "Mileage", band_options("miles", MILES_BANDS, "mileage"))}
            <div class="srp-sheet__foot">
              <button class="srp-sheet__reset" type="button">Reset</button>
              <button class="btn btn--accent srp-sheet__show" type="button">Show <b data-srp-count>{count}</b> cars</button>
            </div>
          </div>
          <form class="srp-search" role="search" action="srp.html" method="get">
            <label class="u-visually-hidden" for="srp-q">Search year, make or model</label>
            {GLASS}
            <input id="srp-q" name="q" type="search" placeholder="Search year, make, model" autocomplete="off">
          </form>
          <p class="srp-count" aria-live="polite"><b data-srp-count>{count}</b> of {count} <span class="srp-dated">· as listed 14&#160;Sep&#160;2026</span></p>
          <label class="srp-sort"><span>Sort:</span>
            <select id="srp-sort" name="sort">
              <option value="listed">As listed</option>
              <option value="price-asc">Price low to high</option>
              <option value="price-desc">Price high to low</option>
              <option value="year-desc">Year newest first</option>
              <option value="year-asc">Year oldest first</option>
              <option value="miles-asc">Mileage low to high</option>
            </select>
          </label>
        </div>
        <div class="srp-chips" id="srp-chips" hidden>
          <ul class="srp-chips__row" aria-label="Active filters"></ul>
          <button class="srp-chips__clear" type="button">Clear all</button>
        </div>
      </div>
    </div>
  </section>

  <!-- 3 — THE LOT: the whole card is the link to the car's own page -->
  <section class="srp-results" id="inventory" aria-label="Results">
    <div class="shell">
      <ul class="srp-grid" id="srp-grid">
{cards}
      </ul>
      <div class="srp-empty" id="srp-empty" hidden>
        <p class="srp-empty__t">No cars match these filters.</p>
        <button class="btn btn--line srp-empty__clear" type="button">Clear filters {ARROW}</button>
      </div>
    </div>
  </section>
</main>

<!-- The floating "Sell your car" pill is not carried onto this page: over a grid
     of cars it covers photographs (U10), and Sell your car is in the header. -->
{footer}


<script src="assets/js/main-final-v2.js?v=2" defer></script>
<script src="assets/js/geneva-final-v2.js?v=2" defer></script>
<script src="assets/js/srp-v2.js?v=3" defer></script>
</body>
</html>
"""
OUT.write_text(page)
print(f"wrote {OUT.name}: {count} cars, {len(makes)} makes, {len(bodies)} bodies, {OUT.stat().st_size // 1024} KB")
