#!/usr/bin/env python3
"""Planungsseite „Gebäude als Hohlkörper“: schreibt plug/hollow/plan.html aus plug/hollow/study.json und plug/testcase/variants_fit.json.

Alle Zahlen und Schnitte der Seite stammen aus der Studie (`python3 -m plug.hollow.study`, Laserscan 1:1500 und OSM 1:1500, Wand und Dach 0,8 mm).
Die Seite ist eine Planung: kein Generatorumbau, keine STL.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.hollow.build_plan
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "plan.html")
STUDY = json.load(open(os.path.join(HERE, "study.json")))
FIT = json.load(open(os.path.join(ROOT, "plug", "testcase", "variants_fit.json")))

NAMES = ("01_paulinum", "02_neues_augusteum", "03_hoersaalgebaeude", "04_seminargebaeude", "05_institutsgebaeude", "06_city_hochhaus")
TITLE = {"01_paulinum": "Paulinum", "02_neues_augusteum": "Neues Augusteum", "03_hoersaalgebaeude": "Hörsaalgebäude",
         "04_seminargebaeude": "Seminargebäude", "05_institutsgebaeude": "Institutsgebäude", "06_city_hochhaus": "City-Hochhaus"}
WALL, ROOF = 0.8, 0.8
PLATE_T, FOOT = 16.2, 10.2        # Platte B, Fußhöhe (plug/testcase/params.py)
V2_TOP = 23.3                     # Kassette V2: Oberkante über der Plattenoberseite (cassettes.md)
V2_W, V2_D = 12.96, 5.34


def de(x, n=1):
    return ("%.*f" % (n, x)).replace(".", ",")


def fmt(v):
    return ("%.1f" % v).rstrip("0").rstrip(".") if abs(v - round(v)) > 1e-9 else str(int(round(v)))


def rect_path(x0, y0, x1, y1):
    return "M%s %sH%sV%sH%sz" % (fmt(x0), fmt(y0), fmt(x1), fmt(y1), fmt(x0))


def ring_path(rings, X, Y):
    out = []
    for r in rings:
        out.append("M" + "L".join("%s %s" % (fmt(X(x)), fmt(Y(y))) for x, y in r) + "z")
    return "".join(out)


# --------------------------------------------------------------------------
# Abb. 1: Schnitt massiv und Schale (Paulinum, Laserscan 1:1500)
# --------------------------------------------------------------------------
def section_svg(name, hollow):
    v = STUDY["laserscan/" + name]
    sect = v["sect"]
    step = 0.4
    xs = [x for _, o, _ in sect for a, b in o for x in (a, b)]
    xmin, xmax = min(xs) - 7, max(xs) + 7
    H = v["H"]
    zmin = -PLATE_T
    k = 11.0
    m = 1.0
    W = (xmax - xmin + 2 * m) * k
    Hh = (H - zmin + 2 * m + 4) * k
    X = lambda x: (x - xmin + m) * k
    Y = lambda z: (H + 4 - z + m) * k
    # Kassette: Mitte dort, wo der Hohlraum bis V2_TOP mindestens V2_W + 0,4 breit ist
    kz = int(V2_TOP / step)
    cav_top = sect[min(kz, len(sect) - 1)][2]
    cx = None
    for a, b in sorted(cav_top, key=lambda t: t[0] - t[1]):
        if b - a >= V2_W + 0.4:
            cx = (a + b) / 2
            break
    if cx is None:
        a, b = max(cav_top, key=lambda t: t[1] - t[0])
        cx = (a + b) / 2
    # Fußintervall um die Kassette
    foot_iv = [iv for iv in sect[0][1]]
    fa, fb = max(foot_iv, key=lambda t: t[1] - t[0])
    p = []
    p.append('<svg viewBox="0 0 %s %s" role="img" aria-label="%s">' % (fmt(W), fmt(Hh),
             "Schnitt durch das Paulinum, %s" % ("als Schale mit 0,8 mm Wand" if hollow else "massiv mit Schacht für die Kassette")))
    # Platte
    p.append('<path class="plate" d="%s"/>' % rect_path(X(xmin + m), Y(0), X(xmax - m), Y(zmin)))
    # Gebäude außen
    outer = []
    for z1, o, c in sect:
        for a, b in o:
            outer.append(rect_path(X(a), Y(z1), X(b), Y(z1 - step) + 0.3))
    p.append('<path class="shell" d="%s"/>' % "".join(outer))
    # Fuß (voll, Querschnitt von Band 0)
    p.append('<path class="foot" d="%s"/>' % rect_path(X(fa), Y(-FOOT + 0), X(fb), Y(0)))
    p.append('<path class="plate-edge" d="%s"/>' % rect_path(X(fa), Y(-FOOT), X(fb), Y(0)))
    if hollow:
        cav = []
        for z1, o, c in sect:
            for a, b in c:
                cav.append(rect_path(X(a), Y(z1), X(b), Y(z1 - step) + 0.3))
        p.append('<path class="cav" d="%s"/>' % "".join(cav))
    else:
        # Schacht in der massiven Wand
        p.append('<path class="hole" d="%s"/>' % rect_path(X(cx - V2_W / 2 - 0.06), Y(V2_TOP + 0.4), X(cx + V2_W / 2 + 0.06), Y(-FOOT)))
    # Schacht im Fuß (auch bei Schale)
    if hollow:
        p.append('<path class="hole" d="%s"/>' % rect_path(X(cx - V2_W / 2 - 0.06), Y(0.01), X(cx + V2_W / 2 + 0.06), Y(-FOOT)))
    # Kassette (schematisch)
    p.append('<path class="cass" d="%s"/>' % rect_path(X(cx - V2_W / 2), Y(V2_TOP), X(cx + V2_W / 2), Y(-FOOT)))
    # LED-Streifen oben auf der Kassette
    p.append('<path class="led" d="%s"/>' % rect_path(X(cx - 1.1), Y(V2_TOP - 0.5), X(cx + 1.1), Y(V2_TOP - 0.5 - 16.7)))
    # Lichtstrahlen zur Wand rechts
    for dz in (3.5, 8.5, 13.5):
        zc = V2_TOP - 0.5 - dz
        p.append('<path class="ray" d="M%s %sH%s"/>' % (fmt(X(cx + 1.6)), fmt(Y(zc)), fmt(X(cx + V2_W / 2 + (6 if hollow else 3)))))
    # Plattenoberseite
    p.append('<path class="ground" d="M%s %sH%s"/>' % (fmt(X(xmin + m)), fmt(Y(0)), fmt(X(xmax - m))))
    # Beschriftungen
    p.append('<text x="%s" y="%s" class="lbl">Platte B (16,2)</text>' % (fmt(X(xmin + m) + 8), fmt(Y(zmin) - 10)))
    p.append('<text x="%s" y="%s" class="lbl">Fuß, voll (10,2)</text>' % (fmt(X(fa) + 8), fmt(Y(-FOOT) + 18)))
    p.append('<text x="%s" y="%s" class="lbl">Kassette V2 (schematisch)</text>' % (fmt(X(cx - V2_W / 2)), fmt(Y(V2_TOP) - 8)))
    if hollow:
        # Wand-Maßlinie auf Höhe 10 mm an der rechten Außenwand
        zc = 10.0
        k10 = int(zc / step)
        o = sect[k10][1]
        a, b = max(o, key=lambda t: t[1])
        p.append('<path class="dim" d="M%s %sH%s"/>' % (fmt(X(b) + 3), fmt(Y(zc)), fmt(X(b - WALL) - 3)))
        p.append('<text x="%s" y="%s" class="lbl">Wand 0,8</text>' % (fmt(X(b) + 8), fmt(Y(zc) - 7)))
        p.append('<text x="%s" y="%s" class="lbl dim-t">Hohlraum, unten offen;</text>' % (fmt(X(xmin + m) + 8), fmt(Y(H + 2.2))))
        p.append('<text x="%s" y="%s" class="lbl dim-t">Boden = Oberseite des Fußes</text>' % (fmt(X(xmin + m) + 8), fmt(Y(H + 2.2) + 16)))
    else:
        p.append('<text x="%s" y="%s" class="lbl dim-t">Material bis zum Schacht:</text>' % (fmt(X(xmin + m) + 8), fmt(Y(H + 2.2))))
        p.append('<text x="%s" y="%s" class="lbl dim-t">mindestens 2,4 mm</text>' % (fmt(X(xmin + m) + 8), fmt(Y(H + 2.2) + 16)))
    p.append("</svg>")
    return "".join(p)


# --------------------------------------------------------------------------
# Abb. 2: Ablauf im Generator
# --------------------------------------------------------------------------
def flow_svg():
    def box(x, y, w, h, title, sub, cls=""):
        return ('<rect class="bx %s" x="%d" y="%d" width="%d" height="%d" rx="4"/>' % (cls, x, y, w, h) +
                '<text class="bt" x="%d" y="%d">%s</text>' % (x + 12, y + 22, title) +
                '<text class="bs" x="%d" y="%d">%s</text>' % (x + 12, y + 42, sub))
    s = ['<svg class="wide" viewBox="0 0 960 330" role="img" aria-label="Ablauf im Generator: massiver Volumenkörper bleibt, aus ihm entsteht zusätzlich die Schale">',
         '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>']
    s.append(box(10, 20, 190, 62, "Datenquelle", "osm · lod2 · laserscan"))
    s.append(box(250, 20, 220, 62, "Volumenkörper massiv", "building_solid() · models()"))
    s.append(box(10, 150, 200, 62, "bleibt wie heute", "komplett · Platte · 3MF"))
    s.append(box(580, 20, 250, 62, "hohl(solid, wand, dach)", "neu, ca. 40 Zeilen · Manifold", "new"))
    s.append(box(580, 150, 250, 62, "einzeln_hohl/*.stl", "neuer Ordner pro Quelle", "new"))
    s.append(box(250, 150, 220, 62, "einzeln/*.stl", "massiv, wie bisher"))
    s.append(box(580, 250, 370, 62, "später, im Steckmechanismus (plug/)", "Fuß 10,2 voll · Schacht · Kassette", "later"))
    arrows = [(200, 51, 250, 51, ""), (470, 51, 580, 51, "je 0,4 mm Höhe"), (705, 82, 705, 150, "Wand 0,8 · Dach 0,8"),
              (360, 82, 360, 150, "wie bisher"), (705, 212, 705, 250, "")]
    for x1, y1, x2, y2, t in arrows:
        s.append('<path class="ln" d="M%d %dL%d %d" marker-end="url(#ar)"/>' % (x1, y1, x2, y2))
        if t:
            s.append('<text class="al" x="%d" y="%d" %s>%s</text>' % ((x1 + x2) // 2 + (8 if x1 == x2 else 0), (y1 + y2) // 2 - (8 if y1 == y2 else -4), "" if x1 == x2 else 'text-anchor="middle"', t))
    s.append('<path class="ln dashed" d="M280 82V116H110V150" marker-end="url(#ar)"/>')
    s.append("</svg>")
    return "".join(s)


# --------------------------------------------------------------------------
# Abb. 3: Wandstärke in Extrusionslinien
# --------------------------------------------------------------------------
def wall_svg():
    k = 80.0   # px je mm
    rows = [(0.4, "1 Linie", "0,4 mm"), (0.8, "2 Linien", "0,8 mm"), (1.2, "3 Linien", "1,2 mm")]
    s = ['<svg viewBox="0 0 760 270" role="img" aria-label="Wandstärke 0,4, 0,8 und 1,2 Millimeter als eine, zwei und drei Extrusionslinien der 0,4-mm-Düse">']
    for i, (t, n, lab) in enumerate(rows):
        y = 20 + i * 82
        x0 = 330
        s.append('<path class="ray" d="M70 %d H%d"/>' % (y + 28, x0 - 10))
        s.append('<path class="ray" d="M%d %d H700"/>' % (x0 + t * k + 10, y + 28))
        for j in range(int(round(t / 0.4))):
            s.append('<rect class="shell" x="%s" y="%d" width="%s" height="56" rx="14"/>' % (fmt(x0 + j * 0.4 * k + 1), y, fmt(0.4 * k - 2)))
        s.append('<text class="lbl" x="70" y="%d">LED, innen</text>' % (y + 16))
        s.append('<text class="lbl" x="%d" y="%d">außen</text>' % (610, y + 16))
        s.append('<text class="lbl strong" x="%d" y="%d">%s</text>' % (x0 + t * k + 30, y + 74 - 12 if False else y + 50, "%s · %s" % (lab, n)))
    s.append("</svg>")
    return "".join(s)


# --------------------------------------------------------------------------
# Abb. 4: Draufsicht, wo die Decke über Luft liegt
# --------------------------------------------------------------------------
def heat_svg(name):
    v = STUDY["laserscan/" + name]
    rings = v["foot"]
    xs = [x for r in rings for x, _ in r]
    ys = [y for r in rings for _, y in r]
    k = 6.0
    m = 1.5
    x0, x1, y0, y1 = min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m
    X = lambda x: (x - x0) * k
    Y = lambda y: (y1 - y) * k
    W, Hh = (x1 - x0) * k, (y1 - y0) * k
    s = ['<svg width="%s" viewBox="0 0 %s %s" role="img" aria-label="Draufsicht %s: Flächen der Decke nach Spannweite">' % (fmt(W), fmt(W), fmt(Hh), TITLE[name])]
    s.append('<path class="fp" fill-rule="evenodd" d="%s"/>' % ring_path(rings, X, Y))
    for key, cls in (("0.5", "s1"), ("2.5", "s2"), ("5.0", "s3"), ("10.0", "s4")):
        rs = v["bridge_polys"].get(key, [])
        if rs:
            s.append('<path class="%s" fill-rule="evenodd" d="%s"/>' % (cls, ring_path(rs, X, Y)))
    s.append('<path class="fpl" fill-rule="evenodd" d="%s"/>' % ring_path(rings, X, Y))
    s.append("</svg>")
    return "".join(s)


# --------------------------------------------------------------------------
# Abb. 5: drei Wege für die Decke
# --------------------------------------------------------------------------
def roof_options_svg():
    k = 12.0
    out = ['<svg class="wide" viewBox="0 0 900 200" role="img" aria-label="Drei Wege für die Decke: glatte Decke als Brücke, 45-Grad-Gewölbe, Rippen">']
    defs = '<defs><marker id="ar2" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="currentColor"/></marker></defs>'
    out.append(defs)
    w, h = 19.6, 8.0     # Außenmaß in mm
    def panel(ox, title, kind):
        x0, y0 = ox, 52
        X = lambda x: x0 + x * k
        Y = lambda z: y0 + (h - z) * k
        g = ['<text class="lbl strong" x="%d" y="22">%s</text>' % (ox, title)]
        g.append('<path class="shell" d="%s"/>' % rect_path(X(0), Y(h), X(w), Y(0)))
        t = WALL
        if kind == "A":
            g.append('<path class="cav" d="%s"/>' % rect_path(X(t), Y(h - t), X(w - t), Y(0)))
            g.append('<path class="dim" marker-start="url(#ar2)" marker-end="url(#ar2)" d="M%s %sH%s"/>' % (fmt(X(t)), fmt(Y(h - t) + 18), fmt(X(w - t))))
            g.append('<text class="lbl" x="%s" y="%s" text-anchor="middle">Brücke 18 mm</text>' % (fmt(X(w / 2)), fmt(Y(h - t) + 36)))
        elif kind == "B":
            s_ = 4.0
            pts = [(t, 0), (w - t, 0), (w - t, h - t - s_), (w - t - s_, h - t), (t + s_, h - t), (t, h - t - s_)]
            g.append('<path class="cav" d="M%sz"/>' % "L".join("%s %s" % (fmt(X(a)), fmt(Y(b))) for a, b in pts))
            g.append('<path class="dim" marker-start="url(#ar2)" marker-end="url(#ar2)" d="M%s %sH%s"/>' % (fmt(X(t + s_)), fmt(Y(h - t) + 18), fmt(X(w - t - s_))))
            g.append('<text class="lbl" x="%s" y="%s" text-anchor="middle">Brücke 10 mm</text>' % (fmt(X(w / 2)), fmt(Y(h - t) + 36)))
            g.append('<text class="lbl dim-t" x="%s" y="%s">45°</text>' % (fmt(X(t + 0.3)), fmt(Y(h - t - s_ / 2) - 4)))
        else:
            g.append('<path class="cav" d="%s"/>' % rect_path(X(t), Y(h - t), X(w - t), Y(0)))
            g.append('<path class="shell" d="%s"/>' % rect_path(X(w / 2 - 0.4), Y(h - t), X(w / 2 + 0.4), Y(0)))
            for a, b in ((t, w / 2 - 0.4), (w / 2 + 0.4, w - t)):
                g.append('<path class="dim" marker-start="url(#ar2)" marker-end="url(#ar2)" d="M%s %sH%s"/>' % (fmt(X(a)), fmt(Y(h - t) + 18), fmt(X(b))))
            for cxx in (t + (w / 2 - 0.4 - t) / 2, w / 2 + 0.4 + (w / 2 - 0.4 - t) / 2):
                g.append('<text class="lbl" x="%s" y="%s" text-anchor="middle">8,6 mm</text>' % (fmt(X(cxx)), fmt(Y(h - t) + 36)))
        g.append('<path class="ground" d="M%s %sH%s"/>' % (fmt(X(-0.5)), fmt(Y(0)), fmt(X(w + 0.5))))
        return "".join(g)
    out.append(panel(10, "A  Glatte Decke", "A"))
    out.append(panel(310, "B  Gewölbe 45°", "B"))
    out.append(panel(610, "C  Rippe in der Mitte", "C"))
    out.append("</svg>")
    return "".join(out)


# --------------------------------------------------------------------------
# Tabellen
# --------------------------------------------------------------------------
def table_numbers():
    rows = []
    for n in NAMES:
        a, b = STUDY["laserscan/" + n], STUDY["osm/" + n]
        big = a["bridge"]["area_cls"]["5.0"]
        islands = a["islands"]["12.0"]
        cls = ' class="warn"' if 2 * a["bridge"]["maxr"] > 10 else ""
        rows.append("<tr><th scope=\"row\">%s</th><td>%s</td><td>%s</td><td>%s %%</td><td%s>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            TITLE[n], de(a["H"]), de(a["vol"] / 1000, 1), de(a["shell_pct"]), cls, de(2 * a["bridge"]["maxr"]),
            ("%s mm²" % big) if big else "–", islands, de(2 * b["bridge"]["maxr"])))
    return "\n".join(rows)


def table_fit():
    names = ("01_paulinum", "02_neues_augusteum", "03_hoersaalgebaeude", "04_seminargebaeude", "05_institutsgebaeude", "06_city_hochhaus")
    rows = []
    for n in names:
        tds = []
        for scale in ("1zu1500", "1zu1000"):
            f = FIT["%s/%s" % (scale, n)]
            for var in ("V2", "V2R"):
                w = f["walls_h"].get(var)
                if w is None:
                    tds.append('<td class="no">passt nicht</td>')
                elif w >= 1.2:
                    tds.append('<td class="yes">%s</td>' % de(w, 2))
                elif w >= WALL:
                    tds.append('<td class="new">%s neu</td>' % de(w, 2))
                else:
                    tds.append('<td class="no">%s zu dünn</td>' % de(w, 2))
        rows.append("<tr><th scope=\"row\">%s</th>%s</tr>" % (TITLE[n], "".join(tds)))
    return "\n".join(rows)


CSS = """
:root{
  /* Layout: schmale Lesespalte, Abbildungen volle Breite, Entscheidungskarten als Raster */
  --bg:#f3f5f8; --fg:#1b2531; --muted:#576577; --line:#d3dae3; --card:#ffffff;
  --accent:#a85d00; --accent-soft:#fbe9cc;
  --shell:#7f93ad; --cav:#fff6e0; --foot:#4f6580; --plate:#cdd4de; --hole:#f3f5f8; --cass:#2b3645; --led:#f0a233;
  --fp:#e4e9f0; --s1:#f4e2bb; --s2:#e9b44c; --s3:#d9722b; --s4:#b3261e;
  --ok:#1f7a4a; --ok-bg:#dff1e6; --warn:#a85d00; --warn-bg:#fbe9cc; --bad:#a82a22; --bad-bg:#f8dcd9;
  --sans:"Schibsted Grotesk",system-ui,-apple-system,"Segoe UI",sans-serif; --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#11161c; --fg:#e3e8ef; --muted:#97a3b3; --line:#29323e; --card:#19202a;
  --accent:#f0a233; --accent-soft:#3a2d14;
  --shell:#6a7f9b; --cav:#2b2416; --foot:#8497b1; --plate:#2b3441; --hole:#11161c; --cass:#c8d2df; --led:#f6b24a;
  --fp:#202935; --s1:#4a3d22; --s2:#a47a25; --s3:#d0702c; --s4:#e0483f;
  --ok:#62c48d; --ok-bg:#173325; --warn:#f0a233; --warn-bg:#3a2d14; --bad:#ee7b72; --bad-bg:#3c1b19; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#11161c; --fg:#e3e8ef; --muted:#97a3b3; --line:#29323e; --card:#19202a;
  --accent:#f0a233; --accent-soft:#3a2d14;
  --shell:#6a7f9b; --cav:#2b2416; --foot:#8497b1; --plate:#2b3441; --hole:#11161c; --cass:#c8d2df; --led:#f6b24a;
  --fp:#202935; --s1:#4a3d22; --s2:#a47a25; --s3:#d0702c; --s4:#e0483f;
  --ok:#62c48d; --ok-bg:#173325; --warn:#f0a233; --warn-bg:#3a2d14; --bad:#ee7b72; --bad-bg:#3c1b19; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font:16px/1.55 var(--sans);margin:0;
  padding-block:32px 72px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:1040px;margin:0 auto;display:flex;flex-direction:column;gap:44px}
h1{font-size:clamp(28px,5vw,40px);line-height:1.12;margin:0 0 10px;letter-spacing:-.01em;text-wrap:balance}
h2{font-size:22px;line-height:1.25;margin:0 0 12px;text-wrap:balance}
h3{font-size:16px;margin:0 0 6px}
p{margin:0 0 12px;max-width:70ch}
.lead{font-size:18px;color:var(--muted);max-width:62ch}
.eyebrow{font:500 12px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
code,.mono{font-family:var(--mono);font-size:.9em}
section{min-width:0}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:16px 18px;min-width:0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}
.summary .card h3{display:flex;gap:8px;align-items:center}
.pill{display:inline-block;font:500 11px var(--mono);letter-spacing:.04em;text-transform:uppercase;padding:2px 8px;border-radius:99px;white-space:nowrap}
.pill.ok{background:var(--ok-bg);color:var(--ok)} .pill.warn{background:var(--warn-bg);color:var(--warn)} .pill.bad{background:var(--bad-bg);color:var(--bad)} .pill.neutral{background:var(--fp);color:var(--muted)}
figure{margin:0;display:flex;flex-direction:column;gap:8px;min-width:0}
figcaption{color:var(--muted);font-size:14px;max-width:80ch}
.fig{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px;overflow-x:auto}
.fig svg{display:block;max-width:100%;height:auto;margin:0 auto}
.fig svg.wide{min-width:680px}
.pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.pair .fig{display:flex;flex-direction:column;gap:6px}
.pair .tag{font:500 12px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.heat{display:flex;flex-wrap:wrap;gap:18px;align-items:flex-start;justify-content:center}
.heat figure{align-items:center;flex:0 0 auto;max-width:100%}
.heat figcaption{text-align:center;font-size:13px}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;color:var(--muted);margin-top:10px;justify-content:center}
.legend i{display:inline-block;width:14px;height:14px;border-radius:3px;margin-right:6px;vertical-align:-2px;border:1px solid var(--line)}
.tblw{overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:var(--card)}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th,td{padding:8px 12px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
thead tr:nth-child(2) th:first-child,thead th[colspan]{text-align:right}
thead th{font:500 12px var(--mono);letter-spacing:.04em;color:var(--muted);vertical-align:bottom;white-space:normal}
tbody tr:last-child th,tbody tr:last-child td{border-bottom:0}
td.warn{color:var(--warn);font-weight:600} td.yes{color:var(--ok)} td.new{color:var(--accent);font-weight:600} td.no{color:var(--muted)}
.dec{display:flex;flex-direction:column;gap:10px}
.dec header{display:flex;gap:10px;align-items:baseline;justify-content:space-between;flex-wrap:wrap}
.dec h3{margin:0}
.opts{display:flex;flex-direction:column;gap:6px;margin:0;padding:0;list-style:none;font-size:14.5px}
.opts li{padding:7px 10px;border:1px solid var(--line);border-radius:6px}
.opts li.rec{border-color:var(--accent);background:var(--accent-soft)}
.opts b{font-weight:600}
.steps{display:flex;flex-direction:column;gap:0;margin:0;padding:0;list-style:none}
.steps li{display:grid;grid-template-columns:auto 1fr auto;gap:4px 14px;padding:12px 0;border-top:1px solid var(--line);align-items:baseline}
.steps li:first-child{border-top:0}
.steps .sn{font:500 12px var(--mono);color:var(--muted);width:18px}
.steps .why{grid-column:2;color:var(--muted);font-size:14px}
ul.plain{margin:0 0 12px;padding-left:20px;max-width:70ch} ul.plain li{margin-bottom:6px}
.note{border-left:3px solid var(--accent);padding:2px 0 2px 14px;color:var(--muted);max-width:70ch}
/* SVG */
svg text{font:12.5px var(--mono);fill:currentColor}
svg .lbl{font-size:12.5px} svg .strong{font-weight:600;font-size:14px;font-family:var(--sans)}
svg .dim-t{fill:var(--muted)}
.shell{fill:var(--shell)} .cav{fill:var(--cav)} .foot{fill:var(--foot)} .plate{fill:var(--plate)} .hole{fill:var(--hole)}
.cass{fill:var(--cass)} .led{fill:var(--led)} .plate-edge{fill:none;stroke:var(--bg);stroke-width:1.5;stroke-dasharray:4 3}
.ground{fill:none;stroke:var(--fg);stroke-width:1.5} .dim{fill:none;stroke:var(--fg);stroke-width:1.3}
.ray{fill:none;stroke:var(--led);stroke-width:2;stroke-dasharray:7 5}
.fp{fill:var(--fp)} .fpl{fill:none;stroke:var(--fg);stroke-width:1.2}
.s1{fill:var(--s1)} .s2{fill:var(--s2)} .s3{fill:var(--s3)} .s4{fill:var(--s4)}
.bx{fill:var(--card);stroke:var(--line);stroke-width:1.5} .bx.new{stroke:var(--accent);stroke-width:2} .bx.later{stroke-dasharray:6 4}
.bt{font-family:var(--sans);font-weight:600;font-size:14px} .bs{fill:var(--muted)} .al{fill:var(--muted);font-size:11.5px}
.ln{fill:none;stroke:currentColor;stroke-width:1.6} .ln.dashed{stroke-dasharray:6 4}
@media (max-width:560px){body{font-size:15px} th,td{padding:7px 9px}}
"""


def card(num, title, status, kind, options, text):
    lis = []
    for lab, desc, rec in options:
        lis.append('<li class="%s"><b>%s</b> %s</li>' % ("rec" if rec else "", lab, desc))
    return ('<article class="card dec"><header><h3>%s %s</h3><span class="pill %s">%s</span></header><p>%s</p><ul class="opts">%s</ul></article>' % (
        num, title, kind, status, text, "".join(lis)))


def page():
    hs = STUDY["laserscan/03_hoersaalgebaeude"]
    heat = []
    for n in NAMES:
        v = STUDY["laserscan/" + n]
        heat.append('<figure>%s<figcaption><b>%s</b><br>%s mm hoch · größte Brücke %s mm</figcaption></figure>' % (
            heat_svg(n), TITLE[n], de(v["H"]), de(2 * v["bridge"]["maxr"])))
    cards = [
        card("1", "Wandstärke", "wartet auf Lichtprobe", "warn",
             [("0,4 mm", "eine Linie, am meisten Licht, in der Hand empfindlich", False),
              ("0,8 mm", "zwei Linien, stabil, Licht mit heller LED wahrscheinlich ausreichend", True),
              ("1,2 mm", "drei Linien, wie die bisherige Lichtkammer; Licht ungewiss", False)],
             "Das Licht der LED muss durch die Wand. Ob 0,8 mm reicht, zeigt erst die Funktionsprobe mit Controller in Steckprobe 2 (Schritt L, drei Wandstreifen). Bis dahin ist die Wand ein Parameter."),
        card("2", "Decke über dem Hohlraum", "Entscheidung nötig", "warn",
             [("A  glatt", "Decke als Brücke, keine Zusatzteile; geht bei allen Gebäuden bis etwa 11 mm Spannweite", True),
              ("B  Gewölbe 45°", "Hörsaalgebäude braucht etwa 4 mm Gewölbehöhe, sonst nichts", False),
              ("C  Rippe", "eine 0,8-mm-Wand im Hohlraum des Hörsaalgebäudes; sie schattet das Licht ab", False)],
             "Nur das Hörsaalgebäude (flaches Dach) überspannt mehr als 11 mm. Die Brücke ist Dachunterseite, kein Passmaß; Durchhängen schadet dort kaum."),
        card("3", "Ausgabe", "Vorschlag", "neutral",
             [("Zusätzlich", "neuer Ordner <code>einzeln_hohl/</code>; komplett, Grundplatte, 3MF bleiben massiv", True),
              ("Ersatz", "<code>einzeln/</code> wird hohl, die massive Variante entfällt", False),
              ("Nur Laserscan", "hohl nur für die Quelle, die gedruckt wird", False)],
             "Die Komplettmodelle sind Schaustücke ohne LED und brauchen keinen Hohlraum. Hohl ist für die Gebäude mit Steckmechanismus."),
        card("4", "Fuß und Kassette", "offen, nicht blockierend", "neutral",
             [("Hohlraum und Fuß getrennt", "Generator liefert nur die Schale ab Plattenoberseite; der Fuß kommt aus <code>plug/</code>", True),
              ("Alles im Generator", "Fuß, Schacht und Kassettenaufnahme schon in <code>generate.py</code>", False)],
             "Welche Kassette (v4, V1, V2) und welcher Maßstab gelten, ist zurückgestellt. Die Schale hängt davon nicht ab, solange der Fuß unter ihr liegt."),
        card("5", "Licht in hohen Gebäuden", "ungemessen", "neutral",
             [("Wie die Kassette liegt", "LED sitzt unten, die Spitze bleibt dunkler; sie reicht bei V2 bis etwa 15 mm über die Platte", True),
              ("Innen hell lassen", "helles Filament, Hohlraum innen unbehandelt; Licht streut weiter nach oben", False),
              ("Längerer Streifen", "144 LED/m (13,9 × 12) oder zweiter Streifen, Kassette wird größer", False)],
             "Der Hohlraum ist ein zusammenhängender Raum, Licht erreicht alle Flügel. Das City-Hochhaus (96 mm) und das Paulinum (39 mm) sind aber viel höher als die LED."),
        card("6", "Farbe", "offen", "neutral",
             [("Hellfarbig, einfarbig", "ein helles Filament je Gebäude, Fassadenfarbe aus dem Filament", True),
              ("Wie die 3MF-Farben", "Zonen farbig, Licht färbt sich mit", False)],
             "Die 3MF-Zonenfarben gelten für die massiven Komplettmodelle. Wie farbige Wände Licht durchlassen, ist ungetestet."),
    ]
    steps = [
        ("Studie: Schale rechnen und Brücken messen", "Zahlen und Bilder auf dieser Seite, 12 Hohlkörper dicht", "erledigt", "ok", "Basis"),
        ("Lichtprobe: Wandstreifen 0,4 / 0,8 / 1,2 mit LED", "Teil des Funktionstests in Steckprobe 2 (Schritt L); legt die Wandstärke fest", "wartet", "warn", "blockiert 1"),
        ("Brückenprobe Dach: 10, 14, 18, 24 mm unter 0,8 mm Decke", "Mini-Gebäude, im selben Druck wie die Lichtprobe möglich", "vorgeschlagen", "neutral", "blockiert 2"),
        ("Generator: <code>hohl()</code>, Option, Ausgabeordner, Prüfzeile <code>dicht=True</code>", "Studie aus <code>plug/hollow/shell.py</code> übernehmen; Laufzeit etwa 20 s für das größte Gebäude", "nach Abnicken", "neutral", "Prototyp"),
        ("Schale mit Fuß und Kassette koppeln", "Fuß unter der Schale, Schacht, Anschlag; erst wenn Kassette und Maßstab feststehen", "später", "neutral", "Steckmechanismus"),
        ("Testdruck Hohlgebäude mit Licht", "ein Gebäude (Neues Augusteum oder Institutsgebäude) mit LED auf Platte B", "später", "neutral", "Auswertung"),
    ]
    steps_html = "".join('<li><span class="sn">%d</span><span><b>%s</b></span><span class="pill %s">%s</span><span class="why">%s · %s</span></li>' % (
        i, t, k, st, w, bl) for i, (t, w, st, k, bl) in enumerate(steps))
    html = f"""<title>Hohlkörper-Gebäude</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Schibsted+Grotesk:wght@400;500;600;700&display=swap">
<style>{CSS}</style>
<main>
<header>
  <div class="eyebrow">Planung · Generator · Steckmechanismus</div>
  <h1>Gebäude als Hohlkörper mit dünner Wand</h1>
  <p class="lead">Statt Lichtfenster bekommt jedes Gebäude eine durchgehende dünne Wand. Die LED in der Kassette leuchtet durch die ganze Hülle. Diese Seite legt fest, wie der Generator die Schale baut, und zeigt mit den echten Gebäuden, was dabei herauskommt.</p>
</header>

<section>
  <div class="summary">
    <div class="card"><h3>Machbar <span class="pill ok">gerechnet</span></h3><p>Alle 6 Gebäude lassen sich aus dem massiven Volumenkörper aushöhlen (Wand 0,8, Dach 0,8, unten offen), alle Ergebnisse sind dicht. Die Schale hat {de(min(STUDY['laserscan/'+n]['shell_pct'] for n in NAMES),0)} bis {de(max(STUDY['laserscan/'+n]['shell_pct'] for n in NAMES),0)} % des Volumens.</p></div>
    <div class="card"><h3>Die Decke <span class="pill ok">meist unkritisch</span></h3><p>Nur das Hörsaalgebäude überspannt mit flachem Dach mehr als 11 mm ({de(2*hs['bridge']['maxr'],0)} mm). Alle anderen liegen zwischen 2 und 11 mm.</p></div>
    <div class="card"><h3>Prototypen <span class="pill warn">noch nicht</span></h3><p>Wandstärke, Decke des Hörsaalgebäudes und Ausgabeform sind offen, dazu Fuß, Kassette und das Licht in hohen Gebäuden. Deshalb gibt es hier noch keine überarbeiteten Gebäude, nur die Studie und den Plan.</p></div>
  </div>
</section>

<section>
  <h2>So sieht die Schale aus</h2>
  <p>Schnitt durch das Paulinum (Laserscan, 1:1500). Links wie heute, rechts als Hohlkörper. Die Kassette V2 mit LED steht schematisch im Schacht; die Lage im echten Grundriss ist noch nicht gewählt. Platte und Fuß sind die des Steckmechanismus.</p>
  <div class="pair">
    <figure><div class="fig"><span class="tag">massiv, wie bisher</span>{section_svg('01_paulinum', False)}</div></figure>
    <figure><div class="fig"><span class="tag">Hohlkörper, Wand und Dach 0,8</span>{section_svg('01_paulinum', True)}</div></figure>
  </div>
  <figure><figcaption style="margin-top:10px">Die Schale folgt außen dem Gebäude. Unten bleibt sie offen: Den Boden des Hohlraums bildet die Oberseite des vollen Fußes. Das Licht läuft von der LED nur noch durch 0,8 mm statt durch mehrere Millimeter Material.</figcaption></figure>
</section>

<section>
  <h2>Wo der Generator ansetzt</h2>
  <figure><div class="fig">{flow_svg()}</div>
  <figcaption>Der Hohlraum entsteht aus dem fertigen Volumenkörper, unabhängig von der Datenquelle. Das ist möglich, weil der Querschnitt aller Gebäude nach oben nur kleiner wird.</figcaption></figure>
  <h3 style="margin-top:18px">Verfahren in vier Schritten</h3>
  <ul class="plain">
    <li>Den Volumenkörper alle 0,4 mm in der Höhe schneiden.</li>
    <li>Jeden Schnitt um die Wandstärke nach innen versetzen. Was dünner als 1,6 mm ist, bleibt voll.</li>
    <li>Die Decke folgt dem Dach: Die Wand einer Lage richtet sich nach dem Querschnitt 0,8 mm weiter oben, so bleibt das Dach überall 0,8 mm dick.</li>
    <li>Die Schnitte zu ineinanderliegenden Prismen vereinigen, nach unten offen machen und vom Volumenkörper abziehen.</li>
  </ul>
  <p class="note">Die Wand ist in Millimetern fest, nicht im Maßstab: 0,8 mm sind bei 1:1500 eine Wand von 1,2 m, bei 1:1000 von 0,8 m.</p>
</section>

<section>
  <h2>Wandstärke und Licht</h2>
  <figure><div class="fig">{wall_svg()}</div>
  <figcaption>Wandstärke als Extrusionslinien der 0,4-mm-Düse. Wie viel Licht je Stärke durchkommt, ist noch nicht gemessen; die Funktionsprobe mit LED in Steckprobe 2 liefert es.</figcaption></figure>
  <p style="margin-top:14px">Mit 0,8 mm statt 1,2 mm wird auch die Passung der Kassette etwas leichter. Die Tabelle zeigt, wie viel Wand um das Kassettenrechteck im jeweils nötigen Höhenschnitt bleibt (aus der Passstudie <code>variants_fit.json</code>). Gebäude, die schon vorher passten, ändern sich nicht; neu ist nur das Institutsgebäude bei 1:1000 mit V2.</p>
  <div class="tblw"><table>
    <thead><tr><th rowspan="2">Gebäude</th><th colspan="2">1:1500</th><th colspan="2">1:1000</th></tr>
    <tr><th>V2</th><th>V2R</th><th>V2</th><th>V2R</th></tr></thead>
    <tbody>
{table_fit()}
    </tbody></table></div>
  <figure><figcaption style="margin-top:8px">Wandstärke in mm um die Kassette. „neu“: zwischen 0,8 und 1,2, passt erst mit der dünnen Wand. „passt nicht“: das Rechteck findet im nötigen Schnitt keinen Platz, meist weil das Gebäude zu niedrig oder oben zu schmal ist. Das löst die dünne Wand nicht.</figcaption></figure>
</section>

<section>
  <h2>Die Decke: wo sie über Luft liegt</h2>
  <p>Gedruckt wird von unten. Die Decke des Hohlraums liegt dort über Luft. Schräge Dächer tragen sich selbst, flache Dächer sind Brücken. Die Bilder zeigen die Gebäude von oben; die Farbe sagt, wie weit die Decke an der Stelle frei spannt (Laserscan, 1:1500, Wand und Dach 0,8).</p>
  <div class="fig"><div class="heat">{''.join(heat)}</div>
  <div class="legend"><span><i style="background:var(--fp)"></i>getragen, unter 1 mm</span><span><i style="background:var(--s1)"></i>ab 1 mm</span><span><i style="background:var(--s2)"></i>ab 5 mm</span><span><i style="background:var(--s3)"></i>ab 10 mm</span><span><i style="background:var(--s4)"></i>ab 20 mm</span></div></div>
  <div class="tblw" style="margin-top:14px"><table>
    <thead><tr><th>Gebäude</th><th>Höhe mm</th><th>Volumen massiv cm³</th><th>Schale</th><th>größte Brücke mm</th><th>Decke ab 10 mm</th><th>getrennte Räume auf 12 mm</th><th>Brücke bei OSM mm</th></tr></thead>
    <tbody>
{table_numbers()}
    </tbody></table></div>
  <figure><figcaption style="margin-top:8px">Spalten 2 bis 7 Laserscan 1:1500, letzte Spalte OSM 1:1500. „Getrennte Räume“: Der Hohlraum teilt sich oben in Nischen, bleibt unten aber zusammenhängend. OSM hat nur Flachdächer, deshalb sind dort die Brücken größer (Hörsaalgebäude 41 mm). Das ist ein Grund, die Hohlkörper aus dem Laserscan zu bauen.</figcaption></figure>

  <h3 style="margin-top:20px">Drei Wege für das Hörsaalgebäude</h3>
  <figure><div class="fig">{roof_options_svg()}</div>
  <figcaption>Schnitt durch einen Flügel mit 18 mm Hohlraumbreite. A lässt die Decke wie sie ist. B schließt den Hohlraum oben mit 45° auf 10 mm, kostet etwa 4 mm Hohlraumhöhe. C teilt die Spannweite mit einer 0,8-mm-Wand, die das Licht abschattet.</figcaption></figure>
  <p class="note">Verworfen: Stützmaterial im Hohlraum (nicht entfernbar), Dach als getrenntes Teil (Fuge, Lichtspalt, noch ein Teil zum Kleben).</p>
</section>

<section>
  <h2>Entscheidungen</h2>
  <div class="cards">{''.join(cards)}</div>
</section>

<section>
  <h2>Vorgehen</h2>
  <p>Prototypen erst, wenn die Entscheidungen 1 und 2 gefallen sind. Die beiden Proben sind klein und passen in den Druck von Steckprobe 2.</p>
  <div class="card"><ol class="steps">{steps_html}</ol></div>
</section>

<section>
  <h2>Grundlage</h2>
  <ul class="plain">
    <li>Studie: <code>python3 -m plug.hollow.study</code> (Laserscan und OSM, 1:1500, etwa 5 s), Ergebnis <code>plug/hollow/study.json</code>, Verfahren in <code>plug/hollow/shell.py</code>.</li>
    <li>Fuß und Platte: <code>plug/logbook/current.md</code>; Kassetten und Passstudie: <code>plug/logbook/cassettes.md</code>.</li>
    <li>Nicht geprüft: Slicer-Verhalten bei 0,8-mm-Wänden, Lichtdurchgang, Durchhang der Decken im Druck.</li>
  </ul>
</section>
</main>
"""
    return html


if __name__ == "__main__":
    open(OUT, "w", encoding="utf-8").write(page())
    print("->", os.path.relpath(OUT, ROOT), "%d KB" % (os.path.getsize(OUT) // 1024))
