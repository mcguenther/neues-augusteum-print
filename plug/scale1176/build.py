#!/usr/bin/env python3
"""Seite plug/scale1176/page.html: Passprüfung des Steckmechanismus bei Maßstab 1:1250 (Platte höchstens 230 × 230 mm),
Kassette versenkt oder über der Oberfläche, Innenhof als Einsteckteil.

Liest data.json (python3 -m plug.scale1176.assemble). Aufruf: python3 -m plug.scale1176.build
(Der Ordnername scale1176 stammt von der ersten Fassung bei 1:1176.)
"""
import json
import os

from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(__file__)
D = json.load(open(os.path.join(HERE, "data.json")))
KW, KL, TAIL = D["KW"], D["KL"], D["tail"]
NAMES = {"01_paulinum": "Paulinum", "02_neues_augusteum": "Neues Augusteum", "03_hoersaalgebaeude": "Hörsaalgebäude",
         "04_seminargebaeude": "Seminargebäude", "05_institutsgebaeude": "Institutsgebäude", "06_city_hochhaus": "City-Hochhaus"}


def poly(rings):
    return unary_union([Polygon(r) for r in rings])


HOF = poly(D["hof"])
B = {k: dict(v, fpoly=poly(v["fp"])) for k, v in D["buildings"].items()}


def rect(cx, cy, w, l, a):
    return affinity.translate(affinity.rotate(box(-w / 2, -l / 2, w / 2, l / 2), a, origin=(0, 0)), cx, cy)


def shapes(p):
    shaft = rect(p["cx"], p["cy"], KW, p["kl"], p["angle"])
    foot = rect(p["cx"], p["cy"], KW + 2 * p["wall"], p["kl"] + 2 * p["wall"], p["angle"])
    sol = affinity.translate(affinity.rotate(box(-KW / 2 - p["wall"], -p["kl"] / 2 - p["wall"] - TAIL, KW / 2 + p["wall"],
                                                 -p["kl"] / 2 - p["wall"]), p["angle"], origin=(0, 0)), p["cx"], p["cy"])
    return shaft, foot, sol


def pts(p, minx, maxy, pad):
    return " ".join("%.2f,%.2f" % (x - minx + pad, maxy - y + pad) for x, y in p.exterior.coords)


def svg_building(slug, variant):
    v, p = B[slug], B[slug][variant]
    shaft, foot, sol = shapes(p)
    g = unary_union([v["fpoly"], sol])
    minx, miny, maxx, maxy = g.bounds
    pad = 4
    w, h = maxx - minx + 2 * pad, maxy - miny + 2 * pad
    out = ['<svg viewBox="0 0 %.1f %.1f" role="img" aria-label="Grundriss %s mit Schacht">' % (w, h, NAMES[slug])]
    for q in (v["fpoly"].geoms if hasattr(v["fpoly"], "geoms") else [v["fpoly"]]):
        out.append('<polygon class="fp" points="%s"/>' % pts(q, minx, maxy, pad))
    for cls, s in (("sol", sol), ("foot", foot), ("shaft", shaft)):
        out.append('<polygon class="%s" points="%s"/>' % (cls, pts(s, minx, maxy, pad)))
    out.append('<line class="sc" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (pad, h - 1.6, pad + 10, h - 1.6))
    out.append('<text class="sct" x="%.1f" y="%.1f">10 mm</text>' % (pad + 11.5, h - 0.9))
    out.append("</svg>")
    return "".join(out)


def svg_overview():
    sh = {k: shapes(v["standard"]) for k, v in B.items()}
    allg = unary_union([v["fpoly"] for v in B.values()] + [HOF] + [s[2] for s in sh.values()])
    minx, miny, maxx, maxy = allg.bounds
    pad = 5
    w, h = maxx - minx + 2 * pad, maxy - miny + 2 * pad
    out = ['<svg viewBox="0 0 %.1f %.1f" role="img" aria-label="Gesamtplan 1:1250 mit Innenhof und Schächten">' % (w, h)]
    for v in B.values():
        for q in (v["fpoly"].geoms if hasattr(v["fpoly"], "geoms") else [v["fpoly"]]):
            out.append('<polygon class="fp" points="%s"/>' % pts(q, minx, maxy, pad))
    for q in (HOF.geoms if hasattr(HOF, "geoms") else [HOF]):
        out.append('<polygon class="hof" points="%s"/>' % pts(q, minx, maxy, pad))
    for shaft, foot, sol in sh.values():
        for cls, s in (("sol", sol), ("foot", foot), ("shaft", shaft)):
            out.append('<polygon class="%s" points="%s"/>' % (cls, pts(s, minx, maxy, pad)))
    for slug, v in B.items():
        c = v["fpoly"].centroid
        out.append('<text class="lbl" x="%.1f" y="%.1f">%s</text>' % (c.x - minx + pad + 7, maxy - c.y + pad - 1, NAMES[slug]))
    c = HOF.centroid
    out.append('<text class="lbl hofl" x="%.1f" y="%.1f">Innenhof</text>' % (c.x - minx + pad - 8, maxy - c.y + pad))
    out.append('<line class="sc" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (pad, h - 2.5, pad + 20, h - 2.5))
    out.append('<text class="sct" x="%.1f" y="%.1f">20 mm</text>' % (pad + 22, h - 1.6))
    out.append("</svg>")
    return "".join(out)


def com(x, n=1):
    return (("%." + str(n) + "f") % x).replace(".", ",")


def verdict(wall):
    if wall is None or wall < 0.8:
        return ("no", "passt nicht")
    if wall < 1.2:
        return ("warn", "knapp")
    return ("ok", "passt")


def cell(wall):
    return "–" if wall is None else ("≥ 6,0" if wall >= 6 else com(wall))


rows = []
for slug, v in B.items():
    f = v["fit"]
    c1, t1 = verdict(f["dmax_mit"])
    c2, t2 = verdict(f["dmax_ohne"])
    rows.append(
        "<tr><th scope=row>%s</th><td class=num>%s</td><td class=num>%s</td>"
        "<td class=num>%s</td><td><span class='pill %s'>%s</span></td><td class=num>%s</td>"
        "<td class=num>%s</td><td><span class='pill %s'>%s</span></td><td class=num>1:%d%s</td></tr>" % (
            NAMES[slug], com(v["area"], 0), com(v["hmax"], 0), cell(f["dmax_mit"]), c1, t1,
            com(min(v["standard"]["kl"], KL) if v["standard"]["wall"] < 1.0 else KL), cell(f["dmax_ohne"]), c2, t2,
            round(1000 / f["kmin"], -1), "+" if f["kmin"] <= 0.51 else ""))
TABLE = "\n".join(rows)
GRID = "\n".join("<figure><div class=plan>%s</div><figcaption><b>%s</b><span>Schacht %s × %s mm, Wand %s mm%s</span></figcaption></figure>" % (
    svg_building(s, "standard"), NAMES[s], com(KW), com(v["standard"]["kl"]), com(v["standard"]["wall"]),
    ", gekürzt" if v["standard"]["kl"] < KL - 0.1 else "") for s, v in B.items())
GRID_V = "\n".join("<figure><div class=plan>%s</div><figcaption><b>%s, versenkt</b><span>Schacht %s × %s mm, Wand %s mm%s</span></figcaption></figure>" % (
    svg_building(s, "versenkt"), NAMES[s], com(KW), com(v["versenkt"]["kl"]), com(v["versenkt"]["wall"]),
    ", gekürzt" if v["versenkt"]["kl"] < KL - 0.1 else "") for s, v in B.items() if "versenkt" in v)
hb = HOF.bounds
VDATA = json.load(open(os.path.join(HERE, "variants1250.json")))
html = open(os.path.join(HERE, "page.template.html")).read()
for k, val in {"@VDATA@": json.dumps(VDATA), "@TABLE@": TABLE, "@GRID@": GRID, "@GRIDV@": GRID_V, "@OVERVIEW@": svg_overview(), "@KW@": com(KW), "@KL@": com(KL),
               "@HOFW@": com(hb[2] - hb[0]), "@HOFL@": com(hb[3] - hb[1]), "@HOFA@": com(D["hof_area"], 0),
               "@F@": com(D["F"]), "@FV@": com(D["F"] + D["kass_top"] + 0.4), "@PT@": com(D["plate_t"]),
               "@PTV@": com(D["plate_t"] + D["kass_top"] + 0.4)}.items():
    html = html.replace(k, val)
open(os.path.join(HERE, "page.html"), "w").write(html)
print("page.html geschrieben")
