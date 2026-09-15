#!/usr/bin/env python3
"""Geneva Motor Haus — build ds.html, the design system.

ONE PAGE, BUILT FROM THE SITE ITSELF. It loads the site's own stylesheets,
so every component on it is the real component, and ds-v1.js reads every
token value, contrast ratio and type size from the live CSS when the page
opens — nothing on this page is a transcription that can drift.

The car card, the sold card, the detail page's pills and its accordion are
lifted from the built pages (srp.html, sold.html, cars/bmw-m3-2015.html), so
build this after the page generators:

    python3 tools/build-ds.py
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gmh_chrome import ROOT, chrome  # noqa: E402

OUT = ROOT / "ds.html"
ARROW = ('<svg class="btn__arrow" width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">'
         '<path d="M2 6.5h9M7.4 3 11 6.5 7.4 10" stroke="currentColor" stroke-width="1.3"/></svg>')
CHECK = ('<svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">'
         '<path d="M2.5 7.3 5.6 10.2 11.5 3.8" stroke="currentColor" stroke-width="1.6"/></svg>')

top, footer = chrome()


def lift(path, pattern):
    text = (ROOT / path).read_text()
    m = re.search(pattern, text, re.S)
    if not m:
        raise SystemExit(f"build-ds: could not find {pattern!r} in {path} — rebuild the pages first")
    return m.group(0).replace(" rv-self", "").replace(" data-reveal", "")


card = lift("srp.html", r'<li class="srp-card[^"]*"[^>]*>.*?</li>')
sold_card = lift("sold.html", r'<li class="srp-card is-sold[^"]*"[^>]*>.*?</li>')
vdp_pills = lift("cars/bmw-m3-2015.html", r'<div class="vdp-act__contact">.*?</div>').replace('href="../', 'href="')
vdp_acc = lift("cars/bmw-m3-2015.html", r'<details class="vdp-acc" id="shipping">.*?</details>').replace('href="../', 'href="')

# ---- colour --------------------------------------------------------------------------
# (token, name, where it is used, chip background, chip ink, kind)
COLORS = [
    ("Ground", [
        ("--bg", "Page ground", "Every page. Photographs sit on it uncut.", "--bg", "--ink", ""),
        ("--bg-raised", "Raised", "Cards, panels, form sections, accordions.", "--bg-raised", "--ink", ""),
        ("--bg-sunk", "Sunk", "The drop zone, the terms box, wells.", "--bg-sunk", "--ink", ""),
        ("--bg-black", "Band", "Dark bands and the footer.", "--bg-black", "--ink", ""),
    ]),
    ("Ink", [
        ("--ink", "Ink", "Titles, values, anything read first.", "--bg", "--ink", "ink"),
        ("--ink-2", "Ink 2", "Body, ledes, field labels.", "--bg", "--ink-2", "ink"),
        ("--ink-3", "Ink 3", "Notes, meta, inactive states. Never below 14px.", "--bg", "--ink-3", "ink"),
    ]),
    ("Rules", [
        ("--rule", "Rule", "Card borders, section hairlines.", "--bg", "--rule", "rule"),
        ("--rule-strong", "Rule strong", "Inputs, outline pills, list hairlines.", "--bg", "--rule-strong", "rule"),
    ]),
    ("The bone chapter", [
        ("--bone", "Bone", "The one light band a page may have.", "--bone", "--bone-ink", ""),
        ("--bone-ink", "Bone ink", "Titles on bone.", "--bone", "--bone-ink", "ink"),
        ("--bone-ink-2", "Bone ink 2", "Body on bone.", "--bone", "--bone-ink-2", "ink"),
        ("--bone-rule", "Bone rule", "Hairlines on bone.", "--bone", "--bone-rule", "rule"),
    ]),
    ("Barn red", [
        ("--accent", "Accent", "The barn roof in the badge.", "--accent", "--action-ink", ""),
        ("--action", "Action", "Primary buttons, the Sold tag.", "--action", "--action-ink", ""),
        ("--action-hover", "Action hover", "The primary button under the pointer.", "--action-hover", "--action-ink", ""),
        ("--accent-deep", "Accent deep", "Step numerals on bone.", "--bone", "--accent-deep", "ink"),
    ]),
    ("The plate", [
        ("--eyebrow-plate", "Plate", "Every eyebrow; the current step in a form panel.", "--eyebrow-plate", "--eyebrow-ink", ""),
        ("--eyebrow-ink", "Plate ink", "The label on the plate.", "--eyebrow-plate", "--eyebrow-ink", "ink"),
    ]),
]


def swatch(token, name, use, chip_bg, chip_fg, kind):
    if kind == "rule":
        chip = f'<div class="ds-sw__chip ds-sw__chip--rule" style="background: var({chip_bg}); --sw: var({chip_fg})" aria-hidden="true"><i></i><i></i><i></i></div>'
    else:
        chip = f'<div class="ds-sw__chip" style="background: var({chip_bg}); color: var({chip_fg})" aria-hidden="true"><span>Aa</span></div>'
    return (f'<li class="ds-sw">{chip}<div class="ds-sw__body"><p class="ds-sw__name">{name}</p>'
            f'<p class="ds-sw__token"><code class="ds-code">{token}</code><span class="ds-sw__val" data-token-value="{token}">—</span></p>'
            f'<p class="ds-sw__use">{use}</p></div></li>')


colors_html = "\n".join(
    f'      <div class="ds-group"><p class="ds-group__t">{group}</p><ul class="ds-swatches rv-stagger" style="--rv-from: 0">'
    + "".join(swatch(*s) for s in items) + "</ul></div>"
    for group, items in COLORS)

PAIRS = [
    ("--ink", "--bg", "Titles on the ground", ""),
    ("--ink-2", "--bg", "Body on the ground", ""),
    ("--ink-3", "--bg", "Notes on the ground", ""),
    ("--ink-2", "--bg-raised", "Body on cards and panels", ""),
    ("--ink-3", "--bg-raised", "Notes on cards and panels", ""),
    ("--ink-3", "--bg-sunk", "Notes in wells", ""),
    ("--bone-ink", "--bone", "Titles on bone", ""),
    ("--bone-ink-2", "--bone", "Body on bone", ""),
    ("--accent-deep", "--bone", "Step numerals on bone (large text)", " data-large"),
    ("--action-ink", "--action", "Button label on red", ""),
    ("--eyebrow-ink", "--eyebrow-plate", "The plate's label", ""),
    ("--ink", "--eyebrow-plate", "The current step in a form panel", ""),
    ("--accent", "--bg", "Red on the ground — a fill, never text", " data-fill"),
]
pairs_html = "\n".join(
    f'          <tr data-contrast data-fg="{fg}" data-bg="{bg}"{flag}><td><span class="ds-pair" style="background: var({bg}); color: var({fg})">Aa</span></td>'
    f'<td>{use}</td><td><code class="ds-code">{fg}</code> on <code class="ds-code">{bg}</code></td><td class="ds-num" data-ratio>—</td><td data-grade>—</td></tr>'
    for fg, bg, use, flag in PAIRS)

# ---- type -------------------------------------------------------------------------------
TYPE = [
    ("ds-t-h1", "Page title", '<div class="is-fin"><h3 class="fin-head__title ds-flat" id="ds-t-h1">Get approved today.</h3></div>', "One per page, in lines (<code class=\"ds-code\">.ttl-line</code>)."),
    ("ds-t-h2", "Section title", '<div class="is-fin"><h3 class="fin-apply__title ds-flat" id="ds-t-h2">Sell us your car.</h3></div>', "Under a plate, over a lede."),
    ("ds-t-h3", "Card title", '<div class="is-fin"><p class="fin-sec__t" id="ds-t-h3">Your vehicle</p></div>', "Form sections, panels, cards."),
    ("ds-t-h4", "Small title", '<div class="is-fin"><p class="fin-point__t ds-flat" id="ds-t-h4">Competitive rates</p></div>', "Points, reasons, list heads."),
    ("ds-t-lede", "Lede", '<div class="is-fin"><p class="fin-head__lede ds-flat" id="ds-t-lede">A fair, no-obligation appraisal — whether you’re selling a luxury vehicle, an exotic or a daily driver.</p></div>', "The paragraph under a page title. Measure 44–52ch."),
    ("ds-t-body", "Body", '<div class="is-fin"><p class="fin-point__p" id="ds-t-body">We work with multiple lenders to find the rate available for your situation.</p></div>', "Everything else that is read. Measure ≤ 60ch."),
    ("ds-t-car", "Car name", '<div class="is-srp"><p class="srp-card__name ds-flat" id="ds-t-car"><span class="srp-card__year">2015</span> M3</p></div>', "The year and model on a card."),
    ("ds-t-plate", "Plate", '<p class="micro gmh-plate" id="ds-t-plate">Inventory</p>', "Names a section. Upper case, the label's own width."),
    ("ds-t-label", "Field label", '<div class="is-fin"><div class="fin-field"><label id="ds-t-label">First name<span class="fin-req" aria-hidden="true">*</span></label></div></div>', "Every field has one. Placeholders never replace it."),
]
type_html = "\n".join(
    f'        <li class="ds-type"><div class="ds-type__spec">{spec}</div><div class="ds-type__doc"><p class="ds-type__name">{name}</p>'
    f'<p class="ds-type__meta" data-measure="{sid}">—</p><p class="ds-type__use">{use}</p></div></li>'
    for sid, name, spec, use in TYPE)

# ---- space, layout, radius -------------------------------------------------------------
SPACE = [f"--sp-{n}" for n in range(1, 13)]
space_html = "\n".join(
    f'        <li><code class="ds-code">{t}</code><span class="ds-num" data-token-value="{t}">—</span><span class="ds-space__bar" style="inline-size: var({t})"></span></li>'
    for t in SPACE)
LAYOUT = [
    ("--container", "The content measure, gutters included."),
    ("--page-gutter", "Side padding at every width; never zero."),
    ("--sec", "A section's vertical padding."),
    ("--sec-lg", "A chapter's vertical padding."),
    ("--gf-head-h", "The header at the top of a page; page heads start below it."),
    ("--gf-head-h-c", "The compact header; sticky things sit under it."),
]
layout_html = "\n".join(f'          <tr><td><code class="ds-code">{t}</code></td><td class="ds-num" data-token-value="{t}">—</td><td>{u}</td></tr>' for t, u in LAYOUT)
RADII = [
    ("0", "The plate, hairline lists, full-bleed bands"),
    ("var(--r-control)", "<code class=\"ds-code\">--r-control</code> · small controls"),
    ("8px", "Thumbnails in a photograph strip or drop zone"),
    ("10px", "Inputs, selects, the terms box"),
    ("12px", "Cards, panels, form sections, accordions"),
    ("var(--r-panel)", "<code class=\"ds-code\">--r-panel</code> · homepage panels"),
    ("16px", "Large photographs and the visit card"),
    ("999px", "Buttons, pills, toggles"),
]
radii_html = "\n".join(f'        <li><span class="ds-radius__box" style="border-radius: {r}"></span><p class="ds-radius__v">{r.replace("var(", "").replace(")", "")}</p><p class="ds-radius__use">{u}</p></li>' for r, u in RADII)

# ---- motion --------------------------------------------------------------------------------
DUR = ["--dur-1", "--dur-2", "--dur-3", "--dur-4", "--rv-step", "--rv-cta", "--rv-lede", "--rv-line", "--rv-photo"]
dur_html = "\n".join(f'          <tr><td><code class="ds-code">{t}</code></td><td class="ds-num" data-token-value="{t}">—</td></tr>' for t in DUR)
ROLES = [
    (".ttl-line", "A headline line", "slides in from the left, 56px", "--rv-line", "one step (130ms) per line"),
    (".rv-eyebrow", "The plate", "fades with 6px of travel", "--rv-cta", "none"),
    (".rv-lede", "The paragraph", "rises 32px", "--rv-lede", "2.2 steps, after the lines"),
    (".rv-act", "The buttons", "settle 10px", "--rv-cta", "3.4 steps, last"),
    (".rv-item · .rv-stagger", "Blocks in order", "rise 24px", "--rv-lede", "from --rv-from (2.6 steps), 0.7 apart"),
    (".rv-photo", "A photograph", "floats up 64px", "--rv-photo", "--rv-delay steps"),
    (".rv-self", "Its own trigger: a card, a photograph in a grid, a form section", "rises 32px (64px as a photograph)", "--rv-lede", "90ms per arrival, up to eight"),
]
roles_html = "\n".join(f'          <tr><td><code class="ds-code">{c}</code></td><td>{w}</td><td>{g}</td><td><code class="ds-code">{d}</code></td><td>{s}</td></tr>' for c, w, g, d, s in ROLES)

# ---- build ------------------------------------------------------------------------------------
GENS = [
    ("index_finale_v2.html", "edited by hand", "The homepage. Its header, menu and footer are the source for every page."),
    ("srp.html", "tools/build-srp.py --force", "assets/data/inventory-2026-09-14.json"),
    ("sold.html", "tools/build-sold.py", "assets/data/sold-2026-09-14.json"),
    ("cars/*.html", "tools/build-vdp.py", "The inventory JSON: one page per car."),
    ("finance.html", "tools/build-finance.py", "The AAN finance application and the inventory."),
    ("sell.html", "tools/build-sell.py", "The AAN sell form (docs/source) and /sell-your-car."),
    ("about.html", "tools/build-about.py", "genevamotorhaus.com/about and its photographs."),
    ("contact.html", "tools/build-contact.py", "The AAN contacts form and /contact."),
    ("ds.html", "tools/build-ds.py", "This page. Build it last: it lifts samples from the pages above."),
]
gens_html = "\n".join(f'          <tr><td><code class="ds-code">{p}</code></td><td><code class="ds-code">{t}</code></td><td>{s}</td></tr>' for p, t, s in GENS)
CSS_ORDER = [
    ("tokens.css", "The token layer: colour, type, space, radius, motion."),
    ("main.css · v2.css · v3.css", "The base the homepage grew from: buttons, .micro, .ttl-line, the section-entry system."),
    ("geneva-final-v2.css", "Geneva's layer: the palette (F21), the plate (F24), header and footer, the homepage, and the entrance roles (F25)."),
    ("srp-v2 · vdp-v2 · finance-v2 · about-v2 · sell-v2 · contact-v2", "One layer per page, scoped to a body class (.is-srp, .is-fin …). finance-v2 is the shared form layer."),
    ("main-final-v2.js · geneva-final-v2.js", "Header, menu, search, and the one observer that plays every entrance."),
]
css_html = "\n".join(f'          <tr><td><code class="ds-code">{f}</code></td><td>{d}</td></tr>' for f, d in CSS_ORDER)

NAV = [("principles", "Principles"), ("color", "Colour"), ("type", "Type"), ("space", "Space"), ("radius", "Radius"),
       ("motion", "Motion"), ("components", "Components"), ("patterns", "Page patterns"), ("content", "Content"), ("build", "Build")]
nav_html = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in NAV)


def comp(title, cls, used, rules, stage, stage_cls=""):
    return (f'      <article class="ds-comp">\n        <div class="ds-comp__stage{stage_cls}">\n{stage}\n        </div>\n'
            f'        <div class="ds-comp__doc"><h3 class="ds-comp__t">{title}</h3><p class="ds-comp__cls">{cls}</p>'
            f'<p class="ds-comp__used">{used}</p><ul class="ds-comp__rules">' + "".join(f"<li>{r}</li>" for r in rules) + "</ul></div>\n      </article>")


C = lambda s: f'<code class="ds-code">{s}</code>'  # noqa: E731
components = "\n".join([
    comp("Buttons", f"{C('.btn.btn--accent')} {C('.btn--line')} {C('.btn--fill')}", "Every page: page heads, forms, cards' onward links.",
         ["Accent is the one primary action in view; line is the second.", "Upper-case label, the arrow nudges 2px on hover and does nothing under reduced motion.", "Never a gradient, never a shadow."],
         f'          <a class="btn btn--accent" href="srp.html">Browse inventory {ARROW}</a>\n          <a class="btn btn--line" href="tel:+12622496777">Call (262) 249-6777 {ARROW}</a>\n          <a class="btn btn--fill" href="contact.html">Ask about shipping {ARROW}</a>'),
    comp("The plate", f"{C('.micro.gmh-plate')}", "Over every page and section title, on the dark and on bone.",
         ["The label's own width, 14px upper case, no radius.", f"Colour from {C('--eyebrow-plate')} and {C('--eyebrow-ink')} only.", "It names; it is never a link or a button."],
         '          <p class="micro gmh-plate">Inventory</p>\n          <p class="micro gmh-plate">How it works</p>'),
    comp("Pills", f"{C('.vdp-pill')} {C('.ct-when')} {C('.ct-social')}", "Car pages (call, email, financing), the contact form's best time, social links.",
         ["A pill is a small action or a choice among few.", "Chosen or primary state: bone fill or red fill; otherwise a strong rule.", "Radio pills are real radios; the label is the target."],
         '          <div class="is-vdp">' + vdp_pills + '</div>\n'
         '          <div class="is-fin is-contact"><fieldset class="ct-when"><legend>Best time to contact<span class="fin-req" aria-hidden="true">*</span></legend><div class="ct-when__opts">'
         '<label><input type="radio" name="ds-when" value="morning"><span>Morning</span></label><label><input type="radio" name="ds-when" value="afternoon" checked><span>Afternoon</span></label>'
         '<label><input type="radio" name="ds-when" value="evening"><span>Evening</span></label></div></fieldset></div>'),
    comp("Car card", f"{C('li.srp-card')} · sold: {C('.is-sold')} + {C('.srp-card__tag')}", "Inventory, Sold, and “More from the lot” on every car page.",
         ["The whole card is one link to the car's own page; sold cards are not links.", "Photograph 3:2 on top; make, year and model, spec line, then pills with price, mileage and body.", "Prices and mileages are dated on the page they appear on."],
         '          <div class="is-srp"><ul class="srp-grid ds-cards">' + card + sold_card + '</ul></div>'),
    comp("Form fields", f"{C('.fin-sec')} {C('.fin-grid')} {C('.fin-field')} {C('.fin-toggle')} {C('.fin-check')}", "Financing, Sell your car, Contact — the shared form layer (finance-v2.css).",
         ["A section is a raised card with a numbered legend; fields sit on six columns and stack on a phone.", "Every field has a label; required fields carry a star. The empty required field below shows the error state after a send.", "Fields keep the AAN names, so the forms can be wired to AAN unchanged."],
         '          <div class="is-fin"><form class="fin-form was-sent ds-form" novalidate onsubmit="return false"><fieldset class="fin-sec"><legend class="fin-sec__head"><span class="fin-sec__n">01</span><span class="fin-sec__t">Your vehicle</span></legend>'
         '<div class="fin-grid"><div class="fin-field f-2"><label for="ds-year">Year<span class="fin-req" aria-hidden="true">*</span></label><select id="ds-year"><option>2008</option><option>2015</option></select></div>'
         '<div class="fin-field f-2"><label for="ds-make">Make<span class="fin-req" aria-hidden="true">*</span></label><input id="ds-make" value="Porsche"></div>'
         '<div class="fin-field f-2"><label for="ds-model">Model<span class="fin-req" aria-hidden="true">*</span></label><input id="ds-model" required placeholder="Required"></div>'
         '<div class="fin-field f-6"><label for="ds-msg">Message</label><textarea id="ds-msg" rows="3" placeholder="Tell us how we can help"></textarea></div></div>'
         '<label class="fin-toggle ds-gap"><input type="checkbox" checked><span class="fin-toggle__track" aria-hidden="true"></span><span class="fin-toggle__text">Apply with a co-applicant</span></label>'
         '<label class="fin-check fin-check--agree"><input type="checkbox" checked><span>Please note that by completing this form, you agree to being contacted via text, phone and email.</span></label></fieldset></form></div>'),
    comp("Summary panel", f"{C('aside.fin-rail')} {C('.fin-step')} {C('.fin-step__s')}", "Beside the Financing and Sell forms; hidden under 960px.",
         ["It says what is filled and what each step still needs — never a bare numbered outline.", "The step in view sits on the plate; complete steps carry a check.", "The panel's button submits the same form."],
         '          <div class="is-fin is-sell ds-rail-demo"><aside class="fin-rail" aria-label="Summary panel example"><div class="fin-rail__head"><p class="fin-rail__t">Your car</p><p class="sl-car is-set">2008 Porsche 911 Turbo</p>'
         '<div class="fin-rail__progress"><p class="fin-rail__count"><b>4</b> of 11 required fields filled</p><span class="fin-rail__bar" aria-hidden="true"><span style="transform: scaleX(0.36)"></span></span></div></div>'
         f'<ol class="fin-rail__steps"><li><a class="fin-step" href="#components"><span class="fin-step__t">Your vehicle</span><span class="fin-step__s is-done">{CHECK}3 / 3 required</span></a></li>'
         f'<li><a class="fin-step" href="#components" aria-current="step"><span class="fin-step__t">Photographs</span><span class="fin-step__s is-done">{CHECK}2 attached</span></a></li>'
         '<li><a class="fin-step" href="#components"><span class="fin-step__t">Contact</span><span class="fin-step__s">1 / 8 required</span></a></li></ol>'
         f'<div class="fin-rail__foot"><button class="btn btn--accent fin-rail__send" type="button">Submit for appraisal {ARROW}</button><p class="fin-rail__help">Questions? Call <a href="tel:+12622496777">(262) 249-6777</a></p></div></aside></div>'),
    comp("Accordion", f"{C('details.vdp-acc')}", "Car pages: about this car, ask, estimate a payment, shipping.",
         ["Native disclosure: works without script, and find-in-page reaches a closed one.", "The plus loses its vertical bar when open — one crisp 280ms gesture."],
         '          <div class="is-vdp ds-acc">' + vdp_acc + '</div>'),
    comp("Step plates", f"{C('ol.sell__steps')} on bone", "The homepage's Sell chapter and Sell your car.",
         ["Four, because Geneva's process has four.", "The numeral in accent deep, the title straight under it, one sentence each."],
         '          <div class="is-gmh is-v3 is-sell"><ol class="sell__steps sl-steps">'
         '<li><span class="micro sell__step-n">01</span><span class="micro sell__step-t">Submit your vehicle info</span><p class="sl-steps__p">Fill out the form with your vehicle details and contact information.</p></li>'
         '<li><span class="micro sell__step-n">02</span><span class="micro sell__step-t">Get your appraisal</span><p class="sl-steps__p">Our team reviews your information and contacts you with an offer.</p></li>'
         '</ol></div>', " ds-comp__stage--bone"),
    comp("Hairline list", f"{C('ul.fin-points')} {C('ul.ct-ways')}", "Beside a page title: Financing's three points, Contact's three ways in.",
         ["Rows on strong rules, a short title and one sentence; no cards, no icons."],
         '          <div class="is-fin ds-wide"><ul class="fin-points"><li class="fin-point"><p class="fin-point__t">Competitive rates</p><p class="fin-point__p">We work with multiple lenders to find the rate available for your situation.</p></li>'
         '<li class="fin-point"><p class="fin-point__t">Flexible terms</p><p class="fin-point__p">A variety of loan terms and payment options to fit your budget.</p></li></ul></div>'),
    comp("Photograph drop", f"{C('label.sl-drop')} {C('.sl-thumbs')}", "Sell your car: up to twelve files, as AAN allows.",
         ["The whole field is the target; the file input stays a real input.", "Each file shows as a thumbnail with its own remove button."],
         '          <div class="is-fin is-sell ds-wide"><label class="sl-drop"><input type="file" multiple accept=".jpg,.jpeg,.png,.gif,.pdf,.doc">'
         '<span class="sl-drop__btn">Add photographs</span><span class="sl-drop__t">or drag them here</span><span class="sl-drop__note">Up to 12 files · JPG, PNG, GIF, PDF or DOC</span></label></div>'),
])

PATTERNS = [
    ("Page head", "The plate, the title in lines, one lede, two actions; on the right, either three hairline points, the three ways in, or one photograph.", [("finance.html", "Financing"), ("contact.html", "Contact"), ("sell.html", "Sell your car")]),
    ("Section head", "The plate, a title, a lede of one or two sentences. The section's own content starts 48px below.", [("about.html", "About")]),
    ("The bone chapter", "One light band per page at most, for the chapter that changes register: the steps, the story.", [("sell.html#sl-how-title", "Sell · how it works"), ("about.html#ab-story-title", "About · story")]),
    ("Form page", "Form sections on raised cards, left; the summary panel, right and sticky; an honest answer in place of the form once sent.", [("finance.html#apply", "Financing"), ("sell.html#apply", "Sell your car")]),
    ("Inventory grid", "A counted title with the makes as tiles, one box of filters, then cards three, two and one across.", [("srp.html", "Inventory"), ("sold.html", "Sold")]),
    ("Car page", "Gallery and decision panel side by side, the ways to reach the dealer, the record as accordions, the standards, the photographs, more from the lot.", [("cars/bmw-m3-2015.html", "2015 BMW M3")]),
    ("Map band", "The Google map of 600 Faust Rd, edge to edge, last in the page before the footer.", [("contact.html", "Contact"), ("index_finale_v2.html#contact", "Homepage")]),
]
patterns_html = "\n".join(
    f'        <li class="ds-card"><p class="ds-card__t">{t}</p><p class="ds-card__p">{d}</p><p class="ds-card__links">'
    + " · ".join(f'<a href="{h}">{l}</a>' for h, l in links) + "</p></li>"
    for t, d, links in PATTERNS)

PRINCIPLES = [
    ("A dark ground and uncut photographs", "The page is #161617 so Geneva's own photographs hold. Cars are shown as photographed, never over stock, never captioned as something they are not."),
    ("One red, and it means act", "Barn red from the badge fills the primary button and the Sold tag. On the dark ground it is a fill, never text."),
    ("Zilla Slab says, Instrument Sans reads", "The slab lettering of the badge for titles and numbers that are said; Instrument Sans for everything read and every label. Two families, nothing else."),
    ("The plate names the section", "Every eyebrow on every page is the same plate: #313C29 with #DFD4AF, the label's own width."),
    ("The client's words, trimmed", "Every sentence and figure has a source in the page's ledger. Template promises and superlatives nobody confirmed are left out, and recorded as left out."),
    ("Motion arrives once, then stays still", "Lines slide in stepped, photographs float up, cards and form sections enter as they are reached — once per visit. Reduced motion gets the finished page."),
]
principles_html = "\n".join(f'        <li class="ds-card"><p class="ds-card__t">{t}</p><p class="ds-card__p">{p}</p></li>' for t, p in PRINCIPLES)

DONTS = [
    "A numbered side rail that reads as a document outline — use a panel with real status.",
    "Scroll-drawn or scroll-linked motion (the scroll-drawn rings were rejected, 2026-09-10).",
    "Stock photographs, or one car's photograph under another car's name.",
    "Numbers or promises the client has not confirmed: “12+ years”, “5000+ sold”, “within 24 hours”, “best price”.",
    "Red text on the dark ground, underlined navigation, gradient buttons, decorative shadows.",
    "A placeholder instead of a label, or a mailto link dressed as a form.",
]
donts_html = "\n".join(f"          <li>{d}</li>" for d in DONTS)

page = f"""<!doctype html>
<!-- ============================================================
     GENEVA MOTOR HAUS — design system
     ============================================================
     GENERATED by tools/build-ds.py. Built from the site's own stylesheets;
     ds-v1.js reads token values, contrast and type sizes from them when the
     page opens, and the car card, sold card, pills and accordion are lifted
     from the built pages. Rebuild after the page generators.
     ============================================================ -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Design system — Geneva Motor Haus</title>
<meta name="description" content="The tokens, components, motion and rules Geneva Motor Haus is built from.">

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
<link rel="stylesheet" href="assets/css/vdp-v2.css?v=4">
<link rel="stylesheet" href="assets/css/finance-v2.css?v=4">
<link rel="stylesheet" href="assets/css/sell-v2.css?v=3">
<link rel="stylesheet" href="assets/css/contact-v2.css?v=2">
<link rel="stylesheet" href="assets/css/ds-v1.css?v=2">
</head>
<body class="v2 is-v3 is-gmh is-ds">

{top}<main>
  <section class="ds-head" data-reveal aria-labelledby="ds-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Design system</p>
      <h1 class="ds-head__title" id="ds-title"><span class="ttl-line">How this site</span> <span class="ttl-line">is built.</span></h1>
      <p class="ds-head__lede rv-lede">The tokens, components, motion and rules every page of this site is made from. The values below are read from the live stylesheets as the page opens, so they cannot drift from the site.</p>
      <p class="ds-head__meta rv-act">Palette, plate and entrance roles as of 14 Sep 2026 · geneva-final-v2.css ?v=21</p>
    </div>
  </section>

  <nav class="ds-nav" aria-label="Design system sections">
    <div class="shell"><ul>{nav_html}</ul></div>
  </nav>

  <section class="ds-sec" id="principles" data-reveal aria-labelledby="ds-principles-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Principles</p>
      <h2 class="ds-sec__title" id="ds-principles-title"><span class="ttl-line">Six decisions everything follows.</span></h2>
      <ul class="ds-grid rv-stagger" style="--rv-from: 1.6">
{principles_html}
      </ul>
      <div class="ds-donts rv-item" style="--rv-from: 5">
        <p class="ds-group__t">Never</p>
        <ul>
{donts_html}
        </ul>
      </div>
    </div>
  </section>

  <section class="ds-sec" id="color" data-reveal aria-labelledby="ds-color-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Colour</p>
      <h2 class="ds-sec__title" id="ds-color-title"><span class="ttl-line">One ground, one red, one plate.</span></h2>
      <p class="ds-sec__lede rv-lede">Components use these tokens and nothing else. Values are read live from the stylesheets.</p>
{colors_html}
      <div class="ds-group">
        <p class="ds-group__t">Contrast, measured live</p>
        <div class="ds-scroll"><table class="ds-table">
          <thead><tr><th scope="col">Sample</th><th scope="col">Used for</th><th scope="col">Pair</th><th scope="col">Ratio</th><th scope="col">Grade</th></tr></thead>
          <tbody>
{pairs_html}
          </tbody>
        </table></div>
      </div>
    </div>
  </section>

  <section class="ds-sec" id="type" data-reveal aria-labelledby="ds-type-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Type</p>
      <h2 class="ds-sec__title" id="ds-type-title"><span class="ttl-line">Zilla Slab says, Instrument Sans reads.</span></h2>
      <p class="ds-sec__lede rv-lede">Nine roles, set by the real classes. Sizes are measured at this window's width; titles scale with it. Nothing functional is set below 14px.</p>
      <ul class="ds-types">
{type_html}
      </ul>
    </div>
  </section>

  <section class="ds-sec" id="space" data-reveal aria-labelledby="ds-space-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Space and layout</p>
      <h2 class="ds-sec__title" id="ds-space-title"><span class="ttl-line">A 4px scale, gaps inside smaller than gaps between.</span></h2>
      <div class="ds-two">
        <ul class="ds-space">
{space_html}
        </ul>
        <div>
          <div class="ds-scroll"><table class="ds-table">
            <thead><tr><th scope="col">Token</th><th scope="col">Value</th><th scope="col">Role</th></tr></thead>
            <tbody>
{layout_html}
            </tbody>
          </table></div>
          <ul class="ds-notes">
            <li>Page heads start at the header's height plus clamp(48px, 5vw, 96px).</li>
            <li>A section's bottom padding is larger than its top.</li>
            <li>Inventory and car pages use the 1700px measure with clamp(24px, 3.4vw, 60px) gutters; every other page uses the container.</li>
            <li>Splits are 5 : 6 or 7 : 5, never 6 : 6 by default; form fields sit on six columns; cards run three, two, then one across (1080px, 700px).</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="ds-sec" id="radius" data-reveal aria-labelledby="ds-radius-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Radius</p>
      <h2 class="ds-sec__title" id="ds-radius-title"><span class="ttl-line">Round where it is touched.</span></h2>
      <p class="ds-sec__lede rv-lede">Pills for what is pressed, 12px for what holds content, square for what names. Known debt: 8, 10, 12 and 16px are written as values in the page layers — make them tokens before the next page.</p>
      <ul class="ds-radius rv-stagger" style="--rv-from: 1.6">
{radii_html}
      </ul>
    </div>
  </section>

  <section class="ds-sec" id="motion" data-reveal aria-labelledby="ds-motion-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Motion</p>
      <h2 class="ds-sec__title" id="ds-motion-title"><span class="ttl-line">Once, stepped, then still.</span></h2>
      <p class="ds-sec__lede rv-lede">A section opts in with <code class="ds-code">data-reveal</code> and marks its parts with a role. One observer plays every entrance once, when the section's top passes 78% of the window. Only the hidden state is written, so nothing is left transformed afterwards. With reduced motion the script never arms, and the page is simply complete.</p>

      <div class="ds-demo">
        <div class="ds-demo__stage" id="ds-demo" data-reveal>
          <div class="ds-demo__copy">
            <p class="micro gmh-plate rv-eyebrow">Inventory</p>
            <p class="ds-demo__title"><span class="ttl-line">Twenty-three cars,</span> <span class="ttl-line">hand-selected in Burlington.</span></p>
            <p class="ds-demo__lede rv-lede">From low-mile collectibles to everyday transportation.</p>
            <ul class="ds-demo__list rv-stagger" style="--rv-from: 3"><li>Porsche</li><li>BMW</li><li>Lexus</li><li>Ford</li></ul>
            <div class="rv-act"><a class="btn btn--accent" href="srp.html">Browse inventory {ARROW}</a></div>
          </div>
          <figure class="ds-demo__photo rv-photo" style="--rv-delay: 1"><img src="assets/img/about/about-story-sm.jpg" alt="A white Porsche 911 on a desert road below snow-capped mountains" width="1000" height="700" loading="lazy" decoding="async"></figure>
        </div>
        <div class="ds-demo__bar"><button class="btn btn--line" type="button" data-replay="ds-demo">Replay the entrance {ARROW}</button><p class="ds-demo__note" data-replay-note></p></div>
      </div>

      <div class="ds-two ds-group">
        <div>
          <p class="ds-group__t">Roles</p>
          <div class="ds-scroll"><table class="ds-table">
            <thead><tr><th scope="col">Class</th><th scope="col">What</th><th scope="col">Gesture</th><th scope="col">Duration</th><th scope="col">Delay</th></tr></thead>
            <tbody>
{roles_html}
            </tbody>
          </table></div>
        </div>
        <div>
          <p class="ds-group__t">Timing and easing</p>
          <div class="ds-ease">
            <svg viewBox="-8 -8 216 216" width="160" height="160" role="img" aria-label="The ease-out curve, cubic-bezier(0.22, 1, 0.36, 1)"><path d="M0 200H200M0 200V0" stroke="currentColor" stroke-opacity=".28" fill="none"/><path d="M0 200C44 0 72 0 200 0" stroke="currentColor" stroke-width="2.5" fill="none"/></svg>
            <p><code class="ds-code">--ease-out</code><br><span class="ds-num" data-token-value="--ease-out">—</span></p>
          </div>
          <div class="ds-scroll"><table class="ds-table">
            <tbody>
{dur_html}
            </tbody>
          </table></div>
          <ul class="ds-notes">
            <li>Hover: the button arrow moves 2px; card photographs scale slightly; nothing else moves under the pointer.</li>
            <li>The accordion's plus loses its vertical bar in 280ms.</li>
            <li>Transform and opacity only. Nothing animates layout.</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="ds-sec" id="components" data-reveal aria-labelledby="ds-components-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Components</p>
      <h2 class="ds-sec__title" id="ds-components-title"><span class="ttl-line">The real parts, working.</span></h2>
      <p class="ds-sec__lede rv-lede">Each sample is the component itself, with the site's CSS. The card, the pills and the accordion are lifted from the built pages.</p>
{components}
    </div>
  </section>

  <section class="ds-sec" id="patterns" data-reveal aria-labelledby="ds-patterns-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Page patterns</p>
      <h2 class="ds-sec__title" id="ds-patterns-title"><span class="ttl-line">Seven arrangements, every page.</span></h2>
      <ul class="ds-grid rv-stagger" style="--rv-from: 1.6">
{patterns_html}
      </ul>
    </div>
  </section>

  <section class="ds-sec" id="content" data-reveal aria-labelledby="ds-content-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Content</p>
      <h2 class="ds-sec__title" id="ds-content-title"><span class="ttl-line">Nothing on a page nobody can source.</span></h2>
      <div class="ds-two">
        <ul class="ds-notes ds-notes--big rv-stagger" style="--rv-from: 1.6">
          <li><b>A ledger per page.</b> <code class="ds-code">docs/content-ledger-*.json</code> holds every claim with its source, and a <em>notUsed</em> list of what was left out and why.</li>
          <li><b>Sources that count:</b> the client's live site captured on a date, the AAN forms, the client's own data. Never an earlier mockup, never a design document.</li>
          <li><b>Dated figures carry their date on screen:</b> prices and mileages read “as listed 14 Sep 2026”.</li>
          <li><b>Photographs are Geneva's own.</b> Uncaptioned when nothing says which car it is; no stock, no aerial of Geneva, Switzerland.</li>
        </ul>
        <ul class="ds-notes ds-notes--big rv-stagger" style="--rv-from: 2.3">
          <li><b>Forms keep AAN's names and required sets,</b> so they can be wired to AAN unchanged. A static preview says it cannot send, and gives the phone.</li>
          <li><b>Floors:</b> WCAG AA contrast, 14px for anything functional, a visible 2px focus ring, reduced motion complete, the same content on a phone.</li>
          <li><b>Known compromise:</b> the car page's contact pills are 41px tall, CMC's measure, under a 44px touch target.</li>
        </ul>
      </div>
    </div>
  </section>

  <section class="ds-sec" id="build" data-reveal aria-labelledby="ds-build-title">
    <div class="shell">
      <p class="micro gmh-plate rv-eyebrow">Build</p>
      <h2 class="ds-sec__title" id="ds-build-title"><span class="ttl-line">Generated pages, one chrome, versioned files.</span></h2>
      <div class="ds-group">
        <p class="ds-group__t">Stylesheets and scripts, in load order</p>
        <div class="ds-scroll"><table class="ds-table"><tbody>
{css_html}
        </tbody></table></div>
      </div>
      <div class="ds-group">
        <p class="ds-group__t">Pages and their generators</p>
        <div class="ds-scroll"><table class="ds-table">
          <thead><tr><th scope="col">Page</th><th scope="col">Built by</th><th scope="col">From</th></tr></thead>
          <tbody>
{gens_html}
          </tbody>
        </table></div>
      </div>
      <div class="ds-group">
        <p class="ds-group__t">Adding a page</p>
        <ol class="ds-steps">
          <li>Capture the source with its date into <code class="ds-code">docs/source/</code>.</li>
          <li>Write <code class="ds-code">tools/build-&lt;page&gt;.py</code>: the chrome from <code class="ds-code">gmh_chrome.chrome(current=…)</code>, markup from the existing classes, motion roles on its parts.</li>
          <li>Add a page layer <code class="ds-code">assets/css/&lt;page&gt;-v2.css</code> scoped to a body class, written in tokens.</li>
          <li>Write <code class="ds-code">docs/content-ledger-&lt;page&gt;.json</code>: every claim and its source, and what was not used.</li>
          <li>Add the route to <code class="ds-code">ROUTES</code> and the homepage's header, menu and footer; rebuild every generator, this page last.</li>
          <li>Bump <code class="ds-code">?v=</code> on every CSS and JS file you edited, everywhere it is linked.</li>
          <li>Check in Chrome at 1440 and 390: errors, missing files, overflow, the 14px floor, contrast, motion leftovers, reduced motion.</li>
        </ol>
      </div>
    </div>
  </section>
</main>

{footer}


<script src="assets/js/main-final-v2.js?v=2" defer></script>
<script src="assets/js/geneva-final-v2.js?v=2" defer></script>
<script src="assets/js/ds-v1.js?v=2" defer></script>
</body>
</html>
"""
OUT.write_text(page)
print(f"wrote {OUT.name} ({OUT.stat().st_size // 1024} KB): {sum(len(i) for _, i in COLORS)} colour tokens, {len(PAIRS)} contrast pairs, {len(TYPE)} type roles, 10 components")
