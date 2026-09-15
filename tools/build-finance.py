#!/usr/bin/env python3
"""Geneva Motor Haus — build finance.html.

THE FORM is the All Auto Network finance application
(aanmaster2027.aandemo.com/finance/, read 2026-09-14): its sections, its
fields, its field NAMES (fname, ssn, co_…, borrower_vehicle, stock…) so the
page can be wired to the AAN backend unchanged, and its terms and state
notices verbatim. Two of its behaviours are corrected, not copied: the
previous-residence section closes again once the time at the address
reaches two years, and "same as applicant" actually removes the
co-applicant's address fields.

THE WORDS around it are Geneva's own /financing page (rendered 2026-09-14),
trimmed of the template promises nobody has confirmed — see
docs/content-ledger-finance.json, notUsed.

THE LANGUAGE is the finale page's. The vehicle of interest lists the cars
actually in stock (assets/data/inventory-2026-09-14.json); a VDP links here
with ?car=<slug> and arrives with its car chosen.

    python3 tools/build-finance.py
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOME = ROOT / "index_finale_v2.html"
DATA = ROOT / "assets/data/inventory-2026-09-14.json"
OUT = ROOT / "finance.html"
LEDGER = ROOT / "docs/content-ledger-finance.json"
LIVE_INVENTORY = "https://www.genevamotorhaus.com/inventory"

e = html.escape
home = HOME.read_text()
V = json.loads(DATA.read_text())["vehicles"]

ARROW = ('<svg class="btn__arrow" width="13" height="13" viewBox="0 0 13 13" fill="none" aria-hidden="true">'
         '<path d="M2 6.5h9M7.4 3 11 6.5 7.4 10" stroke="currentColor" stroke-width="1.3"/></svg>')


def between(text, start, end, include_end=True):
    a = text.index(start)
    b = text.index(end, a) + (len(end) if include_end else 0)
    return text[a:b]


chrome_top = between(home, '<span class="scroll-sentinel"', "<main>", include_end=False).replace(LIVE_INVENTORY, "srp.html")
chrome_top = re.sub(r'<a href="finance\.html">Financing</a>', '<a href="finance.html" aria-current="page">Financing</a>', chrome_top)
footer = between(home, "<footer", "</footer>").replace(LIVE_INVENTORY, "srp.html")

STATES = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "District of Columbia",
          "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
          "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
          "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
          "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia",
          "Washington", "West Virginia", "Wisconsin", "Wyoming"]
YEARS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10+"]
MONTHS = [str(m) for m in range(1, 13)]


# ---- field helpers -------------------------------------------------------------
def field(name, label, span=2, kind="text", req=False, attrs="", options=None, placeholder=None):
    star = '<span class="fin-req" aria-hidden="true">*</span>' if req else ""
    r = " required" if req else ""
    fid = f"f-{name}"
    if kind == "select":
        opts = f'<option value="">{e(placeholder or "Select")}</option>' + "".join(f'<option value="{e(o)}">{e(o)}</option>' for o in options)
        control = f'<select id="{fid}" name="{name}"{r}{attrs}>{opts}</select>'
    elif kind == "textarea":
        control = f'<textarea id="{fid}" name="{name}" rows="5"{r}{attrs}></textarea>'
    else:
        control = f'<input id="{fid}" name="{name}" type="{kind}"{r}{attrs}>'
    return f'<div class="fin-field f-{span}"><label for="{fid}">{e(label)}{star}</label>{control}</div>'


def rows(*fields):
    return '<div class="fin-grid">' + "".join(fields) + "</div>"


def person(p="", prefix_label=""):
    n = lambda s: f"{p}{s}"
    return rows(
        field(n("fname"), "First name", 2, req=True, attrs=' autocomplete="given-name"' if not p else ""),
        field(n("mname"), "Middle name", 2, attrs=' autocomplete="additional-name"' if not p else ""),
        field(n("lname"), "Last name", 2, req=True, attrs=' autocomplete="family-name"' if not p else ""),
        field(n("email"), "Email", 3, "email", req=True, attrs=' autocomplete="email"' if not p else ""),
        field(n("phone"), "Phone", 3, "tel", req=True, attrs=' autocomplete="tel"' if not p else ""),
        field(n("drlic"), "Driver’s license no.", 2, req=True, attrs=' autocomplete="off"'),
        field(n("drlic_exp"), "License expiration", 2, "date", req=True),
        field(n("dob"), "Date of birth", 2, "date", req=True, attrs=' autocomplete="bday"' if not p else ""),
        field(n("ssn"), "Social Security no.", 3, req=True, attrs=' inputmode="numeric" autocomplete="off" maxlength="11" pattern="\\d{3}-?\\d{2}-?\\d{4}" placeholder="123-45-6789"'),
    )


def residence(p="", prev=False):
    q = "prev_" if prev else ""
    n = lambda s: f"{p}{q}{s}"
    lbl = (lambda s: f"Previous {s[0].lower()}{s[1:]}") if prev else (lambda s: s)
    return rows(
        field(n("address"), lbl("Address"), 6, req=True, attrs=' autocomplete="street-address"' if not (p or prev) else ""),
        field(n("city"), lbl("City"), 2, req=True),
        field(n("state"), "State", 2, "select", req=True, options=STATES, placeholder="Select state"),
        field(n("zip"), "ZIP", 2, req=True, attrs=' inputmode="numeric" maxlength="5" pattern="\\d{5}"'),
        field(n("addr_y"), "Time at address — years", 2, "select", req=True, options=YEARS, attrs=' data-under2="' + (f"{p}prev-res" if not prev else "") + '"' if not prev else ""),
        field(n("addr_m"), "Months", 2, "select", req=True, options=MONTHS),
        field(n("addr_type"), "Residence type", 2, "select", options=["Own", "Rent", "Mortgage"]),
        field(n("addr_payments"), "Monthly payment", 3, req=not prev, attrs=' inputmode="decimal" placeholder="$"'),
    )


def employment(p=""):
    n = lambda s: f"{p}{s}"
    return rows(
        field(n("employer"), "Employer", 3, req=True),
        field(n("occupation"), "Occupation", 3, req=True),
        field(n("employer_address"), "Employer address", 6, req=True),
        field(n("employer_city"), "City", 2, req=True),
        field(n("employer_state"), "State", 2, "select", req=True, options=STATES, placeholder="Select state"),
        field(n("employer_zip"), "ZIP", 2, req=True, attrs=' inputmode="numeric" maxlength="5" pattern="\\d{5}"'),
        field(n("employer_phone"), "Office phone", 2, "tel", req=True),
        field(n("employer_supervisor"), "Supervisor", 2),
        field(n("work_y"), "Years at present job", 2, "select", req=True, options=YEARS, attrs=f' data-under2="{p}prev-emp"'),
        field(n("monthly_income"), "Gross monthly income", 3, req=True, attrs=' inputmode="decimal" placeholder="$"'),
        field(n("other_income"), "Other monthly income", 3, attrs=' inputmode="decimal" placeholder="$"'),
    )


def prev_employment(p=""):
    n = lambda s: f"{p}{s}"
    occ = "prev_borrower_occupation" if not p else "prev_occupation"   # AAN's own names
    return rows(
        field(n("prev_employer"), "Previous employer", 3, req=True),
        field(n(occ), "Occupation", 3),
        field(n("prev_employer_phone"), "Office phone", 3, "tel", req=True),
        field(n("prev_employer_supervisor"), "Supervisor", 3, req=True),
    )


def sub(sid, title, why, body):
    return (f'<div class="fin-sub" id="{sid}" hidden><p class="fin-sub__t">{e(title)}</p>'
            f'<p class="fin-sub__why">{e(why)}</p>{body}</div>')


def section(sid, num, title, body, lede="", extra_cls="", hidden=False):
    return (f'<fieldset class="fin-sec rv-self{extra_cls}" id="{sid}" data-reveal{" hidden" if hidden else ""}>'
            f'<legend class="fin-sec__head"><span class="fin-sec__n">{num}</span><span class="fin-sec__t">{e(title)}</span></legend>'
            + (f'<p class="fin-sec__lede">{e(lede)}</p>' if lede else "") + body + "</fieldset>")


# ---- the vehicle of interest: the cars actually in stock -------------------------
makes = sorted({v["make"] for v in V})
car_opts = "".join(
    f'<option value="{v["slug"]}" data-make="{e(v["make"])}">{v["year"]} {e(v["make"])} {e(v["model"])} — ${v["price"]:,}</option>'
    for v in sorted(V, key=lambda v: (v["make"], -v["year"])))
vehicle_block = (
    '<div class="fin-grid">'
    + field("make", "Make", 2, "select", options=makes, placeholder="Any make")
    + f'<div class="fin-field f-4"><label for="f-stock">Vehicle</label><select id="f-stock" name="stock"><option value="">Choose a car in stock</option>{car_opts}</select></div>'
    + field("down_payment", "Down payment", 3, attrs=' inputmode="decimal" placeholder="$"')
    + "</div>")

TERMS = """
<p><strong>ACKNOWLEDGMENT AND CONSENT:</strong> I certify that the above information is complete and accurate to the best of my knowledge. Creditors receiving this application will retain the application whether or not it is approved. Creditors may rely on this application in deciding whether to grant the requested credit. False statements may subject me to criminal penalties. I authorize the creditors to obtain credit reports about me on an ongoing basis during this credit transaction and to check my credit and employment history on an ongoing basis during the term of the credit transaction. If this application is approved, I authorize the creditor to give credit information about me to its affiliates.</p>
<p>Please note that by completing this form, you agree to being contacted via text, phone and email.</p>
<p>If you’re a resident of California, Maine, Massachusetts, New York, Ohio, Rhode Island, Vermont, Washington, or Wisconsin, please scroll down to read the notice called for under the law of your state. By submitting this application, you represent that you’ve read the notice required under the law of your state.</p>
<p><strong>CALIFORNIA RESIDENTS:</strong> A married applicant may apply for an individual account.</p>
<p><strong>MAINE RESIDENTS:</strong> Consumer reports (credit reports) may be obtained in connection with this application. If you request, the creditor will inform you:</p>
<ul><li>whether or not consumer reports were obtained, and</li><li>if reports were obtained, the names and addresses of the consumer reporting agencies (credit bureaus) that furnished the reports.</li></ul>
<p>You have the right to choose the agent and insurer for the insurance required by this transaction, but the insurer must be approved by the creditor.</p>
<p><strong>MASSACHUSETTS RESIDENTS:</strong> Massachusetts law prohibits discrimination on the basis of marital status or sexual orientation.</p>
<p><strong>NEW YORK RESIDENTS:</strong> A consumer credit report may be requested in connection with this application or in connection with updates, renewals, extensions or enforcement of any credit granted as a result of this application. Upon your request, the creditor will inform you whether or not a consumer credit report was requested, and if so, the name and address of the agency that furnished such report.</p>
<p><strong>OHIO RESIDENTS:</strong> The Ohio laws against discrimination require that all creditors make credit equally available to all credit worthy customers, and that credit reporting agencies maintain separate credit histories on each individual upon request. The Ohio Civil Rights Commission administers compliance with this law.</p>
<p><strong>RHODE ISLAND RESIDENTS:</strong> A consumer credit report may be requested in connection with this application.</p>
<p><strong>VERMONT RESIDENTS:</strong> I authorize the creditor to obtain credit reports on an ongoing basis about me from credit reporting agencies in connection with this extension of credit transaction. The creditor may obtain credit reports about me on an ongoing basis in connection with this extension of credit transaction for any one or more of the following reasons:</p>
<ul><li>reviewing the account;</li><li>increasing the credit line on the account;</li><li>taking collection action on the account; or,</li><li>any other legitimate purposes associated with the account.</li></ul>
<p><strong>WASHINGTON RESIDENTS:</strong> Please advise us if the creditor should investigate your credit references and/or credit history under another name.</p>
<p><strong>MARRIED WISCONSIN RESIDENTS:</strong> No provision of a marital property agreement, a unilateral settlement agreement under Wis. Stat. §766.59, or a court decree under Wis. Stat. §766.70 adversely affects the interest of the creditor unless the creditor, prior to the time the credit is granted, is furnished a copy of the agreement, statement or decree, or has actual knowledge of the adverse provision.</p>
"""

STEPS = [("fin-applicant", "Applicant"), ("fin-residence", "Residence"), ("fin-employment", "Employment"),
         ("fin-coapp", "Co-applicant"), ("fin-trade", "Trade-in"), ("fin-vehicle", "Vehicle of interest"),
         ("fin-more", "Additional information"), ("fin-terms", "Terms and conditions")]
# the summary beside the form: what is answered, what each step still needs
steps_html = "\n".join(f'              <li><a class="fin-step" href="#{sid}"><span class="fin-step__t">{t}</span><span class="fin-step__s" data-status></span></a></li>' for sid, t in STEPS)
rail = f"""        <aside class="fin-rail rv-self" data-reveal aria-label="Your application">
          <div class="fin-rail__head">
            <p class="fin-rail__t">Your application</p>
            <div class="fin-rail__progress" data-progress hidden>
              <p class="fin-rail__count"><b data-done>0</b> of <span data-total>0</span> required fields filled</p>
              <span class="fin-rail__bar" aria-hidden="true"><span data-bar></span></span>
            </div>
          </div>
          <nav aria-label="Application steps">
            <ol class="fin-rail__steps">
{steps_html}
            </ol>
          </nav>
          <div class="fin-rail__foot">
            <button class="btn btn--accent fin-rail__send" type="submit" form="fin-form">Send application {ARROW}</button>
            <p class="fin-rail__help">Questions? Call <a href="tel:+12622496777">(262) 249-6777</a></p>
          </div>
        </aside>"""

form = (
    section("fin-applicant", "01", "Applicant", person())
    + section("fin-residence", "02", "Residence", residence()
              + sub("prev-res", "Previous residence", "You’ve lived at this address for less than two years.", residence(prev=True)))
    + section("fin-employment", "03", "Employment", employment()
              + sub("prev-emp", "Previous employment", "You’ve been at this job for less than two years.", prev_employment()))
    + section("fin-coapp", "04", "Co-applicant",
              '<label class="fin-toggle"><input type="checkbox" name="co_applicant_active" value="1" id="f-co_applicant_active">'
              '<span class="fin-toggle__track" aria-hidden="true"></span><span class="fin-toggle__text">Apply with a co-applicant</span></label>'
              '<div class="fin-co" id="fin-co" hidden>'
              '<p class="fin-sub__t">Co-applicant</p>' + person("co_")
              + '<p class="fin-sub__t">Co-applicant residence</p>'
              + '<label class="fin-check"><input type="checkbox" name="co_same_address" value="1" id="f-co_same_address"><span>Same address as the applicant</span></label>'
              + '<div id="co-res-fields">' + residence("co_") + "</div>"
              + sub("co_prev-res", "Co-applicant previous residence", "Less than two years at this address.", residence("co_", prev=True))
              + '<p class="fin-sub__t">Co-applicant employment</p>' + employment("co_")
              + sub("co_prev-emp", "Co-applicant previous employment", "Less than two years at this job.", prev_employment("co_"))
              + "</div>",
              lede="Optional. Adding a co-applicant opens their details, residence and employment.")
    + section("fin-trade", "05", "Trade-in vehicle", rows(
        field("borrower_vehicle", "Your current vehicle", 3, "select", options=["Lease", "Purchase"], placeholder="Select"),
        field("borrower_vehicle_stat", "Vehicle status", 3, "select", options=["Open financing", "Paid off"], placeholder="Select")))
    + section("fin-vehicle", "06", "Vehicle of interest", vehicle_block)
    + section("fin-more", "07", "Additional information", rows(field("message", "Anything we should know", 6, "textarea")))
    + section("fin-terms", "08", "Terms and conditions",
              f'<div class="fin-terms" tabindex="0" role="region" aria-label="Terms and conditions">{TERMS}</div>'
              '<label class="fin-check fin-check--agree"><input type="checkbox" name="agree" value="1" id="f-agree" required><span>I agree to the terms and conditions<span class="fin-req" aria-hidden="true">*</span></span></label>')
)

page = f"""<!doctype html>
<!-- ============================================================
     GENEVA MOTOR HAUS — financing
     ============================================================
     GENERATED by tools/build-finance.py. The form is the AAN finance
     application (fields, names, terms) set in Geneva's language; the words
     around it are Geneva's /financing page, trimmed of unconfirmed promises
     (docs/content-ledger-finance.json). A static preview cannot send an
     application, and the form says so when it is submitted.
     ============================================================ -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Financing — Geneva Motor Haus · Burlington, WI</title>
<meta name="description" content="Apply for financing at Geneva Motor Haus in Burlington, Wisconsin — trusted lenders, competitive rates and flexible terms.">

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
</head>
<body class="v2 is-v3 is-gmh is-fin">

{chrome_top}<main>
  <!-- 1 — THE HEAD: what this is, and the two ways in -->
  <section class="fin-head" data-reveal aria-labelledby="fin-title">
    <div class="shell fin-head__inner">
      <div class="fin-head__copy">
        <p class="micro fin-head__eyebrow rv-eyebrow">Financing</p>
        <h1 class="fin-head__title" id="fin-title"><span class="ttl-line">Get approved</span> <span class="ttl-line">today.</span></h1>
        <p class="fin-head__lede rv-lede">At Geneva Motor Haus we make financing as smooth as it can be: we work with trusted lenders to provide competitive rates and flexible terms.</p>
        <div class="fin-head__acts rv-act">
          <a class="btn btn--accent" href="#apply">Start the application {ARROW}</a>
          <a class="btn btn--line" href="tel:+12622496777">Call (262) 249-6777 {ARROW}</a>
        </div>
      </div>
      <ul class="fin-points rv-stagger" style="--rv-from: 1.6" aria-label="Why finance with us">
        <li class="fin-point"><p class="fin-point__t">Competitive rates</p><p class="fin-point__p">We work with multiple lenders to find the rate available for your situation.</p></li>
        <li class="fin-point"><p class="fin-point__t">Flexible terms</p><p class="fin-point__p">A variety of loan terms and payment options to fit your budget.</p></li>
        <li class="fin-point"><p class="fin-point__t">Pre-owned financing</p><p class="fin-point__p">Financing options for the pre-owned cars in <a href="srp.html">our inventory</a>.</p></li>
      </ul>
    </div>
  </section>

  <!-- 2 — THE APPLICATION: eight steps, a rail that follows the reading -->
  <section class="fin-apply" id="apply" aria-labelledby="fin-apply-title">
    <div class="shell">
      <div class="fin-apply__head" data-reveal>
        <p class="micro fin-apply__eyebrow rv-eyebrow">Application</p>
        <h2 class="fin-apply__title" id="fin-apply-title"><span class="ttl-line">Financing application</span></h2>
        <p class="fin-apply__lede rv-lede">Fill out the form to start your application. Fields marked <span class="fin-req">*</span> are required.</p>
      </div>
      <div class="fin-apply__body">
        <div class="fin-apply__main">
          <form class="fin-form" id="fin-form" novalidate>
{form}
            <div class="fin-actions">
              <button class="btn btn--accent" type="submit">Send application {ARROW}</button>
              <button class="btn btn--line fin-clear" type="button">Clear form</button>
            </div>
          </form>
          <div class="fin-sent" id="fin-sent" hidden tabindex="-1">
            <p class="fin-sent__t">Thanks<span data-sent-name></span>.</p>
            <p class="fin-sent__p">This preview doesn’t send applications. To start financing with Geneva Motor Haus now, call <a href="tel:+12622496777">(262) 249-6777</a>.</p>
          </div>
        </div>
{rail}
      </div>
    </div>
  </section>
</main>

{footer}


<script src="assets/js/main-final-v2.js?v=2" defer></script>
<script src="assets/js/geneva-final-v2.js?v=2" defer></script>
<script src="assets/js/finance-v2.js?v=5" defer></script>
</body>
</html>
"""
OUT.write_text(page)

ledger = {
    "project": "geneva-motor-haus", "page": "finance.html", "compiled": "2026-09-14",
    "note": "The application is the AAN finance form (aanmaster2027.aandemo.com/finance/, read 2026-09-14): fields, names and the terms and state notices verbatim. The words around it are genevamotorhaus.com/financing, rendered 2026-09-14.",
    "entries": [
        {"id": "fin-heading", "claim": "Get approved today.", "status": "verified", "source": "genevamotorhaus.com/financing: 'Get Approved Today'", "sourceType": "live-site", "appearsAt": [".fin-head__title"]},
        {"id": "fin-lede", "claim": "we make financing as smooth as it can be: we work with trusted lenders to provide competitive rates and flexible terms", "status": "verified", "source": "/financing: 'we make financing your luxury vehicle as smooth as possible. Our experienced finance team works with trusted lenders to provide competitive rates and flexible terms'", "sourceType": "live-site", "appearsAt": [".fin-head__lede"]},
        {"id": "fin-rates", "claim": "We work with multiple lenders to find the rate available for your situation.", "status": "verified", "source": "/financing 'Competitive Rates': 'We work with multiple lenders to secure the best financing rates available for your situation.' ('best' removed)", "sourceType": "live-site", "appearsAt": [".fin-point"]},
        {"id": "fin-terms-flex", "claim": "A variety of loan terms and payment options to fit your budget.", "status": "verified", "source": "/financing 'Flexible Terms'", "sourceType": "live-site", "appearsAt": [".fin-point"]},
        {"id": "fin-preowned", "claim": "Financing options for the pre-owned cars in our inventory.", "status": "verified", "source": "/financing 'Pre-Owned Financing' ('extensive selection of pre-owned luxury vehicles' trimmed)", "sourceType": "live-site", "appearsAt": [".fin-point"]},
        {"id": "fin-phone", "claim": "(262) 249-6777", "status": "verified", "source": "live site header", "sourceType": "live-site", "appearsAt": [".fin-head__acts", ".fin-rail__help", ".fin-sent__p"]},
        {"id": "fin-cars", "claim": "Vehicle of interest: the 23 cars in stock with their prices", "status": "dated-requires-reconciliation", "captureDate": "2026-09-14", "source": "assets/data/inventory-2026-09-14.json", "sourceType": "live-site", "appearsAt": ["#f-stock"]},
        {"id": "fin-terms-legal", "claim": "Terms and conditions and state notices", "status": "verified", "source": "AAN finance application, verbatim", "sourceType": "client-data", "appearsAt": [".fin-terms"]},
    ],
    "notUsed": [
        {"claim": "Fast Approval — get pre-approved in minutes", "reason": "a service promise not confirmed by the client (CP6)"},
        {"claim": "Bad Credit OK — we work with all credit types", "reason": "a lending promise not confirmed by the client (CP6)"},
        {"claim": "New Vehicle Financing / Lease Options / Refinancing", "reason": "template services; Geneva sells pre-owned cars and nothing confirms leasing or refinancing"},
        {"claim": "Our finance team will contact you within 24 hours", "reason": "a response-time promise not confirmed (CP6)"},
        {"claim": "luxury vehicle / extensive selection / finance experts", "reason": "superlatives the stock does not support"},
    ],
}
LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False))
print(f"wrote {OUT.name} ({OUT.stat().st_size // 1024} KB) with {len(V)} cars in the vehicle list; ledger {len(ledger['entries'])} entries")
