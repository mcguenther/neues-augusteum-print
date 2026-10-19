#!/usr/bin/env python3
"""Probeteil K4 Kordelprobe (Mitte des Unterkastens Stand 8): STL, README, ZIP, Prüfbericht und Bilder nach stl/steckmodul_kordelprobe/.

Teil (Druckausrichtung: Bett unten = Hut-Seite, Erhebung nach oben):
  K4_stern_F-aussen.stl, K4_stern_F-innen.stl   Stern Ø 70 aus acht Höckern mit den Gängen (F-aussen: freies Rechteck 8 × 5, darüber 45°-Dachschrägen 1,5,
                  Höcker 11,4 × 7,7; F-innen: Fase 1,5 in den oberen Ecken, Höcker 10,4 × 6,2), in der Mitte die Erhebung über dem Knopf: Hohlraum am Bett Ø 39,4 auf Gang-Höhe, ab 8,7 mm vor dem
                  Knopfkörper 45°-Anstieg, Knopfraum Ø 25 × 12,2 frei, flache Decke Ø 20 bei 14,7, Plateau Ø 28 bei 15,9 (Wand 1,2).
                  Ohne Boden, Randwand und Deckplatte: nur das, was die Kordel und der Knopf brauchen; Geometrie wie im Kasten.
Prüft am echten Hut (Knopf Ø 22 × 12,0, Höhe noch Annahme; Kordel 3 × 5): Knopf im Raum, Kordel vom Knopffuß in jeden der acht Gänge,
Decken ohne Support, Kleben. Plan: plug/power/plan_kasten8.html (Abschnitt K4); Werte in plug/power/params.py, Geometrie in plug/power/kasten8.py.
Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 -m plug.power.build_kordelprobe
"""
import os
import zipfile

import manifold3d as m3d
from shapely import affinity
from shapely.geometry import Point, box as sbox
from shapely.ops import unary_union

import generate as G
from plug.fit_test.generator import overhangs
from plug.geom import box as mbox
from plug.geom import to_bed, to_tm, vol_int
from plug.power import build_concept as BC
from plug.power import kasten8 as K8
from plug.power import params as PP

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(HERE, "stl", "steckmodul_kordelprobe")
PREV = os.path.join(HERE, "vorschau", "steckmodul_kordelprobe")
D = 70.0                      # Stern Ø 70 (Gänge 35 mm vom Mittelpunkt)
H = K8.KNOPF_Z                # Höhe 15,9 = Plateau der Erhebung (Höcker 7,7)
CH = PP.CH_BED


class Report:
    def __init__(self):
        self.lines = []

    def __call__(self, s=""):
        print(s)
        self.lines.append(s)


def stern():
    """Stern wie ein Ausschnitt des Kastens, aber ohne Boden und Ring: acht Höcker, Erhebung über dem Knopf, Hohlraum und Gänge ausgeschnitten."""
    c = (0.0, 0.0)
    hw = K8.GANG_W / 2 + K8.WAND
    hoecker = G.union([G.extrude(sbox(0, -hw, D / 2, hw), 0.0, K8.GANG_Z).rotate([0, 0, k * 45.0]) for k in range(8)])
    solid = G.union([K8.erhebung_solid(c, 0.0), hoecker])
    gc = K8.gaenge_cut(c, K8.GANG_W, K8.GANG_H, K8.FASE, PP.KORDEL_GANG["n"], laenge=D / 2 + 2)
    kc = K8.knopf_cut(c)
    strips = unary_union([affinity.rotate(sbox(0, -K8.GANG_W / 2, D, K8.GANG_W / 2), k * 45.0, origin=(0, 0)) for k in range(8)])
    mouth = BC.mouth_ch(unary_union([Point(c).buffer(K8.R_RAMPE, 128), strips]), 0, CH)
    return solid - G.union([kc, gc, mouth])


NAME = {"innen": "K4_stern_F-innen", "aussen": "K4_stern_F-aussen"}
ERST = "aussen"               # zuerst drucken: Rechteck 8 × 5 ganz frei, kostet am Kasten keine Höhe


def main():
    rep = Report()
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith((".stl", ".zip", ".txt")):
            os.remove(os.path.join(OUT, f))
    for d in (PREV, os.path.join(PREV, "unten")):
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.startswith("K4_stern") and f.endswith(".png"):
                    os.remove(os.path.join(d, f))
    rep("Probeteil K4 Kordelprobe: zwei Sterne Ø %.0f × %.1f (Gangfase innen und außen), ohne Boden, Randwand und Deckplatte; Bett unten (Hut-Seite)" % (D, H))
    rep("Maße: Knopf Ø %.0f × %.1f (Höhe Annahme, vom Nutzer zu bestätigen), Kordel %.0f × %.0f unten seitlich am Knopffuß; Knopfraum Ø %.0f × %.1f, Anstieg 45° ab Radius %.1f (%.1f vor dem Knopfkörper), Decke Ø %.0f bei %.1f, Plateau Ø %.0f bei %.1f" % (
        PP.HUT_KNOPF["d"], PP.HUT_KNOPF["h"], PP.KORDEL["b"], PP.KORDEL["h"], 2 * K8.R_RAUM, K8.H_RAUM, K8.R_RAMPE, K8.R_RAMPE - K8.R_KN, 2 * K8.R_DECKE, K8.KNOPF_TOP, 2 * K8.R_PLATEAU, K8.KNOPF_Z))
    info = {}
    bad = 0
    kn = PP.HUT_KNOPF
    cb, ch_ = PP.KORDEL["b"], PP.KORDEL["h"]

    def chk(txt, val, limit=0.05):
        nonlocal bad
        ok = val < limit
        bad += not ok
        rep("  %-66s %8.2f  %s" % (txt, val, "ok" if ok else "FEHLER"))

    def kord(z0, z1, r0, r1):
        return G.union([K8.prism_y_x([(-cb / 2, z0), (cb / 2, z0), (cb / 2, z1), (-cb / 2, z1)], r0, r1).rotate([0, 0, k * 45.0]) for k in range(8)])

    for m in ("innen", "aussen"):
        K8.modus(m)
        name = NAME[m]
        sch = stern()
        rep("\n%s (Gangfase %s%s)" % (name + ".stl", m, ", zuerst drucken" if m == ERST else ""))
        if m == "aussen":
            rep("  Gänge: freies Rechteck %.0f × %.0f, Dachschrägen %.1f × 45° darüber (Decke %.0f breit bei %.1f), Höcker %.1f breit und %.1f hoch, Wand seitlich %.1f (an der Bettkante %.1f)" % (
                K8.GANG_W, K8.GANG_H, K8.FASE, K8.GANG_W - 2 * K8.FASE, K8.GANG_H + K8.FASE, K8.GANG_W + 2 * K8.WAND, K8.GANG_Z, K8.WAND, K8.WAND - CH))
        else:
            rep("  Gänge: %.0f × %.0f mit Fase %.1f × 45° in den oberen Ecken (Decke %.0f breit bei %.1f), Höcker %.1f breit und %.1f hoch, Wand seitlich %.1f (an der Bettkante %.1f)" % (
                K8.GANG_W, K8.GANG_H, K8.FASE, K8.GANG_W - 2 * K8.FASE, K8.GANG_H, K8.GANG_W + 2 * K8.WAND, K8.GANG_Z, K8.WAND, K8.WAND - CH))
        tm = to_tm(sch)
        tm.export(os.path.join(OUT, name + ".stl"))
        g, nl = BC.grams(sch)[0], int(round(tm.extents[2] / 0.2))
        comps = len(sch.decompose())
        ov = overhangs(sch, name)
        ok = bool(tm.is_watertight) and comps == 1
        bad += not ok
        rep("  %5.1f × %5.1f × %4.1f mm  %5.1f cm³  ≈ %2.0f g  dicht=%s  Teile=%d" % (*tm.extents, tm.volume / 1000.0, g, tm.is_watertight, comps))
        rep("  waagerechte Decken: %s   Überhang flacher als 45° zur Senkrechten: %.0f mm²" % (
            "; ".join("z=%.1f: %.0f mm²" % f[:2] for f in sorted(ov["flat"], key=lambda t: -t[1])[:4]) or "keine", ov["steep_area"]))
        knopf = m3d.Manifold.cylinder(kn["h"], kn["d"] / 2, kn["d"] / 2, 64)
        chk("Knopf Ø %.0f × %.1f im Raum (seitlich %.1f, oben %.1f Luft)" % (kn["d"], kn["h"], K8.R_RAUM - K8.R_KN, K8.H_RAUM - kn["h"]), vol_int(knopf, sch))
        raum = m3d.Manifold.cylinder(K8.H_RAUM - 0.03, K8.R_RAUM - 0.02, K8.R_RAUM - 0.02, 96).translate([0, 0, 0.01])
        chk("Knopfraum Ø %.0f × %.1f frei" % (2 * K8.R_RAUM, K8.H_RAUM), vol_int(raum, sch))
        chk("Kordel %.0f × %.0f vom Knopffuß in allen 8 Gängen bis zum Rand" % (cb, ch_), vol_int(kord(0.05, ch_, K8.R_KN, D / 2 - 0.1), sch))
        rect = vol_int(K8.gaenge_cut((0.0, 0.0), K8.GANG_W - 0.04, K8.GANG_H - 0.02, 0.0, 8, z0=0.01, laenge=D / 2 - 0.1), sch)
        if m == "aussen":
            chk("volles Rechteck %.0f × %.0f frei in allen 8 Gängen" % (K8.GANG_W, K8.GANG_H), rect)
        else:
            chk("Gangprofil %.0f × %.0f mit Fase %.1f frei" % (K8.GANG_W, K8.GANG_H, K8.FASE),
                vol_int(K8.gaenge_cut((0.0, 0.0), K8.GANG_W - 0.04, K8.GANG_H - 0.02, K8.FASE - 0.02, 8, z0=0.01, laenge=D / 2 - 0.1), sch))
            rep("  (volles Rechteck 8 × 5 nicht frei: die gefasten Ecken nehmen %.0f mm³ weg, die Kordel passt trotzdem)" % rect)
        det = []
        ow, oa, oz = K8.ueberhang(sch, zmax=H + 0.3, detail=det)
        br = K8.brueckenbereiche(det, (0.0, 0.0))
        rep("  Überhang je 0,2-mm-Lage (45° getragen): breiteste freie Decke %.1f mm (höchstens 20); %s" % (ow, "; ".join("%s %.1f mm bei z %.1f" % t for t in br)))
        if ow > 20.0:
            bad += 1
        info[name] = dict(g=g, layers=nl, gz=K8.GANG_Z, wand=K8.WAND, bruecke=ow, br=br)
    K8.modus(PP.GANG_FASE_MODUS)
    rep("\nWände: über den Gängen %.1f, Schale der Erhebung %.1f (45° senkrecht gemessen); Powerbank oder Buch auf dem Plateau lässt die Kordel frei" % (PP.KORDEL_DACH, PP.KORDEL_DACH))
    rep("-> %s" % ("keine Kollisionen" if not bad else "%d Fehler!" % bad))

    from plug.roadmap import build as rb
    for name in info:
        t = ", ".join("%s ≈ %.0f min" % (prof, info[name]["g"] / pr["rate"] * 60.0 + info[name]["layers"] * pr["layer"] / 60.0 + pr["start"]) for prof, pr in rb.PROFILE.items())
        rep("%s: Material ≈ %.0f g, Zeit %s, bei deinem Drucker (Nacht 1: 47 g in 2,5 h) ≈ %.0f min" % (name, info[name]["g"], t, info[name]["g"] / 47.0 * 2.5 * 60))
    with open(os.path.join(OUT, "pruefbericht.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rep.lines) + "\n")
    write_readme(info)
    zpath = os.path.join(OUT, "kordelprobe.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(OUT)):
            if f.endswith(".stl") or f == "README.txt":
                z.write(os.path.join(OUT, f), f)
    rep("%s: %.0f kB" % (os.path.relpath(zpath, HERE), os.path.getsize(zpath) / 1024))
    images()
    return bad


def images():
    """Bilder mit dem Software-Renderer: beide Sterne schräg von oben und von unten."""
    import subprocess
    import sys
    for name in NAME.values():
        base = os.path.join(OUT, name + ".stl")
        subprocess.run([sys.executable, "preview.py", base, "--azim", "-60", "--elev", "40", "--out", PREV], cwd=HERE, check=False)
        subprocess.run([sys.executable, "preview.py", base, "--azim", "-60", "--elev", "-55", "--out", PREV + "/unten"], cwd=HERE, check=False)


def write_readme(info):
    i, a = info[NAME["innen"]], info[NAME["aussen"]]
    txt = """K4 KORDELPROBE (Mitte des Unterkastens, Stand 8)
================================================
Probeteil zum Plan plug/power/plan_kasten8.html (Abschnitt K4). Noch nichts gedruckt, alle Werte sind Planwerte.

Teile (beide Stern Ø 70 x 15,9 mm, ohne Boden und ohne Randwand, Bett unten = Hut-Seite, kein Support, siehe pruefbericht.txt):
  K4_stern_F-aussen.stl   ZUERST DRUCKEN. Gang: volles Rechteck 8 x 5 frei, 45-Grad-Dachschrägen 1,5 darüber (Decke 5 breit bei 6,5),
                          Höcker 11,4 breit und %(ga)s hoch, Wand 1,7 (an der Bettkante 1,2)                                   ca. %(a).0f g
  K4_stern_F-innen.stl    Gang 8 x 5 mit Fase 1,5 in den oberen Ecken (Decke 5 breit bei 5,0, die Ecken des Rechtecks fehlen),
                          Höcker 10,4 breit und %(gi)s hoch, Wand 1,2 (an der Bettkante 0,7)                                   ca. %(i).0f g

Unterschied: bei F-aussen bleibt das ganze Rechteck 8 x 5 frei, das Gangdach liegt 1,5 mm höher. Am Kasten kostet das keine Höhe, weil
die Powerbank auf der Erhebung über dem Knopf liegt (Plateau 15,9), nicht auf den Gangdächern; nur etwa 5 g mehr. Bei F-innen ist der
Gang oben enger, die Kordel 5 x 3 passt trotzdem (2 mm Luft in der Höhe). Zuerst F-aussen drucken; F-innen nur, wenn man den Vergleich
fühlen will oder F-aussen an der Gangdecke unsauber druckt.

In der Mitte beider Sterne die Erhebung für den Knopf: am Hut ein Hohlraum Ø 39,4 auf Gang-Höhe 5, ab 8,7 mm vor dem Knopf steigt die
Decke mit 45 Grad an, der Knopfraum Ø 25 x 12,2 ist überall frei, oben eine flache Decke Ø 20 bei 14,7, darüber das Plateau Ø 28 bei 15,9.
Annahme: Knopf Ø 22 x 12 mm hoch (bitte nachmessen); die Kordel 3 x 5 kommt unten seitlich am Knopffuß heraus.

Ablauf:
  1. Stern mit der Mitte über den Knopf setzen, Kordel vom Knopffuß in einen Gang legen.
  2. Stern mit Heißkleber auf dem Hut ankleben (nur auf die Unterseite der Höcker und des Rings, nicht in die Gänge und nicht in die Mitte).
  3. Powerbank (oder ein Buch) auf das Plateau legen: drückt es auf den Knopf? Lässt sich die Kordel noch bewegen?
  4. Kordel nacheinander in andere Gänge legen (O, NO, N ...), jedes Mal ohne zu klemmen?
Fragen für den Testbogen: Wie hoch ist der Knopf wirklich (12 mm?), passt er in den Raum (1,5 mm Luft je Seite, 0,2 oben)? Hängt die
Decke über dem Knopf (etwa 20 mm frei) durch? Sind Gangdecken und Fasen sauber (F-aussen und F-innen)? Hält Heißkleber? Ist die Kordel zu
steif für den Knick am Gangausgang?

Druck: PLA, 0,2 mm Schicht, Support aus, Gyroid 10 %% wie plug/slicer.md, Bett unten wie in der Datei (Erhebung oben).
"""
    open(os.path.join(OUT, "README.txt"), "w", encoding="utf-8").write(txt % dict(a=a["g"], i=i["g"], ga=("%.1f" % a["gz"]).replace(".", ","), gi=("%.1f" % i["gz"]).replace(".", ",")))


if __name__ == "__main__":
    raise SystemExit(main())
