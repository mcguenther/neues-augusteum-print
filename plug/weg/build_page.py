#!/usr/bin/env python3
"""Planseite Südweg: plug/weg/plan.html (Vorlage page.template.html).

Der Weg (Gang) zwischen Seminar- und Hörsaalgebäude wird von einem Steg am Hörsaalgebäude verengt. Der Steg steht nur im LoD2-Grundriss (und damit im
Laserscan), nicht in OSM; im Luftbild ist es ein Verbindungsgang in der Höhe. Die Seite zeigt den Befund (Übersicht, Luftbild, Grundriss, 3D der
Steckplatte) und den Vorschlag: den Steg aus dem Grundriss des Hörsaalgebäudes schneiden. Der Schnitt ist hier nur simuliert (Wrapper um
G.source_models, Fenster und Öffnungsbreite siehe STEG_FENSTER, STEG_OEFFNUNG); die Quellen und die Steckplatte in stl/ bleiben unverändert.

Aufruf (aus dem Wurzelverzeichnis, ca. 30 s):
    python3 -m plug.weg.build_page
"""
import base64
import html
import io
import math
import os
import re

import numpy as np
import manifold3d as m3d
import trimesh
from PIL import Image
from shapely.geometry import LineString, box
from shapely.ops import unary_union

import farben
import generate as G
import innenhof
import lod2
import preview
from plug import campus as C
from plug.geom import to_tm
from plug.hof.build_page import NAMEN, Plan, de, gebaeude, hoehenplan
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "03_hoersaalgebaeude"
STEG_FENSTER = (-114.0, -21.5, -106.0, -13.0)   # mm: Fenster um den Steg (x0, y0, x1, y1)
STEG_OEFFNUNG = 1.5                             # mm: Auswüchse im Fenster schmaler als 2 × 1,5 mm werden abgeschnitten
ZOOM = (-126.0, -84.0, -36.0, 8.0)              # mm: Ausschnitt der Grundrisse (x0, x1, y0, y1)
STEG_MITTE = (-110.2, -16.6)                    # mm: Mitte des Stegs (für Beschriftungen)
AERIAL_HALF = 28.0                              # m: halbe Kantenlänge des Luftbild-Ausschnitts


def steg_von(fp):
    """Steg = Auswuchs des Hörsaal-Grundrisses im Fenster, der schmaler ist als 2 × STEG_OEFFNUNG (Öffnen mit Mitre-Ecken)."""
    opened = fp.buffer(-STEG_OEFFNUNG, join_style=2).buffer(STEG_OEFFNUNG, join_style=2)
    return fp.difference(opened).intersection(box(*STEG_FENSTER))


def platte(mit_steg):
    """Steckplatte (Manifold) und Modelle. Seit dem Fix schneidet lod2.models den Steg selbst (lod2.OHNE_STEG); für den Stand mit Steg wird das
    hier abgeschaltet. Die Platzierungen sind zwischengespeichert."""
    orig = lod2.OHNE_STEG
    if mit_steg:
        lod2.OHNE_STEG = {}
    try:
        pl, report, models, places, outline, hof_solid = C.build(P.SCALE_PLAN, False)
    finally:
        lod2.OHNE_STEG = orig
    return pl, report, models, outline


def render3d(plate, azim, elev, marker):
    """Ausschnitt der Platte (Manifold) um den Weg, als PNG (base64) plus Pixelposition der Marke (Weltpunkt)."""
    c = plate ^ m3d.Manifold.cube((44, 36, 30)).translate((-128.5, -38, -5))
    tm = to_tm(c)
    im, proj = preview.render([(tm, "#8a96a5")], size=(760, 600), azim=azim, elev=elev, return_proj=True)
    px, py = proj(np.array(marker))
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode(), im.size, (float(px), float(py))


def fig3d(b64, size, mk, label, cls):
    w, h = size
    ring = ""
    if mk:
        ring = ('<circle class="ring %s" cx="%.0f" cy="%.0f" r="30"/>' % (cls, mk[0], mk[1]))
    return ('<svg class="plan" viewBox="0 0 %d %d" role="img" aria-label="%s"><image href="data:image/png;base64,%s" width="%d" height="%d"/>%s</svg>'
            % (w, h, html.escape(label), b64, w, h, ring))


def breite(fps, x0=-116.5, x1=-100.0):
    """Breite des Wegs auf der Platte (Abstand der Mulden, ohne Fuge der Gebäude) senkrecht zur Kante, je x: [(x, mm)]."""
    sem = fps["04_seminargebaeude"].buffer(P.OUTLINE_CLR_T, join_style=2)
    hor = fps[SLUG].buffer(P.OUTLINE_CLR_T, join_style=2)
    out = []
    for x in np.arange(x0, x1 + 1e-9, 0.25):
        ln = LineString([(x, -40), (x, 5)])
        a, b = ln.intersection(sem), ln.intersection(hor)
        if a.is_empty or b.is_empty:
            continue
        out.append((float(x), (a.bounds[1] - b.bounds[3]) * math.cos(math.radians(11.3))))
    return out


def fig_breite(vor, nach):
    W, H, l, r, t, b = 640, 250, 56, 16, 18, 40
    xs0, xs1, ym = -116.5, -100.0, 14.0
    X = lambda x: l + (x - xs0) / (xs1 - xs0) * (W - l - r)
    Y = lambda y: H - b - y / ym * (H - t - b)
    g = ['<line class="axis" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (l, H - b, W - r, H - b)]
    for v in (0, 2, 4, 6, 8, 10, 12, 14):
        g.append('<line class="grid" x1="%d" y1="%.1f" x2="%d" y2="%.1f"/><text class="tick" x="%d" y="%.1f" text-anchor="end">%d</text>' % (l, Y(v), W - r, Y(v), l - 6, Y(v) + 4, v))
    for x in range(-116, -99, 2):
        g.append('<text class="tick" x="%.1f" y="%d" text-anchor="middle">%d</text>' % (X(x), H - b + 16, x))
    g.append('<text class="tick" x="%.1f" y="%d" text-anchor="middle">Lage x auf der Platte (mm)</text>' % ((l + W - r) / 2, H - 6))
    g.append('<text class="tick" x="14" y="%.1f" transform="rotate(-90 14 %.1f)" text-anchor="middle">Weg (mm)</text>' % ((t + H - b) / 2, (t + H - b) / 2))
    for pts, cls in ((vor, "l-vor"), (nach, "l-nach")):
        g.append('<polyline class="%s" points="%s"/>' % (cls, " ".join("%.1f,%.1f" % (X(x), Y(w)) for x, w in pts)))
    mn = min(vor, key=lambda p: p[1])
    g.append('<circle class="dot-vor" cx="%.1f" cy="%.1f" r="4"/><text class="lab-vor" x="%.1f" y="%.1f">Steg: %s mm</text>' % (X(mn[0]), Y(mn[1]), X(mn[0]) + 10, Y(mn[1]) - 8, de(mn[1])))
    n1 = [p for p in nach if abs(p[0] + 113) < 0.01][0]
    g.append('<text class="lab-nach" x="%.1f" y="%.1f">ohne Steg: %s mm</text>' % (X(-115.8), Y(n1[1]) - 8, de(n1[1])))
    g.append('<text class="lab-abs" x="%.1f" y="%.1f" text-anchor="end">Absatz in der Kante des Hörsaalgebäudes</text>' % (X(-102.3), Y(10.6) - 10))
    return '<svg class="plan chart" viewBox="0 0 %d %d" role="img" aria-label="Breite des Wegs entlang der Strecke, vorher und nachher">%s</svg>' % (W, H, "".join(g))


def grundriss(fps, fp, s, data, auf, steg, mit_steg, dim, wert):
    x0, x1, y0, y1 = ZOOM
    pl = Plan(x0, x1, y0, y1, 10.0)
    hoehenplan(pl, fps, fp, s, data, auf)
    if mit_steg:
        pl.poly(steg, "steg")
    else:
        pl.items.append('<path class="steg-weg" d="%s"/>' % pl.d(steg.buffer(0.05, join_style=2)))
    xd, ys, yh = dim
    (ax, ay), (bx, by) = pl.pt(xd, ys), pl.pt(xd, yh)
    pl.items.append('<path class="dimline" d="M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f"/>'
                    % (ax, ay, bx, by, ax - 5, ay, ax + 5, ay, bx - 5, by, bx + 5, by))
    pl.text(xd + 0.9, (ys + yh) / 2 + 0.6, wert, "dimtxt")
    pl.scale_and_north(5.0)
    return pl


def gap_at(fps, x):
    ln = LineString([(x, -40), (x, 5)])
    sem = fps["04_seminargebaeude"].buffer(P.OUTLINE_CLR_T, join_style=2).intersection(ln)
    hor = fps[SLUG].buffer(P.OUTLINE_CLR_T, join_style=2).intersection(ln)
    return sem.bounds[1], hor.bounds[3]


def luftbild(fp_lod2, steg, s):
    arr, (X0, Y0, X1, Y1) = farben.load_dop()
    Hh, Ww = arr.shape[:2]
    rx, ry = (X1 - X0) / Ww, (Y1 - Y0) / Hh

    def px(xm, ym):
        X, Y = lod2.local_to_utm(np.array([xm]), np.array([ym]))
        return (X[0] - X0) / rx, (Y1 - Y[0]) / ry
    cx, cy = STEG_MITTE[0] / s, STEG_MITTE[1] / s
    a0, b0 = px(cx - AERIAL_HALF, cy + AERIAL_HALF)
    a1, b1 = px(cx + AERIAL_HALF, cy - AERIAL_HALF)
    crop = Image.fromarray(arr).crop((int(a0), int(b0), int(a1), int(b1)))
    k = 760 / crop.size[0]
    crop = crop.resize((760, int(crop.size[1] * k)), Image.LANCZOS)
    buf = io.BytesIO()
    crop.save(buf, "JPEG", quality=82)
    b64 = base64.b64encode(buf.getvalue()).decode()

    def to(x_mm, y_mm):
        a, b = px(x_mm / s, y_mm / s)
        return (a - int(a0)) * k, (b - int(b0)) * k

    def path(geom):
        d = []
        for p in G.polys_of(geom):
            d.append("M" + " L".join("%.1f %.1f" % to(x, y) for x, y in p.exterior.coords) + "Z")
        return " ".join(d)
    W, H = crop.size
    sx, sy = to(*STEG_MITTE)
    lab = lambda x, y, t, a="start": '<text class="alab" x="%.0f" y="%.0f" text-anchor="%s">%s</text>' % (x, y, a, t)
    svg = ('<svg class="plan" viewBox="0 0 %d %d" role="img" aria-label="Luftbild des Wegs mit dem Steg"><image href="data:image/jpeg;base64,%s" width="%d" height="%d"/>'
           '<path class="a-bld" d="%s"/><path class="a-steg" d="%s"/>%s%s%s'
           '<line class="a-lead" x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f"/></svg>'
           % (W, H, b64, W, H, path(fp_lod2), path(steg), lab(W * 0.52, H * 0.16, "Seminargebäude"), lab(W * 0.30, H * 0.80, "Hörsaalgebäude"),
              lab(sx + 112, sy - 50, "Steg"), sx + 30, sy - 8, sx + 104, sy - 54))
    return svg


def uebersicht(fps, fp, s, data, auf, outline, steg):
    pl = Plan(-129.0, -12.0, -123.0, 100.0, 3.0)
    pl.poly(outline, "platte")
    hoehenplan(pl, fps, fp, s, data, auf)
    x0, x1, y0, y1 = ZOOM
    (ax, ay), (bx, by) = pl.pt(x0, y1), pl.pt(x1, y0)
    pl.items.append('<rect class="win" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>' % (ax, ay, bx - ax, by - ay))
    pl.marker(*STEG_MITTE, -122.0, 24.0, "S")
    pl.scale_and_north(20.0)
    return pl.svg("Ganze Steckplatte mit Rahmen um den Ausschnitt und der Stelle des Stegs (S)")


def main():
    G.FAST = True
    s = 1000.0 / P.SCALE_PLAN
    data = innenhof.load()
    # vorher
    pl_v, rep_v, models, outline = platte(True)
    fps_v = {k: v[1] for k, v in models.items() if k in P.CASSETTE}
    abstand = C.hof_abstand(P.HOF_WALL_T)
    hof_v = innenhof.flaeche_mm(list(fps_v.values()), s, abstand)
    auf_v = innenhof.platte_aufbau_mm(hof_v, s)
    steg = steg_von(fps_v[SLUG])
    tab = steg.intersection(box(-112.2, -19.6, -108.0, -14.0))
    rect = list(tab.minimum_rotated_rectangle.exterior.coords)
    steg_w, steg_l = sorted([math.hypot(rect[1][0] - rect[0][0], rect[1][1] - rect[0][1]), math.hypot(rect[2][0] - rect[1][0], rect[2][1] - rect[1][1])])
    steg_b = tab.area / max(steg_l, 1e-9)                       # Breite senkrecht zur Längsachse (der Steg ist ein Parallelogramm)
    # nachher
    pl_n, rep_n, models_n, _ = platte(False)
    fps_n = {k: v[1] for k, v in models_n.items() if k in P.CASSETTE}
    hof_n = innenhof.flaeche_mm(list(fps_n.values()), s, abstand)
    auf_n = innenhof.platte_aufbau_mm(hof_n, s)
    hof_diff = hof_v.symmetric_difference(hof_n).area
    bad_n = max(r[4] for r in rep_n)
    prof_v, prof_n = breite(fps_v), breite(fps_n)
    neck = min(prof_v, key=lambda p: p[1])
    weg_n = [w for x, w in prof_n if -116 <= x <= -103.5]
    # Grafiken
    xd = -109.9
    ys_v, yh_v = gap_at(fps_v, xd)
    ys_n, yh_n = gap_at(fps_n, xd)
    g1 = uebersicht(fps_v, hof_v, s, data, auf_v, outline, steg)
    g_vor = grundriss(fps_v, hof_v, s, data, auf_v, steg, True, (xd, ys_v, yh_v), "%s mm" % de(neck[1])).svg("Grundriss vorher: Steg verengt den Weg")
    g_nach = grundriss(fps_n, hof_n, s, data, auf_n, steg, False, (xd, ys_n, yh_n), "%s mm" % de(min(weg_n))).svg("Grundriss nachher: Weg durchgehend gleich breit")
    g_breite = fig_breite(prof_v, prof_n)
    g_luft = luftbild(fps_v[SLUG], steg, s)
    mk = (STEG_MITTE[0], STEG_MITTE[1], C.plate_thickness(P.dims_plan()))
    b_v, sz, p_v = render3d(pl_v, -60, 50, mk)
    b_n, _, p_n = render3d(pl_n, -60, 50, mk)
    g3_v = fig3d(b_v, sz, p_v, "Steckplatte vorher, Blick von Südosten auf den Weg", "r-bad")
    g3_n = fig3d(b_n, sz, p_n, "Steckplatte nachher, Blick von Südosten auf den Weg", "r-ok")
    z = lambda v, nd=1: de(v, nd)
    ctx = {
        "FIG_UEBER": g1, "FIG_LUFT": g_luft, "FIG_VOR": g_vor, "FIG_NACH": g_nach, "FIG_BREITE": g_breite, "FIG_3D_VOR": g3_v, "FIG_3D_NACH": g3_n,
        "STEG_B": z(steg_b), "STEG_L": z(steg_l), "STEG_B_M": z(steg_b / s), "STEG_L_M": z(steg_l / s), "STEG_A": z(tab.area, 0), "STEG_A_M": z(tab.area / s ** 2, 0),
        "HALS": z(neck[1]), "HALS_X": z(neck[0]), "WEG_N": z(min(weg_n)), "WEG_N_M": z(min(weg_n) / s, 0), "HALS_M": z(neck[1] / s),
        "HOF_DIFF": z(hof_diff, 1), "KOLL": z(bad_n, 1),
    }
    tpl = open(os.path.join(HERE, "page.template.html"), encoding="utf-8").read()
    for k, v in ctx.items():
        tpl = tpl.replace("{{%s}}" % k, v)
    left = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", tpl)))
    if left:
        raise SystemExit("unbelegte Platzhalter: %s" % left)
    out = os.path.join(HERE, "plan.html")
    open(out, "w", encoding="utf-8").write(tpl)
    print("Steg %.1f × %.1f mm (%.1f × %.1f m), Fläche %.1f mm²; Hals %.2f mm bei x %.1f; Weg ohne Steg min %.2f mm; Hof-Differenz %.4f mm²; Kollision %.2f; %s (%d KB)"
          % (steg_b, steg_l, steg_b / s, steg_l / s, tab.area, neck[1], neck[0], min(weg_n), hof_diff, bad_n, os.path.relpath(out, G.HERE), os.path.getsize(out) // 1024))


if __name__ == "__main__":
    main()
