"""Zeichnungen der Planseite 3 (Körper E4): Schnitt und Draufsicht direkt aus den Volumenkörpern von `body4.py` (SVG als Text)."""
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

from plug.display import body4
from plug.display import params as D
from plug.geom import to_tm

de = lambda x, n=1: ("%.*f" % (n, x)).replace(".", ",")
CLASS = dict(plate="plate", body="foot", lid="lid", blende="blende", cassette="kass", pcb="pcb", glass="glass", aa="aa3", header="hdr", pins="pin3",
             leiste="hdr")
ORDER = ["plate", "leiste", "body", "cassette", "lid", "blende", "glass", "pcb", "aa", "header", "pins"]


def slice_polys(man, origin, normal, axes):
    """Schnitt durch einen Körper als shapely-Fläche in den Koordinaten `axes` (Indizes der 3D-Achsen), gerade-ungerade gefüllt."""
    tm = to_tm(man)
    sec = tm.section(plane_origin=origin, plane_normal=normal)
    if sec is None:
        return None
    res = Polygon()
    for loop in sec.discrete:
        pts = [(float(p[axes[0]]), float(p[axes[1]])) for p in loop]
        if len(pts) >= 3:
            res = res.symmetric_difference(Polygon(pts).buffer(0))
    return res


def path_d(poly, X, Y):
    polys = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
    out = []
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            pts = list(ring.coords)
            out.append("M" + " L".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in pts) + "Z")
    return " ".join(out)


class View:
    def __init__(self, x0, x1, y0, y1, s, pad=14):
        self.x0, self.y1, self.s, self.pad = x0, y1, s, pad
        self.w, self.h = (x1 - x0) * s + 2 * pad, (y1 - y0) * s + 2 * pad
        self.o = []

    def X(self, x):
        return self.pad + (x - self.x0) * self.s

    def Y(self, y):
        return self.pad + (self.y1 - y) * self.s

    def fill(self, poly, cls):
        if poly is not None and not poly.is_empty:
            self.o.append('<path d="%s" class="%s" fill-rule="evenodd"/>' % (path_d(poly, self.X, self.Y), cls))

    def line(self, pts, cls):
        self.o.append('<polyline points="%s" class="%s"/>' % (" ".join("%.1f,%.1f" % (self.X(x), self.Y(y)) for x, y in pts), cls))

    def text(self, x, y, s, cls="", anchor="start", dx=0, dy=4):
        self.o.append('<text x="%.1f" y="%.1f" class="%s" text-anchor="%s">%s</text>' % (self.X(x) + dx, self.Y(y) + dy, cls, anchor, s))

    def dim_v(self, x, y0, y1, label, side=1):
        self.line([(x, y0), (x, y1)], "dim")
        for y in (y0, y1):
            self.line([(x - 0.8, y), (x + 0.8, y)], "dim")
        self.text(x + 1.2 * side, (y0 + y1) / 2, label, "num", "start" if side > 0 else "end")

    def dim_h(self, x0, x1, y, label):
        self.line([(x0, y), (x1, y)], "dim")
        for x in (x0, x1):
            self.line([(x, y - 0.8), (x, y + 0.8)], "dim")
        self.text((x0 + x1) / 2, y - 2.0, label, "num", "middle", dy=-2)

    def svg(self, ident, label):
        return '<svg id="%s" viewBox="0 0 %.0f %.0f" role="img" aria-label="%s" class="fig sec" style="max-width:%.0fpx">%s</svg>' % (
            ident, self.w, self.h, label, self.w, "".join(self.o))


def section(P, aux, d):
    """Längsschnitt durch die Mitte (y = 0): Osten rechts, z nach oben."""
    v = View(-58.0, 12.0, -18.0, 40.0, 7.5)
    for name in ORDER:
        poly = slice_polys(P[name], [0, 0, 0], [0, 1, 0], (0, 2))
        v.fill(poly, CLASS[name])
    w = aux["wire"]
    v.line([(x, z) for x, z in _smooth(w)], "wire")
    v.line([(-62.0, 0.0), (6.0, 0.0)], "tablel")
    v.text(-57.0, 1.4, "Plattenoberfläche", "mut")
    v.dim_v(8.0, d["z_hb"], d["z_top"], "", 1)
    v.text(8.8, d["z_top"] / 2 + 3, "Höhe", "num")
    v.text(8.8, d["z_top"] / 2 - 1, de(d["z_top"]), "num")
    v.dim_v(-26.5, d["z_cass"], d["z_rear"] - 1.2, "", -1)
    v.text(-27.5, (d["z_cass"] + d["z_rear"] - 1.2) / 2, "Luft %s" % de(D.AIR), "ok", "end")
    v.text(-d["x_bw"] * 0 - 26.0, -8.0, "Hals mit Kassette", "lab", "end")
    v.text(-17.0, 24.5, "Rückdeckel", "lab", "end")
    v.text(2.0, d["z_top"] + 2.5, "Frontblende", "lab", "middle")
    v.dim_h(-d["depth"], 0.0, -16.6, "Tiefe %s" % de(d["depth"]))
    return v.svg("sec3", "Längsschnitt durch den Körper E4")


def _smooth(pts, n=10):
    """Catmull-Rom-Glättung eines Punktzugs (x, z)."""
    P = np.array(pts, float)
    P = np.vstack([P[0], P, P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return [tuple(p) for p in out]


def plan(P, aux, d):
    """Draufsicht: Umriss in 5 mm Höhe (Kopf, Keil, Hals) und in 20 mm Höhe, dazu Mulde, Kammer, Rückdeckel."""
    v = View(-32.0, 8.0, -24.0, 24.0, 9.0)
    lo = slice_polys(P["body"], [0, 0, 5.0], [0, 0, 1], (0, 1))
    hi = slice_polys(P["body"], [0, 0, 20.0], [0, 0, 1], (0, 1))
    foot = slice_polys(P["body"], [0, 0, -7.0], [0, 0, 1], (0, 1))
    v.fill(foot, "foot2")
    v.fill(lo, "foot")
    v.fill(hi, "foot3")
    cas = slice_polys(P["cassette"], [0, 0, -5.0], [0, 0, 1], (0, 1))
    v.fill(cas, "kass")
    lid = slice_polys(P["lid"], [0, 0, 20.0], [0, 0, 1], (0, 1))
    v.fill(lid, "lid")
    v.fill(slice_polys(P["blende"], [0, 0, 20.0], [0, 0, 1], (0, 1)), "blende")
    v.fill(slice_polys(P["pcb"], [0, 0, 20.0], [0, 0, 1], (0, 1)), "pcb")
    v.dim_h(-d["depth"], 0.0, -22.0, "Tiefe %s" % de(d["depth"]))
    v.dim_v(1.6, -d["W"] / 2, d["W"] / 2, "", 1)
    v.text(2.4, 0, "Kopf %s" % de(d["W"]), "num")
    v.dim_v(-d["depth"] - 1.6, -d["NW"] / 2, d["NW"] / 2, "", -1)
    v.text(-d["depth"] - 2.4, 0, "Hals %s" % de(d["NW"]), "num", "end")
    v.text(-20.0, 0, "Kassette", "lab onfill", "middle")
    v.text(-9.0, 20.0, "Kopf", "mut", "middle")
    return v.svg("plan3", "Draufsicht auf den Körper E4")


def foot_plan(P, aux, d):
    """Fuß und Mulde von unten gesehen wie im Slicer nicht, sondern von oben (Norden oben, Osten rechts): Umriss auf halber Höhe, Fase unten, Mulde, Schacht."""
    from plug.display import body4 as B4
    v = View(-31.0, 9.0, -13.0, 13.0, 14.0)
    mu = Polygon(B4.foot_poly(d)).buffer(D.CLR_MULDE, join_style=2)
    v.fill(mu, "mulde4")
    mid = slice_polys(P["body"], [0, 0, -7.0], [0, 0, 1], (0, 1))
    v.fill(mid, "foot")
    low = slice_polys(P["body"], [0, 0, d["foot"] + 0.15], [0, 0, 1], (0, 1))
    v.fill(low, "foot2")
    v.fill(slice_polys(P["cassette"], [0, 0, -7.0], [0, 0, 1], (0, 1)), "kass")
    x0, x1 = d["x_bw"], d["x_fe"]
    n = d["NW"] / 2
    v.dim_h(x0, x1, -n - 2.4, "Fuß %s" % de(x1 - x0))
    v.dim_v(x0 - 1.4, -n, n, "", -1)
    v.text(x0 - 2.2, 0, "%s" % de(d["NW"]), "num", "end")
    v.dim_h(d["x_be"], x1, n + 2.4, "Verlängerung %s" % de(D.FOOT_EXT))
    v.text(x1 - D.KEY / 2 - 0.6, -n + D.KEY / 2 - 0.2, "Ecke %s" % de(D.KEY), "lab", "start", dx=6)
    v.text(x1 + 0.8, 0, "vorn", "mut")
    v.text(-d["pe"], 0.0, "Kassette", "lab onfill", "middle")
    return v.svg("foot4", "Fuß, Mulde und Kodierecke von oben")


def peg_section(P, aux, d):
    """Schnitt durch einen Zapfen der Frontblende (y = Lochlage) mit Modul und Rückwand."""
    y = D.DISP["hole_dx"] / 2
    v = View(-12.0, 3.0, -1.0, 40.0, 11.0)
    for name in ("body", "pcb", "glass", "blende"):
        v.fill(slice_polys(P[name], [0, y, 0], [0, 1, 0], (0, 2)), CLASS[name])
    v.dim_h(d["x_blende"], d["x_slot0"] - D.PEG_HOLE_T, 38.0, "Zapfen %s" % de(d["x_blende"] - d["x_slot0"] + D.PEG_HOLE_T))
    return v.svg("peg4", "Schnitt durch einen Zapfen der Frontblende")


def bump_cross():
    """Querschnitt des Rückdeckels (y, v): Rastnasen in Nuten der Öffnung (Prinzip)."""
    v = View(-12.0, 12.0, -1.5, 4.5, 20.0)
    w, t = D.LID_W / 2, D.WALL
    v.fill(Polygon([(-w - D.SPILL - 6, -1.2), (-w - D.SPILL, -1.2), (-w - D.SPILL, 3.4), (-w - D.SPILL - 6, 3.4)]), "foot")
    v.fill(Polygon([(w + D.SPILL + 6, -1.2), (w + D.SPILL, -1.2), (w + D.SPILL, 3.4), (w + D.SPILL + 6, 3.4)]), "foot")
    v0 = (t - D.BUMP["t"]) / 2
    for sgn in (-1, 1):
        gx = sgn * (w + D.SPILL)
        v.fill(Polygon([(gx, v0 - 0.15), (gx + sgn * D.BUMP["groove"], v0 - 0.15), (gx + sgn * D.BUMP["groove"], v0 + D.BUMP["t"] + 0.15), (gx, v0 + D.BUMP["t"] + 0.15)]), "void2")
    v.fill(Polygon([(-w, 0), (w, 0), (w, t), (-w, t)]), "lid")
    for sgn in (-1, 1):
        v.fill(Polygon([(sgn * w, v0), (sgn * (w + D.BUMP["h"]), v0), (sgn * (w + D.BUMP["h"]), v0 + D.BUMP["t"]), (sgn * w, v0 + D.BUMP["t"])]), "lid")
    v.text(0, 0.6, "Rückdeckel %s dick" % de(t), "lab", "middle", dy=4)
    v.text(w + 3.5, 1.4, "Nut", "mut", "middle")
    v.text(w + 1.0, 3.9, "Nase %s" % de(D.BUMP["h"]), "mut", "start")
    return v.svg("bump4", "Rastnasen am Rückdeckel im Querschnitt")
