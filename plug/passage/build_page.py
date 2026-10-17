#!/usr/bin/env python3
"""Vorschlagsseite „Durchgang zwischen Paulinum und Institutsgebäude“: plug/passage/page.html (Vorlage page.template.html).

Zeigt, was heute im Modell steckt (Vollblock im Paulinum, senkrechte Streifen an der Ostwand) und den Vorschlag: waagerechter Schnitt unter der
Brücke, Durchgang frei, Brücke beim Institutsgebäude, Treppe der Platte bis zum Ostende des Durchgangs. Grundrisse, Schnitte und 3D (Ist und Neu
nebeneinander, Regler für die Deckenhöhe) kommen aus den echten Laserscan-Körpern (`plug/passage/geom.py`). Nichts davon ist schon im Generator.

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
    pl.poly(t, "bruecke" if neu else "block")
    pl.poly(t, "tunnel-neu" if neu else "tunnel-ist")
    c = t.centroid
    pl.text(c.x, c.y - 0.4, "Brücke über dem Durchgang" if neu else "Vollblock", "lab2", "middle")
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
    neu_ohne = PG.umbauen(pair, mit_bruecke=False)      # für die Ansichten: die Brücke zeichnet die Seite selbst
    data = I.load()
    hb = I.hub(data, S)
    zc = PG.decke_mm()
    zt = PG.decke_mm(PG.Z_DACH_M)
    tun = PG.tunnel_mm()
    mass = PG.maße()
    laenge_m = mass["flaeche_m2"] / mass["breite_m"]       # mittlere Länge (die Stirnflächen stehen schräg)

    fps_alt = {k: v[1] for k, v in pair.items()}
    fps_neu = {k: v[1] for k, v in neu.items()}

    # Stufen: alt (6 Stufen auf 7 m, Gebäude mit Block) und neu (9 Stufen bis zum Ostende des Durchgangs)
    a = PG.ALT
    n_neu = PG.neu(STUFEN_NEU, ENDE_U)
    b_alt = PG.gasse_baender(fps_alt.values(), a["u"], a["t"], a["n"], a["lauf"])
    b_neu = PG.gasse_baender(fps_neu.values(), n_neu["u"], n_neu["t"], n_neu["n"], n_neu["lauf"])
    hof = G.scale_geom(I.hof_polygon_local().buffer(I.HOF_UEBERMASS).intersection(I.huelle_m(data)), S)
    hof = hof.difference(unary_union(list(fps_alt.values())).buffer(0.9, join_style=2))

    # 3D: Ausschnitt um den Durchgang, um die Fenstermitte verschoben
    x0, x1, y0, y1 = PG.FENSTER_M
    cx, cy = (x0 + x1) / 2 * S, (y0 + y1) / 2 * S
    fenster = box(x0 * S, y0 * S, x1 * S, y1 * S)
    crop = lambda solid: solid ^ G.extrude(fenster, -3, 60)
    shift = lambda m: m.translate([-cx, -cy, 0])
    tm = {}
    for tag, src, fps, baender in (("alt", pair, fps_alt, b_alt), ("neu", neu_ohne, fps_neu, b_neu)):
        tm["paulinum_" + tag] = to_tm(shift(crop(src["01_paulinum"][0])))
        tm["institut_" + tag] = to_tm(shift(crop(src["05_institutsgebaeude"][0])))
        tm["platte_" + tag] = to_tm(shift(PG.platte_ausschnitt(fps.values(), baender)))
    dicht = all(to_tm(v[0]).is_watertight for v in neu.values())
    bilder(pair, neu)
    vol = {k: (pair[k][0].volume(), neu[k][0].volume()) for k in pair}

    # Schnitte (echte Querschnitte der Körper; die Brücke zeichnet die Seite selbst, damit der Regler sie verschieben kann)
    tn = PG.nach_hof_mm(tun)
    qb = tn.intersection(box(U_MITTE_M * S - 0.001, -1000, U_MITTE_M * S + 0.001, 1000)).bounds
    lb = tn.intersection(box(-1000, T_MITTE_M * S - 0.001, 1000, T_MITTE_M * S + 0.001)).bounds
    pq_alt = PG.schnitt_quer(pair["01_paulinum"][0], U_MITTE_M)
    pq_neu = PG.schnitt_quer(neu["01_paulinum"][0], U_MITTE_M)
    iq_neu = PG.schnitt_quer(neu_ohne["05_institutsgebaeude"][0], U_MITTE_M)
    pl_alt = PG.schnitt_laengs(pair["01_paulinum"][0], T_MITTE_M)

    def treppe_profil(n, u0, ende, lauf):
        tr = lauf / n
        return [[round((u0 + k * tr) * S, 3), round(min(u0 + (k + 1) * tr, ende) * S, 3), round(hb * (n - 1 - k) / n, 3)] for k in range(n - 1)]
    prof_alt = treppe_profil(a["n"], -94.0, a["u"][1], a["lauf"])
    prof_neu = treppe_profil(STUFEN_NEU, -94.0, ENDE_U, n_neu["lauf"])

    tc3 = np.asarray(tun.centroid.coords[0]) - [cx, cy]
    views = [
        dict(name="Ostportal", t=[tc3[0], tc3[1], 9.0], d=70, az=-12, el=10,
             text="Blick vom Augustusplatz in die Gasse. Neu: unter der Brücke geht es durch, die Decke ist waagerecht. Alt: Vollblock mit senkrechten Streifen."),
        dict(name="Schräg Nordost", t=[tc3[0], tc3[1], 10.0], d=135, az=28, el=26,
             text="Paulinum (blau) und Institutsgebäude (orange) von Nordosten. Die Brücke gehört neu zum Institutsgebäude."),
        dict(name="Von Westen", t=[tc3[0], tc3[1], 8.0], d=75, az=168, el=12,
             text="Blick durch die Gasse nach Osten. Die Platte steigt zum Hof hin an."),
        dict(name="Gasse und Treppe", t=[tc3[0] - 16, tc3[1] + 3, 3.0], d=110, az=165, el=38,
             text="Die Stufen laufen neu von der Hofkante bis zum Ostende des Durchgangs; die untersten liegen unter der Brücke."),
        dict(name="Von oben", t=[tc3[0] - 10, tc3[1], 0.0], d=170, az=-90, el=88, text="Grundriss von oben, Norden ist oben."),
    ]
    daten = {"views": views}
    for k, m in tm.items():
        daten[k] = pack(m)
    daten["tunnel"] = [[round(x * S - cx, 3), round(y * S - cy, 3)] for x, y in list(PG.TUNNEL_M.exterior.coords)[:-1]]
    daten["z"] = dict(zc=round(zc, 3), zt=round(zt, 3), hb=round(hb, 3), zc_min=8.0, zc_max=18.0, fuss=FUSS_T)
    daten["schnitt"] = dict(
        quer=dict(paulinum_alt=rings(pq_alt), paulinum_neu=rings(pq_neu), institut=rings(iq_neu), bruecke=[round(qb[1], 3), round(qb[3], 3)],
                  fenster=[round(52 * S, 2), round(82 * S, 2)]),
        laengs=dict(block=rings(pl_alt), bruecke=[round(lb[0], 3), round(lb[2], 3)], alt=prof_alt, neu=prof_neu,
                    hof_u=round(-94.0 * S, 3), fenster=[round(-100 * S, 2), round(-50 * S, 2)]),
    )

    # Zahlen für Texte und Tabelle
    p_alt_a, p_neu_a = fps_alt["01_paulinum"].area, fps_neu["01_paulinum"].area
    i_alt_a, i_neu_a = fps_alt["05_institutsgebaeude"].area, fps_neu["05_institutsgebaeude"].area
    tbr = tun.area
    lauf_alt = a["lauf"] * (a["n"] - 1) / a["n"] * S
    lauf_neu = (ENDE_U + 94.0) * S
    unter = sum(1 for s0, s1, _ in prof_neu if s1 > tn.bounds[0])
    stufen = lambda n: "%d Stufen à %s mm" % (n, de(hb / n, 2))
    zeilen = [
        ("Durchgang", "zugefüllt: Vollblock, %s mm² Grundfläche" % de(tbr, 0),
         "frei: %s × %s mm, Decke %s mm über der Platte" % (de(laenge_m * S, 1), de(mass["breite"], 1), de(zc, 1)), "Länge im Mittel, Breite quer zur Gasse"),
        ("Brücke (Decke bis Dach)", "Teil des Blocks im Paulinum", "%s mm dick (Decke %s, Dach %s mm), beim Institutsgebäude" % (de(zt - zc, 1), de(zc, 1), de(zt, 1)),
         "eine Platte über der Gasse"),
        ("Grundriss Paulinum", "%s mm²" % de(p_alt_a, 0), "%s mm²" % de(p_neu_a, 0), "minus Durchgang und Splitter an der Institutswand"),
        ("Grundriss Institutsgebäude (Mulde, Fuß)", "%s mm²" % de(i_alt_a, 0), "%s mm²" % de(i_neu_a, 0),
         "nur der Splitter kommt dazu; unter dem Durchgang gibt es keinen Fuß"),
        ("Volumen Paulinum", "%s cm³" % de(vol["01_paulinum"][0] / 1000, 1), "%s cm³" % de(vol["01_paulinum"][1] / 1000, 1), "Laserscan, Maßstab 1:1300, massiv"),
        ("Volumen Institutsgebäude", "%s cm³" % de(vol["05_institutsgebaeude"][0] / 1000, 1), "%s cm³" % de(vol["05_institutsgebaeude"][1] / 1000, 1), "plus Brücke und Splitter"),
        ("Treppe der Platte im Nordosten", "%s auf %s mm" % (stufen(a["n"]), de(lauf_alt, 1)), "%s auf %s mm" % (stufen(STUFEN_NEU), de(lauf_neu, 1)),
         "eine Stufe = eine Druckschicht (0,2 mm); Ende am Ostende des Durchgangs"),
        ("Stufen unter der Brücke", "keine", "%d von %d" % (unter, STUFEN_NEU - 1), "die Stufen laufen unter dem Durchgang bis zur Ostkante"),
        ("Druck der Brücke", "–", "Unterseite %s mm² waagerecht, Support %s mm hoch" % (de(tbr, 0), de(zc + FUSS_T, 1)),
         "Unterseite liegt bei Fuß %s + Decke über der Druckplatte" % de(FUSS_T, 1)),
    ]
    tabelle = "".join('<tr><th scope="row">%s</th><td class="n o">%s</td><td class="n a">%s</td><td class="hint2">%s</td></tr>' % z for z in zeilen)

    ersetz = {
        "@DATA@": json.dumps(daten, ensure_ascii=False),
        "@FIG_IST@": fig_plan("Ist: Vollblock", "Grundriss: heute füllt ein Vollblock den Durchgang", fps_alt, b_alt, hof, False),
        "@FIG_NEU@": fig_plan("Neu: Durchgang mit Brücke", "Grundriss: Durchgang frei, Brücke darüber, Stufen bis zum Ostende", fps_neu, b_neu, hof, True),
        "@TABELLE@": tabelle,
        "@ZC@": de(zc, 1), "@ZT@": de(zt, 1), "@ZC_M@": de(PG.Z_DECKE_M - PG.GROUND["05_institutsgebaeude"], 1),
        "@ZT_M@": de(PG.Z_DACH_M - PG.GROUND["05_institutsgebaeude"], 1),
        "@ZC_ABS@": de(PG.Z_DECKE_M, 1), "@ZT_ABS@": de(PG.Z_DACH_M, 1), "@BODEN_ABS@": de(PG.Z_BODEN_M, 1), "@DICKE@": de(zt - zc, 1),
        "@LAENGE@": de(laenge_m * S, 1), "@LAENGE_M@": de(laenge_m, 1), "@BREITE@": de(mass["breite"], 1), "@BREITE_M@": de(mass["breite_m"], 1),
        "@FLAECHE@": de(tbr, 0), "@FLAECHE_M@": de(mass["flaeche_m2"], 0),
        "@HUB@": de(hb, 1), "@RISER@": de(hb / STUFEN_NEU, 2), "@STUFEN@": str(STUFEN_NEU),
        "@TREAD@": de(n_neu["lauf"] / STUFEN_NEU, 1), "@TREAD_MM@": de(n_neu["lauf"] / STUFEN_NEU * S, 1),
        "@LAUF_NEU@": de(lauf_neu, 1), "@LAUF_ALT@": de(lauf_alt, 1), "@UNTER@": str(unter),
        "@SUPPORT_H@": de(zc + FUSS_T, 1), "@FUSS@": de(FUSS_T, 1),
        "@DICHT@": "ja" if dicht else "NEIN",
        "@VOL_P@": "%s → %s" % (de(vol["01_paulinum"][0] / 1000, 1), de(vol["01_paulinum"][1] / 1000, 1)),
        "@VOL_I@": "%s → %s" % (de(vol["05_institutsgebaeude"][0] / 1000, 1), de(vol["05_institutsgebaeude"][1] / 1000, 1)),
    }
    page = open(os.path.join(HERE, "page.template.html"), encoding="utf-8").read()
    for k, v in ersetz.items():
        page = page.replace(k, v)
    pfad = os.path.join(HERE, "page.html")
    open(pfad, "w", encoding="utf-8").write(page)
    print("page.html: %.0f KB; Körper dicht=%s; Decke %.2f mm (%.1f m), Durchgang %.1f × %.1f mm" % (
        os.path.getsize(pfad) / 1024, dicht, zc, PG.Z_DECKE_M - PG.GROUND["05_institutsgebaeude"], laenge_m * S, mass["breite"]))
    return dicht


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
