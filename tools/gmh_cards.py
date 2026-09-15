"""Geneva Motor Haus — shared by tools/build-srp.py and tools/build-vdp.py.

The listing strings tidied (the dealer's feed arrives in shouting capitals),
and the ONE lot card both pages show: the SRP grid and the VDP's "More from
the lot" are the same component, so their sizes cannot drift apart.

The card's measures are CMC's SRP card, read off the live preview on
2026-09-14: 3:2 photograph, a 24px body of make (14) · name (17) · two
clamped lines (14) · pills (37) — 207px — and "See details" arriving over
the pills on hover. The language is Geneva's.
"""
import html
import re

e = html.escape

ARROW = ('<svg class="btn__arrow" width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">'
         '<path d="M2 6.5h9M7.4 3 11 6.5 7.4 10" stroke="currentColor" stroke-width="1.3"/></svg>')

SMALL = {"with", "over", "and", "of", "the", "a"}
KEEP = {"PDK", "AMG", "SVE", "XL", "V8", "V6", "V10", "V12", "SUV", "4WD", "AWD", "RWD", "FWD", "LED", "PPF", "PCM", "PASM", "PSM", "USA", "OEM"}


def tidy(s):
    """Set a shouting listing string as words, leaving codes in brackets and
    marks like PDK or AMG alone."""
    if not s:
        return None
    out = []
    for i, w in enumerate(s.split()):
        core = w.strip("().,:;")
        if w.startswith("(") or core in KEEP:
            out.append(w)
        elif w.isupper() or w.islower():
            lw = w.lower()
            out.append(lw if (i and lw in SMALL) else lw[:1].upper() + lw[1:])
        else:
            out.append(w)
    return " ".join(out).replace(" - ", " ")


TRANS = {"PDK": "PDK", "AUTO": "Automatic", "AUTOMATIC": "Automatic", "MANUAL": "Manual",
         "6 SPEED MANUAL": "6-speed manual", "8 SPEED AUTO": "8-speed automatic",
         "BORG WARNER 4 SPEED": "Borg-Warner 4-speed"}


def trans(v):
    return TRANS.get(v, tidy(v)) if v else None


def body_label(v):
    if not v:
        return None
    return "SUV" if v.lower() == "suv" else v.title()


def spec_line(v):
    ext, inte, tr = tidy(v.get("exterior")), tidy(v.get("interior")), trans(v.get("transmission"))
    parts = []
    if ext and inte:
        parts.append(f"{ext} over {inte}")
    elif ext or inte:
        parts.append(ext or inte)
    if tr:
        parts.append(tr)
    return " · ".join(parts)


# where the car sits in its own lead photograph, for the 3:2 frame
POS = {
    "bmw-330ci-2006": "50% 74%",
    "chrysler-town-country-touring-l-2012": "50% 72%",
    "ford-galaxie-1936-5": "50% 64%",
    "ford-galaxie-500-xl-hardtop-1963": "50% 64%",
    "porsche-911-carerra-4s-6-speed-1997": "50% 64%",
    "porsche-boxster-1999": "50% 56%",
}


def card(v, img_prefix="", href_prefix="cars/", index=99, data=True, indent="        ", sold=False):
    """One lot card. img_prefix / href_prefix re-root it for pages in cars/.
    sold=True: the SOLD tag on the photograph, no link (a sold car has no page
    to open), and a price or mileage only where the listing gives one."""
    if sold:
        return _sold_card(v, img_prefix, index, indent)
    name = f"{v['year']} {v['make']} {v['model']}"
    price, miles = f"${v['price']:,}", f"{v['mileage']:,} mi"
    body = body_label(v.get("body"))
    spec = spec_line(v)
    if v.get("img"):
        pos = POS.get(v["slug"])
        style = f' style="--pos: {pos}"' if pos else ""
        loading = 'fetchpriority="high"' if index < 3 else 'loading="lazy"'
        media = (f'<span class="srp-card__media"><img src="{img_prefix}{v["imgSm"]}" '
                 f'srcset="{img_prefix}{v["imgSm"]} 600w, {img_prefix}{v["img"]} 1000w" '
                 f'sizes="(max-width: 700px) calc(100vw - 48px), (max-width: 1080px) 48vw, 506px" '
                 f'alt="{e(name)}" width="{v["imgW"]}" height="{v["imgH"]}" {loading} decoding="async"{style}></span>')
    else:
        media = ('<span class="srp-card__media srp-card__media--none">'
                 '<span class="srp-card__nophoto">No photograph available</span></span>')
    attrs = ""
    if data:
        text = " ".join([str(v["year"]), v["make"], v["model"], v.get("titleAsListed", "")]).lower()
        attrs = (f' data-slug="{v["slug"]}" data-make="{e(v["make"])}" data-year="{v["year"]}" data-price="{v["price"]}"'
                 f' data-miles="{v["mileage"]}" data-body="{e(body or "")}" data-order="{v["order"]}" data-text="{e(text)}"')
    pills = f'<span class="srp-pill srp-pill--price">{price}</span><span class="srp-pill">{miles}</span>'
    if body:
        pills += f'<span class="srp-pill">{e(body)}</span>'
    spec_html = f'<span class="srp-card__spec">{e(spec)}</span>' if spec else '<span class="srp-card__spec" aria-hidden="true"></span>'
    i = indent
    return (f'{i}<li class="srp-card{" rv-self" if data else ""}"{attrs}{" data-reveal" if data else ""}>\n'
            f'{i}  <a class="srp-card__link" href="{href_prefix}{v["slug"]}.html" aria-label="{e(name)}, {price}, {miles}">\n'
            f'{i}    {media}\n'
            f'{i}    <span class="srp-card__body">\n'
            f'{i}      <span class="srp-card__make">{e(v["make"])}</span>\n'
            f'{i}      <span class="srp-card__name"><span class="srp-card__year">{v["year"]}</span> {e(v["model"])}</span>\n'
            f'{i}      {spec_html}\n'
            f'{i}      <span class="srp-card__pills">{pills}</span>\n'
            f'{i}      <span class="srp-card__go" aria-hidden="true">See details {ARROW}</span>\n'
            f'{i}    </span>\n'
            f'{i}  </a>\n'
            f'{i}</li>')


def _sold_card(v, img_prefix, index, indent):
    name = f"{v['year']} {v['make']} {v['model']}"
    miles = f"{v['mileage']:,} mi" if v.get("mileage") else None
    price = f"${v['price']:,}" if v.get("price") else None
    if v.get("img"):
        loading = 'fetchpriority="high"' if index < 3 else 'loading="lazy"'
        media_img = (f'<img src="{img_prefix}{v["imgSm"]}" srcset="{img_prefix}{v["imgSm"]} 600w, {img_prefix}{v["img"]} 1000w" '
                     f'sizes="(max-width: 700px) calc(100vw - 48px), (max-width: 1080px) 48vw, 506px" '
                     f'alt="{e(name)}, sold" width="{v["imgW"]}" height="{v["imgH"]}" {loading} decoding="async">')
    else:
        media_img = '<span class="srp-card__nophoto">No photograph available</span>'
    text = " ".join([str(v["year"]), v["make"], v["model"], v.get("titleAsListed", "")]).lower()
    attrs = (f' data-slug="{v["slug"]}" data-make="{e(v["make"])}" data-year="{v["year"]}" data-price="{v.get("price") or ""}"'
             f' data-miles="{v["mileage"] if v.get("mileage") else 999999999}" data-body="" data-order="{v["order"]}" data-text="{e(text)}"')
    pills = ""
    if miles:
        pills += f'<span class="srp-pill">{miles}</span>'
    if price:
        pills += f'<span class="srp-pill srp-pill--price">{price}</span>'
    i = indent
    return (f'{i}<li class="srp-card is-sold rv-self"{attrs} data-reveal>\n'
            f'{i}  <article class="srp-card__link srp-card__link--static" aria-label="{e(name)}, sold">\n'
            f'{i}    <span class="srp-card__media">{media_img}<span class="srp-card__tag">Sold</span></span>\n'
            f'{i}    <span class="srp-card__body">\n'
            f'{i}      <span class="srp-card__make">{e(v["make"])}</span>\n'
            f'{i}      <h3 class="srp-card__name"><span class="srp-card__year">{v["year"]}</span> {e(v["model"])}</h3>\n'
            f'{i}      <span class="srp-card__pills">{pills}</span>\n'
            f'{i}    </span>\n'
            f'{i}  </article>\n'
            f'{i}</li>')
