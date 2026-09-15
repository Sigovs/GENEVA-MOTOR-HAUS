#!/usr/bin/env python3
"""Geneva Motor Haus — build cars/<slug>.html, one vehicle detail page per car,
from assets/data/inventory-2026-09-14.json.

These are DATA pages: 23 of them, identical in form, so the generator owns
them and regenerates all of them on every run. Edit this template,
assets/css/vdp-v2.css or assets/js/vdp-v2.js — never the pages.

MEASURES are CMC's VDP, read off its live preview on 2026-09-14
(sigovs.github.io/AAN_PPREVIEW_CHICAGOMOTORCARS/vdp.html): the 1700 measure,
the 60/40 summary whose photograph takes the panel's height, 6 thumbnails on
12, the panel's 24px sections and 35px rows, the full-width action bar,
96px disclosure cards on 16, the four-card standards row, the photographs
at size on 24, six related cards in a paging track. The language is Geneva's.

    python3 tools/build-vdp.py
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gmh_cards import ARROW, body_label, card, e, spec_line, tidy, trans  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets/data/inventory-2026-09-14.json"
HOME = ROOT / "index_finale_v2.html"
OUTDIR = ROOT / "cars"
OUTDIR.mkdir(exist_ok=True)

CAPTURED_HUMAN = "14&#160;Sep&#160;2026"
PHONE, PHONE_HREF, EMAIL = "(262) 249-6777", "tel:+12622496777", "Info@GenevaMotorHaus.com"
ADDRESS = "600 Faust Rd, Unit 8, Burlington, WI 53105"
DIRECTIONS = "https://www.google.com/maps/dir/?api=1&amp;destination=600+Faust+Rd+Unit+8%2C+Burlington%2C+WI+53105"
FINANCING = "https://www.genevamotorhaus.com/financing"

# Every sentence is a verified Geneva claim (docs/content-ledger.json ids in brackets).
STANDARDS = [
    ("Hand-selected", "Each vehicle in our inventory is hand-selected in Burlington, Wisconsin.", None),          # hand-selected
    ("Reputation", "We stand behind every vehicle we sell.", None),                                                 # reputation-stand-behind
    ("Warranty", "Warranty options are available on the vehicles we sell.", ("Ask about warranty", "#ask")),        # warranty-offered
    ("Nationwide transportation", "Half our cars leave Wisconsin, and transportation is available nationwide.", ("Shipping", "#shipping")),  # half-out-of-state, nationwide-transport
]

V = json.loads(DATA.read_text())["vehicles"]
home = HOME.read_text()

CHEV_L = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M14.5 5.5 8 12l6.5 6.5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
CHEV_R = '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M9.5 5.5 16 12l-6.5 6.5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'
SAVE = '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M4 2.5h8v11L8 10.6 4 13.5z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>'
SHARE = '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M6.5 9.5 9.5 6.5M7 4.5l1.3-1.3a2.8 2.8 0 0 1 4 4L11 8.5M9 11.5l-1.3 1.3a2.8 2.8 0 0 1-4-4L5 7.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>'
PHONE_ICON = '<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true"><rect x="4.5" y="1.5" width="7" height="13" rx="1.6" stroke="currentColor" stroke-width="1.4"/><path d="M7 12h2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>'


# ---- the shared chrome, re-rooted one folder up ------------------------------
def between(text, start, end, include_end=True):
    a = text.index(start)
    b = text.index(end, a) + (len(end) if include_end else 0)
    return text[a:b]


def reroot(fragment):
    return re.sub(r'\b(href|src|action)="(?!(?:https?:|tel:|mailto:|sms:|#|//|data:))([^"]+)"', r'\1="../\2"', fragment)


chrome_top = reroot(between(home, '<span class="scroll-sentinel"', "<main>", include_end=False))
chrome_top = chrome_top.replace('<a href="../srp.html">Inventory</a>', '<a href="../srp.html" aria-current="page">Inventory</a>')
footer = reroot(between(home, "<footer", "</footer>"))


# ---- formatting -----------------------------------------------------------------
def engine(v):
    if not v:
        return None
    return v + "L" if re.fullmatch(r"\d\.\d", v.strip()) else tidy(v)


def unit(v, u):
    if not v:
        return None
    return f"{v} {u}" if re.fullmatch(r"[\d,.]+", v.strip()) else v


def is_shouting_list(line):
    letters = [c for c in line if c.isalpha()]
    return len(letters) > 12 and sum(c.isupper() for c in letters) / len(letters) > 0.85 and re.search(r"[-•]", line)


def points_from(line):
    out = []
    for p in re.split(r"\s*[-•]\s+|-\s*$|\s-\s", line):
        p = p.strip(" -•–—").strip()
        if len(p) >= 3:
            t = tidy(p)
            out.append(t[:1].upper() + t[1:])
    return out


def related(v):
    """Same marque first, then the nearest prices — never this car, never at random."""
    others = [o for o in V if o["slug"] != v["slug"]]
    others.sort(key=lambda o: (o["make"] != v["make"], abs(o["price"] - v["price"])))
    return others[:6]


def acc(aid, title, body, open_=False):
    return f"""      <details class="vdp-acc" id="{aid}"{" open" if open_ else ""}>
        <summary class="vdp-acc__sum"><span class="vdp-acc__label">{title}</span><span class="vdp-acc__mark" aria-hidden="true"></span></summary>
        <div class="vdp-acc__body">
{body}
        </div>
      </details>"""


# ---- one page ---------------------------------------------------------------------
def page(v):
    name = f"{v['year']} {v['make']} {v['model']}"
    price, miles = f"${v['price']:,}", f"{v['mileage']:,} mi"
    specs = v.get("specs") or {}
    photos = v.get("photos") or []
    n = len(photos)

    # the gallery
    if n:
        frames = []
        for k, p in enumerate(photos):
            attrs = 'fetchpriority="high"' if k == 0 else 'loading="lazy"'
            cls = "vdp-gal__frame" + (" is-active" if k == 0 else "") + (" is-portrait" if p["h"] > p["w"] else "")
            frames.append(f'        <img class="{cls}" src="../{p["src"]}" alt="{e(name)}, photograph {k + 1} of {n}" width="{p["w"]}" height="{p["h"]}" {attrs} decoding="async">')
        controls, strip = "", ""
        if n > 1:
            controls = (f'\n        <button class="vdp-gal__arrow vdp-gal__arrow--prev" type="button" data-step="-1" aria-label="Previous photograph">{CHEV_L}</button>'
                        f'\n        <button class="vdp-gal__arrow vdp-gal__arrow--next" type="button" data-step="1" aria-label="Next photograph">{CHEV_R}</button>'
                        f'\n        <p class="vdp-gal__count" aria-hidden="true"><b data-gal-at>1</b> / {n}</p>')
            thumbs = []
            for k, p in enumerate(photos):
                lazy = 'loading="lazy" ' if k > 5 else ""
                thumbs.append(f'        <li><button class="vdp-gal__thumb" type="button" aria-label="Photograph {k + 1} of {n}" aria-current="{"true" if k == 0 else "false"}"><img src="../{p["sm"]}" alt="" {lazy}decoding="async"></button></li>')
            strip = '\n      <ul class="vdp-gal__strip" aria-label="Photographs">\n' + "\n".join(thumbs) + "\n      </ul>"
        gallery = f"""    <div class="vdp-gal rv-self rv-photo" data-gallery data-reveal>
      <div class="vdp-gal__stage" tabindex="0" role="group" aria-roledescription="gallery" aria-label="Photographs of the {e(name)}">
{chr(10).join(frames)}{controls}
      </div>{strip}
    </div>"""
        preload = f'<link rel="preload" as="image" href="../{photos[0]["src"]}" fetchpriority="high">'
    else:
        gallery = f"""    <div class="vdp-gal vdp-gal--none rv-self rv-photo" data-reveal>
      <div class="vdp-gal__stage"><p class="vdp-gal__none"><span>No photograph available</span><a class="vdp-gal__ask" href="#ask">Ask for photographs {ARROW}</a></p></div>
    </div>"""
        preload = ""

    # the panel's rows — only what the listing carries, in the order a buyer reads
    rows = [("Mileage", miles), ("Engine", engine(specs.get("ENGINE"))), ("Horsepower", unit(specs.get("HORSEPOWER"), "hp")),
            ("Torque", unit(specs.get("TORQUE"), "lb-ft")), ("Transmission", trans(v.get("transmission"))),
            ("Exterior", tidy(v.get("exterior"))), ("Interior", tidy(v.get("interior"))), ("Body", body_label(v.get("body"))),
            ("VIN", specs.get("VIN"))]
    rows_html = "\n".join(f'          <div class="vdp-spec"><dt>{k}</dt><dd>{e(val)}</dd></div>' for k, val in rows if val)

    # the record
    prose, points = [], []
    for line in v.get("overview") or []:
        (points.extend(points_from(line)) if is_shouting_list(line) else prose.append(line))
    about = ""
    if prose or points:
        lead = spec_line(v)
        parts = []
        if lead:
            parts.append(f'          <p class="vdp-about__lead">{e(lead)}</p>')
        parts += [f"          <p>{e(p)}</p>" for p in prose]
        if points:
            parts.append('          <ul class="vdp-about__points">' + "".join(f"<li>{e(p)}</li>" for p in points) + "</ul>")
        parts.append(f'          <p class="vdp-acc__note">As listed by Geneva Motor Haus on {CAPTURED_HUMAN}.</p>')
        about = acc("about", "About this car", "\n".join(parts), open_=True) + "\n"

    vin = specs.get("VIN")
    # the history report, under the rows: the CARFAX mark and one link, only
    # where the listing carries a VIN. WIRING: the report address is the
    # public VIN form; AAN puts Geneva's own CARFAX partner code in `partner`.
    carfax = (
        '      <a class="vdp-carfax" href="https://www.carfax.com/VehicleHistory/p/Report.cfx?partner=DVW_1&amp;vin=' + e(vin) + '" target="_blank" rel="noopener">\n'
        '        <img src="../assets/logos/carfax.svg" alt="CARFAX" width="253" height="60">\n'
        '        <span>See report ' + ARROW + '</span>\n'
        '      </a>'
    ) if vin else ""
    message = f"I'm interested in the {name}" + (f" (VIN {vin})" if vin else "") + "."
    ask_body = f"""          <form class="vdp-form vdp-ask" novalidate>
            <input type="hidden" name="vehicle" value="{e(name)}">{f'<input type="hidden" name="vin" value="{e(vin)}">' if vin else ''}
            <label class="vdp-field"><span>First name</span><input name="fname" autocomplete="given-name" required></label>
            <label class="vdp-field"><span>Last name</span><input name="lname" autocomplete="family-name" required></label>
            <label class="vdp-field"><span>Email</span><input name="email" type="email" autocomplete="email" required></label>
            <label class="vdp-field"><span>Phone</span><input name="phone" type="tel" autocomplete="tel"></label>
            <fieldset class="vdp-field vdp-field--wide vdp-when"><legend>Best time to reach you</legend>
              <label><input type="radio" name="when" value="morning" checked><span>Morning</span></label>
              <label><input type="radio" name="when" value="afternoon"><span>Afternoon</span></label>
              <label><input type="radio" name="when" value="evening"><span>Evening</span></label>
            </fieldset>
            <label class="vdp-field vdp-field--wide"><span>Message</span><textarea name="message">{e(message)}</textarea></label>
            <div class="vdp-form__foot"><button class="btn btn--accent" type="submit">Send message {ARROW}</button></div>
          </form>
          <div class="vdp-sent" hidden tabindex="-1">
            <p class="vdp-sent__t">Thanks<span data-sent-name></span>.</p>
            <p class="vdp-sent__p">This preview doesn’t send messages. To reach Geneva Motor Haus about the {e(name)}, call <a href="{PHONE_HREF}">{PHONE}</a>.</p>
          </div>"""
    finance_body = f"""          <form class="vdp-form vdp-calc" data-price="{v['price']}">
            <label class="vdp-field"><span>Price</span><input name="price" value="{price}" readonly></label>
            <label class="vdp-field"><span>Down payment</span><input name="down" inputmode="numeric" placeholder="$0"></label>
            <label class="vdp-field"><span>Term</span><select name="term"><option value="36">36 months</option><option value="48">48 months</option><option value="60" selected>60 months</option><option value="72">72 months</option><option value="84">84 months</option></select></label>
            <label class="vdp-field"><span>Your rate (APR %)</span><input name="apr" inputmode="decimal" placeholder="Your rate"></label>
            <div class="vdp-form__foot">
              <output class="vdp-calc__out" aria-live="polite">Enter a rate</output>
              <a class="btn btn--line" href="../finance.html?car={v['slug']}#apply">Apply for financing {ARROW}</a>
            </div>
            <p class="vdp-acc__note vdp-field--wide">An estimate from your own numbers, not an offer. Tax, title and registration are not included.</p>
          </form>"""
    shipping_body = f"""          <p>Nationwide transportation available. Half our cars leave Wisconsin. Out-of-state buyers ask for photographs from every angle and the inspections they want — we send those first, then the car, by carrier.</p>
          <a class="btn btn--line" href="#ask">Ask about shipping {ARROW}</a>"""

    standards = "\n".join(
        f'        <li class="vdp-stds__item"><p class="vdp-stds__k">{k}</p><p class="vdp-stds__v">{val}</p>'
        + (f'<a class="vdp-stds__link" href="{link[1]}">{link[0]} {ARROW}</a>' if link else "") + "</li>"
        for k, val, link in STANDARDS)

    sheet = ""
    if n >= 2:
        shots = "\n".join(f'        <li class="rv-self rv-photo" data-reveal><a href="../{p["src"]}" target="_blank" rel="noopener"><img src="../{p["sm"]}" alt="{e(name)}, photograph {k + 1}" loading="lazy" decoding="async"></a></li>' for k, p in enumerate(photos))
        more = ""
        if v.get("photosOnListing", 0) > n:
            more = f'\n      <p class="vdp-sheet__more"><a href="{v["url"]}">All {v["photosOnListing"]} photographs on the listing {ARROW}</a></p>'
        sheet = f"""  <section class="shell vdp-sheet" data-reveal aria-labelledby="vdp-photos-title">
      <h2 class="vdp-h2" id="vdp-photos-title"><span class="ttl-line">Photographs</span></h2>
      <ul class="vdp-shots">
{shots}
      </ul>{more}
  </section>
"""

    rel = "\n".join(card(o, img_prefix="../", href_prefix="", data=False, indent="        ") for o in related(v))

    return f"""<!doctype html>
<!-- ============================================================
     GENEVA MOTOR HAUS — vehicle detail page: {e(name)}
     ============================================================
     GENERATED by tools/build-vdp.py from assets/data/inventory-2026-09-14.json.
     Edit the template or vdp-v2.css / vdp-v2.js, not this file.

     Every figure and every sentence about the car is the dealer's own
     listing ({v['url']}), rendered and read on 14 Sep 2026
     (docs/source/site-live-2026-09-14.json; ledger docs/content-ledger-vdp.json).
     Their Specifications and Features tabs are empty, so the panel shows
     only the fields the listing carries. Photographs: {n} held locally of
     {v.get('photosOnListing', 0)} on the listing, in the listing's order.
     ============================================================ -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)} — Geneva Motor Haus · Burlington, WI</title>
<meta name="description" content="{e(name)}: {price}, {miles}, at Geneva Motor Haus in Burlington, Wisconsin.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400..700;1,400..700&family=Zilla+Slab:wght@500;600;700&display=swap" rel="stylesheet">
{preload}
<link rel="icon" href="../assets/logos/gmh-icon-64.png" type="image/png">
<link rel="apple-touch-icon" href="../assets/logos/gmh-icon-180.png">
<link rel="stylesheet" href="../assets/css/tokens.css?v=4">
<link rel="stylesheet" href="../assets/css/main.css?v=3">
<link rel="stylesheet" href="../assets/css/v2.css?v=3">
<link rel="stylesheet" href="../assets/css/v3.css?v=3">
<link rel="stylesheet" href="../assets/css/geneva-final-v2.css?v=21">
<link rel="stylesheet" href="../assets/css/srp-v2.css?v=9">
<link rel="stylesheet" href="../assets/css/vdp-v2.css?v=6">
</head>
<body class="v2 is-v3 is-gmh is-srp is-vdp">

{chrome_top}<main>
  <p class="u-visually-hidden" id="vdp-live" aria-live="polite"></p>

  <div class="shell vdp-top rv-self" data-reveal>
    <nav class="vdp-crumbs" aria-label="Breadcrumb">
      <ol><li><a href="../index_finale_v2.html">Home</a></li><li><a href="../srp.html">Inventory</a></li><li aria-current="page">{e(name)}</li></ol>
    </nav>
    <div class="vdp-tools">
      <button class="vdp-tool" type="button" data-save="{v['slug']}" aria-pressed="false">{SAVE}<span>Save</span></button>
      <button class="vdp-tool" type="button" data-share>{SHARE}<span>Share</span></button>
      <a class="vdp-tool" href="sms:" data-text-to-phone>{PHONE_ICON}<span>Text to phone</span></a>
    </div>
  </div>

  <!-- THE SUMMARY: the photograph and the decision, side by side, ending on
       one line — the photograph takes whatever height the panel makes -->
  <section class="shell vdp-sum" aria-labelledby="vdp-title">
{gallery}
    <aside class="vdp-panel rv-stagger" data-reveal style="--rv-from: 1">
      <div class="vdp-panel__head">
        <p class="micro vdp-plate__eyebrow">In stock</p>
        <h1 class="vdp-plate__title" id="vdp-title"><span class="vdp-plate__year">{v['year']}</span> <span class="vdp-plate__name"><span class="vdp-plate__make">{e(v['make'])}</span> <span class="vdp-plate__model">{e(v['model'])}</span></span></h1>
      </div>
      <div class="vdp-panel__price">
        <div class="vdp-price"><span class="vdp-price__k">Price</span><span class="vdp-price__v">{price}</span></div>
        <p class="vdp-price__dated">Price and mileage as listed on {CAPTURED_HUMAN}</p>
      </div>
      <dl class="vdp-panel__specs">
{rows_html}
      </dl>
{carfax}
      <div class="vdp-panel__act">
        <a class="btn btn--accent vdp-plate__cta" href="#ask">Ask about this car {ARROW}</a>
      </div>
    </aside>
  </section>

  <!-- THE WAYS IN: the showroom, and the ways to reach it — on the summary's
       own columns, so the buttons line up under the panel -->
  <section class="shell vdp-act rv-stagger" data-reveal style="--rv-from: 0" aria-label="Visit or contact">
    <div class="vdp-act__where">
      <p class="vdp-act__k">Showroom</p>
      <p class="vdp-act__v">{ADDRESS}</p>
      <a class="vdp-act__link" href="{DIRECTIONS}" rel="noopener">Get directions {ARROW}</a>
      <a class="vdp-act__pill" href="#shipping">Shipping</a>
    </div>
    <div class="vdp-act__contact">
      <a class="vdp-pill vdp-pill--accent" href="{PHONE_HREF}">{PHONE}</a>
      <a class="vdp-pill vdp-pill--bone" href="mailto:{EMAIL}?subject={e(name)}">Email dealer</a>
      <a class="vdp-pill vdp-pill--line" href="../finance.html?car={v['slug']}#apply">Get financing {ARROW}</a>
    </div>
  </section>

  <!-- THE RECORD: native disclosures — they work without script and
       find-in-page reaches a closed one -->
  <section class="shell vdp-record rv-stagger" data-reveal style="--rv-from: 0" aria-label="About this car">
{about}{acc("ask", "Ask about this car", ask_body)}
{acc("finance", "Estimate a payment", finance_body)}
{acc("shipping", "Shipping", shipping_body)}
  </section>

  <!-- WHAT COMES WITH BUYING HERE: the same on every page, and every line
       one of Geneva's own verified claims -->
  <section class="shell vdp-stds" data-reveal aria-labelledby="vdp-stds-title">
    <p class="micro vdp-stds__eyebrow rv-eyebrow">Buying from Geneva Motor Haus</p>
    <h2 class="vdp-stds__title" id="vdp-stds-title"><span class="ttl-line">From Burlington,</span> <span class="ttl-line">Wisconsin.</span></h2>
    <ul class="vdp-stds__grid rv-stagger" style="--rv-from: 1.6">
{standards}
    </ul>
  </section>

{sheet}  <section class="vdp-rel" data-reveal aria-labelledby="vdp-rel-title">
    <div class="shell">
      <h2 class="vdp-h2" id="vdp-rel-title"><span class="ttl-line">More from the lot</span></h2>
      <ul class="vdp-rel__track rv-lede" data-track>
{rel}
      </ul>
      <div class="vdp-rel__dots" data-dots aria-label="Pages"></div>
    </div>
  </section>
</main>

{footer}

<script src="../assets/js/main-final-v2.js?v=2" defer></script>
<script src="../assets/js/geneva-final-v2.js?v=2" defer></script>
<script src="../assets/js/vdp-v2.js?v=2" defer></script>
</body>
</html>
"""


for v in V:
    (OUTDIR / f"{v['slug']}.html").write_text(page(v))
print(f"wrote {len(V)} pages to cars/ — photos on {sum(1 for v in V if v.get('photos'))}, about-this-car on {sum(1 for v in V if v.get('overview'))}")
