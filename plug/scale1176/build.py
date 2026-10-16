#!/usr/bin/env python3
"""Seite plug/scale1176/page.html: Passprüfung des Steckmechanismus bei Maßstab 1:1176 und Entscheidung zum Innenhof.

Liest data.json (python3 -m plug.scale1176.assemble). Aufruf: python3 -m plug.scale1176.build
"""
import json
import os

from shapely import affinity
from shapely.geometry import MultiPolygon, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(__file__)
D = json.load(open(os.path.join(HERE, "data.json")))
K, KW, KL, TAIL = D["K"], D["KW"], D["KL"], D["tail"]
NAMES = {"01_paulinum": "Paulinum", "02_neues_augusteum": "Neues Augusteum", "03_hoersaalgebaeude": "Hörsaalgebäude",
         "04_seminargebaeude": "Seminargebäude", "05_institutsgebaeude": "Institutsgebäude", "06_city_hochhaus": "City-Hochhaus"}


def poly(rings):
    return unary_union([Polygon(r) for r in rings])


HOF = poly(D["hof"])


def rect(cx, cy, w, l, a):
    return affinity.translate(affinity.rotate(box(-w / 2, -l / 2, w / 2, l / 2), a, origin=(0, 0)), cx, cy)


def shapes(b):
    """Schacht, Fußwand und Lötraum eines Gebäudes; Lötraum liegt am Pin-Ende (y−), Spiegelung so gewählt, dass er möglichst frei bleibt."""
    kl, wall = b["kl"], b["wall"]
    shaft = rect(b["cx"], b["cy"], KW, kl, b["angle"])
    foot = rect(b["cx"], b["cy"], KW + 2 * wall, kl + 2 * wall, b["angle"])
    best = None
    for flip in (0, 180):
        sol = affinity.rotate(box(-KW / 2 - wall, -kl / 2 - wall - TAIL, KW / 2 + wall, -kl / 2 - wall), b["angle"] + flip, origin=(0, 0))
        sol = affinity.translate(sol, b["cx"], b["cy"])
        best = best or (sol, flip)
    return shaft, foot, best[0]


B = {k: dict(v, fpoly=poly(v["fp"])) for k, v in D["buildings"].items()}
for k, v in B.items():
    v["shaft"], v["foot"], v["sol"] = shapes(v)
    # beide Spiegelungen prüfen und die mit weniger Überlappung (Hof, andere Gebäude) nehmen
    alt = affinity.rotate(v["sol"], 180, origin=v["foot"].centroid)
    others = unary_union([o["fpoly"] for kk, o in B.items() if kk != k] + [HOF]) if len(B) > 1 else HOF
    if alt.intersection(others).area < v["sol"].intersection(others).area:
        v["sol"] = alt


def fmt(x, n=1):
    return ("%." + str(n) + "f") % x


def svg_building(slug):
    v = B[slug]
    g = unary_union([v["fpoly"], v["sol"], HOF]) if False else unary_union([v["fpoly"], v["sol"]])
    minx, miny, maxx, maxy = g.bounds
    pad = 4
    w, h = maxx - minx + 2 * pad, maxy - miny + 2 * pad

    def pts(p):
        return " ".join("%.2f,%.2f" % (x - minx + pad, maxy - y + pad) for x, y in p.exterior.coords)

    out = ['<svg viewBox="0 0 %.1f %.1f" role="img" aria-label="Grundriss %s mit Schacht">' % (w, h, NAMES[slug])]
    for p in (v["fpoly"].geoms if hasattr(v["fpoly"], "geoms") else [v["fpoly"]]):
        out.append('<polygon class="fp" points="%s"/>' % pts(p))
    out.append('<polygon class="sol" points="%s"/>' % pts(v["sol"]))
    out.append('<polygon class="foot" points="%s"/>' % pts(v["foot"]))
    out.append('<polygon class="shaft" points="%s"/>' % pts(v["shaft"]))
    out.append('<line class="sc" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (pad, h - 1.6, pad + 10, h - 1.6))
    out.append('<text class="sct" x="%.1f" y="%.1f">10 mm</text>' % (pad + 11.5, h - 0.9))
    out.append("</svg>")
    return "".join(out)


def svg_overview():
    allg = unary_union([v["fpoly"] for v in B.values()] + [HOF] + [v["sol"] for v in B.values()])
    minx, miny, maxx, maxy = allg.bounds
    pad = 5
    w, h = maxx - minx + 2 * pad, maxy - miny + 2 * pad

    def pts(p):
        return " ".join("%.2f,%.2f" % (x - minx + pad, maxy - y + pad) for x, y in p.exterior.coords)

    out = ['<svg viewBox="0 0 %.1f %.1f" role="img" aria-label="Gesamtplan 1:1176 mit Innenhof und Schächten">' % (w, h)]
    for v in B.values():
        for p in (v["fpoly"].geoms if hasattr(v["fpoly"], "geoms") else [v["fpoly"]]):
            out.append('<polygon class="fp" points="%s"/>' % pts(p))
    for p in (HOF.geoms if hasattr(HOF, "geoms") else [HOF]):
        out.append('<polygon class="hof" points="%s"/>' % pts(p))
    for v in B.values():
        out.append('<polygon class="sol" points="%s"/>' % pts(v["sol"]))
        out.append('<polygon class="foot" points="%s"/>' % pts(v["foot"]))
        out.append('<polygon class="shaft" points="%s"/>' % pts(v["shaft"]))
    for slug, v in B.items():
        c = v["fpoly"].centroid
        out.append('<text class="lbl" x="%.1f" y="%.1f">%s</text>' % (c.x - minx + pad + 7, maxy - c.y + pad - 1, NAMES[slug]))
    c = HOF.centroid
    out.append('<text class="lbl hofl" x="%.1f" y="%.1f">Innenhof</text>' % (c.x - minx + pad - 8, maxy - c.y + pad))
    out.append('<line class="sc" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (pad, h - 2.5, pad + 20, h - 2.5))
    out.append('<text class="sct" x="%.1f" y="%.1f">20 mm</text>' % (pad + 22, h - 1.6))
    out.append("</svg>")
    return "".join(out)


def verdict(wall):
    if wall is None or wall < 0.8:
        return ("no", "passt nicht")
    if wall < 1.2:
        return ("warn", "knapp")
    return ("ok", "passt")


rows = []
for slug, v in B.items():
    f = v["fit"]
    dm = f["1176"]["dmax"]
    cls, txt = verdict(dm)
    kmin = f["kmin"]
    rows.append("<tr><th scope=row>%s</th><td class=num>%s</td><td class=num>%s</td><td class=num>%s</td><td class=num>%s</td>"
                "<td class=num>%s</td><td class=num>%s</td><td><span class='pill %s'>%s</span></td></tr>" % (
                    NAMES[slug], fmt(v["area"], 0), fmt(v["hmax"], 0),
                    "≥ 6,0" if f["1000"]["dmax"] >= 6 else fmt(f["1000"]["dmax"] or 0).replace(".", ","),
                    "≥ 6,0" if dm >= 6 else fmt(dm or 0).replace(".", ","),
                    "–" if not f["1500"]["dmax"] else fmt(f["1500"]["dmax"]).replace(".", ","),
                    ("1:%d%s" % (round(1000 / kmin, -1), "+" if kmin <= 0.51 else "")), cls, txt))
TABLE = "\n".join(rows)
GRID = "\n".join("<figure><div class=plan>%s</div><figcaption><b>%s</b><span>Schacht %s × %s mm, Wand %s mm%s</span></figcaption></figure>" % (
    svg_building(s), NAMES[s], fmt(KW), fmt(v["kl"]), fmt(v["wall"]).replace(".", ","),
    ", gekürzt" if v["kl"] < KL - 0.1 else "") for s, v in B.items())
HOFB = HOF.bounds
html = open(os.path.join(HERE, "page.template.html")).read()
for k, val in {"@TABLE@": TABLE, "@GRID@": GRID, "@OVERVIEW@": svg_overview(), "@KW@": fmt(KW).replace(".", ","),
               "@KL@": fmt(KL).replace(".", ","), "@HOFW@": fmt(HOFB[2] - HOFB[0]).replace(".", ","),
               "@HOFL@": fmt(HOFB[3] - HOFB[1]).replace(".", ","), "@HOFA@": fmt(D["hof_area"], 0),
               "@UNIKL@": fmt(B["06_city_hochhaus"]["kl"]).replace(".", ",")}.items():
    html = html.replace(k, val)
open(os.path.join(HERE, "page.html"), "w").write(html)
print("page.html geschrieben")
