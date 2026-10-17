#!/usr/bin/env python3
"""Vergleichsseite zum Innenhof-Einsatz: plug/hof/page.html (Vorlage page.template.html).

Zwei Stände: das Original (Spalt, Steg und Zungen; eingefroren in plug/hof/alt/) und der aktuelle Entwurf aus plug.campus.build und innenhof.py:
Hof bis an die Fassaden mit Trennwand (P.HOF_WALL_T, 0,8 mm) zu den Gebäude-Mulden, Treppen als Rechtecke, der Gang im Süden auf Terrassenhöhe mit
Treppe am Westende, im Nordosten eine Treppe zum Hof (beides Teil der Platte). Die Seite zeigt Grundrisse mit Höhen, Schnitte durch Trennwand und
Gang, 3D von Mulde und Stecker und die Prüfung über alle Quellen und Maßstäbe.

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
GANG_U = -92.0          # mm im Hofsystem: Längsschnitt durch die Mitte des Gangs im Süden
GANG_T = -37.5          # mm im Hofsystem: Querschnitt durch den Westteil des Gangs (zwischen Seminargebäude und Hörsaalgebäude)
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


def fig_vergleich(fps, fp_alt, fp_a):
    out = []
    wa = wand_flaeche(fps, fp_a, P.HOF_WALL_T)
    for titel, fp, wand, label in (("Original", fp_alt, None, "Original"), ("Neu, Einsatz und Trennwand %s mm" % de(P.HOF_WALL_T), fp_a, wa, "Neu")):
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


def hoehenplan(plan, fps, fp, s, data, auf):
    """Zeichnet Einsatz (Hofboden, Terrasse, Treppen) und Aufbauten der Platte (Gang, Treppen) nach Höhe über der Platte in den Plan."""
    hb, h0 = innenhof.hub(data, s), data["terrasse_hoehe"] * s
    zmax = hb + h0
    gebaeude(plan, fps)
    mulden = unary_union(list(fps.values())).buffer(P.OUTLINE_CLR_T, join_style=2)
    for _, bands in auf:
        for poly, top in bands:
            plan.poly(poly.difference(mulden), "zone", zone_stil(top, hb, zmax))
            plan.poly(poly.difference(mulden), "stufe")
    plan.poly(fp, "zone", zone_stil(hb, hb, zmax))
    plan.poly(innenhof.terrasse_mm(fp, s, data), "zone", zone_stil(zmax, hb, zmax))
    for _, stufen in innenhof.treppen_mm(fp, s, data):
        for poly, top in stufen:
            plan.poly(poly, "zone", zone_stil(hb + top, hb, zmax))
            plan.poly(poly, "stufe")
    plan.poly(fp, "hof-line")


def fig_hoehen(fps, fp, s, data, auf):
    """Ganzer Hof mit Gang und Nordost-Treppe, nach Höhe über der Platte gefärbt."""
    pl = Plan(-126, -50, -50, 76, 5.6)
    hoehenplan(pl, fps, fp, s, data, auf)
    pl.scale_and_north()
    return pl.svg("Der ganze Hof mit Gang im Süden und Treppe im Nordosten, gefärbt nach Höhe über der Platte")


def bands_mitte(auf, name, k):
    return dict(auf)[name][k][0].representative_point()


def fig_zoom_sw(fps, fp, s, data, auf):
    pl = Plan(-126, -84, -50, 22, 10.5)
    hoehenplan(pl, fps, fp, s, data, auf)
    pl.scale_and_north(5.0)
    st = dict(innenhof.treppen_mm(fp, s, data))
    mulden = unary_union(list(fps.values())).buffer(P.OUTLINE_CLR_T, join_style=2)
    w, k = st["west"][0][0].representative_point(), st["kante"][0][0].representative_point()
    g = dict(auf)["gang_sued"]
    gp = g[-1][0].difference(mulden).representative_point()
    tp = g[1][0].difference(mulden).representative_point()
    pl.marker(w.x, w.y, -108.0, 16.0, "W")
    pl.marker(k.x, k.y, -86.5, -6.0, "K")
    pl.marker(gp.x, gp.y, -108.0, -40.0, "G")
    pl.marker(tp.x, tp.y, -122.0, -30.0, "T")
    return pl.svg("Südwestecke: Terrasse und Treppen des Einsatzes (W, K), Gang auf Terrassenhöhe (G) und Treppe am Westende (T)")


def fig_zoom_ne(fps, fp, s, data, auf):
    pl = Plan(-80, -48, 44, 76, 15.0)
    hoehenplan(pl, fps, fp, s, data, auf)
    pl.scale_and_north(5.0)
    mulden = unary_union(list(fps.values())).buffer(P.OUTLINE_CLR_T, join_style=2)
    n = dict(auf)["nordost"][1][0].difference(mulden).representative_point()
    pl.marker(n.x, n.y, -52.0, 50.0, "N")
    return pl.svg("Nordost: Treppe aus dem Gang am Paulinum hinauf zum Hofboden")


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


def fig_wand(schn, fp_a, T):
    """Schnitt durch den Rand zum Neuen Augusteum: Mulde des Gebäudes, Trennwand, Hof-Aussparung, Einsatz."""
    xe = intervalle_y(fp_a, WAND_Y)[-1][1]                  # Ostrand der Hof-Aussparung
    x0, x1 = xe - 5.0, xe + 4.4
    mu, ein = schn
    xf = xe + P.OUTLINE_CLR_T + P.HOF_WALL_T                # Fassade (Grundriss) des Gebäudes
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
    sc.dim_a(T + 0.75, xe, xe + P.HOF_WALL_T, "Wand %s" % de(P.HOF_WALL_T))
    return '<figure class="panel wide"><figcaption>Trennwand zwischen Hof und Gebäude-Mulde</figcaption>%s</figure>' % sc.svg(
        "Schnitt durch den Hofrand am Neuen Augusteum"), xe


def fig_gang(schn, T, data, s, a0, a1, titel, label, tick):
    """Schnitt durch den Gang (Längsschnitt oder Querschnitt): Einsatz orange, Platte grau, Höhen bemaßt."""
    mu, ein = schn
    hb, h0 = innenhof.hub(data, s), data["terrasse_hoehe"] * s
    sc = Schnitt(a0, a1, T - 3.4, T + 3.8, 26.0)
    for c in mu:
        sc.contour(c, "m-plate")
    for c in ein:
        sc.contour(c, "m-stecker")
    sc.line(a0, T, a1, T, "ref")
    sc.text(a0 + 0.2, T + 0.3, "Platte, Straßenniveau", "tiny")
    sc.line(a0, T + hb + h0, a1, T + hb + h0, "ref")
    sc.text(a0 + 0.2, T + hb + h0 + 0.3, "Terrassenhöhe %s" % de(hb + h0, 2), "tiny")
    sc.text(*tick)
    return '<figure class="panel wide"><figcaption>%s</figcaption>%s</figure>' % (titel, sc.svg(label))


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
    plate, report, models, places, outline, hof_solid = C.build()
    T = C.plate_thickness(P.dims_plan())
    fps = {k: v[1] for k, v in models.items() if k in P.CASSETTE}
    fp_a = innenhof.flaeche_mm(list(fps.values()), s, C.hof_abstand(P.HOF_WALL_T))
    fp_alt = H.alt_umriss(list(fps.values()), s)
    auf = innenhof.platte_aufbau_mm(fp_a, s, data)
    aufd = dict(auf)
    ach = data["achse_grad"]
    hb, h0 = innenhof.hub(data, s), data["terrasse_hoehe"] * s

    # 3D: Mulde (Platte um Hof, Gang und Treppen) und Stecker (Einsatz, in Einbaulage), Original aus alt/
    aufpolys = unary_union([p for _, bands in auf for p, _ in bands])
    region = H.ausschnitt(unary_union([fp_alt, fp_a, aufpolys]))
    mul = {"alt": lade("mulde_1zu1300.stl"), "neu": plate ^ G.extrude(region, -1.0, 40.0)}
    ein = {"alt": lade("hof_einsatz_1zu1300.stl").translate([0, 0, T]), "neu": hof_solid.translate([0, 0, T])}
    tm = {"mulde_" + k: to_tm(v) for k, v in mul.items()}
    tm.update({"stecker_" + k: to_tm(v) for k, v in ein.items()})

    # Schnitte: Trennwand (y = const), Gang längs (u = const) und Querschnitt durch den Westteil des Gangs (t = const)
    sw = (H.schnitt_y(mul["neu"], WAND_Y), H.schnitt_y(ein["neu"], WAND_Y))
    fig_w, xe = fig_wand(sw, fp_a, T)
    f = data["form"]
    t_gang = f["platte"]["gang_sued"]["t"][1] * s
    fig_lang = fig_gang((H.schnitt_u(mul["neu"], GANG_U, ach), H.schnitt_u(ein["neu"], GANG_U, ach)), T, data, s, -46.0, -10.0,
                        "Längsschnitt durch den Gang im Süden", "Längsschnitt durch den Gang: Einsatz endet auf Terrassenhöhe, die Platte setzt den Gang auf gleicher Höhe fort",
                        (-24.0, T + hb + h0 + 0.9, "Einsatz  →", "lab2", "end"))
    fig_quer = fig_gang((H.schnitt_t(mul["neu"], GANG_T, ach), H.schnitt_t(ein["neu"], GANG_T, ach)), T, data, s, -124.0, -84.0,
                        "Querschnitt durch den Westteil des Gangs", "Querschnitt durch den Westteil des Gang: Treppe am Westende, dann Gang auf Terrassenhöhe",
                        (-119.0, T + 1.0, "Westende", "lab2", "start"))

    def kz(fp, m):
        polys = G.polys_of(fp)
        return dict(fl=fp.area, um=fp.length, schmal=len(schmale_stellen(fp)), loch=sum(len(q.interiors) for q in polys), ext=m.extents, vol=m.volume)
    ko, kn = kz(fp_alt, tm["stecker_alt"]), kz(fp_a, tm["stecker_neu"])
    zeilen = [
        ("Einsatz, Maße", "%s × %s mm" % (de(ko["ext"][0]), de(ko["ext"][1])), "%s × %s mm" % (de(kn["ext"][0]), de(kn["ext"][1])), "Höhe %s mm (Baumkronen)" % de(kn["ext"][2])),
        ("Einsatz, Volumen", "%s cm³" % de(ko["vol"] / 1000), "%s cm³" % de(kn["vol"] / 1000), "Material und Druckzeit"),
        ("Hoffläche der Aussparung", "%s mm²" % de(ko["fl"], 0), "%s mm²" % de(kn["fl"], 0), "ohne Gang; die Trennwand ist abgezogen"),
        ("Trennwand Hof ↔ Gebäude-Mulde", "0,4 mm", "%s mm" % de(P.HOF_WALL_T), "oben schneidet die Einführfase der Mulde %s mm ab, bleibt %s mm" % (de(P.MULDE_CH_T), de(P.HOF_WALL_T - P.MULDE_CH_T))),
        ("Schmale Stellen im Umriss (unter 4 mm)", str(ko["schmal"]), str(kn["schmal"]), "Zungen, Stege"),
        ("Löcher im Umriss", str(ko["loch"]), str(kn["loch"]), ""),
        ("Treppen im Einsatz", "keine", "2 (W, K)", "je 3 Stufen von der Terrasse zum Hof"),
        ("Gang im Süden", "Stufe %s mm" % de(hb + h0, 2), "Terrassenhöhe, in der Platte", "setzt den Einsatz ohne Stufe fort"),
        ("Treppe am Westende des Gangs", "–", "%d Stufen à %s mm" % (f["platte"]["gang_sued"]["stufen"], de((hb + h0) / f["platte"]["gang_sued"]["stufen"], 2)), "Teil der Platte, endet mit den Gebäudewänden"),
        ("Treppe im Nordosten", "–", "%d Stufen à %s mm" % (f["platte"]["nordost"]["stufen"], de(hb / f["platte"]["nordost"]["stufen"], 2)), "Teil der Platte, vom Gang auf den Hofboden"),
    ]
    tabelle = "".join('<tr><th scope="row">%s</th><td class="n o">%s</td><td class="n a">%s</td><td class="hint2">%s</td></tr>' % z for z in zeilen)

    matrix = pruefmatrix()
    pm = "".join('<tr><th scope="row">%s</th><td class="n">1:%d</td><td class="n %s">%s</td><td class="n">%d</td><td class="n">%d</td><td class="n">%d</td><td class="n">%s mm</td></tr>' % (
        q, sc, "ok" if d else "bad", "ja" if d else "NEIN", t, lo, sm, de(ab, 2)) for q, sc, d, t, lo, sm, ab, _ in matrix)
    alles_ok = all(d and t == 1 and lo == 0 and sm == 0 and ab >= 0.49 for _, _, d, t, lo, sm, ab, _ in matrix)

    cx, cy = (fp_a.bounds[0] + fp_a.bounds[2]) / 2, (fp_a.bounds[1] + fp_a.bounds[3]) / 2
    ge, ne = aufd["gang_sued"], aufd["nordost"]
    stair_w, stair_n = ge[0][0].representative_point(), ne[1][0].representative_point()
    views = [
        dict(name="Übersicht", t=[cx, cy - 10, T + 1], d=190, az=-62, el=48, text="Einsatz in der Mulde der Platte, mit Gang im Süden und Treppe im Nordosten. Mit dem Regler hebst du den Stecker heraus."),
        dict(name="Trennwand", t=[xe + 0.4, WAND_Y, T - 1.0], d=24, az=0, el=26,
             text="Blick aus der Gebäude-Mulde nach Westen auf den Hofrand: zwischen Mulde und Aussparung steht eine Wand von %s mm." % de(P.HOF_WALL_T)),
        dict(name="Gang", t=[-100.0, -14.0, T + 1], d=60, az=-95, el=36,
             text="Der Gang zwischen Seminar- und Hörsaalgebäude liegt in der Platte auf Terrassenhöhe und schließt ohne Stufe an den Einsatz an."),
        dict(name="Westende", t=[stair_w.x, stair_w.y, T + 1], d=30, az=-168, el=32,
             text="Am Westende des Gangs, wo Seminar- und Hörsaalgebäude enden, führt eine Treppe aus der Platte hinunter. Sie endet bündig mit den Gebäudewänden."),
        dict(name="Nordost", t=[stair_n.x, stair_n.y, T + 1], d=30, az=-10, el=34,
             text="Im Gang am Paulinum steigt eine Treppe aus der Platte hinauf zum Hofboden. Der Einsatz hat dort einen geraden Rand."),
        dict(name="Von oben", t=[cx, cy - 10, T], d=210, az=-90, el=88, text="Grundriss von oben, Norden ist oben."),
    ]
    daten = {"views": views}
    for k, tmx in tm.items():
        daten[k] = pack(tmx)

    ersetz = {
        "@DATA@": json.dumps(daten, ensure_ascii=False),
        "@FIG_VERGLEICH@": fig_vergleich(fps, fp_alt, fp_a),
        "@FIG_HOEHEN@": fig_hoehen(fps, fp_a, s, data, auf),
        "@FIG_SW@": fig_zoom_sw(fps, fp_a, s, data, auf),
        "@FIG_NE@": fig_zoom_ne(fps, fp_a, s, data, auf),
        "@FIG_WAND@": fig_w,
        "@FIG_LANG@": fig_lang, "@FIG_QUER@": fig_quer,
        "@TABELLE@": tabelle,
        "@PRUEFMATRIX@": pm,
        "@WAND@": de(P.HOF_WALL_T), "@WAND_OBEN@": de(P.HOF_WALL_T - P.MULDE_CH_T), "@FASE@": de(P.MULDE_CH_T), "@SPIEL@": de(P.OUTLINE_CLR_T, 2),
        "@FUGE@": de(P.HOF_CLR_T, 2), "@HOF_FASE@": de(P.HOF_CH_T, 1), "@HUB@": de(hb, 1),
        "@H_TERR@": de(h0, 2), "@H_TERR_M@": de(data["terrasse_hoehe"], 2), "@GESAMT@": de(hb + h0, 2),
        "@RISER_G@": de((hb + h0) / f["platte"]["gang_sued"]["stufen"], 2), "@RISER_N@": de(hb / f["platte"]["nordost"]["stufen"], 2),
        "@LAUF_G@": de(f["platte"]["gang_sued"]["lauf"] * s, 1), "@LAUF_N@": de(f["platte"]["nordost"]["lauf"] * s, 1),
        "@FL_A@": de(kn["fl"], 0), "@FL_O@": de(ko["fl"], 0),
        "@EXT_A@": "%s × %s" % (de(kn["ext"][0]), de(kn["ext"][1])), "@EXT_O@": "%s × %s" % (de(ko["ext"][0]), de(ko["ext"][1])),
        "@SCHMAL_O@": str(ko["schmal"]),
        "@PRUEF_ERGEBNIS@": "Alle %d Läufe (Quelle × Maßstab): Einsatz dicht, ein Teil, ohne Löcher und schmale Stellen" % len(matrix) if alles_ok else "ACHTUNG: Prüfung nicht bestanden",
        "@PLATTE@": "dicht" if to_tm(plate).is_watertight else "NICHT dicht",
        "@KOLLISION@": "keine Kollision der Docks mit Platte oder Hof" if all(r[4] < 0.05 for r in report) else "ACHTUNG: Kollision",
        "@DICHT@": "ja" if tm["stecker_neu"].is_watertight else "NEIN",
    }
    page = open(os.path.join(HERE, "page.template.html"), encoding="utf-8").read()
    for k, v in ersetz.items():
        page = page.replace(k, v)
    pfad = os.path.join(HERE, "page.html")
    open(pfad, "w", encoding="utf-8").write(page)
    print("page.html: %.0f KB; Fläche Original %.0f, neu %.0f mm²; schmale Stellen %d/%d; Matrix ok=%s" % (
        os.path.getsize(pfad) / 1024, ko["fl"], kn["fl"], ko["schmal"], kn["schmal"], alles_ok))
    return alles_ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
