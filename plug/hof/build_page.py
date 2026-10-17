#!/usr/bin/env python3
"""Vergleichsseite zum Innenhof-Einsatz: plug/hof/page.html (Vorlage page.template.html).

Zeigt den alten Stand (Spalt zwischen Hof und Terrasse, Steg am Hörsaalgebäude, schmale Zungen; eingefroren in plug/hof/alt/) neben dem neuen
blockigen Umriss (innenhof.py): Befund, Vorher/Nachher/Unterschied im Grundriss, 3D-Ansicht von Mulde (Platte um den Hof) und Stecker (Einsatz),
Schnitt durch die Stegstelle, Treppen auf dem Einsatz, Prüfung über alle Quellen und Maßstäbe.

Aufruf (aus dem Wurzelverzeichnis, ca. 1 min; plug/hof/alt/ muss existieren, sonst erst `python3 -m plug.hof.freeze_alt`):
    python3 -m plug.hof.build_page
"""
import base64
import html
import json
import os

import numpy as np
from shapely.geometry import LineString, Polygon, box
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
SCHNITT_X = -80.0       # mm: Schnittebene durch Steg, Spalt und Hof
MIN_STELLE_MM2 = 3.0    # kleinere Reste beim Öffnen sind Ecken, keine schmalen Stellen


def de(v, nd=1):
    return ("%.*f" % (nd, v)).replace(".", ",")


def pack(tm):
    """Dreiecke ohne Indizes als float32 (flache Schattierung), base64."""
    return base64.b64encode(np.asarray(tm.triangles, dtype="<f4").tobytes()).decode()


# --------------------------------------------------------------------------
# Grundrisse als SVG (Einheiten: K je mm, y nach oben = Norden)
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

    def poly(self, geom, cls):
        if geom is not None and not geom.is_empty:
            d = self.d(geom)
            if d:
                self.items.append('<path class="%s" d="%s"/>' % (cls, d))

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
    out = []
    for q in G.polys_of(fp.difference(fp.buffer(-r).buffer(r))):
        if q.area >= MIN_STELLE_MM2:
            out.append(q)
    return out


def spalt_punkt(neu, alt, x0=-80.0):
    """Punkt in der Mitte des Spalts (Treppe 1) bei x = x0: Mitte der Linie durch das größte Stück, das der neue Umriss hinzufügt."""
    stuecke = [q for q in G.polys_of(neu.difference(alt)) if q.area >= 8.0 and q.centroid.y < 8.0]
    q = max(stuecke, key=lambda g: g.area)
    seg = q.intersection(LineString([(x0, -10), (x0, 20)]))
    c = seg.centroid
    return c.x, c.y


def marker_set(pl, st, loecher, zoom, spalt):
    """Marker A bis F: Ziel und Beschriftungsort (mm). Im Zoom fehlen D, im Überblick liegt alles im Bild."""
    hx, hy = loecher[0].centroid.coords[0] if loecher else (-91.5, 8.5)
    if zoom:
        pl.marker(*spalt, -72.5, 9.5, "A")
        pl.marker(*st["steg"], -92.5, -3.4, "B")
        pl.marker(-91.2, 17.5, -97.5, 22.0, "C")
        pl.marker(*st["ost"], -68.5, 5.5, "E")
        pl.marker(hx, hy, -98.0, 9.0, "F")
    else:
        pl.marker(*spalt, -70.0, 10.0, "A")
        pl.marker(*st["steg"], -91.5, -4.2, "B")
        pl.marker(-91.2, 17.5, -100.0, 24.0, "C")
        pl.marker(*st["nord"], -63.0, 69.5, "D")
        pl.marker(*st["ost"], -66.0, -1.0, "E")
        pl.marker(hx, hy, -99.5, 12.0, "F")


def fig_befund(fps, alt, stellen, loecher, neu, zoom=False):
    pl = Plan(-100, -66, -5, 25, 13.5) if zoom else Plan(-103, -53, -7, 76, 7.6)
    gebaeude(pl, fps)
    pl.poly(alt, "hof")
    for q in stellen:
        pl.poly(q, "thin")
    for q in G.polys_of(neu.difference(alt)):
        if q.area >= 2.0:
            pl.poly(q, "gap")
    for q in loecher:
        pl.poly(q.buffer(0.35), "gap")
    pl.poly(alt, "hof-line")
    pl.scale_and_north(5.0 if zoom else 10.0)
    marker_set(pl, stellen_nach_ort(stellen), loecher, zoom, spalt_punkt(neu, alt))
    return pl.svg("Grundriss des Innenhofs vor der Änderung mit den Problemstellen " + ("A, B, C, E und F" if zoom else "A bis F"))


def stellen_nach_ort(stellen):
    """Schmale Stellen den Namen zuordnen: Steg (größte), Nord, Ost; Rest sind Ausläufer der Buchten."""
    res = {}
    for q in sorted(stellen, key=lambda q: -q.area):
        c = q.centroid.coords[0]
        if "steg" not in res and q.area > 30:
            res["steg"] = c
        elif c[1] > 50:
            res["nord"] = c
        elif c[0] > -76 and c[1] < 5:
            res["ost"] = c
    return res


def fig_vergleich(fps, alt, neu):
    out = []
    spec = [("Vorher", "vorher"), ("Nachher", "nachher"), ("Unterschied", "diff")]
    entf = alt.difference(neu).buffer(0)
    dazu = neu.difference(alt).buffer(0)
    for titel, kind in spec:
        pl = Plan(-103, -53, -7, 76, 6.8)
        gebaeude(pl, fps)
        if kind == "vorher":
            pl.poly(alt, "hof")
            pl.poly(alt, "hof-line")
        elif kind == "nachher":
            pl.poly(neu, "hof")
            pl.poly(neu, "hof-line")
        else:
            pl.poly(neu.intersection(alt), "hof")
            pl.poly(entf, "weg")
            pl.poly(dazu, "neu")
        pl.scale_and_north()
        out.append('<figure class="panel"><figcaption>%s</figcaption>%s</figure>' % (titel, pl.svg("Grundriss des Innenhofs, " + titel.lower())))
    return "".join(out), entf, dazu


def fig_zoom(fps, alt, neu, treppen, terr_mm, s):
    """Stegstelle: links vorher, rechts nachher mit Höhenstufen."""
    panels = []
    for titel, kind in (("Vorher", "alt"), ("Nachher", "neu")):
        pl = Plan(-100, -66, -5, 25, 13.5)
        gebaeude(pl, fps)
        if kind == "alt":
            pl.poly(alt, "h0")
            pl.poly(alt.intersection(terr_mm), "h3")
            pl.poly(alt, "hof-line")
        else:
            pl.poly(neu, "h0")
            pl.poly(neu.intersection(terr_mm), "h3")
            for poly, stufen in treppen:
                for i, (zone, h) in enumerate(sorted(stufen, key=lambda t: t[1])):   # Zonen sind verschachtelt: niedrige (große) zuerst
                    pl.poly(zone, "h%d" % min(i + 1, 2))
            pl.poly(neu, "hof-line")
        pl.scale_and_north(5.0)
        panels.append('<figure class="panel wide"><figcaption>%s</figcaption>%s</figure>' % (
            titel, pl.svg("Stegstelle am Hörsaalgebäude, " + titel.lower())))
    return "".join(panels)


# --------------------------------------------------------------------------
# Schnitt (y, z) durch die Stegstelle
# --------------------------------------------------------------------------
class Schnitt:
    def __init__(self, y0, y1, z0, z1, k=34.0):
        self.y0, self.y1, self.z0, self.z1, self.k = y0, y1, z0, z1, k
        self.w, self.h = (y1 - y0) * k, (z1 - z0) * k
        self.items = []

    def pt(self, y, z):
        return (y - self.y0) * self.k, (self.z1 - z) * self.k

    def contour(self, c, cls):
        self.items.append('<path class="%s" d="M%sZ"/>' % (cls, " L".join("%.1f %.1f" % self.pt(y, z) for y, z in c)))

    def line(self, y0, z0, y1, z1, cls):
        a, b = self.pt(y0, z0), self.pt(y1, z1)
        self.items.append('<line class="%s" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (cls, a[0], a[1], b[0], b[1]))

    def text(self, y, z, s, cls="t", anchor="start"):
        px, py = self.pt(y, z)
        self.items.append('<text class="%s" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (cls, px, py, anchor, html.escape(s)))

    def dim(self, y, z0, z1, label, side=1):
        """Maßlinie senkrecht bei y von z0 bis z1, Beschriftung rechts (side 1) oder links (-1)."""
        self.line(y, z0, y, z1, "dim")
        for z in (z0, z1):
            self.line(y - 0.12, z, y + 0.12, z, "dim")
        self.text(y + 0.28 * side, (z0 + z1) / 2 - 0.12, label, "tiny", "start" if side > 0 else "end")

    def svg(self, label):
        return '<svg class="plan sec" viewBox="0 0 %.0f %.0f" role="img" aria-label="%s">%s</svg>' % (self.w, self.h, html.escape(label), "".join(self.items))


def intervalle(fp, x0):
    """Teile der Linie x = x0 im Umriss: [(y0, y1), …] von Süden nach Norden."""
    g = fp.intersection(LineString([(x0, -20), (x0, 90)]))
    parts = [g] if g.geom_type == "LineString" else list(g.geoms)
    return sorted((min(p.coords[0][1], p.coords[-1][1]), max(p.coords[0][1], p.coords[-1][1])) for p in parts if not p.is_empty)


def fig_schnitt(schnitte, alt, neu, T, treppen_h, terr_h):
    ia = intervalle(alt, SCHNITT_X)
    (s0, s1), (h0, _) = ia[0], ia[1]
    rippe_y = (s1 + h0) / 2
    out = []
    for titel, key in (("Vorher", "alt"), ("Nachher", "neu")):
        mulde, stecker = schnitte[key]
        sc = Schnitt(-3.0, 9.5, T - 7.6, T + 3.8, 40.0)
        for c in mulde:
            sc.contour(c, "m-plate")
        for c in stecker:
            sc.contour(c, "m-stecker")
        sc.line(-3.0, T, 9.5, T, "ref")
        sc.line(-3.0, T - 6.0, 9.5, T - 6.0, "ref")
        sc.text(-2.9, T + 0.25, "Oberfläche", "tiny")
        sc.text(-2.9, T - 5.75, "Mulden-Boden", "tiny")
        sc.dim(8.7, T - 6.0, T, "6,0", 1)
        sc.dim(8.7, T, T + 1.8, "1,8", 1)
        if key == "alt":
            sc.text((s0 + s1) / 2, T + 2.95, "Steg %s mm" % de(s1 - s0), "lab2", "middle")
            sc.line(rippe_y, T + 0.1, rippe_y + 1.2, T + 3.0, "dim")
            sc.text(rippe_y + 1.35, T + 3.05, "Rippe der Platte %s mm" % de(h0 - s1), "lab2")
        else:
            sc.line(rippe_y, T + 2.15, rippe_y + 0.8, T + 3.0, "dim")
            sc.text(rippe_y + 0.95, T + 3.05, "Treppe: %s" % " → ".join(de(h, 2) for h in [terr_h] + treppen_h + [0.0]), "lab2")
            sc.text(-0.2, T + 3.05, "ein Block", "lab2")
        out.append('<figure class="panel wide"><figcaption>%s</figcaption>%s</figure>' % (
            titel, sc.svg("Schnitt durch den Hof bei x = %s mm, %s" % (de(SCHNITT_X, 0), titel.lower()))))
    return "".join(out)


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
                         len(schmale_stellen(fp)), unary_union(fps).distance(fp), len(innenhof.treppen_mm(fp, s))))
    return rows


def main():
    s = 1000.0 / P.SCALE_PLAN
    plate, report, models, places, outline, hof_solid = C.build()
    T = C.plate_thickness(P.dims_plan())
    fps = {k: v[1] for k, v in models.items() if k in P.CASSETTE}
    neu = innenhof.flaeche_mm(list(fps.values()), s)
    alt = H.alt_umriss(list(fps.values()), s)
    data = innenhof.load()
    terr = G.scale_geom(Polygon(data["terrasse"]), s)
    treppen = innenhof.treppen_mm(neu, s, data)
    treppen_h = sorted({h for _, st in treppen for _, h in st}, reverse=True)

    # 3D: Mulde (Platte um den Hof) und Stecker (Einsatz, in Einbaulage), vorher aus alt/, nachher aus dem Generator
    region = H.ausschnitt(alt)
    mulde_neu = plate ^ G.extrude(region, -1.0, 30.0)
    mulde_alt = H.to_man(H.lade_stl(open(os.path.join(ALT, "mulde_1zu1300.stl"), "rb").read()))
    ein_alt = H.to_man(H.lade_stl(open(os.path.join(ALT, "hof_einsatz_1zu1300.stl"), "rb").read())).translate([0, 0, T])
    ein_neu = hof_solid.translate([0, 0, T])
    tm = {k: to_tm(v) for k, v in dict(mulde_alt=mulde_alt, mulde_neu=mulde_neu, stecker_alt=ein_alt, stecker_neu=ein_neu).items()}
    schnitte = {"alt": (H.schnitt_x(mulde_alt, SCHNITT_X), H.schnitt_x(ein_alt, SCHNITT_X)),
                "neu": (H.schnitt_x(mulde_neu, SCHNITT_X), H.schnitt_x(ein_neu, SCHNITT_X))}

    stellen_alt, stellen_neu = schmale_stellen(alt), schmale_stellen(neu)
    loecher = [Polygon(h) for p in G.polys_of(alt) for h in p.interiors]
    vergleich, entf, dazu = fig_vergleich(fps, alt, neu)
    ia = intervalle(alt, SCHNITT_X)
    rippe = ia[1][0] - ia[0][1] if len(ia) > 1 else 0.0
    steg = ia[0][1] - ia[0][0]

    def kz(p):
        polys = G.polys_of(p)
        return dict(fl=p.area, m2=p.area / s / s, um=p.length, kv=p.area / p.convex_hull.area, loch=sum(len(q.interiors) for q in polys),
                    teile=len(polys), schmal=len(schmale_stellen(p)), schmal_fl=sum(q.area for q in schmale_stellen(p)))
    a, n = kz(alt), kz(neu)
    ea, en = tm["stecker_alt"].extents, tm["stecker_neu"].extents
    va, vn = tm["stecker_alt"].volume, tm["stecker_neu"].volume
    zeilen = [
        ("Umfang des Umrisses", "%s mm" % de(a["um"], 0), "%s mm" % de(n["um"], 0), "weniger Kante, die brechen oder klemmen kann"),
        ("Schmale Stellen (Zungen, Stege unter 4 mm)", "%d, zusammen %s mm²" % (a["schmal"], de(a["schmal_fl"], 0)), "%d" % n["schmal"], "Passage-Ansätze Nord und Ost sind Plattenfläche"),
        ("Rippen und Zähne der Platte im Hof", "2 (Spalt A: %s mm breit, 6 mm hoch)" % de(rippe), "0", "Spalt 1 und 2 sind geschlossen"),
        ("Löcher im Umriss", "%d" % a["loch"], "%d" % n["loch"], "Splitter zwischen Terrasse und Hofgrenze"),
        ("Konvexität (Fläche zu konvexer Hülle)", de(a["kv"], 2), de(n["kv"], 2), "näher an einem Block"),
        ("Fläche des Umrisses", "%s mm² (%s m²)" % (de(a["fl"], 0), de(a["m2"], 0)), "%s mm² (%s m²)" % (de(n["fl"], 0), de(n["m2"], 0)), "Spalte kommen hinzu, Zungen entfallen"),
        ("Einsatz, Maße", "%s × %s mm" % (de(ea[0]), de(ea[1])), "%s × %s mm" % (de(en[0]), de(en[1])), "Höhe bleibt %s mm (Baumkronen)" % de(en[2])),
        ("Einsatz, Volumen", "%s cm³" % de(va / 1000, 1), "%s cm³" % de(vn / 1000, 1), ""),
        ("Treppen auf dem Einsatz", "keine", "2 (3 Stufen, bis %s mm)" % de(max(treppen_h) if treppen_h else 0, 2), "Terrassenhöhe 0,71 m im Scan"),
    ]
    tabelle = "".join('<tr><th scope="row">%s</th><td class="n alt">%s</td><td class="n neu">%s</td><td class="hint2">%s</td></tr>' % z for z in zeilen)

    matrix = pruefmatrix()
    pm = "".join('<tr><th scope="row">%s</th><td class="n">1:%d</td><td class="n %s">%s</td><td class="n">%d</td><td class="n">%d</td><td class="n">%d</td><td class="n">%s mm</td><td class="n">%d</td></tr>' % (
        q, sc, "ok" if d else "bad", "ja" if d else "NEIN", t, lo, sm, de(ab, 2), tr) for q, sc, d, t, lo, sm, ab, tr in matrix)
    alles_ok = all(d and t == 1 and lo == 0 and sm == 0 and ab >= 0.49 for _, _, d, t, lo, sm, ab, _ in matrix)

    cam_c = ((neu.bounds[0] + neu.bounds[2]) / 2, (neu.bounds[1] + neu.bounds[3]) / 2)
    views = [
        dict(name="Übersicht", t=[cam_c[0], cam_c[1], T + 1], d=150, az=-62, el=48, text="Beide Teile eingesteckt. Mit dem Regler hebst du den Stecker aus der Mulde."),
        dict(name="Stegstelle", t=[-82.0, 3.0, T], d=40, az=-76, el=34,
             text="Vorher steht zwischen Steg und Hof eine Rippe der Platte, die kaum breiter als eine Düsenlinie ist. Nachher ist die Stelle ein durchgehender Klotz."),
        dict(name="Treppe", t=[-91.0, 17.0, T + 1.0], d=24, az=-128, el=32,
             text="Die Treppe von der Terrasse zum Hof liegt als zwei Zwischenstufen auf dem Einsatz. Die Aussparung in der Platte bleibt glatt."),
        dict(name="Nordende", t=[-61.0, 64.0, T], d=40, az=-40, el=38,
             text="Die schmale Zunge zur Passage zwischen Paulinum und Augusteum ist weg. An dieser Stelle bleibt Plattenfläche."),
        dict(name="Von oben", t=[cam_c[0], cam_c[1], T], d=170, az=-90, el=88, text="Grundriss von oben, Norden ist oben."),
    ]
    daten = dict(mulde_alt=pack(tm["mulde_alt"]), mulde_neu=pack(tm["mulde_neu"]), stecker_alt=pack(tm["stecker_alt"]),
                 stecker_neu=pack(tm["stecker_neu"]), views=views)

    zoom = fig_zoom(fps, alt, neu, treppen, terr, s)
    ersetz = {
        "@DATA@": json.dumps(daten, ensure_ascii=False),
        "@FIG_BEFUND@": fig_befund(fps, alt, stellen_alt, loecher, neu),
        "@FIG_BEFUND_ZOOM@": fig_befund(fps, alt, stellen_alt, loecher, neu, zoom=True),
        "@FIG_VERGLEICH@": vergleich,
        "@FIG_ZOOM@": zoom,
        "@FIG_SCHNITT@": fig_schnitt(schnitte, alt, neu, T, treppen_h, data["terrasse_hoehe"] * s),
        "@TABELLE@": tabelle,
        "@PRUEFMATRIX@": pm,
        "@STEG_BREIT@": de(steg),
        "@RIPPE_BREIT@": de(rippe),
        "@UMFANG_ALT@": de(a["um"], 0), "@UMFANG_NEU@": de(n["um"], 0),
        "@SCHMAL_ALT@": str(a["schmal"]), "@SCHMAL_NEU@": str(n["schmal"]),
        "@LOCH_ALT@": str(a["loch"]), "@LOCH_NEU@": str(n["loch"]),
        "@H_TERR@": de(data["terrasse_hoehe"] * s, 2), "@H_TERR_M@": de(data["terrasse_hoehe"], 2),
        "@H_S2@": de(treppen_h[0], 2) if treppen_h else "-", "@H_S1@": de(treppen_h[-1], 2) if treppen_h else "-",
        "@H_S2M@": de(treppen_h[0] / s, 2) if treppen_h else "-", "@H_S1M@": de(treppen_h[-1] / s, 2) if treppen_h else "-",
        "@P_SCHLIESSEN@": de(innenhof.HOF_SCHLIESSEN, 1), "@P_BREITE@": de(innenhof.HOF_MIN_BREITE, 1),
        "@P_STUFEN@": str(innenhof.TREPPE_STUFEN), "@P_TIEFE@": de(P.HOF_DEPTH_T, 1), "@P_FUGE@": de(P.HOF_CLR_T, 2), "@P_FASE@": de(P.HOF_CH_T, 1),
        "@HUB@": de(innenhof.hub(data, s), 1),
        "@ENTF@": de(entf.area, 0), "@DAZU@": de(dazu.area, 0),
        "@PRUEF_ERGEBNIS@": "Alle %d Läufe (Quelle × Maßstab): Einsatz dicht, ein Teil, ohne Löcher und schmale Stellen" % len(matrix) if alles_ok else "ACHTUNG: Prüfung nicht bestanden",
        "@PLATTE@": "dicht" if to_tm(plate).is_watertight else "NICHT dicht",
        "@KOLLISION@": "keine Kollision der Docks mit Platte oder Hof" if all(r[4] < 0.05 for r in report) else "ACHTUNG: Kollision",
        "@DICHT_ALT@": "ja" if tm["stecker_alt"].is_watertight else "NEIN", "@DICHT_NEU@": "ja" if tm["stecker_neu"].is_watertight else "NEIN",
    }
    page = open(os.path.join(HERE, "page.template.html"), encoding="utf-8").read()
    for k, v in ersetz.items():
        page = page.replace(k, v)
    pfad = os.path.join(HERE, "page.html")
    open(pfad, "w", encoding="utf-8").write(page)
    print("page.html: %.0f KB; Steg %.1f mm, Rippe %.1f mm; schmale Stellen alt %d neu %d; Löcher alt %d neu %d; Matrix ok=%s" % (
        os.path.getsize(pfad) / 1024, steg, rippe, a["schmal"], n["schmal"], a["loch"], n["loch"], alles_ok))
    return alles_ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
