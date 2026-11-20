"""Builds the profile README and its images in the portfolio's dark metro-map style.

    python build/build.py [path-to-portfolioV6]

Plain Python, no dependencies. Writes the SVGs into assets/ and README.md.
Edit HEADER_LINES / LINKS below (and the stations in tech_map) and re-run to change the content.

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
W = 800          # both images share this width, so the trunk lines up at x=TRUNK
TRUNK = 30
ELBOW = 24       # radius where a line curves off the trunk

# ---------- content ----------
HEADER_LINES = [
    [("Hey, I'm ", 0), ("Marci", 1), (", a ", 0), ("full-stack developer", 1), (" bridging ", 0),
     ("web", 1), (" and ", 0), ("hardware", 1), (".", 0)],
    [("Research developer at ", 0), ("Bay Zoltán Research Institute", 1), (". I build web apps", 0)],
    [("and games, teach programming, and tinker with microchips.", 0)],
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


def faded_trunk(gid, y1, y2, fade_top, fade_bottom, color=None, x=None):
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
            + "".join(f'<stop offset="{o:.3f}" stop-color="{color or C["blue"]}" stop-opacity="{a}"/>' for o, a in stops)
            + "</linearGradient>")
    rect = f'<rect x="{(TRUNK if x is None else x) - 2}" y="{y1}" width="4" height="{span}" fill="url(#{gid})"/>'
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
    # all three lines start at the name station and run down, touching, fading at the edge
    grad, trunk = "", ""
    for i, (color, x) in enumerate(BUNDLE):
        g, r = faded_trunk(f"trunkA{i}", sy, h, False, True, color, x)
        grad += g
        trunk += r
    style = f"""
  .name {{ font-size: 36px; font-weight: 900; fill: {C["ink"]}; }}
  .body {{ font-size: 16px; fill: {C["soft"]}; }}
  .hl {{ fill: {C["blue"]}; font-weight: 700; }}"""
    plane = (f'<g class="moving"><image href="data:image/png;base64,{plane_b64}" x="-13" y="-13" width="26" height="26"/>'
             f'<animateMotion dur="12s" begin="0.5s" repeatCount="indefinite" rotate="auto" keyPoints="0;1;1" '
             f'keyTimes="0;0.45;1" calcMode="linear" path="{flight}"/></g>')
    body = f"""{trunk}
<circle cx="{TRUNK}" cy="{sy}" r="{HUB_R + 2}" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="4"/>
<text x="62" y="{sy + 12}" class="name">Dávid Attila Marcell</text>
<rect x="61.5" y="{card_y + 1.5}" width="{W - 63}" height="{card_h - 3}" rx="8" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="3"/>
{"".join(rows)}
{plane}"""
    return svg(W, h, body, style, "Dávid Attila Marcell — full-stack developer bridging web and hardware", grad)


# ---------- tech stack: a hand-laid metro map ----------
# All three lines run in from the top, through the "Tech stack" hub, as one
# parallel bundle (like the portfolio's branches merging into the trunk), then
# fan out, every bend rounded:
#   WEB       first row, straight across.
#   HARDWARE  second row; cuts up at 45deg THROUGH the JavaScript station,
#             crossing the Web line there, and carries on above it.
#   GAMES     third row; climbs at 45deg to run right alongside the Web line
#             for the stations they share (Pixi.js, Three.js).
# Shared stations are one interchange dot (white ring), never duplicated.
X0, STEP = 110, 129              # column x = X0 + col * STEP
Y_HEAD = 52                      # "Tech stack" hub
Y_LEGEND = 96                    # line colour badges, under the heading
Y_WEB, Y_HW, Y_GAMES = 214, 276, 338     # rows evenly spaced (with Y_HW_TOP)
Y_HW_TOP = 152                   # Hardware's row after it crosses Web
PARALLEL = 4                     # centre-to-centre gap of side-by-side lines = line width, so they touch
BEND = 22                        # radius of the rounded 45deg bends
STOP_R, HUB_R = 11, 14           # station / interchange dot radius


# the three lines side by side, left to right (the rightmost turns off first)
BUNDLE = [(C["green"], TRUNK - PARALLEL), (C["red"], TRUNK), (C["blue"], TRUNK + PARALLEL)]


def col(c):
    return X0 + c * STEP


def climb(c, y_from, y_to):
    """A 45deg step centred in the gap after column c, so every turn sits
    halfway between two stops with a straight run before and after it."""
    mid, d = col(c) + STEP / 2, abs(y_from - y_to)
    return [(mid - d / 2, y_from), (mid + d / 2, y_to)]


def rounded(points, radii):
    """Polyline with every inner corner rounded (radii[i] for corner i).
    Returns the SVG path and dense samples of it, for measuring distances."""
    d = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    samples = [points[0]]

    def line_to(p):
        a = samples[-1]
        n = max(1, int(((p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2) ** .5 / 2))
        samples.extend((a[0] + (p[0] - a[0]) * i / n, a[1] + (p[1] - a[1]) * i / n) for i in range(1, n + 1))
        d.append(f"L {p[0]:.1f} {p[1]:.1f}")

    for i in range(1, len(points) - 1):
        (ax, ay), (bx, by), (cx, cy) = points[i - 1], points[i], points[i + 1]
        la = ((bx - ax) ** 2 + (by - ay) ** 2) ** .5
        lc = ((cx - bx) ** 2 + (cy - by) ** 2) ** .5
        r = min(radii[i - 1], la / 2, lc / 2)
        p1 = (bx + (ax - bx) * r / la, by + (ay - by) * r / la)   # where the curve starts
        p2 = (bx + (cx - bx) * r / lc, by + (cy - by) * r / lc)   # and ends
        line_to(p1)
        for k in range(1, 13):
            t = k / 12
            samples.append(((1 - t) ** 2 * p1[0] + 2 * (1 - t) * t * bx + t * t * p2[0],
                            (1 - t) ** 2 * p1[1] + 2 * (1 - t) * t * by + t * t * p2[1]))
        d.append(f"Q {bx:.1f} {by:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    line_to(points[-1])
    return " ".join(d), samples


def distances(samples, targets):
    """Distance along the sampled path to the sample nearest each target."""
    run = [0.0]
    for (ax, ay), (bx, by) in zip(samples, samples[1:]):
        run.append(run[-1] + ((bx - ax) ** 2 + (by - ay) ** 2) ** .5)
    out = []
    for tx, ty in targets:
        i = min(range(len(samples)), key=lambda k: (samples[k][0] - tx) ** 2 + (samples[k][1] - ty) ** 2)
        out.append(run[i])
    return out, run[-1]


def tech_map():
    js_x = col(1)
    pixi_x, three_x = col(4), col(5)
    games_y_top = Y_WEB + PARALLEL           # Games' track while beside Web

    # Hardware: ESP32 on its row, then 45deg up through JavaScript to the top row.
    hw_up_start = (js_x - (Y_HW - Y_WEB), Y_HW)
    hw_up_end = (js_x + (Y_WEB - Y_HW_TOP), Y_HW_TOP)
    # Games climbs in two steps: after C# up to the row Hardware has left,
    # after Blender up to run right beside Web.

    lines = {
        # name: (colour, bundle x, corner points after the hub, stations [(label, x, y)])
        "WEB": (C["blue"], TRUNK + PARALLEL,
                [(TRUNK + PARALLEL, Y_WEB), (col(5), Y_WEB)],
                [("HTML & CSS", col(0), Y_WEB), ("JavaScript", js_x, Y_WEB), ("TypeScript", col(2), Y_WEB),
                 ("Node.js", col(3), Y_WEB), ("Pixi.js", pixi_x, Y_WEB), ("Three.js", three_x, Y_WEB)]),
        "HARDWARE": (C["red"], TRUNK,
                     [(TRUNK, Y_HW), hw_up_start, hw_up_end, (col(5), Y_HW_TOP)],
                     [("ESP32", col(0), Y_HW), ("JavaScript", js_x, Y_WEB), ("C++", col(2), Y_HW_TOP),
                      ("Arduino", col(3), Y_HW_TOP), ("BLE / Serial", col(4), Y_HW_TOP),
                      ("3D printing", col(5), Y_HW_TOP)]),
        "GAMES": (C["green"], TRUNK - PARALLEL,
                  [(TRUNK - PARALLEL, Y_GAMES)] + climb(1, Y_GAMES, Y_HW) + climb(3, Y_HW, games_y_top)
                  + [(col(5), games_y_top)],
                  [("Unity", col(0), Y_GAMES), ("C#", col(1), Y_GAMES), ("Photon", col(2), Y_HW),
                   ("Blender", col(3), Y_HW), ("Pixi.js", pixi_x, games_y_top),
                   ("Three.js", three_x, games_y_top)]),
    }
    h = Y_GAMES + 48

    defs, leadins, tracks, carts, dots, labels = [], [], [], [], [], []
    for li, (name, (color, bx, corners, stations)) in enumerate(lines.items()):
        # lead-in from the top edge, fading in, so every line runs "from the beginning"
        gid = f"in{li}"
        defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{Y_HEAD}">'
                    f'<stop offset="0" stop-color="{color}" stop-opacity="0"/>'
                    f'<stop offset=".8" stop-color="{color}" stop-opacity="1"/></linearGradient>')
        leadins.append(f'<rect x="{bx - 2}" y="0" width="4" height="{Y_HEAD}" fill="url(#{gid})"/>')
        # the line itself: hub -> down the bundle -> its row, every corner rounded;
        # outer lines of the bundle curve wider so the three elbows nest
        elbow = 22 + (bx - (TRUNK - PARALLEL))
        pts = [(bx, Y_HEAD)] + corners
        d, samples = rounded(pts, [elbow] + [BEND] * (len(pts) - 2))
        tracks.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
        stops, _ = distances(samples, [(bx, Y_HEAD)] + [(x, y) for _, x, y in stations])
        carts.append(cart(color, d, stops, offset=4.7 + li * 6.3))

    # colour legend under the heading
    legend, lx = [], 60
    for name, (color, *_rest) in lines.items():
        bw = len(name) * 8.4 + 22
        legend.append(f'<rect x="{lx}" y="{Y_LEGEND - 11}" width="{bw}" height="22" rx="11" fill="{color}"/>'
                      f'<text x="{lx + bw / 2}" y="{Y_LEGEND + 4.5}" class="badge" text-anchor="middle">{name}</text>')
        lx += bw + 10

    # stations: one dot per technology; shared ones become a single interchange.
    # Every name sits under its dot.
    seen = {}
    for name, (color, _, _, stations) in lines.items():
        for label, x, y in stations:
            seen.setdefault(label, []).append((color, x, y))
    for label, where in seen.items():
        xs = [x for _, x, _ in where]
        ys = [y for _, _, y in where]
        cx, cy = sum(xs) / len(xs), (min(ys) + max(ys)) / 2
        if len(where) == 1:
            r = STOP_R
            dots.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{C["paper"]}" stroke="{where[0][0]}" stroke-width="4"/>')
        else:
            r = HUB_R + (max(ys) - min(ys)) / 2   # covers lines running side by side
            dots.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="4"/>')
        labels.append(f'<text x="{cx}" y="{cy + r + 18}" class="stop" text-anchor="middle">{html.escape(label)}</text>')

    hub = f'<circle cx="{TRUNK}" cy="{Y_HEAD}" r="{HUB_R + 2}" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="4"/>'
    style = f"""
  .title {{ font-size: 30px; font-weight: 900; fill: {C["ink"]}; }}
  .badge {{ font-size: 12px; font-weight: 800; letter-spacing: 1.2px; fill: {C["cream"]}; }}
  .stop {{ font-size: 14px; font-weight: 700; fill: {C["ink"]};
           paint-order: stroke; stroke: #0d1117; stroke-width: 5px; stroke-linejoin: round; }}"""
    body = "\n".join(leadins + tracks + dots + carts
                     + [hub, f'<text x="62" y="{Y_HEAD + 11}" class="title">Tech stack</text>'] + legend + labels)
    alt = "Tech stack — " + "; ".join(
        f"{n.title()}: {', '.join(l for l, _, _ in st)}" for n, (_, _, _, st) in lines.items())
    return svg(W, h, body, style, alt, "".join(defs)), alt


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
