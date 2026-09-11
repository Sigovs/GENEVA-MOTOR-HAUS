# Geneva Motor Haus — discovery

Captured 2026-09-10 from the client ticket, the live site, public listings and the
AAN Control Panel export. **This is the seed of the content ledger**
(`content-provenance` CP1): every claim the new site makes must trace to a row here
or to something the client supplies later. Nothing below is invented; gaps are
marked `not recorded`.

## The client brief — AAN ticket, verbatim

Source: `from client/AAN Control Panel.pdf` (one page; no text layer — read from a
render). Attachment: `from client/Screenshot 2026-09-02 at 11.04.00 AM.png`.

> They want the new CMC design.
>
> His logo colors are: Black, brown, dark red/brown. He unfortunately only has his
> logo in a jpg (see attached).
>
> Few adjustments:
> 1. No search filters on hero section
> 2. Put a search bar in the header
> 3. Remove the sections that don't match up with the current business model: services, karma, random sections.
> 4. Wants to keep warranties, needs a shipping section since half their cars go out of state,
> 5. The sections he has on his live sit is what he wants https://www.genevamotorhaus.com

## Project decisions

| | | Source |
|---|---|---|
| Scope | **Homepage first.** Other routes follow once it is approved. | Alex, 2026-09-10 |
| Platform | **Static HTML / CSS / JS, no build step.** | Alex, 2026-09-10 |
| Design source | **"The new CMC design"** = the approved Chicago Motor Cars preview, `index_3.html` — `/Users/alex/Desktop/WORK/Chicago Motor Cars`, repo `Sigovs/AAN_PPREVIEW_CHICAGOMOTORCARS`, HEAD `fbbdb65` (2026-08-28). `index.html` there is frozen; `index_3` is the approved variant with uncut photography. | client ticket + CMC project memory |
| Mandate | **REDESIGN of Geneva, executed in the CMC system.** Geneva's identity is fixed — logo, logo colours, their section set, their facts. CMC supplies layout, components, type and motion. Nothing CMC-specific carries: no wordmark, no Karma, no CMC figures, no CMC photography. | client ticket |
| Delivery | **BUILD** — the direction was chosen by the client. | TASTE §2 |

## The business

| Fact | Value | Source |
|---|---|---|
| Legal name | Geneva Motor Haus LLC | Autotrader / KBB dealer listing |
| Address | 600 Faust Rd, Unit 8, Burlington, WI 53105 | live site, contact section + map embed |
| Phone | (262) 249-6777 | live site, header + contact |
| Email | Info@GenevaMotorHaus.com | live site, header |
| Hours | Mon–Fri 10AM–4PM · Saturday: Appt Only · Sunday: Closed | live site, contact section |
| Owner | "Shane the owner" — surname not recorded | customer review on the live site |
| Rating | "5.0 out of 5 stars"; a review cites "5 Star rating on Google" — review count not recorded | live site, reviews tile |
| Out-of-state sales | "half their cars go out of state" | client ticket |
| Location line | "Just a hour north of Chicago and minutes from Lake …" — truncated in the search result; which lake is **not verified** | Facebook video title |
| AAN status | All Auto Network dealer, WI, status **Pending**, dated 2026-08-27 | AAN Control Panel export 2026-09-09 |
| Social | Instagram @genevamotorhaus · TikTok @genevamotorhaus and @geneva.motor.haus · Facebook · YouTube (icon in footer) | search results + live footer |

**Not this dealer:** Geneva Motor Cars, 690 Gerry Way, Darien WI — a different business that ranks for the same searches.

## Their own words (verbatim, spelling as published)

- H1: "GENEVA MOTOR HAUS"
- Tagline: "The Car Dealership where Passion meets Perfection"
- Sub: "Where Passion meet Perfection From Low Mile Collectibles to Everyday Transportation! CALL US TODAY 262-249-6777"
- Marquee: "WELCOME TO GENEVA MOTOR HAUS - YOUR PREMIER DESTINATION FOR LUXURY VEHICLES, … AUTOMOBILES WITH UNMATCHED QUALITY AND CUSTOMER CARE."
- Selection: "Our dealership takes pride in curating an exceptional vehicle inventory compilation. … We enjoy having a variety of types of vehicles including exotics, classics, American modern muscle, Japanese supercars and much more."
- Sell: "Get Top Dollar for Your Car · We Make Selling Simple … a fair, no-obligation appraisal. Whether you're selling a luxury vehicle, exotic car, or daily driver, we're interested in purchasing quality automobiles."

**The line worth keeping** is *"From Low Mile Collectibles to Everyday Transportation"* — the only sentence that describes this floor accurately. "Premier destination", "unmatched", "exotics" and "Japanese supercars" do not match the stock on the day of capture, and fall under `content-provenance` before they can be reused.

## The live site's homepage sections — what the client wants kept

In order: marquee bar → header → hero → **Featured Inventory** (carousel, 8) → four tiles: **Reviews / Financing / About Us / Get in Touch** → tabs: **Selection / Reputation / Process / Service** → **Sell your car** → **Reviews** carousel → **Newsletter** → **Contact / Location** + map → footer. Floating "SELL YOUR CAR" pill.

Plus, from the ticket: **Warranties** (keep) and **Shipping** (new).

**Re-rendered 2026-09-10 (Playwright, 1440×900) at Alex's question "is this respected?"** —
what the first build did NOT carry:

- **Featured Inventory shows 8 cars** in a carousel (2007 911 Targa 4S · 2008 Lexus IS-F ·
  2015 BMW M3 · 1989 Mustang Saleen SSC · 1997 911 Carrera 4S · 2010 911 Carrera 4S ·
  2004 911 C4S Cabriolet · 2003 BMW X5 4.4i). The build shows 4.
- **The four tiles are a section of their own**, not only routes: SEE OUR *Reviews*
  (★★★★★ 5.0 out of 5 stars · VIEW ALL REVIEWS) · EXPLORE *Financing* (APPLY NOW) · LEARN
  *About Us* (LEARN MORE) · GET IN *Touch* (CONTACT US).
- **The four tabs, verbatim** (eyebrows: EXCEPTIONAL INVENTORY · HIGHLY RELIABLE · SMOOTH
  DEAL · STRONG CUSTOMER):
  - *Selection* — "Our dealership takes pride in curating an exceptional vehicle inventory
    compilation. Each vehicle in our inventory has been carefully selected to offer a diverse
    and high-quality selection to our customers. We go above and beyond to source vehicles that
    meet our rigorous standards of excellence in terms of condition, performance, and features.
    We enjoy having a variety of types of vehicles including exotics, classics, American modern
    muscle, Japanese supercars and much more."
  - *Reputation* — "With over 12 years in the automotive industry, we have built a reputation
    for reliability and trustworthiness. Our commitment to transparency and honesty has earned
    us the trust of thousands of satisfied customers. We stand behind every vehicle we sell and
    provide comprehensive vehicle history reports to ensure complete transparency."
  - *Process* — "We've streamlined our sales process to make buying or selling your vehicle as
    smooth and stress-free as possible. From initial inquiry to final delivery, our team guides
    you through every step. We handle all paperwork, financing options, and logistics to ensure
    a seamless experience from start to finish."
  - *Service* — "Customer satisfaction is at the heart of everything we do. Our dedicated
    service team is committed to providing exceptional support before, during, and after your
    purchase. We offer comprehensive warranties, maintenance programs, and ongoing support to
    ensure your complete satisfaction with your vehicle."
  The build carried only *Selection*. **This "Service" is customer service, not CMC's service
  department** — ticket item 3 ("remove services") refers to CMC's `.svc` section.
- **Contact / Location has a Google Maps embed** of 600 Faust Rd. The build shows a photograph
  of the door and a directions link.
- **A fixed "SELL YOUR CAR" pill** floats bottom-right on every screen.
- **A sticky info bar** above the nav: address · (262)-249-6777 · Info@GenevaMotorHaus.com.
- Hero CTAs on the live site: BROWSE INVENTORY · CONTACT US.

Claims in the tabs ("over 12 years", "thousands of satisfied customers", "comprehensive vehicle
history reports", "comprehensive warranties, maintenance programs") are the client's own
published words — a live-site source — and each needs a ledger entry before it is set.

## Inventory on 2026-09-10 — 23 vehicles, $9,000–$170,000

**Dated figure — carries its date wherever it is shown (CP5).**

Enthusiast / collectible: 1997 Porsche 911 Carrera 4S 6-speed ($169,993) · 2004 Porsche 911 C4S Cabriolet ($54,996) · 2007 Porsche 911 Targa 4S ($99,997) · 2010 Porsche 911 Carrera 4S ($75,000) · 1999 Porsche Boxster · 1989 Ford Mustang Saleen SSC, 2,470 mi ($170,000) · 1963 Ford Galaxie · 1963 Ford Galaxie 500 XL Hardtop · 1993 Mercedes-Benz 400 SEL · 2003 Mercedes-Benz CL55 AMG · 2006 Cadillac XLR-V · 1997 Toyota Land Cruiser Collectors Edition · 2015 BMW M3 ($59,990) · 2008 Lexus IS-F ($49,990) · 2006 BMW 330Ci

Everyday: 2011 Lexus LS460 · 2004 Lexus ES330 · 2003 BMW X5 4.4i ($12,990) · 2000 Mercedes-Benz ML320 · 2012 Chrysler Town & Country Touring-L · 2003 Nissan Frontier SVE Supercharged · 2001 Chevrolet Blazer 2LT · 2001 Chevrolet Blazer

Prices not listed above were not captured per vehicle. The **Porsche 911 cluster**
(four cars across 993, 996 and 997) is the strongest desirable subject on the floor.

Filters on the live SRP: keyword, make, model, year, mileage, body type, price min/max.

## Current site (what exists, not what carries)

- **Stack:** Vite + React SPA, data from Firestore (project `geneva-motor-haus`), images under `genevamotorhaus.com/uploads/`. Content only exists after JS runs.
- **Routes:** `/` · `/about` · `/inventory` · `/sold` · `/financing` · `/contact` · `/sell-your-car`
- **Type:** system font only — Segoe UI / Tahoma / Verdana.
- **Colour, measured from the stylesheet:** tan `#c2a375` (15 uses), dark tan `#8b6f47`, header dark brown `#332724` (sampled). Not a carrier — the client names the **logo** colours instead.

## Brand assets

- **Logo — CURRENT: `from client/logo_adjsuted.png`** (added 2026-09-10 17:54),
  1376×1143 RGBA with a real transparent ground. A clean redraw of the badge in a
  sticker register: barn roof measured **#BC0F0D** (median of 80,943 pixels), cream
  lettering and car **#FCF0CC**, tan outline **#F0D8B4**, black keyline. Used in the
  header, footer and favicon (`assets/logos/gmh-logo-*.png`, `gmh-icon-*.png`).
  **Who adjusted it, and how, is not recorded** — see `assets/logos/PROVENANCE.md`.
  The page accent follows this red (tokens.css), not the old badge's brown.
- **Superseded — JPG only, as the ticket said.** Two rasters, kept for reference:
  - `from client/Screenshot 2026-09-02 at 11.04.00 AM.png` — a 904×662 PNG screenshot; the badge on a dark weathered-wood square fills ~430px of it, soft. The filename has a narrow no-break space (U+202F) before "AM" — address it by glob, not by typing the name.
  - `genevamotorhaus.com/uploads/media/69172f2b7e2e0_1763127083.png` — 205×241, transparent ground. The better source for a header.
  - Artwork: a dark red/brown barn roof with a white window, over a cream air-cooled 911 silhouette, lettered "GENEVA / MOTOR HAUS" in an arched cream western-slab face.
- **Logo colours (client's words):** black, brown, dark red/brown. The cream lettering is in the artwork but not in his list.
- **Building:** a dark steel-sided pole building with timber-gable door canopies and a large open overhead door; the interior has a timber-clad mezzanine.

## Photography — the declared asset dependency

- Dealer's own iPhone frames, 4032×3024 / 1920×1440, shot on the lot in hard daylight against the building's steel siding. Consistent backdrop, uneven light and reflections.
- Some listing images are **PNG screenshots** (Lexus IS-F 1577×889, BMW M3 1618×937).
- Current hero frame: `uploads/media/69e50875a73aa_1776617589.jpeg` — two 997s on the asphalt, the open door behind; half the frame is empty asphalt.
- **CMC's `index_3` is the right base for exactly this reason** — it was built to carry uncut dealer photography. The cut-out stage in `index_2` needs background removal this dealer will not do.

## Open asks for the client

1. **Warranty terms** — provider, coverage, durations. Not on the live site; CMC's warranty copy is CMC's and cannot be reused.
2. **Shipping details** — enclosed/open transport, partner, how quotes work, whether cost is included.
3. Google review count, for the rating to be shown honestly.
4. Years in business.
5. Which lake the "minutes from Lake …" line means.
