"""Builds the profile README and its images in the portfolio's dark metro-map style.

    python build/build.py [path-to-portfolioV6]

Plain Python, no dependencies. Writes the SVGs into assets/ and README.md.
Edit HEADER_LINES / TECH_LINES / LINKS below and re-run to change the content.

Same map grammar as the portfolio (css/style.css, js/carts.js):
  - a blue trunk with ring stations, each station's name as a heading
  - paper cards with an ink border
  - coloured lines branching off the trunk through a rounded elbow
  - 27x15 carts that hop station to station at a constant speed, pause at
    every stop and bounce back and forth between the ends of their line
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
W = 760          # both images share this width, so the trunk lines up at x=TRUNK
TRUNK = 30
ELBOW = 24       # radius where a line curves off the trunk

# ---------- content ----------
HEADER_LINES = [
    [("Hey, I'm ", 0), ("Marci", 1), (", a ", 0), ("full-stack developer", 1), (" bridging ", 0),
     ("web", 1), (" and ", 0), ("hardware", 1), (".", 0)],
    [("Research developer at ", 0), ("Bay Zoltán Research Institute", 1), (". I build web apps", 0)],
    [("and games, teach programming, and tinker with microchips.", 0)],
]

# Lines top to bottom: name, colour, stations (one per column, None = empty
# column). A label on two ADJACENT lines in the same column is an
# interchange, drawn as one capsule joining both lines.
TECH_LINES = [
    ("HARDWARE", C["red"],   ["ESP32", "JavaScript", "C++", "Arduino", "BLE / Serial", "3D printing"]),
    ("WEB",      C["blue"],  ["HTML & CSS", "JavaScript", "TypeScript", "Node.js", "Pixi.js", "Three.js"]),
    ("GAMES",    C["green"], ["Unity", "C#", "Photon", "Blender", "Pixi.js", "Three.js"]),
]

LINKS = [  # (label, url, file, plane icon)
    ("Portfolio", SITE, "pill-portfolio.svg", True),
    ("Projects", SITE + "#/projects", "pill-projects.svg", False),
    ("LinkedIn", "https://www.linkedin.com/in/marcell-attila-david/", "pill-linkedin.svg", False),
    ("itch.io", "https://dam001.itch.io/", "pill-itchio.svg", False),
]

# cart motion (js/carts.js uses 350 px/s and a 1 s pause; slower here, the map is small)
SPEED, PAUSE, MIN_HOP, MAX_HOP = 120, 1.0, 0.5, 2.5

os.makedirs(OUT, exist_ok=True)
plane_b64 = base64.b64encode(open(os.path.join(PORTFOLIO, "data/icons/plane-blue.png"), "rb").read()).decode()

REDUCED = "@media (prefers-reduced-motion: reduce) { .nudge { animation: none; } .moving { display: none; } }"


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def svg(w, h, body, style="", label=None, defs=""):
    aria = f'role="img" aria-label="{html.escape(label)}"' if label else 'aria-hidden="true"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {aria}>\n'
            f'<defs>{defs}</defs>\n<style>\n  text {{ font-family: {FONT}; }}\n{style}\n  {REDUCED}\n</style>\n'
            f'{body}\n</svg>\n')


def station(x, y, color):
    return f'<circle cx="{x}" cy="{y}" r="9" fill="{C["paper"]}" stroke="{color}" stroke-width="4"/>'


def faded_trunk(gid, y1, y2, fade_top, fade_bottom):
    """Vertical trunk segment that fades out at an image edge, so the break
    between two images reads as the line continuing, not as a cut."""
    span = y2 - y1
    stops = []
    if fade_top:
        stops += [(0, 0), (40 / span, 1)]
    else:
        stops += [(0, 1)]
    if fade_bottom:
        stops += [(1 - 40 / span, 1), (1, 0)]
    else:
        stops += [(1, 1)]
    grad = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{y1}" x2="0" y2="{y2}">'
            + "".join(f'<stop offset="{o:.3f}" stop-color="{C["blue"]}" stop-opacity="{a}"/>' for o, a in stops)
            + "</linearGradient>")
    rect = f'<rect x="{TRUNK - 2}" y="{y1}" width="4" height="{span}" fill="url(#{gid})"/>'
    return grad, rect


def cart(color, path, stops, offset=0.0):
    """A cart riding `path`, hopping between `stops` (distances along the path,
    in px, ascending) like js/carts.js: constant speed with an eased start and
    end per hop, a pause at every stop, bouncing between the first and last."""
    order = list(range(len(stops))) + list(range(len(stops) - 2, 0, -1)) + [0]
    total_len = stops[-1] if stops[-1] > 0 else 1
    points, times, splines = [], [0.0], []
    t = 0.0
    for i, idx in enumerate(order):
        here = stops[idx] / total_len
        if i == len(order) - 1:
            points.append(here)
            break
        # pause at this stop
        points.append(here)
        t += PAUSE
        times.append(t)
        splines.append("0 0 1 1")
        points.append(here)
        # hop to the next stop
        nxt = order[i + 1]
        hop = min(MAX_HOP, max(MIN_HOP, abs(stops[nxt] - stops[idx]) / SPEED))
        t += hop
        times.append(t)
        splines.append(".45 0 .55 1")
    key_times = ";".join(f"{x / t:.4f}" for x in times)
    key_points = ";".join(f"{p:.4f}" for p in points)
    return (f'<g class="moving"><rect x="-13.5" y="-7.5" width="27" height="15" rx="2" fill="{color}"/>'
            f'<animateMotion dur="{t:.2f}s" begin="{-offset:.2f}s" repeatCount="indefinite" rotate="auto" calcMode="spline" '
            f'keyPoints="{key_points}" keyTimes="{key_times}" keySplines="{";".join(splines)}" path="{path}"/></g>')


# ---------- header: name station + intro card, plane flying over ----------
def header():
    top = 44                        # headroom for the plane
    sy = top + 26                   # name station
    card_y = sy + 30
    card_h = 30 + 26 * len(HEADER_LINES)
    h = card_y + card_h + 48
    rows = []
    for i, parts in enumerate(HEADER_LINES):
        spans = "".join(f'<tspan class="{"hl" if hl else ""}">{html.escape(t)}</tspan>' for t, hl in parts)
        rows.append(f'<text x="82" y="{card_y + 37 + i * 26}" class="body">{spans}</text>')
    flight = f"M -40 {top - 8} C {W * .3} {top - 40}, {W * .62} {top + 12}, {W + 40} {top - 22}"
    grad, trunk = faded_trunk("trunkA", sy, h, False, True)
    style = f"""
  .name {{ font-size: 36px; font-weight: 900; fill: {C["ink"]}; }}
  .body {{ font-size: 16px; fill: {C["soft"]}; }}
  .hl {{ fill: {C["blue"]}; font-weight: 700; }}"""
    plane = (f'<g class="moving"><image href="data:image/png;base64,{plane_b64}" x="-13" y="-13" width="26" height="26"/>'
             f'<animateMotion dur="12s" begin="0.5s" repeatCount="indefinite" rotate="auto" keyPoints="0;1;1" '
             f'keyTimes="0;0.45;1" calcMode="linear" path="{flight}"/></g>')
    body = f"""{trunk}
{station(TRUNK, sy, C["blue"])}
<text x="60" y="{sy + 12}" class="name">Dávid Attila Marcell</text>
<rect x="61.5" y="{card_y + 1.5}" width="{W - 63}" height="{card_h - 3}" rx="8" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="3"/>
{"".join(rows)}
{plane}"""
    return svg(W, h, body, style, "Dávid Attila Marcell — full-stack developer bridging web and hardware", grad)


# ---------- tech stack: lines branch off the trunk, one station per technology ----------
def tech_map():
    head_y = 52                     # "Tech stack" station
    first_y, gap = 128, 96          # first line's y, distance between lines
    x0, x1 = 206, W - 52            # first / last column x
    cols = max(len(s) for _, _, s in TECH_LINES)
    step = (x1 - x0) / (cols - 1)
    ys = [first_y + i * gap for i in range(len(TECH_LINES))]
    h = ys[-1] + 46
    trunk_end = ys[-1] - ELBOW

    def is_shared_with_next(li, ci):
        return (li + 1 < len(TECH_LINES) and ci < len(TECH_LINES[li + 1][2])
                and TECH_LINES[li][2][ci] and TECH_LINES[li][2][ci] == TECH_LINES[li + 1][2][ci])

    def is_shared_with_prev(li, ci):
        return li > 0 and is_shared_with_next(li - 1, ci)

    grad, trunk = faded_trunk("trunkB", 0, trunk_end, True, False)
    tracks, badges, carts, stops, capsules, labels = [], [], [], [], [], []

    # blue trunk cart: Tech stack station <-> where the last line curves off
    carts.append(cart(C["blue"], f"M {TRUNK} {head_y} V {trunk_end}", [0, trunk_end - head_y]))

    for li, (name, color, stations) in enumerate(TECH_LINES):
        y = ys[li]
        xs = [x0 + ci * step for ci, s in enumerate(stations) if s]
        end = xs[-1]
        tracks.append(f'<path d="M {TRUNK} {y - ELBOW} Q {TRUNK} {y} {TRUNK + ELBOW} {y} H {end}" fill="none" '
                      f'stroke="{color}" stroke-width="4"/>')
        # line badge sitting on the track, like a metro line sign
        bw = len(name) * 8.4 + 22
        badges.append(f'<rect x="{TRUNK + ELBOW + 14}" y="{y - 11}" width="{bw}" height="22" rx="11" fill="{color}"/>'
                      f'<text x="{TRUNK + ELBOW + 14 + bw / 2}" y="{y + 4.5}" class="badge" text-anchor="middle">{name}</text>')
        # start each line's cart at a different point in its loop, so they don't move in lockstep
        carts.append(cart(color, f"M {xs[0]} {y} H {end}", [x - xs[0] for x in xs], offset=4.7 + li * 6.3))
        for ci, label in enumerate(stations):
            if not label:
                continue
            x = x0 + ci * step
            if is_shared_with_prev(li, ci):
                labels.append(f'<text x="{x}" y="{y + 31}" class="stop" text-anchor="middle">{html.escape(label)}</text>')
                continue  # capsule drawn by the line above
            if is_shared_with_next(li, ci):
                capsules.append(f'<rect x="{x - 11}" y="{y - 11}" width="22" height="{gap + 22}" rx="11" '
                                f'fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="4"/>')
                continue  # labelled once, under the bottom end
            stops.append(station(x, y, color))
            labels.append(f'<text x="{x}" y="{y + 31}" class="stop" text-anchor="middle">{html.escape(label)}</text>')

    style = f"""
  .title {{ font-size: 30px; font-weight: 900; fill: {C["ink"]}; }}
  .badge {{ font-size: 12px; font-weight: 800; letter-spacing: 1.2px; fill: {C["cream"]}; }}
  .stop {{ font-size: 14px; font-weight: 700; fill: {C["ink"]}; }}"""
    body = "\n".join([trunk] + tracks + stops + capsules + carts + [
        station(TRUNK, head_y, C["blue"]),
        f'<text x="60" y="{head_y + 11}" class="title">Tech stack</text>'] + badges + labels)
    alt = "Tech stack — " + "; ".join(f"{n.title()}: {', '.join(s for s in st if s)}" for n, _, st in TECH_LINES)
    return svg(W, h, body, style, alt, grad), alt


# ---------- pill button (the app's outline button), optional plane nudging forward ----------
def pill(label, plane=False):
    text_w = round(len(label) * 8.6)
    pad = 20
    w = pad * 2 + text_w + (30 if plane else 0)
    h = 42
    style = f"""
  .label {{ font-size: 15px; font-weight: 700; fill: {C["ink"]}; }}
  .nudge {{ animation: nudge 2.4s ease-in-out infinite; }}
  @keyframes nudge {{ 0%, 100% {{ transform: translate(-2px, 1px); }} 50% {{ transform: translate(3px, -1px); }} }}"""
    body = (f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="19.5" fill="none" '
            f'stroke="{C["ink"]}" stroke-width="3"/>\n<text x="{pad}" y="26.5" class="label">{html.escape(label)}</text>')
    if plane:
        body += (f'\n<g transform="translate({pad + text_w + 18} 21)"><g class="nudge">'
                 f'<image href="data:image/png;base64,{plane_b64}" x="-11" y="-11" width="22" height="22"/></g></g>')
    return svg(w, h, body, style, label)


# ---------- write everything ----------
for old in os.listdir(OUT):  # drop images from earlier designs
    os.remove(os.path.join(OUT, old))

write("header.svg", header())
tech_svg, tech_alt = tech_map()
write("tech-stack.svg", tech_svg)
for label, _, file, plane in LINKS:
    write(file, pill(label, plane))

pills = "\n".join(f'<a href="{url}"><img src="assets/{file}" alt="{html.escape(label)}" height="38"></a>'
                  for label, url, file, _ in LINKS)
# The two maps are wrapped in a NAMED anchor (no href): GitHub otherwise turns
# every bare image into a link to its own file, making the whole map one big
# button. Only the pills are real links.
readme = f'''<a name="about"><img src="assets/header.svg" alt="Dávid Attila Marcell — full-stack developer bridging web and hardware" width="100%"></a>

<p>
{pills}
</p>

<a name="tech-stack"><img src="assets/tech-stack.svg" alt="{html.escape(tech_alt)}" width="100%"></a>

<!-- Generated by build/build.py -->
'''
with open(os.path.join(REPO, "README.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(readme)
print("built:", ", ".join(sorted(os.listdir(OUT))))
