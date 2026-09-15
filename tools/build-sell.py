#!/usr/bin/env python3
"""Geneva Motor Haus — build sell.html.

THE FORM is the All Auto Network sell-your-car form
(aanmaster2027.aandemo.com/sell-your-car/, read 2026-09-14; its config is
saved as docs/source/aan-sellyourcar-config-2026-09-14.json): the vehicle
and contact fields under AAN's own names (year, make, model, trim, body,
vin, ext_color, int_color, cylinders, litrs, mileage, trans, lienholder,
estimatepayoff, uploader, fname, lname, address, city, state, zip, email,
phone, message, i_agree), its option lists, its limit of twelve files and
its consent sentence. It has no conditional parts. AAN shows names as
placeholders; here every field has a real label.

THE WORDS around it are Geneva's own /sell-your-car and the homepage's Sell
section, trimmed of the promises nobody has confirmed (within 24 hours, in
as little as one day, best value, never share) — docs/content-ledger-sell.json.

THE PHOTOGRAPH is Geneva's own: a handshake over a silver 911 in a snowy
garage. The page's other image, a stock row of parked cars, is not used.

The form layer — fields, sections, the summary panel, send and clear — is
finance.html's (assets/css/finance-v2.css, assets/js/finance-v2.js);
sell-v2.* add the head, the steps and the photograph drop.

    python3 tools/build-sell.py
"""
import html
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gmh_chrome import ROOT, chrome  # noqa: E402

OUT = ROOT / "sell.html"
LEDGER = ROOT / "docs/content-ledger-sell.json"
SRC = ROOT / "docs/source"
MAKES = json.loads((SRC / "aan-vehicle-makes-2026-09-14.json").read_text())
STATES = json.loads((SRC / "aan-states-2026-09-14.json").read_text())
IMG = "assets/img/sell"
e = html.escape
ARROW = ('<svg class="btn__arrow" width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">'
         '<path d="M2 6.5h9M7.4 3 11 6.5 7.4 10" stroke="currentColor" stroke-width="1.3"/></svg>')
PLUS = ('<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">'
        '<path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.6"/></svg>')

top, footer = chrome(current=("sell.html", "Sell your car"))

# AAN's makes are upper case; the values stay AAN's, the labels are set in title case
SPECIAL = {"A.C.": "A.C.", "AM GENERAL": "AM General", "AMC": "AMC", "BMC": "BMC", "BMW": "BMW", "DELOREAN": "DeLorean",
           "DETOMASO": "De Tomaso", "GMC": "GMC", "HOLLYWOOD+PROP": "Hollywood+Prop", "KIT CARS": "Kit cars",
           "LA SALLE": "La Salle", "MCLAREN": "McLaren", "MG": "MG", "MGA": "MGA", "MGB": "MGB", "MINI": "MINI"}


def make_label(m):
    return SPECIAL.get(m) or " ".join("-".join(p.capitalize() for p in w.split("-")) for w in m.split(" "))


def field(name, label, span=2, kind="text", req=False, attrs="", options=None, placeholder=None):
    star = '<span class="fin-req" aria-hidden="true">*</span>' if req else ""
    r = " required" if req else ""
    fid = f"f-{name}"
    if kind == "select":
        pairs = [o if isinstance(o, tuple) else (o, o) for o in options]
        opts = f'<option value="">{e(placeholder or "Select")}</option>' + "".join(f'<option value="{e(v)}">{e(t)}</option>' for v, t in pairs)
        control = f'<select id="{fid}" name="{name}"{r}{attrs}>{opts}</select>'
    elif kind == "textarea":
        control = f'<textarea id="{fid}" name="{name}" rows="5"{r}{attrs}></textarea>'
    else:
        control = f'<input id="{fid}" name="{name}" type="{kind}"{r}{attrs}>'
    return f'<div class="fin-field f-{span}"><label for="{fid}">{e(label)}{star}</label>{control}</div>'


def rows(*fields):
    return '<div class="fin-grid">' + "".join(fields) + "</div>"


def section(sid, num, title, body, lede=""):
    return (f'<fieldset class="fin-sec rv-self" id="{sid}" data-reveal>'
            f'<legend class="fin-sec__head"><span class="fin-sec__n">{num}</span><span class="fin-sec__t">{e(title)}</span></legend>'
            + (f'<p class="fin-sec__lede">{e(lede)}</p>' if lede else "") + body + "</fieldset>")


YEARS = [str(y) for y in range(2027, 1919, -1)]
makes = sorted(((m, make_label(m)) for m in MAKES if m != "OTHER"), key=lambda p: p[1].lower()) + [("OTHER", "Other")]

vehicle = rows(
    field("year", "Year", 2, "select", True, options=YEARS, placeholder="Select year"),
    field("make", "Make", 2, "select", True, options=makes, placeholder="Select make"),
    field("model", "Model", 2, req=True, attrs=' autocomplete="off"'),
    field("trim", "Trim", 2),
    field("body", "Body style", 2, "select", options=[("twodoor", "2 Door"), ("fourdoor", "4 Door"), ("hatchback", "Hatchback")]),
    field("trans", "Transmission", 2, "select", options=[("auto", "Automatic"), ("manual", "Manual")]),
    field("mileage", "Mileage", 2, attrs=' inputmode="numeric"'),
    field("vin", "VIN", 4, attrs=' maxlength="17" autocapitalize="characters" spellcheck="false" autocomplete="off"'),
    field("ext_color", "Exterior color", 3),
    field("int_color", "Interior color", 3),
    field("cylinders", "Cylinders", 3, attrs=' inputmode="numeric"'),
    field("litrs", "Engine size (liters)", 3, attrs=' inputmode="decimal"'),
    field("lienholder", "Lien holder", 3),
    field("estimatepayoff", "Estimated payoff", 3, attrs=' inputmode="decimal" placeholder="$"'),
)

photos = ('<label class="sl-drop" for="f-uploader">'
          '<input id="f-uploader" name="uploader" type="file" multiple accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,image/jpeg,image/png,image/gif,application/pdf,application/msword">'
          f'<span class="sl-drop__btn">{PLUS}Add photographs</span>'
          '<span class="sl-drop__t">or drag them here</span>'
          '<span class="sl-drop__note">Up to 12 files · JPG, PNG, GIF, PDF or DOC</span>'
          '</label>'
          '<p class="sl-drop__msg" data-drop-msg aria-live="polite"></p>'
          '<ul class="sl-thumbs" data-thumbs hidden></ul>')

contact = rows(
    field("fname", "First name", 3, req=True, attrs=' autocomplete="given-name"'),
    field("lname", "Last name", 3, req=True, attrs=' autocomplete="family-name"'),
    field("address", "Address", 6, attrs=' autocomplete="street-address"'),
    field("city", "City", 2, attrs=' autocomplete="address-level2"'),
    field("state", "State", 2, "select", True, options=[(s["key"], s["value"]) for s in STATES], placeholder="Select state"),
    field("zip", "ZIP", 2, req=True, attrs=' inputmode="numeric" maxlength="5" pattern="\\d{5}" autocomplete="postal-code"'),
    field("email", "Email", 3, "email", True, attrs=' autocomplete="email"'),
    field("phone", "Phone", 3, "tel", True, attrs=' autocomplete="tel"'),
    field("message", "Message", 6, "textarea", True, attrs=' placeholder="Condition, service history, options — anything we should know"'),
) + ('<label class="fin-check fin-check--agree"><input type="checkbox" name="i_agree" value="1" id="f-i_agree" required>'
     '<span>Please note that by completing this form, you agree to being contacted via text, phone and email.'
     '<span class="fin-req" aria-hidden="true">*</span></span></label>')

form = (section("sl-vehicle", "01", "Your vehicle", vehicle)
        + section("sl-photos", "02", "Photographs", photos, lede="Optional, up to twelve. We can inspect your vehicle in person or via photos.")
        + section("sl-contact", "03", "Contact", contact))

STEPS = [
    ("Submit your vehicle info", "Fill out the form with your vehicle details and contact information."),
    ("Get your appraisal", "Our team reviews your information and contacts you with an offer."),
    ("Schedule inspection", "We arrange a convenient time to inspect your vehicle, in person or via photos."),
    ("Complete the sale", "Once agreed, we handle the paperwork and payment."),
]
steps_li = "\n".join(
    f'        <li><span class="micro sell__step-n">{k + 1:02d}</span><span class="micro sell__step-t">{t}</span><p class="sl-steps__p">{e(p)}</p></li>'
    for k, (t, p) in enumerate(STEPS))

RAIL_STEPS = [("sl-vehicle", "Your vehicle"), ("sl-photos", "Photographs"), ("sl-contact", "Contact")]
rail_li = "\n".join(f'              <li><a class="fin-step" href="#{sid}"><span class="fin-step__t">{t}</span><span class="fin-step__s" data-status></span></a></li>' for sid, t in RAIL_STEPS)

page = f"""<!doctype html>
<!-- ============================================================
     GENEVA MOTOR HAUS — sell your car
     ============================================================
     GENERATED by tools/build-sell.py. The form is AAN's sell-your-car
     form (fields, names, lists, twelve files, consent) in Geneva's language;
     the words are Geneva's /sell-your-car, trimmed of unconfirmed promises
     (docs/content-ledger-sell.json). A static preview cannot send a request
     or upload a file, and says so when the form is submitted.
     ============================================================ -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sell your car — Geneva Motor Haus · Burlington, WI</title>
<meta name="description" content="Sell your car to Geneva Motor Haus in Burlington, Wisconsin: a fair, no-obligation appraisal.">

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
<link rel="stylesheet" href="assets/css/finance-v2.css?v=4">
<link rel="stylesheet" href="assets/css/sell-v2.css?v=3">
</head>
<body class="v2 is-v3 is-gmh is-fin is-sell">

{top}<main>
  <!-- 1 — THE HEAD: the promise, and a handover in a snowy garage -->
  <section class="sl-head" data-reveal aria-labelledby="sl-title">
    <div class="shell sl-head__inner">
      <div class="sl-head__copy">
        <p class="micro gmh-plate rv-eyebrow">Sell your car</p>
        <h1 class="sl-head__title" id="sl-title"><span class="ttl-line">Get top dollar</span> <span class="ttl-line">for your car.</span></h1>
        <p class="sl-head__lede rv-lede">A fair, no-obligation appraisal — whether you’re selling a luxury vehicle, an exotic or a daily driver.</p>
        <div class="sl-head__acts rv-act">
          <a class="btn btn--accent" href="#apply">Start with your car {ARROW}</a>
          <a class="btn btn--line" href="tel:+12622496777">Call (262) 249-6777 {ARROW}</a>
        </div>
      </div>
      <figure class="sl-head__photo rv-photo" style="--rv-delay: 1">
        <img src="{IMG}/sell-handover.jpg" srcset="{IMG}/sell-handover-sm.jpg 1000w, {IMG}/sell-handover.jpg 2000w" sizes="(max-width: 960px) 100vw, 55vw"
             alt="A handshake over a silver Porsche 911 in a snowy home garage" width="2000" height="1500" fetchpriority="high" decoding="async">
      </figure>
    </div>
  </section>

  <!-- 2 — HOW IT WORKS: the homepage's four step plates, on the bone ground -->
  <section class="sl-how" data-reveal aria-labelledby="sl-how-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">How it works</p>
      <h2 class="sl-how__title" id="sl-how-title"><span class="ttl-line">A simple four-step process.</span></h2>
      <ol class="sell__steps sl-steps">
{steps_li}
      </ol>
    </div>
  </section>

  <!-- 3 — THE FORM: AAN's fields, finance.html's form layer -->
  <section class="fin-apply" id="apply" aria-labelledby="sl-apply-title">
    <div class="shell">
      <div class="fin-apply__head" data-reveal>
        <p class="micro gmh-plate rv-eyebrow">Get started</p>
        <h2 class="fin-apply__title" id="sl-apply-title"><span class="ttl-line">Sell us your car.</span></h2>
        <p class="fin-apply__lede rv-lede">Fill out the form with your vehicle information and contact details, and our team will review your submission. Fields marked <span class="fin-req">*</span> are required.</p>
      </div>
      <div class="fin-apply__body">
        <div class="fin-apply__main">
          <form class="fin-form" id="fin-form" novalidate>
{form}
            <div class="fin-actions">
              <button class="btn btn--accent" type="submit">Submit for appraisal {ARROW}</button>
              <button class="btn btn--line fin-clear" type="button">Clear form</button>
            </div>
          </form>
          <div class="fin-sent" id="fin-sent" hidden tabindex="-1">
            <p class="fin-sent__t">Thanks<span data-sent-name></span>.</p>
            <p class="fin-sent__p">This preview doesn’t send requests. To get an appraisal now, call <a href="tel:+12622496777">(262) 249-6777</a>.</p>
          </div>
        </div>
        <aside class="fin-rail rv-self" data-reveal aria-label="Your car">
          <div class="fin-rail__head">
            <p class="fin-rail__t">Your car</p>
            <p class="sl-car" data-car>Year, make and model</p>
            <div class="fin-rail__progress" data-progress hidden>
              <p class="fin-rail__count"><b data-done>0</b> of <span data-total>0</span> required fields filled</p>
              <span class="fin-rail__bar" aria-hidden="true"><span data-bar></span></span>
            </div>
          </div>
          <nav aria-label="Form steps">
            <ol class="fin-rail__steps">
{rail_li}
            </ol>
          </nav>
          <div class="fin-rail__foot">
            <button class="btn btn--accent fin-rail__send" type="submit" form="fin-form">Submit for appraisal {ARROW}</button>
            <p class="fin-rail__help">Questions? Call <a href="tel:+12622496777">(262) 249-6777</a></p>
          </div>
        </aside>
      </div>
    </div>
  </section>
</main>

{footer}


<script src="assets/js/main-final-v2.js?v=2" defer></script>
<script src="assets/js/geneva-final-v2.js?v=2" defer></script>
<script src="assets/js/finance-v2.js?v=5" defer></script>
<script src="assets/js/sell-v2.js?v=1" defer></script>
</body>
</html>
"""
OUT.write_text(page)

G = "genevamotorhaus.com/sell-your-car, rendered 2026-09-14"
ledger = {
    "project": "geneva-motor-haus", "page": "sell.html", "compiled": "2026-09-14",
    "note": "The form is AAN's sell-your-car form (aanmaster2027.aandemo.com/sell-your-car/, read 2026-09-14; config in docs/source/). The words are Geneva's, trimmed.",
    "entries": [
        {"id": "sl-heading", "claim": "Get top dollar for your car.", "status": "verified", "source": "homepage ledger sell-heading ('Get Top Dollar for Your Car')", "sourceType": "live-site", "appearsAt": ["#sl-title"]},
        {"id": "sl-lede", "claim": "A fair, no-obligation appraisal — whether you’re selling a luxury vehicle, an exotic or a daily driver.", "status": "verified", "source": "homepage ledger sell-appraisal (live homepage Sell section)", "sourceType": "live-site", "appearsAt": [".sl-head__lede"]},
        {"id": "sl-steps", "claim": " / ".join(f"{t}: {p}" for t, p in STEPS), "status": "verified", "source": f"{G}, 'Simple 4-Step Process' (titles verbatim; texts trimmed: 'fair market value offer' → 'an offer', 'all paperwork' → 'the paperwork', 'you drive away satisfied' removed)", "sourceType": "live-site", "appearsAt": [".sl-steps"]},
        {"id": "sl-form-intro", "claim": "Fill out the form with your vehicle information and contact details, and our team will review your submission.", "status": "verified", "source": f"{G}, 'Sell Us Your Car' intro, with 'contact you within 24 hours with a competitive offer' removed", "sourceType": "live-site", "appearsAt": [".fin-apply__lede"]},
        {"id": "sl-photos-lede", "claim": "We can inspect your vehicle in person or via photos.", "status": "verified", "source": f"{G}, step 03: 'inspect your vehicle in person or via photos'", "sourceType": "live-site", "appearsAt": ["#sl-photos"]},
        {"id": "sl-form", "claim": "Form fields, option lists, twelve-file limit and the consent sentence", "status": "verified", "source": "AAN sell-your-car form config (docs/source/aan-sellyourcar-config-2026-09-14.json, aan-vehicle-makes, aan-states)", "sourceType": "client-data", "appearsAt": ["#fin-form"]},
        {"id": "sl-phone", "claim": "(262) 249-6777", "status": "verified", "source": "homepage ledger contact-phone", "sourceType": "live-site", "appearsAt": [".sl-head__acts", ".fin-rail__help", ".fin-sent__p"]},
        {"id": "sl-photo", "claim": "Photograph: a handshake over a silver Porsche 911 in a snowy home garage", "status": "verified", "source": f"{G}, hero image uploads/media/693cf6bb82e27_1765603003.JPG (assets/img/source/sell/), resized; no one named, no car offered", "sourceType": "live-site", "appearsAt": [".sl-head__photo"]},
    ],
    "notUsed": [
        {"claim": "Get the Best Value · the best value for your car · easy and profitable", "reason": "a superlative promise without a source (CP6)"},
        {"claim": "Get an appraisal in minutes and complete the sale in as little as one day", "reason": "a time promise not confirmed by the client (CP6)"},
        {"claim": "contact you within 24 hours with a competitive offer", "reason": "a response-time promise not confirmed (CP6)"},
        {"claim": "We buy luxury vehicles, exotics, classics, and daily drivers of all makes and models", "reason": "'all makes and models' is an unconfirmed promise; the homepage's verified sentence carries the range"},
        {"claim": "We respect your privacy and will never share your information with third parties", "reason": "a legal/privacy commitment for the client's counsel, not the design (CP6); AAN's consent sentence is used instead"},
        {"claim": "free, no-obligation appraisal · stress-free · as easy as possible", "reason": "'free' and the ease claims are unconfirmed; 'fair, no-obligation appraisal' (verified) is used"},
        {"claim": "CTA background: a stock photograph of a row of parked cars (uploads/media/69174bf6dc021_1763134454.jpg)", "reason": "stock imagery, not Geneva's; no car of theirs in it (CP7)"},
        {"claim": "Geneva's own short form (fullName, yearMakeModel, titleStatus, desiredPrice, vehicleInfo)", "reason": "the AAN form is the spec; its message field carries the rest"},
    ],
}
LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False))
print(f"wrote {OUT.name} ({OUT.stat().st_size // 1024} KB): {len(makes)} makes, {len(STATES)} states, {len(YEARS)} years; ledger {len(ledger['entries'])} entries")
