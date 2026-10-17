#!/usr/bin/env python3
"""Vergleichsseite zum Innenhof-Einsatz: plug/hof/page.html (Vorlage page.template.html).

Drei Fassungen: das Original (Spalt, Steg und Zungen; eingefroren in plug/hof/alt/), Fassung A mit Trennwand (P.HOF_WALL_T, 0,8 mm) zwischen
Hof-Aussparung und Gebäude-Mulden und Fassung B ohne Trennwand (Einsatz liegt zwischen den Gebäuden). Beide neuen Fassungen kommen aus
plug.campus.build und innenhof.py: Hof bis an die Fassaden, Treppen als Rechtecke, Abstieg nach Süden bündig zur Platte.
Die Seite zeigt Grundrisse, Schnitte durch die Trennwand und die Südtreppe, die Treppenhöhen, 3D von Mulde und Stecker und die Prüfung über alle
Quellen und Maßstäbe.

Aufruf (aus dem Wurzelverzeichnis, ca. 1 min; plug/hof/alt/ muss existieren, sonst erst `python3 -m plug.hof.freeze_alt`):
    python3 -m plug.hof.build_page
"""
import base64
import html
import json
import math
import os

import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

import generate as G
import innenhof
from plug import campus as C
from plug.geom import to_tm
from plug.hof import compare as H
from plug.testcase import params as P

HERE = os.path.dirname(os.path.abspath(__file__))
ALT = os.path.join(HERE, "alt")
NAMEN = {"01_paulinum": "Paulinum", "02_neues_augusteum": "Neues Augusteum", "03_hoersaalgebaeude": "Hörsaalgebäude",
         "04_seminargebaeude": "Seminargebäude", "05_institutsgebaeude": "Institutsgebäude", "06_city_hochhaus": "Hochhaus"}
WAND_Y = 24.0           # mm: Schnitt y = const durch die Trennwand am Neuen Augusteum (Osten des Hofs)
SUED_U = -92.0          # mm im Hofsystem: Schnitt durch die Südtreppe, Mitte des Gangs
MIN_STELLE_MM2 = 3.0    # kleinere Reste beim Öffnen sind Ecken, keine schmalen Stellen


def de(v, nd=1):
    return ("%.*f" % (nd, v)).replace(".", ",")


def pack(tm):
    """Dreiecke ohne Indizes als float32 (flache Schattierung), base64."""
    return base64.b64encode(np.asarray(tm.triangles, dtype="<f4").tobytes()).decode()


# --------------------------------------------------------------------------
# Grundrisse als SVG (Einheiten: k je mm, y nach oben = Norden)
# --------------------------------------------------------------------------
class Plan:
    def __init__(self, x0, x1, y0, y1, k=8.0):
        self.x0, self.x1, self.y0, self.y1, self.k = x0, x1, y0, y1, k
        self.w, self.h = (x1 - x0) * k, (y1 - y0) * k
        self.box = box(x0, y0, x1, y1)
        self.items = []

    def pt(self, x, y):
        return (x - self.x0) * self.k, (self.y1 - y) * self.k

    def d(self, geom):
        out = []
        for p in G.polys_of(geom.intersection(self.box)):
            for ring in [p.exterior] + list(p.interiors):
                out.append("M" + " L".join("%.1f %.1f" % self.pt(x, y) for x, y in ring.coords) + "Z")
        return " ".join(out)

    def poly(self, geom, cls, style=""):
        if geom is not None and not geom.is_empty:
            d = self.d(geom)
            if d:
                self.items.append('<path class="%s"%s d="%s"/>' % (cls, ' style="%s"' % style if style else "", d))

    def text(self, x, y, s, cls="t", anchor="start"):
        px, py = self.pt(x, y)
        self.items.append('<text class="%s" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (cls, px, py, anchor, html.escape(s)))

    def marker(self, x, y, lx, ly, letter):
        """Kreis mit Buchstabe bei (lx, ly), Linie zum Ziel (x, y)."""
        (px, py), (qx, qy) = self.pt(x, y), self.pt(lx, ly)
        self.items.append('<line class="lead" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/><circle class="dot" cx="%.1f" cy="%.1f" r="2.5"/>'
                          '<circle class="mk" cx="%.1f" cy="%.1f" r="9.5"/><text class="mkt" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
                          % (px, py, qx, qy, px, py, qx, qy, qx, qy + 4.2, letter))

    def scale_and_north(self, mm=10.0):
        x, y = self.x1 - mm - 1.5, self.y0 + 1.7
        (ax, ay), (bx, by) = self.pt(x, y), self.pt(x + mm, y)
        self.items.append('<path class="bar" d="M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f"/>'
                          % (ax, ay, bx, by, ax, ay - 4, ax, ay + 4, bx, by - 4, bx, by + 4))
        self.text(x + mm / 2, y + 2.0, "%d mm = %s m" % (mm, de(mm * P.SCALE_PLAN / 1000, 1)), "tiny", "middle")
        nx, ny = self.pt(self.x1 - 3.0, self.y1 - 2.0)
        self.items.append('<path class="north" d="M%.1f %.1f l6 18 l-6 -5 l-6 5 Z"/><text class="tiny" x="%.1f" y="%.1f" text-anchor="middle">N</text>'
                          % (nx, ny, nx, ny - 4))

    def svg(self, label, cls=""):
        return ('<svg class="plan %s" viewBox="0 0 %.0f %.0f" role="img" aria-label="%s">%s</svg>'
                % (cls, self.w, self.h, html.escape(label), "".join(self.items)))


def gebaeude(plan, fps):
    from shapely.ops import polylabel
    for slug, fp in fps.items():
        plan.poly(fp, "bld")
    for slug, fp in fps.items():
        vis = unary_union(G.polys_of(fp)).intersection(plan.box.buffer(-2.0))
        polys = G.polys_of(vis)
        if not polys:
            continue
        q = max(polys, key=lambda g: g.area)
        pt = polylabel(q, 0.1)
        name = NAMEN.get(slug, slug)
        if 2 * q.exterior.distance(pt) * plan.k < 6.2 * len(name) + 8:     # Text passt nicht in die sichtbare Fläche
            continue
        plan.text(pt.x, pt.y, name, "bname", "middle")


def schmale_stellen(fp):
    """Teile des Umrisses, in die kein Kreis mit halber Mindestbreite passt (Zungen, Stege, Zähne), ohne die Rundung gewöhnlicher Ecken."""
    r = innenhof.HOF_MIN_BREITE / 2
    return [q for q in G.polys_of(fp.difference(fp.buffer(-r).buffer(r))) if q.area >= MIN_STELLE_MM2]


def wand_flaeche(fps, fp, wand):
    """Trennwand (mm) im Grundriss: Band zwischen Gebäude-Mulde und Hof-Aussparung, nur dort, wo der Hof anliegt."""
    if wand <= 0:
        return Polygon()
    bl = unary_union(list(fps.values()))
    return (bl.buffer(P.OUTLINE_CLR_T + wand, join_style=2).difference(bl.buffer(P.OUTLINE_CLR_T, join_style=2))).intersection(fp.buffer(wand + 0.3))


def fig_vergleich(fps, fp_alt, fp_a, fp_b):
    out = []
    wa = wand_flaeche(fps, fp_a, P.HOF_WALL_T)
    for titel, fp, wand, label in (("Original", fp_alt, None, "Original"), ("A mit Trennwand %s mm" % de(P.HOF_WALL_T), fp_a, wa, "Fassung A"),
                                   ("B ohne Trennwand", fp_b, None, "Fassung B")):
        pl = Plan(-103, -53, -30, 76, 6.6)
        gebaeude(pl, fps)
        pl.poly(fp, "hof")
        pl.poly(wand, "wand")
        pl.poly(fp, "hof-line")
        pl.scale_and_north()
        out.append('<figure class="panel"><figcaption>%s</figcaption>%s</figure>' % (titel, pl.svg("Grundriss des Innenhofs, " + label)))
    return "".join(out)


def zone_stil(z, hb, zmax):
    """Füllung nach Höhe z über der Plattenoberfläche: Platte 0, Hofboden 0,5, Terrasse 1 (Stufen über dem Hof bekommen so mehr Spielraum)."""
    p = 0.5 * z / hb if z <= hb else 0.5 + 0.5 * (z - hb) / (zmax - hb)
    return "--p:%.2f" % max(0.0, min(1.0, p))


def fig_treppen(fps, fp, s, data):
    """Südwestecke des Hofs mit allen Höhen: Terrasse, Stufen, Hofboden, Abstieg bis zur Platte, in Zonenfarben nach Höhe über der Platte."""
    hb, h0 = innenhof.hub(data, s), data["terrasse_hoehe"] * s
    zmax = hb + h0
    pl = Plan(-103, -66, -30, 18, 13.0)
    gebaeude(pl, fps)
    pl.poly(fp, "zone", zone_stil(hb, hb, zmax))
    pl.poly(innenhof.terrasse_mm(fp, s, data), "zone", zone_stil(zmax, hb, zmax))
    marken = {}
    for name, fall, stufen in innenhof.treppen_mm(fp, s, data):
        for poly, _, top in stufen:
            pl.poly(poly, "zone", zone_stil(hb + top, hb, zmax))
            pl.poly(poly, "stufe")
        marken[name] = unary_union([p for p, _, _ in stufen]).representative_point()
    pl.poly(fp, "hof-line")
    pl.scale_and_north(5.0)
    return pl, marken


def fig_treppen_svg(fps, fp, s, data):
    pl, marken = fig_treppen(fps, fp, s, data)
    m = {k: (v.x, v.y) for k, v in marken.items()}
    pl.marker(*m["west"], -99.5, 12.0, "W")
    pl.marker(*m["kante"], -68.0, 4.5, "K")
    pl.marker(*m["sued"], -101.0, -23.0, "S")
    return pl.svg("Südwestecke des Hofs mit Terrasse und den drei Treppen W, K und S, gefärbt nach Höhe über der Platte")


# --------------------------------------------------------------------------
# Schnitte (Zeichnung in mm, z nach oben)
# --------------------------------------------------------------------------
class Schnitt:
    def __init__(self, a0, a1, z0, z1, k=34.0):
        self.a0, self.a1, self.z0, self.z1, self.k = a0, a1, z0, z1, k
        self.w, self.h = (a1 - a0) * k, (z1 - z0) * k
        self.items = []

    def pt(self, a, z):
        return (a - self.a0) * self.k, (self.z1 - z) * self.k

    def contour(self, c, cls):
        self.items.append('<path class="%s" d="M%sZ"/>' % (cls, " L".join("%.1f %.1f" % self.pt(a, z) for a, z in c)))

    def line(self, a0, z0, a1, z1, cls):
        p, q = self.pt(a0, z0), self.pt(a1, z1)
        self.items.append('<line class="%s" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (cls, p[0], p[1], q[0], q[1]))

    def rect(self, a0, z0, a1, z1, cls):
        (x0, y0), (x1, y1) = self.pt(a0, z1), self.pt(a1, z0)
        self.items.append('<rect class="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>' % (cls, x0, y0, x1 - x0, y1 - y0))

    def text(self, a, z, s, cls="tiny", anchor="start"):
        px, py = self.pt(a, z)
        self.items.append('<text class="%s" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (cls, px, py, anchor, html.escape(s)))

    def dim_z(self, a, z0, z1, label, side=1):
        """Maßlinie senkrecht bei a von z0 bis z1, Beschriftung rechts (side 1) oder links (-1)."""
        self.line(a, z0, a, z1, "dim")
        for z in (z0, z1):
            self.line(a - 0.12, z, a + 0.12, z, "dim")
        self.text(a + 0.25 * side, (z0 + z1) / 2 - 0.12, label, "tiny", "start" if side > 0 else "end")

    def dim_a(self, z, a0, a1, label):
        """Maßlinie waagerecht bei z von a0 bis a1, Beschriftung darüber."""
        self.line(a0, z, a1, z, "dim")
        for a in (a0, a1):
            self.line(a, z - 0.12, a, z + 0.12, "dim")
        self.text((a0 + a1) / 2, z + 0.28, label, "lab2", "middle")

    def svg(self, label):
        return '<svg class="plan sec" viewBox="0 0 %.0f %.0f" role="img" aria-label="%s">%s</svg>' % (self.w, self.h, html.escape(label), "".join(self.items))


def intervalle_y(fp, y0):
    """Teile der Linie y = y0 im Umriss: [(x0, x1), …] von West nach Ost."""
    from shapely.geometry import LineString
    g = fp.intersection(LineString([(-200, y0), (0, y0)]))
    parts = [g] if g.geom_type == "LineString" else list(g.geoms)
    return sorted((min(p.coords[0][0], p.coords[-1][0]), max(p.coords[0][0], p.coords[-1][0])) for p in parts if not p.is_empty)


def fig_wand(schn, fp_a, fp_b, T):
    """Schnitt durch den Rand zum Neuen Augusteum: Mulde des Gebäudes, Trennwand, Hof-Aussparung, Einsatz."""
    xe = intervalle_y(fp_a, WAND_Y)[-1][1]                  # Ostrand der Hof-Aussparung in A
    xb = intervalle_y(fp_b, WAND_Y)[-1][1]                  # und in B
    x0, x1 = xe - 5.0, xe + 4.4
    out = []
    for titel, key, xr in (("A mit Trennwand %s mm" % de(P.HOF_WALL_T), "a", xe), ("B ohne Trennwand", "b", xb)):
        mu, ein = schn[key]
        xf = xr + (P.OUTLINE_CLR_T + P.HOF_WALL_T if key == "a" else P.OUTLINE_CLR_T - P.HOF_OVERLAP_T)   # Fassade (Grundriss) des Gebäudes
        sc = Schnitt(x0, x1, T - 8.0, T + 3.4, 46.0)
        sc.rect(xf, T - 8.0, x1, T, "foot")
        for c in mu:
            sc.contour(c, "m-plate")
        for c in ein:
            sc.contour(c, "m-stecker")
        sc.line(x0, T, x1, T, "ref")
        sc.line(x0, T - 6.0, x1, T - 6.0, "ref")
        sc.text(x0 + 0.1, T + 0.25, "Oberfläche", "tiny")
        sc.text(x0 + 0.1, T - 5.75, "Boden der Aussparung", "tiny")
        sc.text(x1 - 0.1, T - 2.2, "Gebäude", "lab2", "end")
        sc.text(x1 - 0.1, T - 2.75, "Fuß in der Mulde", "tiny", "end")
        if key == "a":
            sc.dim_a(T + 0.75, xr, xr + P.HOF_WALL_T, "Wand %s" % de(P.HOF_WALL_T))
        else:
            sc.text(xr - 0.1, T + 0.75, "keine Wand", "lab2", "end")
        out.append('<figure class="panel wide"><figcaption>%s</figcaption>%s</figure>' % (
            titel, sc.svg("Schnitt durch den Hofrand am Neuen Augusteum, Fassung %s" % key.upper())))
    return "".join(out), xe


def fig_sued(schn, T, data, s):
    """Längsschnitt durch den Gang im Süden: Terrasse, Stufen, Abstieg bis zur Platte."""
    mu, ein = schn
    sc = Schnitt(-31.0, -9.0, T - 7.4, T + 3.6, 36.0)
    for c in mu:
        sc.contour(c, "m-plate")
    for c in ein:
        sc.contour(c, "m-stecker")
    sc.line(-31.0, T, -9.0, T, "ref")
    sc.text(-30.8, T + 0.3, "Platte, Straßenniveau", "tiny")
    hb, h0 = innenhof.hub(data, s), data["terrasse_hoehe"] * s
    sc.dim_z(-9.6, T, T + hb, "%s Hof" % de(hb, 1), -1)
    sc.dim_z(-9.2, T + hb, T + hb + h0, "%s" % de(h0, 2), 1)
    return sc.svg("Längsschnitt durch den Gang zwischen Seminar- und Hörsaalgebäude: Terrasse, Stufen, Abstieg bis zur Plattenoberfläche")


# --------------------------------------------------------------------------
# Prüfung über alle Quellen und Maßstäbe
# --------------------------------------------------------------------------
def pruefmatrix():
    rows = []
    G.FAST = True
    for quelle in ("osm", "lod2", "laserscan"):
        for scale in (1000, 1300, 1500):
            s = 1000.0 / scale
            models = G.source_models(quelle, s)
            fps = [v[1] for v in models.values()]
            solid, fp, _ = innenhof.model(s, fps)
            tm = G.to_trimesh(solid)
            polys = G.polys_of(fp)
            rows.append((quelle, scale, tm.is_watertight, len(polys), sum(len(p.interiors) for p in polys),
                         len(schmale_stellen(fp)), unary_union(fps).distance(fp), tm.extents))
    return rows


def lade(name):
    return H.to_man(H.lade_stl(open(os.path.join(ALT, name), "rb").read()))


def main():
    s = 1000.0 / P.SCALE_PLAN
    data = innenhof.load()
    plate_a, report, models, places, outline, hof_a = C.build(hof_wand=P.HOF_WALL_T)
    plate_b, _, _, _, _, hof_b = C.build(hof_wand=0.0)
    T = C.plate_thickness(P.dims_plan())
    fps = {k: v[1] for k, v in models.items() if k in P.CASSETTE}
    fp_a = innenhof.flaeche_mm(list(fps.values()), s, C.hof_abstand(P.HOF_WALL_T))
    fp_b = innenhof.flaeche_mm(list(fps.values()), s, C.hof_abstand(0.0))
    fp_alt = H.alt_umriss(list(fps.values()), s)

    # 3D: Mulde (Platte um den Hof) und Stecker (Einsatz, in Einbaulage) der drei Fassungen
    region = H.ausschnitt(unary_union([fp_alt, fp_a, fp_b]))
    mul = {"alt": lade("mulde_1zu1300.stl"), "a": plate_a ^ G.extrude(region, -1.0, 30.0), "b": plate_b ^ G.extrude(region, -1.0, 30.0)}
    ein = {"alt": lade("hof_einsatz_1zu1300.stl").translate([0, 0, T]), "a": hof_a.translate([0, 0, T]), "b": hof_b.translate([0, 0, T])}
    tm = {"mulde_" + k: to_tm(v) for k, v in mul.items()}
    tm.update({"stecker_" + k: to_tm(v) for k, v in ein.items()})

    # Schnitte
    ach = data["achse_grad"]
    schn_wand = {k: (H.schnitt_y(mul[k], WAND_Y), H.schnitt_y(ein[k], WAND_Y)) for k in ("a", "b")}
    schn_sued = (H.schnitt_u(mul["a"], SUED_U, ach), H.schnitt_u(ein["a"], SUED_U, ach))
    fig_w, xe = fig_wand(schn_wand, fp_a, fp_b, T)

    def kz(fp, m):
        polys = G.polys_of(fp)
        return dict(fl=fp.area, m2=fp.area / s / s, um=fp.length, schmal=len(schmale_stellen(fp)), loch=sum(len(q.interiors) for q in polys),
                    ext=m.extents, vol=m.volume)
    ko, ka, kb = kz(fp_alt, tm["stecker_alt"]), kz(fp_a, tm["stecker_a"]), kz(fp_b, tm["stecker_b"])
    stufen = {n: len(st) for n, _, st in innenhof.treppen_mm(fp_a, s, data)}
    hb, h0 = innenhof.hub(data, s), data["terrasse_hoehe"] * s
    spiel_o = P.OUTLINE_CLR_T + 0.4 + P.HOF_CLR_T                      # Original: Hof-Aussparung 0,5 vom Grundriss (Wand 0,4)
    zeilen = [
        ("Einsatz, Maße", "%s × %s mm" % (de(ko["ext"][0]), de(ko["ext"][1])), "%s × %s mm" % (de(ka["ext"][0]), de(ka["ext"][1])),
         "%s × %s mm" % (de(kb["ext"][0]), de(kb["ext"][1])), "Höhe %s mm (Baumkronen)" % de(ka["ext"][2])),
        ("Einsatz, Volumen", "%s cm³" % de(ko["vol"] / 1000), "%s cm³" % de(ka["vol"] / 1000), "%s cm³" % de(kb["vol"] / 1000), "Material und Druckzeit"),
        ("Hoffläche der Aussparung", "%s mm²" % de(ko["fl"], 0), "%s mm²" % de(ka["fl"], 0), "%s mm²" % de(kb["fl"], 0), "A lässt rund %s mm² als Wand und Fuge liegen" % de(kb["fl"] - ka["fl"], 0)),
        ("Trennwand Hof ↔ Gebäude-Mulde", "0,4 mm", "%s mm" % de(P.HOF_WALL_T), "keine", "oben schneidet die Einführfase der Mulde 0,5 mm ab, bleibt in A %s mm" % de(P.HOF_WALL_T - P.MULDE_CH_T)),
        ("Abstand Einsatz ↔ Gebäudegrundriss", "%s mm" % de(spiel_o + 0.0, 2), "%s mm" % de(P.OUTLINE_CLR_T + P.HOF_WALL_T + P.HOF_CLR_T, 2),
         "%s mm" % de(P.OUTLINE_CLR_T - P.HOF_OVERLAP_T + P.HOF_CLR_T, 2), "Fuß, Mulde (Spiel %s) und Fuge (%s) zusammen" % (de(P.OUTLINE_CLR_T, 2), de(P.HOF_CLR_T, 2))),
        ("Schmale Stellen im Umriss (unter 4 mm)", str(ko["schmal"]), str(ka["schmal"]), str(kb["schmal"]), "Zungen, Stege"),
        ("Löcher im Umriss", str(ko["loch"]), str(ka["loch"]), str(kb["loch"]), ""),
        ("Treppen auf dem Einsatz", "keine", "3 (W, K, S)", "3 (W, K, S)", "Stufen je %s, %s und %s" % tuple("%d" % stufen[n] for n in ("west", "kante", "sued"))),
        ("Anschluss im Süden an die Platte", "Stufe %s mm" % de(hb + h0, 2), "bündig, %d Stufen" % stufen["sued"], "bündig, %d Stufen" % stufen["sued"], "Abstieg des Gangs zwischen Seminar- und Hörsaalgebäude"),
    ]
    tabelle = "".join('<tr><th scope="row">%s</th><td class="n">%s</td><td class="n a">%s</td><td class="n b">%s</td><td class="hint2">%s</td></tr>' % z for z in zeilen)

    matrix = pruefmatrix()
    pm = "".join('<tr><th scope="row">%s</th><td class="n">1:%d</td><td class="n %s">%s</td><td class="n">%d</td><td class="n">%d</td><td class="n">%d</td><td class="n">%s mm</td></tr>' % (
        q, sc, "ok" if d else "bad", "ja" if d else "NEIN", t, lo, sm, de(ab, 2)) for q, sc, d, t, lo, sm, ab, _ in matrix)
    alles_ok = all(d and t == 1 and lo == 0 and sm == 0 and ab >= 0.49 for _, _, d, t, lo, sm, ab, _ in matrix)

    cx, cy = (fp_b.bounds[0] + fp_b.bounds[2]) / 2, (fp_b.bounds[1] + fp_b.bounds[3]) / 2
    views = [
        dict(name="Übersicht", t=[cx, cy, T + 1], d=150, az=-62, el=48, text="Beide Teile eingesteckt. Mit dem Regler hebst du den Stecker aus der Mulde."),
        dict(name="Trennwand", t=[xe + 0.4, WAND_Y, T - 1.0], d=24, az=0, el=26,
             text="Blick aus der Gebäude-Mulde nach Westen auf den Hofrand. In A steht eine Wand von %s mm zwischen Mulde und Aussparung, in B gehen Mulde und Aussparung ineinander über." % de(P.HOF_WALL_T)),
        dict(name="Südtreppe", t=[-93.5, -17.0, T], d=36, az=-122, el=30,
             text="Der Gang zwischen Seminar- und Hörsaalgebäude: Terrasse, dann sechs Stufen bis auf Plattenhöhe. Die letzte Stufe liegt bündig mit der Platte."),
        dict(name="Westrampe", t=[-94.5, 2.0, T + 1], d=34, az=-15, el=38,
             text="Die Rampe am Seminargebäude ist ein Rechteck, das bis an die Fassade reicht. Drei Stufen führen von der Terrasse nach Norden zum Hof."),
        dict(name="Von oben", t=[cx, cy, T], d=170, az=-90, el=88, text="Grundriss von oben, Norden ist oben."),
    ]
    daten = {"views": views}
    for k, tmx in tm.items():
        daten[k] = pack(tmx)

    ersetz = {
        "@DATA@": json.dumps(daten, ensure_ascii=False),
        "@FIG_VERGLEICH@": fig_vergleich(fps, fp_alt, fp_a, fp_b),
        "@FIG_TREPPEN@": fig_treppen_svg(fps, fp_a, s, data),
        "@FIG_WAND@": fig_w,
        "@FIG_SUED@": fig_sued(schn_sued, T, data, s),
        "@TABELLE@": tabelle,
        "@PRUEFMATRIX@": pm,
        "@WAND@": de(P.HOF_WALL_T), "@WAND_OBEN@": de(P.HOF_WALL_T - P.MULDE_CH_T), "@FASE@": de(P.MULDE_CH_T), "@SPIEL@": de(P.OUTLINE_CLR_T, 2),
        "@FUGE@": de(P.HOF_CLR_T, 2), "@HOF_FASE@": de(P.HOF_CH_T, 1), "@TIEFE@": de(P.HOF_DEPTH_T, 1), "@HUB@": de(hb, 1),
        "@H_TERR@": de(h0, 2), "@H_TERR_M@": de(data["terrasse_hoehe"], 2), "@GESAMT@": de(hb + h0, 2), "@RISER@": de((hb + h0) / stufen["sued"], 2),
        "@STUFEN_S@": str(stufen["sued"]), "@LAUF_S@": de((data["form"]["treppen"][2]["t"][1] - data["form"]["treppen"][2]["t"][0]) * s, 1),
        "@MIN_BREITE@": de(innenhof.HOF_MIN_BREITE, 1),
        "@FL_A@": de(ka["fl"], 0), "@FL_B@": de(kb["fl"], 0), "@FL_O@": de(ko["fl"], 0),
        "@UM_A@": de(ka["um"], 0), "@UM_O@": de(ko["um"], 0),
        "@EXT_A@": "%s × %s" % (de(ka["ext"][0]), de(ka["ext"][1])), "@EXT_B@": "%s × %s" % (de(kb["ext"][0]), de(kb["ext"][1])), "@EXT_O@": "%s × %s" % (de(ko["ext"][0]), de(ko["ext"][1])),
        "@SCHMAL_O@": str(ko["schmal"]),
        "@PRUEF_ERGEBNIS@": "Alle %d Läufe (Quelle × Maßstab): Einsatz dicht, ein Teil, ohne Löcher und schmale Stellen" % len(matrix) if alles_ok else "ACHTUNG: Prüfung nicht bestanden",
        "@PLATTE@": "dicht" if (to_tm(plate_a).is_watertight and to_tm(plate_b).is_watertight) else "NICHT dicht",
        "@KOLLISION@": "keine Kollision der Docks mit Platte oder Hof" if all(r[4] < 0.05 for r in report) else "ACHTUNG: Kollision",
        "@DICHT@": "ja" if all(tm["stecker_" + k].is_watertight for k in ("a", "b")) else "NEIN",
    }
    page = open(os.path.join(HERE, "page.template.html"), encoding="utf-8").read()
    for k, v in ersetz.items():
        page = page.replace(k, v)
    pfad = os.path.join(HERE, "page.html")
    open(pfad, "w", encoding="utf-8").write(page)
    print("page.html: %.0f KB; Fläche Original %.0f, A %.0f, B %.0f mm²; schmale Stellen %d/%d/%d; Matrix ok=%s" % (
        os.path.getsize(pfad) / 1024, ko["fl"], ka["fl"], kb["fl"], ko["schmal"], ka["schmal"], kb["schmal"], alles_ok))
    return alles_ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
