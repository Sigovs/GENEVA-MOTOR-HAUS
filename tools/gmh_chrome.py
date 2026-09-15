"""Geneva Motor Haus — the shared chrome for generated pages.

The header, the menu and the footer live once, in index_finale_v2.html.
Every generated page lifts them from there, so a change to the homepage's
chrome reaches every page on the next build.

ROUTES is the one map from the live site's addresses to this preview's
pages. The homepage itself is written with these local routes; the map is
applied again on lift so an older copy of the chrome cannot leak a live
address into a generated page.

    from gmh_chrome import chrome
    top, footer = chrome(current=("sell.html", "Sell your car"))
    top, footer = chrome(root="../")          # pages one folder down (cars/)
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOME = ROOT / "index_finale_v2.html"

ROUTES = {
    "https://www.genevamotorhaus.com/inventory": "srp.html",
    "https://www.genevamotorhaus.com/sold": "sold.html",
    "https://www.genevamotorhaus.com/financing": "finance.html",
    "https://www.genevamotorhaus.com/sell-your-car": "sell.html",
    "https://www.genevamotorhaus.com/about": "about.html",
    "https://www.genevamotorhaus.com/contact": "contact.html",
}


def between(text, start, end, include_end=True):
    a = text.index(start)
    b = text.index(end, a) + (len(end) if include_end else 0)
    return text[a:b]


def localise(fragment):
    for live, local in ROUTES.items():
        fragment = fragment.replace(f'href="{live}"', f'href="{local}"')
    return fragment


def reroot(fragment, root="../"):
    return re.sub(r'\b(href|src|srcset|action)="(?!(?:https?:|tel:|mailto:|sms:|#|//|data:))([^"]+)"', rf'\1="{root}\2"', fragment)


def chrome(current=None, root=""):
    """(header + menu, footer) from the homepage. current = (href, label) marks the page in the nav."""
    home = HOME.read_text()
    top = localise(between(home, '<span class="scroll-sentinel"', "<main>", include_end=False))
    foot = localise(between(home, "<footer", "</footer>"))
    if current:
        href, label = current
        top = top.replace(f'<a href="{href}">{label}</a>', f'<a href="{href}" aria-current="page">{label}</a>')
    if root:
        top, foot = reroot(top, root), reroot(foot, root)
    return top, foot
