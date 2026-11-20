"""Builds the profile README's images in the portfolio's dark metro-map style.

    python build/build.py [path-to-portfolioV6]

Reads the main-row projects (isFeatured, in order) from the portfolio's
data/projects.json, renders each as a card PNG (Playwright + Edge), and
writes the SVG header, section title and link pills into assets/.
Re-run it whenever the portfolio's featured projects change.
"""
import base64, html, json, os, sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "assets")
PORTFOLIO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "..", "portfolioV6")
SITE = "https://www.damdev.xyz/Content/portfolioV6/"

# portfolio dark theme (css/common.css)
C = dict(cream="#18181a", paper="#232326", ink="#e2ddd0", soft="#b8b2a6",
         red="#e2483c", yellow="#f2b632", blue="#5090c8", green="#5aad7c")
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
W = 840          # every SVG shares this width so the trunk lines up at x=TRUNK
TRUNK = 30

os.makedirs(OUT, exist_ok=True)
plane_b64 = base64.b64encode(open(os.path.join(PORTFOLIO, "data/icons/plane-blue.png"), "rb").read()).decode()


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def station(x, y, color):
    return f'<circle cx="{x}" cy="{y}" r="9" fill="{C["paper"]}" stroke="{color}" stroke-width="4"/>'


# ---------- header: name station + intro card, a cart running down the line ----------
def header():
    lines = [
        [("Hey, I'm ", 0), ("Marci", 1), (", a ", 0), ("full-stack developer", 1), (" bridging ", 0),
         ("web", 1), (" and ", 0), ("hardware", 1), (".", 0)],
        [("Research developer at ", 0), ("Bay Zoltán Research Institute", 1), (". I build ", 0),
         ("web apps", 1), (" and ", 0), ("games", 1), (",", 0)],
        [("teach programming, and tinker with ", 0), ("microchips", 1), (" when I get the chance.", 0)],
    ]
    rows = []
    for i, parts in enumerate(lines):
        spans = "".join(
            f'<tspan class="{"hl" if hl else ""}">{html.escape(t)}</tspan>' for t, hl in parts)
        rows.append(f'<text x="80" y="{134 + i * 27}" class="body">{spans}</text>')
    stack = "JavaScript · TypeScript · Node.js · Pixi.js · Three.js · ESP32 · C++ · Unity"
    h = 268
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="Dávid Attila Marcell — full-stack developer bridging web and hardware">
<style>
  text {{ font-family: {FONT}; }}
  .name {{ font-size: 36px; font-weight: 900; fill: {C["ink"]}; }}
  .body {{ font-size: 16.5px; fill: {C["soft"]}; }}
  .hl {{ fill: {C["blue"]}; font-weight: 700; }}
  .stack {{ font-size: 13.5px; font-weight: 700; fill: {C["soft"]}; letter-spacing: .3px; }}
  .cart {{ animation: ride 7s cubic-bezier(.45,0,.25,1) infinite; }}
  @keyframes ride {{
    0%, 12% {{ transform: translateY(0); }}
    70%, 100% {{ transform: translateY({h - 52}px); }}
  }}
  @media (prefers-reduced-motion: reduce) {{ .cart {{ animation: none; }} }}
</style>
<line x1="{TRUNK}" y1="44" x2="{TRUNK}" y2="{h}" stroke="{C["blue"]}" stroke-width="4"/>
<rect class="cart" x="{TRUNK - 7}" y="38" width="14" height="26" rx="5" fill="{C["blue"]}"/>
{station(TRUNK, 44, C["blue"])}
<text x="60" y="57" class="name">Dávid Attila Marcell</text>
<rect x="56" y="78" width="{W - 70}" height="{h - 92}" rx="12" fill="none" stroke="{C["blue"]}" stroke-width="4"/>
<rect x="61.5" y="83.5" width="{W - 81}" height="{h - 103}" rx="8" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="3"/>
{"".join(rows)}
<text x="80" y="{h - 38}" class="stack">{html.escape(stack)}</text>
</svg>
'''


# ---------- section title: a station on its own line colour ----------
def section(title, color):
    h = 64
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{html.escape(title)}">
<style> text {{ font-family: {FONT}; font-size: 30px; font-weight: 900; fill: {C["ink"]}; }} </style>
<line x1="{TRUNK}" y1="0" x2="{TRUNK}" y2="{h}" stroke="{color}" stroke-width="4"/>
{station(TRUNK, 34, color)}
<text x="60" y="45">{html.escape(title)}</text>
</svg>
'''


# ---------- pill button, optionally with the portfolio's plane ----------
def pill(label, plane=False):
    text_w = round(len(label) * 8.6)
    pad = 22
    icon = 30 if plane else 0
    w = pad * 2 + text_w + icon
    h = 46
    plane_svg = (f'<image href="data:image/png;base64,{plane_b64}" x="{pad + text_w + 8}" y="12" width="22" height="22"/>'
                 if plane else "")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(label)}">
<style> text {{ font-family: {FONT}; font-size: 15px; font-weight: 700; fill: {C["ink"]}; }} </style>
<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="21" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="3"/>
<text x="{pad}" y="28.5">{html.escape(label)}</text>
{plane_svg}
</svg>
'''


write("header.svg", header())
write("projects.svg", section("Projects", C["yellow"]))
write("pill-portfolio.svg", pill("Portfolio", plane=True))
write("pill-linkedin.svg", pill("LinkedIn"))
write("pill-itchio.svg", pill("itch.io"))
write("pill-all-projects.svg", pill("See all projects", plane=True))


# ---------- project cards: same markup/CSS as the portfolio's main row ----------
projects = json.load(open(os.path.join(PORTFOLIO, "data/projects.json"), encoding="utf-8"))
featured = [p for p in projects if p.get("isFeatured")][:6]


def card_html(p):
    d = datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00"))
    img = "file:///" + os.path.abspath(os.path.join(PORTFOLIO, p["images"][0])).replace("\\", "/")
    plane = "file:///" + os.path.abspath(os.path.join(PORTFOLIO, "data/icons/plane-blue.png")).replace("\\", "/")
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
  html, body {{ margin: 0; background: transparent; }}
  .card {{ position: relative; box-sizing: border-box; width: 240px; height: 360px; display: flex; align-items: flex-end;
          border: 3px solid {C["ink"]}; border-radius: 8px; overflow: hidden; background: {C["paper"]} url('{img}') center/cover no-repeat;
          font-family: {FONT}; }}
  .plane {{ position: absolute; top: 10px; right: 10px; width: 26px; height: 26px; transform: rotate(-45deg); }}
  .info {{ width: 100%; background: {C["paper"]}; border-top: 3px solid {C["ink"]}; padding: 10px; box-sizing: border-box; }}
  .date {{ margin: -4px 0 2px; color: {C["soft"]}; font-size: 12.8px; }}
  .title {{ margin: 0; color: {C["ink"]}; font-weight: 800; font-size: 15.2px; line-height: 1.1;
           white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
</style></head><body>
<div class="card"><img class="plane" src="{plane}">
<div class="info"><p class="date">{d:%d/%m/%Y}</p><p class="title">{html.escape(p["nameEng"])}</p></div></div>
</body></html>'''


from playwright.sync_api import sync_playwright

for old in os.listdir(OUT):
    if old.startswith("card-"):
        os.remove(os.path.join(OUT, old))

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="msedge")
    page = browser.new_page(viewport={"width": 260, "height": 380}, device_scale_factor=2)
    for p in featured:
        tmp = os.path.join(HERE, "_card.html")
        open(tmp, "w", encoding="utf-8").write(card_html(p))
        page.goto("file:///" + tmp.replace("\\", "/"))
        page.wait_for_load_state("networkidle")
        page.locator(".card").screenshot(path=os.path.join(OUT, f"card-{p['id']}.png"), omit_background=True)
        os.remove(tmp)
    browser.close()

# ---------- README ----------
cards = "\n".join(
    f'<a href="{SITE}#/projects/{p["id"]}"><img src="assets/card-{p["id"]}.png" alt="{html.escape(p["nameEng"])}" width="250"></a>'
    for p in featured)

readme = f'''<a href="{SITE}"><img src="assets/header.svg" alt="Dávid Attila Marcell — full-stack developer bridging web and hardware" width="100%"></a>

<p>
<a href="{SITE}"><img src="assets/pill-portfolio.svg" alt="Portfolio" height="40"></a>
<a href="https://www.linkedin.com/in/marcell-attila-david/"><img src="assets/pill-linkedin.svg" alt="LinkedIn" height="40"></a>
<a href="https://dam001.itch.io/"><img src="assets/pill-itchio.svg" alt="itch.io" height="40"></a>
</p>

<a href="{SITE}#/projects"><img src="assets/projects.svg" alt="Projects" width="100%"></a>

<p>
{cards}
</p>

<a href="{SITE}#/projects"><img src="assets/pill-all-projects.svg" alt="See all projects" height="40"></a>

<!-- Generated by build/build.py from the portfolio's featured projects. -->
'''
with open(os.path.join(REPO, "README.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(readme)
print("built", len(featured), "cards:", ", ".join(p["id"] for p in featured))
