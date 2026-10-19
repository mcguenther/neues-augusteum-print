#!/usr/bin/env python3
"""Passungs-Probedrucke bei wechselnden Filamenten: zwei Varianten, STL, Prüfbericht, Druckzeit-Schätzung nach `stl/steckmodul_passung/`.

Variante A (die vorhandenen beigen Gebäude sind die Lehre): Mulden-Block mit dem echten Institutsumriss (A1) und die Kassettenserie (K1 bis K3).
Variante B (eigener kompakter Probedruck, kein Gebäude nötig): zwei Probefüße (B1 Fuß-Fase 2,0 wie die Gebäude, B2 Fuß-Fase 4,0), ein kleiner
Mulden-Block dazu (B3) und dieselbe Kassettenserie. Der Probefuß ist rechteckig mit Kodierecke (verdrehsicher, wie der Fuß des Display-Gebäudes) und hat
den Schacht der Kassette V1RS mit 45°-Walmdach. Die Kassetten sind nur der Unterbau (dort sitzt die Passung): Tasche unten, ohne Blatt und Streifen.

Spielwerte (je Seite): Mulden 0,10 / 0,15 / 0,20 (Kennung 1 bis 3 erhabene Balken); Kassette im Schacht 0,12 / 0,16 / 0,20 (Außenmaß der Kassette um
0,06 / 0,10 / 0,14 je Seite kleiner als heute, Schacht unverändert 0,06). Schachtdecke 0,35 über dem Unterbau (SHAFT_EXTRA_T im Code 0,30; hier die
Empfehlung aus L36).

Aufruf (aus dem Wurzelverzeichnis, ca. 1 min):
    python3 -m plug.filament.build
"""
import os
import zipfile

import manifold3d as m3d
import numpy as np
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

import generate as G
from plug import campus as C
from plug import series2 as N2
from plug.filament import geom as FG
from plug.footfit.build_stub import layer_poly, ueberhang
from plug.geom import box, cbox, diff, to_tm, union
from plug.power import build_concept as BC
from plug.testcase import params as P
from plug.testcase import variants as V

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_passung")
PREV = os.path.join(HERE, "vorschau", "steckmodul_passung")
VAR = "V1RS"
MULDEN_SPIEL = (0.10, 0.15, 0.20)
KASS_SPIEL = (0.12, 0.16, 0.20)          # Spiel im Modell je Seite (Einpressspiel heute 0,06)
SCHACHT_EXTRA = 0.35
PROBE_W, PROBE_D, PROBE_KEY = 31.0, 18.0, 3.0
DACH = 1.2
LAGE = 0.2
BAR_W, BAR_GAP, BAR_L, BAR_H = 1.2, 1.0, 8.0, 0.6


def ext(poly, z0, z1):
    return G.extrude(poly, z0, z1)


# ---- Kassette (Unterbau)
def kassette(spiel):
    """Unterbau der Kassette V1RS, je Seite um (spiel - 0,06) schlanker, Tasche unten am Bett (z = 0), Buchsentasche unverändert."""
    d = V.dims(VAR)
    dd = spiel - P.KASS_CLR_T
    w, depth, zb = d["w"], d["depth"], d["z_b"]
    body = N2.chamfered_block(w - 2 * dd, depth - 2 * dd, zb, V.EF, 0.0).translate([0, depth / 2, 0])
    cuts = [cbox(d["pk_w"], d["pk_d"], -0.01, d["zp"], cy=d["ypin"]),
            N2.chamfer_hole(d["pk_w"], d["pk_d"], 0.0, P.ENTRY_CH_T, True, cy=d["ypin"]),
            box(-d["slot"] / 2, d["slot"] / 2, d["y_p0"], d["y1"], d["zp"] - 0.01, zb + 0.01)]
    return diff(body, *cuts)


# ---- Probefuß
def probe_outline():
    """Rechteck W × D, Mitte im Ursprung, Kodierecke (+x, −y)."""
    return sbox(-PROBE_W / 2, -PROBE_D / 2, PROBE_W / 2, PROBE_D / 2).difference(sbox(PROBE_W / 2 - PROBE_KEY, -PROBE_D / 2, PROBE_W / 2 + 1, -PROBE_D / 2 + PROBE_KEY))


def probefuss(fase):
    """Probefuß: Fuß mit Fase `fase` an der Bettkante, Schacht der V1RS (Kassette plus 0,06 je Seite) mit Einführfase, 45°-Walm darüber, Dach 1,2."""
    fp = probe_outline()
    w, dep = C.shaft_size(VAR)
    rect = sbox(-w / 2, -dep / 2, w / 2, dep / 2)
    zs = V.dims(VAR)["z_b"] + SCHACHT_EXTRA
    parts = [ext(rect, -0.01, zs), BC.mouth_ch(rect, 0.0, P.ENTRY_CH_T)]
    t = 0.0
    while True:
        g = rect.buffer(-(t + 0.05), join_style=2)
        if g.is_empty or g.area < 0.05:
            break
        parts.append(ext(g, zs + t - 0.005, zs + t + 0.1 + 0.005))
        t += 0.1
    top = zs + t + DACH
    body = BC.slab_ch(fp, 0.0, top, fase)
    return body - G.union(parts), top


# ---- Mulden-Block
def mulden_block(poly, spiele, wand=2.4, rand=3.0):
    """Platte mit je einer Mulde je Spiel (Boden 0,4, Fase oben 0,5, Plattenkante unten 0,5 und oben 1,5), erhabene Balken als Kennung (1 bis n)."""
    rand_l = 2.0 + len(spiele) * BAR_W + (len(spiele) - 1) * BAR_GAP + 1.0 + 1.0
    if wand < 2.0:                         # kompakt: Kennung als kurze Querbalken (3,5 lang) übereinander statt nebeneinander
        rand_l = 1.8 + 3.5 + 1.2
    b = FG.block(poly, spiele, wand=wand, rand=rand, rand_l=rand_l)
    T = FG.PLATTE_T
    outline = b["platte"]
    plate = BC.slab_ch(outline, 0.0, T, P.EF_CH_T) ^ C.top_edge(outline, T, P.PLATE_TOP_CH_T)
    ch = P.MULDE_CH_T
    n = BC.n_layers(ch)
    dz = ch / n
    for (s, g), (_, fp) in zip(b["mulden"], b["fps"]):
        cut = [ext(g, FG.BODEN, T - ch + 0.01)]
        for k in range(n):
            top = T + 1.0 if k == n - 1 else T - ch + dz * (k + 1) + 0.01
            cut.append(ext(fp.buffer(s + dz * (k + 0.5), join_style=2), T - ch + dz * k, top))
        plate = plate - G.union(cut)
    bars = []
    for i, (s, g) in enumerate(b["mulden"]):
        yc = (g.bounds[1] + g.bounds[3]) / 2
        for j in range(i + 1):
            if wand < 2.0:
                y0 = yc - ((i + 1) * BAR_W + i * BAR_GAP) / 2 + j * (BAR_W + BAR_GAP)
                bars.append(box(1.8, 5.3, y0, y0 + BAR_W, T - 0.01, T + BAR_H))
            else:
                x0 = 2.0 + j * (BAR_W + BAR_GAP)
                bars.append(box(x0, x0 + BAR_W, yc - BAR_L / 2, yc + BAR_L / 2, T - 0.01, T + BAR_H))
    plate = plate + G.union(bars)
    return plate, b


# ---- Prüfungen und Zeit
def zeit_min(man, voll_unten=4, voll_oben=5, wand=1.2, fuell=0.15, v=60.0):
    """Zeitschätzung (Muster der r8-Schätzung: Pfadlänge = Fläche / 0,42, 60 mm/s, Zuschlag 1,5 s, Mindestzeit 6 s, Start 6 min), Wände 1,2 mm
    (3 Linien), Füllung 15 %, unten 4 und oben 5 volle Lagen. Gibt (Minuten roh, Minuten mit Faktor 1,2 nach L45) zurück."""
    b = man.bounding_box()
    n = int(round((b[5] - b[2]) / LAGE))
    sec = 0.0
    for i in range(n):
        g = layer_poly(man, b[2] + (i + 0.5) * LAGE)
        if g is None or g.is_empty:
            continue
        schale = g.difference(g.buffer(-wand, join_style=2))
        innen = g.area - schale.area
        voll = i < voll_unten or i >= n - voll_oben
        fl = g.area if voll else schale.area + innen * fuell
        sec += max(fl / 0.42 / v + 1.5, 6.0)
    m = sec / 60.0 + 6.0
    return m, m * 1.2


def kassetten_zeit(man):
    b = man.bounding_box()
    sec = 0.0
    for i in range(int(round((b[5] - b[2]) / LAGE))):
        g = layer_poly(man, b[2] + (i + 0.5) * LAGE)
        sec += max(g.area / 0.42 / 60.0 + 1.5, 6.0) if g is not None and not g.is_empty else 0.0
    m = sec / 60.0 + 6.0
    return m, m * 1.2


def flach_gefuellt(man, **kw):
    return zeit_min(man, **kw)


class Report:
    def __init__(self):
        self.lines = []

    def __call__(self, txt):
        print(txt)
        self.lines.append(txt)


def main():
    rep = Report()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith((".stl", ".zip", ".txt")):
            os.remove(os.path.join(OUT, f))
    u = FG.umrisse()
    teile = {}
    ziel = {}
    plate_a, ba = mulden_block(u["05_institutsgebaeude"]["poly"], MULDEN_SPIEL)
    teile["A1_mulden_block_institut"] = plate_a
    ziel["A1_mulden_block_institut"] = "mulde"
    for i, s in enumerate(KASS_SPIEL):
        teile["K%d_kassette_V1RS_%d" % (i + 1, round(s * 100))] = kassette(s)
    f2, h2 = probefuss(2.0)
    f4, h4 = probefuss(4.0)
    teile["B1_probefuss_fase2"] = f2
    teile["B2_probefuss_fase4"] = f4
    plate_b, bb = mulden_block(probe_outline(), MULDEN_SPIEL, wand=1.6, rand=2.5)
    plate_b2, bb2 = mulden_block(probe_outline(), MULDEN_SPIEL[1:], wand=1.6, rand=2.5)
    teile["B3b_mulden_block_probe_2"] = plate_b2
    teile["B3_mulden_block_probe"] = plate_b

    rep("Passungs-Probedrucke (Plan plug/filament/plan.html); Spiele Mulde %s, Kassette im Modell %s, Schachtdecke +%.2f" % (MULDEN_SPIEL, KASS_SPIEL, SCHACHT_EXTRA))
    rep("\nTeile (Druckausrichtung, Bett z = 0), Druckzeit geschätzt nach dem Muster der r8-Schätzung (nicht kalibriert; Faktor 1,2 nach L45):")
    zeiten = {}
    for name, man in teile.items():
        tm = to_tm(man)
        tm.export(os.path.join(OUT, name + ".stl"))
        ue = ueberhang(man)
        roh, kor = (kassetten_zeit(man) if name.startswith("K") else zeit_min(man))
        zeiten[name] = (roh, kor)
        rep("  %-26s %6.1f × %6.1f × %5.1f mm  %5.2f cm³  dicht=%s (Manifold: %s)  Zeit %3.0f min (mit Faktor %3.0f)" % (
            name + ".stl", *tm.extents, tm.volume / 1000.0, tm.is_watertight, man.status().name, roh, kor))
        rep("      Lagenprüfung (Überhang je 0,2 mm über 0.25): Brücken %.2f mm² (bis %.2f mm), Kragstücke %.2f mm² (bis %.2f mm), Stellen über 1 mm: %s" % (
            ue["bruecke_mm2"], ue["bruecke_mm"], ue["krag_mm2"], ue["krag_mm"], ue["stellen"][:4] or "keine"))

    # ---- Passungen
    rep("\nPrüfung der Passungen (Überschneidungsvolumen in mm³; muss 0 sein, die Kontrollen müssen anstoßen):")
    bad = 0

    def chk(txt, v, soll_null=True):
        nonlocal bad
        ok = (v < 0.05) == soll_null
        bad += 0 if ok else 1
        rep("  %-78s %8.3f  %s" % (txt, v, "ok" if ok else "FEHLER"))

    # Kassette im Schacht des Probefußes (Probefuß-Schacht liegt zentriert, Kassettenmitte bei y = depth/2)
    d = V.dims(VAR)
    for i, s in enumerate(KASS_SPIEL):
        k = kassette(s).translate([0, -d["depth"] / 2, 0])
        chk("Kassette %d (Spiel %.2f) im Schacht des Probefußes B1" % (i + 1, s), (f2 ^ k).volume())
    k0 = kassette(P.KASS_CLR_T).translate([0, -d["depth"] / 2, 0])
    chk("Kontrolle: Kassette mit Spiel 0,06 (heute) liegt ohne Verschiebung im Schacht", (f2 ^ k0).volume())
    k_zu = N2.chamfered_block(d["w"] + 0.30, d["depth"] + 0.30, d["z_b"], V.EF, 0.0).translate([0, 0, 0])
    chk("Kontrolle: um 0,15 je Seite zu breite Kassette stößt im Schacht an", (f2 ^ k_zu.translate([0, 0, 0])).volume(), soll_null=False)
    # Probefuß in der Mulde des Blocks B3 (Fuß liegt mit Bett = Muldenboden: Mulde reicht ab z = 0,4, Fuß 14,2 über dem Boden)
    p0 = probe_outline().bounds
    for (s, g), (_, fp) in zip(bb["mulden"], bb["fps"]):
        ox, oy = fp.bounds[0] - p0[0], fp.bounds[1] - p0[1]          # Verschiebung des Umrisses (Probefuß liegt um den Ursprung)
        for nm, f in (("B1", f2), ("B2", f4)):
            ft = f.trim_by_plane([0, 0, -1], -FG.FUSS).translate([ox, oy, FG.BODEN])       # nur der Fuß (z <= 14,2), auf dem Muldenboden
            chk("Probefuß %s in der Mulde des Blocks B3 mit Spiel %.2f" % (nm, s), (plate_b ^ ft).volume())
        ft = f2.trim_by_plane([0, 0, -1], -FG.FUSS).translate([ox + s + 0.05, oy, FG.BODEN])
        chk("Kontrolle: Probefuß um Spiel + 0,05 in +x verschoben stößt an (Mulde %.2f)" % s, (plate_b ^ ft).volume(), soll_null=False)
    rep("  -> %s" % ("keine Kollisionen" if not bad else "%d Fehler!" % bad))

    # ---- Druckzeiten: Gesamt je Variante
    za = zeiten["A1_mulden_block_institut"][1]
    zk = sum(v[1] for n, v in zeiten.items() if n.startswith("K"))
    zb = zeiten["B1_probefuss_fase2"][1] + zeiten["B2_probefuss_fase4"][1] + zeiten["B3_mulden_block_probe"][1]
    rep("\nDruckzeit je Variante (Summe der Einzelteile, nacheinander; mehrere Teile gleichzeitig auf einem Bett sparen nur den Start):")
    rep("  Variante A (Mulden-Block für die vorhandenen Gebäude + 3 Kassetten): %.0f min Block + %.0f min Kassetten = %.0f min" % (za, zk, za + zk))
    rep("  Variante B (zwei Probefüße + kleiner Mulden-Block + 3 Kassetten): %.0f min Füße + %.0f min Block + %.0f min Kassetten = %.0f min" % (
        zeiten["B1_probefuss_fase2"][1] + zeiten["B2_probefuss_fase4"][1], zeiten["B3_mulden_block_probe"][1], zk, zb + zk))
    rep("  Eichung: dieselbe Schätzung ergab für den r8-Stummel 47 min bei gedruckten 55 min (Faktor 1,17); der Faktor 1,2 ist enthalten.")
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    zt = {n: "%.0f" % v[1] for n, v in zeiten.items()}
    zb_block_ = zeiten["B3_mulden_block_probe"][1]
    za_total, zb_total = za + zk, zb + zk
    zb_ohne4 = zeiten["B1_probefuss_fase2"][1] + zb_block_ + zk
    readme = README.format(za_total=za_total, zb_total=zb_total, zb_ohne4=zb_ohne4, za=za, zk=zk, zb_fuss=zeiten["B1_probefuss_fase2"][1] + zeiten["B2_probefuss_fase4"][1], zb_block=zeiten["B3_mulden_block_probe"][1],
                           zk1=zeiten["K1_kassette_V1RS_12"][1], za_block=za, ba=ba["breite"], ha=ba["hoehe"], bb=bb["breite"], hb=bb["hoehe"], **{"t_" + k: v for k, v in zt.items()})
    with open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme)
    sets = {"passung_variante_A.zip": ["A1_mulden_block_institut", "K1_kassette_V1RS_12", "K2_kassette_V1RS_16", "K3_kassette_V1RS_20"],
            "passung_variante_B.zip": ["B1_probefuss_fase2", "B2_probefuss_fase4", "B3_mulden_block_probe", "K1_kassette_V1RS_12", "K2_kassette_V1RS_16", "K3_kassette_V1RS_20"]}
    for zn, names in sets.items():
        with zipfile.ZipFile(os.path.join(OUT, zn), "w", zipfile.ZIP_DEFLATED) as z:
            for n in names:
                z.write(os.path.join(OUT, n + ".stl"), n + ".stl")
            z.write(os.path.join(OUT, "README.txt"), "README.txt")
            z.write(os.path.join(OUT, "pruefbericht.txt"), "pruefbericht.txt")
    return rep, zeiten, bad


README = """Passungs-Probedrucke bei wechselnden Filamenten (Plan: plug/filament/plan.html)
=====================================================================================
Stand 2026-10-19. Alles ungedruckt. Zwei Varianten, beide mit derselben Kassettenserie K1 bis K3.

Variante A: die vorhandenen beigen Gebäude sind die Lehre (Institutsgebäude für Mulde und Kassette; Hörsaal und Seminar zur Gegenprobe)
  A1_mulden_block_institut.stl   GRAU. Platte {ba:.0f} x {ha:.0f} x 14,6 mm mit drei Mulden im Umriss des Institutsfußes, Spiel je Seite
                                 0,10 (ein Balken) / 0,15 (zwei) / 0,20 (drei Balken, erhaben links); Mulde 14,2 tief, Boden 0,4, Fase oben 0,5.
                                 Das beige Institutsgebäude in jede Mulde stecken. Druckzeit etwa {t_A1_mulden_block_institut} min (Schätzung).
Variante B: eigener kompakter Probedruck, kein Gebäude nötig
  B1_probefuss_fase2.stl         BEIGE (oder die Farbe, die geprüft wird). Fuß 31 x 18 mm mit Kodierecke (verdrehsicher), Fuß-Fase 2,0 wie die Gebäude,
                                 Schacht für die Kassette V1RS mit Walmdach, 20 mm hoch. Etwa {t_B1_probefuss_fase2} min.
  B2_probefuss_fase4.stl         wie B1, aber Fuß-Fase 4,0 (Variante C aus dem Plan). Etwa {t_B2_probefuss_fase4} min.
  B3_mulden_block_probe.stl      GRAU. Platte {bb:.0f} x {hb:.0f} x 14,6 mm mit drei Mulden im Umriss des Probefußes, Spiele wie A1. Etwa {t_B3_mulden_block_probe} min.
Beide Varianten:
  K1_kassette_V1RS_12.stl        BEIGE. Unterbau der Kassette V1RS (nur dort sitzt die Passung; ohne Blatt und Streifen), Tasche unten am Bett.
  K2_kassette_V1RS_16.stl        Spiel im Schacht je Seite 0,12 / 0,16 / 0,20 (heute 0,06): Außenmaß 0,06 / 0,10 / 0,14 je Seite kleiner.
  K3_kassette_V1RS_20.stl        Kerben/Kennung: Dateiname; mit Stift auf der Unterseite markieren. Je etwa {zk1:.0f} min.

Druckzeit (Schätzung nach dem Muster der r8-Schätzung, mal 1,2 nach L45; nicht kalibriert; bitte die echte Zeit aus dem Slicer melden):
  Variante A: Block {za_block:.0f} min + Kassetten {zk:.0f} min = {za_total:.0f} min
  Variante B: Füße {zb_fuss:.0f} min + Block {zb_block:.0f} min + Kassetten {zk:.0f} min = {zb_total:.0f} min (nur B1 ohne B2: {zb_ohne4:.0f} min)

Slicer: PLA, Düse 0,4, Schicht 0,2, Wände 3, Füllung 15 %, Support aus, Ausrichtung wie exportiert (Fuß bzw. Plattenunterseite und Kassettentasche am Bett).
Filament: Fluss möglichst vorher kalibrieren (Plan, Abschnitt 6, Messplättchen T4).
Auswertung nach Gefühl: Fuß in Mulde 1 bis 3 (geht es ohne Kraft hinein, wie fest zieht man heraus, wackelt es), Kassette 1 bis 3 im Schacht
(Sitz 1 bis 5, Ziel wie in Schwarz: hält beim Schütteln, Herausdrücken nur mit Druck). Prüfbericht: pruefbericht.txt (dicht, keine Kollisionen, Überhang).
Schachtdecke im Probefuß 0,35 über dem Unterbau (im Code der Gebäude steht noch 0,30).
"""


if __name__ == "__main__":
    main()
