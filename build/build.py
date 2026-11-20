"""Builds the profile README and its images in the portfolio's dark metro-map style.

    python build/build.py [path-to-portfolioV6]

Plain Python, no dependencies. Writes the SVGs into assets/ and README.md.
Edit INTRO / LINKS below (and the stations in tech_map) and re-run to
change the content. Phones get the same images, scaled down to ~40%,
so text is sized large relative to the canvas to stay readable there.

Same map grammar as the portfolio (css/style.css, js/carts.js):
  - ring stations, each station's name as a heading
  - paper cards with an ink border
  - coloured lines running side by side and curving off through rounded bends
  - 27x15 carts that hop station to station at a constant speed, pause at
    every stop and bounce back and forth between the ends of their line
"""
import base64, hashlib, html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(REPO, "assets")
PORTFOLIO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "..", "portfolioV6")
SITE = "https://www.damdev.xyz/Content/portfolioV6/"

# portfolio dark theme (css/common.css)
C = dict(cream="#18181a", paper="#232326", ink="#e2ddd0", soft="#b8b2a6",
         red="#e2483c", yellow="#f2b632", blue="#5090c8", green="#5aad7c")
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"
W = 860          # canvas width (header + map share it, so the lines line up)
SHOW_W = 600     # display width in the README
TRUNK = 30
PARALLEL = 4     # centre-to-centre gap of side-by-side lines = line width, so they touch
# the three lines side by side, left to right (the rightmost turns off first)
BUNDLE = [(C["green"], TRUNK - PARALLEL), (C["red"], TRUNK), (C["blue"], TRUNK + PARALLEL)]

# ---------- content ----------
INTRO = [("Hey, I'm ", 0), ("Marci", 1), (", a ", 0), ("full-stack developer", 1), (" bridging ", 0),
         ("web", 1), (" and ", 0), ("hardware", 1), (". Research developer at ", 0),
         ("Bay Zoltán Research Institute", 1),
         (". I build web apps and games, teach programming, and tinker with microchips.", 0)]

LINKS = [  # (label, url, file, plane icon)
    ("Portfolio", SITE, "pill-portfolio.svg", True),
    ("Projects", SITE + "#/projects", "pill-projects.svg", False),
    ("LinkedIn", "https://www.linkedin.com/in/marcell-attila-david/", "pill-linkedin.svg", False),
    ("itch.io", "https://dam001.itch.io/", "pill-itchio.svg", False),
]

# cart motion (js/carts.js uses 350 px/s and a 1 s pause; slower here, the map is small)
SPEED, PAUSE, MIN_HOP, MAX_HOP = 120, 1.0, 0.5, 2.5

os.makedirs(OUT, exist_ok=True)
_plane = os.path.join(PORTFOLIO, "data/icons/plane-blue.png")
if os.path.exists(_plane):
    plane_b64 = base64.b64encode(open(_plane, "rb").read()).decode()
else:  # no portfolio checkout: reuse the icon embedded in the current pill
    plane_b64 = re.search(r"base64,([^\"]+)", open(os.path.join(OUT, "pill-portfolio.svg")).read()).group(1)

REDUCED = "@media (prefers-reduced-motion: reduce) { .moving { display: none; } }"


def write(name, text):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def svg(w, h, body, style="", label=None, defs=""):
    aria = f'role="img" aria-label="{html.escape(label)}"' if label else 'aria-hidden="true"'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" {aria}>\n'
            f'<defs>{defs}</defs>\n<style>\n  text {{ font-family: {FONT}; }}\n{style}\n  {REDUCED}\n</style>\n'
            f'{body}\n</svg>\n')


def hub(x, y, r):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="4"/>'


def faded(gid, x, y1, y2, color, fade_top):
    """One vertical line segment fading out at an image edge, so the break
    between two images reads as the line continuing, not as a cut."""
    a, b = ((0, 0), (40 / (y2 - y1), 1)) if fade_top else ((1 - 40 / (y2 - y1), 1), (1, 0))
    stops = [a, b, (1, 1)] if fade_top else [(0, 1), a, b]
    grad = (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{y1}" x2="0" y2="{y2}">'
            + "".join(f'<stop offset="{o:.3f}" stop-color="{color}" stop-opacity="{op}"/>' for o, op in stops)
            + "</linearGradient>")
    return grad, f'<rect x="{x - 2}" y="{y1}" width="4" height="{y2 - y1}" fill="url(#{gid})"/>'


def bundle(prefix, y1, y2, fade_top):
    """The three touching lines between y1 and y2, fading at one end."""
    defs, body = "", ""
    for i, (color, x) in enumerate(BUNDLE):
        g, r = faded(f"{prefix}{i}", x, y1, y2, color, fade_top)
        defs += g
        body += r
    return defs, body


def cart(color, path, stops, offset=0.0):
    """A cart riding `path`, hopping between `stops` (distances along the path,
    in px, ascending, the last one = path end) like js/carts.js: constant speed
    with an eased start and end per hop, a pause at every stop, bouncing
    between the first and last."""
    order = list(range(len(stops))) + list(range(len(stops) - 2, 0, -1)) + [0]
    total_len = stops[-1] if stops[-1] > 0 else 1
    points, times, splines = [], [0.0], []
    t = 0.0
    for i, idx in enumerate(order):
        here = stops[idx] / total_len
        points.append(here)
        if i == len(order) - 1:
            break
        t += PAUSE                                  # pause at this stop
        times.append(t)
        splines.append("0 0 1 1")
        points.append(here)
        nxt = order[i + 1]                          # then hop to the next one
        t += min(MAX_HOP, max(MIN_HOP, abs(stops[nxt] - stops[idx]) / SPEED))
        times.append(t)
        splines.append(".45 0 .55 1")
    return (f'<g class="moving"><rect x="-13.5" y="-7.5" width="27" height="15" rx="2" fill="{color}"/>'
            f'<animateMotion dur="{t:.2f}s" begin="{-offset:.2f}s" repeatCount="indefinite" rotate="auto" '
            f'calcMode="spline" keyPoints="{";".join(f"{p:.4f}" for p in points)}" '
            f'keyTimes="{";".join(f"{x / t:.4f}" for x in times)}" keySplines="{";".join(splines)}" path="{path}"/></g>')


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
    return [run[min(range(len(samples)), key=lambda k: (samples[k][0] - tx) ** 2 + (samples[k][1] - ty) ** 2)]
            for tx, ty in targets]


def wrap(parts, max_chars):
    """Word-wrap (text, highlighted) runs into lines of at most max_chars."""
    words = []
    for text, hl in parts:
        for i, w in enumerate(re.split(r"(?<= )", text)):
            if w:
                words.append((w, hl))
    lines, cur, n = [], [], 0
    for w, hl in words:
        if n + len(w.rstrip()) > max_chars and cur:
            lines.append(cur)
            cur, n = [], 0
        cur.append((w, hl))
        n += len(w)
    lines.append(cur)
    return lines


def legend(x, y, size):
    out = []
    for name, color in (("WEB", C["blue"]), ("HARDWARE", C["red"]), ("GAMES", C["green"])):
        bw = len(name) * size * .72 + size * 1.9
        bh = size * 1.85
        out.append(f'<rect x="{x}" y="{y - bh / 2}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="{color}"/>'
                   f'<text x="{x + bw / 2}" y="{y + size * .36}" class="badge" text-anchor="middle">{name}</text>')
        x += bw + 10
    return out


LINE_STYLE = """
  .title { font-weight: 900; fill: %(ink)s; }
  .badge { font-weight: 800; letter-spacing: 1.2px; fill: %(cream)s; }
  .stop { font-weight: 700; fill: %(ink)s; paint-order: stroke; stroke: #0d1117; stroke-width: 5px; stroke-linejoin: round; }
""" % C


# ---------- header: name station + intro card ----------
def header(w, name_size, body_size, chars):
    sy = 42                                         # name station
    lines = wrap(INTRO, chars)
    line_h = body_size * 1.55
    card_y = sy + name_size * .55 + 12
    card_h = body_size * 1.6 + line_h * (len(lines) - 1) + body_size * .9
    h = card_y + card_h + 48
    rows = []
    for i, parts in enumerate(lines):
        spans = "".join(f'<tspan class="{"hl" if hl else ""}">{html.escape(t)}</tspan>' for t, hl in parts)
        rows.append(f'<text x="84" y="{card_y + body_size * 1.75 + i * line_h:.1f}" class="body">{spans}</text>')
    defs, lines_svg = bundle("hd", sy, h, fade_top=False)
    style = f"""
  .name {{ font-size: {name_size}px; font-weight: 900; fill: {C["ink"]}; }}
  .body {{ font-size: {body_size}px; fill: {C["soft"]}; }}
  .hl {{ fill: {C["blue"]}; font-weight: 700; }}"""
    body = f"""{lines_svg}
{hub(TRUNK, sy, 16)}
<text x="62" y="{sy + name_size * .36:.1f}" class="name">Dávid Attila Marcell</text>
<rect x="61.5" y="{card_y + 1.5:.1f}" width="{w - 63}" height="{card_h - 3:.1f}" rx="8" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="3"/>
{"".join(rows)}"""
    return svg(w, round(h), body, style, "Dávid Attila Marcell — full-stack developer bridging web and hardware", defs)


# ---------- desktop tech map: hand-laid, with a crossing and a merge ----------
# All three lines run in from the top, through the "Tech stack" hub, touching,
# then fan out, every bend rounded:
#   WEB       first row, straight across.
#   HARDWARE  second row; cuts up at 45deg THROUGH the JavaScript station,
#             crossing the Web line there, and carries on above it.
#   GAMES     climbs in two 45deg steps to run right alongside the Web line
#             for the stations they share (Pixi.js, Three.js).
# Shared stations are one interchange dot (white ring), never duplicated.
# Every climb sits halfway between two stops. Station names slant up
# and to the right at 45deg, all above their dot.
X0, STEP = 112, 125
Y_HEAD, Y_LEGEND = 64, 134
# used on all three lines: one stop on the shared trunk, before they fan out
TRUNK_STOP, Y_TRUNK_STOP = "Python", 405
Y_HW_TOP, Y_WEB, Y_HW, Y_GAMES = 300, 470, 600, 730     # extra room above Web for its names
RUN = 84          # horizontal run of a climb between rows (steeper than 45deg)
BEND = 16
STOP_R, SHARED_R = 13, 16
LABEL = 28


def col(c):
    return X0 + c * STEP


def climb(c, y_from, y_to):
    """A climb centred in the gap after column c."""
    mid, d = col(c) + STEP / 2, RUN
    return [(mid - d / 2, y_from), (mid + d / 2, y_to)]


def slanted(x, y, label):
    """A station name reading up and to the right at 45deg from (x, y)."""
    return (f'<text x="{x:.1f}" y="{y:.1f}" class="stop" transform="rotate(-45 {x:.1f} {y:.1f})">'
            f'{html.escape(label)}</text>')


def stations_svg(lines, label_pos):
    """One dot per technology (shared ones become a single white interchange),
    each with its name placed by label_pos(x, y, r, index) -> (x, y)."""
    seen = {}
    for color, stations in lines:
        for i, (label, x, y) in enumerate(stations):
            seen.setdefault(label, []).append((color, x, y, i))
    dots, labels = [], []
    for label, where in seen.items():
        xs = [x for _, x, _, _ in where]
        ys = [y for _, _, y, _ in where]
        cx, cy = sum(xs) / len(xs), (min(ys) + max(ys)) / 2
        if len(where) == 1 or max(xs) - min(xs) > 1 or max(ys) - min(ys) > PARALLEL * 2:
            # one line, or the same tech on two separate lines : a dot per place
            for color, x, y, i in where:
                r = STOP_R if len(where) == 1 else SHARED_R
                stroke = color if len(where) == 1 else C["ink"]
                dots.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C["paper"]}" stroke="{stroke}" stroke-width="4"/>')
                lx, ly = label_pos(x, y, r, i, label)
                labels.append(slanted(lx, ly, label))
            continue
        r = SHARED_R + (max(ys) - min(ys)) / 2      # covers lines running side by side
        dots.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="4"/>')
        lx, ly = label_pos(cx, cy, r, where[0][3], label)
        labels.append(slanted(lx, ly, label))
    return dots, labels


def tech_map():
    js_x, pixi_x, three_x = col(1), col(4), col(5)
    beside_web = Y_WEB + PARALLEL                   # Games' track while beside Web
    hw_up = [(js_x - RUN, Y_HW), (col(2) - 22, Y_HW_TOP)]

    lines = [  # (colour, bundle x, corners after the hub, stations)
        (C["blue"], TRUNK + PARALLEL, [(TRUNK + PARALLEL, Y_WEB), (col(5), Y_WEB)],
         [("HTML & CSS", col(0), Y_WEB), ("JavaScript", js_x, Y_WEB), ("TypeScript", col(2), Y_WEB),
          ("Node.js", col(3), Y_WEB), ("Pixi.js", pixi_x, Y_WEB), ("Three.js", three_x, Y_WEB)]),
        (C["red"], TRUNK, [(TRUNK, Y_HW)] + hw_up + [(col(5), Y_HW_TOP)],
         [("ESP32", col(0), Y_HW), ("JavaScript", js_x, Y_WEB), ("C++", col(2), Y_HW_TOP),
          ("Arduino", col(3), Y_HW_TOP), ("BLE / Serial", col(4), Y_HW_TOP), ("3D printing", col(5), Y_HW_TOP)]),
        (C["green"], TRUNK - PARALLEL,
         [(TRUNK - PARALLEL, Y_GAMES)] + climb(1, Y_GAMES, Y_HW) + climb(3, Y_HW, beside_web) + [(col(5), beside_web)],
         [("Unity", col(0), Y_GAMES), ("C#", col(1), Y_GAMES), ("Photon", col(2), Y_HW),
          ("Blender", col(3), Y_HW), ("Pixi.js", pixi_x, beside_web), ("Three.js", three_x, beside_web)]),
    ]
    h = Y_GAMES + 60
    defs, lead = bundle("tm", 0, Y_HEAD, fade_top=True)
    tracks, carts = [], []
    for li, (color, bx, corners, stations) in enumerate(lines):
        pts = [(bx, Y_HEAD)] + corners
        elbow = 24 + (bx - (TRUNK - PARALLEL))      # nested elbows: outer lines curve wider
        d, samples = rounded(pts, [elbow] + [BEND] * (len(pts) - 2))
        tracks.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round"/>')
        carts.append(cart(color, d, distances(samples, [(bx, Y_HEAD), (bx, Y_TRUNK_STOP)] + [(x, y) for _, x, y in stations]),
                          offset=4.7 + li * 6.3))
    dots, labels = stations_svg([(c, s) for c, _, _, s in lines],
                                lambda x, y, r, i, n: (x + r * .45, y - r * .8 - 4))
    r = SHARED_R + PARALLEL                         # covers all three touching lines
    dots.append(f'<circle cx="{TRUNK}" cy="{Y_TRUNK_STOP}" r="{r}" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="4"/>')
    labels.append(slanted(TRUNK + r * .45, Y_TRUNK_STOP - r * .8 - 4, TRUNK_STOP))
    style = LINE_STYLE + f"""
  .title {{ font-size: 56px; }} .badge {{ font-size: 20px; }} .stop {{ font-size: {LABEL}px; }}"""
    body = "\n".join([lead] + tracks + dots + carts
                     + [hub(TRUNK, Y_HEAD, 18), f'<text x="64" y="{Y_HEAD + 20}" class="title">Tech stack</text>']
                     + legend(64, Y_LEGEND, 20) + labels)
    alt = "Tech stack — " + "; ".join(f"{n}: {', '.join([TRUNK_STOP] + [l for l, _, _ in s])}"
                                      for n, (_, _, _, s) in zip(("Web", "Hardware", "Games"), lines))
    return svg(W, h, body, style, alt, defs), alt


# ---------- pill button (the app's outline button), optional static plane ----------
def pill(label, plane=False):
    text_w = round(len(label) * 9.2)
    pad = 20
    w = pad * 2 + text_w + (30 if plane else 0)
    h = 42
    style = f"""
  .label {{ font-size: 16px; font-weight: 700; fill: {C["ink"]}; }}"""
    body = (f'<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="19.5" fill="none" '
            f'stroke="{C["ink"]}" stroke-width="3"/>\n<text x="{pad}" y="27" class="label">{html.escape(label)}</text>')
    if plane:
        body += (f'\n<image href="data:image/png;base64,{plane_b64}" x="{pad + text_w + 7}" y="10" '
                 f'width="22" height="22"/>')
    return svg(w, h, body, style, label)


# ---------- write everything ----------
for old in os.listdir(OUT):  # drop images from earlier designs
    os.remove(os.path.join(OUT, old))

write("header.svg", header(W, 64, 38, 33))
tech_svg, tech_alt = tech_map()
write("tech-stack.svg", tech_svg)
for label, _, file, plane in LINKS:
    write(file, pill(label, plane))


def still(name, file, alt):
    # Named anchor (no href): GitHub otherwise turns every bare image into a
    # link to its own file, making the whole map one big button. Only the
    # pills are real links.
    # Fixed width, not 100%: desktop shows the big type at a normal size,
    # while GitHub's max-width: 100% shrinks it to fit the box on phones.
    return f'<a name="{name}"><img src="assets/{file}" alt="{html.escape(alt)}" width="{SHOW_W}"></a>'


pills = "\n".join(f'<a href="{url}"><img src="assets/{file}" alt="{html.escape(label)}" height="42"></a>'
                  for label, url, file, _ in LINKS)
readme = f'''{still("about", "header.svg", "Dávid Attila Marcell — full-stack developer bridging web and hardware")}

<p>
{pills}
</p>

{still("tech-stack", "tech-stack.svg", tech_alt)}

<!-- Generated by build/build.py -->
'''
# Cache-busting: GitHub caches README images, so tag every asset link with a
# hash of its content. A changed image gets a new URL and shows up right away.
readme = re.sub(r'(src|srcset)="assets/([^"]+)"', lambda m: '%s="assets/%s?v=%s"' % (
    m.group(1), m.group(2), hashlib.md5(open(os.path.join(OUT, m.group(2)), "rb").read()).hexdigest()[:8]), readme)
with open(os.path.join(REPO, "README.md"), "w", encoding="utf-8", newline="\n") as f:
    f.write(readme)
print("built:", ", ".join(sorted(os.listdir(OUT))))
