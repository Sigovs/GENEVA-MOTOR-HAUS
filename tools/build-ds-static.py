#!/usr/bin/env python3
"""Geneva Motor Haus — build design-system/, the developer handoff.

A folder that stands on its own — no site CSS, no JavaScript — for whoever
builds Geneva Motor Haus into production:

    design-system/index.html     the handoff document
    design-system/tokens.css     every token as a custom property   (generated here)
    design-system/tokens.json    the same tokens as data             (generated here)
    design-system/geneva-ds.css  the components, .g-*               (hand-maintained)
    design-system/docs.css       the document's own layout           (hand-maintained)
    design-system/img/           the photographs the examples use    (copied here)

TOKENS ARE READ FROM THE SITE: the top-level :root blocks of
assets/css/tokens.css, then the :root and .is-gmh blocks of
assets/css/geneva-final-v2.css (later wins), with var() references resolved.
Contrast ratios are computed from those values. Component sizes in
geneva-ds.css were measured from the site's rendered components (ds.html) on
2026-09-14; the mapping to the site's own classes is in the document.

    python3 tools/build-ds-static.py
"""
import html
import json
import pathlib
import re
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gmh_cards import body_label, spec_line  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "design-system"
PREVIEW = "https://sigovs.github.io/GENEVA-MOTOR-HAUS/"
DATE = "14 Sep 2026"
e = html.escape


# ---- 1. tokens, read from the site's CSS ---------------------------------------------------
def top_level_blocks(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    blocks, depth, sel_start, selector, body_start = [], 0, 0, "", 0
    for i, c in enumerate(text):
        if c == "{":
            if depth == 0:
                selector, body_start = text[sel_start:i].strip(), i + 1
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                blocks.append((selector, text[body_start:i]))
                sel_start = i + 1
        elif c == ";" and depth == 0:
            sel_start = i + 1
    return blocks


raw = {}
for path, sels in (("assets/css/tokens.css", {":root"}), ("assets/css/geneva-final-v2.css", {":root", ".is-gmh"})):
    for sel, body in top_level_blocks((ROOT / path).read_text()):
        if sel in sels:
            for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", body):
                raw[m.group(1)] = " ".join(m.group(2).split())


def resolve(name, depth=0):
    value = raw.get(name, "")
    if depth > 12:
        return value
    return re.sub(r"var\((--[\w-]+)(?:\s*,\s*([^()]*))?\)", lambda m: resolve(m.group(1), depth + 1) or (m.group(2) or ""), value)


# (token, name, use) — the site's tokens, grouped for people
GROUPS = [
    ("color", "Colour", [
        ("--bg", "Page ground", "Every page; photographs sit on it uncut."),
        ("--bg-raised", "Raised", "Cards, panels, form sections, accordions."),
        ("--bg-sunk", "Sunk", "Card media well, drop zone, terms box."),
        ("--bg-black", "Band", "Dark bands and the footer."),
        ("--ink", "Ink", "Titles, values, anything read first."),
        ("--ink-2", "Ink 2", "Body, ledes, field labels."),
        ("--ink-3", "Ink 3", "Notes, meta, inactive states. Never below 14px."),
        ("--rule", "Rule", "Card borders, section hairlines."),
        ("--rule-strong", "Rule strong", "Inputs, outline pills, list hairlines."),
        ("--bone", "Bone", "The one light band a page may have; bone buttons."),
        ("--bone-ink", "Bone ink", "Text on bone."),
        ("--bone-ink-2", "Bone ink 2", "Body on bone."),
        ("--bone-rule", "Bone rule", "Hairlines on bone."),
        ("--accent", "Accent", "The barn roof in the badge."),
        ("--accent-deep", "Accent deep", "Step numerals on bone."),
        ("--action", "Action", "Primary buttons, the Sold tag, error borders."),
        ("--action-hover", "Action hover", "Primary button under the pointer."),
        ("--action-press", "Action press", "Primary button pressed."),
        ("--action-ink", "Action ink", "Label on red."),
        ("--action-edge", "Action edge", "The 1px inner edge of a red button."),
        ("--action-focus", "Action focus", "Focus ring around a red button."),
        ("--eyebrow-plate", "Plate", "Every eyebrow; the current step in a panel."),
        ("--eyebrow-ink", "Plate ink", "The label on the plate."),
    ]),
    ("type", "Type", [
        ("--font-display", "Display face", "Titles, card titles, numerals. Zilla Slab 500–700."),
        ("--font-body", "Body face", "Everything read. Instrument Sans 400–600."),
        ("--font-label", "Label face", "Labels, pills, buttons, plates."),
        ("--t-micro", "Micro", "14px — the floor for anything functional."),
        ("--t-body", "Body size", "16px."),
        ("--t-lede", "Lede size", "Homepage ledes."),
        ("--lh-body", "Body line height", ""),
        ("--lh-head", "Heading line height", ""),
        ("--lh-label", "Label line height", ""),
        ("--tr-display", "Display tracking", "Zilla Slab titles."),
        ("--tr-label", "Label tracking", ""),
    ]),
    ("space", "Space", [(f"--sp-{n}", f"Space {n}", "") for n in range(1, 13)]),
    ("layout", "Layout", [
        ("--page-gutter", "Page gutter", "Side padding at every width; never zero."),
        ("--container", "Container", "The content measure with its gutters (1240px of content)."),
        ("--sec", "Section padding", "A section's vertical padding."),
        ("--sec-lg", "Chapter padding", "A chapter's vertical padding."),
        ("--gf-head-h", "Header height", "Page heads start below it."),
        ("--gf-head-h-c", "Compact header height", "Sticky things sit under it."),
    ]),
    ("radius", "Radius", [
        ("--r-control", "Control", "Step plates, the Sold tag, small controls."),
        ("--r-panel", "Panel", "Homepage panels."),
    ]),
    ("motion", "Motion", [
        ("--ease-out", "Ease out", "Every entrance and state change."),
        ("--ease-in", "Ease in", "Exits only."),
        ("--dur-1", "Duration 1", "Colour and border changes."),
        ("--dur-2", "Duration 2", "Arrow nudge, plate hovers."),
        ("--dur-3", "Duration 3", ""),
        ("--dur-4", "Duration 4", ""),
        ("--rv-step", "Entrance step", "The gap between stepped parts."),
        ("--rv-cta", "Entrance: plate, buttons", ""),
        ("--rv-lede", "Entrance: paragraph, blocks", ""),
        ("--rv-line", "Entrance: headline line", ""),
        ("--rv-photo", "Entrance: photograph", ""),
    ]),
]
# named here so production can use them; the site writes these values directly
HANDOFF_TOKENS = [
    ("radius", "--r-thumb", "8px", "Thumb", "Thumbnails, contrast samples."),
    ("radius", "--r-input", "10px", "Input", "Inputs, selects, the terms box."),
    ("radius", "--r-card", "12px", "Card", "Cards, panels, form sections, accordions."),
    ("radius", "--r-photo", "16px", "Photograph", "Large photographs, the visit card."),
    ("radius", "--r-pill", "999px", "Pill", "Buttons, pills, toggles, progress bars."),
    ("helper", "--bg-rgb", None, "Ground as RGB channels", "For rgb(var(--bg-rgb) / .8)."),
]

tokens = {}
for key, label, items in GROUPS:
    tokens[key] = {t: {"value": resolve(t), "name": n, "use": u} for t, n, u in items}
    missing = [t for t, v in tokens[key].items() if not v["value"]]
    if missing:
        raise SystemExit(f"build-ds-static: no value for {missing}")
for key, t, v, n, u in HANDOFF_TOKENS:
    tokens.setdefault(key, {})[t] = {"value": v or resolve(t), "name": n, "use": u, "handoff": True}


# ---- 2. contrast ------------------------------------------------------------------------------
def channels(value):
    value = value.strip()
    if value.startswith("#"):
        h = value[1:]
        h = "".join(c * 2 for c in h) if len(h) == 3 else h
        return [int(h[i:i + 2], 16) for i in (0, 2, 4)], 1.0
    nums = [float(x) for x in re.findall(r"[\d.]+", value)]
    return nums[:3], (nums[3] if len(nums) > 3 else 1.0)


def lum(rgb):
    lin = [(x / 255) / 12.92 if x / 255 <= 0.03928 else (((x / 255) + 0.055) / 1.055) ** 2.4 for x in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(fg, bg):
    f, fa = channels(tokens["color"][fg]["value"])
    b, _ = channels(tokens["color"][bg]["value"])
    mixed = [f[i] * fa + b[i] * (1 - fa) for i in range(3)]
    l1, l2 = lum(mixed), lum(b)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


PAIRS = [
    ("--ink", "--bg", "Titles on the ground", False), ("--ink-2", "--bg", "Body on the ground", False),
    ("--ink-3", "--bg", "Notes on the ground", False), ("--ink-2", "--bg-raised", "Body on cards", False),
    ("--ink-3", "--bg-raised", "Notes on cards", False), ("--bone-ink", "--bone", "Titles on bone", False),
    ("--bone-ink-2", "--bone", "Body on bone", False), ("--accent-deep", "--bone", "Step numerals (large)", True),
    ("--action-ink", "--action", "Label on red", False), ("--eyebrow-ink", "--eyebrow-plate", "Plate label", False),
    ("--ink", "--eyebrow-plate", "Current panel step", False), ("--accent", "--bg", "Red on the ground", None),
]


def grade(r, large):
    if large is None:
        return "Fill only" if r < 4.5 else "AA — still a fill", False
    aa, aaa = (3, 4.5) if large else (4.5, 7)
    return ("AAA" if r >= aaa else "AA" if r >= aa else "Fails"), r >= aa


# ---- 3. example data from the inventory -------------------------------------------------------------
IMG = OUT / "img"
IMG.mkdir(parents=True, exist_ok=True)


def copy_img(rel):
    src = ROOT / rel
    dst = IMG / src.name
    shutil.copy2(src, dst)
    return f"img/{src.name}"


inv = json.loads((ROOT / "assets/data/inventory-2026-09-14.json").read_text())["vehicles"]
car = next(v for v in inv if v.get("imgSm") and v.get("price") and v.get("mileage"))
sold_all = json.loads((ROOT / "assets/data/sold-2026-09-14.json").read_text())["vehicles"]
sold = next(v for v in sold_all if v.get("imgSm") and v.get("price") and v.get("mileage"))
car_img, sold_img = copy_img(car["imgSm"]), copy_img(sold["imgSm"])
photo_img = copy_img("assets/img/about/about-story-sm.jpg")
badge_img = copy_img("assets/logos/gmh-icon-180.png")

ARROW = '<svg class="g-btn__arrow" width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true"><path d="M2 6.5h9M7.4 3 11 6.5 7.4 10" stroke="currentColor" stroke-width="1.3"/></svg>'
CHECK = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true"><path d="M2.5 7.3 5.6 10.2 11.5 3.8" stroke="currentColor" stroke-width="1.6"/></svg>'
X = '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M2.5 2.5l7 7M9.5 2.5l-7 7" stroke="currentColor" stroke-width="1.6"/></svg>'

car_name = f"{car['year']} {car['make']} {car['model']}"
sold_name = f"{sold['year']} {sold['make']} {sold['model']}"
car_pills = [f"${car['price']:,}", f"{car['mileage']:,} mi"] + ([body_label(car.get("body"))] if body_label(car.get("body")) else [])

# ---- 4. components: one snippet each, shown live and as code ---------------------------------------
C = {}
C["buttons"] = f"""<div class="g-row">
  <a class="g-btn g-btn--accent" href="#">Browse inventory {ARROW}</a>
  <a class="g-btn g-btn--line" href="#">Call (262) 249-6777 {ARROW}</a>
  <a class="g-btn g-btn--fill" href="#">Ask about shipping {ARROW}</a>
</div>"""
C["plate"] = """<p class="g-plate">Inventory</p>"""
C["pills"] = f"""<div class="g-row">
  <a class="g-pill g-pill--accent" href="tel:+12622496777">(262) 249-6777</a>
  <a class="g-pill g-pill--bone" href="#">Email dealer</a>
  <a class="g-pill g-pill--line" href="#">Get financing {ARROW}</a>
</div>"""
C["choice"] = """<fieldset class="g-choice">
  <legend>Best time to contact<span class="g-req" aria-hidden="true">*</span></legend>
  <div class="g-choice__opts">
    <label><input type="radio" name="contact_mode" value="morning" required><span>Morning</span></label>
    <label><input type="radio" name="contact_mode" value="afternoon" checked><span>Afternoon</span></label>
    <label><input type="radio" name="contact_mode" value="evening"><span>Evening</span></label>
  </div>
</fieldset>"""
C["card"] = f"""<ul class="g-cards g-cards--2">
  <li class="g-card">
    <a class="g-card__link" href="{PREVIEW}cars/{car['slug']}.html">
      <span class="g-card__media"><img src="{car_img}" alt="{e(car_name)}" width="1000" height="667" loading="lazy" decoding="async"></span>
      <span class="g-card__body">
        <span class="g-card__make">{e(car['make'])}</span>
        <span class="g-card__name">{car['year']} {e(car['model'])}</span>
        <span class="g-card__spec">{e(spec_line(car) or '')}</span>
        <span class="g-card__pills">{''.join(f'<span class="g-card__pill">{e(p)}</span>' for p in car_pills)}</span>
        <span class="g-card__go" aria-hidden="true">See details {ARROW}</span>
      </span>
    </a>
  </li>
  <li class="g-card g-card--sold">
    <article class="g-card__link">
      <span class="g-card__media"><img src="{sold_img}" alt="{e(sold_name)}" width="1000" height="667" loading="lazy" decoding="async"><span class="g-card__tag">Sold</span></span>
      <span class="g-card__body">
        <span class="g-card__make">{e(sold['make'])}</span>
        <h3 class="g-card__name">{sold['year']} {e(sold['model'])}</h3>
        <span class="g-card__pills"><span class="g-card__pill">{sold['mileage']:,} mi</span><span class="g-card__pill">${sold['price']:,}</span></span>
      </span>
    </article>
  </li>
</ul>"""
C["form"] = """<form class="g-form" novalidate>
  <fieldset class="g-section">
    <legend class="g-section__head"><span class="g-section__n">01</span><span class="g-section__t">Your vehicle</span></legend>
    <div class="g-fields">
      <div class="g-field g-span-2"><label for="f-year">Year<span class="g-req" aria-hidden="true">*</span></label>
        <select id="f-year" name="year" required><option value="">Select year</option><option selected>2008</option></select></div>
      <div class="g-field g-span-2"><label for="f-make">Make<span class="g-req" aria-hidden="true">*</span></label>
        <input id="f-make" name="make" value="Porsche" required></div>
      <div class="g-field g-span-2"><label for="f-model">Model<span class="g-req" aria-hidden="true">*</span></label>
        <input id="f-model" name="model" required aria-invalid="true" placeholder="Required"></div>
      <div class="g-field g-span-6"><label for="f-message">Message</label>
        <textarea id="f-message" name="message" rows="4" placeholder="Tell us how we can help"></textarea></div>
    </div>
    <label class="g-toggle"><input type="checkbox" name="co_applicant_active" checked><span class="g-toggle__track" aria-hidden="true"></span><span class="g-toggle__text">Apply with a co-applicant</span></label>
    <label class="g-check"><input type="checkbox" name="i_agree" value="1" required><span>Please note that by completing this form, you agree to being contacted via text, phone and email.<span class="g-req" aria-hidden="true">*</span></span></label>
  </fieldset>
</form>"""
C["panel"] = f"""<aside class="g-panel" aria-label="Your car">
  <div class="g-panel__head">
    <p class="g-panel__t">Your car</p>
    <p class="g-panel__sub">2008 Porsche 911 Turbo</p>
    <p class="g-panel__count"><b>4</b> of 11 required fields filled</p>
    <span class="g-progress" style="--progress: 0.36" aria-hidden="true"><span></span></span>
  </div>
  <ol class="g-panel__steps">
    <li><a class="g-step" href="#vehicle"><span>Your vehicle</span><span class="g-step__s is-done">{CHECK}3 / 3 required</span></a></li>
    <li><a class="g-step" href="#photos" aria-current="step"><span>Photographs</span><span class="g-step__s is-done">{CHECK}2 attached</span></a></li>
    <li><a class="g-step" href="#contact"><span>Contact</span><span class="g-step__s">1 / 8 required</span></a></li>
  </ol>
  <div class="g-panel__foot">
    <button class="g-btn g-btn--accent" type="submit" form="sell-form">Submit for appraisal {ARROW}</button>
    <p class="g-panel__help">Questions? Call <a href="tel:+12622496777">(262) 249-6777</a></p>
  </div>
</aside>"""
C["accordion"] = """<details class="g-acc" open>
  <summary class="g-acc__sum"><span class="g-acc__label">Shipping</span><span class="g-acc__mark" aria-hidden="true"></span></summary>
  <div class="g-acc__body">
    <p>Nationwide transportation available. Half our cars leave Wisconsin.</p>
  </div>
</details>
<details class="g-acc">
  <summary class="g-acc__sum"><span class="g-acc__label">Estimate a payment</span><span class="g-acc__mark" aria-hidden="true"></span></summary>
  <div class="g-acc__body"><p>An estimate from your own numbers, not an offer.</p></div>
</details>"""
C["steps"] = """<div class="g-bone">
  <ol class="g-steps">
    <li><span class="g-steps__n">01</span><span class="g-steps__t">Submit your vehicle info</span><p class="g-steps__p">Fill out the form with your vehicle details and contact information.</p></li>
    <li><span class="g-steps__n">02</span><span class="g-steps__t">Get your appraisal</span><p class="g-steps__p">Our team reviews your information and contacts you with an offer.</p></li>
    <li><span class="g-steps__n">03</span><span class="g-steps__t">Schedule inspection</span><p class="g-steps__p">We arrange a convenient time to inspect your vehicle, in person or via photos.</p></li>
    <li><span class="g-steps__n">04</span><span class="g-steps__t">Complete the sale</span><p class="g-steps__p">Once agreed, we handle the paperwork and payment.</p></li>
  </ol>
</div>"""
C["points"] = """<ul class="g-points">
  <li class="g-point"><p class="g-point__t">Competitive rates</p><p class="g-point__p">We work with multiple lenders to find the rate available for your situation.</p></li>
  <li class="g-point"><p class="g-point__t">Flexible terms</p><p class="g-point__p">A variety of loan terms and payment options to fit your budget.</p></li>
</ul>"""
C["drop"] = f"""<label class="g-drop">
  <input type="file" name="uploader" multiple accept=".jpg,.jpeg,.png,.gif,.pdf,.doc">
  <span class="g-drop__btn">Add photographs</span>
  <span class="g-drop__t">or drag them here</span>
  <span class="g-drop__note">Up to 12 files · JPG, PNG, GIF, PDF or DOC</span>
</label>
<ul class="g-thumbs">
  <li class="g-thumb"><img src="{car_img}" alt=""><button class="g-thumb__x" type="button" aria-label="Remove photo-1.jpg">{X}</button></li>
  <li class="g-thumb"><img src="{sold_img}" alt=""><button class="g-thumb__x" type="button" aria-label="Remove photo-2.jpg">{X}</button></li>
</ul>"""

COMPONENTS = [
    ("buttons", "Buttons", "g-btn · g-btn--accent · g-btn--line · g-btn--fill", ".btn.btn--accent · .btn--line · .btn--fill (main.css, v2.css)",
     [("Height", "54px — 16px padding, 14px label on a 1.6 line"), ("Inline padding", "clamp(32px, 2.4vw, 48px)"), ("Radius", "--r-pill"), ("Label", "--font-label 500, 14px, upper case"), ("Gap to arrow", "12px; arrow 13×13, stroke 1.3")],
     ["Accent: --action; hover --action-hover; pressed --action-press; focus ring 2px --action-focus, offset 3px.", "Line: 1.5px inner ring at 42% ink; hover ring --ink.", "Fill (bone): hover turns red, --action with --action-ink.", "The arrow moves 2px up-right on hover; not under reduced motion."],
     ["One accent button per view. Never a gradient, never a shadow.", "Buttons are links when they go somewhere, <button> when they act."]),
    ("plate", "The plate", "g-plate", ".micro.gmh-plate (geneva-final-v2.css F24)",
     [("Height", "22px"), ("Padding", "4px 8px — the label's own width"), ("Label", "14px, 500, upper case, tracking 0.06em"), ("Colour", "--eyebrow-ink on --eyebrow-plate · 7.8:1"), ("Radius", "none")],
     ["No states: it names, it is never a link."], ["One plate over every page title and section title."]),
    ("pills", "Pills", "g-pill · g-pill--accent · g-pill--bone · g-pill--line", ".vdp-pill (vdp-v2.css)",
     [("Height", "41px — 8px 16px 9px padding, 1px border"), ("Label", "14px, 500"), ("Radius", "--r-pill"), ("Gap", "8px between pills")],
     ["Accent hover --action-hover; bone hover darkens 12%; line hover border --ink.", "Focus ring 2px --ink, offset 2px."],
     ["Known compromise: 41px is under the 44px touch target. In production, set min-height: 44px."]),
    ("choice", "Choice pills", "g-choice · g-choice__opts", ".ct-when (contact-v2.css)",
     [("Height", "47px — 11px 20px 12px padding, 1px border"), ("Label", "14px, 500, --ink-2"), ("Chosen", "--bone fill, --bone-ink label"), ("Legend", "14px, 500, tracking 0.04em")],
     ["Hover: border --ink-3, label --ink.", "Focus: 2px --ink ring around the pill.", "Error after a send: border --action."],
     ["Real radio inputs, visually hidden over the pill; the whole pill is the target."]),
    ("card", "Car card", "g-cards · g-card · g-card--sold", "li.srp-card (srp-v2.css; markup from tools/gmh_cards.py)",
     [("Grid", "3 across; 2 at ≤1080px; 1 at ≤700px; gap clamp(24px, 2.2vw, 32px)"), ("Card", "1px --rule, --r-card, --bg-raised"), ("Media", "3:2, object-fit cover, --bg-sunk while loading"), ("Body", "24px padding; make 14px upper case --ink-3; name 17px/600/1.24; spec 14px/1.45, two lines reserved"), ("Pills", "37px — 7px 13px 8px, 14px 600, ink at 6%"), ("Sold tag", "top-left 16px, 6px 12px 7px, --r-control, tracking 0.2em")],
     ["Hover: border --rule-strong, ground 6% lighter, photograph scales to 1.04, “See details” appears bottom-right.", "Focus: 2px --ink ring, offset 3px; “See details” shows.", "Touch (hover: none): “See details” is always visible.", "Sold: no link, no hover."],
     ["The whole card is one link to the car's page.", "Prices and mileages are dated on the page they appear on (“as listed 14 Sep 2026”)."]),
    ("form", "Form section and fields", "g-form · g-section · g-fields · g-field · g-span-* · g-toggle · g-check", ".fin-sec · .fin-grid · .fin-field · .fin-toggle · .fin-check (finance-v2.css)",
     [("Section", "clamp(24px, 3vw, 40px) padding, 1px --rule, --r-card, --bg-raised"), ("Legend", "number 14px --ink-3, title Zilla Slab 700 clamp(22px, 1.8vw, 26px)"), ("Grid", "6 columns, gap 20px 24px; 2 columns at ≤720px; 1 at ≤480px"), ("Field", "label 14px/500 --ink-2, 8px to the control"), ("Control", "48px min height, 12px 16px padding, 1px --rule-strong, --r-input, 16px text"), ("Toggle", "44×26 track, 18px knob"), ("Checkbox", "20×20, accent-color --action")],
     ["Hover: border --ink-3. Focus: border --ink, ground ink 6%.", "Error: border --action — on :user-invalid, on [aria-invalid=\"true\"], or on :invalid inside .g-form.was-sent.", "Toggle on: bone track, dark knob moved 18px."],
     ["Every control has a visible <label>; placeholders never replace it.", "Keep the AAN field names (fname, lname, email, phone, i_agree …) so the forms post to AAN unchanged."]),
    ("panel", "Summary panel", "g-panel · g-progress · g-step", "aside.fin-rail (finance-v2.css)",
     [("Width", "20rem, sticky at the compact header + 24px"), ("Sections", "24px padding on hairlines"), ("Title", "Zilla Slab 700, 20px"), ("Progress", "4px, --r-pill; fill --bone, scaleX(--progress)"), ("Step row", "12px 24px, 15px/500 label, status 14px")],
     ["Current step: --eyebrow-plate ground, --ink label.", "Complete: check icon, status in --ink.", "Hidden under 960px — the form is complete without it."],
     ["Status says what is filled and what each step still needs (“0 / 3 required”), never a bare numbered outline."]),
    ("accordion", "Accordion", "g-acc", "details.vdp-acc (vdp-v2.css)",
     [("Container", "1px --rule-strong, --r-card, --bg-raised; 16px between"), ("Summary", "clamp(20px, 2.2vw, 32px) clamp(24px, 3.4vw, 48px) padding"), ("Label", "Zilla Slab 700, clamp(17px, 1.4vw, 20px)"), ("Mark", "32px ring, 12×2 bars on whole pixels")],
     ["Open: the vertical bar scales to 0 in 280ms cubic-bezier(.2, 0, 0, 1).", "Hover or open: ring --ink-2, ground ink 6%.", "Focus: 2px --ink ring inside the summary."],
     ["Native <details>: works without script, find-in-page reaches closed content."]),
    ("steps", "Step plates on bone", "g-bone · g-steps", ".sell__steps (v3.css, geneva-final-v2.css, sell-v2.css)",
     [("Grid", "4 across; 2 at ≤900px; 1 at ≤520px"), ("Plate", "32px padding (24px ≤900), 1px --bone-rule, --r-control, bone-ink at 3.5%"), ("Numeral", "Zilla Slab 700 clamp(36px, 2.8vw, 48px), --accent-deep, followed by a full stop"), ("Title", "17px/500 --bone-ink, 12px to the sentence"), ("Sentence", "16px/1.55 --bone-ink-2")],
     ["Hover: border darkens to bone-ink 40%."], ["Four, because Geneva's process has four. One bone band per page at most."]),
    ("points", "Hairline list", "g-points · g-point", ".fin-points (finance-v2.css) · .ct-ways (contact-v2.css)",
     [("Rows", "24px vertical padding on --rule-strong hairlines"), ("Columns", "11rem title, the rest the sentence; stacked at ≤720px"), ("Title", "Zilla Slab 700, 20px"), ("Sentence", "16px/1.6 --ink-2")],
     ["No states."], ["Three rows beside a page title. No icons, no cards."]),
    ("drop", "Photograph drop", "g-drop · g-thumbs · g-thumb", ".sl-drop · .sl-thumbs (sell-v2.css)",
     [("Zone", "48px 24px padding, 1px --rule-strong, --r-card, --bg-sunk"), ("Button", "12px 20px, --bone, 14px upper case"), ("Thumbnails", "auto-fill minmax(7.5rem, 1fr), 3:2, --r-thumb"), ("Remove", "32px circle, ground at 82%")],
     ["Hover or dragging over: border --ink, ground ink 4%.", "Keyboard: the file input is focusable; the zone shows the focus ring."],
     ["Up to 12 files, JPG/PNG/GIF/PDF/DOC, as the AAN sell form allows.", "Each file gets its own remove button with the file name in its label."]),
]

MAP = [
    (".g-btn --accent / --line / --fill", ".btn.btn--accent / .btn--line / .btn--fill", "main.css · v2.css"),
    (".g-plate", ".micro.gmh-plate", "geneva-final-v2.css F24"),
    (".g-pill", ".vdp-pill", "vdp-v2.css"),
    (".g-choice", ".ct-when", "contact-v2.css"),
    (".g-card", "li.srp-card", "srp-v2.css · tools/gmh_cards.py"),
    (".g-section · .g-field · .g-toggle · .g-check", ".fin-sec · .fin-field · .fin-toggle · .fin-check", "finance-v2.css"),
    (".g-panel · .g-step", "aside.fin-rail · .fin-step", "finance-v2.css"),
    (".g-acc", "details.vdp-acc", "vdp-v2.css"),
    (".g-steps", ".sell__steps", "v3.css · geneva-final-v2.css · sell-v2.css"),
    (".g-points", ".fin-points · .ct-ways", "finance-v2.css · contact-v2.css"),
    (".g-drop · .g-thumb", ".sl-drop · .sl-thumb", "sell-v2.css"),
    (".ttl-line · .rv-*", ".ttl-line · .rv-*", "main.css · geneva-final-v2.css F25 · main-final-v2.js"),
]

TYPE_ROLES = [
    ("g-h1", "Page title", "Get approved today.", "Zilla Slab 700 · clamp(40px, 5vw, 72px) / 1.02 · −0.012em", "One per page; set in lines."),
    ("g-h2", "Section title", "Sell us your car.", "Zilla Slab 700 · clamp(28px, 3vw, 44px) / 1.08 · −0.012em", "Under a plate, over a lede."),
    ("g-h3", "Card title", "Your vehicle", "Zilla Slab 700 · clamp(22px, 1.8vw, 26px) / 1.2 · −0.01em", "Form sections, panels."),
    ("g-h4", "Small title", "Competitive rates", "Zilla Slab 700 · 20px / 1.3", "List heads, reasons."),
    ("g-lede", "Lede", "A fair, no-obligation appraisal — whether you’re selling a luxury vehicle, an exotic or a daily driver.", "Instrument Sans 400 · 18px / 1.6 · --ink-2 · ≤ 52ch", "Under a page title."),
    ("g-body", "Body", "We work with multiple lenders to find the rate available for your situation.", "Instrument Sans 400 · 16px / 1.6 · --ink-2 · ≤ 60ch", "Everything else that is read."),
    ("g-label", "Label", "First name", "Instrument Sans 500 · 14px / 1.3 · tracking 0.04em · --ink-2", "Field labels, legends."),
    ("g-meta", "Meta", "Price and mileage as listed on 14 Sep 2026", "Instrument Sans 400 · 14px / 1.5 · --ink-3", "Dates, notes, help. The floor."),
]

ROLES = [
    (".ttl-line", "A headline line", "slides in from the left, 56px", "--rv-line", "one step per line"),
    (".rv-eyebrow", "The plate", "fades, 6px", "--rv-cta", "none"),
    (".rv-lede", "The paragraph", "rises 32px", "--rv-lede", "2.2 steps"),
    (".rv-act", "The buttons", "settle 10px", "--rv-cta", "3.4 steps"),
    (".rv-item / .rv-stagger > *", "Blocks in order", "rise 24px", "--rv-lede", "from --rv-from (2.6), 0.7 apart"),
    (".rv-photo", "A photograph", "floats up 64px", "--rv-photo", "--rv-delay steps"),
    (".rv-self", "Its own trigger (card, grid photo, form section)", "rises 32px", "--rv-lede", "90ms × arrival order, up to 8"),
]
OBSERVER = """(function () {
  var targets = [].slice.call(document.querySelectorAll('[data-reveal]'));
  if (!targets.length || !('IntersectionObserver' in window)) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.documentElement.classList.add('reveal-armed');   // nothing is hidden before this line runs
  var io = new IntersectionObserver(function (entries) {
    var k = 0;
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      io.unobserve(entry.target);                               // once per visit
      if (entry.target.classList.contains('rv-self')) entry.target.style.setProperty('--rv-batch', k++);
      entry.target.classList.add('is-revealed');
    });
  }, { rootMargin: '0px 0px -22% 0px' });                      // when the top passes 78% of the window
  targets.forEach(function (t) { io.observe(t); });
})();"""
MOTION_MARKUP = """<section data-reveal>
  <p class="g-plate rv-eyebrow">Inventory</p>
  <h2 class="g-h2"><span class="ttl-line">Twenty-three cars,</span> <span class="ttl-line">hand-selected in Burlington.</span></h2>
  <p class="g-lede rv-lede">From low-mile collectibles to everyday transportation.</p>
  <ul class="rv-stagger" style="--rv-from: 3"><li>…</li><li>…</li></ul>
  <div class="rv-act"><a class="g-btn g-btn--accent" href="#">Browse inventory</a></div>
</section>
<ul class="g-cards">
  <li class="g-card rv-self" data-reveal>…</li>
</ul>"""

PATTERNS = [
    ("Page head", "The plate, the title in lines, one lede, two actions; on the right three hairline points, the three ways in, or one photograph.", "finance.html",
     '<div class="w w-2col"><div><i class="w-plate"></i><i class="w-h"></i><i class="w-h w-h--s"></i><i class="w-t"></i><i class="w-t w-t--s"></i><span class="w-row"><i class="w-pill w-pill--red"></i><i class="w-pill"></i></span></div><div class="w-list"><i></i><i></i><i></i></div></div>'),
    ("Section head", "The plate, a title, a lede of one or two sentences; content 48px below.", "about.html",
     '<div class="w"><i class="w-plate"></i><i class="w-h w-h--m"></i><i class="w-t"></i><span class="w-row w-gap"><i class="w-card"></i><i class="w-card"></i><i class="w-card"></i></span></div>'),
    ("The bone chapter", "One light band per page at most, for the chapter that changes register.", "sell.html",
     '<div class="w w-bands"><i class="w-band"></i><div class="w-band w-band--bone"><i class="w-plate"></i><span class="w-row"><i class="w-card w-card--bone"></i><i class="w-card w-card--bone"></i><i class="w-card w-card--bone"></i><i class="w-card w-card--bone"></i></span></div><i class="w-band"></i></div>'),
    ("Form page", "Form sections on raised cards; the summary panel sticky on the right; an honest answer in place of the form once sent.", "finance.html#apply",
     '<div class="w w-form"><div class="w-stack"><i class="w-card w-card--tall"></i><i class="w-card w-card--tall"></i><i class="w-card"></i></div><i class="w-panel"></i></div>'),
    ("Inventory grid", "A counted title with the makes as tiles, one filter box, then cards three, two and one across.", "srp.html",
     '<div class="w"><i class="w-h w-h--m"></i><span class="w-row"><i class="w-chip"></i><i class="w-chip"></i><i class="w-chip"></i><i class="w-chip"></i></span><i class="w-bar"></i><span class="w-grid3"><i class="w-card w-card--photo"></i><i class="w-card w-card--photo"></i><i class="w-card w-card--photo"></i></span></div>'),
    ("Car page", "Gallery 60 / decision panel 40; ways to reach the dealer; the record as accordions; standards; photographs; more from the lot.", "cars/bmw-m3-2015.html",
     '<div class="w"><span class="w-6040"><i class="w-photo"></i><i class="w-panel"></i></span><span class="w-row"><i class="w-pill w-pill--red"></i><i class="w-pill w-pill--bone"></i><i class="w-pill"></i></span><i class="w-acc"></i><i class="w-acc"></i></div>'),
    ("Map band", "The map of 600 Faust Rd, edge to edge, last before the footer.", "contact.html",
     '<div class="w w-bands"><span class="w-row w-pad"><i class="w-card"></i><i class="w-panel w-panel--short"></i></span><i class="w-map"></i><i class="w-band w-band--foot"></i></div>'),
]


def swatch_rows():
    rows = []
    for t, d in tokens["color"].items():
        rows.append(f'<tr><td><span class="ds-chip" style="background: var({t})"></span></td><td><code>{t}</code></td><td class="ds-val">{e(d["value"])}</td><td>{e(d["name"])}</td><td>{e(d["use"])}</td></tr>')
    return "\n".join(rows)


def token_rows(key, sample=None):
    rows = []
    for t, d in tokens[key].items():
        extra = ' <span class="ds-tag">handoff name</span>' if d.get("handoff") else ""
        viz = ""
        if sample == "space":
            viz = f'<span class="ds-bar" style="inline-size: var({t})"></span>'
        elif sample == "radius":
            viz = f'<span class="ds-rbox" style="border-radius: var({t})"></span>'
        rows.append(f'<tr><td><code>{t}</code>{extra}</td><td class="ds-val">{e(d["value"])}</td><td>{e(d["name"])}</td><td>{e(d["use"])}{viz}</td></tr>')
    return "\n".join(rows)


pairs_html = "\n".join(
    (lambda r, g: f'<tr><td><span class="ds-pair" style="background: var({bg}); color: var({fg})">Aa</span></td><td>{use}</td><td><code>{fg}</code> on <code>{bg}</code></td><td class="ds-val">{r:.2f}:1</td><td><span class="ds-grade{" is-pass" if g[1] else ""}">{g[0]}</span></td></tr>')(ratio(fg, bg), grade(ratio(fg, bg), large))
    for fg, bg, use, large in PAIRS)

type_html = "\n".join(
    f'<div class="ds-type"><p class="{cls}">{e(sample)}</p><div class="ds-type__doc"><p class="ds-type__name">{name} · <code>.{cls}</code></p><p class="ds-type__spec">{e(spec)}</p><p class="ds-type__use">{use}</p></div></div>'
    for cls, name, sample, spec, use in TYPE_ROLES)


def component_html(cid, title, classes, site, specs, states, rules):
    snippet = C[cid]
    spec_rows = "".join(f"<tr><th scope=\"row\">{k}</th><td>{e(v)}</td></tr>" for k, v in specs)
    return f"""    <article class="ds-comp" id="c-{cid}">
      <header class="ds-comp__head">
        <h3 class="g-h3">{title}</h3>
        <p class="ds-comp__cls"><code>{e(classes)}</code></p>
        <p class="ds-comp__site">On the site: <code>{e(site)}</code></p>
      </header>
      <div class="ds-stage">
{snippet}
      </div>
      <div class="ds-comp__cols">
        <div>
          <p class="ds-k">Spec</p>
          <table class="ds-spec"><tbody>{spec_rows}</tbody></table>
        </div>
        <div>
          <p class="ds-k">States</p>
          <ul class="ds-list">{''.join(f'<li>{e(s)}</li>' for s in states)}</ul>
          <p class="ds-k">Rules</p>
          <ul class="ds-list">{''.join(f'<li>{e(r)}</li>' for r in rules)}</ul>
        </div>
      </div>
      <details class="ds-code">
        <summary>HTML</summary>
        <pre><code>{e(snippet)}</code></pre>
      </details>
    </article>"""


components_html = "\n".join(component_html(*c) for c in COMPONENTS)
roles_html = "\n".join(f'<tr><td><code>{c}</code></td><td>{w}</td><td>{g}</td><td><code>{d}</code></td><td>{s}</td></tr>' for c, w, g, d, s in ROLES)
map_html = "\n".join(f'<tr><td><code>{a}</code></td><td><code>{b}</code></td><td>{c}</td></tr>' for a, b, c in MAP)
patterns_html = "\n".join(
    f'<li class="ds-pattern">{wire}<p class="g-h4">{t}</p><p class="ds-pattern__p">{d}</p><p class="ds-pattern__link"><a href="{PREVIEW}{link}">See it on the preview</a></p></li>'
    for t, d, link, wire in PATTERNS)
comp_nav = " · ".join(f'<a href="#c-{c[0]}">{c[1]}</a>' for c in COMPONENTS)

INCLUDE = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400..700&family=Zilla+Slab:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="geneva-ds.css">

<body class="g-page">"""

NAV = [("start", "Start"), ("tokens", "Tokens"), ("type", "Type"), ("components", "Components"), ("motion", "Motion"), ("patterns", "Page patterns"), ("rules", "Rules"), ("map", "Site map")]
nav_html = "".join(f'<a href="#{i}">{t}</a>' for i, t in NAV)

page = f"""<!doctype html>
<!-- Geneva Motor Haus — design system, developer handoff.
     GENERATED by tools/build-ds-static.py on {DATE}. Standalone: tokens.css,
     geneva-ds.css and docs.css; no JavaScript. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Geneva Motor Haus — Design system</title>
<meta name="description" content="Tokens, components, motion and rules for building Geneva Motor Haus.">
<link rel="icon" href="{badge_img}" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400..700&family=Zilla+Slab:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="geneva-ds.css">
<link rel="stylesheet" href="docs.css">
</head>
<body class="g-page">

<header class="ds-top">
  <div class="g-shell ds-top__in">
    <a class="ds-brand" href="{PREVIEW}index_finale_v2.html"><img src="{badge_img}" alt="" width="40" height="40"><span>Geneva Motor Haus</span></a>
    <nav class="ds-nav" aria-label="Sections">{nav_html}</nav>
  </div>
</header>

<main>
  <section class="ds-hero">
    <div class="g-shell">
      <p class="g-plate">Design system · developer handoff</p>
      <h1 class="g-h1 ds-hero__t"><span class="g-line">Build Geneva</span> <span class="g-line">from these parts.</span></h1>
      <p class="g-lede ds-hero__lede">Tokens, eleven components, the entrance motion, the page patterns and the rules behind them. Everything here is plain HTML and CSS; the values come from the live site's stylesheets, and every size was measured from its rendered components.</p>
      <ul class="ds-files">
        <li><a href="tokens.css"><code>tokens.css</code></a><span>every token as a custom property</span></li>
        <li><a href="tokens.json"><code>tokens.json</code></a><span>the same tokens as data</span></li>
        <li><a href="geneva-ds.css"><code>geneva-ds.css</code></a><span>the components and motion roles</span></li>
        <li><a href="{PREVIEW}index_finale_v2.html">Live preview</a><span>the site these were taken from</span></li>
      </ul>
      <p class="g-meta">Generated {DATE} from assets/css/tokens.css and geneva-final-v2.css.</p>
    </div>
  </section>

  <section class="ds-sec" id="start">
    <div class="g-shell">
      <p class="g-plate">Start</p>
      <h2 class="g-h2 ds-sec__t">Two stylesheets, two faces.</h2>
      <div class="ds-cols">
        <div>
          <p class="g-body">Load the fonts, then <code>tokens.css</code>, then <code>geneva-ds.css</code>. Put <code>g-page</code> on the body for the ground, the ink and box sizing. Components are self-contained classes; nothing depends on page structure.</p>
          <ul class="ds-list">
            <li>Use tokens, never raw colours or sizes.</li>
            <li>Nothing functional below 14px (<code>--t-micro</code>).</li>
            <li>Every text pair meets WCAG AA; the table under Tokens shows each ratio.</li>
            <li>Every animation has a reduced-motion path: the page arrives complete.</li>
            <li>Browsers: current Chrome, Safari, Firefox, Edge. Uses <code>clamp()</code>, <code>color-mix()</code>, <code>:user-invalid</code>, the <code>translate</code> property.</li>
          </ul>
        </div>
        <pre class="ds-pre"><code>{e(INCLUDE)}</code></pre>
      </div>
    </div>
  </section>

  <section class="ds-sec" id="tokens">
    <div class="g-shell">
      <p class="g-plate">Tokens</p>
      <h2 class="g-h2 ds-sec__t">One ground, one red, one plate.</h2>
      <h3 class="g-h4 ds-sub">Colour</h3>
      <div class="ds-scroll"><table class="ds-table"><thead><tr><th></th><th>Token</th><th>Value</th><th>Name</th><th>Use</th></tr></thead><tbody>
{swatch_rows()}
      </tbody></table></div>
      <h3 class="g-h4 ds-sub">Contrast</h3>
      <div class="ds-scroll"><table class="ds-table"><thead><tr><th></th><th>Used for</th><th>Pair</th><th>Ratio</th><th>Grade</th></tr></thead><tbody>
{pairs_html}
      </tbody></table></div>
      <div class="ds-cols">
        <div>
          <h3 class="g-h4 ds-sub">Space</h3>
          <div class="ds-scroll"><table class="ds-table ds-table--tight"><tbody>
{token_rows("space", "space")}
          </tbody></table></div>
        </div>
        <div>
          <h3 class="g-h4 ds-sub">Radius</h3>
          <div class="ds-scroll"><table class="ds-table ds-table--tight"><tbody>
{token_rows("radius", "radius")}
          </tbody></table></div>
          <h3 class="g-h4 ds-sub">Layout</h3>
          <div class="ds-scroll"><table class="ds-table ds-table--tight"><tbody>
{token_rows("layout")}
          </tbody></table></div>
        </div>
      </div>
      <h3 class="g-h4 ds-sub">Type tokens</h3>
      <div class="ds-scroll"><table class="ds-table ds-table--tight"><tbody>
{token_rows("type")}
      </tbody></table></div>
      <h3 class="g-h4 ds-sub">Motion tokens</h3>
      <div class="ds-scroll"><table class="ds-table ds-table--tight"><tbody>
{token_rows("motion")}
      </tbody></table></div>
    </div>
  </section>

  <section class="ds-sec" id="type">
    <div class="g-shell">
      <p class="g-plate">Type</p>
      <h2 class="g-h2 ds-sec__t">Zilla Slab says, Instrument Sans reads.</h2>
      <div class="ds-types">
{type_html}
      </div>
    </div>
  </section>

  <section class="ds-sec" id="components">
    <div class="g-shell">
      <p class="g-plate">Components</p>
      <h2 class="g-h2 ds-sec__t">Eleven parts, with their code.</h2>
      <p class="g-body ds-comp-nav">{comp_nav}</p>
{components_html}
    </div>
  </section>

  <section class="ds-sec" id="motion">
    <div class="g-shell">
      <p class="g-plate">Motion</p>
      <h2 class="g-h2 ds-sec__t">Once, stepped, then still.</h2>
      <p class="g-body">A section opts in with <code>data-reveal</code> and marks its parts with a role. One observer adds <code>is-revealed</code> once, when the section's top passes 78% of the window. The CSS writes only the hidden state, so nothing stays transformed afterwards. Under reduced motion the observer never arms and nothing is ever hidden.</p>

      <div class="ds-demo">
        <input class="ds-demo__toggle" type="checkbox" id="ds-replay">
        <div class="ds-demo__stage">
          <div>
            <p class="g-plate d-eyebrow">Inventory</p>
            <p class="g-h2 ds-demo__t"><span class="g-line d-line">Twenty-three cars,</span> <span class="g-line d-line">hand-selected in Burlington.</span></p>
            <p class="g-lede d-lede">From low-mile collectibles to everyday transportation.</p>
            <ul class="ds-demo__list"><li class="d-item">Porsche</li><li class="d-item">BMW</li><li class="d-item">Lexus</li><li class="d-item">Ford</li></ul>
            <div class="d-act"><span class="g-btn g-btn--accent">Browse inventory {ARROW}</span></div>
          </div>
          <figure class="ds-demo__photo d-photo"><img src="{photo_img}" alt="A white Porsche 911 on a desert road below snow-capped mountains" width="1000" height="700"></figure>
        </div>
        <div class="ds-demo__bar"><label class="g-btn g-btn--line" for="ds-replay">Replay the entrance {ARROW}</label><p class="g-meta">This demo runs on CSS animations so the page needs no script; production uses the roles and the observer below.</p></div>
      </div>

      <div class="ds-scroll"><table class="ds-table"><thead><tr><th>Role</th><th>What</th><th>Gesture</th><th>Duration</th><th>Delay</th></tr></thead><tbody>
{roles_html}
      </tbody></table></div>
      <div class="ds-cols">
        <div><p class="ds-k">Markup</p><pre class="ds-pre"><code>{e(MOTION_MARKUP)}</code></pre></div>
        <div><p class="ds-k">The observer (the only script)</p><pre class="ds-pre"><code>{e(OBSERVER)}</code></pre></div>
      </div>
      <ul class="ds-list">
        <li>Scroll-triggered, never scroll-linked; one entrance per visit.</li>
        <li>Transform and opacity only; nothing animates layout.</li>
        <li>Hover: a button's arrow moves 2px, a card's photograph scales to 1.04; nothing else moves under the pointer.</li>
        <li>Rejected on this project: scroll-drawn rings and lines.</li>
      </ul>
    </div>
  </section>

  <section class="ds-sec" id="patterns">
    <div class="g-shell">
      <p class="g-plate">Page patterns</p>
      <h2 class="g-h2 ds-sec__t">Seven arrangements, every page.</h2>
      <ul class="ds-patterns">
{patterns_html}
      </ul>
    </div>
  </section>

  <section class="ds-sec" id="rules">
    <div class="g-shell">
      <p class="g-plate">Rules</p>
      <h2 class="g-h2 ds-sec__t">What holds on every page.</h2>
      <div class="ds-cols">
        <div>
          <h3 class="g-h4 ds-sub">Content</h3>
          <ul class="ds-list">
            <li>Words and figures are the client's, trimmed, never extended. Each page on the site has a ledger of every claim and its source (docs/content-ledger-*.json).</li>
            <li>Dated figures carry their date on screen: prices and mileages read “as listed 14 Sep 2026”.</li>
            <li>Photographs are Geneva's own. No stock; no photograph under a car it is not.</li>
            <li>Left out on purpose: “12+ years”, “5000+ sold”, “98%”, “within 24 hours”, “best price”, “no hidden fees” — unconfirmed by the client.</li>
            <li>Forms keep the AAN field names and required sets.</li>
          </ul>
        </div>
        <div>
          <h3 class="g-h4 ds-sub">Accessibility</h3>
          <ul class="ds-list">
            <li>WCAG AA contrast for every text pair (see Tokens).</li>
            <li>14px minimum for anything functional.</li>
            <li>Visible focus: 2px --ink ring (2–3px offset); inside the control on list rows.</li>
            <li>Every field has a label; errors are a colour plus the browser's message, never colour alone.</li>
            <li>Reduced motion: nothing hidden, nothing moving.</li>
            <li>The same content on a phone; the summary panel is the one thing hidden, because the form is complete without it.</li>
          </ul>
          <h3 class="g-h4 ds-sub">Never</h3>
          <ul class="ds-list">
            <li>Red text on the dark ground; underlined navigation; gradient buttons; decorative shadows.</li>
            <li>A numbered side rail that reads as a document outline.</li>
            <li>A placeholder instead of a label, or a mailto link dressed as a form.</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="ds-sec" id="map">
    <div class="g-shell">
      <p class="g-plate">Site map</p>
      <h2 class="g-h2 ds-sec__t">Where each part lives on the site.</h2>
      <p class="g-body">The preview site is generated by <code>tools/build-*.py</code> in the repository; its header, menu and footer come from <code>index_finale_v2.html</code>. These are the classes to look for there.</p>
      <div class="ds-scroll"><table class="ds-table"><thead><tr><th>Handoff class</th><th>Site class</th><th>Site file</th></tr></thead><tbody>
{map_html}
      </tbody></table></div>
    </div>
  </section>
</main>

<footer class="ds-foot">
  <div class="g-shell"><p class="g-meta">Geneva Motor Haus · 600 Faust Rd, Unit 8, Burlington, WI 53105 · design system generated {DATE}</p></div>
</footer>
</body>
</html>
"""

# ---- 5. write --------------------------------------------------------------------------------------
lines = [f"/* Geneva Motor Haus — tokens. GENERATED by tools/build-ds-static.py on {DATE}",
         "   from assets/css/tokens.css and assets/css/geneva-final-v2.css. Do not edit; rebuild. */", ":root {"]
for key, items in tokens.items():
    lines.append(f"  /* {key} */")
    for t, d in items.items():
        note = f"  /* {d['name']}" + (f" — {d['use']}" if d["use"] else "") + (" · named for handoff" if d.get("handoff") else "") + " */"
        lines.append(f"  {t}: {d['value']};{note}")
lines.append("}")
(OUT / "tokens.css").write_text("\n".join(lines) + "\n")
(OUT / "tokens.json").write_text(json.dumps({"generated": DATE, "source": ["assets/css/tokens.css", "assets/css/geneva-final-v2.css"], "tokens": tokens}, indent=2, ensure_ascii=False) + "\n")
(OUT / "index.html").write_text(page)
print(f"design-system/: {sum(len(v) for v in tokens.values())} tokens, {len(COMPONENTS)} components, {len(PAIRS)} contrast pairs; car example {car_name}, sold example {sold_name}")
