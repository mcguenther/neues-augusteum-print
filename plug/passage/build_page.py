#!/usr/bin/env python3
"""Vorschlagsseite „Durchgang zwischen Paulinum und Institutsgebäude“: plug/passage/page.html (Vorlage page.template.html).

Zeigt, was heute im Modell steckt (Vollblock im Paulinum, senkrechte Streifen an der Ostwand) und den Vorschlag: das ganze Teil entfällt (Block und
Brücke), die Gasse ist auf ganzer Länge frei, die Treppe der Platte reicht bis zum früheren Ostende der Brücke. Grundrisse, Schnitte, 3D (Ist und
Neu nebeneinander) und die Prüfung der freien Gasse kommen aus den echten Laserscan-Körpern (`plug/passage/geom.py`). Nichts davon ist schon im
Generator.

Aufruf (aus dem Wurzelverzeichnis, ca. 30 s):
    python3 -m plug.passage.build_page
"""
import base64
import html
import json
import os

import numpy as np
from shapely.geometry import box
from shapely.ops import unary_union

import generate as G
import innenhof as I
from plug.geom import to_tm
from plug.passage import geom as PG

HERE = os.path.dirname(os.path.abspath(__file__))
S = PG.S
U_MITTE_M = -60.3          # Querschnitt quer durch den Durchgang (Hofsystem, m)
T_MITTE_M = 64.3           # Längsschnitt durch die Mitte der Gasse (Hofsystem, m)
STUFEN_NEU = 9
ENDE_U = -56.0             # Ostende des Durchgangs im Hofsystem (m)
FUSS_T = 14.2              # Fußhöhe der steckbaren Gebäude (plug/testcase/params.py)


def de(v, nd=1):
    return ("%.*f" % (nd, v)).replace(".", ",")


def pack(tm):
    """Dreiecke ohne Indizes als float32 (flache Schattierung), base64."""
    return base64.b64encode(np.asarray(tm.triangles, dtype="<f4").tobytes()).decode()


def rings(geom, nd=2):
    """Flächen als Liste von Polygonen, je Polygon Liste von Ringen (Außenring zuerst), Punkte [x, y]."""
    return [[[[round(x, nd), round(y, nd)] for x, y in r.coords] for r in [p.exterior] + list(p.interiors)] for p in G.polys_of(geom)]


# --------------------------------------------------------------------------
# Grundrisse im Hofsystem (Gasse waagerecht, Osten rechts)
# --------------------------------------------------------------------------
class Plan:
    def __init__(self, u0, u1, t0, t1, k=14.0):
        self.u0, self.u1, self.t0, self.t1, self.k = u0 * S, u1 * S, t0 * S, t1 * S, k
        self.w, self.h = (self.u1 - self.u0) * k, (self.t1 - self.t0) * k
        self.box = box(self.u0, self.t0, self.u1, self.t1)
        self.items = []

    def pt(self, u, t):
        return (u - self.u0) * self.k, (self.t1 - t) * self.k

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

    def text(self, u, t, s, cls="t", anchor="start"):
        x, y = self.pt(u, t)
        self.items.append('<text class="%s" x="%.1f" y="%.1f" text-anchor="%s">%s</text>' % (cls, x, y, anchor, html.escape(s)))

    def scale(self, mm=10.0):
        u, t = self.u1 - mm - 1.2, self.t0 + 1.4
        (ax, ay), (bx, by) = self.pt(u, t), self.pt(u + mm, t)
        self.items.append('<path class="bar" d="M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f M%.1f %.1f L%.1f %.1f"/>'
                          % (ax, ay, bx, by, ax, ay - 4, ax, ay + 4, bx, by - 4, bx, by + 4))
        self.text(u + mm / 2, t + 1.6, "%d mm = %s m" % (mm, de(mm / S, 1)), "tiny", "middle")

    def svg(self, label):
        return '<svg class="plan" viewBox="0 0 %.0f %.0f" role="img" aria-label="%s">%s</svg>' % (self.w, self.h, html.escape(label), "".join(self.items))


def stil(z, hb):
    return "--p:%.2f" % max(0.0, min(1.0, z / hb))


def fig_plan(titel, label, fps, baender, hof, neu):
    """Grundriss der Gasse: Gebäude, Hof, Stufen nach Höhe, Durchgang (Ist: Vollblock, Neu: Brücke darüber)."""
    hb = I.hub(I.load(), S)
    pl = Plan(-100, -50, 52, 93, 15.0)
    h = PG.nach_hof_mm
    pl.poly(h(hof), "hof")
    for poly, z in baender:
        pl.poly(h(poly), "zone", stil(z, hb))
        pl.poly(h(poly), "stufe")
    for fp in fps.values():
        pl.poly(h(fp), "bld")
    t = h(PG.tunnel_mm())
    if neu:
        pl.poly(t, "tunnel-neu")
        c = t.centroid
        pl.text(c.x, c.y - 0.4, "frei", "lab2", "middle")
    else:
        pl.poly(t, "block")
        pl.poly(t, "tunnel-ist")
        c = t.centroid
        pl.text(c.x, c.y - 0.4, "Vollblock", "lab2", "middle")
    pl.text(-86 * S, 57.0 * S, "Paulinum", "bname", "middle")
    pl.text(-80 * S, 80.0 * S, "Institutsgebäude", "bname", "middle")
    pl.text(-97.5 * S, 70.0 * S, "Hof", "bname", "middle")
    pl.text(-52.3 * S, 66.0 * S, "Augustus-", "tiny", "middle")
    pl.text(-52.3 * S, 64.6 * S, "platz", "tiny", "middle")
    pl.scale(10.0)
    return '<figure class="panel"><figcaption>%s</figcaption>%s</figure>' % (titel, pl.svg(label))


def bilder(pair, neu):
    """Ist und Neu von Nordosten und vom Augustusplatz nach vorschau/passage/ (Paulinum blau, Institutsgebäude kupfer)."""
    import preview
    out = os.path.join(os.path.dirname(os.path.dirname(HERE)), "vorschau", "passage")
    os.makedirs(out, exist_ok=True)
    for tag, src in (("ist", pair), ("neu", neu)):
        tms = [(to_tm(src[k][0]), c) for k, c in (("01_paulinum", "#8fa4c4"), ("05_institutsgebaeude", "#d49a68"))]
        for az, el, name in ((20, 22, "nordost"), (-12, 10, "ostportal")):
            preview.render(tms, size=(1300, 900), azim=az, elev=el, light_from_view=True).save(os.path.join(out, "%s_%s.png" % (tag, name)))


# --------------------------------------------------------------------------
def main():
    pair = PG.laser_pair()
    neu = PG.umbauen(pair)
    data = I.load()
    hb = I.hub(data, S)
    tun = PG.tunnel_mm()
    mass = PG.maße()
    laenge_m = mass["flaeche_m2"] / mass["breite_m"]       # mittlere Länge der früheren Brücke (die Stirnflächen stehen schräg)

    fps_alt = {k: v[1] for k, v in pair.items()}
    fps_neu = {k: v[1] for k, v in neu.items()}

    # Stufen: alt (6 Stufen auf 7 m, Gebäude mit Block) und neu (9 Stufen bis zum früheren Ostende der Brücke)
    a = PG.ALT
    n_neu = PG.neu(STUFEN_NEU, ENDE_U)
    b_alt = PG.gasse_baender(fps_alt.values(), a["u"], a["t"], a["n"], a["lauf"])
    b_neu = PG.gasse_baender(fps_neu.values(), n_neu["u"], n_neu["t"], n_neu["n"], n_neu["lauf"])
    hof = G.scale_geom(I.hof_polygon_local().buffer(I.HOF_UEBERMASS).intersection(I.huelle_m(data)), S)
    hof = hof.difference(unary_union(list(fps_alt.values())).buffer(0.9, join_style=2))

    # 3D: Ausschnitt um die Gasse, um die Fenstermitte verschoben
    x0, x1, y0, y1 = PG.FENSTER_M
    cx, cy = (x0 + x1) / 2 * S, (y0 + y1) / 2 * S
    fenster = box(x0 * S, y0 * S, x1 * S, y1 * S)
    crop = lambda solid: solid ^ G.extrude(fenster, -3, 60)
    shift = lambda m: m.translate([-cx, -cy, 0])
    tm = {}
    for tag, src, fps, baender in (("alt", pair, fps_alt, b_alt), ("neu", neu, fps_neu, b_neu)):
        tm["paulinum_" + tag] = to_tm(shift(crop(src["01_paulinum"][0])))
        tm["institut_" + tag] = to_tm(shift(crop(src["05_institutsgebaeude"][0])))
        tm["platte_" + tag] = to_tm(shift(PG.platte_ausschnitt(fps.values(), baender)))
    dicht = all(to_tm(v[0]).is_watertight for v in neu.values())
    bilder(pair, neu)
    vol = {k: (pair[k][0].volume(), neu[k][0].volume()) for k in pair}

    # Prüfung: ist die Gasse leer?
    rest_max, rest_liste, eng = PG.freie_gasse(neu)
    rest_alt, _, eng_alt = PG.freie_gasse(pair)
    frei_ok = rest_max < 1e-6

    # Schnitte (echte Querschnitte der Körper)
    pq_alt = PG.schnitt_quer(pair["01_paulinum"][0], U_MITTE_M)
    pq_neu = PG.schnitt_quer(neu["01_paulinum"][0], U_MITTE_M)
    iq = PG.schnitt_quer(neu["05_institutsgebaeude"][0], U_MITTE_M)
    pl_alt = PG.schnitt_laengs(pair["01_paulinum"][0], T_MITTE_M)
    tn = PG.nach_hof_mm(tun)

    def treppe_profil(n, u0, ende, lauf):
        tr = lauf / n
        return [[round((u0 + k * tr) * S, 3), round(min(u0 + (k + 1) * tr, ende) * S, 3), round(hb * (n - 1 - k) / n, 3)] for k in range(n - 1)]
    prof_alt = treppe_profil(a["n"], -94.0, a["u"][1], a["lauf"])
    prof_neu = treppe_profil(STUFEN_NEU, -94.0, ENDE_U, n_neu["lauf"])

    tc3 = np.asarray(tun.centroid.coords[0]) - [cx, cy]
    views = [
        dict(name="Ostportal", t=[tc3[0], tc3[1], 9.0], d=70, az=-12, el=10,
             text="Blick vom Augustusplatz in die Gasse. Neu: frei bis zum Hof. Ist: Vollblock mit senkrechten Streifen."),
        dict(name="Schräg Nordost", t=[tc3[0], tc3[1], 10.0], d=135, az=28, el=26,
             text="Paulinum (blau) und Institutsgebäude (orange) von Nordosten. Die Nordwand des Paulinums ist gerade."),
        dict(name="Von Westen", t=[tc3[0], tc3[1], 8.0], d=75, az=168, el=12,
             text="Blick vom Hof durch die Gasse nach Osten. Die Platte steigt zum Hof hin an."),
        dict(name="Gasse und Treppe", t=[tc3[0] - 16, tc3[1] + 3, 3.0], d=110, az=165, el=38,
             text="Die Stufen laufen neu von der Hofkante bis zum Ostende der Gasse."),
        dict(name="Von oben", t=[tc3[0] - 10, tc3[1], 0.0], d=170, az=-90, el=88, text="Grundriss von oben, Norden ist oben."),
    ]
    daten = {"views": views}
    for k, m in tm.items():
        daten[k] = pack(m)
    daten["z"] = dict(hb=round(hb, 3))
    daten["schnitt"] = dict(
        quer=dict(paulinum_alt=rings(pq_alt), paulinum_neu=rings(pq_neu), institut=rings(iq), fenster=[round(52 * S, 2), round(82 * S, 2)],
                  frei=[round(PG.WAND_T * S, 3), round(67.4 * S, 3)]),
        laengs=dict(block=rings(pl_alt), alt=prof_alt, neu=prof_neu, hof_u=round(-94.0 * S, 3), fenster=[round(-100 * S, 2), round(-50 * S, 2)],
                    bruecke=[round(tn.bounds[0], 3), round(tn.bounds[2], 3)]),
    )

    # Zahlen für Texte und Tabelle
    p_alt_a, p_neu_a = fps_alt["01_paulinum"].area, fps_neu["01_paulinum"].area
    tbr = tun.area
    lauf_alt = a["lauf"] * (a["n"] - 1) / a["n"] * S
    lauf_neu = (ENDE_U + 94.0) * S
    stufen = lambda n: "%d Stufen à %s mm" % (n, de(hb / n, 2))
    zeilen = [
        ("Block im Durchgang", "Vollblock, %s mm² Grundfläche, im Paulinum" % de(tbr, 0), "entfällt, Gasse frei", "samt Brücke; Nordwand des Paulinums gerade"),
        ("Freie Breite der Gasse (engste Stelle)", "%s m" % de(eng_alt, 1) if eng_alt > 0 else "0 m, zugefüllt", "%s m = %s mm" % (de(eng, 1), de(eng * S, 1)), "Hof bis Augustusplatz, alle Höhen geprüft"),
        ("Grundriss Paulinum", "%s mm², %d Teile" % (de(p_alt_a, 0), len(G.polys_of(fps_alt["01_paulinum"]))), "%s mm², %d Teil" % (de(p_neu_a, 0), len(G.polys_of(fps_neu["01_paulinum"]))),
         "Absatz und Splitter an der Institutswand entfallen"),
        ("Grundriss Institutsgebäude", "%s mm²" % de(fps_alt["05_institutsgebaeude"].area, 0), "%s mm²" % de(fps_neu["05_institutsgebaeude"].area, 0), "unverändert"),
        ("Volumen Paulinum", "%s cm³" % de(vol["01_paulinum"][0] / 1000, 1), "%s cm³" % de(vol["01_paulinum"][1] / 1000, 1), "Laserscan, 1:1300, massiv"),
        ("Volumen Institutsgebäude", "%s cm³" % de(vol["05_institutsgebaeude"][0] / 1000, 1), "%s cm³" % de(vol["05_institutsgebaeude"][1] / 1000, 1), "unverändert"),
        ("Treppe der Platte im Nordosten", "%s auf %s mm" % (stufen(a["n"]), de(lauf_alt, 1)), "%s auf %s mm" % (stufen(STUFEN_NEU), de(lauf_neu, 1)),
         "eine Stufe = eine Druckschicht (0,2 mm), Ende am früheren Ostende der Brücke"),
        ("Support", "–", "keiner nötig", "kein Überhang mehr über der Gasse"),
    ]
    tabelle = "".join('<tr><th scope="row">%s</th><td class="n o">%s</td><td class="n a">%s</td><td class="hint2">%s</td></tr>' % z for z in zeilen)
    hoehen = [z for z, _ in rest_liste]
    ersetz = {
        "@DATA@": json.dumps(daten, ensure_ascii=False),
        "@FIG_IST@": fig_plan("Ist: Vollblock", "Grundriss: heute füllt ein Vollblock die Gasse", fps_alt, b_alt, hof, False),
        "@FIG_NEU@": fig_plan("Neu: Gasse frei", "Grundriss: Gasse frei, Stufen bis zum Ostende", fps_neu, b_neu, hof, True),
        "@TABELLE@": tabelle,
        "@ZC_ABS@": de(PG.Z_DECKE_M, 1), "@ZT_ABS@": de(PG.Z_DACH_M, 1), "@BODEN_ABS@": de(PG.Z_BODEN_M, 1),
        "@ZC_M@": de(PG.Z_DECKE_M - PG.GROUND["05_institutsgebaeude"], 1), "@ZT_M@": de(PG.Z_DACH_M - PG.GROUND["05_institutsgebaeude"], 1),
        "@LAENGE_M@": de(laenge_m, 1), "@BREITE_M@": de(mass["breite_m"], 1), "@FLAECHE_M@": de(mass["flaeche_m2"], 0),
        "@HUB@": de(hb, 1), "@RISER@": de(hb / STUFEN_NEU, 2), "@STUFEN@": str(STUFEN_NEU),
        "@TREAD@": de(n_neu["lauf"] / STUFEN_NEU, 1), "@TREAD_MM@": de(n_neu["lauf"] / STUFEN_NEU * S, 1),
        "@LAUF_NEU@": de(lauf_neu, 1), "@LAUF_ALT@": de(lauf_alt, 1),
        "@ENG@": de(eng, 1), "@ENG_MM@": de(eng * S, 1),
        "@FREI@": "ja, in %d Höhen von 0,2 bis 28 mm ist in der Gasse kein Material" % 18 if frei_ok else "NEIN, Reste in Höhen %s mm" % ", ".join(de(z, 1) for z in hoehen),
        "@FREI_ALT@": "%s mm²" % de(rest_alt, 0),
        "@DICHT@": "ja" if dicht else "NEIN",
        "@VOL_P@": "%s → %s" % (de(vol["01_paulinum"][0] / 1000, 1), de(vol["01_paulinum"][1] / 1000, 1)),
    }
    page = open(os.path.join(HERE, "page.template.html"), encoding="utf-8").read()
    for k, v in ersetz.items():
        page = page.replace(k, v)
    pfad = os.path.join(HERE, "page.html")
    open(pfad, "w", encoding="utf-8").write(page)
    print("page.html: %.0f KB; Körper dicht=%s; Gasse frei=%s (engste Breite %.2f m, Restfläche Ist %.0f mm²)" % (
        os.path.getsize(pfad) / 1024, dicht, frei_ok, eng, rest_alt))
    return dicht and frei_ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
