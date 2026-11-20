"""Builds the profile README and its images in the portfolio's dark metro-map style.

    python build/build.py [path-to-portfolioV6]

Plain Python, no dependencies. Writes the SVGs into assets/ and README.md.
Edit HEADER_LINES / TECH_LINES / LINKS below and re-run to change the content.
"""
import base64, html, os, sys

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

# ---------- content ----------
HEADER_LINES = [
    [("Hey, I'm ", 0), ("Marci", 1), (", a ", 0), ("full-stack developer", 1), (" bridging ", 0),
     ("web", 1), (" and ", 0), ("hardware", 1), (".", 0)],
    [("Research developer at ", 0), ("Bay Zoltán Research Institute", 1), (". I build web apps and", 0)],
    [("games, teach programming, and tinker with microchips when I get the chance.", 0)],
]

# Each line: name, colour, stations. A station shared by two lines (same
# label, "interchange") is drawn as one capsule joining both lines.
TECH_LINES = [
    ("WEB", C["blue"], ["HTML & CSS", "JavaScript", "TypeScript", "Node.js", "Pixi.js", "Three.js"]),
    ("HARDWARE", C["red"], ["ESP32", "JavaScript", "C++", "Arduino", "Web Serial / BLE", "3D printing"]),
    ("GAMES", C["green"], ["Unity", "C#", "Photon", "Blender", "Python"]),
]

LINKS = [  # (label, url, file, plane icon)
    ("Portfolio", SITE, "pill-portfolio.svg", True),
    ("Projects", SITE + "#/projects", "pill-projects.svg", False),
    ("LinkedIn", "https://www.linkedin.com/in/marcell-attila-david/", "pill-linkedin.svg", False),
    ("itch.io", "https://dam001.itch.io/", "pill-itchio.svg", False),
]

os.makedirs(OUT, exist_ok=True)
plane_b64 = base64.b64encode(open(os.path.join(PORTFOLIO, "data/icons/plane-blue.png"), "rb").read()).decode()

MOTION = """
  .pulse { transform-box: fill-box; transform-origin: center; animation: pulse 2.8s ease-out infinite; }
  @keyframes pulse { 0% { transform: scale(1); opacity: .7; } 80%, 100% { transform: scale(2.6); opacity: 0; } }
  @media (prefers-reduced-motion: reduce) { .pulse, .cart, .nudge { animation: none; } .fly { display: none; } }
"""


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def station(x, y, color):
    return f'<circle cx="{x}" cy="{y}" r="9" fill="{C["paper"]}" stroke="{color}" stroke-width="4"/>'


def pulse(x, y, color):
    return f'<circle class="pulse" cx="{x}" cy="{y}" r="9" fill="none" stroke="{color}" stroke-width="3"/>'


def plane_img(size):
    return (f'<image href="data:image/png;base64,{plane_b64}" x="{-size / 2}" y="{-size / 2}" '
            f'width="{size}" height="{size}"/>')


def svg(w, h, body, style="", label=None):
    aria = f'role="img" aria-label="{html.escape(label)}"' if label else 'aria-hidden="true"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {aria}>\n'
            f'<style>\n  text {{ font-family: {FONT}; }}\n{style}\n{MOTION}</style>\n{body}\n</svg>\n')


# ---------- header: name station + intro card; a plane flies over, a cart rides down ----------
def header():
    top = 40                        # headroom for the plane's flight
    sy = top + 44                   # name station
    card_y = top + 80
    card_h = 34 + 27 * len(HEADER_LINES)
    h = card_y + card_h + 22
    rows = []
    for i, parts in enumerate(HEADER_LINES):
        spans = "".join(f'<tspan class="{"hl" if hl else ""}">{html.escape(t)}</tspan>' for t, hl in parts)
        rows.append(f'<text x="82" y="{card_y + 40 + i * 27}" class="body">{spans}</text>')
    flight = f"M -40 {top - 2} C {W * .3} {top - 34}, {W * .62} {top + 20}, {W + 40} {top - 16}"
    style = f"""
  .name {{ font-size: 38px; font-weight: 900; fill: {C["ink"]}; }}
  .body {{ font-size: 16.5px; fill: {C["soft"]}; }}
  .hl {{ fill: {C["blue"]}; font-weight: 700; }}
  .cart {{ animation: ride 6s cubic-bezier(.45,0,.25,1) infinite; }}
  @keyframes ride {{ 0%, 15% {{ transform: translateY(0); }} 75%, 100% {{ transform: translateY({h - sy + 10}px); }} }}"""
    body = f"""<g class="fly">{plane_img(26)}<animateMotion dur="12s" begin="0.5s" repeatCount="indefinite" rotate="auto"
   keyPoints="0;1;1" keyTimes="0;0.45;1" calcMode="linear" path="{flight}"/></g>
<line x1="{TRUNK}" y1="{sy}" x2="{TRUNK}" y2="{h}" stroke="{C["blue"]}" stroke-width="4"/>
<rect class="cart" x="{TRUNK - 7}" y="{sy - 6}" width="14" height="26" rx="5" fill="{C["blue"]}"/>
{pulse(TRUNK, sy, C["blue"])}
{station(TRUNK, sy, C["blue"])}
<text x="60" y="{sy + 13}" class="name">Dávid Attila Marcell</text>
<rect x="57" y="{card_y - 5}" width="{W - 71}" height="{card_h + 10}" rx="12" fill="none" stroke="{C["blue"]}" stroke-width="4"/>
<rect x="62.5" y="{card_y + .5}" width="{W - 82}" height="{card_h - 1}" rx="8" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="3"/>
{"".join(rows)}"""
    return svg(W, h, body, style, "Dávid Attila Marcell — full-stack developer bridging web and hardware")


# ---------- tech stack: lines branch off the trunk, one station per technology ----------
def tech_map():
    head_y = 34                     # "Tech stack" station
    first_y, gap = 128, 100         # y of the first line, distance between lines
    x0, x1 = 170, W - 40            # first / last station x
    r = 18                          # elbow radius
    ys = [first_y + i * gap for i in range(len(TECH_LINES))]
    h = ys[-1] + 44
    step = (x1 - x0) / (max(len(s) for _, _, s in TECH_LINES) - 1)

    # station x per (line, label); interchange labels share the first line's x
    pos = {}
    for li, (_, _, stations) in enumerate(TECH_LINES):
        for si, label in enumerate(stations):
            pos[(li, label)] = x0 + si * step
    owners = {}
    for li, (_, _, stations) in enumerate(TECH_LINES):
        for label in stations:
            owners.setdefault(label, []).append(li)
    for label, lis in owners.items():
        if len(lis) > 1:
            for li in lis:
                pos[(li, label)] = pos[(lis[0], label)]

    parts = [f'<line x1="{TRUNK}" y1="0" x2="{TRUNK}" y2="{ys[-1] - r}" stroke="{C["blue"]}" stroke-width="4"/>',
             pulse(TRUNK, head_y, C["blue"]), station(TRUNK, head_y, C["blue"]),
             f'<text x="60" y="{head_y + 11}" class="title">Tech stack</text>']
    tracks, carts, stops, labels = [], [], [], []
    for li, (name, color, stations) in enumerate(TECH_LINES):
        y = ys[li]
        end = max(pos[(li, s)] for s in stations)
        path = f"M {TRUNK} {y - r} Q {TRUNK} {y} {TRUNK + r} {y} H {end}"
        tracks.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="4" stroke-linejoin="round"/>')
        labels.append(f'<text x="{TRUNK + 26}" y="{y - 12}" class="line" fill="{color}">{name}</text>')
        dur = 7 + li * 1.3
        carts.append(f'<g class="fly"><rect x="-13" y="-7" width="26" height="14" rx="5" fill="{color}"/>'
                     f'<animateMotion dur="{dur}s" begin="{li * 1.1}s" repeatCount="indefinite" rotate="auto" '
                     f'keyPoints="0;1;1" keyTimes="0;0.8;1" keySplines="0.45 0 0.25 1;0 0 1 1" calcMode="spline" '
                     f'path="{path}"/></g>')
        for label in stations:
            x = pos[(li, label)]
            shared = owners[label]
            if len(shared) > 1 and li != shared[0]:
                labels.append(f'<text x="{x}" y="{y + 30}" class="stop" text-anchor="middle">{html.escape(label)}</text>')
                continue  # the capsule itself is drawn once, by its first line
            if len(shared) > 1:
                y2 = ys[shared[-1]]
                stops.append(f'<rect x="{x - 11}" y="{y - 11}" width="22" height="{y2 - y + 22}" rx="11" '
                             f'fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="4"/>')
                continue  # labelled once, under the bottom end of the capsule
            stops.append(station(x, y, color))
            labels.append(f'<text x="{x}" y="{y + 30}" class="stop" text-anchor="middle">{html.escape(label)}</text>')
    style = f"""
  .title {{ font-size: 30px; font-weight: 900; fill: {C["ink"]}; }}
  .line {{ font-size: 12px; font-weight: 800; letter-spacing: 1.5px; }}
  .stop {{ font-size: 14.5px; font-weight: 700; fill: {C["ink"]}; }}"""
    body = "\n".join(parts + tracks + carts + stops + labels)
    alt = "Tech stack — " + "; ".join(f"{n.title()}: {', '.join(s)}" for n, _, s in TECH_LINES)
    return svg(W, h, body, style, alt), alt


# ---------- pill button, optionally with the portfolio's plane nudging forward ----------
def pill(label, plane=False):
    text_w = round(len(label) * 8.6)
    pad = 22
    w = pad * 2 + text_w + (30 if plane else 0)
    h = 46
    style = """
  .label { font-size: 15px; font-weight: 700; fill: %s; }
  .nudge { animation: nudge 2.4s ease-in-out infinite; }
  @keyframes nudge { 0%%, 100%% { transform: translate(-2px, 1px); } 50%% { transform: translate(3px, -1px); } }""" % C["ink"]
    body = (f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="21" fill="{C["paper"]}" '
            f'stroke="{C["ink"]}" stroke-width="3"/>\n<text x="{pad}" y="28.5" class="label">{html.escape(label)}</text>')
    if plane:
        body += f'\n<g transform="translate({pad + text_w + 19} 23)"><g class="nudge">{plane_img(22)}</g></g>'
    return svg(w, h, body, style, label)


# ---------- write everything ----------
for old in os.listdir(OUT):  # drop images from earlier designs
    os.remove(os.path.join(OUT, old))

write("header.svg", header())
tech_svg, tech_alt = tech_map()
write("tech-stack.svg", tech_svg)
for label, _, file, plane in LINKS:
    write(file, pill(label, plane))

pills = "\n".join(f'<a href="{url}"><img src="assets/{file}" alt="{html.escape(label)}" height="40"></a>'
                  for label, url, file, _ in LINKS)
readme = f'''<a href="{SITE}"><img src="assets/header.svg" alt="Dávid Attila Marcell — full-stack developer bridging web and hardware" width="100%"></a>

<p>
{pills}
</p>

<a href="{SITE}#/projects"><img src="assets/tech-stack.svg" alt="{html.escape(tech_alt)}" width="100%"></a>

<!-- Generated by build/build.py -->
'''
with open(os.path.join(REPO, "README.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(readme)
print("built:", ", ".join(sorted(os.listdir(OUT))))
